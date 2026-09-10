# Week 2 evaluation report

25 authored questions run against the same retrieval pipeline plus local Qwen/llama.cpp. Latency includes local model calls and the 6.5-second output-validation fallback, but excludes browser/network-to-site time. Exact quotation support is automatic; semantic faithfulness still requires human review. This is a development set, not a held-out benchmark.

Measured on 2026-09-09T22:01:50.422Z. Corpus b5a546b2573d3262879867b7c19f2745d4f4dea66b13b4a0f3fcdd4fa0a92231.

- status_accuracy: 1
- relevant_source_recall: 1
- correct_refusal: 1
- verbatim_support: 1
- semantic_faithfulness: Not evaluated
- p95_local_ms: 5035.92
- graph_recall: 0.5712683150183151
- vector_recall: 0.4915979853479853

## Per-question results

| Question | Expected | Actual | Relevant-source recall |
|---|---|---|---|
|History of KT-101-TC-001|VERIFIED|VERIFIED|1|
|History of KT-202-TC-001|VERIFIED|VERIFIED|1|
|History of KT-303-TC-001|VERIFIED|VERIFIED|1|
|History of KT-404-TC-001|VERIFIED|VERIFIED|1|
|Which tests executed in RUN-00001?|VERIFIED|VERIFIED|1|
|How many results are in RUN-00002?|VERIFIED|VERIFIED|1|
|What is the BSP testing strategy?|VERIFIED|VERIFIED|1|
|What is the CXE testing strategy?|VERIFIED|VERIFIED|1|
|What is the Salesforce business process testing strategy?|VERIFIED|VERIFIED|1|
|What is the SPROG hybrid testing strategy?|VERIFIED|VERIFIED|1|
|How should I investigate flaky tests?|VERIFIED|VERIFIED|1|
|How do Confluence inherited view restrictions work?|VERIFIED|VERIFIED|1|
|How do Slack conversation scopes affect access?|VERIFIED|VERIFIED|1|
|How can I inspect TestOps execution artifacts?|VERIFIED|VERIFIED|1|
|What are the ACs for KAT-1499?|INSUFFICIENT_EVIDENCE|INSUFFICIENT_EVIDENCE|N/A|
|Which tests cover KAT-1498?|INSUFFICIENT_EVIDENCE|INSUFFICIENT_EVIDENCE|N/A|
|Analyze the DB mapping|INSUFFICIENT_EVIDENCE|INSUFFICIENT_EVIDENCE|N/A|
|Where is the Step Definition for the payment API?|INSUFFICIENT_EVIDENCE|INSUFFICIENT_EVIDENCE|N/A|
|Who approved PR-884?|INSUFFICIENT_EVIDENCE|INSUFFICIENT_EVIDENCE|N/A|
|What is the current status of KT-101-TC-001?|INSUFFICIENT_EVIDENCE|INSUFFICIENT_EVIDENCE|N/A|
|History of KT-101-TC-001|INSUFFICIENT_EVIDENCE|INSUFFICIENT_EVIDENCE|N/A|
|Explain xylophone aardvark nebula|INSUFFICIENT_EVIDENCE|INSUFFICIENT_EVIDENCE|N/A|
|Teach me the CXE user journey testing strategy|VERIFIED|VERIFIED|1|
|What are the MyKC sample portfolio results?|VERIFIED|VERIFIED|1|
|What are the BSP Services sample portfolio results?|VERIFIED|VERIFIED|1|

## Graph versus vector (10 questions)

Recall@6 measures linked test IDs found; a seed run consumes one result slot. Large runs have a ceiling below 100%.

| Question | Graph recall | Vector recall |
|---|---|---|
|Which test cases executed in RUN-00049?|1|1|
|Which test cases executed in RUN-00050?|1|1|
|Which test cases executed in RUN-00051?|0.625|0.375|
|Which test cases executed in RUN-00052?|0.625|0.375|
|Which test cases executed in RUN-00053?|0.4166666666666667|0.4166666666666667|
|Which test cases executed in RUN-00054?|0.7142857142857143|0.5714285714285714|
|Which test cases executed in RUN-00055?|0.3125|0.3125|
|Which test cases executed in RUN-00056?|0.38461538461538464|0.3076923076923077|
|Which test cases executed in RUN-00057?|0.25|0.25|
|Which test cases executed in RUN-00058?|0.38461538461538464|0.3076923076923077|

## Limits

Semantic faithfulness requires human claim review. No LLM faithfulness or hosted P95 claim is made by this run. Unit safety tests use clearly synthetic permission, outage, injection and conflict mutations; those are not included as business evidence. Source ingestion is export-based, not live enterprise synchronization.
