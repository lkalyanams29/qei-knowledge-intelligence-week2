"""Build a provenance-preserving immutable retrieval snapshot from approved files.

No enterprise API shapes are assumed. Additional source exports use the same
validated document schema (see docs/corpus-contract.md).
"""
from __future__ import annotations
import argparse, csv, hashlib, html, json, re, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPO = "https://github.com/lkalyanams29/qei-knowledge-intelligence-week2/blob/main/"
STOP = set("a an the is are was were to for of on in and or with what which how me tell about does do has have this that it from show please".split())
SOURCES = {"jira","confluence","sharepoint","bitbucket","slack","katalon","testops","architecture"}

def tokens(text):
    return [w for w in re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", text.lower()) if w not in STOP and len(w)>1]

def clean(text):
    text = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", "", text, flags=re.S|re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()

def validate(doc):
    required = ["source_type","source_id","project","document_type","title","authoritative_level","updated_at","url","access_scope","owner","content"]
    if any(k not in doc for k in required): raise ValueError("Document missing required metadata")
    for key in ("source_id", "project", "document_type", "title", "url", "owner", "content"):
        if not isinstance(doc[key], str) or not doc[key].strip(): raise ValueError(f"Invalid or empty {key}")
    if doc["source_type"] not in SOURCES: raise ValueError("Unknown source type")
    if not isinstance(doc["authoritative_level"],int) or not 1<=doc["authoritative_level"]<=5: raise ValueError("Authority must be 1–5")
    if not (doc["access_scope"]=="public" or doc["access_scope"]==f"project:{doc['project']}"): raise ValueError("Invalid access scope")
    if not re.match(r"^https://",doc["url"]): raise ValueError("Provenance URL must use HTTPS")
    if doc["updated_at"]: datetime.fromisoformat(doc["updated_at"].replace("Z","+00:00"))
    doc = dict(doc); doc["content"]=clean(doc["content"])
    if not doc["content"]: raise ValueError("Empty content")
    doc.setdefault("relationships",[]); doc.setdefault("facts",{})
    doc.setdefault("synthetic",False)
    doc.setdefault("dataset","user-supplied-sample" if doc["source_type"]=="testops" else "public-or-design-notes")
    doc.setdefault("approval_status","observed")
    doc["id"]=doc["source_id"]
    doc["sha256"]=hashlib.sha256(doc["content"].encode()).hexdigest()
    doc["injection_flag"]=bool(re.search(r"ignore (all |your |previous )*instructions|reveal.*(secret|password)|system prompt",doc["content"],re.I))
    return doc

def validate_relationships(docs):
    by_id={d["id"]:d for d in docs}
    for doc in docs:
        for relation in doc["relationships"]:
            if relation["target"] not in by_id: raise ValueError("Dangling graph relationship")
            target=by_id[relation["target"]]
            if target["access_scope"]!="public" and doc["access_scope"]!=target["access_scope"]:
                raise ValueError("Source scope must inherit the restricted target's scope")
            quote=relation.get("evidence_quote")
            if not quote and not doc.get("source_rows"):
                raise ValueError("Relationship requires exact source evidence or validated CSV row provenance")
            if quote and (quote not in doc["content"] or relation.get("evidence_source_id")!=doc["id"]):
                raise ValueError("Relationship evidence does not match its source")
            if doc["synthetic"]!=target["synthetic"]:
                raise ValueError("Synthetic links must not invent coverage of supplied records")

def chunk(doc, size=240, overlap=35):
    words=doc["content"].split(); out=[]
    for start in range(0,len(words),size-overlap):
        content=" ".join(words[start:start+size])
        out.append({**doc,"chunk_id":f"{doc['id']}::{len(out)}","content":content,"word_start":start,"word_end":min(len(words),start+size)})
        if start+size>=len(words): break
    return out

def base_doc(sid,project,title,kind,content,line,updated,relations=None):
    return {"source_type":"testops","source_id":sid,"project":project,"title":title,"document_type":kind,"content":content,"authoritative_level":3,"updated_at":updated,"url":REPO+f"sources/katalon_testops_sample_dataset.csv#L{line}","access_scope":"public","owner":"User-supplied sample dataset","relationships":relations or []}

def csv_documents(path):
    with path.open(encoding="utf-8-sig",newline="") as stream:
        raw=list(csv.DictReader(stream))
    required={"execution_id","run_id","project_id","project_name","test_case_id","test_case_name","status","execution_started_at","duration_seconds","suite_name","failure_category","environment","is_flaky"}
    if not raw or not required.issubset(raw[0]): raise ValueError("CSV columns missing or no data")
    seen={}; tests=defaultdict(list); runs=defaultdict(list); projects=defaultdict(list)
    for line,row in enumerate(raw,2):
        key=row["execution_id"]
        if any(not row[k] for k in ("execution_id","run_id","project_name","test_case_id")): raise ValueError(f"Blank identifier at row {line}")
        if key in seen:
            if {k:v for k,v in seen[key].items() if k!="_line"}!=row: raise ValueError(f"Conflicting duplicate execution ID at row {line}")
            continue
        seen[key]=row
        if row["status"] not in {"PASSED","FAILED","SKIPPED","ERROR","INCOMPLETE"}: raise ValueError(f"Unknown status at row {line}")
        datetime.fromisoformat(row["execution_started_at"].replace("Z","+00:00"))
        duration=float(row["duration_seconds"])
        if not np.isfinite(duration) or duration<0: raise ValueError(f"Invalid duration at row {line}")
        row["_line"]=line
        tests[(row["project_name"],row["test_case_id"])].append(row)
        runs[(row["project_name"],row["run_id"])].append(row)
        projects[row["project_name"]].append(row)
    docs=[]
    for (project,tid),rows in sorted(tests.items()):
        rows=sorted(rows,key=lambda r:r["execution_started_at"]); counts=Counter(r["status"] for r in rows); name=rows[0]["test_case_name"]
        run_ids=sorted({r["run_id"] for r in rows}); suites=sorted({r["suite_name"] for r in rows})
        text=f"Test {tid}, {name}, belongs to {project}. The supplied sample records {len(rows)} results: {counts['PASSED']} passed, {counts['FAILED']} failed, {counts['SKIPPED']} skipped. Suites: {', '.join(suites)}. First observed {rows[0]['execution_started_at']}; last observed {rows[-1]['execution_started_at']}. Latest status: {rows[-1]['status']}. Linked run identifiers: {', '.join(run_ids)}. Failure categories: {', '.join(sorted({r['failure_category'] for r in rows if r['failure_category']})) or 'not recorded'}. The sample is_flaky flag occurs in {sum(r['is_flaky']=='1' for r in rows)} result rows. No Jira requirement, source file or step definition linkage is present in this CSV."
        doc=base_doc(tid,project,name,"test_history",text,rows[0]["_line"],rows[-1]["execution_started_at"],[{"target":rid,"type":"executed_in"} for rid in run_ids])
        doc["facts"]={"latest_status":rows[-1]["status"],"passed":counts["PASSED"],"failed":counts["FAILED"],"skipped":counts["SKIPPED"]}
        docs.append(doc)
        doc["source_rows"]=sorted(r["_line"] for r in rows)
    for (project,rid),rows in sorted(runs.items()):
        counts=Counter(r["status"] for r in rows); ids=sorted({r["test_case_id"] for r in rows}); date=max(r["execution_started_at"] for r in rows)
        text=f"Run {rid} belongs to {project}. It contains {len(rows)} results: {counts['PASSED']} passed, {counts['FAILED']} failed, {counts['SKIPPED']} skipped. Latest recorded result timestamp: {date}. Test identifiers in this run: {', '.join(ids)}. Environments: {', '.join(sorted({r['environment'] for r in rows}))}. These are observed sample outcomes, not proof of requirement coverage."
        docs.append(base_doc(rid,project,f"{project} / {rid}","run",text,rows[0]["_line"],date,[{"target":tid,"type":"contains_test"} for tid in ids]))
        docs[-1]["source_rows"]=sorted(r["_line"] for r in rows)
    for project,rows in sorted(projects.items()):
        counts=Counter(r["status"] for r in rows); passed=counts["PASSED"]; failed=counts["FAILED"]; rate=round(100*passed/(passed+failed),2) if passed+failed else None
        ids=sorted({r["test_case_id"] for r in rows}); date=max(r["execution_started_at"] for r in rows)
        text=f"{project} supplied CSV portfolio: {len(ids)} distinct automated test case identifiers, {len({r['run_id'] for r in rows})} runs, {len(rows)} test results. Passed: {passed}; failed: {failed}; skipped: {counts['SKIPPED']}. Pass rate is {rate}% using passed divided by passed plus failed. Skipped and error outcomes are excluded from the denominator. This is the full supplied file, not the previous dashboard's last-30-day window. Observation period: {min(r['execution_started_at'] for r in rows)} through {date}. Test names in this project include: {', '.join(sorted({r['test_case_name'] for r in rows})[:12])}."
        docs.append(base_doc(f"PORTFOLIO-{rows[0]['project_id']}",project,f"{project} sample portfolio","portfolio",text,rows[0]["_line"],date,[{"target":tid,"type":"owns_test"} for tid in ids]))
        docs[-1]["source_rows"]=sorted(r["_line"] for r in rows)
    return docs,{"rows":len(seen),"raw_rows":len(raw),"tests":len(tests),"runs":len(runs),"projects":sorted(projects),"period_start":min(r["execution_started_at"] for r in seen.values()),"period_end":max(r["execution_started_at"] for r in seen.values())}

def build(extra=None,size=240,output=None):
    docs,stats=csv_documents(ROOT/"sources/katalon_testops_sample_dataset.csv")
    docs+=json.loads((ROOT/"sources/public-notes.json").read_text(encoding="utf-8"))
    profiles=json.loads((ROOT/"config/projects.json").read_text(encoding="utf-8"))
    for name,p in profiles.items():
        docs.append({"source_type":"architecture","source_id":"PROFILE-"+name.replace(" ","-"),"project":name,"document_type":"project_profile","title":name+" QE strategy","content":f"User-provided design notes: {name} project type is {p['type']}. Testing strategy: {p['strategy']}. Review dimensions: {', '.join(p['checks'])}. {p['basis']} This is a design brief, not an approved business requirement or an implementation artifact.","authoritative_level":2,"updated_at":None,"url":REPO+"sources/qei-architecture.txt","access_scope":"public","owner":"Project author"})
    if extra:
        docs+=json.loads(Path(extra).read_text(encoding="utf-8"))
    for synthetic_folder in (ROOT/"data/synthetic", ROOT/"data/mcp_samples"):
        for export in sorted(synthetic_folder.glob("*.json")):
            docs+=json.loads(export.read_text(encoding="utf-8"))
    docs=[validate(d) for d in docs]
    if len({d["id"] for d in docs})!=len(docs): raise ValueError("Duplicate source IDs: namespace exported IDs before ingesting")
    validate_relationships(docs)
    chunks=[c for d in docs for c in chunk(d,size)]
    vocab=sorted({t for c in chunks for t in tokens(c["title"]+" "+c["content"])})
    lookup={t:i for i,t in enumerate(vocab)}
    matrix=np.zeros((len(chunks),len(vocab)),dtype=np.float64)
    for i,c in enumerate(chunks):
        freq=Counter(tokens(c["title"]+" "+c["content"]));c["terms"]=dict(freq);c["length"]=sum(freq.values())
        for t,n in freq.items(): matrix[i,lookup[t]]=n
    df=(matrix>0).sum(axis=0);idf=np.log((1+len(chunks))/(1+df))+1
    tfidf=(1+np.log(np.maximum(matrix,1)))*(matrix>0)*idf
    tfidf/=np.maximum(np.linalg.norm(tfidf,axis=1,keepdims=True),1e-12)
    _,_,vt=np.linalg.svd(tfidf,full_matrices=False)
    dimensions=min(96,max(1,len(chunks)-1),len(vocab));projection=vt[:dimensions]
    vectors=tfidf@projection.T
    vectors/=np.maximum(np.linalg.norm(vectors,axis=1,keepdims=True),1e-12)
    for c,v in zip(chunks,vectors): c["vector"]=np.round(v,7).tolist()
    index={"version":1,"built_at":datetime.now(timezone.utc).isoformat(),"embedding":{"model":"corpus-trained TF-IDF / LSA","dimensions":dimensions,"vocab":vocab,"idf":np.round(idf,7).tolist(),"projection":np.round(projection,7).tolist(),"stop_words":sorted(STOP)},"chunking":{"words":size,"overlap":35,"strategy":"document-boundary word windows"},"stats":stats,"profiles":profiles,"documents":docs,"chunks":chunks,"average_length":sum(c["length"] for c in chunks)/len(chunks),"df":dict(zip(vocab,df.tolist()))}
    index["corpus_hash"]=hashlib.sha256(json.dumps(docs,sort_keys=True).encode()).hexdigest()
    index["stats"]["synthetic_documents"]=sum(d["synthetic"] for d in docs)
    out=Path(output) if output else ROOT/"data/index.json";out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(index,separators=(",",":")),encoding="utf-8")
    print(json.dumps({"documents":len(docs),"chunks":len(chunks),"dimensions":dimensions,"stats":stats,"output":str(out)}))
    return index
if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--extra");parser.add_argument("--chunk-words",type=int,default=240);parser.add_argument("--output");args=parser.parse_args()
    if args.chunk_words<80: parser.error("chunk size must be at least 80 words")
    build(args.extra,args.chunk_words,args.output)
