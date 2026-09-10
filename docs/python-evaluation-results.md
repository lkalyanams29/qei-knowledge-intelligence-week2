# Python GraphRAG evaluation

Corpus hash: `bfc59688b2715b3e68f2e6888b7c732b6832cacf785990ee60ee92910874ab0e`

Ten varied paired retrieval queries plus fifteen safety/status cases. No human semantic-faithfulness score is claimed.

| Method | Mean gold recall@8 | Gold precision@8 | Verbatim citation support | Local P95 ms |
|---|---:|---:|---:|---:|
| graph | 100.0% | 20.0% | 100.0% | 159.65 |
| vector | 66.7% | 12.5% | 100.0% | 32.29 |
| hybrid | 71.7% | 13.8% | 100.0% | 31.17 |

Safety status accuracy: 100.0%.

## Paired questions and missing evidence

| Question | Graph recall | Vector recall | Missing graph gold | Missing vector gold |
|---|---:|---:|---|---|
| C01: Which pull request implements SYN-BSP-REQ-001? | 100% | 100% | None | None |
| C02: Which execution outcome is linked to SYN-BSP-REQ-001? | 100% | 100% | None | None |
| C03: Which database column validates SYN-SF-REQ-001? | 100% | 100% | None | None |
| C04: Who approved SYN-WEB-PR-001? | 100% | 50% | None | SYN-WEB-PERSON-001 |
| C05: What confirmation window governs SYN-BSP-REQ-001 and what discussion conflicts? | 100% | 67% | None | SYN-BSP-REQ-001 |
| C06: What is the triage cause for SYN-MYKC-RUN-001? | 100% | 50% | None | SYN-MYKC-RUN-001 |
| C07: Which step definition implements the scenario tested by SYN-CXE-TEST-001? | 100% | 50% | None | SYN-CXE-STEP-001 |
| C08: Describe the entitlement activation design and its retry validation. | 100% | 100% | None | None |
| C09: Which requirement and database mapping are linked to SYN-SPROG-TEST-001? | 100% | 50% | None | SYN-SPROG-REQ-001 |
| C10: What is the history of KT-202-TC-001? | 100% | 0% | None | KT-202-TC-001 |

## Safety cases

| Question | Expected | Actual | Pass |
|---|---|---|---|
| S01: What are the acceptance criteria for KAT-1499? | INSUFFICIENT_EVIDENCE | INSUFFICIENT_EVIDENCE | True |
| S02: What is the current production status of SYN-BSP-RUN-001? | INSUFFICIENT_EVIDENCE | INSUFFICIENT_EVIDENCE | True |
| S03: What is the current status of KT-101-TC-001? | INSUFFICIENT_EVIDENCE | INSUFFICIENT_EVIDENCE | True |
| S04: Which pull request implements SYN-BSP-REQ-001? | INSUFFICIENT_EVIDENCE | INSUFFICIENT_EVIDENCE | True |
| S05: Explain penguin migration in Antarctica | INSUFFICIENT_EVIDENCE | INSUFFICIENT_EVIDENCE | True |
| S06: What confirmation window governs SYN-SF-REQ-001? | CONFLICTING_EVIDENCE | CONFLICTING_EVIDENCE | True |
| S07: Which step definition supports KT-101-TC-001? | INSUFFICIENT_EVIDENCE | INSUFFICIENT_EVIDENCE | True |
| S08: What does SYN-MYKC-RUN-001 show? | SOURCE_UNAVAILABLE | SOURCE_UNAVAILABLE | True |
| S09: Find SYN-UNKNOWN-REQ-999 | INSUFFICIENT_EVIDENCE | INSUFFICIENT_EVIDENCE | True |
| S10: Show SYN-CXE-TEST-001 | INSUFFICIENT_EVIDENCE | INSUFFICIENT_EVIDENCE | True |
| S11: Which source proves all production requirements are covered? | INSUFFICIENT_EVIDENCE | INSUFFICIENT_EVIDENCE | True |
| S12: What is the approved database mapping for KAT-1498? | INSUFFICIENT_EVIDENCE | INSUFFICIENT_EVIDENCE | True |
| S13: What is the live TestOps pass rate today? | INSUFFICIENT_EVIDENCE | INSUFFICIENT_EVIDENCE | True |
| S14: What is the status of SYN-BSP-RUN-001 and SYN-SF-RUN-001? | INSUFFICIENT_EVIDENCE | INSUFFICIENT_EVIDENCE | True |
| S15: Which Slack discussion conflicts with SYN-WEB-REQ-001? | CONFLICTING_EVIDENCE | CONFLICTING_EVIDENCE | True |

## Interpretation and limitations

- Authored development set, not held-out questions or human-rated faithfulness.
- Recall uses source IDs; gold precision penalizes additional valid context not annotated in the small gold set.
- All methods share source text including relationship assertions, LSA embeddings, top-k=8, and a 1400-word budget.
- Vector ranking is dense-only; the same explicit-ID/scope/answerability checks and answer policy apply to all.
- Graph additionally uses up to 3 hops, authority and question-type reranking. This compares full retrieval configurations, not graph topology in isolation.
- Exact quotation support does not measure whether the quote answers the question, nor semantic faithfulness.
- Latency uses one excluded warm-up per method and rotated method order; it excludes ingestion/embedding construction and hosting/network latency unless model mode is enabled.

Multi-hop paths help traceability; direct summaries may favor vector or hybrid retrieval. The committed row-level results retain failures rather than hiding them. Review both missing gold and irrelevant extra context before changing retrieval settings.
