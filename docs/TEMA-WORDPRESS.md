# Tema WordPress Kyma, instalação automática

Base visual e de conteúdo: versão aprovada no commit `098e3d1efec34994fc0bfb6d40460269a0fa7933`, incluindo as rodadas 1 a 3, o complemento de fotos de Quem Somos, as duas humanizadas atribuídas ao Monte Zurich por instrução do Joshua e os percentuais demonstrativos.

## Instalar

1. No WordPress da hospedagem, abra **Aparência → Temas → Adicionar tema → Enviar tema**.
2. Envie **kyma-wordpress-1.1.0.zip** e clique em **Instalar agora**. Não envie o ZIP do repositório GitHub nem os ZIPs de fotos.
3. Clique em **Ativar**. A ativação é a etapa que troca a apresentação e executa a configuração automática. Apenas enviar o arquivo não troca o tema ativo no WordPress.

Não há importação XML separada, page builder obrigatório, plugin obrigatório do tema, comando Python, Node, Composer ou configuração de senha própria a executar na hospedagem.

Requisitos: WordPress 6.5 ou superior, PHP 8.1 ou superior e uma instalação WordPress com banco de dados e permissões normais de instalação de temas. O pacote tem aproximadamente 27 MB. Se o painel informar que o arquivo excede o limite, ajuste o limite de upload da hospedagem ou extraia a pasta `kyma` em `wp-content/themes/` por SFTP/gerenciador de arquivos e ative em Aparência → Temas.

## O que acontece ao ativar

- O tema passa a renderizar o site com o layout Kyma.
- Cria e publica 15 páginas: Início, Quem somos, Empreendimentos, Lançamentos, Blog, Contato e as páginas dos nove empreendimentos.
- Define Início como página inicial e cria o menu na ordem Quem somos, Empreendimentos, Blog, Contato.
- Cria as três notícias atuais como posts nativos do WordPress. A home e a página Blog leem os posts publicados; novas notícias entram pelo painel Posts.
- Preenche as páginas com as fotos, logos, ícones, textos e contatos aprovados. As mídias necessárias ficam dentro do tema, sem depender da pasta `/assets` da raiz do domínio antigo.
- Mantém o carrossel de quatro imagens, os filtros, lightbox, efeitos de entrada, contagem de evolução, barras em sequência, movimento reduzido, mapa com nove pins, concierge e formulário que encaminha a mensagem pelo WhatsApp.
- Aplica o tema tanto na raiz do domínio quanto em uma instalação WordPress em subpasta. Links e caminhos de mídia são ajustados ao endereço da instalação.
- Tenta limpar os caches nativos e dos plugins de cache reconhecidos. Se a hospedagem ou CDN ainda entregar o HTML anterior em cache, limpe o cache nesse serviço.

## Substituição do conteúdo anterior

A substituição é automática na ativação, sem apagar definitivamente o conteúdo antigo:

- Páginas e posts antigos publicados ou agendados passam a rascunho, exceto páginas que são reutilizadas por terem o mesmo endereço das novas páginas.
- Quando já existe uma página com um slug como `quem-somos` ou `contato`, seu ID é reutilizado. O título, conteúdo e configurações de layout anteriores são guardados antes da troca.
- Os dados e configurações anteriores são preservados numa opção privada do banco, sem acesso público por REST.
- Contas de usuários, senhas do WordPress, biblioteca de mídia e arquivos do tema antigo não são apagados. Plugins instalados não são desativados.
- Dados de outros tipos de conteúdo mantidos por plugins não são excluídos. As rotas conhecidas do novo site são direcionadas às novas páginas Kyma.
- Reativar o tema depois de uma instalação concluída não duplica as 15 páginas ou as notícias e não reinicializa seu conteúdo editado.

### Voltar ao site anterior

Enquanto o tema Kyma estiver ativo, abra **Kyma → Restaurar site anterior**, marque a confirmação e clique no botão. A ferramenta restaura o conteúdo e os metadados das páginas substituídas, os estados dos posts antigos, a configuração da página inicial e o tema anterior, se ele ainda estiver instalado. As páginas e notícias novas da Kyma ficam em rascunho, sem exclusão definitiva.

Apenas mudar de tema em Aparência não é equivalente a executar essa restauração: a ferramenta é que repõe as configurações e o conteúdo anteriores. A cópia interna não contém arquivos de plugins, uploads ou o banco inteiro; ela cobre as alterações de conteúdo e configuração feitas pela ativação do tema.

## Editar depois da instalação

### Cores, fontes, imagens, contatos e textos (versão 1.1.0)

- **Kyma → Cores, fontes e contatos** (ou Aparência → Personalizar → Kyma: aparência do site): as 9 cores da marca, trocadas no site inteiro (CSS, botões, barras, ícones e o tom do logo); as fontes dos títulos, dos textos e de destaque, com uma lista pronta ou qualquer nome do Google Fonts; o tamanho dos textos; telefone, WhatsApp, Instagram e endereço; e trocas de texto fixo, como no rodapé (`texto atual => texto novo`). Tudo aparece na prévia ao vivo e só vai ao ar ao clicar em Publicar.
- **Kyma → Imagens**: todas as fotos e logos do site, cada uma com Trocar (biblioteca de mídia) e Voltar ao original.
- **CSS adicional**: Aparência → Personalizar → CSS adicional, para ajustes livres.

- **Kyma:** atalhos para todas as páginas e para a restauração.
- **Páginas:** cada página já vem preenchida. O layout fiel usa blocos HTML personalizados, editáveis no WordPress; não depende de Elementor, de um construtor externo ou de geração Python. Alterações estruturais livres nesses blocos exigem cuidado com o HTML.
- **Posts:** criar, editar, excluir notícias e escolher imagem destacada. Novas notícias aparecem na home e no Blog. As notícias iniciais não exibem uma data editorial inventada, pois a fonte não informou essas datas.
- **Aparência → Menus:** editar o menu principal, compartilhado pelo desktop e celular.
- **Páginas → empreendimento → Evolução da obra:** editar o percentual geral e os nomes/percentuais das etapas pelos campos, sem editar HTML. Campo vazio significa “a informar”. Salvar/Atualizar a página publica os novos números e as animações usam os novos alvos.

### Percentuais desta entrega

Mon Trésor, Monte Cristo, Monte Negro, Monte Zurich, Altos do Parque e Serra do Sincorá começam com 100%, por instrução do Joshua para os Entregues. Haus 76%, Azure 45% e Uniko 10% são demonstrações, com cinco etapas ilustrativas, e continuam identificados no site.

Quando os oficiais chegarem, atualize o geral e todas as etapas confirmadas no quadro Evolução da obra e desmarque **Valores de demonstração**. Etapas não confirmadas devem ficar sem número ou ser removidas, sem manter um exemplo ilustrativo apresentado como medição real.

## Acesso administrativo

O WordPress usa seus usuários e senhas existentes. `/adm` encaminha para o painel Kyma protegido pelo login do WordPress. O tema não distribui uma senha compartilhada, não modifica a senha do administrador e não inclui o JSON privado de autenticação do pacote PHP anterior.

O backend standalone de `/adm` e o gerador Python não são instalados como backend paralelo. No WordPress, as páginas, notícias e campos de evolução são salvos no banco pelo próprio WordPress, com as permissões e os nonces da plataforma.

## Arquivos e serviços

- Todo CSS, JavaScript, fotos, logos, ícones SVG e fontes usados pelo tema estão no pacote. As fotos foram otimizadas sem recortar os enquadramentos. Plantas e humanizadas de detalhe mantêm seus arquivos de alta resolução.
- As fotos ficam no diretório do tema; elas não são duplicadas em massa na biblioteca de mídia durante a ativação. Para substituir uma imagem ou publicar notícia nova, pode-se usar normalmente a biblioteca de mídia do WordPress.
- O mapa continua usando tiles OpenStreetMap. Os mapas individuais do Google, o WhatsApp e a incorporação pública do Instagram continuam dependendo desses serviços e da conexão do visitante.
- A incorporação do Instagram permanece pública. O tema não inventa um feed autenticado nem inclui credenciais da conta.
- PHP do tema: `functions.php`, `inc/setup.php`, `inc/render.php`, `inc/content.php`, `inc/admin.php`, `index.php`, `404.php`.
- ZIP montado: inclui ainda `pages/`, `shells/`, `data/`, `assets/`, fontes/licenças e a miniatura do tema.

## Construir o ZIP novamente

Na cópia de desenvolvimento do repositório, com Python e Pillow disponíveis:

```sh
python3 tools/package-wordpress.py --output dist
```

Isso gera `dist/kyma-wordpress-1.1.0.zip` e o SHA-256 correspondente. A ferramenta parte das páginas estáticas aprovadas e dos JSONs atuais. Os arquivos gerados são preparados antes da instalação; não existe essa dependência na hospedagem WordPress.

O ZIP não inclui `wp-config.php`, bancos de teste, sessões de navegador, credenciais, `.env`, `private/admin-config.json` ou o backend standalone.

## Validação desta entrega

Ambiente isolado: WordPress 7.1.4 e PHP 8.4.27, usando o adaptador SQLite oficial de testes do WordPress Performance Team. Esse adaptador pertence somente ao ambiente de validação, não ao ZIP nem à hospedagem de destino; o tema usa as APIs normais do WordPress.

A raiz e uma instalação em subpasta foram verificadas no Chromium em desktop e celular. A contagem intermediária, o anel e as etapas em sequência foram verificados com animação normal e com movimento reduzido.

A validação inclui o upload pelo instalador nativo, a ativação sobre um site com conteúdo anterior, as 15 páginas, os três posts, o menu desktop/mobile, os quatro slides, os nove pins, as nove fotos únicas de Quem Somos, as humanizadas do Monte Zurich, os percentuais e as etapas. A integração verifica a reativação sem duplicatas, os dados antigos preservados, os campos de evolução com nonce e a edição nativa de posts/páginas. A ferramenta de restauração também é validada no ambiente isolado.
