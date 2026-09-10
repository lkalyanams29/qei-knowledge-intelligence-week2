# Week 2 live demo guide

Keep the submitted recording under five minutes. Use only the approved sample corpus, not private tabs, secrets or enterprise records.

1. **0:00–0:30 — Objective and scope.** Show the actual Streamlit app. Explain the separate Week 2 QE assistant and its Python/LangGraph/NetworkX/FAISS architecture. Identify the synthetic banner and absence of live enterprise connections.
2. **0:30–1:20 — Three-hop answer and provenance.** Ask `Which execution outcome is linked to SYN-BSP-REQ-001?` with comparison enabled. Show the fictional run outcome, source export and workflow trace. Explain requirement → feature → test → execution.
3. **1:20–2:00 — Authority conflict.** Ask `What confirmation window governs SYN-BSP-REQ-001 and what discussion conflicts?`. Show the approved 30-second decision versus the stale 15-second Slack proposal. Both are fictional records.
4. **2:00–2:30 — Safe fallback.** Ask `What are the acceptance criteria for KAT-1499?`. Show refusal. Explain why synthetic data and old executions cannot prove current production state.
5. **2:30–3:05 — Corpus and graph.** Show 326 source records, including 72 synthetic records. Explore the BSP requirement and highlight retrieved nodes. Change the graph control and return to the retained answer. Briefly show Mentor Mode's review checklist.
6. **3:05–3:45 — Evaluation.** Show 10 varied paired comparisons and 15 safety cases. Distinguish source recall and exact quotation support from unmeasured semantic faithfulness. Discuss one vector retrieval miss and low gold-set precision.
7. **3:45–4:30 — AI workflow and code.** Show the separate repository's reference-shaped Python files. Describe using Codex to review the example, clarify the migration, generate fictional linked data, implement the pipeline, fix date handling and test the UI. State the remaining live-connectors, identity and human-evaluation work.

The report's 95% faithfulness target is not a measured certification. Do not say enterprise APIs are connected or the old chatgpt.site URL runs this Python version. Default excerpt mode uses no model; optional model mode must be configured and verified separately. The existing `demo/QEI_Week2_Walkthrough_Draft.mp4` is an older React screenshot-narration draft, not this Streamlit live recording. Record the current application continuously and keep the submission under five minutes.
