"""Reproducible paired evaluation; no model or paid API is used by default."""
from __future__ import annotations
import argparse
from dataclasses import replace
from datetime import datetime, timezone
import json
from pathlib import Path
import numpy as np

from graph_builder import load_corpus
from graph_rag import GraphRAG
from questions import COMPARISON_QUESTIONS, SAFETY_QUESTIONS
from settings import QueryOptions, ROOT


def retrieval_scores(result, gold):
    actual = {item["source_id"] for item in result["evidence"]}
    expected = set(gold)
    return {"recall_at_8": len(actual & expected)/len(expected),
            "gold_precision_at_8": len(actual & expected)/max(1, len(actual)),
            "missing_gold": sorted(expected-actual), "retrieved_ids": sorted(actual)}


def citation_scores(result):
    chunks = {e["chunk_id"]: e for e in result["evidence"]}
    claims = result["claims"]
    valid = sum(c["chunk_id"] in chunks and c["source_id"] == chunks[c["chunk_id"]]["source_id"]
                and c["quote"] in chunks[c["chunk_id"]]["content"] and bool(c["quote"]) for c in claims)
    return {"claims": len(claims), "valid_citations": valid,
            "verbatim_citation_support": valid/len(claims) if claims else None}


def evaluate(output=ROOT/"docs/python-evaluation-results.json", model=False):
    corpus = load_corpus()
    engine = GraphRAG(corpus)
    options = QueryOptions(now=datetime(2026, 9, 10, 12, tzinfo=timezone.utc), use_model=model)
    rows = []
    methods = ("graph", "vector", "hybrid")
    for method in methods:
        engine.answer("Show SYN-BSP-REQ-001", options, method)  # Excluded warm-up.
    for position, query in enumerate(COMPARISON_QUESTIONS):
        row = dict(query)
        order = methods[position % 3:]+methods[:position % 3]
        for method in order:
            result = engine.answer(query["question"], options, method)
            row[method] = {**retrieval_scores(result, query["gold"]), **citation_scores(result),
                           "status": result["status"], "latency_ms": result["latency_ms"],
                           "generation": result["generation"]}
        rows.append(row)
    safety = []
    for query in SAFETY_QUESTIONS:
        opt = replace(options, project=query.get("project", "All"), corpus=query.get("corpus", "All"),
                      unavailable=frozenset(query.get("unavailable", [])))
        result = engine.answer(query["question"], opt)
        safety.append({**query, "actual": result["status"], "passed": result["status"] == query["status"],
                       "claims": len(result["claims"]), "latency_ms": result["latency_ms"]})
    summary = {}
    for method in ("graph", "vector", "hybrid"):
        values = [row[method] for row in rows]
        total = sum(v["claims"] for v in values)
        summary[method] = {"mean_recall_at_8": float(np.mean([v["recall_at_8"] for v in values])),
                           "mean_gold_precision_at_8": float(np.mean([v["gold_precision_at_8"] for v in values])),
                           "verbatim_citation_support": sum(v["valid_citations"] for v in values)/total if total else None,
                           "p95_local_ms": float(np.percentile([v["latency_ms"] for v in values], 95))}
    report = {"generated_at": datetime.now(timezone.utc).isoformat(), "corpus_hash": corpus["corpus_hash"],
              "as_of": options.now.isoformat(), "comparison_queries": len(rows), "safety_queries": len(safety),
              "summary": summary, "safety_status_accuracy": sum(q["passed"] for q in safety)/len(safety),
              "semantic_faithfulness": None, "model_enabled": model, "warmup_per_method": 1,
              "limitations": ["Authored development set, not held-out questions or human-rated faithfulness.",
                  "Recall uses source IDs; gold precision penalizes additional valid context not annotated in the small gold set.",
                  "All methods share source text including relationship assertions, LSA embeddings, top-k=8, and a 1400-word budget.",
                  "Vector ranking is dense-only; the same explicit-ID/scope/answerability checks and answer policy apply to all.",
                  "Graph additionally uses up to 3 hops, authority and question-type reranking. This compares full retrieval configurations, not graph topology in isolation.",
                  "Exact quotation support does not measure whether the quote answers the question, nor semantic faithfulness.",
                  "Latency uses one excluded warm-up per method and rotated method order; it excludes ingestion/embedding construction and hosting/network latency unless model mode is enabled."],
              "comparisons": rows, "safety": safety}
    Path(output).write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    lines = ["# Python GraphRAG evaluation", "", f"Corpus hash: `{corpus['corpus_hash']}`", "",
             "Ten varied paired retrieval queries plus fifteen safety/status cases. No human semantic-faithfulness score is claimed.", "",
             "| Method | Mean gold recall@8 | Gold precision@8 | Verbatim citation support | Local P95 ms |",
             "|---|---:|---:|---:|---:|"]
    for method, value in summary.items():
        lines.append(f"| {method} | {value['mean_recall_at_8']:.1%} | {value['mean_gold_precision_at_8']:.1%} | {value['verbatim_citation_support']:.1%} | {value['p95_local_ms']:.2f} |")
    lines += ["", f"Safety status accuracy: {report['safety_status_accuracy']:.1%}.", "", "## Paired questions and missing evidence", "",
              "| Question | Graph recall | Vector recall | Missing graph gold | Missing vector gold |", "|---|---:|---:|---|---|"]
    for row in rows:
        lines.append(f"| {row['id']}: {row['question']} | {row['graph']['recall_at_8']:.0%} | {row['vector']['recall_at_8']:.0%} | {', '.join(row['graph']['missing_gold']) or 'None'} | {', '.join(row['vector']['missing_gold']) or 'None'} |")
    lines += ["", "## Safety cases", "", "| Question | Expected | Actual | Pass |", "|---|---|---|---|"]
    for row in safety:
        lines.append(f"| {row['id']}: {row['question']} | {row['status']} | {row['actual']} | {row['passed']} |")
    lines += ["", "## Interpretation and limitations", "", *[f"- {item}" for item in report["limitations"]], "",
              "Multi-hop paths help traceability; direct summaries may favor vector or hybrid retrieval. The committed row-level results retain failures rather than hiding them. Review both missing gold and irrelevant extra context before changing retrieval settings.", ""]
    Path(output).with_suffix(".md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"summary": summary, "safety_status_accuracy": report["safety_status_accuracy"]}))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", action="store_true", help="Opt into the configured model endpoint")
    parser.add_argument("--output", type=Path, default=ROOT/"docs/python-evaluation-results.json")
    args = parser.parse_args()
    evaluate(args.output, args.model)
