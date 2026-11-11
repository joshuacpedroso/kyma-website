module.exports=(_req,res)=>{res.statusCode=404;res.setHeader('Cache-Control','no-store');res.end('Not found');};
