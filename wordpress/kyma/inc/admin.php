<?php
defined('ABSPATH') || exit;
add_action('admin_menu',function() {
    add_menu_page('Site Kyma','Kyma','manage_options','kyma','kyma_admin_screen','dashicons-building',3);
});
function kyma_admin_screen(): void {
    if (!current_user_can('manage_options')) return;
    echo '<div class="wrap"><h1>Site Kyma</h1>';
    if ($error=get_option('kyma_install_error')) echo '<div class="notice notice-error"><p>'.esc_html($error).'</p></div>';
    else echo '<div class="notice notice-success inline"><p>As páginas, o menu, as notícias e o acervo visual estão instalados.</p></div>';
    echo '<p><a class="button button-primary" href="'.esc_url(home_url('/')).'" target="_blank" rel="noopener">Ver site</a> <a class="button" href="'.esc_url(admin_url('edit.php')).'">Editar notícias</a> <a class="button" href="'.esc_url(admin_url('nav-menus.php')).'">Editar menu</a></p>';
    echo '<h2>Páginas e empreendimentos</h2><p>Abra uma página para editar seu conteúdo. Nos empreendimentos, o quadro “Evolução da obra” permite atualizar os percentuais e as etapas sem editar HTML.</p><ul>';
    foreach(kyma_page_ids() as $key=>$id) if(get_post($id)) echo '<li><a href="'.esc_url(get_edit_post_link($id)).'">'.esc_html(get_the_title($id)).'</a></li>';
    echo '</ul><h2>Restaurar o site anterior</h2><p>A ativação preservou o conteúdo antigo como rascunho e guardou os dados das páginas substituídas. Restaurar repõe o conteúdo, a página inicial, as configurações anteriores e o tema anterior, quando ele ainda está instalado. As páginas novas da Kyma ficam como rascunho.</p>';
    if (get_option('kyma_previous_site')) {
        echo '<form method="post" action="'.esc_url(admin_url('admin-post.php')).'"><input type="hidden" name="action" value="kyma_restore">';
        wp_nonce_field('kyma_restore');
        echo '<p><label><input type="checkbox" name="confirm" value="yes" required> Quero restaurar o conteúdo e a apresentação anteriores.</label></p><p><button class="button" type="submit">Restaurar site anterior</button></p></form>';
    }
    echo '</div>';
}
add_action('admin_post_kyma_restore',function() {
    if (!current_user_can('manage_options')) wp_die('Acesso não autorizado.',403);
    check_admin_referer('kyma_restore');
    if (($_POST['confirm']??'')!=='yes') wp_die('Confirme a restauração.');
    $backup=get_option('kyma_previous_site');
    if (!is_array($backup)) wp_die('Cópia anterior não encontrada.');
    kyma_restore_snapshot($backup,true);
    wp_safe_redirect(admin_url('themes.php?kyma-restored=1'));exit;
});
add_action('admin_notices',function() {
    if (!current_user_can('manage_options')) return;
    if ($error=get_option('kyma_install_error')) echo '<div class="notice notice-error"><p>Kyma: '.esc_html($error).' <a href="'.esc_url(kyma_admin_url()).'">Abrir configuração</a></p></div>';
});
add_action('add_meta_boxes_page',function($post) {
    if (get_post_meta($post->ID,'_kyma_project',true)) add_meta_box('kyma-progress','Evolução da obra','kyma_progress_metabox','page','normal','high');
});
function kyma_progress_metabox(WP_Post $post): void {
    $data=get_post_meta($post->ID,'_kyma_progress',true);$data=is_array($data)?$data:[];
    wp_nonce_field('kyma_save_progress','kyma_progress_nonce');
    echo '<p><label>Percentual geral (0 a 100; vazio = a informar)<br><input type="number" name="kyma_progress" min="0" max="100" step="0.1" value="'.esc_attr($data['progress_percent']??'').'"></label></p>';
    echo '<p><label><input type="checkbox" name="kyma_demo" value="1" '.checked(!empty($data['progress_is_demo']),true,false).'> Valores de demonstração, aguardando os oficiais</label></p>';
    echo '<p>Ao receber os números oficiais, atualize o geral e cada etapa e desmarque a demonstração. Uma etapa sem percentual mostra “a informar”.</p><table class="widefat"><thead><tr><th>Etapa</th><th>Percentual (%)</th></tr></thead><tbody>';
    $stages=(array)($data['progress_stages']??[]);$rows=max(8,count($stages)+2);
    for($i=0;$i<$rows;$i++) {
        $stage=$stages[$i]??[];
        echo '<tr><td><input style="width:100%" name="kyma_stage_name['.$i.']" value="'.esc_attr($stage['name']??'').'"></td><td><input type="number" name="kyma_stage_percent['.$i.']" min="0" max="100" step="0.1" value="'.esc_attr($stage['percent']??'').'"></td></tr>';
    }
    echo '</tbody></table><p>Para remover uma etapa, deixe seu nome vazio. Clique em Atualizar/Salvar na página para publicar as alterações.</p>';
}
function kyma_parse_percent($raw) {
    if (!is_scalar($raw)) return null;
    $raw=trim((string)$raw);if($raw==='') return null;
    $raw=str_replace(',','.',$raw);
    return is_numeric($raw)?max(0,min(100,(float)$raw)):null;
}
add_action('save_post_page',function($id) {
    if (wp_is_post_revision($id) || wp_is_post_autosave($id)) return;
    if (!current_user_can('edit_post',$id) || !get_post_meta($id,'_kyma_project',true)) return;
    if (!isset($_POST['kyma_progress_nonce']) || !wp_verify_nonce(sanitize_text_field(wp_unslash($_POST['kyma_progress_nonce'])),'kyma_save_progress')) return;
    $data=get_post_meta($id,'_kyma_progress',true);$data=is_array($data)?$data:[];
    $data['progress_percent']=kyma_parse_percent(wp_unslash($_POST['kyma_progress']??''));
    $data['progress_is_demo']=isset($_POST['kyma_demo']);
    $data['progress_source']='Atualizado no WordPress em '.current_time('mysql');
    $names=wp_unslash($_POST['kyma_stage_name']??[]);$values=wp_unslash($_POST['kyma_stage_percent']??[]);
    $data['progress_stages']=[];
    foreach(array_slice(is_array($names)?$names:[],0,50,true) as $i=>$name) {
        if (!is_string($name)) continue;$name=sanitize_text_field($name);
        if($name!=='')$data['progress_stages'][]=['name'=>$name,'percent'=>kyma_parse_percent($values[$i]??'')];
    }
    update_post_meta($id,'_kyma_progress',$data);
    if(function_exists('clean_post_cache')) clean_post_cache($id);
});
