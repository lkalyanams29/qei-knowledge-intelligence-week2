# Week 2 live demo guide

Keep the submitted recording under five minutes. Use only the approved sample corpus, not private tabs, secrets or enterprise records.

1. **0:00–0:30 — Objective and scope.** Show the landing page. Explain that this is the separate Week 2 QE knowledge assistant, with actual retrieval from approved CSV-derived records and design/public notes. Identify absent enterprise integrations.
2. **0:30–1:20 — Answer and provenance.** Ask `Which tests executed in RUN-00001?`. Show the answer, cited records, exact source excerpt, original-source link and dated evidence. Describe the model configuration banner accurately.
3. **1:20–1:50 — Safe fallback.** Ask `What are the ACs for KAT-1499?`. Explain that requirements were not supplied and the app refuses to invent them.
4. **1:50–2:20 — Mentor Mode.** Select CXE, enable Mentor Mode and ask `What is the CXE testing strategy?`. Show the source-backed strategy, learning path and explicitly missing implementation evidence.
5. **2:20–3:00 — Corpus and graph.** Show 254 records, 96-dimensional classical LSA embeddings and recorded test/run relationships. Explain that the graph does not infer Jira coverage from a test name.
6. **3:00–3:45 — Evaluation.** Show 25 authored questions and 10 graph/vector comparisons. Distinguish exact-source support from unmeasured semantic faithfulness. State the measured model/fallback counts from the saved report.
7. **3:45–4:30 — AI workflow and code.** Show the separate repository. Describe using Codex to build in slices, reconcile the CSV, run tests, fix the static prototype and invalid model outputs, and document the remaining integration work.

The report's 95% faithfulness and 8-second P95 are targets. Do not say enterprise APIs are connected or the hosted endpoint uses the laptop's local model. If recording the local LLM demo, keep the model service running and verify the configured-model banner before starting.
