# Kyma Empreendimentos — site

Site estático premium da Kyma Empreendimentos, feito para substituir o WordPress/Elementor.
HTML + CSS + JS puros: sem framework, sem build obrigatório, carregamento rápido.

## Páginas

| URL | Arquivo |
| --- | --- |
| `/` | `index.html` — hero com slider, manifesto, lançamentos, portfólio, valores |
| `/empreendimentos` | lista completa com filtros |
| `/lancamentos` | Haus, Mon Trésor e Azure |
| `/haus` | página completa (plantas, lazer, galeria, mapa) |
| `/mon-tresor`, `/azure`, `/monte-cristo`, `/monte-negro`, `/monte-zurich`, `/altos-do-parque`, `/serra-do-sincora` | páginas de cada empreendimento |
| `/quem-somos`, `/contato`, `/404` | institucionais |

## Destaques

- **Kyma Concierge**: chat com assistente virtual (efeito de digitação, respostas rápidas,
  cards dos empreendimentos, agendamento de visita) que entrega o lead no WhatsApp com a
  mensagem pronta. Tudo no navegador, em `assets/js/chat.js`.
- **Animações**: preloader, texto revelado palavra a palavra, parallax, revelação de imagens,
  cursor customizado, botões magnéticos, marquee, contadores, transição entre páginas.
  Respeita `prefers-reduced-motion`.
- **SEO**: títulos e descrições únicos, canonical, Open Graph/Twitter, JSON-LD
  (Organization, ApartmentComplex, BreadcrumbList, ItemList), `sitemap.xml`, `robots.txt`,
  HTML semântico e conteúdo visível mesmo sem JavaScript.

## Como editar

O conteúdo fica no topo do `build.py` (empreendimentos, contatos, textos). Depois de editar:

```bash
python3 build.py
```

Isso regenera todas as páginas `.html`, o `sitemap.xml` e o `assets/js/data.js` usado pelo chat.
Estilos em `assets/css/style.css`; interações em `assets/js/main.js`.

## Imagens

As imagens são reaproveitadas do WordPress atual (`kyma.com.br/wp-content/uploads`).
Antes de desligar o WordPress, copie a pasta `wp-content/uploads` para `assets/img` e troque
a constante `UP` no `build.py` para `"/assets/img"`.

## Rodar localmente

```bash
npx serve .
```

(`serve` entende URLs limpas como `/haus`.)

## Deploy

Pronto para Vercel: o `vercel.json` ativa URLs limpas, redireciona `/home` e faz cache dos assets.
