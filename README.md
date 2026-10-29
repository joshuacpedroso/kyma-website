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

## Conteúdo pendente

- Uniko: substituir a identificação tipográfica provisória pelos materiais oficiais e informar endereço, plantas e imagens.
- Haus e Azure: informar `progress` (0–100) em cada registro de `PROJECTS`; enquanto ausente, a página orienta a consultar a equipe. Entregues exibem 100%.
- Mapas usam os endereços disponíveis, com seleção de empreendimento. Azure indica o bairro Tabatinga; ainda falta o endereço exato. Uniko não recebe um pin fictício.
- Instagram usa incorporação pública oficial do perfil, com link alternativo. O carregamento depende da Meta e das configurações públicas do perfil; um feed por API requer integração autenticada.
- As opções de ajuda encaminham o assunto ao formulário e ao WhatsApp da Kyma. Não há URLs fornecidas de portais, e-mail ou canais específicos para cada departamento.

## Imagens

As imagens existentes foram copiadas sem alterações do WordPress para `assets/img`, preservando ano, mês e nome. O site não depende mais desse servidor para carregar fotos e logos. O logo Azure usa composição CSS para ocultar o fundo branco e segue o efeito luminoso dos demais logos.

## Validação e deploy

Rode `python3 build.py` após editar o conteúdo. O gerador atualiza HTML, sitemap e dados do chat, e versiona os assets para evitar cache desatualizado.

O `vercel.json` mantém URLs limpas e redirecionamentos. O projeto Vercel existente é `kyma-website`, da equipe `joshua-pedroso`.
