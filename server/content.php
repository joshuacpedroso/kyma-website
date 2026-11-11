<?php
declare(strict_types=1);
function root_dir(): string { return dirname(__DIR__); }
function private_dir(): string { return getenv('KYMA_PRIVATE_DIR') ?: root_dir().'/private'; }
function config(): array { $file=private_dir().'/admin-config.json';if(!is_file($file))throw new RuntimeException('Configure o arquivo privado com tools/set-admin-password.php antes de entrar.');return json_decode(file_get_contents($file),true,512,JSON_THROW_ON_ERROR); }
function files_map(): array { return ['projects'=>'content/projects.json','updates'=>'content/project-updates.json','media'=>'assets/project-media.json','details'=>'content/project-details.json','site'=>'content/site.json','blog'=>'content/blog.json']; }
function snapshot(): array { $data=[];foreach(files_map() as $key=>$file) $data[$key]=json_decode(file_get_contents(root_dir().'/'.$file),true,512,JSON_THROW_ON_ERROR);return $data; }
function revision(): string { $bytes='';foreach(files_map() as $file)$bytes.=file_get_contents(root_dir().'/'.$file);return hash('sha256',$bytes); }
function atomic_write(string $file,string $text): void { $tmp=tempnam(dirname($file),'.kyma-');if($tmp===false || file_put_contents($tmp,$text,LOCK_EX)===false)throw new RuntimeException('Falha ao gravar dados.');chmod($tmp,0640);if(!rename($tmp,$file)){@unlink($tmp);throw new RuntimeException('Falha ao substituir arquivo.');} }
function encode_json($v): string { return json_encode($v, JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES|JSON_THROW_ON_ERROR)."\n"; }
function slug_ok($v): bool { return is_string($v) && preg_match('/^[a-z0-9]+(?:-[a-z0-9]+)*$/D',$v) && strlen($v)<=80; }
function image_url($v): bool { return is_string($v) && strlen($v)<2000 && !preg_match('/[<>"\x27\\\\\x00-\x20]/',$v) && (preg_match('#^/assets/[a-zA-Z0-9_./()%-]+$#D',$v) && !str_contains($v,'..') || filter_var($v,FILTER_VALIDATE_URL) && str_starts_with($v,'https://')); }
function percent_ok($v): bool { return $v===null || (is_int($v)||is_float($v)) && $v>=0 && $v<=100; }
function validate_tree($v,int $depth=0): void {
  if($depth>18)throw new InvalidArgumentException('Conteúdo muito profundo.');
  if(is_array($v)){foreach($v as $key=>$item){if(in_array((string)$key,['__proto__','prototype','constructor'],true))throw new InvalidArgumentException('Chave de conteúdo inválida.');validate_tree($item,$depth+1);}return;}
  if(is_string($v)){
    if((str_starts_with($v,'/')||preg_match('#^https?://#i',$v))&&preg_match('/[\x00-\x20\x22\x27<>]/',$v))throw new InvalidArgumentException('Caminho ou URL inválido.');
    if(strlen($v)>100000)throw new InvalidArgumentException('Texto muito longo.');
    $plain=preg_replace('#</?(?:em|strong|br|b|i)\s*/?>#i','',$v);
    if(preg_match('/[<>]/',$plain) || preg_match('/(?:javascript|data|vbscript)\s*:/i',$v))throw new InvalidArgumentException('HTML não permitido. Use somente texto ou em/strong/br sem atributos.');
  }
}
function validate_bundle(array $b): array {
  foreach(array_keys(files_map()) as $key)if(!isset($b[$key])||!is_array($b[$key]))throw new InvalidArgumentException('Seção ausente: '.$key);
  validate_tree($b);
  if(!array_is_list($b['projects'])||!array_is_list($b['blog']))throw new InvalidArgumentException('Lista de registros inválida.');
  if(count($b['projects'])>100 || count($b['blog'])>500)throw new InvalidArgumentException('Limite de registros excedido.');
  $ids=[];$orders=[];$reserved=['index','adm','api','blog','contato','empreendimentos','lancamentos','quem-somos','404'];
  foreach($b['projects'] as $p){
    if(!slug_ok($p['slug']??null)||in_array($p['slug'],$reserved,true)||isset($ids[$p['slug']]))throw new InvalidArgumentException('Endereço de empreendimento inválido ou repetido.');
    $id=$p['slug'];$ids[$id]=true;
    foreach(['name','full','location','pitch'] as $key)if(!isset($p[$key])||!is_string($p[$key])||trim($p[$key])==='')throw new InvalidArgumentException('Preencha '.$key.' em '.$id);
    if(!slug_ok($p['region']??null))throw new InvalidArgumentException('Use somente letras minúsculas, números e hífen na região.');
    if(!in_array($p['status']??'', ['lancamento','em-obras','entregue'],true))throw new InvalidArgumentException('Status inválido.');
    foreach(['card','hero','hero_logo','launch_card'] as $key)if(isset($p[$key])&&(!is_array($p[$key])||count($p[$key])!==3||!image_url($p[$key][0])||!is_numeric($p[$key][1])||!is_numeric($p[$key][2])||$p[$key][1]<=0||$p[$key][2]<=0))throw new InvalidArgumentException('Imagem inválida em '.$id);
    if(!isset($p['logo'])||count($p['logo'])!==2||!image_url($p['logo'][0])||!image_url($p['logo'][1]))throw new InvalidArgumentException('Logo inválida.');
    if(isset($p['wa_link']) && (!filter_var($p['wa_link'],FILTER_VALIDATE_URL)||!str_starts_with($p['wa_link'],'https://')))throw new InvalidArgumentException('Link de atendimento inválido.');
    $order=$p['featured_order']??null;if($order!==null){if(!is_int($order)||$order<1||$order>100||isset($orders[$order]))throw new InvalidArgumentException('Ordem dos destaques repetida ou inválida.');$orders[$order]=true;}
    $u=$b['updates'][$id]??null;if(!is_array($u)||!array_key_exists('progress_percent',$u)||!percent_ok($u['progress_percent']))throw new InvalidArgumentException('Percentual inválido em '.$id);
    if(isset($u['coordinates'])&&(!is_array($u['coordinates'])||count($u['coordinates'])!==2||!is_numeric($u['coordinates'][0])||!is_numeric($u['coordinates'][1])||abs($u['coordinates'][0])>90||abs($u['coordinates'][1])>180))throw new InvalidArgumentException('Coordenadas inválidas.');
    foreach($u['progress_stages']??[] as $stage)if(!is_string($stage['name']??null)||trim($stage['name'])===''||!array_key_exists('percent',$stage)||!percent_ok($stage['percent']))throw new InvalidArgumentException('Etapa inválida em '.$id);
    foreach($b['media'][$id]??[] as $photo)if(!image_url($photo['src']??null)||!is_numeric($photo['width']??null)||!is_numeric($photo['height']??null))throw new InvalidArgumentException('Galeria inválida.');
  }
  foreach(['updates','media','details'] as $key)foreach(array_keys($b[$key]) as $id)if(!isset($ids[$id]))unset($b[$key][$id]);
  $posts=[];foreach($b['blog'] as $post){if(!slug_ok($post['id']??null)||isset($posts[$post['id']])||!is_string($post['title']??null)||trim($post['title'])===''||!is_string($post['text']??null)||!image_url($post['image']??null)||!preg_match('/^(?:\d{4}-\d{2}-\d{2})?$/D',$post['date']??''))throw new InvalidArgumentException('Notícia inválida.');$posts[$post['id']]=true;}
  $site=$b['site'];foreach(['name','url','phone','phone_intl','whatsapp','instagram','address','maps_query','logo','favicon','navigation','hero','about','texts','cta_image'] as $key)if(!array_key_exists($key,$site))throw new InvalidArgumentException('Configuração do site incompleta.');
  if(!preg_match('/^[0-9+() .-]+$/D',$site['phone_intl'])||!preg_match('/^[0-9]{8,16}$/D',$site['whatsapp'])||!preg_match('/^[a-zA-Z0-9_.]+$/D',$site['instagram'])||!filter_var($site['url'],FILTER_VALIDATE_URL)||!str_starts_with($site['url'],'https://'))throw new InvalidArgumentException('Contato ou domínio inválido.');
  foreach(['logo','favicon'] as $key)if(!image_url($site[$key]))throw new InvalidArgumentException('Imagem institucional inválida.');
  foreach($site['hero']['slides'] as $slide)if(!image_url($slide[0]??null)||count($slide)!==4)throw new InvalidArgumentException('Imagem de hero inválida.');
  if(count($site['hero']['slides'])<1)throw new InvalidArgumentException('Mantenha pelo menos uma imagem no hero.');
  foreach($site['navigation'] as $nav)if(!preg_match('#^/[a-z0-9/-]*$#D',$nav[0]??''))throw new InvalidArgumentException('Link do menu inválido.');
  foreach([$site['about']['hero_image'],$site['about']['intro_image'],$site['about']['values_image'],$site['cta_image']] as $image)if(!image_url($image[0]??null))throw new InvalidArgumentException('Foto institucional inválida.');
  return $b;
}
function run_build(): array {
  if(!function_exists('proc_open'))return ['generated'=>false,'message'=>'Conteúdo salvo. Execute python3 build.py para publicar; a hospedagem não permite executar processos.'];
  $cfg=config();$command=$cfg['python_command']??'python3';
  if(!is_string($command)||!preg_match('#^[a-zA-Z0-9_./-]+$#D',$command))throw new RuntimeException('Comando Python inválido na configuração.');
  $pipes=[];$process=@proc_open([$command,root_dir().'/build.py'],[['pipe','r'],['pipe','w'],['pipe','w']],$pipes,root_dir());
  if(!is_resource($process))return ['generated'=>false,'message'=>'Conteúdo salvo. Python indisponível: execute o build.py manualmente.'];
  fclose($pipes[0]);$out=stream_get_contents($pipes[1]);$err=stream_get_contents($pipes[2]);fclose($pipes[1]);fclose($pipes[2]);$exit=proc_close($process);
  if($exit===127)return ['generated'=>false,'message'=>'Conteúdo salvo. Python não encontrado: execute o build.py manualmente.'];
  if($exit!==0)throw new RuntimeException('A regeneração falhou. Os dados anteriores foram restaurados. Confira o Python e os dados na hospedagem.');
  return ['generated'=>true,'message'=>'Conteúdo salvo e site regenerado.'];
}
