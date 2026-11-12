(() => {
  'use strict';
  const $=s=>document.querySelector(s);
  const state={data:null,revision:null,csrf:null,demo:true,dirty:false,tab:'projects',project:0,post:0};
  const labels={name:'Nome',full:'Nome completo',location:'Localização',region:'Região',city:'Cidade',hood:'Bairro',street:'Endereço',area:'Metragem',beds:'Dormitórios',pitch:'Descrição',featured_text:'Texto nos destaques',additional_description:'Descrição adicional',phone:'Telefone',phone_intl:'Telefone para ligação',whatsapp:'WhatsApp (somente números)',instagram:'Perfil do Instagram',address:'Endereço institucional',maps_query:'Endereço para busca no mapa',url:'Domínio do site',logo:'Logo oficial',favicon:'Ícone do site',navigation:'Menu',line:'Primeira parte da frase',emphasis:'Parte em itálico',hero:'Hero',about:'Quem Somos',values:'Visão, Missão e Valores',intro_text:'Texto institucional',hero_image:'Foto do topo',intro_image:'Foto da apresentação',values_image:'Foto de valores',texts:'Títulos e frases',cta_image:'Imagem de contato',about_intro_heading:'Título da apresentação',about_values_heading:'Título dos valores',about_values_intro:'Texto dos valores',about_title:'Título de Quem Somos',about_subtitle:'Subtítulo de Quem Somos',home_featured_heading:'Título dos destaques',home_featured_eyebrow:'Chamada dos destaques',addresses_heading:'Título de endereços',addresses_subtitle:'Subtítulo de endereços',portfolio_heading:'Título do portfólio',footer_heading:'Frase do rodapé',footer_summary:'Texto do rodapé',cta_title:'Título de contato',cta_text:'Frase de contato',listing_heading:'Título de Empreendimentos',listing_subtitle:'Subtítulo de Empreendimentos',launch_heading:'Título de lançamentos',launch_subtitle:'Subtítulo de lançamentos',contact_heading:'Título de Contato',contact_subtitle:'Subtítulo de Contato',news_heading:'Título de notícias',hero_title:'Título do topo',intro_heading:'Título de apresentação',intro_image:'Foto da apresentação',specs:'Características',private_heading:'Título de áreas privativas',common_heading:'Título de lazer',common_intro:'Texto de lazer ({count} = quantidade de espaços)',plans_heading:'Título das plantas',gallery_heading:'Título da galeria',location_heading:'Título da localização',location_description:'Texto da localização',private:'Áreas privativas',common:'Áreas comuns',blocks:'Blocos de informações',plans:'Plantas',feats:'Diferenciais',eyebrow:'Chamada',title:'Título',img:'Imagem'};
  const el=(tag,text,cls)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e;};
  function notice(message,error=false){$('#notice').textContent=message;$('#notice').classList.toggle('error',error);}
  function dirty(){state.dirty=true;$('#save').textContent='Salvar alterações •';}
  async function api(action,{method='GET',body,file}={}){
    const headers={};if(method==='POST')headers['X-CSRF-Token']=state.csrf||'';
    let payload;if(file){payload=new FormData();payload.append('file',file);}else if(body){headers['Content-Type']='application/json';payload=JSON.stringify(body);}
    const response=await fetch('/adm/api.php?action='+encodeURIComponent(action),{method,headers,body:payload,credentials:'same-origin',cache:'no-store'});
    const data=await response.json();if(response.status===401&&action!=='login'){showLogin();throw new Error(data.message);}
    if(!response.ok)throw new Error(data.message||'Não foi possível concluir.');return data;
  }
  function showLogin(){state.data=null;state.csrf=null;state.dirty=false;$('#editor-view').hidden=true;$('#login-view').hidden=false;$('#password').value='';$('#password').focus();}
  async function load(){const result=await api('load');state.data=result.data;state.revision=result.revision;state.dirty=false;state.demo=result.demo;$('#save').textContent='Salvar alterações';$('#login-view').hidden=true;$('#editor-view').hidden=false;$('#mode-banner').hidden=!state.demo;$('#mode-banner').textContent='Modo demonstração: explore e edite os campos. A gravação e os uploads ficam ativos na hospedagem definitiva; recarregar descarta as alterações locais.';render();}
  let fieldId=0;
  function field(parent,label,value,set,{type='text',wide=false,help='',disabled=false}={}){
    const wrap=el('div',undefined,'field'+(wide?' full':''));const caption=el('label',label);const input=el(type==='textarea'?'textarea':'input');input.id='field-'+(++fieldId);caption.htmlFor=input.id;wrap.append(caption);if(type!=='textarea')input.type=type;if(type==='number')input.step='any';input.value=value??'';input.disabled=disabled;input.addEventListener('input',()=>{set(type==='number'?(input.value===''?null:Number(input.value)):input.value);dirty();});wrap.append(input);if(help){const hint=el('small',help,'hint');hint.id=input.id+'-hint';input.setAttribute('aria-describedby',hint.id);wrap.append(hint);}parent.append(wrap);return input;
  }
  function select(parent,label,value,choices,set){const wrap=el('label',label),input=el('select');for(const [key,text]of choices){const option=el('option',text);option.value=key;input.append(option);}input.value=value;input.addEventListener('change',()=>{set(input.value);dirty();});wrap.append(input);parent.append(wrap);}
  function button(parent,text,fn,cls='secondary small'){const b=el('button',text,cls);b.type='button';b.addEventListener('click',fn);parent.append(b);return b;}
  function photo(parent,label,value,set){
    const box=el('div',undefined,'photo-editor full');box.append(el('h3',label));const image=el('img');image.alt=label;if(value)image.src=value;box.append(image);
    field(box,'Caminho ou URL HTTPS',value,v=>{set(v);image.src=v;});
    const upload=el('input');upload.type='file';upload.accept='image/jpeg,image/png,image/webp,image/gif';upload.disabled=state.demo;
    upload.addEventListener('change',async()=>{const file=upload.files[0];if(!file)return;try{const r=await api('upload',{method:'POST',file});if(!r.ok)return notice(r.message);set(r.url,r.width,r.height);dirty();render();notice('Imagem enviada. Salve as alterações para publicá-la.');}catch(e){notice(e.message,true);}});
    box.append(upload,el('small',state.demo?'Upload disponível na hospedagem definitiva. Você pode testar a edição do caminho.':'JPG, PNG, WebP ou GIF · até 8 MB.'));parent.append(box);
  }
  function generic(parent,value,set,label){
    if(value===null||typeof value!=='object'){field(parent,label,value,set,{type:typeof value==='number'?'number':'textarea'});return;}
    const group=el('fieldset',undefined,'group');group.append(el('legend',label));parent.append(group);
    if(Array.isArray(value)&&value.length>=3&&typeof value[0]==='string'&&(value[0].startsWith('/assets/')||value[0].startsWith('https://'))&&typeof value[1]==='number'){
      photo(group,'Imagem',value[0],(url,w,h)=>{value[0]=url;if(w)value[1]=w;if(h)value[2]=h;set(value);});if(typeof value[3]==='string')field(group,'Descrição da imagem',value[3],v=>value[3]=v);return;
    }
    if(Array.isArray(value)&&value.length===4&&typeof value[0]==='string'&&typeof value[1]==='string'&&typeof value[2]==='number'){
      photo(group,'Imagem',value[0],(url,w,h)=>{value[0]=url;if(w)value[2]=w;if(h)value[3]=h;set(value);});field(group,'Descrição da imagem',value[1],v=>value[1]=v);return;
    }
    for(const [key,item]of Object.entries(value)){
      const container=el('div',undefined,Array.isArray(value)?'array-item':'stack');group.append(container);
      generic(container,item,v=>{value[key]=v;set(value);},Array.isArray(value)?'Item '+(Number(key)+1):(labels[key]||key.replaceAll('_',' ')));
      if(Array.isArray(value))button(container,'Remover item',()=>{value.splice(Number(key),1);set(value);dirty();render();},'danger small');
    }
    if(Array.isArray(value))button(group,'Adicionar item',()=>{const sample=value[0];value.push(sample&&typeof sample==='object'?structuredClone(sample):'');set(value);dirty();render();});
  }
  function projectEditor(){
    const layout=el('div',undefined,'split-editor'),list=el('div',undefined,'record-list');layout.append(list);$('#editor').append(layout);
    button(list,'+ Novo empreendimento',()=>{
      const name=prompt('Nome do novo empreendimento:');if(!name?.trim())return;
      let slug=name.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'')||'empreendimento';const base=slug;let n=2;while(state.data.projects.some(p=>p.slug===slug))slug=base+'-'+n++;
      const logo=state.data.site.logo;
      state.data.projects.push({slug,name:name.trim(),full:name.trim(),status:'lancamento',region:'vale',city:null,hood:null,location:'Localização a informar',street:null,area:null,beds:null,pitch:'Descrição a informar',featured_text:'Descrição a informar',additional_description:'',card:[logo,1200,800],hero:null,hero_logo:[logo,1200,800],logo:[logo,logo],contain:true,featured_order:null});state.data.updates[slug]={progress_percent:null,progress_stages:[],exact_address:null,coordinates:null,coordinate_source:null};state.data.media[slug]=[];state.project=state.data.projects.length-1;dirty();render();},'add');
    state.data.projects.forEach((p,i)=>{const b=button(list,p.name,()=>{state.project=i;render();});b.setAttribute('aria-pressed',String(i===state.project));});
    const p=state.data.projects[state.project];if(!p){layout.append(el('p','Adicione um empreendimento.','panel'));return;}
    const panel=el('div',undefined,'panel');layout.append(panel);panel.append(el('h2',p.name));const form=el('div',undefined,'form-grid');panel.append(form);
    for(const key of ['name','full','location','city','hood','street','area','beds','region'])field(form,labels[key]||key,p[key],v=>{p[key]=v||null;if(key==='street')state.data.updates[p.slug].exact_address=v||null;if(p.slug==='haus'&&state.data.details.haus?.specs){if(key==='area')state.data.details.haus.specs[0][1]=v;if(key==='beds')state.data.details.haus.specs[1][1]=v;}});
    field(form,'Endereço da página',p.slug,()=>{},{disabled:true,help:'Criado a partir do nome. A edição do nome preserva o endereço dos links existentes.'});
    select(form,'Status',p.status,[['lancamento','Lançamento'],['em-obras','Em obras'],['entregue','Entregue']],v=>p.status=v);
    field(form,'Ordem nos destaques',p.featured_order,v=>p.featured_order=v,{type:'number',help:'Deixe vazio para não destacar. Use 1, 2, 3… sem repetir.'});
    for(const key of ['pitch','featured_text','additional_description'])field(form,labels[key],p[key],v=>p[key]=v,{type:'textarea',wide:true});
    field(form,'Link de atendimento (opcional)',p.wa_link,v=>{if(v)p.wa_link=v;else delete p.wa_link;},{wide:true});
    photo(form,'Foto de apresentação / card',p.card[0],(url,w,h)=>{p.card=[url,w||p.card[1],h||p.card[2]];p.contain=false;if(p.launch_card)p.launch_card=[...p.card];});
    photo(form,'Foto do topo da página',p.hero?.[0]||p.card[0],(url,w,h)=>{p.hero=[url,w||1200,h||800];p.presentation_override=true;});
    photo(form,'Logo do empreendimento',p.logo[0],url=>{p.logo=[url,url];p.hero_logo=[url,1200,800];});
    const u=state.data.updates[p.slug];const progress=el('fieldset',undefined,'group');progress.append(el('legend','Evolução da obra'));panel.append(progress);
    field(progress,'Percentual geral (%)',u.progress_percent,v=>u.progress_percent=v,{type:'number',help:'Vazio = a informar. Zero é um percentual real e só deve ser usado quando confirmado.'});
    (u.progress_stages||=[]).forEach((stage,i)=>{const row=el('div',undefined,'inline-row');progress.append(row);field(row,'Etapa',stage.name,v=>stage.name=v);field(row,'Percentual (%)',stage.percent,v=>stage.percent=v,{type:'number'});button(row,'Remover',()=>{u.progress_stages.splice(i,1);dirty();render();},'danger small');});
    button(progress,'+ Adicionar etapa',()=>{u.progress_stages.push({name:'Nova etapa',percent:null});dirty();render();});
    field(progress,'Endereço exato confirmado',u.exact_address,v=>{u.exact_address=v||null;p.street=v||null;});const coord=el('div',undefined,'inline-row');progress.append(coord);
    ['Latitude','Longitude'].forEach((label,i)=>field(coord,label,u.coordinates?.[i],v=>{const pair=u.coordinates||[null,null];pair[i]=v;u.coordinates=pair.every(n=>n===null)?null:pair;},{type:'number'}));
    field(progress,'Fonte da localização',u.coordinate_source,v=>u.coordinate_source=v||null);
    const gallery=el('fieldset',undefined,'group');gallery.append(el('legend','Galeria de fotos'));panel.append(gallery);const media=state.data.media[p.slug]||=[];
    media.forEach((image,i)=>{const item=el('div',undefined,'array-item');gallery.append(item);photo(item,'Foto '+(i+1),image.src,(url,w,h)=>{image.src=url;if(w)image.width=w;if(h)image.height=h;});field(item,'Legenda',image.caption,v=>image.caption=v);button(item,'Remover foto',()=>{media.splice(i,1);dirty();render();},'danger small');});
    button(gallery,'+ Adicionar foto',()=>{media.push({src:p.card[0],width:p.card[1],height:p.card[2],caption:p.name});dirty();render();});
    if(state.data.details[p.slug]){const more=el('details');more.append(el('summary','Informações adicionais: plantas, lazer e diferenciais'));panel.append(more);generic(more,state.data.details[p.slug],v=>state.data.details[p.slug]=v,'Conteúdo detalhado');}
    button(panel,'Excluir empreendimento',()=>{if(!confirm('Excluir '+p.name+'? A exclusão será aplicada ao salvar.'))return;state.data.projects.splice(state.project,1);delete state.data.updates[p.slug];delete state.data.media[p.slug];delete state.data.details[p.slug];state.project=Math.max(0,state.project-1);dirty();render();},'danger');
  }
  function blogEditor(){
    const layout=el('div',undefined,'split-editor'),list=el('div',undefined,'record-list');layout.append(list);$('#editor').append(layout);
    button(list,'+ Nova notícia',()=>{state.data.blog.unshift({id:'noticia-'+Date.now(),title:'Nova notícia',text:'',image:state.data.site.logo,date:new Date().toISOString().slice(0,10),project_slug:''});state.post=0;dirty();render();},'add');
    state.data.blog.forEach((post,i)=>{const b=button(list,post.title,()=>{state.post=i;render();});b.setAttribute('aria-pressed',String(i===state.post));});
    const post=state.data.blog[state.post];if(!post)return;const panel=el('div',undefined,'panel stack');layout.append(panel);
    field(panel,'Título',post.title,v=>post.title=v);field(panel,'Texto',post.text,v=>post.text=v,{type:'textarea'});field(panel,'Data (opcional)',post.date,v=>post.date=v,{type:'date'});
    select(panel,'Empreendimento relacionado',post.project_slug||'',[['','Nenhum'],...state.data.projects.map(p=>[p.slug,p.name])],v=>post.project_slug=v);
    photo(panel,'Imagem da notícia',post.image,v=>post.image=v);
    button(panel,'Excluir notícia',()=>{if(confirm('Excluir esta notícia ao salvar?')){state.data.blog.splice(state.post,1);state.post=0;dirty();render();}},'danger');
  }
  function siteEditor(){const panel=el('div',undefined,'panel');panel.append(el('p','Edite os textos e as imagens institucionais. Nos títulos, em e strong sem atributos mantêm os destaques de formatação.','hint'));$('#editor').append(panel);generic(panel,state.data.site,v=>state.data.site=v,'Conteúdo do site');}
  function passwordEditor(){const panel=el('form',undefined,'panel stack password-panel');panel.append(el('h2','Trocar senha'));const first=field(panel,'Nova senha','',()=>{},{type:'password'}),second=field(panel,'Confirmar nova senha','',()=>{},{type:'password'});const submit=el('button','Alterar senha');submit.type='submit';panel.append(submit);panel.addEventListener('submit',async e=>{e.preventDefault();if(first.value!==second.value)return notice('As senhas não conferem.',true);try{const r=await api('password',{method:'POST',body:{password:first.value}});if(r.ok)showLogin();else notice(r.message);}catch(error){notice(error.message,true);}});$('#editor').append(panel);}
  function render(){
    $('#editor').replaceChildren();$('#section-title').textContent={projects:'Empreendimentos',blog:'Blog',site:'Textos do site',password:'Senha'}[state.tab];
    document.querySelectorAll('[data-tab]').forEach(b=>b.setAttribute('aria-current',b.dataset.tab===state.tab?'page':'false'));
    ({projects:projectEditor,blog:blogEditor,site:siteEditor,password:passwordEditor})[state.tab]();
  }
  document.querySelectorAll('[data-tab]').forEach(b=>b.addEventListener('click',()=>{state.tab=b.dataset.tab;render();}));
  $('#login-form').addEventListener('submit',async e=>{e.preventDefault();const b=e.submitter;b.disabled=true;$('#login-error').textContent='';try{const r=await api('login',{method:'POST',body:{password:$('#password').value}});state.csrf=r.csrf;$('#password').value='';await load();}catch(error){$('#login-error').textContent=error.message;}finally{b.disabled=false;}});
  $('#save').addEventListener('click',async()=>{const b=$('#save');b.disabled=true;try{const r=await api('save',{method:'POST',body:{data:state.data,revision:state.revision}});notice(r.message,!r.ok&&!r.demo);if(r.ok){state.revision=r.revision;state.dirty=false;b.textContent='Salvar alterações';}}catch(error){notice(error.message,true);}finally{b.disabled=false;}});
  $('#reload').addEventListener('click',()=>{if(!state.dirty||confirm('Descartar as alterações ainda não salvas?'))load().catch(e=>notice(e.message,true));});
  $('#logout').addEventListener('click',async()=>{try{await api('logout',{method:'POST',body:{}});showLogin();}catch(error){notice(error.message,true);}});
  addEventListener('beforeunload',e=>{if(state.dirty){e.preventDefault();e.returnValue='';}});
  api('status').then(async r=>{if(r.authenticated){state.csrf=r.csrf;await load();}}).catch(error=>{$('#login-error').textContent=error.message||'Não foi possível conectar ao painel. Tente novamente.';});
})();
