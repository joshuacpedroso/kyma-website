<?php
defined('ABSPATH') || exit;

function kyma_seed(string $name): array {
    static $cache=[];
    if (!isset($cache[$name])) {
        $file=get_template_directory().'/data/'.$name.'.json';
        $data=is_file($file)?json_decode(file_get_contents($file),true):null;
        $cache[$name]=is_array($data)?$data:[];
    }
    return $cache[$name];
}
function kyma_page_ids(): array { return (array)get_option('kyma_page_ids',[]); }
function kyma_admin_url(): string { return admin_url('admin.php?page=kyma'); }
function kyma_purge_cache(): void {
    flush_rewrite_rules();
    wp_cache_flush();
    if (function_exists('rocket_clean_domain')) rocket_clean_domain();
    if (function_exists('w3tc_flush_all')) w3tc_flush_all();
    if (has_action('litespeed_purge_all')) do_action('litespeed_purge_all');
}
function kyma_capture_post(int $id): array {
    return ['post'=>get_post($id,ARRAY_A),'meta'=>get_post_meta($id)];
}
function kyma_store_backup(array $backup): void {
    update_option('kyma_previous_site',$backup,false);
    if (get_option('kyma_previous_site')!==$backup) throw new RuntimeException('Não foi possível guardar a cópia do site anterior. A implantação foi interrompida para preservar o conteúdo.');
}
function kyma_restore_snapshot(array $backup, bool $switch=false): void {
    foreach ((array)($backup['created_ids']??[]) as $id) {
        if (get_post($id)) wp_update_post(['ID'=>$id,'post_status'=>'draft']);
    }
    foreach ((array)($backup['posts']??[]) as $id=>$record) {
        if (!get_post($id)) continue;
        $post=$record['post']; unset($post['filter']);
        $kses=has_filter('content_save_pre','wp_filter_post_kses');
        if($kses!==false)remove_filter('content_save_pre','wp_filter_post_kses',$kses);
        try { wp_update_post(wp_slash($post)); }
        finally { if($kses!==false)add_filter('content_save_pre','wp_filter_post_kses',$kses); }
        foreach (get_post_meta($id) as $key=>$unused) delete_post_meta($id,$key);
        foreach ($record['meta'] as $key=>$values) {
            foreach ($values as $value) add_post_meta($id,$key,maybe_unserialize($value));
        }
        clean_post_cache($id);
    }
    foreach ((array)($backup['options']??[]) as $key=>$value) {
        if ($value===null) delete_option($key); else update_option($key,$value);
    }
    update_option('kyma_install_complete',false,false);
    if ($switch && !empty($backup['theme']) && wp_get_theme($backup['theme'])->exists()) {
        switch_theme($backup['theme']);
    }
    kyma_purge_cache();
}
function kyma_activate($old_name='', $old_theme=null): void {
    if (!add_option('kyma_install_lock',time(),'','no')) {
        if ((int)get_option('kyma_install_lock')>time()-300) return;
        delete_option('kyma_install_lock');
        if (!add_option('kyma_install_lock',time(),'','no')) return;
    }
    $backup_ready=false;
    try {
        if (get_option('kyma_install_complete') && kyma_page_ids()) {
            $ids=kyma_page_ids();
            update_option('show_on_front','page');
            update_option('page_on_front',$ids['inicio']??0);
            update_option('page_for_posts',0);
            kyma_purge_cache();
            return;
        }
        $manifest=kyma_seed('pages'); $site=kyma_seed('site');
        if (!$manifest || !$site) throw new RuntimeException('O pacote do tema está incompleto.');
        $backup=['theme'=>$old_theme instanceof WP_Theme?$old_theme->get_stylesheet():(string)get_option('theme_switched'),
                 'time'=>current_time('mysql'),'posts'=>[],'created_ids'=>[],'options'=>[]];
        foreach (['show_on_front','page_on_front','page_for_posts','permalink_structure','blogname','blogdescription','site_icon'] as $key) {
            $backup['options'][$key]=get_option($key,null);
        }
        $legacy=get_posts(['post_type'=>['page','post'],'post_status'=>['publish','future'],'numberposts'=>-1,'fields'=>'ids']);
        foreach ($legacy as $id) $backup['posts'][$id]=kyma_capture_post((int)$id);
        // Also protect an existing draft/private page that occupies a target slug.
        foreach ($manifest as $key=>$entry) {
            $existing=get_page_by_path($entry['slug'],OBJECT,'page');
            if ($existing && !isset($backup['posts'][$existing->ID])) $backup['posts'][$existing->ID]=kyma_capture_post($existing->ID);
        }
        kyma_store_backup($backup);$backup_ready=true;
        update_option('kyma_seed_site_url',untrailingslashit(home_url()),false);
        update_option('kyma_seed_theme_url',get_template_directory_uri(),false);
        // Keep every local page link working immediately on ordinary WP hosting.
        if (!get_option('permalink_structure')) { global $wp_rewrite; $wp_rewrite->set_permalink_structure('/%postname%/'); }
        $ids=[];$created=[];
        foreach ($manifest as $key=>$entry) {
            $existing=get_page_by_path($entry['slug'],OBJECT,'page');
            $body=file_get_contents(get_template_directory().'/pages/'.$key.'.html');
            $body=kyma_prepare_import($body);
            $post=['post_type'=>'page','post_status'=>'publish','post_title'=>$entry['title'],
                   'post_name'=>$entry['slug'],'post_excerpt'=>$entry['description']??'','post_content'=>"<!-- wp:html -->\n".$body."\n<!-- /wp:html -->",
                   'comment_status'=>'closed','ping_status'=>'closed'];
            if ($existing) $post['ID']=$existing->ID;
            // These are reviewed theme assets, not a browser-supplied HTML payload.
            $kses=has_filter('content_save_pre','wp_filter_post_kses');
            if ($kses!==false) remove_filter('content_save_pre','wp_filter_post_kses',$kses);
            try { $id=wp_insert_post(wp_slash($post),true); }
            finally { if ($kses!==false) add_filter('content_save_pre','wp_filter_post_kses',$kses); }
            if (is_wp_error($id)) throw new RuntimeException($id->get_error_message());
            if (!$existing) $created[]=$id;
            foreach (['_elementor_data','_elementor_edit_mode','_wp_page_template','_yoast_wpseo_title','_yoast_wpseo_metadesc','rank_math_title','rank_math_description'] as $meta) delete_post_meta($id,$meta);
            update_post_meta($id,'_kyma_page_key',$key);
            update_post_meta($id,'_wp_page_template','default');
            $ids[$key]=$id;
            $backup['created_ids']=$created;
            kyma_store_backup($backup);
        }
        update_option('kyma_page_ids',$ids,false);
        foreach (kyma_seed('projects') as $project) {
            $id=$ids[$project['slug']]??0;
            if (!$id) continue;
            update_post_meta($id,'_kyma_project',$project['slug']);
            update_post_meta($id,'_kyma_progress',kyma_seed('project-updates')[$project['slug']]??[]);
        }
        // Archive previous public content; never delete old pages or articles.
        foreach ($legacy as $id) if (!in_array($id,$ids,true)) wp_update_post(['ID'=>$id,'post_status'=>'draft']);
        foreach (kyma_seed('blog') as $position=>$article) {
            $post=['post_type'=>'post','post_status'=>'publish','post_title'=>$article['title'],
                   'post_name'=>'noticia-'.$article['id'],'menu_order'=>$position,'post_content'=>$article['text'],
                   'comment_status'=>'closed','ping_status'=>'closed'];
            if (!empty($article['date'])) $post['post_date']=$article['date'].' 12:00:00';
            $id=wp_insert_post(wp_slash($post),true);
            if (is_wp_error($id)) throw new RuntimeException($id->get_error_message());
            $created[]=$id;
            update_post_meta($id,'_kyma_news',true);
            update_post_meta($id,'_kyma_seed_image',$article['image']);
            update_post_meta($id,'_kyma_project_slug',$article['project_slug']??'');
            update_post_meta($id,'_kyma_hide_seed_date',empty($article['date']));
            $backup['created_ids']=$created; kyma_store_backup($backup);
        }
        $menu=wp_create_nav_menu('Kyma, menu principal');
        if (is_wp_error($menu)) $menu=wp_create_nav_menu('Kyma, menu principal '.substr(wp_generate_uuid4(),0,8));
        if (is_wp_error($menu)) throw new RuntimeException('Não foi possível criar o menu principal.');
        foreach (['quem-somos','empreendimentos','blog','contato'] as $position=>$key) {
            $result=wp_update_nav_menu_item($menu,0,['menu-item-object-id'=>$ids[$key],'menu-item-object'=>'page',
                'menu-item-type'=>'post_type','menu-item-title'=>$manifest[$key]['title'],
                'menu-item-position'=>$position+1,'menu-item-status'=>'publish']);
            if (is_wp_error($result)) throw new RuntimeException($result->get_error_message());
        }
        set_theme_mod('nav_menu_locations',['primary'=>$menu]);
        update_option('show_on_front','page');update_option('page_on_front',$ids['inicio']);update_option('page_for_posts',0);
        update_option('blogname',$site['name']);update_option('blogdescription','O privilégio de viver o singular');update_option('site_icon',0);
        update_option('kyma_install_complete',KYMA_THEME_VERSION,false);delete_option('kyma_install_error');
        kyma_purge_cache();
    } catch (Throwable $error) {
        if ($backup_ready && isset($backup)) {
            $backup['created_ids']=$created??[];
            update_option('kyma_previous_site',$backup,false);
            kyma_restore_snapshot($backup);
        }
        update_option('kyma_install_error',$error->getMessage(),false);
    } finally { delete_option('kyma_install_lock'); }
}
