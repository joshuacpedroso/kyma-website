#!/usr/bin/env python3
"""Real PHP session, file and Python-build integration, isolated in a temporary copy.
Run: PHP_BIN=php python3 tests/adm_integration.py (PHP >= 8.1, Python >= 3.8).
Never edits the working tree or authenticates to production.
"""
import copy, hashlib, http.cookiejar, json, os, shutil, socket, subprocess, tempfile, time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, build_opener, HTTPCookieProcessor
ROOT=Path(__file__).resolve().parents[1]
PASSWORD='integration-test-password-only'

def main():
 with tempfile.TemporaryDirectory(prefix='kyma-adm-test-') as tmp:
  root=Path(tmp)/'site'
  shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('.git','__pycache__','node_modules','backups','login-attempts.json','*.lock'))
  cfg_path=root/'private/admin-config.json';cfg=json.loads((cfg_path if cfg_path.exists() else root/'private/admin-config.example.json').read_text());salt='isolated-test-salt'
  cfg['password'].update(salt=salt,hash=hashlib.pbkdf2_hmac('sha256',PASSWORD.encode(),salt.encode(),210000).hex())
  cfg_path.write_text(json.dumps(cfg))
  router=Path(tmp)/'router.php';router.write_text('''<?php
$p=parse_url($_SERVER['REQUEST_URI'],PHP_URL_PATH);
if($p==='/adm'||$p==='/adm/') {require __DIR__.'/site/adm/index.php';return true;}
if(preg_match('#^/(private|server|tools|tests|content)(/|$)#',$p)){http_response_code(403);return true;}
if(!is_file(__DIR__.'/site'.$p)&&is_file(__DIR__.'/site'.$p.'.html')){readfile(__DIR__.'/site'.$p.'.html');return true;}
return false;
''')
  with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
  log=open(Path(tmp)/'server.log','w+')
  proc=subprocess.Popen([os.environ.get('PHP_BIN','php'),'-n','-d','session.save_path='+tmp,'-d','upload_max_filesize=8M','-d','post_max_size=12M','-S',f'127.0.0.1:{port}','-t',str(root),str(router)],stdout=log,stderr=log)
  base=f'http://127.0.0.1:{port}';jar=http.cookiejar.CookieJar();client=build_opener(HTTPCookieProcessor(jar));csrf=None
  def request(action,body=None,token=True,raw=None,content_type=None):
   headers={}
   if body is not None:raw=json.dumps(body).encode();headers['Content-Type']='application/json'
   if content_type:headers['Content-Type']=content_type
   if token and csrf:headers['X-CSRF-Token']=csrf
   req=Request(base+'/adm/api.php?action='+action,data=raw,headers=headers)
   try:response=client.open(req)
   except HTTPError as e:response=e
   return response.status,json.loads(response.read())
  def save(data,rev):return request('save',{'data':data,'revision':rev})
  def load():
   status,result=request('load');assert status==200,result;return result['data'],result['revision']
  try:
   for _ in range(50):
    try:request('status');break
    except OSError:time.sleep(.1)
   html=client.open(base+'/adm').read().decode();assert 'type="password"' in html and PASSWORD not in html
   assert request('load')[0]==401
   assert request('save',{})[0]==401
   assert request('upload',raw=b'')[0]==401
   assert request('login',{'password':'incorrect'})[0]==401
   status,result=request('login',{'password':PASSWORD});assert status==200 and result['authenticated'];csrf=result['csrf']
   status,result=request('save',{},token=False);assert status==403,(status,result)
   data,rev=load();original=copy.deepcopy(data)
   # Reject script HTML, path traversal and invalid percentages before writing.
   for change in ('xss','percent','slug'):
    bad=copy.deepcopy(data)
    if change=='xss':bad['site']['texts']['cta_text']='<img src=x onerror=alert(1)>'
    if change=='percent':bad['updates']['uniko']['progress_percent']=101
    if change=='slug':bad['projects'][0]['slug']='../escape'
    status,result=save(bad,rev);assert status==422,(change,status,result)
    assert load()[1]==rev
   print('PASS login, session, CSRF, HTML/path/percent validation')
   # Upload and use a real image; executable text must be rejected.
   def upload(blob,filename,mime):
    boundary='kyma-test-boundary';raw=(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\nContent-Type: {mime}\r\n\r\n'.encode()+blob+f'\r\n--{boundary}--\r\n'.encode())
    return request('upload',raw=raw,content_type='multipart/form-data; boundary='+boundary)
   assert upload(b'<?php echo "x";','evil.php','image/jpeg')[0]==422
   status,image=upload((root/'assets/img/hero/hero-1.jpg').read_bytes(),'photo.jpg','image/jpeg');assert status==200,image
   assert (root/image['url'].lstrip('/')).is_file()
   new=copy.deepcopy(data['projects'][0]);new.update(slug='teste-painel',name='Teste Painel',full='Teste Painel',featured_order=None,hero=[image['url'],image['width'],image['height']],presentation_override=True)
   data['projects'].append(new);data['updates']['teste-painel']={'progress_percent':45.5,'progress_stages':[{'name':'Estrutura','percent':70},{'name':'Acabamento','percent':None}],'coordinates':None};data['media']['teste-painel']=[]
   data['blog'].insert(0,{'id':'teste-noticia','title':'Notícia de teste','text':'Texto de teste salvo.','date':'2026-11-11','image':image['url'],'project_slug':'teste-painel'})
   data['site']['texts']['cta_text']='Contato editado pelo painel.'
   status,result=save(data,rev);assert status==200 and result.get('generated'),(status,result)
   page=(root/'teste-painel.html').read_text();assert 'Teste Painel' in page and 'data-progress="45.5"' in page and 'data-progress-target="70"' in page and image['url'] in page
   assert 'Notícia de teste' in (root/'blog.html').read_text()
   assert 'Contato editado pelo painel.' in (root/'index.html').read_text()
   assert save(data,rev)[0]==409
   print('PASS image upload, project/blog creation, real progress, JSON save and Python regeneration, stale-edit conflict')
   # Delete all projects (including special Haus details); the builder must handle empty maps.
   data,rev=load();data['projects']=[];data['updates']={};data['media']={};data['details']={};data['blog']=[]
   status,result=save(data,rev);assert status==200 and result.get('generated'),(status,result)
   assert not (root/'teste-painel.html').exists() and not (root/'haus.html').exists()
   assert json.loads((root/'content/project-details.json').read_text())=={}
   data,rev=load();status,result=save(original,rev);assert status==200 and result.get('generated'),result
   print('PASS project/blog deletion, orphan page cleanup, empty lists and restore')
   # Missing Python persists content and clearly requires a manual build.
   cfg['python_command']='/missing-kyma-python';cfg_path.write_text(json.dumps(cfg));data,rev=load();data['site']['texts']['cta_text']='Aguardando build manual.'
   status,result=save(data,rev);assert status==200 and result['generated'] is False,(status,result)
   assert load()[0]['site']['texts']['cta_text']=='Aguardando build manual.'
   cfg['python_command']='python3';cfg_path.write_text(json.dumps(cfg));data,rev=load();status,result=save(original,rev);assert status==200 and result.get('generated'),result
   # A failed build restores previous JSON bytes.
   (root/'build.py').write_text('raise RuntimeError("integration failure")')
   before_rev=load()[1];data['site']['texts']['cta_text']='Must roll back'
   status,result=save(data,before_rev);assert status==500,(status,result)
   assert load()[1]==before_rev
   print('PASS missing-Python manual fallback and rollback on build failure')
   status,result=request('password',{'password':'replacement-test-password'});assert status==200 and result['ok']
   assert request('load')[0]==401
   assert request('login',{'password':PASSWORD})[0]==401
   status,result=request('login',{'password':'replacement-test-password'});assert status==200;csrf=result['csrf']
   assert request('logout',{})[0]==200
   assert request('save',{})[0]==401
   print('PASS password change, old session invalidation, logout and write rejection')
  finally:
   proc.terminate();proc.wait(timeout=5);log.seek(0);server_log=log.read();log.close()
   assert 'PHP Fatal error' not in server_log,server_log[-2000:]
if __name__=='__main__':main()
