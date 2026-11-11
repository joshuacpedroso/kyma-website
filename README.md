# Kyma Empreendimentos — site

Site estático premium da Kyma Empreendimentos, feito para substituir o WordPress/Elementor.
HTML + CSS + JS puros: sem framework, sem build obrigatório, carregamento rápido.

## Páginas

| URL | Arquivo |
| --- | --- |
| `/` | `index.html` — slider, localizações, destaques e notícias |
| `/empreendimentos` | lista completa com filtros |
| `/lancamentos` | Uniko |
| `/haus` | página completa (plantas, lazer, galeria, mapa) |
| `/mon-tresor`, `/azure`, `/monte-cristo`, `/monte-negro`, `/monte-zurich`, `/altos-do-parque`, `/serra-do-sincora` | páginas de cada empreendimento |
| `/quem-somos`, `/contato`, `/blog`, `/uniko`, `/404` | institucionais |

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

## Revisão de novembro de 2026

Consulte [a conferência dos 23 itens e pendências](docs/REVISAO-2026-11-09.md).

- Galerias oficiais: 7 fotos de Montresor, 22 de Haus, 6 de Azure e 15 imagens de Uniko.
- Status: lançamento somente Uniko; em obras Haus e Azure; demais entregues.
- Marca: logos oficiais fornecidas e paleta verde/cinza do pedido.
- Fotos das galerias restritas às respectivas páginas. As quatro fotos do hero são exclusivas da home.
- Percentuais e localizações confirmadas em `content/project-updates.json`; `null` não é um percentual zero.
- Atualize os dados e execute `python3 build.py` antes de publicar.

## Deploy

Projeto Vercel existente: `kyma-website`, equipe `joshua-pedroso`.
O site é estático, com URLs limpas configuradas em `vercel.json`.

## Rodada 2 — novembro de 2026

[Conferência dos 26 itens e pendências](docs/RODADA-2-2026-11-11.md).
A evolução animada usa `progress_percent` e `progress_stages` em `content/project-updates.json`; campos ausentes ficam como `null`, sem números presumidos. As fontes das metragens estão em `content/area-sources.json`.
