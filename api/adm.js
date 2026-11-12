const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const {promisify}=require('node:util');
const pbkdf2=promisify(crypto.pbkdf2);
const files={projects:'content/projects.json',updates:'content/project-updates.json',media:'assets/project-media.json',details:'content/project-details.json',site:'content/site.json',blog:'content/blog.json'};
const read=file=>fs.readFileSync(path.join(process.cwd(),file),'utf8');
const equal=(a,b)=>{const x=Buffer.from(String(a||'')),y=Buffer.from(String(b||''));return x.length===y.length&&crypto.timingSafeEqual(x,y);};
module.exports=async(req,res)=>{
  res.setHeader('Content-Type','application/json; charset=utf-8');res.setHeader('Cache-Control','no-store');res.setHeader('X-Content-Type-Options','nosniff');
  const send=(code,body)=>{res.statusCode=code;res.end(JSON.stringify(body));};
  try{
    if(!process.env.KYMA_ADM_CONFIG)return send(503,{ok:false,message:'Login de demonstração aguardando configuração privada da hospedagem.'});
    const config=JSON.parse(process.env.KYMA_ADM_CONFIG);
    const secret=process.env.KYMA_ADM_SESSION_SECRET;
    if(!secret||secret.length<32)return send(503,{ok:false,message:'Demonstração temporariamente indisponível.'});
    const sign=value=>crypto.createHmac('sha256',secret).update(value).digest('base64url');
    const version=crypto.createHash('sha256').update(config.password.hash).digest('hex');
    const url=new URL(req.url,'https://kyma.local');const action=url.searchParams.get('action')||'status';
    const post=req.method==='POST';let body=req.body||{};
    if(typeof body==='string'){try{body=JSON.parse(body);}catch{return send(400,{ok:false,message:'Pedido inválido.'});}}
    const cookie=(req.headers.cookie||'').split(';').map(x=>x.trim()).find(x=>x.startsWith('kyma_adm_preview='))?.slice(17);
    let session=null;
    if(cookie){try{const [payload,signature]=cookie.split('.');if(equal(sign(payload),signature)){const decoded=JSON.parse(Buffer.from(payload,'base64url').toString());if(decoded.exp>Date.now()&&decoded.version===version)session=decoded;}}catch{}}
    if(action==='login'){
      if(!post)return send(405,{ok:false,message:'Método inválido.'});
      if(typeof body.password!=='string'||body.password.length>256)return send(401,{ok:false,message:'Senha incorreta.'});
      const hash=(await pbkdf2(body.password,config.password.salt,config.password.iterations,32,'sha256')).toString('hex');
      if(!equal(hash,config.password.hash))return send(401,{ok:false,message:'Senha incorreta.'});
      session={version,exp:Date.now()+config.session_ttl*1000,csrf:crypto.randomBytes(32).toString('hex')};
      const payload=Buffer.from(JSON.stringify(session)).toString('base64url');
      res.setHeader('Set-Cookie',`kyma_adm_preview=${payload}.${sign(payload)}; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=${config.session_ttl}`);
    }
    if(action==='status'||action==='login')return send(200,{ok:true,authenticated:!!session,demo:true,csrf:session?.csrf||null});
    if(!session)return send(401,{ok:false,message:'Entre com a senha para continuar.'});
    if(post&&!equal(req.headers['x-csrf-token'],session.csrf))return send(403,{ok:false,message:'Sessão inválida. Atualize a página.'});
    if(action==='logout'&&post){res.setHeader('Set-Cookie','kyma_adm_preview=; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=0');return send(200,{ok:true});}
    if(action==='load'&&req.method==='GET'){
      const data={};let bytes='';for(const [key,file]of Object.entries(files)){const text=read(file);bytes+=text;data[key]=JSON.parse(text);}
      return send(200,{ok:true,demo:true,data,revision:crypto.createHash('sha256').update(bytes).digest('hex')});
    }
    if(['save','upload','password'].includes(action)&&post)return send(200,{ok:false,demo:true,message:'Modo demonstração: a gravação e os uploads ficam ativos somente na hospedagem definitiva com PHP. Nenhuma alteração foi gravada.'});
    send(405,{ok:false,message:'Ação inválida.'});
  }catch{send(500,{ok:false,message:'Não foi possível abrir a demonstração. Confira a configuração do servidor.'});}
};
