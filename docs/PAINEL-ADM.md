# Painel de edição da Kyma

## Acesso

Abra `/adm` no domínio do site. A primeira tela pede **somente a senha**, sem usuário. A senha inicial é a fornecida pelo Joshua para esta entrega; ela não aparece no HTML, JavaScript público ou nesta documentação.

Após entrar, use Empreendimentos, Blog, Textos do site ou Senha no menu. **Salvar alterações** publica todas as alterações da sessão; mudar de seção preserva o rascunho. **Recarregar** descarta o rascunho e traz os dados salvos. **Sair** encerra a sessão. Cada edição deve ser salva antes de fechar o navegador.

## Na Vercel: demonstração

Depois de configurar o JSON privado descrito abaixo, o login e o editor funcionam. O banner identifica o modo de demonstração. Salvar mostra que a gravação só estará ativa na hospedagem definitiva; nenhuma tentativa altera os JSONs, arquivos ou o site público. Upload fica desabilitado, mas é possível experimentar caminhos de imagens. Recarregar perde o rascunho. Trocar senha também não grava na demonstração.

A função Node `api/adm.js` lê a configuração da variável privada `KYMA_ADM_CONFIG` e valida o mesmo hash de senha usado pelo PHP e assina uma sessão de uma hora com `KYMA_ADM_SESSION_SECRET`. Essa variável privada está configurada na Vercel em produção e preview, com valores distintos. Para ativar o login do preview, é necessário cadastrar o JSON privado completo como variável sensível `KYMA_ADM_CONFIG`, em produção e preview, e fazer novo deploy. Até essa configuração ser autorizada, a tela de senha abre com a mensagem de configuração pendente; o backend não libera acesso ao conteúdo. Não coloque essas variáveis nos arquivos públicos. A função `api/blocked.js` e as regras de `vercel.json` bloqueiam acesso HTTP aos arquivos privados e de conteúdo. A implementação PHP é destinada à hospedagem definitiva; a Vercel não a executa. O build `node tools/prepare-vercel.cjs` gera `.vercel-public/` somente com HTMLs e assets públicos, sem PHP, JSONs editoriais ou configuração privada. Isso permite que as chamadas `/adm/api.php` cheguem à função Node em vez de servir o arquivo PHP como texto. Não é necessário enviar essa pasta gerada à hospedagem PHP.

## O que cada seção edita

- **Empreendimentos:** criar, editar ou excluir; nome, título completo, status, cidade/bairro/endereço, localização, metragem, dormitórios, região, descrições e link de atendimento. O endereço da página nasce do nome e permanece estável após a criação. Os nomes `adm`, `blog`, `contato`, entre outros usados pelo site, são reservados.
- **Destaques:** preencher a ordem 1, 2, 3… sem repetir. Vazio retira o empreendimento dos destaques. A ordem inicial permanece Uniko, Haus, Azure.
- **Fotos:** imagem do card, topo, logo e galeria, por caminho `/assets/...`, URL HTTPS ou upload de JPG, PNG, WebP ou GIF, até 8 MB. O upload usa nomes aleatórios e valida o conteúdo da imagem. SVG não é aceito por upload. Logos oficiais em SVG que já existem no acervo podem ser usadas pelo caminho. Remover uma foto da galeria retira a referência; não apaga o arquivo original compartilhado com outras páginas.
- **Evolução da obra:** percentual geral e etapas com nome e percentual. Campo vazio é `null` e exibe **A informar**. Preencher um número real de 0 a 100 ativa a contagem e o preenchimento animados já existentes. Zero é um valor real, não um substituto para dado desconhecido. Nenhum percentual foi inventado nesta entrega.
- **Localização:** endereço exato, latitude/longitude e fonte. Deixe coordenadas vazias quando não confirmadas.
- **Informações adicionais:** no Haus, o bloco expansível permite editar apresentação detalhada, características, lazer, plantas, imagens e chamadas específicas dessa página. Não é necessário editar Python.
- **Blog:** criar, editar e excluir notícias, com título, texto, imagem, data opcional e empreendimento relacionado. As primeiras três notícias aparecem na home; a página Blog mostra a lista completa. As notícias iniciais mantêm a data vazia porque não havia data editorial confirmada.
- **Textos do site:** hero e suas imagens/legendas, Quem Somos, imagens institucionais, Missão/Visão/Valores, títulos e subtítulos, frases de contato, rodapé, navegação, telefone, endereço e Instagram. As listas têm botões de adicionar/remover. Títulos aceitam apenas `em`, `strong`, `br`, `b` e `i`, sem atributos; os posts usam texto simples. URLs precisam ser HTTPS ou caminhos locais permitidos. Ícones, estrutura visual e textos funcionais de interface continuam no gerador.
- **Senha:** na hospedagem PHP, digite a nova senha duas vezes. A alteração grava o hash no arquivo de configuração e exige novo login. Use uma senha de pelo menos oito caracteres.

## Onde os dados ficam

| Arquivo | Conteúdo |
| --- | --- |
| `content/projects.json` | Cadastro, status, textos, fotos principais e ordem dos destaques |
| `content/project-updates.json` | Percentuais, etapas, endereços exatos e coordenadas |
| `assets/project-media.json` | Fotos e legendas das galerias |
| `content/project-details.json` | Conteúdo detalhado específico do Haus |
| `content/site.json` | Conteúdo institucional, contatos, hero, títulos e frases |
| `content/blog.json` | Notícias |
| `content/generated-pages.json` | Manifesto automático das páginas; permite remover páginas de empreendimentos excluídos |
| `private/admin-config.json` | Hash/salt da senha, duração da sessão, comando Python e limite de upload |

O backend usa uma lista fixa de arquivos graváveis. O navegador não escolhe caminhos arbitrários. Um identificador de revisão impede sobrescrever silenciosamente a edição salva por outra pessoa: se houver conflito, copie seu texto, recarregue e reaplique a alteração.

## Trocar a senha diretamente na configuração

`private/admin-config.json` contém `password.algorithm`, `iterations`, `salt` e `hash`. A senha é armazenada como **PBKDF2-SHA256 com salt e 210.000 iterações**, nunca em texto puro. Não substitua `hash` por uma senha legível.

Na primeira instalação a partir do GitHub, copie `private/admin-config.json` do pacote privado de migração, ou execute o utilitário abaixo para criar o arquivo a partir do modelo (use a senha inicial fornecida). Não deixe os campos de hash/salt do modelo vazios no arquivo real.

A forma mais simples é a seção Senha do painel na hospedagem PHP. Para recuperação sem login, abra o terminal da hospedagem, na raiz do site, e execute:

```sh
php tools/set-admin-password.php
```

O utilitário pede a nova senha e atualiza o mesmo JSON. Ele só funciona pela linha de comando. Se só houver acesso por SFTP, gere esse JSON numa cópia local com o utilitário e envie **apenas** o arquivo de configuração atualizado. Não substitua os JSONs editoriais de produção por cópias antigas. Após troca de senha via arquivo, as sessões anteriores são recusadas no próximo pedido. Na Vercel, atualize `KYMA_ADM_CONFIG` com o JSON privado completo e faça novo deploy; o arquivo real não é enviado ao GitHub.

## Subir na hospedagem definitiva

1. Use hospedagem com **PHP 8.1 ou superior**, sessões PHP funcionando e HTTPS. Python 3.8+ é necessário para regeneração automática, sem pacotes externos.
2. Use o pacote privado de migração entregue ou envie os arquivos do repositório com o JSON privado configurado separadamente, incluindo `adm/`, `server/`, `private/`, `content/`, `tools/`, `assets/`, `build.py`, páginas geradas e os arquivos ocultos `.htaccess` e `.user.ini`. Não envie backups antigos, arquivos de tentativas de login ou pastas `.git`. A pasta `api/` e `vercel.json` atendem somente ao preview da Vercel e podem ser omitidos na hospedagem PHP.
3. No Apache/LiteSpeed, habilite `mod_rewrite` e o uso de `.htaccess` (`AllowOverride`). A raiz resolve `/adm` pelo `adm/index.php`, e as páginas públicas sem extensão pelos HTMLs. Não use uma hospedagem apenas estática para esse modo.
4. Dê ao usuário do PHP permissão de escrita em `private/`, `content/`, `assets/uploads/`, `assets/` (para atualizar o JSON de mídia), `assets/js/` e nos arquivos/pasta raiz gerados pelo build (HTMLs e `sitemap.xml`). Use proprietário/grupo adequados; **não use chmod 777**. A gravação atômica exige permissão na pasta, além do arquivo.
5. Ajuste `python_command` no JSON privado: `python3` ou o caminho absoluto, por exemplo `/usr/bin/python3`. O PHP precisa permitir `proc_open`. Esse comando não é editável por requisições do navegador.
6. `adm/.user.ini` solicita upload de 8 MB, POST de 12 MB e erros fora da resposta pública. Confirme os limites efetivos no painel da hospedagem, pois alguns provedores aplicam valores próprios. Confirme também que o diretório de sessões PHP é gravável.
7. Verifique `/adm`, entre, altere um texto de teste, salve e confira **Conteúdo salvo e site regenerado**. Confirme a alteração no site e reverta o texto de teste. Teste Sair.
8. Confirme que `/private/admin-config.json`, `/server/content.php`, `/content/site.json` e `/tools/set-admin-password.php` retornam 403/404 por HTTP. Os `.htaccess` bloqueiam essas pastas e a execução de scripts em uploads. Faça esse teste antes de abrir o painel à equipe.

Se o servidor usa Nginx, `.htaccess` não tem efeito: a equipe de hospedagem deve reproduzir os bloqueios dessas pastas, de `build.py` e dos scripts em `assets/uploads/`, além das rotas sem extensão. Preferencialmente, mova `private/` para fora da raiz pública e configure a variável de ambiente PHP `KYMA_PRIVATE_DIR` com seu caminho absoluto. Inclua `admin-config.json` nessa pasta; backups e controle de tentativas serão gravados ali.

Cada salvamento PHP cria uma cópia dos JSONs anteriores em `private/backups/`, grava os novos arquivos e executa `build.py`. Em falha de build, restaura os JSONs anteriores e tenta regenerá-los. Mantenha backup externo dos arquivos e faça retenção periódica dos backups locais. Os uploads são arquivos locais e também precisam entrar no backup.

### Se não houver Python ou o PHP não puder executar processos

O painel salva os JSONs e informa que falta regenerar. **O site público continua exibindo a última versão dos HTMLs** até esse passo. Em um computador com Python, baixe os JSONs atualizados e os uploads da hospedagem para uma cópia completa do site e execute:

```sh
python3 build.py
```

Envie os HTMLs gerados, `assets/js/data.js`, `sitemap.xml` e `content/generated-pages.json` para a hospedagem. Se um empreendimento foi excluído, exclua também seu HTML antigo no servidor. O script faz essa remoção automaticamente quando executado diretamente na hospedagem. Nunca sobrescreva as edições mais recentes da equipe com JSONs antigos.

## Segurança e limites

O arquivo real `private/admin-config.json` é ignorado pelo Git: o repositório contém somente `private/admin-config.example.json`, sem hash ou senha real. O pacote privado de migração entregue separadamente inclui o JSON configurado. Não publique esse pacote nem a configuração em repositórios.

O PHP recusa gravação/upload/troca de senha sem sessão válida e token CSRF; o cookie é HttpOnly e SameSite Strict, com Secure em HTTPS. Há limite de tentativas de senha no backend PHP, expiração de sessão, validação de tipos, percentuais, imagens e caminhos, trava de gravação e detecção de edição simultânea. O painel usa uma senha compartilhada conforme solicitado; não há usuários individuais ou trilha de autoria. A demonstração usa sessão assinada e não tem capacidade de escrita.

O painel não inventa metragens, percentuais, endereços ou conteúdo editorial. O feed do Instagram permanece com a incorporação pública já existente; este painel não concede autorização à conta nem fornece um feed autenticado em tempo real. Textos funcionais, layout e código não são um editor visual de temas.

## Validação reproduzível

```sh
python3 build.py
node --check adm/admin.js
node --check api/adm.js
node tests/adm_demo.cjs
php -l adm/api.php
php -l server/content.php
PHP_BIN=php python3 tests/adm_integration.py
```

O teste de integração cria uma cópia temporária, usa uma senha de teste e inicia o servidor PHP local. Confere login, rejeição sem sessão/CSRF, upload válido/inválido, CRUD de projetos e notícias, percentuais reais, regeneração Python, limpeza de páginas excluídas, conflito de revisões, ausência de Python, restauração em falha, troca de senha e logout. Não altera o site real. O teste não substitui a conferência dos bloqueios `.htaccess` na hospedagem escolhida.
