#!/usr/bin/env python3
"""Build a self-contained installable WordPress theme from the approved static site.
This is a packaging tool only. Python is not needed on the destination WP server.
"""
import argparse,hashlib,json,re,shutil,zipfile
from PIL import Image,ImageOps
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Doc(HTMLParser):
 def __init__(self,text):
  super().__init__();self.title='';self.in_title=False;self.description='';self.feed(text)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='title':self.in_title=True
  if tag=='meta' and a.get('name')=='description':self.description=a.get('content','')
 def handle_endtag(self,tag):
  if tag=='title':self.in_title=False
 def handle_data(self,text):
  if self.in_title:self.title+=text

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',default=str(ROOT/'dist'));parser.add_argument('--fonts',default=str(ROOT/'wordpress/kyma/fonts'),help='Directory containing the bundled open-license font assets');args=parser.parse_args()
 output=Path(args.output).resolve();theme=output/'kyma'
 if theme.exists():shutil.rmtree(theme)
 shutil.copytree(ROOT/'wordpress/kyma',theme,ignore=shutil.ignore_patterns('fonts'))
 for name in ['pages','shells','data']:(theme/name).mkdir(exist_ok=True)
 manifest={};project_names={p['slug']:p['name'] for p in json.loads((ROOT/'content/projects.json').read_text())}
 titles={'inicio':'Início','quem-somos':'Quem somos','empreendimentos':'Empreendimentos','lancamentos':'Lançamentos','blog':'Blog','contato':'Contato'}|project_names
 originals=[]
 for name in json.loads((ROOT/'content/generated-pages.json').read_text()):
  key='inicio' if name=='index.html' else name.removesuffix('.html');html=(ROOT/name).read_text();originals.append(html);meta=Doc(html)
  match=re.search(r'(<main id="conteudo">)(.*?)(</main>)',html,re.S);assert match,name
  body=match[2].strip()
  if key=='inicio':body=re.sub(r'<section class="section theme-ink2 news-highlights">.*?</section>','[kyma_news_highlights]',body,flags=re.S)
  if key=='blog':
   end=body.index('</section>')+len('</section>');body=body[:end]+'\n[kyma_news_archive]'
  if key in project_names:
   body=re.sub(r'<section class="section theme-ink2 build-progress".*?</section>',f'[kyma_progress project="{key}"]',body,flags=re.S)
  shell=html[:match.start(2)]+'\n<!-- KYMA_CONTENT -->\n'+html[match.end(2):]
  shell=re.sub(r'<link[^>]+href="(?:https://fonts\.(?:googleapis|gstatic)\.com|/assets/(?:css|vendor)).*?>\s*','',shell)
  shell=re.sub(r'<script src="/assets/.*?</script>\s*','',shell)
  (theme/'pages'/f'{key}.html').write_text(body+'\n')
  (theme/'shells'/f'{key}.html').write_text(shell)
  if key!='404':manifest[key]={'slug':key,'title':titles.get(key,key),'seo_title':meta.title,'description':meta.description}
 (theme/'data/pages.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 for name in ['site','projects','project-updates','blog']:
  shutil.copyfile(ROOT/'content'/f'{name}.json',theme/'data'/f'{name}.json')
 # Include every media file reachable from the rendered pages and editable seed data.
 paths=set()
 def find(text):
  for raw in re.findall(r"/assets/[^\s\"'<>?#]+",text):
   raw=unescape(raw).rstrip(');,')
   candidate=ROOT/raw.lstrip('/')
   if candidate.is_file():paths.add(candidate)
 for text in originals:find(text)
 for file in (ROOT/'content').glob('*.json'):find(file.read_text())
 for file in [ROOT/'assets/project-media.json',ROOT/'assets/css/style.css',ROOT/'assets/js/main.js',ROOT/'assets/js/chat.js',ROOT/'assets/js/data.js']:find(file.read_text());paths.add(file)
 for file in (ROOT/'assets/vendor').rglob('*'):
  if file.is_file():paths.add(file)
 for file in (ROOT/'assets/fonts').glob('*'):
  if file.is_file():paths.add(file)
 paths.discard(ROOT/'assets/project-media.json')
 preserve=set()
 details=json.loads((ROOT/'content/project-details.json').read_text())
 for detail in details.values():
  for plan in detail.get('plans',[]):
   if 'planta' in plan[4].lower():preserve.update(plan[:2])
 for photos in json.loads((ROOT/'assets/project-media.json').read_text()).values():
  for photo in photos:
   if any(word in photo['caption'].lower() for word in ['planta','humanizada']):preserve.add(photo['src'])
 replacements={}
 for source in sorted(paths):
  relative=source.relative_to(ROOT);target=theme/relative;target.parent.mkdir(parents=True,exist_ok=True)
  optimize=source.suffix.lower() in ['.jpg','.jpeg','.png','.webp'] and '/brand/' not in str(source) and '/'+str(relative) not in preserve
  if optimize:
   with Image.open(source) as image:
    optimize=max(image.size)>600
    if optimize:
     image=ImageOps.exif_transpose(image);image.thumbnail((1920,1920),Image.Resampling.LANCZOS)
     target=target.with_suffix('.webp');image.convert('RGB').save(target,'WEBP',quality=86,method=6)
     if target.stat().st_size<source.stat().st_size:
      replacements['/'+str(relative)]='/'+str(target.relative_to(theme))
     else:
      if target!=theme/relative:target.unlink()
      shutil.copyfile(source,theme/relative)
  if not optimize:shutil.copyfile(source,target)
 for file in theme.rglob('*'):
  if file.is_file() and file.suffix in ['.html','.css','.js','.json','.php']:
   text=file.read_text()
   for old,new in replacements.items():text=text.replace(old,new)
   file.write_text(text)
 css=theme/'assets/css/style.css';css.write_text(css.read_text().replace('/assets/fonts/','../fonts/'))
 # Keep all JS behavior; only the WordPress-specific URL/data adapter is appended.
 data=theme/'assets/js/data.js';data.write_text(data.read_text()+'''\n(function(){const config=window.KYMA_WORDPRESS;if(!config||!window.KYMA)return;window.KYMA.projects=window.KYMA.projects.map(p=>Object.assign(p,config.projects[p.slug]||{}));})();\n''')
 fonts=Path(args.fonts)
 for file in fonts.iterdir():
  if file.is_file():shutil.copyfile(file,theme/'assets/fonts'/file.name)
 (theme/'assets/css/wordpress.css').write_text('''/* Integration with native WordPress. */
body.admin-bar .site-header{top:32px}body.admin-bar .progress{top:32px}
.kyma-entry-content p{font-size:clamp(17px,1.4vw,20px);line-height:1.75;color:var(--text-secondary)}
.kyma-entry-content>*+*{margin-top:18px}.kyma-entry-content a{color:var(--brand-deep);text-decoration:underline}
.kyma-pagination{padding-bottom:70px}.kyma-pagination ul{display:flex;gap:14px;flex-wrap:wrap}
@media(max-width:782px){body.admin-bar .site-header{top:46px}body.admin-bar .progress{top:46px}}
''')
 # No admin password, wp-config, database or deployment environment enters the package.
 forbidden=['admin-config.json','wp-config.php','.env','db.php','build.py']
 for file in theme.rglob('*'):
  if file.is_file() and file.name in forbidden:raise RuntimeError('Private/build file in package: '+str(file))
 (theme/'docs').mkdir(exist_ok=True)
 for name in ['TEMA-WORDPRESS.md','RODADA-3-2026-11-16.md']:shutil.copyfile(ROOT/'docs'/name,theme/'docs'/name)
 archive=output/'kyma-wordpress-1.0.0.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for file in sorted(theme.rglob('*')):
   if file.is_file():z.write(file,'kyma/'+str(file.relative_to(theme)))
 sha=hashlib.sha256(archive.read_bytes()).hexdigest();(output/'kyma-wordpress-1.0.0.sha256').write_text(sha+'  '+archive.name+'\n')
 print(json.dumps({'zip':str(archive),'bytes':archive.stat().st_size,'pages':len(manifest),'news':len(json.loads((theme/'data/blog.json').read_text())),'assets':len(paths),'sha256':sha},ensure_ascii=False))
if __name__=='__main__':main()
