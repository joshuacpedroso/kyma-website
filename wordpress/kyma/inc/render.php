<?php
defined('ABSPATH') || exit;

function kyma_enqueue(): void {
    $uri=get_template_directory_uri();
    wp_enqueue_style('kyma-fonts',$uri.'/assets/fonts/fonts.css',[],KYMA_THEME_VERSION);
    wp_enqueue_style('kyma-leaflet',$uri.'/assets/vendor/leaflet/leaflet.css',[],KYMA_THEME_VERSION);
    wp_enqueue_style('kyma-visual',$uri.'/assets/css/style.css',['kyma-fonts','kyma-leaflet'],KYMA_THEME_VERSION);
    wp_enqueue_style('kyma-wordpress',$uri.'/assets/css/wordpress.css',['kyma-visual'],KYMA_THEME_VERSION);
    $settings=['siteUrl'=>untrailingslashit(home_url()),'themeUrl'=>$uri,'projects'=>[]];
    foreach (kyma_seed('projects') as $project) {
        $progress=kyma_progress_data($project['slug']);
        $settings['projects'][$project['slug']]=['url'=>kyma_local_url('/'.$project['slug']),
            'thumb'=>kyma_asset_url($project['card'][0]),'progress'=>$progress['progress_percent']??null,
            'progressIsDemo'=>!empty($progress['progress_is_demo'])];
    }
    wp_enqueue_script('kyma-data',$uri.'/assets/js/data.js',[],KYMA_THEME_VERSION,['strategy'=>'defer','in_footer'=>true]);
    wp_add_inline_script('kyma-data','window.KYMA_WORDPRESS='.wp_json_encode($settings,JSON_HEX_TAG|JSON_HEX_AMP|JSON_HEX_APOS|JSON_HEX_QUOT).';','before');
    wp_enqueue_script('kyma-leaflet',$uri.'/assets/vendor/leaflet/leaflet.js',[],KYMA_THEME_VERSION,['strategy'=>'defer','in_footer'=>true]);
    wp_enqueue_script('kyma-main',$uri.'/assets/js/main.js',['kyma-data','kyma-leaflet'],KYMA_THEME_VERSION,['strategy'=>'defer','in_footer'=>true]);
    wp_enqueue_script('kyma-chat',$uri.'/assets/js/chat.js',['kyma-main'],KYMA_THEME_VERSION,['strategy'=>'defer','in_footer'=>true]);
}
function kyma_menu_attributes(array $attrs,$item,$args,$depth): array {
    if (($args->theme_location??'')!=='primary') return $attrs;
    if (($args->kyma_variant??'')==='mobile') $attrs['class']=trim(($attrs['class']??'').' menu-link');
    if (get_post_meta(get_queried_object_id(),'_kyma_project',true)) {
        $id=kyma_page_ids()['empreendimentos']??0;
        if ((int)$item->object_id===(int)$id) $attrs['aria-current']='page';
    }
    return $attrs;
}
function kyma_menu(string $variant='desktop'): string {
    return (string)wp_nav_menu(['theme_location'=>'primary','echo'=>false,'container'=>false,
        'fallback_cb'=>false,'menu_class'=>'kyma-'.$variant.'-list','kyma_variant'=>$variant,
        'items_wrap'=>$variant==='mobile'?'<ol>%3$s</ol>':'<ul class="%2$s">%3$s</ul>']);
}
function kyma_render_document(?string $forced=null): void {
    $id=get_queried_object_id();$post=get_post($id);
    $key=$forced??(is_front_page()?'inicio':(string)get_post_meta($id,'_kyma_page_key',true));
    $manifest=kyma_seed('pages');
    if ($key!=='404' && !isset($manifest[$key])) $key='blog';
    $file=get_template_directory().'/shells/'.$key.'.html';
    if (!is_file($file)) $file=get_template_directory().'/shells/404.html';
    $html=file_get_contents($file);
    if ($key==='404') $body=file_get_contents(get_template_directory().'/pages/404.html');
    elseif ($post && $post->post_type==='post') {
        $title='<section class="page-hero page-hero--short"><div class="page-hero__content"><div class="container"><p class="eyebrow">Notícias Kyma</p><h1 class="h1">'.esc_html($post->post_title).'</h1></div></div></section>';
        $body=$title.kyma_news_article($post);
    } elseif ($post && is_singular()) $body=apply_filters('the_content',$post->post_content);
    elseif (is_search()) {
        $body='<section class="section"><div class="container"><h1 class="h1">Resultados da busca</h1>';
        if (have_posts()) { while(have_posts()) { the_post();$body.='<p><a href="'.esc_url(get_permalink()).'">'.esc_html(get_the_title()).'</a></p>'; } }
        else $body.='<p>Nenhum resultado encontrado.</p>';
        $body.='</div></section>';
    } else $body=kyma_news_archive();
    $html=str_replace('<!-- KYMA_CONTENT -->',$body,$html);
    $desktop=kyma_menu('desktop');$mobile=kyma_menu('mobile');
    if ($desktop) $html=preg_replace('~(<nav class="nav"[^>]*>).*?(</nav>)~s','$1'.$desktop.'$2',$html,1);
    if ($mobile) $html=preg_replace('~(<nav aria-label="Menu">).*?(</nav>)~s','$1'.$mobile.'$2',$html,1);
    $html=kyma_rewrite_html($html);
    // WordPress owns the document title and canonical URL.
    $html=preg_replace('~<title>.*?</title>\s*~s','',$html);
    $html=preg_replace('~<link rel="canonical"[^>]*>\s*~','',$html);
    $title=wp_get_document_title();
    $html=preg_replace_callback('~(<meta (?:property|name)="(?:og:title|twitter:title)" content=")[^"]*(">)~',function($m)use($title){return $m[1].esc_attr($title).$m[2];},$html);
    if (is_singular()) {
        $url=get_permalink($id);
        $html=preg_replace_callback('~(<meta property="og:url" content=")[^"]*(">)~',function($m)use($url){return $m[1].esc_url($url).$m[2];},$html);
    }
    if (defined('WPSEO_VERSION') || defined('RANK_MATH_VERSION') || defined('AIOSEO_VERSION')) {
        $html=preg_replace('~<meta (?:property|name)="(?:og:[^"]+|twitter:[^"]+|description)"[^>]*>\s*~','',$html);
        $html=preg_replace('~<script type="application/ld\+json">.*?</script>\s*~s','',$html);
    }
    $head=explode('</head>',$html,2);
    echo $head[0];wp_head();echo "</head>\n";
    $body_parts=explode('</body>',$head[1]??'',2);
    $body_markup=$body_parts[0];
    if (preg_match('~<body([^>]*)>~',$body_markup,$match,PREG_OFFSET_CAPTURE)) {
        $tag=$match[0][0];$offset=$match[0][1];
        $tag=preg_replace('~>$~',' class="'.esc_attr(implode(' ',get_body_class('kyma-wordpress'))).'">',$tag);
        echo substr($body_markup,0,$offset).$tag;
        wp_body_open();
        echo substr($body_markup,$offset+strlen($match[0][0]));
    } else echo $body_markup;
    wp_footer();echo "</body>\n".($body_parts[1]??'</html>');
}
add_action('rest_api_init',function() {
    register_rest_route('kyma/v1','/manifest',['methods'=>'GET','permission_callback'=>'__return_true','callback'=>function() {
        $site=kyma_seed('site');
        return new WP_REST_Response(['name'=>$site['name'],'short_name'=>'Kyma','start_url'=>home_url('/'),
            'display'=>'standalone','background_color'=>'#ffffff','theme_color'=>'#303F1F',
            'icons'=>[['src'=>kyma_asset_url($site['favicon']),'sizes'=>'any','type'=>'image/png']]],200);
    }]);
});
