<?php
defined('ABSPATH') || exit;
define('KYMA_THEME_VERSION', '1.0.0');
require_once __DIR__.'/inc/setup.php';
require_once __DIR__.'/inc/content.php';
require_once __DIR__.'/inc/render.php';
require_once __DIR__.'/inc/admin.php';

add_action('after_setup_theme', function () {
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('responsive-embeds');
    add_theme_support('html5', ['search-form','gallery','caption','style','script']);
    register_nav_menus(['primary'=>'Menu principal Kyma']);
});
add_action('after_switch_theme', 'kyma_activate', 10, 2);
add_action('init', function () { add_rewrite_rule('^adm/?$', 'index.php?kyma_adm=1', 'top'); });
add_filter('query_vars', function ($vars) { $vars[]='kyma_adm'; return $vars; });
add_action('template_redirect', function () {
    if (get_query_var('kyma_adm')) {
        wp_safe_redirect(is_user_logged_in() ? admin_url('admin.php?page=kyma') : wp_login_url(admin_url('admin.php?page=kyma')));
        exit;
    }
});
add_action('wp_enqueue_scripts', 'kyma_enqueue', 100);
add_filter('template_include', function ($template) {
    if (is_feed() || is_embed()) return $template;
    return get_template_directory().(is_404()?'/404.php':'/index.php');
}, PHP_INT_MAX);
add_shortcode('kyma_news_highlights', 'kyma_news_highlights');
add_shortcode('kyma_news_archive', 'kyma_news_archive');
add_shortcode('kyma_progress', 'kyma_progress_shortcode');
add_filter('nav_menu_link_attributes', 'kyma_menu_attributes', 10, 4);

add_filter('document_title_separator',function(){return '|';});
add_filter('document_title_parts',function($parts){
    $id=get_queried_object_id();$key=is_front_page()?'inicio':(string)get_post_meta($id,'_kyma_page_key',true);$entry=kyma_seed('pages')[$key]??null;
    if($entry && get_the_title($id)===$entry['title']){$parts['title']=$entry['seo_title'];unset($parts['site'],$parts['tagline']);}
    return $parts;
});
add_filter('request',function($vars){
    if(isset($vars['feed'])||isset($vars['rest_route'])||isset($vars['preview']))return $vars;
    global $wp;$path=trim((string)($wp->request??''),'/');$page=1;
    if(preg_match('#^blog/page/(\d+)$#',$path,$match)){$path='blog';$page=(int)$match[1];}
    $id=kyma_page_ids()[$path]??0;
    if($id && get_post_status($id)==='publish')return ['page_id'=>$id,'paged'=>$page];
    return $vars;
},100);

// A theme ZIP can replace a same-named, already-active legacy theme. In that
// case WordPress does not fire after_switch_theme. Complete the first setup
// on the next genuine admin visit, never in a Customizer preview or after restore.
add_action('admin_init',function(){
    if (!current_user_can('switch_themes') || is_customize_preview()) return;
    if (isset($_GET['wp_theme_preview']) || isset($_GET['customize_theme'])) return;
    if (get_option('kyma_install_complete',null)===null && !get_option('kyma_install_error')) kyma_activate();
},5);
