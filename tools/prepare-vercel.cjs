// Only public assets are emitted as static files. PHP and content stay server-side.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..'),output=path.join(root,'.vercel-public');
fs.rmSync(output,{recursive:true,force:true});fs.mkdirSync(output,{recursive:true});
for(const entry of fs.readdirSync(root,{withFileTypes:true})){
 if(entry.isFile()&&(/\.html$/.test(entry.name)||['robots.txt','sitemap.xml','site.webmanifest'].includes(entry.name)))fs.copyFileSync(path.join(root,entry.name),path.join(output,entry.name));
}
fs.cpSync(path.join(root,'assets'),path.join(output,'assets'),{recursive:true,filter:src=>!['.htaccess','project-media.json'].includes(path.basename(src))});
fs.mkdirSync(path.join(output,'adm'));
for(const name of ['index.html','admin.css','admin.js'])fs.copyFileSync(path.join(root,'adm',name),path.join(output,'adm',name));
console.log('Public pages/assets emitted; PHP, private configuration and editorial JSONs excluded.');
