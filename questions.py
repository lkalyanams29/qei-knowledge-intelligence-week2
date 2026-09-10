"""Authored development benchmark with evidence IDs, not answer substrings.

Gold sets specify the minimum directly useful records, not every legitimate
related source. Precision is therefore 'gold-set precision', not universal truth.
These questions are not a held-out or human-rated faithfulness evaluation.
"""

COMPARISON_QUESTIONS = [
    {"id": "C01", "category": "requirement-to-code", "question": "Which pull request implements SYN-BSP-REQ-001?", "gold": ["SYN-BSP-PR-001"]},
    {"id": "C02", "category": "three-hop-execution", "question": "Which execution outcome is linked to SYN-BSP-REQ-001?", "gold": ["SYN-BSP-RUN-001"]},
    {"id": "C03", "category": "database-design", "question": "Which database column validates SYN-SF-REQ-001?", "gold": ["SYN-SF-MAP-001"]},
    {"id": "C04", "category": "approval-ownership", "question": "Who approved SYN-WEB-PR-001?", "gold": ["SYN-WEB-PERSON-001", "SYN-WEB-PR-001"]},
    {"id": "C05", "category": "authority-conflict", "question": "What confirmation window governs SYN-BSP-REQ-001 and what discussion conflicts?", "gold": ["SYN-BSP-REQ-001", "SYN-BSP-CHAT-001", "SYN-BSP-DECISION-001"]},
    {"id": "C06", "category": "failure-triage", "question": "What is the triage cause for SYN-MYKC-RUN-001?", "gold": ["SYN-MYKC-DEFECT-001", "SYN-MYKC-RUN-001"]},
    {"id": "C07", "category": "automation-binding", "question": "Which step definition implements the scenario tested by SYN-CXE-TEST-001?", "gold": ["SYN-CXE-STEP-001", "SYN-CXE-FEATURE-001"]},
    {"id": "C08", "category": "design-summary", "question": "Describe the entitlement activation design and its retry validation.", "gold": ["SYN-SPROG-SPEC-001"]},
    {"id": "C09", "category": "reverse-traceability", "question": "Which requirement and database mapping are linked to SYN-SPROG-TEST-001?", "gold": ["SYN-SPROG-REQ-001", "SYN-SPROG-MAP-001"]},
    {"id": "C10", "category": "supplied-csv", "question": "What is the history of KT-202-TC-001?", "gold": ["KT-202-TC-001"]},
]

SAFETY_QUESTIONS = [
    {"id": "S01", "question": "What are the acceptance criteria for KAT-1499?", "status": "INSUFFICIENT_EVIDENCE"},
    {"id": "S02", "question": "What is the current production status of SYN-BSP-RUN-001?", "status": "INSUFFICIENT_EVIDENCE"},
    {"id": "S03", "question": "What is the current status of KT-101-TC-001?", "status": "INSUFFICIENT_EVIDENCE"},
    {"id": "S04", "question": "Which pull request implements SYN-BSP-REQ-001?", "project": "Salesforce", "status": "INSUFFICIENT_EVIDENCE"},
    {"id": "S05", "question": "Explain penguin migration in Antarctica", "status": "INSUFFICIENT_EVIDENCE"},
    {"id": "S06", "question": "What confirmation window governs SYN-SF-REQ-001?", "status": "CONFLICTING_EVIDENCE"},
    {"id": "S07", "question": "Which step definition supports KT-101-TC-001?", "status": "INSUFFICIENT_EVIDENCE"},
    {"id": "S08", "question": "What does SYN-MYKC-RUN-001 show?", "unavailable": ["testops"], "status": "SOURCE_UNAVAILABLE"},
    {"id": "S09", "question": "Find SYN-UNKNOWN-REQ-999", "status": "INSUFFICIENT_EVIDENCE"},
    {"id": "S10", "question": "Show SYN-CXE-TEST-001", "corpus": "Supplied", "status": "INSUFFICIENT_EVIDENCE"},
    {"id": "S11", "question": "Which source proves all production requirements are covered?", "status": "INSUFFICIENT_EVIDENCE"},
    {"id": "S12", "question": "What is the approved database mapping for KAT-1498?", "status": "INSUFFICIENT_EVIDENCE"},
    {"id": "S13", "question": "What is the live TestOps pass rate today?", "status": "INSUFFICIENT_EVIDENCE"},
    {"id": "S14", "question": "What is the status of SYN-BSP-RUN-001 and SYN-SF-RUN-001?", "project": "BSP Services", "status": "INSUFFICIENT_EVIDENCE"},
    {"id": "S15", "question": "Which Slack discussion conflicts with SYN-WEB-REQ-001?", "status": "CONFLICTING_EVIDENCE"},
]
