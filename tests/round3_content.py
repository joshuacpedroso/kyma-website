"""Regression checks for the approved 16/11/2026 content and pending-media rules."""
import json
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
load=lambda path:json.loads((ROOT/path).read_text())
class Page(HTMLParser):
 def __init__(self,text):super().__init__();self.text=[];self.images=[];self.skip=0;self.feed(text)
 def handle_starttag(self,tag,attrs):
  if tag in ['script','style']:self.skip+=1
  if tag=='img':self.images.append(dict(attrs).get('src'))
 def handle_endtag(self,tag):
  if tag in ['script','style']:self.skip-=1
 def handle_data(self,text):
  if not self.skip:self.text.append(text)
projects=load('content/projects.json');updates=load('content/project-updates.json');sources=load('content/address-sources.json');site=load('content/site.json');media=load('assets/project-media.json');details=load('content/project-details.json')
assert len(projects)==len(sources)==9
numbers={'uniko':'162','haus':'286','mon-tresor':'65','azure':'60','monte-cristo':'661','monte-negro':'155','monte-zurich':'346','altos-do-parque':'686','serra-do-sincora':'130'}
for p in projects:
 slug=p['slug'];u=updates[slug];s=sources[slug]
 assert u['exact_address']==p['street']==s['official_address']
 assert numbers[slug]==s['house_number'] and numbers[slug] in p['street']
 assert u['coordinates']==s['coordinates'] and len(u['coordinates'])==2
 assert -24<u['coordinates'][0]<-23 and -46<u['coordinates'][1]<-45
 assert s['address_type'] in ['PointAddress','StreetAddress'] and s['score']>=98
 assert u['progress_percent'] is None and u['progress_stages']==[]
 assert p['status']==('lancamento' if slug=='uniko' else 'em-obras' if slug in ['haus','azure'] else 'entregue')
 assert p['street'] in ''.join(Page((ROOT/(slug+'.html')).read_text()).text)
assert [p['slug'] for p in sorted((p for p in projects if p['featured_order']),key=lambda p:p['featured_order'])]==['uniko','haus','azure']
expected='Kyma empreendimentos - Somos uma empresa da Indústria da Construção Civil que atua regionalmente no Vale do Paraíba e Litoral Norte no Estado de São Paulo. Oferecemos empreendimentos atuais, que primam pela qualidade, localização e que tragam o retorno esperado aos nossos clientes. Sempre em busca da satisfação dos nossos investidores, parceiros, fornecedores ou consumidores finais, proporcionando uma experiência única no mercado!'
assert site['about']['intro_text']==expected
assert expected in ''.join(Page((ROOT/'quem-somos.html').read_text()).text)
assert expected in (ROOT/'index.html').read_text() # Organization structured data uses the same canonical copy.
office='/assets/img/round3/quem-somos/'
assert site['about']['intro_image'][0]==office+'01-equipe-trabalhando.jpg'
assert site['about']['values_image'][0]==office+'02-sala-reuniao.jpg'
about_images=[url for url in Page((ROOT/'quem-somos.html').read_text()).images if url and url.startswith(office)]
assert len(about_images)==len(set(about_images))==9
assert [Path(url).name[:2] for url in about_images]==[f'{i:02}' for i in range(1,10)]
assert len(site['about']['office_gallery'])==7
humans=[p for p in media['monte-zurich'] if 'humanizada-apto-' in p['src']]
assert len(humans)==2 and all(p['contain'] and 'Joshua' in p['assignment_basis'] for p in humans)
assert all(p['src'] in (ROOT/'monte-zurich.html').read_text() for p in humans)
assert all('humanizada-apto-' not in (ROOT/(p['slug']+'.html')).read_text() for p in projects if p['slug']!='monte-zurich')
zurich=next(p for p in projects if p['slug']=='monte-zurich')
assert zurich['card'][0]=='/assets/img/2022/05/capa-zurich-1024x576.png'
assert zurich['hero'][0]=='/assets/img/2022/05/capa-zurich.png'
for name in load('content/generated-pages.json'):
 raw=(ROOT/name).read_text();page=Page(raw)
 assert '—' not in raw and '–' not in raw,name
 for phrase in ['Localização exata a confirmar','endereço exato a confirmar','Pin a confirmar']:assert phrase not in raw,name
 assert '/round3/pendentes/' not in raw,name
 assert all((ROOT/path.lstrip('/')).is_file() for path in page.images if path and path.startswith('/assets/')),name
for f in ['content/projects.json','content/site.json','content/project-details.json','assets/js/main.js','assets/js/chat.js','assets/js/data.js']:
 assert '—' not in (ROOT/f).read_text(),f
assert len([p for p in media['altos-do-parque'] if '/round3/' in p['src']])==12
assert len(details['monte-zurich']['plans'])==5
assert not any('/pendentes/' in p['published'] for p in load('content/round3-media-sources.json'))
assert len([p for p in load('content/round3-media-sources.json') if p.get('assignment_basis') and p.get('project_slug')=='monte-zurich'])==2
for slug in ['mon-tresor','altos-do-parque','serra-do-sincora']:
 p=next(p for p in projects if p['slug']==slug);assert '/round3/' in p['card'][0] and p['hero']==p['card'] and not p['contain']
print('PASS 9 official addresses/pins, source quality, copy, media assignments, no dashes, 9 unique office photos, Joshua-assigned humanized images, statuses and unknown percentages')
