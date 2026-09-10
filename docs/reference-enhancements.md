# Reference alignment and enhancements

Reference reviewed: [The Gen Academy — GraphRAG for Organizational Knowledge](https://github.com/The-Gen-Academy/2C-Graph-RAG-for-Organizational-Knowledge/tree/b9bae00d35769cb1408f02634940acc1639a4034), pinned to commit `b9bae00d35769cb1408f02634940acc1639a4034`.

The user explicitly chose to adopt its Python/Streamlit structure. This implementation follows its recognizable module responsibilities, not its organization-specific mock facts. No reference source files, diagrams or bundled third-party JavaScript were copied.

| Reference idea / review finding | QEI implementation |
|---|---|
| `data/mock_data.py` | Deterministic fictional QE corpus: 72 records, seven source types, six projects, 90 source-supported links |
| `graph_builder.py` / NetworkX | Validated directed graph, exact IDs, unique quoted titles, bidirectional traversal |
| `graph_rag.py` / LangGraph | Explicit authorize, link, retrieve, expand, attach, generate stages with conditional refusal routes |
| `vector_rag.py` / FAISS | Dense vector baseline plus BM25 fusion over the same chunks/facts |
| `llm.py` | Optional LangChain structured evidence selector, bounded timeout, no retries, validated citations, visible fallback |
| `ui.py` / Streamlit | Side-by-side answers, graph visualization, source inventory, trace, project context and persistent result state |
| `questions.py`, `compare.py` | Ten varied evidence-retrieval comparisons plus fifteen safety/status questions and generated reports |
| Hard-coded two-hop traversal misses longer paths | Configurable 1–3 hops with node and context budgets; regression test for a three-hop execution path |
| Node-only vector corpus excludes graph relationships | Relationship assertions are embedded in source text available to both retrieval methods |
| Relation filtering can suppress document attachment | Candidate node traversal and provenance attachment are separate stages; directly attach selected source chunks |
| Substring answer scores can reward wrong/negated prose | Score retrieved source IDs against annotated gold; measure exact citation validity separately; do not claim semantic faithfulness |
| Fuzzy first-match entity links can choose the wrong record | Exact identifiers, unique quoted aliases, explicit ambiguity fallback |
| No enterprise scope enforcement | Fail-closed normalized scopes before search/traversal; anonymous demo cannot grant itself private access |
| Graph facts treated as unquestioned truth | Distinguish authority, age, synthetic provenance and conflicting structured facts |
| UI answers disappear on widget reruns | Store completed answers in Streamlit session state; AppTest changes graph highlighting and verifies retention |
| Environment is loaded after key checks | Load `.env` before model configuration checks; no key required for excerpt mode |
| Broad dependency lower bounds | Full tested dependency pins, isolated environment, compatibility check |

## Intentional differences

- NumPy TF-IDF/LSA provides deterministic local dense embeddings instead of requiring a paid external embedding endpoint. FAISS performs actual vector retrieval. This has limited vocabulary/paraphrase generalization and is not a transformer model.
- Streamlit's Graphviz renderer is used instead of PyVis/CDN scripts. The graph and highlighted retrieved nodes remain inspectable without vendoring browser libraries.
- No free-form LLM answer is trusted. Exact span selection preserves verifiable provenance, but can be less fluent and does not automatically guarantee answer relevance.
- No real Jira/Confluence/Slack/Bitbucket/SharePoint connectors or enterprise identity adapters are claimed. Approved exports use a reusable normalized ingestion contract.
- The prior Sites/React implementation is archived rather than deleted or silently replaced with an incompatible Python deployment.

## Remaining enterprise work

Add approved connector credentials and source-specific pagination, incremental synchronization, deletion handling and source ACL inheritance; implement trusted identity-to-project grants; evaluate on real authorized QE questions with independently rated claim-level faithfulness; calibrate fallback thresholds; review paraphrase/alias coverage; and measure latency on the chosen Python host. The current demo intentionally cannot establish today's production state from synthetic evidence.
