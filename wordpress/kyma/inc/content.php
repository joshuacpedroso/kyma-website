<?php
defined('ABSPATH') || exit;

function kyma_asset_url(string $path): string {
    $path='/'.ltrim($path,'/');
    if (function_exists('kyma_image_overrides') && isset(kyma_image_overrides()[$path])) return kyma_image_overrides()[$path];
    return get_template_directory_uri().$path;
}
function kyma_local_url(string $path): string {
    if ($path==='/site.webmanifest') return rest_url('kyma/v1/manifest');
    if (str_starts_with($path,'/assets/')) return kyma_asset_url($path);
    $parts=wp_parse_url($path); $slug=trim($parts['path']??'','/');
    if ($slug==='') $url=home_url('/');
    else {
        $slug=preg_replace('/\.html$/','',$slug);
        $key=$slug==='home'?'inicio':($slug==='serra-sincora'?'serra-do-sincora':$slug);
        $id=kyma_page_ids()[$key]??0;
        $page=$id?get_post($id):get_page_by_path($key,OBJECT,'page');
        $url=$page?get_permalink($page):home_url('/'.$slug.'/');
    }
    if (!empty($parts['query'])) $url.=(str_contains($url,'?')?'&':'?').$parts['query'];
    if (!empty($parts['fragment'])) $url.='#'.$parts['fragment'];
    return $url;
}
function kyma_rewrite_html(string $html): string {
    $old_theme=(string)get_option('kyma_seed_theme_url','');
    if ($old_theme) $html=str_replace($old_theme,get_template_directory_uri(),$html);
    $old_site=(string)get_option('kyma_seed_site_url','');
    if ($old_site && $old_site!==untrailingslashit(home_url())) $html=str_replace($old_site,untrailingslashit(home_url()),$html);
    $html=str_replace('https://kyma.com.br',untrailingslashit(home_url()),$html);
    // Rewrite only actual root-relative attributes; keep SVG #references and remote embeds.
    $html=preg_replace_callback('~\b(src|href|poster|action)=("|\')(/(?!/)[^"\']*)\2~',function($m) {
        return $m[1].'='.$m[2].esc_url(kyma_local_url(html_entity_decode($m[3],ENT_QUOTES,'UTF-8'))).$m[2];
    },$html);
    return $html;
}
function kyma_prepare_import(string $html): string { return kyma_rewrite_html($html); }
function kyma_icon(string $key): string {
    return '<svg aria-hidden="true"><use href="#i-'.esc_attr($key).'"/></svg>';
}
function kyma_image(string $src,string $alt,int $w=1200,int $h=800): string {
    if (str_starts_with($src,'/')) $src=kyma_local_url($src);
    return '<img src="'.esc_url($src).'" alt="'.esc_attr($alt).'" width="'.$w.'" height="'.$h.'" loading="lazy" decoding="async">';
}
function kyma_news_posts(int $count=3,int $page=1): WP_Query {
    return new WP_Query(['post_type'=>'post','post_status'=>'publish','posts_per_page'=>$count,'paged'=>$page,
        'orderby'=>['menu_order'=>'ASC','date'=>'DESC','ID'=>'DESC'],'ignore_sticky_posts'=>true]);
}
function kyma_news_image(WP_Post $post): string {
    $featured=get_the_post_thumbnail_url($post,'large');
    return $featured?:((string)get_post_meta($post->ID,'_kyma_seed_image',true)?:kyma_seed('site')['logo']);
}
function kyma_news_date(WP_Post $post): string {
    if (get_post_meta($post->ID,'_kyma_hide_seed_date',true)) return '';
    return '<time datetime="'.esc_attr(get_the_date('c',$post)).'">'.esc_html(get_the_date('d/m/Y',$post)).'</time>';
}
function kyma_news_highlights(): string {
    $posts=kyma_news_posts(3)->posts; $cards='';
    foreach ($posts as $post) {
        $excerpt=$post->post_excerpt?:wp_trim_words(wp_strip_all_tags(strip_shortcodes($post->post_content)),32);
        $url=get_permalink($post);
        $cards.='<article class="card"><a class="card__media" href="'.esc_url($url).'">'.kyma_image(kyma_news_image($post),$post->post_title).'</a><div><p class="eyebrow">Notícias</p>'.kyma_news_date($post).'<h3 class="card__title"><a href="'.esc_url($url).'">'.esc_html($post->post_title).'</a></h3><p class="muted">'.esc_html($excerpt).'</p></div></article>';
    }
    return '<section class="section theme-ink2 news-highlights"><div class="container"><div class="section-head section-head--split"><div><p class="eyebrow">Blog</p><h2 class="h1">'.wp_kses_post(kyma_seed('site')['texts']['news_heading']).'</h2></div><a class="btn" href="'.esc_url(kyma_local_url('/blog')).'">Ver notícias '.kyma_icon('arrow').'</a></div><div class="cards">'.$cards.'</div></div></section>';
}
function kyma_news_article(WP_Post $post): string {
    $slug=(string)get_post_meta($post->ID,'_kyma_project_slug',true);
    $related='';
    foreach (kyma_seed('projects') as $project) if ($project['slug']===$slug) {
        $related='<a class="btn" href="'.esc_url(kyma_local_url('/'.$slug)).'">Conhecer o '.esc_html($project['name']).' '.kyma_icon('arrow').'</a>';
        break;
    }
    $content=apply_filters('the_content',$post->post_content);
    return '<article class="section" id="noticia-'.absint($post->ID).'"><div class="container"><div class="split"><div class="split__media">'.kyma_image(kyma_news_image($post),$post->post_title).'</div><div class="split__body"><p class="eyebrow">Notícias</p>'.kyma_news_date($post).'<h2 class="h2">'.esc_html($post->post_title).'</h2><div class="kyma-entry-content">'.$content.'</div>'.$related.'</div></div></div></article>';
}
function kyma_news_archive(): string {
    $query=kyma_news_posts(10,max(1,(int)get_query_var('paged'),(int)get_query_var('page')));
    $html='';
    foreach ($query->posts as $post) $html.=kyma_news_article($post);
    if (!$query->posts) $html='<section class="section"><div class="container"><p class="lead">Nenhuma notícia publicada.</p></div></section>';
    $links=paginate_links(['total'=>$query->max_num_pages,'current'=>max(1,(int)get_query_var('paged'),(int)get_query_var('page')),'type'=>'list']);
    if ($links) $html.='<nav class="container kyma-pagination" aria-label="Paginação das notícias">'.$links.'</nav>';
    return $html;
}
function kyma_progress_data(string $slug): array {
    $id=kyma_page_ids()[$slug]??0;
    $meta=$id?get_post_meta($id,'_kyma_progress',true):null;
    return is_array($meta)?$meta:(kyma_seed('project-updates')[$slug]??[]);
}
function kyma_percent_label($value): string { return $value===null?'A informar':rtrim(rtrim(number_format((float)$value,1,'.',''),'0'),'.').'%'; }
function kyma_progress_shortcode($attrs=[]): string {
    $attrs=shortcode_atts(['project'=>''],$attrs,'kyma_progress');$slug=sanitize_title($attrs['project']);
    $project=null;foreach(kyma_seed('projects') as $candidate)if($candidate['slug']===$slug){$project=$candidate;break;}
    if (!$project) return '';
    $data=kyma_progress_data($slug);$value=$data['progress_percent']??null;$demo=!empty($data['progress_is_demo']);
    $delivered=$project['status']==='entregue' && (float)$value===100.0;
    $target=$value===null?'':(string)$value;$label=kyma_percent_label($value);
    $description=$demo?'Percentuais ilustrativos para visualizar as animações. Aguardando os valores oficiais.':($delivered?'Empreendimento entregue.':($value===null?'Percentual a informar. Entre em contato para acompanhar a evolução da obra.':'Acompanhe a evolução da obra.'));
    $stages='';
    foreach(($data['progress_stages']??[]) as $i=>$stage) {
        $percent=$stage['percent']??null;$text=kyma_percent_label($percent);$number=$percent===null?'':(string)$percent;
        $aria=$percent===null?'':' aria-valuenow="'.esc_attr($number).'"';
        $stages.='<div class="build-stage" data-progress-stage data-progress-target="'.esc_attr($number).'" style="--stage-index:'.absint($i).'"><div class="build-stage__label"><span>'.esc_html($stage['name']).'</span><strong data-progress-count>'.esc_html($text).'</strong></div><div class="build-stage__track" role="progressbar" aria-label="'.esc_attr($stage['name']).'" aria-valuemin="0" aria-valuemax="100"'.$aria.' aria-valuetext="'.esc_attr($text).'"><span data-progress-fill style="--progress-value:'.esc_attr($percent??0).'%"></span></div></div>';
    }
    if (!$stages && !$delivered) $stages='<p class="build-progress__pending">Etapas detalhadas a informar.</p>';
    $stage_panel=$stages?'<div class="build-progress__stages">'.$stages.'</div>':'';
    $badge=$demo?'<span class="build-progress__demo">Valores de demonstração</span>':'';
    $aria=$value===null?'':' aria-valuenow="'.esc_attr($target).'"';
    $wa=$project['wa_link']??'https://wa.me/'.kyma_seed('site')['whatsapp'];
    return '<section class="section theme-ink2 build-progress" id="evolucao" data-progress="'.esc_attr($target).'" data-progress-section><div class="container build-progress__panel"><div class="build-progress__intro"><p class="eyebrow">'.esc_html($project['name']).'</p><h2 class="h2">Evolução <em>da obra.</em></h2>'.$badge.'<p class="lead">'.esc_html($description).'</p><a class="link-arrow" href="'.esc_url($wa).'" target="_blank" rel="noopener">Entre em contato '.kyma_icon('arrow').'</a></div><div class="build-progress__overall" data-progress-overall data-progress-target="'.esc_attr($target).'" role="progressbar" aria-label="Evolução geral da obra" aria-valuemin="0" aria-valuemax="100"'.$aria.' aria-valuetext="'.esc_attr($label).'"><svg class="build-progress__ring" viewBox="0 0 180 180" aria-hidden="true"><circle class="build-progress__track" cx="90" cy="90" r="76"/><circle class="build-progress__fill" data-progress-ring cx="90" cy="90" r="76" pathLength="100" stroke-dasharray="100" style="stroke-dashoffset:'.esc_attr($value===null?100:100-$value).'"/></svg><div class="build-progress__number"><strong data-progress-count>'.esc_html($label).'</strong><span>Evolução geral</span></div></div>'.$stage_panel.'</div></section>';
}
