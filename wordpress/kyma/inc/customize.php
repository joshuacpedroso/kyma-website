<?php
/**
 * Editable appearance: colors, fonts, images, contacts and fixed texts.
 * Everything is stored as theme mods (Appearance → Customize, with live preview)
 * or, for images, in the kyma_image_overrides option (Kyma → Imagens).
 */
defined('ABSPATH') || exit;

/* ---------------------------------------------------------------------------
 * Palette
 * ------------------------------------------------------------------------- */
function kyma_palette(): array {
    return [
        'verde_escuro' => ['Verde escuro (cor principal, fundos e títulos)', '#303f1f'],
        'verde_medio'  => ['Verde médio (detalhes e ícones)', '#6c8b44'],
        'verde_vivo'   => ['Verde de destaque (botões, barras e links)', '#94be43'],
        'verde_claro'  => ['Verde claro (textos sobre fundo escuro)', '#c1d897'],
        'grafite'      => ['Grafite (texto principal)', '#414042'],
        'cinza'        => ['Cinza (texto secundário)', '#595a5a'],
        'branco'       => ['Branco (fundo das páginas)', '#ffffff'],
        'fundo_suave'  => ['Fundo suave (seções alternadas)', '#f7f7f5'],
        'fundo_neutro' => ['Fundo neutro (cartões e blocos)', '#eeefed'],
    ];
}
/** Map of original hex (lowercase, 6 digits) => chosen hex, only for changed colors. */
function kyma_color_map(): array {
    $map = [];
    foreach (kyma_palette() as $key => [$label, $default]) {
        $value = sanitize_hex_color((string)get_theme_mod('kyma_color_'.$key, $default));
        if (!$value) continue;
        $value = strtolower(kyma_hex6($value));
        if ($value !== $default) $map[$default] = $value;
    }
    return $map;
}
function kyma_hex6(string $hex): string {
    $hex = ltrim($hex, '#');
    if (strlen($hex) === 3) $hex = $hex[0].$hex[0].$hex[1].$hex[1].$hex[2].$hex[2];
    return '#'.strtolower($hex);
}
function kyma_hex_rgb(string $hex): array {
    $hex = ltrim(kyma_hex6($hex), '#');
    return [hexdec(substr($hex, 0, 2)), hexdec(substr($hex, 2, 2)), hexdec(substr($hex, 4, 2))];
}
/** Swap every palette color in CSS/HTML: #hex, #hex3, rgb()/rgba() and SVG color matrices. */
function kyma_recolor(string $text, ?array $map = null): string {
    $map = $map ?? kyma_color_map();
    if (!$map) return $text;
    $text = preg_replace_callback('/#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})(?![0-9a-fA-F\w-])/', function ($m) use ($map) {
        $key = kyma_hex6($m[1]);
        return $map[$key] ?? $m[0];
    }, $text);
    $rgb = [];
    foreach ($map as $old => $new) $rgb[implode(',', kyma_hex_rgb($old))] = kyma_hex_rgb($new);
    $text = preg_replace_callback('/(rgba?\(\s*)(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})/i', function ($m) use ($rgb) {
        $new = $rgb[$m[2].','.$m[3].','.$m[4]] ?? null;
        return $new ? $m[1].implode(',', $new) : $m[0];
    }, $text);
    // Logo tints are SVG feColorMatrix filters: "0 0 0 0 R 0 0 0 0 G 0 0 0 0 B".
    $text = preg_replace_callback('/0 0 0 0 ([\d.]+) 0 0 0 0 ([\d.]+) 0 0 0 0 ([\d.]+)/', function ($m) use ($rgb) {
        $key = implode(',', array_map(fn($v) => (int)round((float)$v * 255), [$m[1], $m[2], $m[3]]));
        $new = $rgb[$key] ?? null;
        if (!$new) return $m[0];
        $f = fn($c) => rtrim(rtrim(number_format($c / 255, 5, '.', ''), '0'), '.') ?: '0';
        return '0 0 0 0 '.$f($new[0]).' 0 0 0 0 '.$f($new[1]).' 0 0 0 0 '.$f($new[2]);
    }, $text);
    return $text;
}

/* ---------------------------------------------------------------------------
 * Fonts
 * ------------------------------------------------------------------------- */
/** name => [Google Fonts css2 family spec, or '' when bundled in the theme; generic fallback]. */
function kyma_fonts(): array {
    return [
        'Playfair Display'   => ['', 'serif'],
        'Inter'              => ['', 'sans-serif'],
        'Cormorant Garamond' => ['', 'serif'],
        'Montserrat'         => ['Montserrat:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400', 'sans-serif'],
        'Poppins'            => ['Poppins:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400', 'sans-serif'],
        'Open Sans'          => ['Open+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400', 'sans-serif'],
        'Roboto'             => ['Roboto:ital,wght@0,300;0,400;0,500;0,700;1,400', 'sans-serif'],
        'Lato'               => ['Lato:ital,wght@0,300;0,400;0,700;1,400', 'sans-serif'],
        'Raleway'            => ['Raleway:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400', 'sans-serif'],
        'Nunito'             => ['Nunito:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400', 'sans-serif'],
        'DM Sans'            => ['DM+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400', 'sans-serif'],
        'Work Sans'          => ['Work+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400', 'sans-serif'],
        'Josefin Sans'       => ['Josefin+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400', 'sans-serif'],
        'Manrope'            => ['Manrope:wght@300;400;500;600;700', 'sans-serif'],
        'Outfit'             => ['Outfit:wght@300;400;500;600;700', 'sans-serif'],
        'Lora'               => ['Lora:ital,wght@0,400;0,500;0,600;0,700;1,400', 'serif'],
        'Merriweather'       => ['Merriweather:ital,wght@0,300;0,400;0,700;1,400', 'serif'],
        'Libre Baskerville'  => ['Libre+Baskerville:ital,wght@0,400;0,700;1,400', 'serif'],
        'EB Garamond'        => ['EB+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400', 'serif'],
        'Bodoni Moda'        => ['Bodoni+Moda:ital,wght@0,400;0,500;0,600;0,700;1,400', 'serif'],
        'DM Serif Display'   => ['DM+Serif+Display:ital@0;1', 'serif'],
        'Cinzel'             => ['Cinzel:wght@400;500;600;700', 'serif'],
        'Marcellus'          => ['Marcellus', 'serif'],
    ];
}
function kyma_font_roles(): array {
    return [
        'titulos'  => ['Fonte dos títulos', 'Playfair Display'],
        'textos'   => ['Fonte dos textos, menus e botões', 'Inter'],
        'destaque' => ['Fonte de destaque (frase do carrossel e números da evolução)', 'Cormorant Garamond'],
    ];
}
/** Returns [family, generic fallback, Google spec or ''] for a role. */
function kyma_font(string $role): array {
    [, $default] = kyma_font_roles()[$role];
    $fonts = kyma_fonts();
    $custom = trim((string)get_theme_mod('kyma_font_'.$role.'_custom', ''));
    if ($custom !== '') {
        $custom = preg_replace('/[^\p{L}\p{N} \-]/u', '', $custom);
        if ($custom !== '') {
            if (isset($fonts[$custom])) return [$custom, $fonts[$custom][1], $fonts[$custom][0]];
            return [$custom, $role === 'textos' ? 'sans-serif' : 'serif', str_replace(' ', '+', $custom)];
        }
    }
    $name = (string)get_theme_mod('kyma_font_'.$role, $default);
    if (!isset($fonts[$name])) $name = $default;
    return [$name, $fonts[$name][1], $fonts[$name][0]];
}
function kyma_font_stack(array $font): string {
    $fallback = $font[1] === 'serif' ? 'Georgia, "Times New Roman", serif' : 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif';
    return '"'.$font[0].'", '.$fallback;
}

/* ---------------------------------------------------------------------------
 * Images
 * ------------------------------------------------------------------------- */
/** Every replaceable image shipped in the theme: '/assets/img/…' paths. */
function kyma_theme_images(): array {
    $base = get_template_directory();
    $dir = $base.'/assets/img';
    if (!is_dir($dir)) return [];
    $list = [];
    $it = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($dir, FilesystemIterator::SKIP_DOTS));
    foreach ($it as $file) {
        if (!$file->isFile() || !preg_match('/\.(jpe?g|png|webp|gif|svg|avif)$/i', $file->getFilename())) continue;
        $list[] = '/'.ltrim(str_replace('\\', '/', substr($file->getPathname(), strlen($base))), '/');
    }
    sort($list, SORT_NATURAL | SORT_FLAG_CASE);
    return $list;
}
/** '/assets/img/…' => replacement URL, for images swapped in Kyma → Imagens. */
function kyma_image_overrides(): array {
    static $cache = null;
    if ($cache !== null) return $cache;
    $cache = [];
    foreach ((array)get_option('kyma_image_overrides', []) as $path => $id) {
        $url = $id ? wp_get_attachment_url((int)$id) : '';
        if ($url) $cache['/'.ltrim((string)$path, '/')] = $url;
    }
    return $cache;
}

/* ---------------------------------------------------------------------------
 * Contacts and fixed texts
 * ------------------------------------------------------------------------- */
function kyma_contact_fields(): array {
    $site = kyma_seed('site');
    return [
        'telefone'  => ['Telefone (como aparece no site)', $site['phone'] ?? ''],
        'whatsapp'  => ['WhatsApp (só números, com 55 e DDD)', $site['whatsapp'] ?? ''],
        'instagram' => ['Instagram (usuário, sem @)', $site['instagram'] ?? ''],
        'endereco'  => ['Endereço', $site['address'] ?? ''],
    ];
}
function kyma_contact(string $key): string {
    $fields = kyma_contact_fields();
    $value = trim((string)get_theme_mod('kyma_contact_'.$key, ''));
    if ($key === 'whatsapp') $value = preg_replace('/\D+/', '', $value);
    if ($key === 'instagram') $value = ltrim(preg_replace('/[^A-Za-z0-9._@]/', '', $value), '@');
    return $value !== '' ? $value : (string)($fields[$key][1] ?? '');
}
function kyma_phone_tel(string $phone): string {
    $digits = preg_replace('/\D+/', '', $phone);
    if ($digits === '') return '';
    if (strlen($digits) <= 11) $digits = '55'.$digits;
    return '+'.$digits;
}
/** Pairs [search => replace] that move the original contacts to the edited ones. */
function kyma_contact_replacements(): array {
    $site = kyma_seed('site');
    $pairs = [];
    $phone = kyma_contact('telefone');
    if (!empty($site['phone']) && $phone !== $site['phone']) {
        $pairs[$site['phone']] = $phone;
        if (!empty($site['phone_intl'])) $pairs['+'.ltrim($site['phone_intl'], '+')] = kyma_phone_tel($phone);
    }
    $wa = kyma_contact('whatsapp');
    if (!empty($site['whatsapp']) && $wa !== $site['whatsapp']) $pairs[$site['whatsapp']] = $wa;
    $insta = kyma_contact('instagram');
    if (!empty($site['instagram']) && $insta !== $site['instagram']) {
        $pairs['instagram.com/'.$site['instagram']] = 'instagram.com/'.$insta;
        $pairs['@'.$site['instagram']] = '@'.$insta;
    }
    $address = kyma_contact('endereco');
    if (!empty($site['address']) && $address !== $site['address']) {
        $pairs[$site['address']] = $address;
        $pairs[esc_html($site['address'])] = esc_html($address);
        if (!empty($site['maps_query'])) $pairs['query='.rawurlencode($site['maps_query'])] = 'query='.rawurlencode($address);
    }
    return $pairs;
}
/** Free text swaps typed by the editor, one per line: "texto antigo => texto novo". */
function kyma_text_replacements(): array {
    $pairs = [];
    foreach (preg_split('/\R/', (string)get_theme_mod('kyma_text_swaps', '')) as $line) {
        if (!str_contains($line, '=>')) continue;
        [$old, $new] = array_map('trim', explode('=>', $line, 2));
        if (mb_strlen($old) >= 3) $pairs[$old] = $new;
    }
    return $pairs;
}
/** Applies text swaps only to visible text, never inside tags, scripts or styles. */
function kyma_replace_visible_text(string $html, array $pairs): string {
    if (!$pairs) return $html;
    $escaped = [];
    foreach ($pairs as $old => $new) $escaped[esc_html($old)] = esc_html($new);
    $escaped += $pairs;
    $parts = preg_split('~(<script\b.*?</script>|<style\b.*?</style>|<[^>]+>)~is', $html, -1, PREG_SPLIT_DELIM_CAPTURE);
    foreach ($parts as $i => $part) if ($i % 2 === 0 && $part !== '') $parts[$i] = strtr($part, $escaped);
    return implode('', $parts);
}

/* ---------------------------------------------------------------------------
 * Output filters used by render.php
 * ------------------------------------------------------------------------- */
function kyma_apply_customizations(string $html): string {
    $theme = get_template_directory_uri();
    // Open Graph images point at the old domain's /assets folder; serve them from the theme.
    $html = str_replace(untrailingslashit(home_url()).'/assets/', $theme.'/assets/', $html);
    foreach (kyma_image_overrides() as $path => $url) {
        $html = str_replace([$theme.$path, esc_url($theme.$path)], $url, $html);
    }
    if ($pairs = kyma_contact_replacements()) $html = strtr($html, $pairs);
    $html = kyma_replace_visible_text($html, kyma_text_replacements());
    return kyma_recolor($html);
}
/** Contacts and image swaps for the JavaScript data (cards, map, concierge). */
function kyma_js_overrides(): array {
    $address = kyma_contact('endereco');
    $images = [];
    foreach (kyma_image_overrides() as $path => $url) $images[$path] = $url;
    return [
        'contact' => [
            'whatsapp' => kyma_contact('whatsapp'), 'phone' => kyma_contact('telefone'),
            'instagram' => kyma_contact('instagram'), 'address' => $address,
            'mapsUrl' => 'https://www.google.com/maps/search/?api=1&query='.rawurlencode(
                $address === (kyma_seed('site')['address'] ?? '') ? (kyma_seed('site')['maps_query'] ?? $address) : $address),
        ],
        'images' => $images, 'themeUrl' => get_template_directory_uri(),
    ];
}

/** Main stylesheet: the original file, or a recolored copy when the palette changed. */
function kyma_stylesheet_src(): array {
    $original = get_template_directory().'/assets/css/style.css';
    $uri = get_template_directory_uri().'/assets/css/style.css';
    $map = kyma_color_map();
    if (!$map) return [$uri, ''];
    $css = (string)file_get_contents($original);
    $css = str_replace('../fonts/', get_template_directory_uri().'/assets/fonts/', $css);
    $css = kyma_recolor($css, $map);
    if (is_customize_preview()) return [false, $css];
    $hash = substr(md5($css.KYMA_THEME_VERSION), 0, 12);
    $upload = wp_upload_dir(null, false);
    if (empty($upload['error'])) {
        $dir = trailingslashit($upload['basedir']).'kyma';
        $file = $dir.'/style-'.$hash.'.css';
        if (is_file($file) || (wp_mkdir_p($dir) && file_put_contents($file, $css) !== false)) {
            return [set_url_scheme(trailingslashit($upload['baseurl']).'kyma/style-'.$hash.'.css'), ''];
        }
    }
    return [false, $css];
}
/** Inline CSS for fonts, loaded after the main stylesheet. */
function kyma_font_css(): string {
    $t = kyma_font('titulos'); $b = kyma_font('textos'); $d = kyma_font('destaque');
    $size = (int)get_theme_mod('kyma_text_size', 100);
    $css = ':root{--serif:'.kyma_font_stack($t).';--sans:'.kyma_font_stack($b).'}';
    $css .= '.hero .hero__tagline,.build-progress__number strong{font-family:'.kyma_font_stack($d).'}';
    if ($size !== 100 && $size >= 80 && $size <= 130) {
        $css .= 'body{font-size:'.round(16 * $size / 100, 2).'px}';
        $css .= '.lead,.muted,.kyma-entry-content p,main p{font-size:'.round($size / 100, 3).'em}';
    }
    return $css;
}
/** One stylesheet per Google family, so a mistyped custom name never blocks the others. */
function kyma_google_fonts_urls(): array {
    $urls = [];
    foreach (array_keys(kyma_font_roles()) as $role) {
        $spec = kyma_font($role)[2];
        if ($spec !== '') $urls['kyma-font-'.sanitize_title($spec)] = 'https://fonts.googleapis.com/css2?family='.$spec.'&display=swap';
    }
    return $urls;
}

/* ---------------------------------------------------------------------------
 * Customizer (Aparência → Personalizar)
 * ------------------------------------------------------------------------- */
add_action('customize_register', function (WP_Customize_Manager $wp) {
    $wp->add_panel('kyma', ['title' => 'Kyma: aparência do site', 'priority' => 1,
        'description' => 'Cores, fontes, contatos e textos fixos do site. As alterações aparecem na prévia ao lado e só vão ao ar quando você clicar em Publicar. As fotos e logos são trocadas em Kyma → Imagens.']);

    $wp->add_section('kyma_colors', ['title' => 'Cores', 'panel' => 'kyma',
        'description' => 'Cada cor é trocada no site inteiro: fundos, textos, botões, barras, ícones e a cor do logo aplicada pelo site. Para voltar ao original, use o botão Padrão de cada cor.']);
    foreach (kyma_palette() as $key => [$label, $default]) {
        $wp->add_setting('kyma_color_'.$key, ['default' => $default, 'sanitize_callback' => 'sanitize_hex_color']);
        $wp->add_control(new WP_Customize_Color_Control($wp, 'kyma_color_'.$key, ['label' => $label, 'section' => 'kyma_colors']));
    }

    $wp->add_section('kyma_fonts', ['title' => 'Fontes', 'panel' => 'kyma',
        'description' => 'Playfair Display, Inter e Cormorant Garamond já vêm no tema. As outras são carregadas do Google Fonts. Se quiser uma fonte fora da lista, escreva o nome exato dela no Google Fonts (fonts.google.com) no campo "Outra fonte".']);
    $choices = array_combine(array_keys(kyma_fonts()), array_keys(kyma_fonts()));
    foreach (kyma_font_roles() as $role => [$label, $default]) {
        $wp->add_setting('kyma_font_'.$role, ['default' => $default,
            'sanitize_callback' => fn($v) => isset(kyma_fonts()[$v]) ? $v : $default]);
        $wp->add_control('kyma_font_'.$role, ['type' => 'select', 'label' => $label, 'section' => 'kyma_fonts', 'choices' => $choices]);
        $wp->add_setting('kyma_font_'.$role.'_custom', ['default' => '', 'sanitize_callback' => 'sanitize_text_field']);
        $wp->add_control('kyma_font_'.$role.'_custom', ['type' => 'text', 'label' => 'Outra fonte do Google Fonts (opcional)',
            'description' => 'Ex.: Cormorant, Archivo, Plus Jakarta Sans. Deixe vazio para usar a escolhida acima.', 'section' => 'kyma_fonts']);
    }
    $wp->add_setting('kyma_text_size', ['default' => 100, 'sanitize_callback' => fn($v) => max(80, min(130, (int)$v))]);
    $wp->add_control('kyma_text_size', ['type' => 'range', 'label' => 'Tamanho dos textos (%)', 'section' => 'kyma_fonts',
        'description' => '100% é o tamanho original.', 'input_attrs' => ['min' => 80, 'max' => 130, 'step' => 5]]);

    $wp->add_section('kyma_contacts', ['title' => 'Contatos', 'panel' => 'kyma',
        'description' => 'Atualiza os contatos no site inteiro: cabeçalho, rodapé, páginas, botões de WhatsApp, links de telefone, mapa e concierge.']);
    foreach (kyma_contact_fields() as $key => [$label, $default]) {
        $wp->add_setting('kyma_contact_'.$key, ['default' => $default, 'sanitize_callback' => 'sanitize_text_field']);
        $wp->add_control('kyma_contact_'.$key, ['type' => 'text', 'label' => $label, 'section' => 'kyma_contacts']);
    }

    $wp->add_section('kyma_texts', ['title' => 'Textos fixos (cabeçalho e rodapé)', 'panel' => 'kyma',
        'description' => 'O texto das páginas se edita em Páginas. Aqui você troca qualquer texto que aparece em todas as páginas, como o rodapé. Escreva uma troca por linha, no formato:<br><code>texto atual => texto novo</code><br>Exemplo:<br><code>Design &amp; desenvolvimento por Joshua => Feito com carinho pela Kyma</code>']);
    $wp->add_setting('kyma_text_swaps', ['default' => '', 'sanitize_callback' => 'sanitize_textarea_field']);
    $wp->add_control('kyma_text_swaps', ['type' => 'textarea', 'label' => 'Trocas de texto', 'section' => 'kyma_texts']);
});

/* ---------------------------------------------------------------------------
 * Kyma → Imagens
 * ------------------------------------------------------------------------- */
add_action('admin_menu', function () {
    add_submenu_page('kyma', 'Imagens do site', 'Imagens', 'manage_options', 'kyma-imagens', 'kyma_images_screen');
    add_submenu_page('kyma', 'Cores, fontes e contatos', 'Cores, fontes e contatos', 'manage_options',
        'customize.php?autofocus[panel]=kyma');
}, 20);
add_action('admin_enqueue_scripts', function ($hook) {
    if (!str_ends_with((string)$hook, 'kyma-imagens')) return;
    wp_enqueue_media();
});
function kyma_images_screen(): void {
    if (!current_user_can('manage_options')) return;
    $overrides = (array)get_option('kyma_image_overrides', []);
    $groups = [];
    foreach (kyma_theme_images() as $path) {
        $folder = trim(dirname(substr($path, strlen('/assets/img/'))), './');
        $groups[$folder === '' ? 'geral' : $folder][] = $path;
    }
    $names = ['brand' => 'Logos e marca', 'hero' => 'Carrossel da página inicial', 'projects' => 'Empreendimentos', 'round2' => 'Empreendimentos (fachadas e cards)'];
    echo '<div class="wrap"><h1>Imagens do site</h1>';
    if (isset($_GET['saved'])) echo '<div class="notice notice-success is-dismissible"><p>Imagens atualizadas.</p></div>';
    echo '<p>Todas as fotos, logos e ícones de imagem usados no site estão aqui. Clique em <strong>Trocar</strong>, escolha ou envie uma imagem na biblioteca de mídia e depois clique em <strong>Salvar imagens</strong>. A imagem nova aparece em todos os lugares onde a antiga aparecia. <strong>Voltar ao original</strong> desfaz a troca.</p>';
    echo '<p><input type="search" id="kyma-img-filter" class="regular-text" placeholder="Filtrar pelo nome do arquivo ou pasta…"></p>';
    echo '<form method="post" action="'.esc_url(admin_url('admin-post.php')).'"><input type="hidden" name="action" value="kyma_save_images">';
    wp_nonce_field('kyma_save_images');
    foreach ($groups as $folder => $paths) {
        $title = $names[$folder] ?? ucwords(str_replace(['/', '-'], [' › ', ' '], $folder));
        echo '<details class="kyma-img-group" open><summary><h2 style="display:inline">'.esc_html($title).'</h2> <span class="count">('.count($paths).')</span></summary><div class="kyma-img-grid">';
        foreach ($paths as $path) {
            $original = get_template_directory_uri().$path;
            $id = (int)($overrides[$path] ?? 0);
            $current = $id ? (wp_get_attachment_url($id) ?: $original) : $original;
            $key = md5($path);
            echo '<div class="kyma-img" data-name="'.esc_attr(strtolower($path)).'"><div class="kyma-img__thumb"><img src="'.esc_url($current).'" data-original="'.esc_url($original).'" alt="" loading="lazy"></div>';
            echo '<code title="'.esc_attr($path).'">'.esc_html(basename($path)).'</code>';
            echo '<input type="hidden" name="kyma_img['.$key.']" value="'.($id ?: '').'"><input type="hidden" name="kyma_img_path['.$key.']" value="'.esc_attr($path).'">';
            echo '<span class="kyma-img__state">'.($id ? 'Trocada' : 'Original').'</span>';
            echo '<p><button type="button" class="button kyma-img__pick">Trocar</button> <button type="button" class="button-link kyma-img__reset"'.($id ? '' : ' hidden').'>Voltar ao original</button></p></div>';
        }
        echo '</div></details>';
    }
    submit_button('Salvar imagens');
    echo '</form></div>';
    ?>
<style>
.kyma-img-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:16px;margin:12px 0 28px}
.kyma-img{background:#fff;border:1px solid #dcdcde;border-radius:6px;padding:10px}
.kyma-img__thumb{aspect-ratio:4/3;background:repeating-conic-gradient(#f0f0f1 0 25%,#fff 0 50%) 0 0/16px 16px;display:flex;align-items:center;justify-content:center;overflow:hidden;border-radius:4px}
.kyma-img__thumb img{max-width:100%;max-height:100%;object-fit:contain}
.kyma-img code{display:block;margin:8px 0 4px;font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.kyma-img__state{font-size:12px;color:#646970}.kyma-img.is-changed{border-color:#2271b1;box-shadow:0 0 0 1px #2271b1}
.kyma-img p{margin:8px 0 0}.kyma-img-group summary{cursor:pointer;margin-top:12px}
</style>
<script>
(function(){
  document.querySelectorAll('.kyma-img').forEach(function(card){
    var input=card.querySelector('input[name^="kyma_img["]'),img=card.querySelector('img'),state=card.querySelector('.kyma-img__state'),reset=card.querySelector('.kyma-img__reset');
    if(input.value)card.classList.add('is-changed');
    card.querySelector('.kyma-img__pick').addEventListener('click',function(){
      var frame=wp.media({title:'Escolha a nova imagem',button:{text:'Usar esta imagem'},library:{type:'image'},multiple:false});
      frame.on('select',function(){var a=frame.state().get('selection').first().toJSON();input.value=a.id;img.src=(a.sizes&&a.sizes.medium?a.sizes.medium.url:a.url);state.textContent='Trocada (salve para aplicar)';reset.hidden=false;card.classList.add('is-changed');});
      frame.open();
    });
    reset.addEventListener('click',function(){input.value='';img.src=img.dataset.original;state.textContent='Original (salve para aplicar)';reset.hidden=true;card.classList.remove('is-changed');});
  });
  var filter=document.getElementById('kyma-img-filter');
  filter&&filter.addEventListener('input',function(){var q=filter.value.trim().toLowerCase();document.querySelectorAll('.kyma-img').forEach(function(c){c.style.display=!q||c.dataset.name.indexOf(q)>-1?'':'none';});});
})();
</script>
    <?php
}
add_action('admin_post_kyma_save_images', function () {
    if (!current_user_can('manage_options')) wp_die('Acesso não autorizado.', 403);
    check_admin_referer('kyma_save_images');
    $known = array_flip(kyma_theme_images());
    $ids = (array)wp_unslash($_POST['kyma_img'] ?? []);
    $paths = (array)wp_unslash($_POST['kyma_img_path'] ?? []);
    $overrides = [];
    foreach ($paths as $key => $path) {
        $path = (string)$path; $id = absint($ids[$key] ?? 0);
        if (!isset($known[$path]) || md5($path) !== $key || !$id) continue;
        if (get_post_type($id) !== 'attachment') continue;
        $overrides[$path] = $id;
    }
    update_option('kyma_image_overrides', $overrides, false);
    kyma_purge_cache();
    wp_safe_redirect(admin_url('admin.php?page=kyma-imagens&saved=1'));
    exit;
});
add_action('customize_save_after', function () { kyma_purge_cache(); });
