# QEI Knowledge Intelligence — Week 2 GraphRAG

A Python/Streamlit QE knowledge assistant over supplied and **explicitly synthetic** source records. It follows the module structure of the [Gen Academy GraphRAG reference](https://github.com/The-Gen-Academy/2C-Graph-RAG-for-Organizational-Knowledge), with original QE-domain data and a new implementation of the safety and retrieval improvements.

**No live enterprise connectors are configured.** Jira, Confluence, SharePoint, Bitbucket, Slack, Katalon assets and TestOps are represented by file exports. Synthetic artifacts never establish real requirements, production status or coverage of the supplied CSV.

## Run the Python app

Tested with Python 3.12. No API key is needed for the default cited-excerpt mode.

```sh
python -m venv .venv
# Windows PowerShell: ./.venv/Scripts/Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m data.mock_data
python -m data.mcp_documents
python scripts/ingest.py
python -m streamlit run ui.py
```

Open the local URL printed by Streamlit. The first launch also builds the index if missing, from the included files only. Subsequent questions use the saved index; they do not retrieve or re-embed source history.

Try:

- `Which execution outcome is linked to SYN-BSP-REQ-001?` — three-hop requirement → feature → test → execution.
- `What confirmation window governs SYN-BSP-REQ-001 and what discussion conflicts?` — approved requirement versus stale Slack proposal.
- `Which step definition implements the scenario tested by SYN-CXE-TEST-001?` — automation binding.
- `Which database column validates SYN-SF-REQ-001?` — database mapping.
- `What is the history of KT-202-TC-001?` — original CSV evidence.
- `What are the acceptance criteria for KAT-1499?` — explicit missing-evidence fallback.

Ask QE supports paired GraphRAG/vector answers, source citations, authority/freshness labels, conflict disclosure, and a stage-by-stage trace. Mentor Mode provides a project-specific review checklist, not invented facts. Corpus, Evidence graph and Evaluation tabs expose the actual inputs and measured results. Answers survive Streamlit widget reruns.

## Repository structure

```text
data/
  mock_data.py          deterministic synthetic-data generator
  synthetic/*.json     seven source types across six projects
  mcp_documents.py     richer Jira/Confluence/SharePoint fixture generator
  mcp_samples/         normalized exports + human-readable Markdown documents
  index.json           generated local index; ignored by Git
graph_builder.py       NetworkX graph, entity linking, ACL filters, traversal
graph_rag.py           staged LangGraph workflow and citation policy
vector_rag.py          FAISS dense retrieval and BM25/hybrid baseline
llm.py                 optional constrained LangChain model selection
questions.py           10 varied comparison questions + 15 safety cases
compare.py             reproducible evaluation and reports
ui.py                  Streamlit application
settings.py            scope, freshness and bounded query options
logging_config.py      redacted structured operational logs
scripts/ingest.py      source validation, chunking, embedding snapshot
sources/               unchanged supplied CSV, design notes, public summaries
config/                project profiles
tests/                 ingestion, retrieval, safety and Streamlit AppTest tests
docs/                  project report, evaluation, deployment and limitations
legacy/sites/          preserved earlier React/Worker version; not the active app
```

The primary app uses **Python + LangGraph + NetworkX + FAISS + Streamlit**, as requested. It does not require the old Node/pnpm workflow. The prior React version and its hosting manifest are preserved under `legacy/sites/`; its existing chatgpt.site deployment is unchanged. That hosting runtime cannot directly run a Streamlit Python server. See [Python deployment](docs/deployment.md).

## Datasets and provenance

| Input | Records | Meaning |
|---|---:|---|
| Supplied Katalon CSV | 2,063 result rows → 244 documents | 144 tests, 96 runs, 4 project summaries; May 26–August 15, 2026 |
| User design notes | 6 project profiles | Design intent, not approved implementation evidence |
| Public documentation summaries | 4 documents | Tool guidance, not enterprise integration |
| Original synthetic exports | 72 documents, 90 links | 12 fictional artifacts for each of six projects |
| Native-MCP documentation fixtures | 36 documents, 60 links | 12 Jira issues, 12 Confluence pages, 12 SharePoint documents |
| Combined index | 362 documents / chunks, 4,420 recorded links | 108 synthetic records; provenance and datasets remain distinct |

Synthetic projects: BSP Services, Salesforce, WebOps, MyKC, CXE and SPROG. The seven source types include invented requirements, designs, database mappings, pull requests, step definitions, Gherkin features, test cases, executions, discussions, decisions, owners and triage records. All invented people, outcomes and schemas are labeled fictional. Source URLs point to actual JSON or Markdown source files in this repository, not fake Jira or Slack URLs. Synthetic IDs use the `SYN-` namespace; no synthetic links are attached to actual CSV test IDs.

The additional Jira, Confluence and SharePoint collection includes four acceptance criteria per story, defect reproduction and expected outcomes, designs, runbooks, test strategies and pending release checklists. It is available as normalized JSON plus readable Markdown. It assumes **future native MCP connections**, but its metadata is a QEI-owned mapping contract, not an alleged vendor response. Endpoints/tool bindings remain unconfigured. Native-style synthetic issue keys such as `SYNBSP-201` resolve to the appropriate authorized source. See the [native MCP data guide](docs/native-mcp-data-guide.md).

## Retrieval and safety improvements

1. Validate identifiers, source type, authority, dates, scope, duplicate records and relationship evidence. Reject public-to-private links that would disclose restricted targets.
2. Chunk within document boundaries: 240 words with 35-word overlap. Fit 96-dimensional TF-IDF/LSA embeddings, preserving the projection for queries. This is classical corpus-trained dense embedding, **not a pretrained transformer**.
3. Filter project, dataset, source availability, permissions and quarantined documents **before** FAISS ranking or graph traversal. The public demo grants no private scopes; project filters never authorize access.
4. Use exact IDs and unique quoted titles. Unknown IDs abstain; ambiguous titles ask for clarification. No fuzzy first-match entity guessing.
5. Traverse incoming/outgoing relationships up to 3 hops and 36 nodes. Rank target artifact types, relevance, authority and freshness. Attach original source text independently of relationship-type filters.
6. Both graph and vector paths use the same chunks, including relationship assertions, and the same maximum 8 context records / 1,400 words. The vector baseline ranks only dense cosine similarity; graph uses hybrid seeding plus traversal/reranking. Shared scope and answerability checks apply to both.
7. Return exact cited spans, disclose conflicts and partial sources, and refuse unsupported current-production conclusions. Evidence quality is a heuristic, not calibrated confidence.
8. Optional model selection accepts only validated integer indices pointing to source spans. Invalid output or timeout falls back visibly to excerpts. No unconstrained model-authored factual prose is displayed.

Limits: heuristic intent matching, English tokenization, small authored corpus, no live synchronization or real enterprise SSO, no independently measured semantic faithfulness, and possible irrelevant extra context. Prompt-injection pattern quarantine is defense-in-depth, not a complete detector. See [corpus contract](docs/corpus-contract.md) and [project report](docs/project-report.md).

## Import authorized exports

Use the normalized JSON schema in [data/synthetic/bsp.json](data/synthetic/bsp.json) as a structural example, but **do not label real data synthetic**. Each relationship must have an existing target, source ID and exact source-supported quote. Set an appropriate access scope; restricted targets require scope inheritance. No automatic relationship inference is performed.

```sh
python scripts/ingest.py --extra sources/private/approved-export.json --output work/private-index.json
```

The extra export and private output are ignored by Git. Set `QEI_CORPUS_PATH` in an ignored `.env` to use that index locally. The shipped anonymous UI still denies restricted records; authenticated enterprise deployment requires a trusted server-side identity adapter, not a client-side project grant selector. Do not publish private corpora, derived summaries or indexes to this public repository.

## Optional model

Copy `.env.example` to ignored `.env` and configure `QEI_MODEL_BASE_URL`, `QEI_MODEL_NAME`, and optionally `QEI_MODEL_API_KEY`. Use only an approved OpenAI-compatible endpoint supporting structured JSON-schema responses. Restart the app and opt in using its model checkbox. No paid endpoint is automatically chosen; no model call is made in default mode. Environment loading occurs before the UI checks configuration. External tracing should remain disabled for sensitive evidence.

The previous local Qwen experiment belongs to the legacy version. The Python adapter is covered with deterministic fake-provider tests; a live model-inclusive evaluation must be run separately with `python compare.py --model --output docs/python-model-evaluation.json` after endpoint approval/configuration. Do not mistake mock tests for a live provider benchmark.

## Validate and evaluate

```sh
python -m unittest discover -s tests -p "test_*.py" -v
python compare.py
python -m pip check
```

See [paired evaluation and failures](docs/python-evaluation-results.md). With the expanded corpus, the recorded 10-question development set produced graph source recall@8 of 100%, vector 66.7%, and hybrid 71.7%; all 15 safety/status cases passed. Gold-set precision is much lower because up to eight records are returned and the gold sets contain only minimum required sources. Verbatim citation support is measured separately; **the ≥95% semantic faithfulness objective is not yet independently measured**. Timings and corpus hash are included in the generated report.

## Deliverables

- [Project report: prompts, iterations and learnings](docs/project-report.md)
- [Reference alignment and implemented changes](docs/reference-enhancements.md)
- [Synthetic documentation and native MCP mapping guide](docs/native-mcp-data-guide.md)
- [Python deployment instructions](docs/deployment.md)
- [Current submission status](docs/submission-status.md)

The existing video in `demo/` demonstrates the earlier React version. It is a narrated screenshot draft, not a current Streamlit live-demo recording. A new ≤5-minute live recording remains to be made; the [demo guide](docs/demo-guide.md) describes the current flow.
