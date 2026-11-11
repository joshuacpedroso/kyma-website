#!/usr/bin/env python3
"""
Gerador do site estático da Kyma Empreendimentos.

Uso:  python3 build.py

O conteúdo editável fica nos JSONs de content/ e assets/project-media.json.
O painel /adm grava esses arquivos e executa este gerador na hospedagem PHP.
"""
import json
from hashlib import sha256
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).parent
def load_content(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))

SITE_CONTENT = load_content('content/site.json')
def T(key):
    return SITE_CONTENT['texts'][key]

SITE = SITE_CONTENT['url']
UP = '/assets/img'
BRAND = SITE_CONTENT['name']
PHONE = SITE_CONTENT['phone']
PHONE_INTL = SITE_CONTENT['phone_intl']
WHATSAPP = SITE_CONTENT['whatsapp']
INSTAGRAM = SITE_CONTENT['instagram']
INSTAGRAM_URL = f'https://www.instagram.com/{INSTAGRAM}/'
ADDRESS = SITE_CONTENT['address']
MAPS_Q = SITE_CONTENT['maps_query']
MAPS_URL = 'https://www.google.com/maps/search/?api=1&query=' + quote(MAPS_Q)
MAPS_EMBED = 'https://www.google.com/maps?q=' + quote(MAPS_Q) + '&output=embed'
LOGO_WHITE = SITE_CONTENT['logo']
FAVICON = SITE_CONTENT['favicon']
NAV = SITE_CONTENT['navigation']

def wa(msg):
    return f'https://wa.me/{WHATSAPP}?text={quote(msg)}'

PROJECTS = load_content('content/projects.json')
P = {p['slug']:p for p in PROJECTS}
STATUS = {'lancamento':'Lançamento','em-obras':'Em obras','entregue':'Entregue'}
UPDATES = load_content('content/project-updates.json')
MEDIA = load_content('assets/project-media.json')
DETAILS = load_content('content/project-details.json')
for p in PROJECTS:
    update = UPDATES.get(p['slug'], {})
    p['progress'] = update.get('progress_percent')
    p['progress_stages'] = update.get('progress_stages', [])
    p['coordinates'] = update.get('coordinates')
    p['map_source'] = update.get('coordinate_source')
    p.setdefault('contain',False)
    p.setdefault('wa_link',wa(f"Olá! Gostaria de mais informações sobre {p['name']}."))
FEATURED = sorted([p for p in PROJECTS if p.get('featured_order')],key=lambda p:p['featured_order'])
FEATURED_COPY = {p['slug']:p.get('featured_text',p['pitch']) for p in PROJECTS}
LAUNCHES = [p for p in PROJECTS if p['status']=='lancamento']
PORTFOLIO = [p for p in PROJECTS if p['status']=='entregue']
HAUS = DETAILS.get('haus',{})
VALUES = SITE_CONTENT['about']['values']
ABOUT = SITE_CONTENT['about']['intro_text']
POSTS = load_content('content/blog.json')

# --------------------------------------------------------------------------
# Ícones (sprite SVG)
# --------------------------------------------------------------------------
SPRITE = """<svg width="0" height="0" style="position:absolute" aria-hidden="true">
<symbol id="i-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></symbol>
<symbol id="i-arrow-ur" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M7 17L17 7M8 7h9v9"/></symbol>
<symbol id="i-pin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 21s-7-6.2-7-11.5a7 7 0 1 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></symbol>
<symbol id="i-area" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></symbol>
<symbol id="i-bed" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 18v-7a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v7M3 15h18M6 9V6h5v3M13 9V6h5v3"/></symbol>
<symbol id="i-car" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M5 16h14M5 16v2M19 16v2M4 16l1.5-6A2 2 0 0 1 7.4 8.5h9.2a2 2 0 0 1 1.9 1.5L20 16"/><circle cx="8" cy="13" r=".6"/><circle cx="16" cy="13" r=".6"/></symbol>
<symbol id="i-building" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 21h16M6 21V4h9v17M15 9h3v12M9 8h3M9 12h3M9 16h3"/></symbol>
<symbol id="i-key" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="15" r="4"/><path d="M11 12l8-8M16 7l2 2"/></symbol>
<symbol id="i-wa" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.1l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.1-1.2l-.4-.2z"/></symbol>
<symbol id="i-insta" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".8" fill="currentColor"/></symbol>
<symbol id="i-phone" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></symbol>
<symbol id="i-clock" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></symbol>
</svg>"""


SPRITE += '''<svg width="0" height="0" aria-hidden="true" style="position:absolute"><defs>
<filter id="logo-solid" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0 0 0 0 .75686 0 0 0 0 .84706 0 0 0 0 .59216 0 0 0 1 0"/></filter>
<filter id="logo-light-alpha" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0 0 0 0 .75686 0 0 0 0 .84706 0 0 0 0 .59216 .2126 .7152 .0722 0 0"/><feComposite in2="SourceAlpha" operator="in"/></filter>
<filter id="logo-dark-alpha" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0 0 0 0 .75686 0 0 0 0 .84706 0 0 0 0 .59216 -.2126 -.7152 -.0722 0 1"/><feComposite in2="SourceAlpha" operator="in"/></filter>
<filter id="logo-deep-solid" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0 0 0 0 .18824 0 0 0 0 .24706 0 0 0 0 .12157 0 0 0 1 0"/></filter>
<filter id="logo-deep-alpha" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0 0 0 0 .18824 0 0 0 0 .24706 0 0 0 0 .12157 -.2126 -.7152 -.0722 0 1"/><feComposite in2="SourceAlpha" operator="in"/></filter>
</defs></svg>'''


def ic(name: str) -> str:
    return f'<svg aria-hidden="true"><use href="#i-{name}"/></svg>'


def img(src, alt, w, h, cls="", eager=False, extra=""):
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    c = f' class="{cls}"' if cls else ""
    return f'<img src="{escape(src, quote=True)}" alt="{escape(alt)}" width="{escape(str(w))}" height="{escape(str(h))}" {load} decoding="async"{c}{extra}>'


# --------------------------------------------------------------------------
# Componentes
# --------------------------------------------------------------------------
def header(active: str) -> str:
    cur = ' aria-current="page"'
    items = "".join(
        f'<li><a href="{href}"{cur if href == active else ""}>{label}</a></li>'
        for href, label in NAV)
    menu_items = "".join(f'<li><a class="menu-link" href="{href}">{label}</a></li>' for href, label in [("/", "Início")] + NAV)
    return f"""
<a class="skip-link" href="#conteudo">Pular para o conteúdo</a>
<div class="progress" aria-hidden="true"></div>
<header class="site-header" data-header>
  <div class="header-inner">
    <a class="brand" href="/" aria-label="{escape(BRAND)} — página inicial">
      <img src="{LOGO_WHITE}" alt="{escape(BRAND)}" width="461" height="140">
    </a>
    <nav class="nav" aria-label="Navegação principal"><ul>{items}</ul></nav>
    <div class="header-actions">
      <a class="icon-btn" href="{INSTAGRAM_URL}" target="_blank" rel="noopener" aria-label="Instagram da Kyma">{ic("insta")}</a>
      <a class="btn btn--sm btn--solid" data-magnetic href="{wa("Olá! Vim pelo site da Kyma e gostaria de mais informações.")}" target="_blank" rel="noopener">Fale conosco</a>
      <button class="burger" type="button" aria-label="Abrir menu" aria-expanded="false" aria-controls="menu"><span></span><span></span></button>
    </div>
  </div>
</header>
<div class="menu" id="menu" aria-hidden="true">
  <nav aria-label="Menu"><ol>{menu_items}</ol></nav>
  <div class="menu__foot">
    <a href="tel:{PHONE_INTL}">{PHONE}</a>
    <span>{ADDRESS}</span>
    <a href="{INSTAGRAM_URL}" target="_blank" rel="noopener">@{INSTAGRAM}</a>
  </div>
</div>"""


def footer() -> str:
    nav = "".join(f'<li><a href="{h}">{l}</a></li>' for h, l in NAV)
    projs = "".join(f'<li><a href="/{p["slug"]}">{p["name"]}</a></li>' for p in LAUNCHES)
    return f"""
<footer class="site-footer">
  <div class="container">
    <div class="footer-cta">
      <p class="eyebrow">Vamos conversar</p>
      <a class="footer-big" href="/contato" data-cursor="Contato">{T('footer_heading')} <span class="arrow-c">{ic("arrow-ur")}</span></a>
    </div>
    <div class="footer-grid">
      <div class="footer-brand">
        <img src="{LOGO_WHITE}" alt="{escape(BRAND)}" width="461" height="140" loading="lazy">
        <p>{T('footer_summary')}</p>
        <div class="footer-social">
          <a class="icon-btn" href="{INSTAGRAM_URL}" target="_blank" rel="noopener" aria-label="Instagram">{ic("insta")}</a>
          <a class="icon-btn" href="{wa("Olá! Vim pelo site da Kyma.")}" target="_blank" rel="noopener" aria-label="WhatsApp">{ic("wa")}</a>
          <a class="icon-btn" href="tel:{PHONE_INTL}" aria-label="Telefone">{ic("phone")}</a>
        </div>
      </div>
      <nav aria-label="Rodapé"><h2>Navegação</h2><ul>{nav}</ul></nav>
      <div><h2>Lançamentos</h2><ul>{projs}</ul></div>
      <address style="font-style:normal">
        <h2>Contato</h2>
        <ul>
          <li><a href="{MAPS_URL}" target="_blank" rel="noopener">{ADDRESS}</a></li>
          <li><a href="tel:{PHONE_INTL}">{PHONE}</a></li>
          <li><a href="{INSTAGRAM_URL}" target="_blank" rel="noopener">@{INSTAGRAM}</a></li>
        </ul>
      </address>
    </div>
    <div class="footer-bottom">
      <span>© <span data-year>{date.today().year}</span> {BRAND}. Todos os direitos reservados.</span>
      <span>Design &amp; desenvolvimento por Joshua</span>
    </div>
  </div>

</footer>"""


def meta_items(p, cls="card__meta"):
    bits = []
    if p.get("area"):
        bits.append(f'<span>{ic("area")}{p["area"]}</span>')
    else:
        bits.append('<span class="area-pending">Metragem a confirmar</span>')
    bits.append(f'<span>{ic("pin")}{p["location"]}</span>')
    return f'<div class="{cls}">{"".join(bits)}</div>'


def card(p, tags=True):
    c, w, h = p["card"]
    t = f' data-tags="{p["status"]} {p["region"]}"' if tags else ""
    badge = f'<span class="badge">{STATUS[p["status"]]}</span>'
    return f"""
<article class="card"{t}>
  <a class="card__media{' is-contain' if p['contain'] else ''}" href="/{p['slug']}" data-cursor="Ver" data-tilt aria-label="Conhecer o {escape(p['name'])}">
    {badge}{img(c, f"{p['full']} — {p['location']}", w, h, cls=f'identity-logo logo-{p["slug"]}' if p['contain'] else '')}
    <span class="card__go">{ic("arrow-ur")}</span>
  </a>
  <div>
    <h3 class="card__title"><a href="/{p['slug']}">{p['name']}</a></h3>
    {meta_items(p)}
  </div>
</article>"""


def cta_band(title=T("cta_title"), text=T("cta_text"),
             bg=tuple(SITE_CONTENT["cta_image"]), msg="Olá! Estou procurando um apartamento e gostaria de ajuda."):
    return f"""
<section class="section section--tight">
  <div class="container">
    <div class="cta" data-reveal>
      <div class="cta__bg" data-parallax="0.12">{img(bg[0], "", bg[1], bg[2])}</div>
      <p class="eyebrow">Atendimento exclusivo</p>
      <h2 class="h2" data-split>{title}</h2>
      <p class="lead">{text}</p>
      <div class="cta__actions">
        <a class="btn btn--solid" data-magnetic href="{wa(msg)}" target="_blank" rel="noopener">{ic("wa")} Entre em contato</a>
        <a class="btn btn--glass" href="/contato">Outros contatos {ic("arrow")}</a>
      </div>
    </div>
  </div>
</section>"""


def page_hero(title, eyebrow, crumbs, bg=None, bg_logo=None, lead=None, facts="", short=False, extra=""):
    crumb_html = "".join(
        f'<li><a href="{h}">{l}</a></li>' if h else f'<li aria-current="page">{l}</li>' for h, l in crumbs)
    if bg:
        media = f'<div class="page-hero__bg"><div data-parallax="0.18" style="height:100%">{img(bg[0], "", bg[1], bg[2], eager=True)}</div></div>'
    elif bg_logo:
        media = f'<div class="page-hero__bg page-hero__bg--logo">{img(bg_logo[0], "", bg_logo[1], bg_logo[2], eager=True)}</div>'
    else:
        media = ""
    lead_html = f'<p class="lead" data-reveal>{lead}</p>' if lead else ""
    return f"""
<section class="page-hero{' page-hero--short' if short else ''}">
  {media}
  <div class="page-hero__content">
    <div class="container">
      <nav aria-label="Você está em"><ol class="crumbs" data-reveal>{crumb_html}</ol></nav>
      <p class="eyebrow" data-reveal>{eyebrow}</p>
      <h1 class="h1" data-split>{title}</h1>
      {lead_html}{facts}{extra}
    </div>
  </div>
</section>"""


# --------------------------------------------------------------------------
# Layout base
# --------------------------------------------------------------------------
ORG = {
    "@context": "https://schema.org",
    "@type": ["Organization", "HomeAndConstructionBusiness"],
    "@id": f"{SITE}/#org",
    "name": BRAND,
    "alternateName": "Kyma",
    "url": SITE + "/",
    "logo": LOGO_WHITE,
    "image": f"{UP}/2024/11/Kyma_Haus_Lateral_OK-2048x1625.jpg",
    "telephone": PHONE_INTL,
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "Av. Alfredo Ignácio Nogueira Penido, 305 – Sala 1.301",
        "addressLocality": "São José dos Campos",
        "addressRegion": "SP",
        "addressCountry": "BR",
    },
    "areaServed": ["Vale do Paraíba", "Litoral Norte de São Paulo"],
    "sameAs": [INSTAGRAM_URL],
    "description": ABOUT,
}


def breadcrumb_ld(items):
    return {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u}
            for i, (u, n) in enumerate(items)
        ],
    }


def layout(*, path, title, desc, body, active="", og_image=None, jsonld=(), project="", preload=None, page="page"):
    asset_version = sha256(b''.join(path.read_bytes() for path in sorted((ROOT/'content').glob('*.json')) if path.name!='generated-pages.json') + (ROOT/'assets/project-media.json').read_bytes() + (ROOT/'assets/css/style.css').read_bytes() + (ROOT/'assets/js/main.js').read_bytes() + (ROOT/'assets/js/chat.js').read_bytes() + Path(__file__).read_bytes()).hexdigest()[:12]
    url = SITE + (path if path != "/" else "/")
    og = og_image or f"{UP}/2024/11/Kyma_Haus_Lateral_OK-1024x813.jpg"
    if og.startswith("/"): og = SITE + og
    ld = "\n".join(
        f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in jsonld)
    pre = f'<link rel="preload" as="image" href="{preload}" fetchpriority="high">' if preload else ""
    return f"""<!doctype html>
<html lang="pt-BR" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#303F1F">
<meta name="format-detection" content="telephone=no">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="{escape(BRAND)}">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{escape(title)}">
<meta name="twitter:description" content="{escape(desc)}">
<meta name="twitter:image" content="{og}">
<meta name="geo.region" content="BR-SP">
<meta name="geo.placename" content="São José dos Campos">
<link rel="icon" href="{FAVICON}" type="image/png">
<link rel="apple-touch-icon" href="{FAVICON}">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://kyma.com.br">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&amp;family=Playfair+Display:ital,wght@0,400;0,500;1,400;1,500&amp;display=swap">
<link rel="stylesheet" href="/assets/vendor/leaflet/leaflet.css">
<link rel="stylesheet" href="/assets/css/style.css?v={asset_version}">
<link rel="preload" as="font" href="/assets/fonts/cormorant-garamond-normal.ttf" type="font/ttf" crossorigin>
{pre}
<script>document.documentElement.classList.replace('no-js','js')</script>
{ld}
</head>
<body data-page="{page}"{f' data-project="{project}"' if project else ""}>
{SPRITE}
<div class="preloader" aria-hidden="true">
  <div class="preloader__inner">
    <img class="preloader__logo" src="{LOGO_WHITE}" alt="" width="461" height="140">
    <div class="preloader__bar"><span></span></div>
    <p class="preloader__tag">{SITE_CONTENT['hero']['line']} {SITE_CONTENT['hero']['emphasis']}</p>
  </div>
</div>
{header(active)}
<main id="conteudo">
{body}
</main>
{footer()}
<script src="/assets/js/data.js?v={asset_version}" defer></script>
<script src="/assets/vendor/leaflet/leaflet.js" defer></script>
<script src="/assets/js/main.js?v={asset_version}" defer></script>
<script src="/assets/js/chat.js?v={asset_version}" defer></script>
</body>
</html>
"""


# --------------------------------------------------------------------------
# Páginas
# --------------------------------------------------------------------------
def page_home():
    slides = SITE_CONTENT['hero']['slides']
    slide_html = "".join(
        f'<div class="hero__slide{" is-active" if i == 0 else ""}" data-caption="{escape(c)}">'
        f'{img(s, c, w, h, eager=(i == 0))}</div>'
        for i, (s, w, h, c) in enumerate(slides))
    dots = "".join(
        f'<button type="button" aria-label="Imagem {i + 1}" aria-current="{"true" if i == 0 else "false"}"></button>'
        for i in range(len(slides)))

    logos = "".join(
        f'<a class="marquee__item logo-{p["slug"]}" href="/{p["slug"]}" aria-label="{escape(p["name"])}">'
        f'<img class="base" src="{p["logo"][0]}" alt="" width="200" height="200" loading="lazy"></a>'
        f'<span class="marquee__word" aria-hidden="true">✦</span>'
        for p in PROJECTS)

    shows = ""
    for i, p in enumerate(FEATURED):
        c, w, h = p["card"]
        facts = f'<span>{ic("pin")}{p["location"]}</span>'
        shows += f"""
<article class="show" data-featured="{p['slug']}">
  <a class="show__media reveal-img" href="/{p['slug']}" data-cursor="Ver">
    <span class="badge">{STATUS[p["status"]]}</span>
    {img(c, f"{p['full']} — {p['location']}", w, h)}
  </a>
  <div class="show__body">
    <h3 class="h2" data-split>{p['name']}</h3>
    <p class="lead" data-reveal>{FEATURED_COPY.get(p['slug'], p['pitch'])}</p>
    <div class="show__meta" data-reveal>{facts}</div>
    <div data-reveal><a class="link-arrow" href="/{p['slug']}">Conhecer o {p['name']} <span class="line"></span></a></div>
  </div>
</article>"""

    body = f"""
<section class="hero" data-hero-slider aria-label="Destaques">
  <div class="hero__slides">{slide_html}</div>
  <div class="hero__content">
    <div class="container">
      <h1 class="hero__tagline" data-hero><span>{SITE_CONTENT['hero']['line']}</span> <em>{SITE_CONTENT['hero']['emphasis']}</em></h1>

    </div>
  </div>
  <div class="hero__meta" data-hero="4">
    <div class="hero__bar"><span></span></div>
    <div class="hero__dots">{dots}</div>
  </div>
  <span class="scroll-hint" aria-hidden="true"></span>
</section>

<section class="marquee" aria-label="Nossos empreendimentos">
  <div class="marquee__track">
    <div class="marquee__group">{logos}</div>
    <div class="marquee__group" aria-hidden="true" inert>{logos}</div>
  </div>
</section>

{locations_section()}

<section class="section theme-ink2" id="lancamentos">
  <div class="container">
    <div class="section-head section-head--split">
      <div style="display:grid;gap:22px">
        <p class="eyebrow" data-reveal>{T('home_featured_eyebrow')}</p>
        <h2 class="h1" data-split>{T('home_featured_heading')}</h2>
      </div>
      <a class="btn" data-reveal data-magnetic href="/empreendimentos">Ver empreendimentos {ic("arrow")}</a>
    </div>
    <div class="cards featured-cards">{shows}</div>
  </div>
</section>

{blog_section()}

{cta_band()}

{instagram_section()}"""

    return layout(
        path="/", page="home",
        title="Kyma Empreendimentos | Apartamentos em São José dos Campos e Litoral Norte",
        desc="Kyma Empreendimentos: lançamentos e apartamentos em São José dos Campos (Vila Ema) e no Litoral Norte. Conheça Uniko, Haus, Azure e todo o portfólio.",
        body=body, preload=slides[0][0],
        jsonld=[ORG, {"@context": "https://schema.org", "@type": "WebSite", "name": BRAND, "url": SITE + "/", "inLanguage": "pt-BR", "publisher": {"@id": f"{SITE}/#org"}}],
    )


def page_listing(kind):
    if kind == "empreendimentos":
        items, path = PROJECTS, "/empreendimentos"
        title_html = T("listing_heading")
        eyebrow = "Empreendimentos Kyma"
        lead = T("listing_subtitle")
        bg = (f"{UP}/2024/11/fechado-2.jpg", 1920, 1080)
        title = "Empreendimentos | Kyma Empreendimentos"
        desc = "Conheça todos os empreendimentos da Kyma: Haus, Mon Trésor, Azure, Monte Cristo, Monte Negro, Monte Zurich e mais, em São José dos Campos e Litoral Norte."
        filters = [("todos", "Todos"), ("lancamento", "Lançamentos"), ("em-obras", "Em obras"), ("entregue", "Entregues")]
    else:
        items, path = LAUNCHES, "/lancamentos"
        title_html = T("launch_heading")
        eyebrow = "Oportunidades exclusivas"
        lead = T("launch_subtitle")
        bg = ("/assets/img/brand/uniko-oficial.svg", 733, 500)
        title = "Lançamentos | Kyma Empreendimentos"
        desc = "Conheça o Uniko, lançamento da Kyma. Entre em contato para mais informações."
        filters = [("todos", "Todos"), ("lancamento", "Lançamentos")]
    label = "Empreendimentos" if kind == "empreendimentos" else "Lançamentos"
    fbtn = "".join(
        f'<button class="filter" type="button" data-filter="{k}" aria-pressed="{"true" if k == "todos" else "false"}">{l}</button>'
        for k, l in filters)
    cards = "".join(card(dict(p,card=p["launch_card"],contain=False)) if kind == "lancamentos" and p.get("launch_card") else card(p) for p in items)
    extra_section = ""
    if kind == "lancamentos":
        extra_section = f"""
<section class="section theme-ink2">
  <div class="container">
    <div class="section-head section-head--split">
      <div style="display:grid;gap:22px">
        <p class="eyebrow" data-reveal>Portfólio</p>
        <h2 class="h2" data-split>Veja também <em>o que já construímos.</em></h2>
      </div>
      <a class="btn" data-reveal href="/empreendimentos">Ver todos {ic("arrow")}</a>
    </div>
    <div class="hscroll" data-reveal>{"".join(card(p, tags=False) for p in PORTFOLIO)}</div>
  </div>
</section>"""

    body = page_hero(title_html, eyebrow, [("/", "Início"), (None, label)], bg=bg, lead=lead, short=True) + f"""
<section class="section">
  <div class="container">
    <div class="filters" data-filters role="group" aria-label="Filtrar empreendimentos" data-reveal>
      {fbtn}
    </div>
    <div class="cards" data-stagger="0.08">{cards}</div>
  </div>
</section>
{extra_section}
{cta_band()}"""
    item_list = {
        "@context": "https://schema.org", "@type": "ItemList", "name": label,
        "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{SITE}/{p['slug']}", "name": p["full"]} for i, p in enumerate(items)],
    }
    return layout(path=path, title=title, desc=desc, body=body, active=path, og_image=bg[0],
                  jsonld=[breadcrumb_ld([("/", "Início"), (path, label)]), item_list], preload=bg[0])


def project_ld(p):
    ld = {
        "@context": "https://schema.org", "@type": "ApartmentComplex",
        "name": p["full"], "url": f"{SITE}/{p['slug']}", "description": p["pitch"],
        "image": (p["hero"] or p["card"])[0],
        "containedInPlace": {"@type": "Place", "name": p["location"]},
        "provider": {"@id": f"{SITE}/#org"},
    }
    if p["city"]:
        ld["address"] = {"@type": "PostalAddress", "addressLocality": p["city"], "addressRegion": "SP", "addressCountry": "BR"}
        if p.get("street") and p["street"].startswith("Rua"):
            ld["address"]["streetAddress"] = p["street"]
    return ld


def facts_chips(p):
    items = [f'<span class="chip">{ic("pin")}{p["street"] + " · " if p.get("street") else ""}{p["location"]}</span>']
    if p["area"]:
        items.append(f'<span class="chip">{ic("area")}{p["area"]}</span>')
    if p["beds"]:
        items.append(f'<span class="chip">{ic("bed")}{p["beds"]}</span>')
    items.append(f'<span class="chip">{ic("building")}{STATUS[p["status"]]}</span>')
    return f'<div class="hero-facts" data-stagger="0.06">{"".join(items)}</div>'


def related(p):
    others = [x for x in PROJECTS if x["slug"] != p["slug"]]
    others.sort(key=lambda x: (x["status"] != p["status"], x["region"] != p["region"]))
    return f"""
<section class="section theme-ink2">
  <div class="container">
    <div class="section-head section-head--split">
      <div style="display:grid;gap:22px">
        <p class="eyebrow" data-reveal>Continue explorando</p>
        <h2 class="h2" data-split>Outros <em>empreendimentos.</em></h2>
      </div>
      <a class="btn" data-reveal href="/empreendimentos">Ver todos {ic("arrow")}</a>
    </div>
    <div class="hscroll" data-reveal>{"".join(card(x, tags=False) for x in others)}</div>
  </div>
</section>"""


def page_haus():
    p = project_page_data(P["haus"])
    hero_btns = f"""<div class="hero__cta" data-reveal style="margin-top:8px">
      <a class="btn btn--solid" data-magnetic href="{p['wa_link']}" target="_blank" rel="noopener">{ic("wa")} Entre em contato</a>
      <a class="btn btn--glass" href="#plantas">Ver plantas {ic("arrow")}</a></div>"""
    about = "".join(f'<p class="lead" data-reveal>{t}</p>' for t in HAUS["about"])
    specs = '<div class="specs" data-stagger="0.08">' + ''.join(f'<div class="spec">{ic(icon)}<b>{value}</b><span>{label}</span></div>' for icon,value,label in HAUS['specs']) + '</div>'
    private = "".join(f"<li>{x}</li>" for x in HAUS["private"])
    common = "".join(f"<li>{x}</li>" for x in HAUS["common"])
    blocks = ""
    for i, b in enumerate(HAUS["blocks"]):
        feats = "".join(
            f'<div class="feat"><span class="feat__i">0{j + 1}</span><div><h3>{t}</h3><p>{x}</p></div></div>'
            for j, (t, x) in enumerate(b["feats"]))
        s, w, h = b["img"]
        blocks += f"""
<div class="split{' split--rev' if i % 2 else ''}" style="margin-top:{'0' if i == 0 else 'clamp(88px,12vw,160px)'}">
  <a class="split__media split__media--tall reveal-img" href="{s}" data-lightbox="haus-amb" data-caption="Haus — {escape(b['eyebrow'], quote=True)}" data-cursor="Ampliar">
    <div data-parallax="0.08" style="height:112%;margin-top:-6%">{img(s, f"Haus Vila Ema — {b['eyebrow']}", w, h)}</div>
    <span class="frame-deco"></span>
  </a>
  <div class="split__body">
    <p class="eyebrow" data-reveal>{b['eyebrow']}</p>
    <h3 class="h1{' word-together' if b['eyebrow'].startswith('Conforto') else ''}" data-split>{b['title']}</h3>
    <div class="feats" data-stagger="0.08">{feats}</div>
    <div data-reveal><a class="link-arrow" href="{p['wa_link']}" target="_blank" rel="noopener">Mais informações <span class="line"></span></a></div>
  </div>
</div>"""
    plans = "".join(
        f'<figure class="plan" data-reveal><a href="{full}" data-lightbox="haus-plantas" data-caption="Haus — {escape(cap, quote=True)}" data-cursor="Ampliar">{img(med, f"Haus Vila Ema — {cap}", w, h)}</a>'
        f'<figcaption><b>{cap}</b><span>Clique para ampliar</span></figcaption></figure>'
        for full, med, w, h, cap in HAUS["plans"])
    gallery_imgs = [
        (f"{UP}/2024/11/Kyma_Haus_Lateral_OK-2048x1625.jpg", f"{UP}/2024/11/Kyma_Haus_Lateral_OK-1024x813.jpg", 1024, 813, "Fachada"),
        (f"{UP}/2024/11/1_3-Foto.jpg", f"{UP}/2024/11/1_3-Foto.jpg", 1074, 1080, "Interiores"),
        (f"{UP}/2025/01/obra-haus.jpg", f"{UP}/2025/01/obra-haus-1024x573.jpg", 1024, 573, "Andamento da obra"),
        (f"{UP}/2024/11/fechado-2.jpg", f"{UP}/2024/11/fechado-2.jpg", 1920, 1080, "Open space"),
    ]
    if MEDIA.get('haus'):
        gallery_imgs = [(photo['src'], photo['src'], photo['width'], photo['height'], photo['caption']) for photo in MEDIA['haus']]
    gallery = "".join(
        f'<a href="{full}" data-lightbox="haus-galeria" data-caption="Haus — {escape(cap, quote=True)}" data-cursor="Ampliar" data-reveal>{img(med, f"Haus Vila Ema — {cap}", w, h)}</a>'
        for full, med, w, h, cap in gallery_imgs)

    body = page_hero(HAUS["hero_title"] if p["name"]=="Haus" else p["name"], f"{STATUS[p['status']]} · {p['location']}",
                     [("/", "Início"), ("/empreendimentos", "Empreendimentos"), (None, "Haus")],
                     bg=p["hero"], facts=facts_chips(p), extra=hero_btns) + f"""
<section class="section theme-light">
  <div class="container">
    <div class="split">
      <div class="split__body">
        <p class="eyebrow" data-reveal>O empreendimento</p>
        <h2 class="h2" data-split>{HAUS["intro_heading"]}</h2>
        <p class="lead" data-reveal>{p["pitch"]}</p>
        <p class="lead" data-reveal>{p.get("additional_description", "")}</p>
        {about}
        <div data-reveal style="display:flex;gap:14px;flex-wrap:wrap">
          <a class="btn btn--dark" href="{p['wa_link']}" target="_blank" rel="noopener">Entre em contato {ic("arrow")}</a>
        </div>
      </div>
      <a class="split__media split__media--wide reveal-img" href="{HAUS['intro_image'][0]}" data-lightbox="haus-galeria-top" data-caption="Haus — Fachada" data-cursor="Ampliar">
        {img(HAUS["intro_image"][0], "Fachada lateral do Residencial Haus Vila Ema", *HAUS["intro_image"][1:])}
      </a>
    </div>
    <div class="mt-l">{specs}</div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head">
      <p class="eyebrow" data-reveal>Áreas privativas</p>
      <h2 class="h1" data-split>{HAUS["private_heading"]}</h2>
    </div>
    <ul class="amen" data-stagger="0.04">{private}</ul>
  </div>
</section>

<section class="section theme-ink2">
  <div class="container">
    <div class="section-head section-head--split">
      <div style="display:grid;gap:22px">
        <p class="eyebrow" data-reveal>Áreas comuns</p>
        <h2 class="h1" data-split>{HAUS["common_heading"]}</h2>
      </div>
      <p class="lead" data-reveal style="max-width:40ch">{HAUS["common_intro"].replace("{count}", str(len(HAUS["common"])))}</p>
    </div>
    <ul class="amen" data-stagger="0.03">{common}</ul>
  </div>
</section>

<section class="section">
  <div class="container">{blocks}</div>
</section>

<section class="section theme-light" id="plantas">
  <div class="container">
    <div class="section-head section-head--split">
      <div style="display:grid;gap:22px">
        <p class="eyebrow" data-reveal>Plantas</p>
        <h2 class="h1" data-split>{HAUS["plans_heading"]}</h2>
      </div>
      <a class="btn btn--dark" data-reveal href="{p['wa_link']}" target="_blank" rel="noopener">Entre em contato {ic("arrow")}</a>
    </div>
    <div class="plans">{plans}</div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head">
      <p class="eyebrow" data-reveal>Galeria</p>
      <h2 class="h1" data-split>{HAUS["gallery_heading"]}</h2>
    </div>
    <div class="gallery">{gallery}</div>
  </div>
</section>

<section class="section section--tight">
  <div class="container">
    <div class="section-head">
      <p class="eyebrow" data-reveal>Localização</p>
      <h2 class="h2" data-split>{HAUS["location_heading"]}</h2>
      <p class="lead" data-reveal>{HAUS["location_description"]}</p>
    </div>
    <div class="map" data-reveal><iframe title="Mapa — Haus Vila Ema" loading="lazy" referrerpolicy="no-referrer-when-downgrade" src="https://www.google.com/maps?q={quote(', '.join(filter(None,[p.get('street'),p.get('hood'),p.get('city'),'SP'])))}&amp;output=embed"></iframe></div>
  </div>
</section>

{progress_section(p)}
{cta_band(title=HAUS["cta_title"],text=HAUS["cta_text"],msg="Olá! Gostaria de agendar uma visita ao Haus Vila Ema.",bg=HAUS["cta_image"])}
{related(p)}"""
    ld = project_ld(p)
    ld["numberOfBedrooms"] = 2
    ld["amenityFeature"] = [{"@type": "LocationFeatureSpecification", "name": x, "value": True} for x in HAUS["common"]]
    return layout(
        path="/haus", project="haus", active="/empreendimentos",
        title="Haus Vila Ema | Apartamentos de 2 dormitórios em São José dos Campos — Kyma",
        desc="Haus Vila Ema: apartamentos de 79,95m² e 82,21m² com 2 dormitórios, lazer completo com piscina de borda infinita e 2 vagas. Rua Padre Rodolfo, 286 — São José dos Campos.",
        body=body, og_image=p["hero"][0], preload=p["hero"][0],
        jsonld=[breadcrumb_ld([("/", "Início"), ("/empreendimentos", "Empreendimentos"), ("/haus", "Haus")]), ld])


def project_page_data(p):
    local = dict(p)
    photos = MEDIA.get(p['slug'], [])
    if photos:
        first = next((photo for photo in photos if photo['caption'] in ['Fachada principal', 'Fachada frontal', 'Fachada A Final']), photos[0])
        local['card'] = (first['src'], first['width'], first['height'])
        local['hero'] = local['card']
        local['contain'] = False
    if p.get("presentation_from_card"):
        local["card"] = p["card"]
        local["hero"] = local["card"]
    if p.get("presentation_override") and p.get("hero"):
        local["hero"] = p["hero"]
    return local


def page_project(p):
    p = project_page_data(p)
    section = "Lançamentos" if p["status"] == "lancamento" else "Empreendimentos"
    sec_path = "/lancamentos" if p["status"] == "lancamento" else "/empreendimentos"
    hero_btns = f"""<div class="hero__cta" data-reveal style="margin-top:8px">
      <a class="btn btn--solid" data-magnetic href="{p['wa_link']}" target="_blank" rel="noopener">{ic("wa")} Entre em contato</a>
      <a class="btn btn--glass" href="#sobre">Conhecer {ic("arrow")}</a></div>"""
    status_txt = STATUS[p["status"]]
    c, w, h = p["card"]
    big = p["hero"] or p["card"]
    specs = [
        (ic("pin"), p["location"], "Localização"),
        (ic("area"), p["area"] or "A confirmar", "Área privativa"),
        (ic("building"), status_txt, "Status"),
        (ic("clock"), "Atendimento", "Corretor dedicado"),
    ]
    spec_html = "".join(f'<div class="spec">{i}<b>{b}</b><span>{s}</span></div>' for i, b, s in specs)
    gallery = [(photo["src"], photo["src"], photo["width"], photo["height"], photo["caption"]) for photo in MEDIA.get(p["slug"], [])]
    if not gallery:
        gallery = [(big[0], c, w, h, "Imagem principal")]
    if p["logo"][1] != c:
        gallery.append((p["logo"][1], p["logo"][1], 500, 500, "Identidade visual"))
    contain_cls = ' class="is-contain"'
    gal_html = "".join(
        f'<a href="{full}" data-lightbox="{p["slug"]}" data-caption="{escape(p["name"])} — {escape(cap, quote=True)}" data-cursor="Ampliar" data-reveal'
        f'{contain_cls if (p["contain"] or cap == "Identidade visual") else ""}>{img(med, p["full"] + " — " + cap, ww, hh, cls="identity-logo logo-" + p["slug"] if (p["contain"] or cap == "Identidade visual") else "")}</a>'
        for i, (full, med, ww, hh, cap) in enumerate(gallery))
    extra_copy = p.get('additional_description','')
    body = page_hero(p["name"], f"{status_txt} · {p['location']}",
                     [("/", "Início"), (sec_path, section), (None, p["name"])],
                     bg=p["hero"], bg_logo=p.get("hero_logo"), facts=facts_chips(p), extra=hero_btns) + f"""
<section class="section theme-light" id="sobre">
  <div class="container">
    <div class="split">
      <div class="split__body">
        <p class="eyebrow" data-reveal>O empreendimento</p>
        <img class="project-logo logo-{p['slug']}" src="{p['logo'][0]}" alt="Logo oficial {escape(p['name'])}" width="300" height="200" loading="lazy">
        <h2 class="h2" data-split>{p['full']}</h2>
        <p class="lead" data-reveal>{p['pitch']}</p>
        <p class="lead" data-reveal>{extra_copy}</p>
        <div data-reveal><a class="btn btn--dark" href="{p['wa_link']}" target="_blank" rel="noopener">Entre em contato {ic("arrow")}</a></div>
      </div>
      <a class="split__media split__media--wide reveal-img{' is-contain' if p['contain'] else ''}" href="{big[0]}" data-lightbox="{p['slug']}-top" data-caption="{escape(p['name'])}" data-cursor="Ampliar" style="{'background:var(--ink-3)' if p['contain'] else ''}">
        {img(c, f"{p['full']} — {p['location']}", w, h, extra=' style="object-fit:contain;padding:10%"' if p['contain'] else "")}
      </a>
    </div>
    <div class="specs mt-l" data-stagger="0.08">{spec_html}</div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head">
      <p class="eyebrow" data-reveal>Galeria</p>
      <h2 class="h2" data-split>Detalhes do <em>{p['name']}.</em></h2>
    </div>
    <div class="gallery">{gal_html}</div>
  </div>
</section>

{project_map(p)}
{progress_section(p)}
{cta_band(title=f"Quer conhecer o <em>{p['name']}?</em>", text="Fale com um corretor e receba plantas, disponibilidade e condições atualizadas.", msg=f"Olá! Gostaria de mais informações sobre o {p['name']}.")}
{related(p)}"""
    return layout(
        path=f"/{p['slug']}", project=p["slug"], active=sec_path,
        title=f"{p['full']} | {p['location']} — Kyma Empreendimentos",
        desc=f"{p['full']} ({p['location']}{', ' + p['area'] if p['area'] else ''}). {p['pitch']}",
        body=body, og_image=big[0], preload=(p["hero"] or [None])[0],
        jsonld=[breadcrumb_ld([("/", "Início"), (sec_path, section), (f"/{p['slug']}", p["name"])]), project_ld(p)])


def page_about():
    pillars = "".join(
        f'<div class="pillar"><span class="pillar__n">0{i + 1}</span><h3>{t}</h3><p>{x}</p></div>'
        for i, (t, x) in enumerate(VALUES))
    body = page_hero(T("about_title"), "Quem somos", [("/", "Início"), (None, "Quem somos")],
                     bg=SITE_CONTENT['about']['hero_image'],
                     lead=T("about_subtitle"), short=True) + f"""
<section class="section about-intro">
  <div class="container">
    <div class="split">
      <div class="split__media split__media--tall reveal-img">
        <div data-parallax="0.08" style="height:112%;margin-top:-6%">{img(*SITE_CONTENT['about']['intro_image'])}</div>
        <span class="frame-deco"></span>
      </div>
      <div class="split__body">
        <p class="eyebrow" data-reveal>Nossa essência</p>
        <h2 class="h2" data-split>{T('about_intro_heading')}</h2>
        <p class="lead" data-reveal>{ABOUT}</p>
        <div data-reveal style="display:flex;gap:14px;flex-wrap:wrap">
          <a class="btn btn--solid" href="/empreendimentos">Ver empreendimentos {ic("arrow")}</a>
          <a class="btn" href="/contato">Fale conosco</a>
        </div>
      </div>
    </div>
  </div>
</section>

{portfolio_section()}

<section class="section theme-light about-values">
  <div class="container">
    <div class="split split--rev">
      <div class="split__media split__media--wide reveal-img">{img(*SITE_CONTENT['about']['values_image'])}</div>
      <div class="split__body">
        <p class="eyebrow" data-reveal>Comprometimento</p>
        <h2 class="h1" data-split>{T('about_values_heading')}</h2>
        <p class="lead" data-reveal>{T('about_values_intro')}</p>
      </div>
    </div>
    <div class="pillars mt-l" data-stagger="0.12">{pillars}</div>
  </div>
</section>

"""
    return layout(
        path="/quem-somos", page="about", active="/quem-somos",
        title="Quem somos | Kyma Empreendimentos",
        desc="Conheça a Kyma Empreendimentos: construção civil no Vale do Paraíba e Litoral Norte de SP, com foco em qualidade, localização e retorno para o cliente.",
        body=body, og_image=SITE_CONTENT['about']['hero_image'][0], preload=SITE_CONTENT['about']['hero_image'][0],
        jsonld=[breadcrumb_ld([("/", "Início"), ("/quem-somos", "Quem somos")]), ORG])


def page_contact():
    options = "".join(f'<option value="{p["name"]}">{p["name"]}</option>' for p in PROJECTS)
    body = page_hero(T("contact_heading"), "Contato", [("/", "Início"), (None, "Contato")],
                     bg=(f"{UP}/2024/11/1_3-Foto.jpg", 1074, 1080),
                     lead=T("contact_subtitle"), short=True) + f"""
{help_section()}
<section class="section">
  <div class="container">
    <div class="contact-grid">
      <div style="display:grid;gap:32px">
        <div style="display:grid;gap:20px">
          <p class="eyebrow" data-reveal>Canais de atendimento</p>
          <h2 class="h2" data-split>Estamos <em>por perto.</em></h2>
        </div>
        <ul class="info-list" data-stagger="0.08">
          <li><span class="ic">{ic("wa")}</span><div><small>WhatsApp</small><a href="{wa("Olá! Vim pelo site da Kyma.")}" target="_blank" rel="noopener">{PHONE}</a></div></li>
          <li><span class="ic">{ic("phone")}</span><div><small>Telefone</small><a href="tel:{PHONE_INTL}">{PHONE}</a></div></li>
          <li><span class="ic">{ic("pin")}</span><div><small>Escritório</small><a href="{MAPS_URL}" target="_blank" rel="noopener">{ADDRESS}</a></div></li>
          <li><span class="ic">{ic("insta")}</span><div><small>Instagram</small><a href="{INSTAGRAM_URL}" target="_blank" rel="noopener">@{INSTAGRAM}</a></div></li>
        </ul>
      </div>
      <form class="form" id="contact-form" data-wa="{WHATSAPP}" novalidate data-reveal>
        <div class="field full"><input id="f-nome" name="nome" type="text" placeholder=" " autocomplete="name" required><label for="f-nome">Seu nome *</label></div>
        <div class="field"><input id="f-tel" name="telefone" type="tel" placeholder=" " autocomplete="tel" required><label for="f-tel">Telefone / WhatsApp *</label></div>
        <div class="field"><input id="f-email" name="email" type="email" placeholder=" " autocomplete="email"><label for="f-email">E-mail</label></div>
        <div class="field full">
          <label class="sr-only" for="f-assunto">Assunto</label><select id="f-assunto" name="assunto" aria-label="Assunto"><option>Procurando por um imóvel</option><option>Financeiro</option><option>Seguro de entrega</option><option>Trabalhe conosco</option><option>Negocie seu terreno</option><option>Sou fornecedor</option><option>Boleto bancário</option><option>Solicitar assistência</option><option>Sou vizinho de uma obra</option><option>Relatar desvio de conduta</option><option>Enviar e-mail</option><option>Assessoria de imprensa</option><option>Privacidade de dados</option></select></div><div class="field full"><select id="f-int" name="interesse"><option value="">Ainda não sei — quero conhecer as opções</option>{options}</select>
          <label for="f-int">Interesse</label>
        </div>
        <div class="field full"><textarea id="f-msg" name="mensagem" placeholder=" " rows="4"></textarea><label for="f-msg">Mensagem</label></div>
        <div class="form__foot full">
          <p class="form__note">Ao enviar, abrimos o WhatsApp com a sua mensagem pronta para um de nossos corretores.</p>
          <button class="btn btn--solid" type="submit" data-magnetic>Enviar mensagem {ic("arrow")}</button>
        </div>
      </form>
    </div>
  </div>
</section>
"""
    contact_ld = dict(ORG)
    contact_ld["contactPoint"] = {"@type": "ContactPoint", "telephone": PHONE_INTL, "contactType": "sales", "areaServed": "BR", "availableLanguage": "Portuguese"}
    return layout(
        path="/contato", active="/contato",
        title="Contato | Kyma Empreendimentos — São José dos Campos",
        desc=f"Fale com a Kyma Empreendimentos: WhatsApp e telefone {PHONE}. Escritório na {ADDRESS}. Agende sua visita.",
        body=body, og_image=f"{UP}/2024/11/1_3-Foto.jpg",
        jsonld=[breadcrumb_ld([("/", "Início"), ("/contato", "Contato")]), contact_ld])


def portfolio_section():
    return f'''<section class="section"><div class="container">
      <div class="section-head"><p class="eyebrow">Portfólio</p><h2 class="h1" data-split>{T('portfolio_heading')}</h2></div>
      <div class="cards">{"".join(card(p, tags=False) for p in PORTFOLIO)}</div>
    </div></section>'''


def project_map(p):
    if not p.get("coordinates"):
        return f'''<section class="section section--tight"><div class="container"><p class="eyebrow">Localização</p><h2 class="h2">{escape(p['name'])}</h2><p class="lead">{escape(p['location'])}. Entre em contato para receber o endereço exato.</p></div></section>'''
    query = ", ".join(filter(None, [p.get("street"), p.get("hood"), p.get("city"), "SP"]))
    return f'''<section class="section section--tight"><div class="container">
      <div class="section-head"><p class="eyebrow">Localização</p><h2 class="h2">{escape(p['name'])} · <em>{escape(p['location'])}</em></h2></div>
      <div class="map"><iframe title="Localização de {escape(p['name'])}" loading="lazy" src="https://www.google.com/maps?q={quote(query)}&amp;output=embed" referrerpolicy="no-referrer-when-downgrade"></iframe></div>
      <a class="link-arrow" href="https://www.google.com/maps/search/?api=1&amp;query={quote(query)}" target="_blank" rel="noopener">Abrir localização no Google Maps</a>
    </div></section>'''


def locations_section():
    # Coordinates remain null until an exact address has been verified.
    items = ''.join(f'''<li><a class="map-project" href="/{p['slug']}" data-map-project="{p['slug']}"><span>{p['name']}</span><small>{escape(p['street'] or p['location'])}</small><small>{'Ver empreendimento' if p['coordinates'] else 'Pin a confirmar' if UPDATES.get(p['slug'], {}).get('exact_address') else 'Localização exata a confirmar'}</small></a></li>''' for p in PROJECTS)
    return f'''<section class="section" id="enderecos"><div class="container">
      <div class="section-head"><p class="eyebrow">{T('home_featured_eyebrow')}</p><h2 class="h1">{T('addresses_heading')}</h2><p class="lead">{T('addresses_subtitle')}</p></div>
      <div class="locations-layout"><div><div id="project-map" class="project-map" role="region" aria-label="Mapa dos empreendimentos com localização confirmada"></div><p id="map-status" class="map-status" role="status">Selecione um empreendimento. Pins disponíveis para endereços confirmados.</p><p id="map-tiles-note" class="map-status" role="status"></p><noscript><p>Consulte os endereços na lista de empreendimentos.</p></noscript></div><ul class="map-projects">{items}</ul></div>
    </div></section>'''


def progress_section(p):
    value = p['progress']
    target = '' if value is None else str(value)
    label = 'A informar' if value is None else f'{value:g}%'
    aria = '' if value is None else f' aria-valuenow="{value:g}"'
    offset = 100 if value is None else 100 - value
    stages = ''
    for i, stage in enumerate(p.get('progress_stages', [])):
        percent = stage.get('percent')
        stage_target = '' if percent is None else str(percent)
        stage_label = 'A informar' if percent is None else f'{percent:g}%'
        stage_aria = '' if percent is None else f' aria-valuenow="{percent:g}"'
        stages += f'''<div class="build-stage" data-progress-stage data-progress-target="{stage_target}" style="--stage-index:{i}">
          <div class="build-stage__label"><span>{escape(stage['name'])}</span><strong data-progress-count>{stage_label}</strong></div>
          <div class="build-stage__track" role="progressbar" aria-label="{escape(stage['name'])}" aria-valuemin="0" aria-valuemax="100"{stage_aria} aria-valuetext="{stage_label}"><span data-progress-fill style="--progress-value:{0 if percent is None else percent}%"></span></div>
        </div>'''
    if not stages:
        stages = '<p class="build-progress__pending">Etapas detalhadas a informar.</p>'
    return f'''<section class="section theme-ink2 build-progress" id="evolucao" data-progress="{target}" data-progress-section>
      <div class="container build-progress__panel">
        <div class="build-progress__intro"><p class="eyebrow">{p['name']}</p><h2 class="h2">Evolução <em>da obra.</em></h2><p class="lead">{'Percentual a informar. Entre em contato para acompanhar a evolução da obra.' if value is None else 'Acompanhe a evolução da obra.'}</p>
          <a class="link-arrow" href="{p['wa_link']}" target="_blank" rel="noopener">Entre em contato {ic('arrow')}</a></div>
        <div class="build-progress__overall" data-progress-overall data-progress-target="{target}" role="progressbar" aria-label="Evolução geral da obra" aria-valuemin="0" aria-valuemax="100"{aria} aria-valuetext="{label}">
          <svg class="build-progress__ring" viewBox="0 0 180 180" aria-hidden="true"><circle class="build-progress__track" cx="90" cy="90" r="76"/><circle class="build-progress__fill" data-progress-ring cx="90" cy="90" r="76" pathLength="100" stroke-dasharray="100" style="stroke-dashoffset:{offset}"/></svg>
          <div class="build-progress__number"><strong data-progress-count>{label}</strong><span>Evolução geral</span></div>
        </div>
        <div class="build-progress__stages">{stages}</div>
      </div></section>'''


def instagram_section():
    # Official public profile embed. An authenticated live feed requires account authorization.
    return f'''<section class="section instagram-section" id="instagram"><div class="container">
      <div class="section-head section-head--split"><div><p class="eyebrow">Instagram</p><h2 class="h2">@{INSTAGRAM}</h2></div><a class="btn" href="{INSTAGRAM_URL}" target="_blank" rel="noopener">{ic('insta')} Ver no Instagram</a></div>
      <div class="instagram-feed"><blockquote class="instagram-media" data-instgrm-permalink="{INSTAGRAM_URL}" data-instgrm-version="14"><a href="{INSTAGRAM_URL}" target="_blank" rel="noopener">Ver publicações de @{INSTAGRAM} no Instagram</a></blockquote></div>
      <script async src="https://www.instagram.com/embed.js"></script>
    </div></section>'''


def post_media(post):
    return post.get('image') or LOGO_WHITE

def post_date(post):
    return f'<time datetime="{escape(post["date"])}">{escape(post["date"])}</time>' if post.get('date') else ''

def blog_section():
    cards = ''.join(f'''<article class="card"><a class="card__media" href="/blog#{escape(post['id'])}">{img(post_media(post),post['title'],1200,800)}</a><div><p class="eyebrow">Notícias</p>{post_date(post)}<h3 class="card__title"><a href="/blog#{escape(post['id'])}">{escape(post['title'])}</a></h3><p class="muted">{escape(post['text'].split(chr(10))[0])}</p></div></article>''' for post in POSTS[:3])
    return f'''<section class="section theme-ink2 news-highlights"><div class="container"><div class="section-head section-head--split"><div><p class="eyebrow">Blog</p><h2 class="h1">{T('news_heading')}</h2></div><a class="btn" href="/blog">Ver notícias {ic('arrow')}</a></div><div class="cards">{cards}</div></div></section>'''

def page_blog():
    articles = ''
    for post in POSTS:
        project = P.get(post.get('project_slug'))
        paragraphs = ''.join(f'<p class="lead">{escape(text)}</p>' for text in post['text'].split('\n\n') if text.strip())
        link = f'<a class="btn" href="/{project["slug"]}">Conhecer o {escape(project["name"])} {ic("arrow")}</a>' if project else ''
        articles += f'''<article class="section" id="{escape(post['id'])}"><div class="container"><div class="split"><div class="split__media">{img(post_media(post),post['title'],1200,800)}</div><div class="split__body"><p class="eyebrow">Notícias</p>{post_date(post)}<h2 class="h2">{escape(post['title'])}</h2>{paragraphs}{link}</div></div></div></article>'''
    body = page_hero(T('news_heading'),'Blog Kyma',[('/', 'Início'),(None,'Blog')],short=True)+articles
    return layout(path='/blog',active='/blog',title='Blog | Notícias da Kyma Empreendimentos',desc='Notícias e informações dos empreendimentos Kyma.',body=body)


def help_section():
    subjects = [('Procurando por um imóvel', 'key'), ('Financeiro', 'building'), ('Seguro de entrega', 'key'), ('Trabalhe conosco', 'building'), ('Negocie seu terreno', 'pin'), ('Sou fornecedor', 'building'), ('Boleto bancário', 'building'), ('Solicitar assistência', 'building'), ('Sou vizinho de uma obra', 'pin'), ('Relatar desvio de conduta', 'phone'), ('Enviar e-mail', 'phone'), ('Assessoria de imprensa', 'phone'), ('Privacidade de dados', 'key')]
    items = ''.join(f'<a class="help-card" href="#contact-form" data-subject="{label}">{ic(icon)}<span>{label}</span>{ic("arrow-ur")}</a>' for label, icon in subjects)
    return f'''<section class="section theme-light"><div class="container"><div class="section-head"><p class="eyebrow">Atendimento Kyma</p><h2 class="h1">Precisando de <em>ajuda?</em></h2><p class="lead">Selecione o assunto. O formulário abaixo encaminha sua mensagem à equipe pelo WhatsApp.</p></div><div class="help-grid">{items}</div></div></section>'''


def page_404():
    body = f"""
<section class="notfound">
  <div style="display:grid;gap:26px;justify-items:center">
    <p class="eyebrow eyebrow--plain">Página não encontrada</p>
    <h1 class="display">404</h1>
    <p class="lead">Parece que esse endereço não existe — mas o seu próximo pode estar a um clique.</p>
    <div class="hero__cta" style="justify-content:center">
      <a class="btn btn--solid" href="/">Voltar ao início {ic("arrow")}</a>
      <a class="btn" href="/empreendimentos">Ver empreendimentos</a>
    </div>
  </div>
</section>"""
    html = layout(path="/404", title="Página não encontrada | Kyma Empreendimentos",
                  desc="A página que você procura não foi encontrada.", body=body)
    return html.replace('content="index, follow, max-image-preview:large"', 'content="noindex, follow"')


def data_js():
    data = {
        "whatsapp": WHATSAPP, "phone": PHONE, "address": ADDRESS, "instagram": INSTAGRAM, "mapsUrl": MAPS_URL,
        "projects": [
            {
                "slug": p["slug"], "name": p["name"], "status": p["status"], "location": p["location"],
                "area": p["area"], "beds": p["beds"], "pitch": p["pitch"],
                "progress": p["progress"], "coordinates": p["coordinates"], "mapSource": p["map_source"], "url": f"/{p['slug']}",
                "thumb": p["card"][0], "contain": p["contain"],
            } for p in PROJECTS
        ],
    }
    return "/* Gerado por build.py — não edite à mão */\nwindow.KYMA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n"


def main():
    pages = {
        "index.html": page_home(),
        "empreendimentos.html": page_listing("empreendimentos"),
        "lancamentos.html": page_listing("lancamentos"),
        "quem-somos.html": page_about(),
        "contato.html": page_contact(),
        "blog.html": page_blog(),
        "404.html": page_404(),
    }
    for p in PROJECTS:
        pages[f"{p['slug']}.html"] = page_haus() if p["slug"] == "haus" and HAUS else page_project(p)
    manifest = ROOT / 'content/generated-pages.json'
    previous = json.loads(manifest.read_text()) if manifest.exists() else []
    for name, html in pages.items():
        target = ROOT / name
        temp = target.with_suffix('.html.tmp')
        temp.write_text(html,encoding='utf-8')
        temp.replace(target)
    for old in previous:
        if old not in pages and '/' not in old and old.endswith('.html'):
            (ROOT / old).unlink(missing_ok=True)
    manifest.write_text(json.dumps(list(pages),indent=2)+'\n')
    (ROOT / "assets/js/data.js").write_text(data_js(), encoding="utf-8")

    today = date.today().isoformat()
    urls = ["/", "/empreendimentos", "/lancamentos", "/quem-somos", "/blog", "/contato"] + [f"/{p['slug']}" for p in PROJECTS]
    prio = {"/": "1.0", "/empreendimentos": "0.9", "/lancamentos": "0.9"}
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sitemap.append(f"  <url><loc>{SITE}{u}</loc><lastmod>{today}</lastmod><priority>{prio.get(u, '0.8')}</priority></url>")
    sitemap.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sitemap) + "\n", encoding="utf-8")
    print(f"OK — {len(pages)} páginas geradas.")


if __name__ == "__main__":
    main()
