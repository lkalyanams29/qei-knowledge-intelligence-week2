"""Streamlit entry point, following the academy reference's Python structure."""
from __future__ import annotations

from collections import Counter
import json
import os
import streamlit as st

from graph_builder import build_graph, dot_graph, eligible_documents, load_corpus
from graph_rag import GraphRAG
from llm import model_configured
from logging_config import configure_logging
from questions import COMPARISON_QUESTIONS
from settings import ROOT, QueryOptions, index_path

st.set_page_config(page_title="QEI Knowledge Intelligence", page_icon="🔎", layout="wide")


@st.cache_resource(show_spinner="Loading the approved evidence corpus…")
def load_engine(path, modified):
    del modified  # Part of the cache key: changes invalidate the cached engine.
    return GraphRAG(load_corpus(path))


def result_panel(result, heading):
    st.subheader(heading)
    status = result["status"]
    message = status.replace("_", " ").title()
    if status == "EVIDENCE_FOUND":
        st.success(message)
    elif status in {"CONFLICTING_EVIDENCE", "SOURCE_UNAVAILABLE"}:
        st.warning(message)
    else:
        st.info(message)
    st.caption(f"Asked in {result['project']} · {result['corpus']} corpus · {result['generation']} · {result['latency_ms']:.0f} ms")
    if result["reason"]:
        st.write(result["reason"])
    if result["synthetic"]:
        st.caption("SYNTHETIC EVIDENCE — fictional demo records, not enterprise facts.")
    st.caption(f"Evidence quality: {result['evidence_quality']}/100. {result['quality_note']}")
    for number, claim in enumerate(result["claims"], 1):
        st.text(f"[{number}] {claim['quote']}")
        st.markdown(f"[{claim['source_id']}]({claim['url']})")
    for conflict in result["conflicts"]:
        with st.expander(f"Conflicting field: {conflict['field']}", expanded=True):
            st.write("Preferred source: "+conflict["preferred_source_id"])
            st.caption(conflict["reason"])
            st.dataframe(conflict["sources"], hide_index=True, width="stretch")
    with st.expander("Source evidence and citations"):
        for item in result["evidence"]:
            st.write(item["source_id"]+" · "+item["title"])
            st.caption(f"{item['source_type']} · L{item['authority']} authority · {item['approval_status']} · {item['freshness']} · updated {item['updated_at'] or 'unknown'} · hop {item['hop'] if item['hop'] is not None else '—'}")
            st.text(item["content"])
            st.markdown(f"[Open original source export]({item['url']})")
            if item["source_rows"]:
                st.caption("CSV row provenance: "+", ".join(map(str, item["source_rows"])))
    with st.expander("Retrieval workflow trace"):
        for step in result["trace"]:
            st.json(step, expanded=False)


def main():
    configure_logging()
    st.title("QEI Knowledge Intelligence")
    st.caption("Requirements → implementation → automation → execution evidence")
    st.info("Demo corpus: supplied TestOps sample + design notes + public documentation + 72 clearly labeled synthetic records. No live Jira, Confluence, SharePoint, Bitbucket, Slack, Katalon or TestOps connection.")
    path = index_path()
    if not path.exists():
        if path != ROOT/"data/index.json":
            st.error("The configured corpus file is unavailable. Contact the application owner.")
            return
        with st.spinner("Building the local index from the included sample files…"):
            from scripts.ingest import build
            build()
    engine = load_engine(path, path.stat().st_mtime_ns)
    corpus = engine.corpus
    with st.sidebar:
        st.header("Evidence scope")
        project = st.selectbox("Project", ["All", *sorted(corpus["profiles"])], key="project")
        source_set = st.selectbox("Corpus", ["All", "Synthetic", "Supplied"], key="corpus")
        hops = st.slider("Maximum graph hops", 1, 3, 3)
        st.caption("At most 36 traversed nodes, 8 context records and 1,400 context words per answer.")
        with st.expander("Simulate source outage"):
            unavailable = st.multiselect("Unavailable source types", ["jira", "confluence", "sharepoint", "bitbucket", "slack", "katalon", "testops"])
            st.caption("This simulates missing source evidence; it does not disconnect a live service.")
        use_model = st.checkbox("Use configured model to select evidence", disabled=not model_configured())
        st.caption("No API key needed for excerpt mode. Model mode sends authorized candidate spans only to your configured endpoint.")
        st.caption("Public demo: private project scopes are denied. A project filter never grants access.")
    options = QueryOptions(project=project, corpus=source_set, max_hops=hops,
                           unavailable=frozenset(unavailable), use_model=use_model)
    documents = eligible_documents(corpus, options)
    graph = build_graph(documents)
    ask_tab, corpus_tab, graph_tab, eval_tab = st.tabs(["Ask QE", "Corpus", "Evidence graph", "Evaluation"])

    with ask_tab:
        mode = st.radio("Answer mode", ["Ask QE", "Mentor Mode"], horizontal=True)
        example = st.selectbox("Example question", [q["question"] for q in COMPARISON_QUESTIONS], key="example")
        if st.button("Use example"):
            st.session_state["question"] = example
        st.session_state.setdefault("question", COMPARISON_QUESTIONS[0]["question"])
        with st.form("ask_form"):
            question = st.text_area("Your QE question", key="question", max_chars=2000)
            comparison = st.checkbox("Compare GraphRAG with vector retrieval", value=True)
            submitted = st.form_submit_button("Ask QE", type="primary")
        if submitted:
            try:
                with st.spinner("Retrieving source-backed evidence…"):
                    results = {"graph": engine.answer(question, options)}
                    if comparison:
                        results["vector"] = engine.answer(question, options, "vector")
                st.session_state["results"] = results
            except (ValueError, OSError) as error:
                st.error("The question could not be processed. Check the question and local corpus configuration.")
                st.session_state.pop("results", None)
        results = st.session_state.get("results")
        if results:
            columns = st.columns(len(results))
            for column, (method, result) in zip(columns, results.items()):
                with column:
                    result_panel(result, "GraphRAG" if method == "graph" else "Vector baseline")
            if mode == "Mentor Mode":
                with st.expander("QE review checklist", expanded=True):
                    profile = corpus["profiles"].get(results["graph"]["project"], {})
                    st.write("Suggested learning activity—not additional factual evidence.")
                    st.write("Strategy: "+profile.get("strategy", "Select one project to use its design-note strategy."))
                    for check in profile.get("checks", ["Requirement", "Implementation", "Coverage", "Execution", "Missing evidence"]):
                        st.write("• "+check+": identify the supporting citation or mark the evidence missing.")
                    st.write("Explain why an earlier Slack proposal should not override an approved requirement. What source would you ask the QE owner for next?")
            st.download_button("Download answer, citations and trace", json.dumps(results, indent=2),
                               "qei-answer.json", "application/json")

    with corpus_tab:
        columns = st.columns(4)
        columns[0].metric("Accessible records", len(documents))
        columns[1].metric("Synthetic records", sum(bool(d.get("synthetic")) for d in documents.values()))
        columns[2].metric("Recorded relationships", graph.number_of_edges())
        columns[3].metric("Supplied CSV results", corpus["stats"]["rows"])
        st.caption("CSV result count always refers to the original supplied file; synthetic runs are never added to it.")
        counts = Counter((d["source_type"], "Synthetic" if d.get("synthetic") else "Supplied/public notes") for d in documents.values())
        st.dataframe([{"Source": source, "Dataset": dataset, "Records": count, "Connection": "File snapshot, not live"}
                      for (source, dataset), count in sorted(counts.items())], hide_index=True, width="stretch")
        search = st.text_input("Find source records")
        records = [d for d in documents.values() if search.lower() in (d["id"]+" "+d["title"]).lower()]
        st.dataframe([{"ID": d["id"], "Title": d["title"], "Project": d["project"], "Source": d["source_type"],
                       "Synthetic": d.get("synthetic", False), "Authority": d["authoritative_level"], "Updated": d["updated_at"]}
                      for d in records], hide_index=True, width="stretch")

    with graph_tab:
        if documents:
            seeds = sorted(documents, key=lambda sid: (not sid.startswith("SYN-"), sid))
            seed = st.selectbox("Explore a source record", seeds)
            from graph_builder import traverse
            depths, _, _ = traverse(graph, [seed], {"max_hops": hops, "max_nodes": 36})
            highlight = st.checkbox("Highlight last retrieved evidence", value=True)
            selected_ids = {e["source_id"] for e in st.session_state.get("results", {}).get("graph", {}).get("evidence", [])} if highlight else set()
            st.graphviz_chart(dot_graph(graph.subgraph(depths), selected_ids), width="stretch")
            st.caption("Arrows show recorded relationship direction. Retrieval can traverse either direction. Every displayed node passes the active source and access filters.")
        else:
            st.info("No source records are available in this scope.")

    with eval_tab:
        report_path = ROOT/"docs/python-evaluation-results.json"
        if not report_path.exists():
            st.info("Run python compare.py to generate the paired evaluation report.")
        else:
            report = json.loads(report_path.read_text(encoding="utf-8"))
            if report["corpus_hash"] != corpus["corpus_hash"]:
                st.warning("This evaluation used an older corpus. Regenerate it before comparing scores.")
            st.subheader("Same evidence, different retrieval")
            st.dataframe([{"Method": method, **values} for method, values in report["summary"].items()], hide_index=True, width="stretch")
            st.write(f"{report['comparison_queries']} varied comparison queries · {report['safety_queries']} safety cases · safety status accuracy {report['safety_status_accuracy']:.1%}")
            st.warning("≥95% semantic faithfulness is a project target, not a measured result. Exact quotation support is not the same as answering correctly.")
            with st.expander("Question-level results and failures"):
                st.json(report, expanded=False)
            st.download_button("Download evaluation report", report_path.read_bytes(), report_path.name, "application/json")


if __name__ == "__main__":
    main()
