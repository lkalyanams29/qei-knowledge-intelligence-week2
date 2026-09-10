import index from "./index.json" with {type:"json"};
import {answer,permitted,publicEvidence,projectName} from "./engine.mjs";
export {index};
export function principal(request,env={}){
 const user=env.QEI_TRUST_SITES_IDENTITY==="true"?request.headers.get("oai-authenticated-user-id"):null;
 let acl={};try{acl=JSON.parse(env.QEI_USER_PROJECTS||"{}")}catch{}
 return {projects:user&&Array.isArray(acl[user])?acl[user]:[]};
}
export async function askRequest(request,env={}){
 let body;try{if(Number(request.headers.get("content-length"))>10000)return Response.json({error:"Request too large"},{status:413});const text=await request.text();if(text.length>10000)return Response.json({error:"Request too large"},{status:413});body=JSON.parse(text)}catch{return Response.json({error:"Invalid JSON"},{status:400})}
 if(typeof body.question!=="string"||body.question.trim().length<3||body.question.length>2000)return Response.json({error:"Enter a question between 3 and 2,000 characters."},{status:400});
 const selected=projectName(body.project,index);if(selected!=="All"&&!index.profiles[selected])return Response.json({error:"Unknown project"},{status:400});
 if(!["ask","mentor"].includes(body.mode||"ask")||!["graph","hybrid","vector"].includes(body.strategy||"graph"))return Response.json({error:"Unknown mode or retrieval strategy"},{status:400});
 const result=await answer(index,{question:body.question,project:selected,mode:body.mode||"ask",strategy:body.strategy||"graph",principal:principal(request,env),unavailable:(env.QEI_UNAVAILABLE_SOURCES||"").split(",").filter(Boolean)},{baseUrl:env.QEI_MODEL_BASE_URL,model:env.QEI_MODEL_NAME,apiKey:env.QEI_MODEL_API_KEY});
 return Response.json(publicEvidence(result),{headers:{"Cache-Control":"no-store"}});
}
export function corpusRequest(request,env={}){
 const docs=index.documents.filter(d=>permitted(d,principal(request,env)));
 const allowed=new Set(docs.map(d=>d.id));
 return Response.json({built_at:index.built_at,hash:index.corpus_hash,stats:index.stats,profiles:index.profiles,embedding:{model:index.embedding.model,dimensions:index.embedding.dimensions},chunking:index.chunking,model_configured:!!(env.QEI_MODEL_BASE_URL&&env.QEI_MODEL_NAME),documents:docs.map(({content,injection_flag,sha256,...d})=>({...d,relationships:d.relationships.filter(e=>allowed.has(e.target))})),chunks:index.chunks.filter(c=>allowed.has(c.id)).length},{headers:{"Cache-Control":"no-store"}});
}
