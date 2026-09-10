"""Staged LangGraph pipeline: authorize → link → retrieve → expand → attach → answer.

Graph traversal finds candidates, never manufactures evidence. The same scope,
answerability, citation and context-budget policies apply to the vector baseline.
"""
from __future__ import annotations

import logging
import re
from time import perf_counter
from typing import TypedDict
from langgraph.graph import END, START, StateGraph

from graph_builder import build_graph, eligible_documents, link_entities, query_plan, traverse
from llm import model_configured, select_claims
from settings import QueryOptions, freshness
from vector_rag import VectorRAG

LOG = logging.getLogger("qei.pipeline")


class State(TypedDict, total=False):
    question: str
    options: QueryOptions
    strategy: str
    documents: dict
    seeds: list
    plan: dict
    ranked: list
    depths: dict
    parents: dict
    trace: list
    evidence: list
    conflicts: list
    result: dict
    refusal: str


class GraphRAG:
    def __init__(self, corpus, vectors=None):
        self.corpus = corpus
        self.vectors = vectors or VectorRAG(corpus)
        flow = StateGraph(State)
        for name in ("authorize", "link", "retrieve", "expand", "attach", "generate"):
            flow.add_node(name, getattr(self, "_"+name))
        flow.add_edge(START, "authorize")
        flow.add_edge("authorize", "link")
        flow.add_conditional_edges("link", lambda state: "generate" if state.get("refusal") else "retrieve")
        flow.add_conditional_edges("retrieve", lambda state: "generate" if state.get("refusal") else "expand")
        flow.add_edge("expand", "attach")
        flow.add_edge("attach", "generate")
        flow.add_edge("generate", END)
        self.workflow = flow.compile()

    def answer(self, question, options=None, strategy="graph"):
        if not isinstance(question, str) or not 3 <= len(question.strip()) <= 2000:
            raise ValueError("Enter a question between 3 and 2,000 characters")
        if strategy not in {"graph", "hybrid", "vector"}:
            raise ValueError("Unknown retrieval strategy")
        options = options or QueryOptions()
        started = perf_counter()
        state = self.workflow.invoke({"question": question.strip(), "options": options,
                                      "strategy": strategy, "trace": [], "evidence": [], "conflicts": []})
        result = state["result"]
        result.update(latency_ms=round((perf_counter()-started)*1000, 2), strategy=strategy,
                      question=question, project=options.project, corpus=options.corpus,
                      corpus_hash=self.corpus["corpus_hash"], as_of=options.now.isoformat())
        # No question, document text, credentials, or user identity in logs.
        LOG.info("query_completed", extra={"strategy": strategy, "status": result["status"],
                                         "latency_ms": result["latency_ms"], "evidence_count": len(result["evidence"])})
        return result

    def _authorize(self, state):
        docs = eligible_documents(self.corpus, state["options"])
        return {"documents": docs, "trace": [{"stage": "authorize", "eligible_records": len(docs),
                 "policy": "Project, corpus, ACL, quarantine and source-availability filters precede retrieval."}]}

    def _link(self, state):
        seeds, error = link_entities(state["question"], state["documents"])
        plan = query_plan(state["question"], state["options"])
        return {"seeds": seeds, "plan": plan, "refusal": error or "",
                "trace": state["trace"] + [{"stage": "link", "seeds": seeds, "plan": plan,
                                             "resolution": "exact identifiers / unique quoted titles; no fuzzy first-match"}]}

    def _retrieve(self, state):
        ranked = self.vectors.search(state["question"], state["options"],
                                     "vector" if state["strategy"] == "vector" else "hybrid", state["documents"])
        # A shared, explicitly documented answerability gate. It is not used to
        # reorder the vector baseline or to cherry-pick graph evaluation results.
        usable = [r for r in ranked if r["dense"] > .05 and r["coverage"] >= .18]
        refusal = "" if usable or state["seeds"] else "The authorized corpus has no sufficiently relevant evidence."
        seeds = state["seeds"] or list(dict.fromkeys(r["chunk"]["id"] for r in usable[:2]))
        return {"ranked": ranked, "seeds": seeds, "refusal": refusal,
                "trace": state["trace"] + [{"stage": "retrieve", "method": state["strategy"],
                    "seeds": seeds, "shared_corpus": True, "same_context_budget": True}]}

    def _expand(self, state):
        if state["strategy"] != "graph":
            return {"depths": {}, "parents": {}, "trace": state["trace"]+[
                {"stage": "expand", "skipped": True, "reason": "Baseline uses no graph traversal"}]}
        graph = build_graph(state["documents"])
        depths, parents, truncated = traverse(graph, state["seeds"], state["plan"])
        return {"depths": depths, "parents": parents, "trace": state["trace"] + [
            {"stage": "expand", "visited_records": len(depths), "node_budget_reached": truncated,
             "max_hops": state["plan"]["max_hops"], "paths": parents}]}

    def _attach(self, state):
        options = state["options"]
        rows = state["ranked"]
        depths = state["depths"]
        target_types = set(state["plan"]["target_types"])
        graph_mode = state["strategy"] == "graph"
        if graph_mode:
            rows = [r for r in rows if r["chunk"]["id"] in depths]
            def priority(row):
                doc = row["chunk"]
                return (3 * (doc["document_type"] in target_types) + row["coverage"]
                        + .06 * doc["authoritative_level"] - .025 * depths[doc["id"]]
                        + .05 * (freshness(doc, options.now) == "current"))
            rows = sorted(rows, key=lambda r: (-priority(r), r["chunk"]["chunk_id"]))
        selected = []
        used = set()
        words = 0
        for row in rows:
            chunk = row["chunk"]
            count = len(chunk["content"].split())
            if chunk["id"] in used or words+count > options.max_context_words:
                continue
            # On no-ID broad queries, prevent unrelated dense tail from becoming
            # claimed evidence. Baselines still expose their actual ranked top-k.
            if not graph_mode and row["dense"] <= .05:
                continue
            used.add(chunk["id"])
            words += count
            selected.append({"source_id": chunk["id"], "chunk_id": chunk["chunk_id"],
                "title": chunk["title"], "source_type": chunk["source_type"], "project": chunk["project"],
                "url": chunk["url"], "content": chunk["content"], "synthetic": chunk.get("synthetic", False),
                "authority": chunk["authoritative_level"], "updated_at": chunk["updated_at"],
                "freshness": freshness(chunk, options.now), "approval_status": chunk.get("approval_status", "observed"),
                "source_rows": chunk.get("source_rows", []), "hop": depths.get(chunk["id"]),
                "dense_score": round(row["dense"], 4), "match_coverage": round(row["coverage"], 4)})
            if len(selected) >= options.top_k:
                break
        # Detect conflicts across authorized documents for entities actually
        # retrieved, independently of relation filters and the displayed top-k.
        entities = {state["documents"][s["source_id"]].get("entity_id") for s in selected} - {None}
        conflicts = []
        for entity in sorted(entities):
            related = [d for d in state["documents"].values() if d.get("entity_id") == entity]
            keys = set().union(*(d.get("facts", {}).keys() for d in related))
            for key in sorted(keys):
                holders = [d for d in related if key in d.get("facts", {})]
                if len({str(d["facts"][key]) for d in holders}) > 1:
                    preferred = max(holders, key=lambda d: (d["authoritative_level"], d["updated_at"] or ""))
                    conflicts.append({"field": key, "preferred_source_id": preferred["id"],
                        "reason": "Higher authority, then newer timestamp; discrepancy is still disclosed.",
                        "sources": [{"source_id": d["id"], "value": d["facts"][key], "url": d["url"],
                                     "in_context": d["id"] in used} for d in holders]})
        return {"evidence": selected, "conflicts": conflicts, "trace": state["trace"] + [
            {"stage": "attach", "context_records": len(selected), "context_words": words,
             "max_context_words": options.max_context_words, "top_k": options.top_k,
             "policy": "Source documents attached directly; relation filters cannot suppress their provenance."}]}

    def _generate(self, state):
        options = state["options"]
        evidence = state.get("evidence", [])
        reason = state.get("refusal") or ""
        status = "INSUFFICIENT_EVIDENCE" if reason or not evidence else "EVIDENCE_FOUND"
        if "Ambiguous" in reason:
            status = "NEEDS_CLARIFICATION"
        target_types = set(state.get("plan", {}).get("target_types", []))
        required_types = set(state.get("plan", {}).get("required_types", []))
        found_types = {state["documents"][e["source_id"]]["document_type"] for e in evidence}
        if required_types - found_types:
            status, reason = "INSUFFICIENT_EVIDENCE", "Requested artifact types are missing: "+", ".join(sorted(required_types-found_types))+"."
        if evidence and target_types and not any(state["documents"][e["source_id"]]["document_type"] in target_types for e in evidence):
            status, reason = "INSUFFICIENT_EVIDENCE", "Related records were found, but not the requested artifact type."
        if evidence and re.search(r"\b(today|current|latest|production|now)\b", state["question"], re.I):
            relevant = [e for e in evidence if not target_types or state["documents"][e["source_id"]]["document_type"] in target_types]
            if not relevant or any(e["freshness"] != "current" or e["synthetic"] for e in relevant):
                status, reason = "INSUFFICIENT_EVIDENCE", "Dated samples and synthetic records cannot establish current production state."
        answerable = status not in {"INSUFFICIENT_EVIDENCE", "NEEDS_CLARIFICATION"}
        if options.unavailable:
            status = "SOURCE_UNAVAILABLE"
            reason = "Simulated unavailable sources: "+", ".join(sorted(options.unavailable))+". Any remaining evidence is partial."
        conflicts = state.get("conflicts", [])
        if conflicts and status == "EVIDENCE_FOUND":
            status, reason = "CONFLICTING_EVIDENCE", "Sources disagree. Prefer the approved authority shown below; do not merge conflicting claims."
        claims = []
        if answerable:
            for item in evidence:
                candidates = re.split(r"(?<=[.!?])\s+", item["content"])
                query_terms = {t for t in self.vectors.tokens(state["question"]) if not re.search(r"-\d", t)}
                def span_score(text):
                    score = len(query_terms & set(self.vectors.tokens(text)))
                    if re.search(r"who|approv|owner", state["question"], re.I) and re.search(r"approved|owner|lead", text, re.I):
                        score += 3
                    return score
                best_index = max(range(len(candidates)), key=lambda i: span_score(candidates[i]))
                if re.search(r"(which|list|what).*(tests|test cases).*(run|execut)", state["question"], re.I):
                    membership = next((i for i, text in enumerate(candidates) if text.startswith("Test identifiers in this run:")), None)
                    if membership is not None:
                        best_index = membership
                best = " ".join(candidates[best_index:best_index+2])
                # One exact evidence span, not an invented fluent assertion.
                claims.append({"source_id": item["source_id"], "chunk_id": item["chunk_id"], "quote": best,
                               "url": item["url"], "synthetic": item["synthetic"]})
        generation = "extractive"
        if options.use_model and claims:
            try:
                claims = select_claims(state["question"], claims)
                generation = "llm-constrained"
                if not claims:
                    status, reason = "INSUFFICIENT_EVIDENCE", "The model selected no answerable evidence."
            except Exception as error:
                generation = "extractive-fallback"
                # Do not log exception strings: providers can echo prompts/keys.
                LOG.warning("model_fallback", extra={"error_type": type(error).__name__})
        by_chunk = {e["chunk_id"]: e for e in evidence}
        if any(c["quote"] not in by_chunk[c["chunk_id"]]["content"] or c["source_id"] != by_chunk[c["chunk_id"]]["source_id"] for c in claims):
            raise ValueError("Citation validation failed")
        quality = round(100*sum(.5*e["authority"]/5+.3*e["match_coverage"]+.2*(e["freshness"]=="current") for e in evidence)/max(1,len(evidence)))
        return {"result": {"status": status, "reason": reason, "claims": claims, "evidence": evidence,
            "conflicts": conflicts, "generation": generation, "evidence_quality": quality,
            "quality_note": "Heuristic evidence quality, not calibrated confidence or semantic faithfulness.",
            "trace": state["trace"]+[{"stage": "generate", "generation": generation, "validated_claims": len(claims)}],
            "synthetic": any(e["synthetic"] for e in evidence), "model_configured": model_configured()}}
