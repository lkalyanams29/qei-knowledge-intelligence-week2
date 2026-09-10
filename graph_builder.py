"""Validated NetworkX evidence graph, exact entity linking, bounded traversal."""
from __future__ import annotations

import json
import re
from collections import deque
import networkx as nx

from settings import QueryOptions, index_path

ID_PATTERN = re.compile(r"\b[A-Z]{2,}[A-Z0-9]*(?:-[A-Z0-9]+)*-\d+\b", re.I)


def load_corpus(path=None):
    with (path or index_path()).open(encoding="utf-8") as stream:
        corpus = json.load(stream)
    if not corpus.get("corpus_hash") or not corpus.get("chunks"):
        raise ValueError("Missing or invalid corpus; run python scripts/ingest.py")
    return corpus


def permitted(doc, options: QueryOptions):
    scope = doc.get("access_scope")
    return (scope == "public" or scope == f"project:{doc.get('project')}" and doc.get("project") in options.grants)


def eligible_documents(corpus, options):
    return {
        doc["id"]: doc for doc in corpus["documents"]
        if permitted(doc, options)
        and (options.project == "All" or doc["project"] in {options.project, "GLOBAL"})
        and (options.corpus == "All" or bool(doc.get("synthetic")) == (options.corpus == "Synthetic"))
        and not doc.get("injection_flag") and doc["source_type"] not in options.unavailable
    }


def build_graph(documents):
    graph = nx.MultiDiGraph()
    for sid, doc in documents.items():
        graph.add_node(sid, **doc)
    for sid, doc in documents.items():
        for rel in doc.get("relationships", []):
            target = rel["target"]
            if target not in documents:
                continue
            quote = rel.get("evidence_quote")
            if quote and (quote not in doc["content"] or rel.get("evidence_source_id") != sid):
                continue
            # CSV relations are deterministic records with row-level provenance;
            # synthetic/exported relations additionally retain exact assertion spans.
            graph.add_edge(sid, target, type=rel["type"], evidence_source_id=sid,
                           evidence_quote=quote, source_rows=doc.get("source_rows", []))
    return graph


def link_entities(question, documents):
    """No fuzzy first-match: exact IDs, then unique title/alias matches only."""
    ids = list(dict.fromkeys(x.upper() for x in ID_PATTERN.findall(question)))
    by_upper = {sid.upper(): sid for sid in documents}
    if ids:
        if any(sid not in by_upper for sid in ids):
            return [], "No authorized evidence for the requested identifier(s)."
        return [by_upper[sid] for sid in ids], None
    quoted = re.findall(r'"([^"]+)"', question)
    for alias in quoted:
        matches = [sid for sid, d in documents.items() if alias.casefold() in
                   {x.casefold() for x in [d["title"], *d.get("aliases", [])]}]
        if len(matches) > 1:
            return [], "Ambiguous title. Choose a project or use an exact source ID."
        if len(matches) == 1:
            return matches, None
    return [], None


def query_plan(question, options):
    q = question.lower()
    kinds = set()
    if re.search(r"requirement|acceptance|\bacs?\b", q): kinds.add("requirement")
    if re.search(r"design|specification", q): kinds.add("specification")
    if re.search(r"database|\bdb\b|column|mapping", q): kinds.add("database_mapping")
    if re.search(r"pull request|implementation|\bpr\b", q): kinds.add("pull_request")
    if re.search(r"step.definition|helper", q): kinds.add("step_definition")
    if re.search(r"feature|gherkin", q): kinds.add("automation_source")
    if re.search(r"tests?|coverage", q): kinds |= {"test_case", "test_history"}
    if re.search(r"execut|runs?|outcome|status", q): kinds.add("run")
    if re.search(r"triage|cause|defect", q): kinds.add("defect")
    if re.search(r"owner|who|approv", q): kinds |= {"person", "decision", "pull_request"}
    if re.search(r"conflict|window|supersed|discuss|decision", q): kinds |= {"requirement", "decision", "discussion"}
    required = []
    for pattern, kind in [(r"step.definition|helper", "step_definition"),
                          (r"database|\bdb\b|column|mapping", "database_mapping"),
                          (r"pull request|\bpr\b", "pull_request"),
                          (r"acceptance|\bacs?\b", "requirement")]:
        if re.search(pattern, q): required.append(kind)
    return {"target_types": sorted(kinds), "required_types": required, "max_hops": options.max_hops,
            "max_nodes": options.max_nodes, "direction": "incoming + outgoing"}


def traverse(graph, seeds, plan):
    queue = deque((sid, 0) for sid in seeds if sid in graph)
    depths = {sid: 0 for sid, _ in queue}
    parents = {}
    truncated = False
    while queue:
        node, depth = queue.popleft()
        if depth >= plan["max_hops"]:
            continue
        edges = list(graph.out_edges(node, data=True)) + list(graph.in_edges(node, data=True))
        # Stable deterministic traversal; selection/reranking happens after traversal.
        for source, target, data in sorted(edges, key=lambda e: (e[0], e[1], e[2]["type"])):
            neighbor = target if source == node else source
            if neighbor in depths:
                continue
            if len(depths) >= plan["max_nodes"]:
                truncated = True
                continue
            depths[neighbor] = depth + 1
            parents[neighbor] = {"from": node, "source": source, "target": target, **data}
            queue.append((neighbor, depth + 1))
    return depths, parents, truncated


def dot_graph(graph, highlighted=()):
    """JSON escaping prevents untrusted labels from injecting DOT syntax."""
    out = ['digraph QE { rankdir=LR; node [shape=box,style="rounded,filled",fontname="Arial"];']
    for sid, doc in graph.nodes(data=True):
        color = "#bce9e4" if sid in highlighted else "#e9eff6"
        label = sid + "\n" + doc["source_type"] + (" / synthetic" if doc.get("synthetic") else " / supplied")
        out.append(f'{json.dumps(sid)} [label={json.dumps(label)},fillcolor="{color}"];')
    for source, target, data in graph.edges(data=True):
        out.append(f'{json.dumps(source)} -> {json.dumps(target)} [label={json.dumps(data["type"])}];')
    return "\n".join(out + ["}"])
