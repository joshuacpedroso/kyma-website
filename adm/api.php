<?php
declare(strict_types=1);
require_once dirname(__DIR__).'/server/content.php';
ini_set('display_errors','0');
header('Content-Type: application/json; charset=utf-8');header('Cache-Control: no-store');header('X-Content-Type-Options: nosniff');
function answer(array $body,int $status=200): never { http_response_code($status);echo json_encode($body,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);exit; }
try {
  $cfg=config();$secure=!empty($_SERVER['HTTPS'])&&$_SERVER['HTTPS']!=='off';
  session_name('kyma_adm');session_set_cookie_params(['lifetime'=>0,'path'=>'/','secure'=>$secure,'httponly'=>true,'samesite'=>'Strict']);ini_set('session.use_strict_mode','1');if(!session_start())throw new RuntimeException('A hospedagem não conseguiu iniciar a sessão PHP. Confira o diretório de sessões.');
  $action=$_GET['action']??'status';$post=$_SERVER['REQUEST_METHOD']==='POST';$input=$post && $action!=='upload'?json_decode(file_get_contents('php://input'),true,512,JSON_THROW_ON_ERROR):[];
  $version=hash('sha256',$cfg['password']['hash']);
  $valid=($_SESSION['authenticated']??false)&&($_SESSION['version']??'')===$version&&($_SESSION['expires']??0)>time();
  if($action==='login'){
    if(!$post)answer(['ok'=>false,'message'=>'Método inválido.'],405);
    $ip=hash('sha256',$_SERVER['REMOTE_ADDR']??'local');$file=private_dir().'/login-attempts.json';$lock=fopen(private_dir().'/.login.lock','c');flock($lock,LOCK_EX);
    $attempts=is_file($file)?json_decode(file_get_contents($file),true):[];$row=$attempts[$ip]??['count'=>0,'until'=>time()+600];if($row['until']<time())$row=['count'=>0,'until'=>time()+600];
    if($row['count']>=8){flock($lock,LOCK_UN);answer(['ok'=>false,'message'=>'Aguarde alguns minutos antes de tentar novamente.'],429);}
    $password=$input['password']??'';$p=$cfg['password'];$hash=is_string($password)&&strlen($password)<=256?hash_pbkdf2('sha256',$password,$p['salt'],$p['iterations'],64,false):'';
    if(!hash_equals($p['hash'],$hash)){$row['count']++;$attempts[$ip]=$row;atomic_write($file,encode_json(array_filter($attempts,fn($v)=>$v['until']>=time())));flock($lock,LOCK_UN);answer(['ok'=>false,'message'=>'Senha incorreta.'],401);}
    unset($attempts[$ip]);atomic_write($file,encode_json($attempts));flock($lock,LOCK_UN);session_regenerate_id(true);$_SESSION=['authenticated'=>true,'version'=>$version,'expires'=>time()+$cfg['session_ttl'],'csrf'=>bin2hex(random_bytes(32))];$valid=true;
  }
  if($action==='status'||$action==='login')answer(['ok'=>true,'authenticated'=>$valid,'demo'=>false,'csrf'=>$valid?$_SESSION['csrf']:null]);
  if(!$valid)answer(['ok'=>false,'message'=>'Entre com a senha para continuar.'],401);
  $_SESSION['expires']=time()+$cfg['session_ttl'];
  if($post && !hash_equals($_SESSION['csrf'],$_SERVER['HTTP_X_CSRF_TOKEN']??''))answer(['ok'=>false,'message'=>'Sessão inválida. Atualize a página.'],403);
  if($action==='logout'&&$post){$_SESSION=[];session_destroy();setcookie(session_name(),'', ['expires'=>1,'path'=>'/','secure'=>$secure,'httponly'=>true,'samesite'=>'Strict']);answer(['ok'=>true]);}
  if($action==='load'&&!$post){$lock=fopen(private_dir().'/.edit.lock','c');flock($lock,LOCK_SH);$data=snapshot();$rev=revision();flock($lock,LOCK_UN);answer(['ok'=>true,'data'=>$data,'revision'=>$rev,'demo'=>false]);}
  if($action==='upload'&&$post){
    $f=$_FILES['file']??null;if(!$f||$f['error']!==UPLOAD_ERR_OK||$f['size']>$cfg['uploads_max_bytes'])answer(['ok'=>false,'message'=>'Envie uma imagem de até 8 MB.'],422);
    $info=@getimagesize($f['tmp_name']);$types=[IMAGETYPE_JPEG=>'jpg',IMAGETYPE_PNG=>'png',IMAGETYPE_GIF=>'gif',IMAGETYPE_WEBP=>'webp'];
    if(!$info||!isset($types[$info[2]])||$info[0]>12000||$info[1]>12000)answer(['ok'=>false,'message'=>'Formato de imagem inválido. Use JPG, PNG, WebP ou GIF.'],422);
    $dir=root_dir().'/assets/uploads';if(!is_dir($dir))mkdir($dir,0755,true);$name=bin2hex(random_bytes(16)).'.'.$types[$info[2]];
    if(!move_uploaded_file($f['tmp_name'],$dir.'/'.$name))throw new RuntimeException('Não foi possível salvar a imagem.');chmod($dir.'/'.$name,0644);answer(['ok'=>true,'url'=>'/assets/uploads/'.$name,'width'=>$info[0],'height'=>$info[1]]);
  }
  if($action==='password'&&$post){
    $password=$input['password']??'';if(!is_string($password)||strlen($password)<8||strlen($password)>256)answer(['ok'=>false,'message'=>'Use uma senha entre 8 e 256 caracteres.'],422);
    $salt=bin2hex(random_bytes(16));$cfg['password']=['algorithm'=>'pbkdf2-sha256','iterations'=>210000,'salt'=>$salt,'hash'=>hash_pbkdf2('sha256',$password,$salt,210000,64,false)];atomic_write(private_dir().'/admin-config.json',encode_json($cfg));$_SESSION=[];session_destroy();answer(['ok'=>true,'message'=>'Senha alterada. Entre novamente.']);
  }
  if($action==='save'&&$post){
    $bundle=validate_bundle($input['data']??[]);$lock=fopen(private_dir().'/.edit.lock','c');flock($lock,LOCK_EX);
    if(!hash_equals(revision(),$input['revision']??''))answer(['ok'=>false,'message'=>'O conteúdo mudou em outra sessão. Recarregue antes de salvar.'],409);
    $before=[];foreach(files_map() as $key=>$file)$before[$file]=file_get_contents(root_dir().'/'.$file);
    $backup=private_dir().'/backups';if(!is_dir($backup))mkdir($backup,0700,true);atomic_write($backup.'/'.date('Ymd-His').'-'.bin2hex(random_bytes(3)).'.json',encode_json($before));
    try {foreach(files_map() as $key=>$file)atomic_write(root_dir().'/'.$file,encode_json(in_array($key,['updates','media','details'],true)?(object)$bundle[$key]:$bundle[$key]));$result=run_build();}
    catch(Throwable $e){foreach($before as $file=>$text)atomic_write(root_dir().'/'.$file,$text);try{run_build();}catch(Throwable $ignored){}throw $e;}
    flock($lock,LOCK_UN);answer(['ok'=>true,'revision'=>revision()]+$result);
  }
  answer(['ok'=>false,'message'=>'Ação inválida.'],405);
}catch(InvalidArgumentException|JsonException $e){answer(['ok'=>false,'message'=>$e->getMessage()],422);}catch(Throwable $e){answer(['ok'=>false,'message'=>$e instanceof RuntimeException?$e->getMessage():'Falha no painel. Confira a configuração e as permissões da hospedagem.'],500);}
