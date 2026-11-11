<?php
if(PHP_SAPI!=='cli'){http_response_code(404);exit;}
require_once dirname(__DIR__).'/server/content.php';
fwrite(STDOUT,"Nova senha (não será gravada em texto puro): ");
if(function_exists('shell_exec'))@shell_exec('stty -echo');
$password=trim(fgets(STDIN));
if(function_exists('shell_exec'))@shell_exec('stty echo');
fwrite(STDOUT,"\n");
if(strlen($password)<8){fwrite(STDERR,"Use pelo menos oito caracteres.\n");exit(1);}
$file=private_dir().'/admin-config.json';
$config=is_file($file)?config():json_decode(file_get_contents(dirname(__DIR__).'/private/admin-config.example.json'),true,512,JSON_THROW_ON_ERROR);$salt=bin2hex(random_bytes(16));
$config['password']=['algorithm'=>'pbkdf2-sha256','iterations'=>210000,'salt'=>$salt,'hash'=>hash_pbkdf2('sha256',$password,$salt,210000,64,false)];
atomic_write(private_dir().'/admin-config.json',encode_json($config));
fwrite(STDOUT,"Senha atualizada no arquivo privado.\n");
