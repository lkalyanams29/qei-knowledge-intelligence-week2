# QEI Knowledge Intelligence

A separate Week 2 project: a working, source-backed QE question-answering workspace with reproducible ingestion, classical dense embeddings, hybrid retrieval, recorded graph relationships, citations, safe abstention, and an optional constrained LLM answer step.

This is independent of the Week 1 automation dashboard. It does **not** claim live access to Jira, Confluence, SharePoint, Bitbucket, Slack, Katalon repositories, or TestOps APIs. The UI explicitly identifies missing sources.

## One liner

My RAG app helps Quality Engineers and new team members answer test-history, project-strategy, and QE-tool questions from 254 records derived from a supplied Katalon CSV, project architecture notes, and four public-documentation summaries in a web workspace, targeting at least 95% grounded semantic faithfulness and an 8-second P95 answer time.

Those are targets, not certification. Automatic exact-quotation support is measured separately from human semantic faithfulness.

## Try it

Prerequisites: Node.js 22.13+, pnpm, Python 3.10+ with NumPy. The committed index allows running the app without rebuilding embeddings.

```sh
pnpm install --frozen-lockfile
pnpm dev --port 3012
```

Open `http://localhost:3012`. Try:

- `Which tests executed in RUN-00001?` — recorded run-to-test relationships.
- `History of KT-202-TC-001` — Salesforce source history.
- `What is the CXE testing strategy?` — design-note provenance, not an implementation claim.
- `What are the ACs for KAT-1499?` — refuses because requirements were not supplied.
- `What is the current status of KT-101-TC-001?` — dated executions cannot establish today's status.

Ask QE and Mentor Mode share the same retrieval and citation policy. Corpus and Evidence graph views reveal exactly what was indexed. Evaluation shows measured results rather than fabricated scores. A page-level `ask_qe` WebMCP action invokes the same visible workflow.

## Real model generation

By default the app returns exact cited excerpts. To activate the LLM step, put these values in an ignored `.dev.vars` file and restart development:

```dotenv
QEI_MODEL_BASE_URL=http://127.0.0.1:8092/v1
QEI_MODEL_NAME=qei-local
QEI_MODEL_API_KEY=
QEI_TRUST_SITES_IDENTITY=false
```

The OpenAI-compatible endpoint must support structured JSON-schema outputs. The model selects up to four candidate source spans. The server validates the selected indices and returns the corresponding exact text and citations; it never accepts model-authored factual prose. A 6.5-second timeout or invalid output triggers a visibly labeled extractive fallback.

For the recorded experiment, Qwen2.5-0.5B-Instruct Q4_K_M ran through the official llama.cpp Windows CPU runtime. Download into ignored local work files:

```powershell
./scripts/download-local-model.ps1
./work/local-model/runtime/llama-server.exe -m ./work/local-model/qwen2.5-0.5b-instruct-q4_k_m.gguf --host 127.0.0.1 --port 8092 -c 4096 -t 4 --parallel 1
```

Model weights and executables are **not** in GitHub. For hosted generation, configure the three model environment values in the host's secret settings with an approved reachable endpoint. A laptop's localhost address will not work from the hosted application. Hosted default mode is source-excerpt answering until configured; no paid endpoint is selected automatically.

## Rebuild and evaluate

```sh
python -m pip install -r requirements.txt
python scripts/ingest.py
python -m unittest discover -s tests -p 'test_*.py'
pnpm test
pnpm evaluate
pnpm typecheck
pnpm build
```

Set `QEI_MODEL_BASE_URL`, `QEI_MODEL_NAME`, and optionally `QEI_MODEL_API_KEY` in the shell before `pnpm evaluate` to produce the separate model-inclusive report. Evaluation does not read `.dev.vars` automatically. An eval run overwrites its report with measured results, not expected values.

## Data and architecture

```text
Approved CSV + design profiles + public notes + optional normalized exports
  → Python validation, cleaning, deduplication, provenance
  → 240-word document windows with 35-word overlap
  → TF-IDF → corpus-trained 96-dimensional LSA vectors
  → immutable server-side JSON document, vector and graph index
  → scope filter → BM25 + vector fusion → authority/freshness ranking
  → optional one-hop graph expansion → top 6 records
  → exact evidence spans → optional LLM selection → validated citations
  → Ask QE / Mentor Mode / Corpus / Graph / Evaluation
```

LSA is a real classical dense semantic representation fitted to this corpus, not a pretrained transformer embedding. Its vocabulary and projection are stored with the index and reused for queries. It is an inexpensive, reproducible POC choice with limited generalization; unseen vocabulary and paraphrases can fail.

The original CSV has 2,063 results, 144 distinct test IDs, 96 runs, and four projects, observed May 26–August 15, 2026. Normalization produces 144 test histories, 96 run records, four portfolio records, six design profiles, and four public-documentation summaries: 254 documents/chunks and 4,270 directed links. See [corpus contract](docs/corpus-contract.md).

The index lives only in server code. Browser responses omit vectors and token statistics. The graph follows recorded test/run links; it does not invent Jira-to-code-to-test coverage.

## Import future source exports

Add approved metadata-normalized exports under ignored `sources/private/`, following [the schema](docs/corpus-contract.md), then rebuild:

```sh
python scripts/ingest.py --extra sources/private/approved-export.json --output work/private-index.json
```

Review ACLs, inherited restrictions, provenance, and derived summaries before deploying to a private environment. **Never replace the public repository's index with private material or push private indexes.** The public source tree and its generated artifacts must contain only publication-approved data. This POC is not a production multi-tenant security boundary.

For another approved monthly CSV, preserve the previous source file, supply a merged file using the same schema, and rebuild. Exact duplicate execution IDs are ignored; conflicting duplicates fail. Ingestion is explicit and snapshot-based, not scheduled. The Week 1 dashboard's interactive CSV importer is a different project.

## Evaluation and known limits

- 25 authored development questions: 100% expected-status accuracy, specified-source recall, correct refusal, and exact quotation support in the recorded run. The set was used while developing and is not a held-out benchmark.
- 10 identical relationship queries: mean linked-test recall@6 was 57.1% for graph-assisted retrieval and 49.2% for the vector baseline. The seed consumes one result slot, and many runs have more tests than the limit.
- Latest local model experiment: 17 validated LLM selections, no extractive fallbacks, and 8 pre-generation refusals. P95 including the local model was about 5.04 seconds, excluding the browser and hosting network. An earlier run had 6 timeouts/validation fallbacks; performance varies.
- Semantic faithfulness and production P95 are not measured. Exact support alone does not establish contextual relevance, completeness, or correctness of the source.
- 14 JavaScript tests and 5 Python tests cover retrieval, answer relevance, citation validation, input validation, project scope, permissions, stale data, conflicts, source outage, injection quarantine and ingestion.
- No live connectors, scheduler, enterprise identity provisioning, source-owner adjudication workflow, or automatic production access revocation is implemented.
- Prompt-injection quarantine is a limited pattern detector, not a complete defense. Quote-only generation and server-side scope filters reduce risk but do not replace a security review.

Reports: [baseline evaluation](docs/evaluation-report.md), [model evaluation](docs/evaluation-llm-report.md), [project documentation](docs/project-report.md), [demo guide](docs/demo-guide.md).

Private application: [QEI Week 2 workspace](https://qei-knowledge-intelligence-week2.lkalyanams.chatgpt.site). Owner sign-in is required. This separate Week 2 site does not change the Week 1 site's name or access.

Demo aid: [4-minute AI-narrated screenshot walkthrough](demo/QEI_Week2_Walkthrough_Draft.mp4), captured from actual local app interactions. This edited screenshot video is not the final continuous live recording required by the handout. Its narration and scene metadata are in `demo/walkthrough-manifest.json`; [submission status](docs/submission-status.md) identifies the remaining Google Doc and live-recording steps.

## Project layout

| Location | Responsibility |
|---|---|
| `scripts/ingest.py` | validation, cleaning, chunking, embedding, graph snapshot |
| `lib/engine.mjs` | retrieval, freshness, conflicts, evidence composition, model adapter |
| `lib/service.mjs` | request validation and trusted server identity mapping |
| `app/api/` | HTTP endpoints for answers, corpus metadata and evaluation |
| `app/Workspace.tsx` | interactive React workspace |
| `config/projects.json` | explicit project types, aliases and strategies |
| `sources/` | publication-approved source material and attribution |
| `tests/` | executable safety and ingestion checks |
| `docs/` | methodology, evaluation data and submission documentation |

The code-heavy track uses Python and JavaScript primitives rather than LangChain/LangGraph. The handout permits other frameworks. The optional graph extension meets the 20-node and 10-query comparison scope on execution relationships, but does not model real people or approval decisions that were never provided.
