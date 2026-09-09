import {writeFile,mkdir} from "node:fs/promises";
import {performance} from "node:perf_hooks";
import index from "../lib/index.json" with {type:"json"};
import {answer,retrieve} from "../lib/engine.mjs";
const queries=[
 ["History of KT-101-TC-001","WebOps","VERIFIED",["KT-101-TC-001"]],
 ["History of KT-202-TC-001","Salesforce","VERIFIED",["KT-202-TC-001"]],
 ["History of KT-303-TC-001","BSP Services","VERIFIED",["KT-303-TC-001"]],
 ["History of KT-404-TC-001","MyKC","VERIFIED",["KT-404-TC-001"]],
 ["Which tests executed in RUN-00001?","WebOps","VERIFIED",["RUN-00001","KT-101-TC-001"]],
 ["How many results are in RUN-00002?","WebOps","VERIFIED",["RUN-00002"]],
 ["What is the BSP testing strategy?","BSP Services","VERIFIED",["PROFILE-BSP-Services"]],
 ["What is the CXE testing strategy?","CXE","VERIFIED",["PROFILE-CXE"]],
 ["What is the Salesforce business process testing strategy?","Salesforce","VERIFIED",["PROFILE-Salesforce"]],
 ["What is the SPROG hybrid testing strategy?","SPROG","VERIFIED",["PROFILE-SPROG"]],
 ["How should I investigate flaky tests?","All","VERIFIED",["DOC-FLAKINESS"]],
 ["How do Confluence inherited view restrictions work?","All","VERIFIED",["DOC-CONFLUENCE-ACL"]],
 ["How do Slack conversation scopes affect access?","All","VERIFIED",["DOC-SLACK-SCOPES"]],
 ["How can I inspect TestOps execution artifacts?","All","VERIFIED",["DOC-RESULTS"]],
 ["What are the ACs for KAT-1499?","BSP Services","INSUFFICIENT_EVIDENCE",[]],
 ["Which tests cover KAT-1498?","BSP Services","INSUFFICIENT_EVIDENCE",[]],
 ["Analyze the DB mapping","BSP Services","INSUFFICIENT_EVIDENCE",[]],
 ["Where is the Step Definition for the payment API?","BSP Services","INSUFFICIENT_EVIDENCE",[]],
 ["Who approved PR-884?","BSP Services","INSUFFICIENT_EVIDENCE",[]],
 ["What is the current status of KT-101-TC-001?","WebOps","INSUFFICIENT_EVIDENCE",[]],
 ["History of KT-101-TC-001","Salesforce","INSUFFICIENT_EVIDENCE",[]],
 ["Explain xylophone aardvark nebula","All","INSUFFICIENT_EVIDENCE",[]],
 ["Teach me the CXE user journey testing strategy","CXE","VERIFIED",["PROFILE-CXE"]],
 ["What are the MyKC sample portfolio results?","MyKC","VERIFIED",["PORTFOLIO-KT-404"]],
 ["What are the BSP Services sample portfolio results?","BSP Services","VERIFIED",["PORTFOLIO-KT-303"]]
];
const now=new Date("2026-09-09T12:00:00Z"),cases=[];
const modelConfig=process.env.QEI_MODEL_BASE_URL?{baseUrl:process.env.QEI_MODEL_BASE_URL,model:process.env.QEI_MODEL_NAME,apiKey:process.env.QEI_MODEL_API_KEY}:{};
const reportName=modelConfig.baseUrl?"evaluation-llm":"evaluation";
for(const [question,project,status,relevant] of queries){
 const r=await answer(index,{question,project,strategy:"graph",mode:question.startsWith("Teach")?"mentor":"ask",now},modelConfig);
 const ids=r.evidence.map(c=>c.id),hits=relevant.filter(id=>ids.includes(id)).length;
 const supported=r.claims.filter(c=>r.evidence.find(e=>e.chunk_id===c.chunk_id)?.content.includes(c.text)).length;
 cases.push({question,project,expected_status:status,actual_status:r.status,status_correct:r.status===status,expected_relevant_ids:relevant,retrieved_ids:ids,recall:relevant.length?hits/relevant.length:null,claims:r.claims,supported_claims:supported,total_claims:r.claims.length,latency_ms:r.latency_ms,reason:r.reason,generation:r.generation});
}
const graphQueries=[];
for(const run of index.documents.filter(d=>d.document_type==="run").slice(0,10)){
 const question="Which test cases executed in "+run.id+"?";
 const expected=run.relationships.map(e=>e.target),row={question,project:run.project,expected_related_ids:expected};
 for(const strategy of ["vector","graph"]){
  const start=performance.now(),r=retrieve(index,{question,project:run.project,strategy,now,topK:6});const ids=r.evidence.map(c=>c.id);
  row[strategy]={retrieved_ids:ids,recall:expected.filter(id=>ids.includes(id)).length/expected.length,latency_ms:performance.now()-start};
 }
 graphQueries.push(row);
}
const valid=cases.filter(c=>c.recall!==null),refusals=cases.filter(c=>c.expected_status==="INSUFFICIENT_EVIDENCE"),claimCount=cases.reduce((s,c)=>s+c.total_claims,0);
const latency=cases.map(c=>c.latency_ms).sort((a,b)=>a-b);
const report={generated_at:new Date().toISOString(),as_of:now.toISOString(),corpus_hash:index.corpus_hash,corpus:{documents:index.documents.length,chunks:index.chunks.length,graph_nodes:index.documents.length,graph_edges:index.documents.reduce((s,d)=>s+d.relationships.length,0)},methodology:"25 authored checks; gold source IDs manually specified from corpus inventory. Not a held-out benchmark. Exact-quote support is automatic, not semantic faithfulness. Latency is warm local retrieval/extractive composition, not LLM or network latency.",metrics:{status_accuracy:cases.filter(c=>c.status_correct).length/cases.length,relevant_source_recall:valid.reduce((s,c)=>s+c.recall,0)/valid.length,correct_refusal:refusals.filter(c=>c.status_correct).length/refusals.length,verbatim_support:claimCount?cases.reduce((s,c)=>s+c.supported_claims,0)/claimCount:null,semantic_faithfulness:null,p95_local_ms:latency[Math.ceil(latency.length*.95)-1],graph_recall:graphQueries.reduce((s,c)=>s+c.graph.recall,0)/10,vector_recall:graphQueries.reduce((s,c)=>s+c.vector.recall,0)/10},targets:{semantic_faithfulness:.95,retrieval_recall:.9,citation_coverage:1,correct_refusal:.95,p95_end_to_end_ms:8000},cases,graphQueries};
await mkdir(new URL("../docs/",import.meta.url),{recursive:true});
 if(modelConfig.model)report.methodology="25 authored questions run against the same retrieval pipeline plus local Qwen/llama.cpp. Latency includes local model calls and the 6.5-second output-validation fallback, but excludes browser/network-to-site time. Exact quotation support is automatic; semantic faithfulness still requires human review. This is a development set, not a held-out benchmark.";
 report.model=modelConfig.model||null;
 report.model_note=modelConfig.model?"Measured with a configured model, including validated-output fallback; inspect generation per case.":"No model calls in this run.";
 await writeFile(new URL("../docs/"+reportName+"-results.json",import.meta.url),JSON.stringify(report,null,2));
await writeFile(new URL("../docs/"+reportName+"-report.md",import.meta.url),"# Week 2 evaluation report\n\n"+report.methodology+"\n\nMeasured on "+report.generated_at+". Corpus "+report.corpus_hash+".\n\n"+Object.entries(report.metrics).map(([k,v])=>"- "+k+": "+(v===null?"Not evaluated":v)).join("\n")+"\n\n## Per-question results\n\n| Question | Expected | Actual | Relevant-source recall |\n|---|---|---|---|\n"+cases.map(c=>"|"+c.question+"|"+c.expected_status+"|"+c.actual_status+"|"+(c.recall??"N/A")+"|").join("\n")+"\n\n## Graph versus vector (10 questions)\n\nRecall@6 measures linked test IDs found; a seed run consumes one result slot. Large runs have a ceiling below 100%.\n\n| Question | Graph recall | Vector recall |\n|---|---|---|\n"+graphQueries.map(c=>"|"+c.question+"|"+c.graph.recall+"|"+c.vector.recall+"|").join("\n")+"\n\n## Limits\n\nSemantic faithfulness requires human claim review. No LLM faithfulness or hosted P95 claim is made by this run. Unit safety tests use clearly synthetic permission, outage, injection and conflict mutations; those are not included as business evidence. Source ingestion is export-based, not live enterprise synchronization.\n");
console.log(JSON.stringify({metrics:report.metrics,failures:cases.filter(c=>!c.status_correct||c.recall!==null&&c.recall<1).map(c=>({q:c.question,status:c.actual_status,recall:c.recall}))},null,2));
