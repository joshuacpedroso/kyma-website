// Exercises the Vercel adapter with a disposable password, never production credentials.
const assert=require('node:assert/strict'),crypto=require('node:crypto'),fs=require('node:fs');
const handler=require('../api/adm.js');
const password='test-password-only',salt='local-test-salt';
const config={password:{salt,iterations:210000,hash:crypto.pbkdf2Sync(password,salt,210000,32,'sha256').toString('hex')},session_ttl:3600};
process.env.KYMA_ADM_SESSION_SECRET=crypto.randomBytes(32).toString('hex');
let cookie='',csrf='';
async function call(action,method='GET',body={},withToken=true){
 const headers={};if(cookie)headers.cookie=cookie;if(withToken&&csrf)headers['x-csrf-token']=csrf;
 const result={headers:{}};
 const res={setHeader:(key,value)=>result.headers[key.toLowerCase()]=value,end:body=>result.body=JSON.parse(body)};
 Object.defineProperty(res,'statusCode',{set:value=>result.status=value});
 await handler({url:'/api/adm?action='+action,method,body,headers},res);return result;
}
(async()=>{
 assert.equal((await call('status')).status,503);
 process.env.KYMA_ADM_CONFIG=JSON.stringify(config);
 assert.equal((await call('status')).body.authenticated,false);
 assert.equal((await call('load')).status,401);
 assert.equal((await call('save','POST')).status,401);
 assert.equal((await call('login','POST',{password:'wrong'})).status,401);
 const login=await call('login','POST',{password});assert.equal(login.body.authenticated,true);csrf=login.body.csrf;
 cookie=login.headers['set-cookie'].split(';')[0];assert.match(login.headers['set-cookie'],/HttpOnly; Secure; SameSite=Strict/);
 const before=await call('load');assert.equal(before.status,200);assert.ok(before.body.data.projects.length);
 assert.equal((await call('save','POST',{},false)).status,403);
 const result=await call('save','POST',{data:before.body.data,revision:before.body.revision});assert.equal(result.status,200);assert.equal(result.body.demo,true);assert.equal(result.body.ok,false);
 assert.equal((await call('load')).body.revision,before.body.revision);
 assert.equal((await call('upload','POST')).body.demo,true);
 assert.equal((await call('password','POST',{password:'replacement'})).body.demo,true);
 const logout=await call('logout','POST');assert.match(logout.headers['set-cookie'],/Max-Age=0/);cookie='';assert.equal((await call('save','POST')).status,401);
 console.log('PASS demo configuration guard, login, signed session, CSRF, protected data, Save/upload/password no-write, logout');
})().catch(error=>{console.error(error);process.exit(1)});
