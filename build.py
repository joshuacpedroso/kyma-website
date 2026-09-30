#!/usr/bin/env python3
"""
Gerador do site estático da Kyma Empreendimentos.

Uso:  python3 build.py

Todo o conteúdo (empreendimentos, textos, contatos) fica aqui em cima.
Edite, rode o script e as páginas .html + sitemap.xml são regeneradas.
"""
import json
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).parent
SITE = "https://kyma.com.br"

# Imagens reaproveitadas do WordPress. Quando copiar os arquivos para
# /assets/img (mantendo a mesma estrutura de pastas), troque por "/assets/img".
UP = "https://kyma.com.br/wp-content/uploads"

BRAND = "Kyma Empreendimentos"
PHONE = "(12) 3878-4488"
PHONE_INTL = "+55-12-3878-4488"
WHATSAPP = "551238784488"
INSTAGRAM = "kymaempreendimentos"
INSTAGRAM_URL = f"https://www.instagram.com/{INSTAGRAM}/"
ADDRESS = "Av. Alfredo Ignácio Nogueira Penido, 305 – Sala 1.301, São José dos Campos – SP"
MAPS_Q = "Av. Alfredo Ignácio Nogueira Penido, 305, São José dos Campos - SP"
MAPS_URL = "https://www.google.com/maps/search/?api=1&query=" + quote(MAPS_Q)
MAPS_EMBED = "https://www.google.com/maps?q=" + quote(MAPS_Q) + "&output=embed"

LOGO_WHITE = f"{UP}/2022/04/logo-kyma-branco-full.png"
FAVICON = f"{UP}/2022/06/cropped-logo-kyma02"


def wa(msg: str) -> str:
    return f"https://wa.me/{WHATSAPP}?text={quote(msg)}"


# --------------------------------------------------------------------------
# Empreendimentos
# --------------------------------------------------------------------------
PROJECTS = [
    dict(
        slug="haus", name="Haus", full="Residencial Haus Vila Ema", status="lancamento",
        region="vale", city="São José dos Campos", hood="Vila Ema",
        location="Vila Ema · São José dos Campos", street="Rua Padre Rodolfo, 286",
        area="79,95m² e 82,21m²", beds="2 dormitórios",
        pitch="Moderno, sofisticado e completo, em uma das regiões mais desejadas de São José dos Campos.",
        card=(f"{UP}/2025/01/obra-haus-1024x573.jpg", 1024, 573),
        hero=(f"{UP}/2024/11/Kyma_Haus_Lateral_OK-2048x1625.jpg", 2048, 1625),
        logo=(f"{UP}/2022/05/haus0.png", f"{UP}/2022/05/SIT.png"),
        wa_link="https://w.app/CoXsmt",
    ),
    dict(
        slug="mon-tresor", name="Mon Trésor", full="Residencial Mon Trésor", status="lancamento",
        region="vale", city="São José dos Campos", hood="Vila Ema",
        location="Vila Ema · São José dos Campos", street="Em frente à Igreja Sagrada Família",
        area="114,66m²", beds=None,
        pitch="Arquitetura marcante e plantas amplas, em frente à Igreja Sagrada Família — um novo marco na Vila Ema.",
        card=(f"{UP}/2025/01/obra-mon-2-1024x573.jpg", 1024, 573),
        hero=(f"{UP}/2025/01/obra-mon-2.jpg", 1200, 672),
        logo=(f"{UP}/2022/05/monte-tresor0.png", f"{UP}/2022/05/SITE-1.png"),
    ),
    dict(
        slug="azure", name="Azure", full="Residencial Azure", status="lancamento",
        region="litoral", city="Caraguatatuba", hood="Tabatinga",
        location="Tabatinga · Caraguatatuba", street=None,
        area=None, beds=None,
        pitch="O Litoral Norte como endereço: um lançamento pensado para quem quer viver — ou investir — perto do mar.",
        card=(f"{UP}/2025/01/obra-azure-new-1024x573.jpg", 1024, 573),
        hero=(f"{UP}/2025/01/obra-azure-new.jpg", 1200, 672),
        logo=(f"{UP}/2022/05/azure.png", f"{UP}/2022/05/COLORIDO.png"),
    ),
    dict(
        slug="monte-cristo", name="Monte Cristo", full="Residencial Monte Cristo", status="portfolio",
        region="vale", city="São José dos Campos", hood=None,
        location="São José dos Campos · SP", street=None,
        area="65,76m²", beds=None,
        pitch="Plantas inteligentes e bem distribuídas, com a assinatura de qualidade Kyma.",
        card=(f"{UP}/2022/05/site-miniatura-monte-cristo-1-1024x576.png", 1024, 576),
        hero=(f"{UP}/2022/05/site-miniatura-monte-cristo-1.png", 1200, 675),
        logo=(f"{UP}/2022/05/monte-cristo0.png", f"{UP}/2022/05/image-1.png"),
    ),
    dict(
        slug="monte-negro", name="Monte Negro", full="Residencial Monte Negro", status="portfolio",
        region="vale", city="São José dos Campos", hood=None,
        location="São José dos Campos · SP", street=None,
        area="68,94m²", beds=None,
        pitch="Conforto e praticidade para o dia a dia, em uma localização estratégica da cidade.",
        card=(f"{UP}/2022/05/capa-monte-negro-1024x576.png", 1024, 576),
        hero=(f"{UP}/2022/05/capa-monte-negro.png", 1200, 675),
        logo=(f"{UP}/2022/05/monte-negro0.png", f"{UP}/2022/05/image.png"),
    ),
    dict(
        slug="monte-zurich", name="Monte Zurich", full="Residencial Monte Zurich", status="portfolio",
        region="vale", city="São José dos Campos", hood=None,
        location="São José dos Campos · SP", street=None,
        area="69,60m²", beds=None,
        pitch="Linhas contemporâneas e espaços bem aproveitados para viver com leveza.",
        card=(f"{UP}/2022/05/capa-zurich-1024x576.png", 1024, 576),
        hero=(f"{UP}/2022/05/capa-zurich.png", 1200, 675),
        logo=(f"{UP}/2022/05/monte-zurich0.png", f"{UP}/2022/05/500X500.png"),
    ),
    dict(
        slug="altos-do-parque", name="Altos do Parque", full="Altos do Parque", status="portfolio",
        region="vale", city=None, hood=None,
        location="Região Sul", street=None,
        area=None, beds=None,
        pitch="Localização privilegiada na região Sul, com a natureza como vizinha.",
        card=(f"{UP}/2022/05/site-2.png", 500, 500), contain=True,
        hero=None, hero_logo=(f"{UP}/2022/05/altos-do-parque-branco.png", 500, 350),
        logo=(f"{UP}/2022/05/altos-do-parque0.png", f"{UP}/2022/05/site-2.png"),
    ),
    dict(
        slug="serra-do-sincora", name="Serra do Sincorá", full="Serra do Sincorá", status="portfolio",
        region="outros", city=None, hood=None,
        location="Consulte a localização", street=None,
        area=None, beds=None,
        pitch="Um projeto que integra o portfólio Kyma — fale com nosso time para conhecer os detalhes.",
        card=(f"{UP}/2022/05/image-3.png", 500, 500), contain=True,
        hero=None, hero_logo=(f"{UP}/2022/05/image-3.png", 500, 500),
        logo=(f"{UP}/2022/05/sincora00.jpg", f"{UP}/2022/05/image-3.png"),
    ),
]
P = {p["slug"]: p for p in PROJECTS}
for p in PROJECTS:
    p.setdefault("contain", False)
    p.setdefault("wa_link", wa(f"Olá! Vim pelo site e gostaria de mais informações sobre o {p['name']}."))

LAUNCHES = [p for p in PROJECTS if p["status"] == "lancamento"]
PORTFOLIO = [p for p in PROJECTS if p["status"] == "portfolio"]

HAUS = dict(
    about=[
        "O HAUS Vila Ema está localizado em uma das regiões mais desejadas de São José dos Campos, com infraestrutura completa e opções de lazer, cultura, gastronomia e serviços. A torre possui plantas de 79,95m² e 82,21m², com dois dormitórios.",
        "O empreendimento combina conforto, conveniência, modernidade e uma localização privilegiada — ideal para quem busca qualidade de vida, oferecendo facilidade na rotina dos proprietários ou se tornando uma ótima oportunidade de investimento.",
    ],
    private=[
        "Área gourmet com churrasqueira", "Área técnica e infra para ar-condicionado", "Bancada em granito",
        "Conceito aberto", "Fechadura biométrica", "Hobby box", "Porta anti-impacto",
        "2 vagas cobertas e demarcadas em subsolo",
    ],
    common=[
        "Piscina adulto e infantil com deck molhado e borda infinita", "Academia", "Espaço gym", "Sauna", "Solarium",
        "Coworking outdoor e indoor", "Sala de reuniões", "Salão de festas", "Sala de jogos", "Brinquedoteca",
        "Playground", "Espaço lareira", "Espaço outdoor", "Lounge externo", "Sala de estar", "Churrasqueira",
        "Bicicletário", "Carregamento veicular", "Pulmão de segurança",
    ],
    blocks=[
        dict(eyebrow="Open", title="Open <em>space</em>", img=(f"{UP}/2024/11/fechado-2.jpg", 1920, 1080), feats=[
            ("Ar-condicionado", "Infraestrutura para ar-condicionado entregue em dormitórios e sala."),
            ("Aquecimento de água individual a gás", "Proporcionando muito mais praticidade."),
            ("Churrasqueira integrada", "Churrasqueira a carvão com ponto extra para gás."),
            ("Fechaduras elétricas", "Fechadura eletromecânica nas áreas sociais."),
        ]),
        dict(eyebrow="O imóvel", title="Do seu <em>jeito</em>", img=(f"{UP}/2024/11/1_3-Foto.jpg", 1074, 1080), feats=[
            ("Menos ruídos", "Borracha atenuadora de ruídos nas portas."),
            ("Personalização em revestimentos e pedras", "Crie a sua identidade para o imóvel."),
            ("Ventilação natural", "Além de ecológica, garante maior conforto nos espaços internos."),
            ("Vista privilegiada", "Visão para um dos principais pontos da cidade."),
        ]),
        dict(eyebrow="Conforto &amp;", title="Exclusi&shy;<em>vidade</em>", img=(f"{UP}/2024/11/Kyma_Haus_Lateral_OK-1024x813.jpg", 1024, 813), feats=[
            ("Ambientes integrados", "Entregue com piso nivelado e fechamento na sacada."),
            ("Bancadas em granito", "Tornando o apartamento muito mais elegante e funcional."),
            ("Banheiros com circulação de ar natural", "Sem necessidade de ventilação mecânica."),
            ("Revestimento Portobello", "Áreas frias com revestimento Portobello."),
        ]),
    ],
    plans=[
        (f"{UP}/2024/11/planta-1-haus.png", f"{UP}/2024/11/planta-1-haus-1024x870.png", 1024, 870, "Planta tipo 1"),
        (f"{UP}/2024/11/planta-2-haus.png", f"{UP}/2024/11/planta-2-haus-1024x872.png", 1024, 872, "Planta tipo 2"),
    ],
)

VALUES = [
    ("Visão", "Identificar e viabilizar as melhores oportunidades do mercado imobiliário, sendo reconhecida por investidores, fornecedores e clientes."),
    ("Missão", "Agregar valor aos empreendimentos realizados, a fim de superar as expectativas de nossos clientes e investidores."),
    ("Valores", "Ética, transparência, credibilidade, compromisso, disciplina e criatividade."),
]

ABOUT = ("Somos uma empresa da indústria da construção civil que atua regionalmente no Vale do Paraíba e no "
         "Litoral Norte do Estado de São Paulo. Oferecemos empreendimentos atuais, que primam pela qualidade, "
         "localização e que tragam o retorno esperado aos nossos clientes — sempre em busca da satisfação de "
         "investidores, parceiros, fornecedores e consumidores finais, proporcionando uma experiência única no mercado.")

NAV = [("/empreendimentos", "Empreendimentos"), ("/lancamentos", "Lançamentos"),
       ("/quem-somos", "Quem somos"), ("/contato", "Contato")]

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


def ic(name: str) -> str:
    return f'<svg aria-hidden="true"><use href="#i-{name}"/></svg>'


def img(src, alt, w, h, cls="", eager=False, extra=""):
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    c = f' class="{cls}"' if cls else ""
    return f'<img src="{src}" alt="{escape(alt)}" width="{w}" height="{h}" {load} decoding="async"{c}{extra}>'


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
    <a class="brand" href="/" aria-label="{BRAND} — página inicial">
      <img src="{LOGO_WHITE}" alt="{BRAND}" width="461" height="140">
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
      <a class="footer-big" href="/contato" data-cursor="Contato">Encontre o seu <em>lugar.</em> <span class="arrow-c">{ic("arrow-ur")}</span></a>
    </div>
    <div class="footer-grid">
      <div class="footer-brand">
        <img src="{LOGO_WHITE}" alt="{BRAND}" width="461" height="140" loading="lazy">
        <p>Empreendimentos atuais, com qualidade e localização, no Vale do Paraíba e Litoral Norte de São Paulo.</p>
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
  <div class="footer-word" aria-hidden="true">Kyma</div>
</footer>"""


def meta_items(p, cls="card__meta"):
    bits = []
    if p.get("area"):
        bits.append(f'<span>{ic("area")}{p["area"]}</span>')
    bits.append(f'<span>{ic("pin")}{p["location"]}</span>')
    return f'<div class="{cls}">{"".join(bits)}</div>'


def card(p, tags=True):
    c, w, h = p["card"]
    t = f' data-tags="{p["status"]} {p["region"]}"' if tags else ""
    badge = '<span class="badge">Lançamento</span>' if p["status"] == "lancamento" else ""
    return f"""
<article class="card"{t}>
  <a class="card__media{' is-contain' if p['contain'] else ''}" href="/{p['slug']}" data-cursor="Ver" data-tilt aria-label="Conhecer o {escape(p['name'])}">
    {badge}{img(c, f"{p['full']} — {p['location']}", w, h)}
    <span class="card__go">{ic("arrow-ur")}</span>
  </a>
  <div>
    <h3 class="card__title"><a href="/{p['slug']}">{p['name']}</a></h3>
    {meta_items(p)}
  </div>
</article>"""


def cta_band(title="Está procurando um <em>apartamento?</em>", text="Fale com um de nossos corretores e descubra o empreendimento ideal para o seu momento.",
             bg=(f"{UP}/2024/11/fechado-2.jpg", 1920, 1080), msg="Olá! Estou procurando um apartamento e gostaria de ajuda."):
    return f"""
<section class="section section--tight">
  <div class="container">
    <div class="cta" data-reveal>
      <div class="cta__bg" data-parallax="0.12">{img(bg[0], "", bg[1], bg[2])}</div>
      <p class="eyebrow">Atendimento exclusivo</p>
      <h2 class="h2" data-split>{title}</h2>
      <p class="lead">{text}</p>
      <div class="cta__actions">
        <a class="btn btn--solid" data-magnetic href="{wa(msg)}" target="_blank" rel="noopener">{ic("wa")} Chamar no WhatsApp</a>
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
    url = SITE + (path if path != "/" else "/")
    og = og_image or f"{UP}/2024/11/Kyma_Haus_Lateral_OK-1024x813.jpg"
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
<meta name="theme-color" content="#0b0c0c">
<meta name="format-detection" content="telephone=no">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="{BRAND}">
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
<link rel="icon" href="{FAVICON}-32x32.png" sizes="32x32">
<link rel="icon" href="{FAVICON}-192x192.png" sizes="192x192">
<link rel="apple-touch-icon" href="{FAVICON}-180x180.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://kyma.com.br">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&amp;family=Playfair+Display:ital,wght@0,400;0,500;1,400;1,500&amp;display=swap">
<link rel="stylesheet" href="/assets/css/style.css">
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
    <p class="preloader__tag">A vida ideal é a real</p>
  </div>
</div>
{header(active)}
<main id="conteudo">
{body}
</main>
{footer()}
<script src="/assets/js/data.js" defer></script>
<script src="/assets/js/main.js" defer></script>
<script src="/assets/js/chat.js" defer></script>
</body>
</html>
"""


# --------------------------------------------------------------------------
# Páginas
# --------------------------------------------------------------------------
def page_home():
    slides = [
        (f"{UP}/2024/11/Kyma_Haus_Lateral_OK-2048x1625.jpg", 2048, 1625, "Haus — Vila Ema, São José dos Campos"),
        (f"{UP}/2025/01/obra-mon-2.jpg", 1200, 672, "Mon Trésor — Vila Ema, São José dos Campos"),
        (f"{UP}/2024/11/fechado-2.jpg", 1920, 1080, "Haus — Open space"),
        (f"{UP}/2025/01/obra-azure-new.jpg", 1200, 672, "Azure — Tabatinga, Caraguatatuba"),
    ]
    slide_html = "".join(
        f'<div class="hero__slide{" is-active" if i == 0 else ""}" data-caption="{escape(c)}">'
        f'{img(s, c, w, h, eager=(i == 0))}</div>'
        for i, (s, w, h, c) in enumerate(slides))
    dots = "".join(
        f'<button type="button" aria-label="Imagem {i + 1}" aria-current="{"true" if i == 0 else "false"}"></button>'
        for i in range(len(slides)))

    logos = "".join(
        f'<a class="marquee__item" href="/{p["slug"]}" aria-label="{escape(p["name"])}">'
        f'<img class="base" src="{p["logo"][0]}" alt="" width="200" height="200" loading="lazy">'
        f'<img class="alt" src="{p["logo"][1]}" alt="" width="200" height="200" loading="lazy"></a>'
        f'<span class="marquee__word" aria-hidden="true">✦</span>'
        for p in PROJECTS)

    shows = ""
    for i, p in enumerate(LAUNCHES):
        c, w, h = p["card"]
        facts = "".join(filter(None, [
            f'<span>{ic("pin")}{p["location"]}</span>',
            f'<span>{ic("area")}{p["area"]}</span>' if p["area"] else "",
            f'<span>{ic("bed")}{p["beds"]}</span>' if p["beds"] else "",
        ]))
        shows += f"""
<article class="show">
  <a class="show__media reveal-img" href="/{p['slug']}" data-cursor="Ver">
    <span class="badge">Lançamento</span>
    {img(c, f"{p['full']} — {p['location']}", w, h)}
  </a>
  <div class="show__body">
    <span class="show__num" aria-hidden="true">0{i + 1}</span>
    <h3 class="h2" data-split>{p['name']}</h3>
    <p class="lead" data-reveal>{p['pitch']}</p>
    <div class="show__meta" data-reveal>{facts}</div>
    <div data-reveal><a class="link-arrow" href="/{p['slug']}">Conhecer o {p['name']} <span class="line"></span></a></div>
  </div>
</article>"""

    haus = P["haus"]
    band_items = "".join(f"<li>{x}</li>" for x in [
        "Piscina com borda infinita", "Academia e sauna", "Coworking indoor e outdoor",
        "Fechadura biométrica", "2 vagas cobertas", "Carregamento veicular"])

    portfolio_cards = "".join(card(p, tags=False) for p in PORTFOLIO)
    insta_imgs = [
        (f"{UP}/2024/11/1_3-Foto.jpg", "Interior decorado do Haus"),
        (f"{UP}/2025/01/obra-haus-1024x573.jpg", "Obra do Haus"),
        (f"{UP}/2025/01/obra-mon-2-1024x573.jpg", "Obra do Mon Trésor"),
        (f"{UP}/2025/01/obra-azure-new-1024x573.jpg", "Obra do Azure"),
    ]
    insta = "".join(
        f'<a href="{INSTAGRAM_URL}" target="_blank" rel="noopener" data-cursor="Seguir">{img(s, a, 600, 600)}{ic("insta")}</a>'
        for s, a in insta_imgs)
    pillars = "".join(
        f'<div class="pillar"><span class="pillar__n">0{i + 1}</span><h3>{t}</h3><p>{x}</p></div>'
        for i, (t, x) in enumerate(VALUES))

    body = f"""
<section class="hero" data-hero-slider aria-label="Destaques">
  <div class="hero__slides">{slide_html}</div>
  <div class="hero__content">
    <div class="container">
      <p class="eyebrow" data-hero>Kyma Empreendimentos · Vale do Paraíba &amp; Litoral Norte</p>
      <h1 class="display" data-split="0.2">A vida ideal <em>é a real.</em></h1>
      <p class="hero__sub" data-hero="2">Empreendimentos que unem arquitetura, localização e qualidade construtiva para transformar o seu jeito de morar — e de investir.</p>
      <div class="hero__cta" data-hero="3">
        <a class="btn btn--solid" data-magnetic href="/empreendimentos">Ver empreendimentos {ic("arrow")}</a>
        <a class="btn btn--glass" data-magnetic href="/lancamentos">Lançamentos</a>
      </div>
    </div>
  </div>
  <div class="hero__meta" data-hero="4">
    <p class="hero__count"><b>01</b> / 0{len(slides)}</p>
    <p class="hero__caption">{slides[0][3]}</p>
    <div class="hero__bar"><span></span></div>
    <div class="hero__dots">{dots}</div>
  </div>
  <span class="scroll-hint" aria-hidden="true"></span>
</section>

<section class="marquee" aria-label="Nossos empreendimentos">
  <div class="marquee__track">
    <div class="marquee__group">{logos}</div>
    <div class="marquee__group" aria-hidden="true">{logos}</div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="manifesto__grid">
      <div class="manifesto__side">
        <p class="eyebrow" data-reveal>Quem somos</p>
        <p class="muted" data-reveal>Construção civil com propósito, do Vale do Paraíba ao Litoral Norte de São Paulo.</p>
        <div data-reveal><a class="link-arrow" href="/quem-somos">Conheça a Kyma <span class="line"></span></a></div>
      </div>
      <h2 class="manifesto__text" data-words>Criamos empreendimentos atuais, que primam pela <em>qualidade</em>, pela <em>localização</em> e pelo retorno que cada cliente espera. Porque, para nós, a vida ideal não é um sonho distante — ela é real, e começa no endereço certo.</h2>
    </div>
    <div class="stats">
      <div class="stat" data-reveal><span class="stat__num" data-count="{len(PROJECTS)}" data-pad="2">{len(PROJECTS):02d}</span><span class="stat__label">Empreendimentos no portfólio</span></div>
      <div class="stat" data-reveal><span class="stat__num" data-count="{len(LAUNCHES)}" data-pad="2">{len(LAUNCHES):02d}</span><span class="stat__label">Lançamentos em andamento</span></div>
      <div class="stat" data-reveal><span class="stat__num" data-count="2" data-pad="2">02</span><span class="stat__label">Regiões: Vale do Paraíba e Litoral Norte</span></div>
    </div>
  </div>
</section>

<section class="section theme-ink2" id="lancamentos">
  <div class="container">
    <div class="section-head section-head--split">
      <div style="display:grid;gap:22px">
        <p class="eyebrow" data-reveal>Lançamentos</p>
        <h2 class="h1" data-split>Novos endereços, <em>novas histórias.</em></h2>
      </div>
      <a class="btn" data-reveal data-magnetic href="/lancamentos">Todos os lançamentos {ic("arrow")}</a>
    </div>
    <div class="showcase">{shows}</div>
  </div>
</section>

<section class="band" aria-label="Destaque Haus">
  <div class="band__bg" data-parallax="0.14">{img(haus["hero"][0], "Fachada do Residencial Haus Vila Ema", haus["hero"][1], haus["hero"][2])}</div>
  <div class="container">
    <div class="band__card">
      <p class="eyebrow" data-reveal>Em destaque · Vila Ema</p>
      <h2 class="h1" data-split>Haus. <em>Lazer de clube,</em> rotina de cidade.</h2>
      <p class="lead" data-reveal>Plantas de 79,95m² e 82,21m² com 2 dormitórios, conceito aberto e uma estrutura de lazer completa na Rua Padre Rodolfo, 286.</p>
      <ul class="band__list" data-stagger="0.08">{band_items}</ul>
      <div data-reveal><a class="btn btn--solid" data-magnetic href="/haus">Conhecer o Haus {ic("arrow")}</a></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head section-head--split">
      <div style="display:grid;gap:22px">
        <p class="eyebrow" data-reveal>Portfólio</p>
        <h2 class="h1" data-split>Obras que <em>assinamos.</em></h2>
      </div>
      <a class="btn" data-reveal data-magnetic href="/empreendimentos">Ver todos {ic("arrow")}</a>
    </div>
    <div class="hscroll" data-reveal>{portfolio_cards}</div>
  </div>
</section>

<section class="section theme-light">
  <div class="container">
    <div class="section-head">
      <p class="eyebrow" data-reveal>Compromisso</p>
      <h2 class="h1" data-split>O que nos <em>move.</em></h2>
    </div>
    <div class="pillars" data-stagger="0.12">{pillars}</div>
  </div>
</section>

{cta_band()}

<section class="section section--tight">
  <div class="container">
    <div class="section-head section-head--split">
      <div style="display:grid;gap:22px">
        <p class="eyebrow" data-reveal>Redes sociais</p>
        <h2 class="h2" data-split>Acompanhe cada <em>etapa da obra.</em></h2>
      </div>
      <a class="btn" data-reveal href="{INSTAGRAM_URL}" target="_blank" rel="noopener">{ic("insta")} @{INSTAGRAM}</a>
    </div>
    <div class="insta" data-stagger="0.08">{insta}</div>
  </div>
</section>"""

    return layout(
        path="/", page="home",
        title="Kyma Empreendimentos | Apartamentos em São José dos Campos e Litoral Norte",
        desc="Kyma Empreendimentos: lançamentos e apartamentos em São José dos Campos (Vila Ema) e no Litoral Norte. Conheça Haus, Mon Trésor, Azure e todo o portfólio.",
        body=body, preload=slides[0][0],
        jsonld=[ORG, {"@context": "https://schema.org", "@type": "WebSite", "name": BRAND, "url": SITE + "/", "inLanguage": "pt-BR", "publisher": {"@id": f"{SITE}/#org"}}],
    )


def page_listing(kind):
    if kind == "empreendimentos":
        items, path = PROJECTS, "/empreendimentos"
        title_html = "Nossos <em>empreendimentos</em>"
        eyebrow = f"{len(PROJECTS)} projetos · Vale do Paraíba &amp; Litoral Norte"
        lead = "Do lançamento à entrega, cada projeto Kyma nasce do mesmo compromisso: qualidade, localização e retorno para quem confia na gente."
        bg = (f"{UP}/2024/11/fechado-2.jpg", 1920, 1080)
        title = "Empreendimentos | Kyma Empreendimentos"
        desc = "Conheça todos os empreendimentos da Kyma: Haus, Mon Trésor, Azure, Monte Cristo, Monte Negro, Monte Zurich e mais, em São José dos Campos e Litoral Norte."
        filters = [("todos", "Todos"), ("lancamento", "Lançamentos"), ("portfolio", "Portfólio"), ("vale", "Vale do Paraíba"), ("litoral", "Litoral Norte")]
    else:
        items, path = LAUNCHES, "/lancamentos"
        title_html = "Lança&shy;<em>mentos</em>"
        eyebrow = "Oportunidades exclusivas"
        lead = "Seja para morar ou investir, nossos lançamentos estão em regiões que você vai querer chamar de casa."
        bg = (f"{UP}/2025/01/obra-azure-new.jpg", 1200, 672)
        title = "Lançamentos | Kyma Empreendimentos"
        desc = "Lançamentos Kyma: Haus e Mon Trésor na Vila Ema, em São José dos Campos, e Azure em Tabatinga, Caraguatatuba. Agende sua visita."
        filters = [("todos", "Todos"), ("vale", "Vale do Paraíba"), ("litoral", "Litoral Norte")]
    label = "Empreendimentos" if kind == "empreendimentos" else "Lançamentos"
    fbtn = "".join(
        f'<button class="filter" type="button" data-filter="{k}" aria-pressed="{"true" if k == "todos" else "false"}">{l}</button>'
        for k, l in filters)
    cards = "".join(card(p) for p in items)
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
      <p class="filters__count"><b data-filter-count>{len(items):02d}</b> resultados</p>
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
    items.append(f'<span class="chip">{ic("building")}{"Lançamento" if p["status"] == "lancamento" else "Portfólio Kyma"}</span>')
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
    p = P["haus"]
    hero_btns = f"""<div class="hero__cta" data-reveal style="margin-top:8px">
      <a class="btn btn--solid" data-magnetic href="{p['wa_link']}" target="_blank" rel="noopener">{ic("wa")} Quero saber mais</a>
      <a class="btn btn--glass" href="#plantas">Ver plantas {ic("arrow")}</a></div>"""
    about = "".join(f'<p class="lead" data-reveal>{t}</p>' for t in HAUS["about"])
    specs = f"""
<div class="specs" data-stagger="0.08">
  <div class="spec">{ic("area")}<b>79,95 e 82,21m²</b><span>Área privativa</span></div>
  <div class="spec">{ic("bed")}<b>2 dormitórios</b><span>1 suíte + 1 banheiro</span></div>
  <div class="spec">{ic("car")}<b>2 vagas</b><span>Cobertas e demarcadas no subsolo</span></div>
  <div class="spec">{ic("key")}<b>Biometria</b><span>Fechadura biométrica e porta anti-impacto</span></div>
</div>"""
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
  <a class="split__media split__media--tall reveal-img" href="{s}" data-lightbox="haus-amb" data-caption="Haus — {b['eyebrow']}" data-cursor="Ampliar">
    <div data-parallax="0.08" style="height:112%;margin-top:-6%">{img(s, f"Haus Vila Ema — {b['eyebrow']}", w, h)}</div>
    <span class="frame-deco"></span>
  </a>
  <div class="split__body">
    <p class="eyebrow" data-reveal>{b['eyebrow']}</p>
    <h3 class="h1" data-split>{b['title']}</h3>
    <div class="feats" data-stagger="0.08">{feats}</div>
    <div data-reveal><a class="link-arrow" href="{p['wa_link']}" target="_blank" rel="noopener">Mais informações <span class="line"></span></a></div>
  </div>
</div>"""
    plans = "".join(
        f'<figure class="plan" data-reveal><a href="{full}" data-lightbox="haus-plantas" data-caption="Haus — {cap}" data-cursor="Ampliar">{img(med, f"Haus Vila Ema — {cap}", w, h)}</a>'
        f'<figcaption><b>{cap}</b><span>Clique para ampliar</span></figcaption></figure>'
        for full, med, w, h, cap in HAUS["plans"])
    gallery_imgs = [
        (f"{UP}/2024/11/Kyma_Haus_Lateral_OK-2048x1625.jpg", f"{UP}/2024/11/Kyma_Haus_Lateral_OK-1024x813.jpg", 1024, 813, "Fachada"),
        (f"{UP}/2024/11/1_3-Foto.jpg", f"{UP}/2024/11/1_3-Foto.jpg", 1074, 1080, "Interiores"),
        (f"{UP}/2025/01/obra-haus.jpg", f"{UP}/2025/01/obra-haus-1024x573.jpg", 1024, 573, "Andamento da obra"),
        (f"{UP}/2024/11/fechado-2.jpg", f"{UP}/2024/11/fechado-2.jpg", 1920, 1080, "Open space"),
    ]
    gallery = "".join(
        f'<a href="{full}" data-lightbox="haus-galeria" data-caption="Haus — {cap}" data-cursor="Ampliar" data-reveal>{img(med, f"Haus Vila Ema — {cap}", w, h)}</a>'
        for full, med, w, h, cap in gallery_imgs)

    body = page_hero("Haus <em>Vila Ema</em>", "Lançamento · São José dos Campos",
                     [("/", "Início"), ("/lancamentos", "Lançamentos"), (None, "Haus")],
                     bg=p["hero"], facts=facts_chips(p), extra=hero_btns) + f"""
<section class="section theme-light">
  <div class="container">
    <div class="split">
      <div class="split__body">
        <p class="eyebrow" data-reveal>O empreendimento</p>
        <h2 class="h2" data-split>Moderno, sofisticado e <em>completo.</em></h2>
        {about}
        <div data-reveal style="display:flex;gap:14px;flex-wrap:wrap">
          <a class="btn btn--dark" href="{p['wa_link']}" target="_blank" rel="noopener">Falar com corretor {ic("arrow")}</a>
        </div>
      </div>
      <a class="split__media split__media--wide reveal-img" href="{UP}/2024/11/Kyma_Haus_Lateral_OK-2048x1625.jpg" data-lightbox="haus-galeria-top" data-caption="Haus — Fachada" data-cursor="Ampliar">
        {img(f"{UP}/2024/11/Kyma_Haus_Lateral_OK-1024x813.jpg", "Fachada lateral do Residencial Haus Vila Ema", 1024, 813)}
      </a>
    </div>
    <div class="mt-l">{specs}</div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head">
      <p class="eyebrow" data-reveal>Áreas privativas</p>
      <h2 class="h1" data-split>Cada detalhe <em>pensado.</em></h2>
    </div>
    <ul class="amen" data-stagger="0.04">{private}</ul>
  </div>
</section>

<section class="section theme-ink2">
  <div class="container">
    <div class="section-head section-head--split">
      <div style="display:grid;gap:22px">
        <p class="eyebrow" data-reveal>Áreas comuns</p>
        <h2 class="h1" data-split>Lazer de <em>clube.</em></h2>
      </div>
      <p class="lead" data-reveal style="max-width:40ch">São {len(HAUS["common"])} espaços para viver, trabalhar, receber e desacelerar — sem sair de casa.</p>
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
        <h2 class="h1" data-split>Espaços que <em>se adaptam.</em></h2>
      </div>
      <a class="btn btn--dark" data-reveal href="{p['wa_link']}" target="_blank" rel="noopener">Receber plantas completas {ic("arrow")}</a>
    </div>
    <div class="plans">{plans}</div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head">
      <p class="eyebrow" data-reveal>Galeria</p>
      <h2 class="h1" data-split>Veja de <em>perto.</em></h2>
    </div>
    <div class="gallery">{gallery}</div>
  </div>
</section>

<section class="section section--tight">
  <div class="container">
    <div class="section-head">
      <p class="eyebrow" data-reveal>Localização</p>
      <h2 class="h2" data-split>Rua Padre Rodolfo, 286 — <em>Vila Ema.</em></h2>
      <p class="lead" data-reveal>Uma das regiões mais desejadas de São José dos Campos, com infraestrutura completa e opções de lazer, cultura, gastronomia e serviços.</p>
    </div>
    <div class="map" data-reveal><iframe title="Mapa — Haus Vila Ema" loading="lazy" referrerpolicy="no-referrer-when-downgrade" src="https://www.google.com/maps?q={quote('Rua Padre Rodolfo, 286 - Vila Ema, São José dos Campos - SP')}&amp;output=embed"></iframe></div>
  </div>
</section>

{cta_band(title="Seu novo endereço na <em>Vila Ema.</em>", text="Agende uma visita e conheça o Haus de perto com um de nossos corretores.", msg="Olá! Gostaria de agendar uma visita ao Haus Vila Ema.", bg=(f"{UP}/2024/11/1_3-Foto.jpg", 1074, 1080))}
{related(p)}"""
    ld = project_ld(p)
    ld["numberOfBedrooms"] = 2
    ld["amenityFeature"] = [{"@type": "LocationFeatureSpecification", "name": x, "value": True} for x in HAUS["common"]]
    return layout(
        path="/haus", project="haus", active="/lancamentos",
        title="Haus Vila Ema | Apartamentos de 2 dormitórios em São José dos Campos — Kyma",
        desc="Haus Vila Ema: apartamentos de 79,95m² e 82,21m² com 2 dormitórios, lazer completo com piscina de borda infinita e 2 vagas. Rua Padre Rodolfo, 286 — São José dos Campos.",
        body=body, og_image=p["hero"][0], preload=p["hero"][0],
        jsonld=[breadcrumb_ld([("/", "Início"), ("/lancamentos", "Lançamentos"), ("/haus", "Haus")]), ld])


def page_project(p):
    section = "Lançamentos" if p["status"] == "lancamento" else "Empreendimentos"
    sec_path = "/lancamentos" if p["status"] == "lancamento" else "/empreendimentos"
    hero_btns = f"""<div class="hero__cta" data-reveal style="margin-top:8px">
      <a class="btn btn--solid" data-magnetic href="{p['wa_link']}" target="_blank" rel="noopener">{ic("wa")} Quero saber mais</a>
      <a class="btn btn--glass" href="#sobre">Conhecer {ic("arrow")}</a></div>"""
    status_txt = "Lançamento" if p["status"] == "lancamento" else "Portfólio Kyma"
    c, w, h = p["card"]
    big = p["hero"] or p["card"]
    specs = [
        (ic("pin"), p["location"], "Localização"),
        (ic("area"), p["area"] or "Consulte", "Área privativa"),
        (ic("building"), status_txt, "Status"),
        (ic("clock"), "Atendimento", "Corretor dedicado"),
    ]
    spec_html = "".join(f'<div class="spec">{i}<b>{b}</b><span>{s}</span></div>' for i, b, s in specs)
    gallery = [(big[0], c, w, h, "Imagem principal")]
    if p["logo"][1] != c:
        gallery.append((p["logo"][1], p["logo"][1], 500, 500, "Identidade visual"))
    contain_cls = ' class="is-contain"'
    gal_html = "".join(
        f'<a href="{full}" data-lightbox="{p["slug"]}" data-caption="{escape(p["name"])} — {cap}" data-cursor="Ampliar" data-reveal'
        f'{contain_cls if (p["contain"] or i > 0) else ""}>{img(med, p["full"] + " — " + cap, ww, hh)}</a>'
        for i, (full, med, ww, hh, cap) in enumerate(gallery))
    extra_copy = {
        "mon-tresor": "Todos os dias recebemos contatos perguntando se o Residencial Mon Trésor é a obra em frente à Igreja Sagrada Família — e a resposta é sim! Com ótima arquitetura e localização, o empreendimento chega para ser um marco no bairro, com plantas de 114,66m².",
        "azure": "Localizado em Tabatinga, Caraguatatuba, o Azure leva a assinatura Kyma para o Litoral Norte. Fale com nosso time para conhecer plantas, estágio de obra e condições.",
    }.get(p["slug"], "Quer saber mais sobre plantas, disponibilidade e condições? Nosso time de corretores está pronto para te atender com todas as informações atualizadas.")
    body = page_hero(p["name"], f"{status_txt} · {p['location']}",
                     [("/", "Início"), (sec_path, section), (None, p["name"])],
                     bg=p["hero"], bg_logo=p.get("hero_logo"), facts=facts_chips(p), extra=hero_btns) + f"""
<section class="section theme-light" id="sobre">
  <div class="container">
    <div class="split">
      <div class="split__body">
        <p class="eyebrow" data-reveal>O empreendimento</p>
        <h2 class="h2" data-split>{p['full']}</h2>
        <p class="lead" data-reveal>{p['pitch']}</p>
        <p class="lead" data-reveal>{extra_copy}</p>
        <div data-reveal><a class="btn btn--dark" href="{p['wa_link']}" target="_blank" rel="noopener">Falar com corretor {ic("arrow")}</a></div>
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
    body = page_hero("Kyma <em>Empreendimentos</em>", "Quem somos", [("/", "Início"), (None, "Quem somos")],
                     bg=(f"{UP}/2022/05/quem-somos-02.png", 1550, 1330),
                     lead="Construção civil com propósito, do Vale do Paraíba ao Litoral Norte de São Paulo.", short=True) + f"""
<section class="section">
  <div class="container">
    <div class="split">
      <div class="split__media split__media--tall reveal-img">
        <div data-parallax="0.08" style="height:112%;margin-top:-6%">{img(f"{UP}/2022/05/quem-somos-01.png", "Kyma Empreendimentos", 813, 830)}</div>
        <span class="frame-deco"></span>
      </div>
      <div class="split__body">
        <p class="eyebrow" data-reveal>Nossa essência</p>
        <h2 class="h2" data-split>A vida ideal <em>é a real.</em></h2>
        <p class="lead" data-reveal>{ABOUT}</p>
        <div data-reveal style="display:flex;gap:14px;flex-wrap:wrap">
          <a class="btn btn--solid" href="/empreendimentos">Ver empreendimentos {ic("arrow")}</a>
          <a class="btn" href="/contato">Fale conosco</a>
        </div>
      </div>
    </div>
    <div class="stats">
      <div class="stat" data-reveal><span class="stat__num" data-count="{len(PROJECTS)}" data-pad="2">{len(PROJECTS):02d}</span><span class="stat__label">Empreendimentos no portfólio</span></div>
      <div class="stat" data-reveal><span class="stat__num" data-count="{len(LAUNCHES)}" data-pad="2">{len(LAUNCHES):02d}</span><span class="stat__label">Lançamentos em andamento</span></div>
      <div class="stat" data-reveal><span class="stat__num" data-count="2" data-pad="2">02</span><span class="stat__label">Regiões atendidas</span></div>
    </div>
  </div>
</section>

<section class="section theme-light">
  <div class="container">
    <div class="split split--rev">
      <div class="split__media split__media--wide reveal-img">{img(f"{UP}/2022/05/quem-somos-02-1024x879.png", "Empreendimento Kyma", 1024, 879)}</div>
      <div class="split__body">
        <p class="eyebrow" data-reveal>Comprometimento</p>
        <h2 class="h1" data-split>Nossos <em>valores.</em></h2>
        <p class="lead" data-reveal>Oferecemos empreendimentos diferenciados, prezando pela qualidade, segurança e responsabilidade social.</p>
      </div>
    </div>
    <div class="pillars mt-l" data-stagger="0.12">{pillars}</div>
  </div>
</section>

<section class="section theme-ink2">
  <div class="container">
    <div class="section-head section-head--split">
      <div style="display:grid;gap:22px">
        <p class="eyebrow" data-reveal>Lançamentos</p>
        <h2 class="h1" data-split>Conheça nossos <em>lançamentos.</em></h2>
        <p class="lead" data-reveal>Marque uma visita com um de nossos corretores e conheça os lançamentos exclusivos na região.</p>
      </div>
      <a class="btn" data-reveal href="/lancamentos">Ver lançamentos {ic("arrow")}</a>
    </div>
    <div class="cards" data-stagger="0.08">{"".join(card(p, tags=False) for p in LAUNCHES)}</div>
  </div>
</section>
{cta_band()}"""
    return layout(
        path="/quem-somos", active="/quem-somos",
        title="Quem somos | Kyma Empreendimentos",
        desc="Conheça a Kyma Empreendimentos: construção civil no Vale do Paraíba e Litoral Norte de SP, com foco em qualidade, localização e retorno para o cliente.",
        body=body, og_image=f"{UP}/2022/05/quem-somos-02.png", preload=f"{UP}/2022/05/quem-somos-02.png",
        jsonld=[breadcrumb_ld([("/", "Início"), ("/quem-somos", "Quem somos")]), ORG])


def page_contact():
    options = "".join(f'<option value="{p["name"]}">{p["name"]}</option>' for p in PROJECTS)
    body = page_hero("Vamos <em>conversar?</em>", "Contato", [("/", "Início"), (None, "Contato")],
                     bg=(f"{UP}/2024/11/1_3-Foto.jpg", 1074, 1080),
                     lead="Tire dúvidas, agende uma visita ou receba a tabela atualizada. Nosso time responde rapidinho.", short=True) + f"""
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
          <select id="f-int" name="interesse"><option value="">Ainda não sei — quero conhecer as opções</option>{options}</select>
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
<section class="section section--tight" style="padding-top:0">
  <div class="container">
    <div class="map" data-reveal><iframe title="Mapa — escritório Kyma Empreendimentos" loading="lazy" referrerpolicy="no-referrer-when-downgrade" src="{MAPS_EMBED}"></iframe></div>
  </div>
</section>"""
    contact_ld = dict(ORG)
    contact_ld["contactPoint"] = {"@type": "ContactPoint", "telephone": PHONE_INTL, "contactType": "sales", "areaServed": "BR", "availableLanguage": "Portuguese"}
    return layout(
        path="/contato", active="/contato",
        title="Contato | Kyma Empreendimentos — São José dos Campos",
        desc=f"Fale com a Kyma Empreendimentos: WhatsApp e telefone {PHONE}. Escritório na {ADDRESS}. Agende sua visita.",
        body=body, og_image=f"{UP}/2024/11/1_3-Foto.jpg",
        jsonld=[breadcrumb_ld([("/", "Início"), ("/contato", "Contato")]), contact_ld])


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
                "area": p["area"], "beds": p["beds"], "pitch": p["pitch"], "url": f"/{p['slug']}",
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
        "haus.html": page_haus(),
        "404.html": page_404(),
    }
    for p in PROJECTS:
        if p["slug"] != "haus":
            pages[f"{p['slug']}.html"] = page_project(p)
    for name, html in pages.items():
        (ROOT / name).write_text(html, encoding="utf-8")
    (ROOT / "assets/js/data.js").write_text(data_js(), encoding="utf-8")

    today = date.today().isoformat()
    urls = ["/", "/empreendimentos", "/lancamentos", "/quem-somos", "/contato"] + [f"/{p['slug']}" for p in PROJECTS]
    prio = {"/": "1.0", "/empreendimentos": "0.9", "/lancamentos": "0.9"}
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sitemap.append(f"  <url><loc>{SITE}{u}</loc><lastmod>{today}</lastmod><priority>{prio.get(u, '0.8')}</priority></url>")
    sitemap.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sitemap) + "\n", encoding="utf-8")
    print(f"OK — {len(pages)} páginas geradas.")


if __name__ == "__main__":
    main()
