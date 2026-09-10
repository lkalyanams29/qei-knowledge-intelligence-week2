"""Deterministic, fictional cross-source QE stories. No enterprise APIs are called.

Run python -m data.mock_data to regenerate reviewable JSON source exports.
The file/module name mirrors the academy reference; the content is original.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = "https://github.com/lkalyanams29/qei-knowledge-intelligence-week2/blob/main/"
SCENARIOS = [
    ("BSP", "BSP Services", "payment idempotency", "duplicate payment rejection", "payments.idempotency_key", "Mira Chen", "FAILED", "environment certificate expired"),
    ("SF", "Salesforce", "opportunity approval", "manager approval before close", "opportunity.approval_status", "Owen Shah", "PASSED", "none recorded"),
    ("WEB", "WebOps", "checkout recovery", "cart recovery after session timeout", "checkout.recovery_token", "Nora Kim", "PASSED", "none recorded"),
    ("MYKC", "MyKC", "sponsor enrollment", "duplicate sponsor prevention", "sponsor.enrollment_key", "Eli Park", "FAILED", "automation locator changed"),
    ("CXE", "CXE", "accessible sign in", "keyboard-only sign in", "identity.accessibility_audit", "Asha Rao", "PASSED", "none recorded"),
    ("SPROG", "SPROG", "entitlement activation", "consistent API and UI entitlement state", "entitlement.activation_state", "Theo Diaz", "PASSED", "none recorded"),
]


def synthetic_documents():
    docs = []
    for code, project, feature, criterion, column, owner, outcome, cause in SCENARIOS:
        sid = lambda kind: f"SYN-{code}-{kind}-001"
        entity = f"{code}:confirmation-window"

        def add(kind, source, doc_type, title, text, authority=3, facts=None, entity_id=None, age=None):
            doc = {
                "source_type": source, "source_id": sid(kind), "project": project,
                "document_type": doc_type, "title": title, "content": text,
                "authoritative_level": authority, "updated_at": age or "2026-09-08T14:00:00Z",
                "created_at": age or "2026-09-01T09:00:00Z", "url": REPO+f"data/synthetic/{code.lower()}.json",
                "access_scope": "public", "owner": owner+" (fictional)", "synthetic": True,
                "dataset": "qei-synthetic-v1", "approval_status": "approved" if authority >= 4 else "observed",
                "version": 1, "facts": facts or {}, "entity_id": entity_id,
                "relationships": [], "aliases": [f"{project} {title}"],
            }
            docs.append(doc)
            return doc

        req = add("REQ", "jira", "requirement", f"{feature.title()} requirement",
                  f"Fictional {project} requirement {sid('REQ')}: {criterion}. Acceptance criteria: the confirmation window is 30 seconds; invalid input must be rejected; an audit record must be retained. Release scope: September demo only.",
                  5, {"confirmation_window_seconds": 30}, entity)
        spec = add("SPEC", "confluence", "specification", f"{feature.title()} design",
                   f"The fictional {project} design implements {criterion}. The approved confirmation window is 30 seconds. A retry after the window must trigger a new validation; an earlier retry must return the original outcome.", 4)
        mapping = add("MAP", "sharepoint", "database_mapping", f"{feature.title()} database mapping",
                      f"The fictional {project} validation maps to {column}. Verify one audit row per request and never store access tokens in the audit payload. This is an invented schema, not an enterprise database.", 4)
        pr = add("PR", "bitbucket", "pull_request", f"{feature.title()} implementation review",
                 f"Fictional pull request {sid('PR')} implements {criterion}. {owner} approved the change. Changed files: src/{code.lower()}/validation.py and tests/{code.lower()}/confirmation.feature. Review decision: approved for the demo branch.")
        feature_doc = add("FEATURE", "katalon", "automation_source", f"{feature.title()} Gherkin feature",
                          f"Fictional feature file tests/{code.lower()}/confirmation.feature. Scenario: {criterion}. Given a valid request, when confirmation is retried within 30 seconds, then exactly one audit row exists. Negative scenario: invalid input is rejected.")
        step = add("STEP", "bitbucket", "step_definition", f"{feature.title()} step definitions",
                   f"Fictional step definition src/{code.lower()}/steps.py binds the confirmation scenario to assert_single_audit_row(request_id). The helper checks {column} using a read-only database fixture. No executable production code is provided.")
        test = add("TEST", "katalon", "test_case", f"{feature.title()} regression test",
                   f"Synthetic automated test {sid('TEST')} checks {criterion}, the 30-second confirmation boundary and invalid input. It traces to the demo requirement, not to a test identifier in the supplied CSV.")
        run = add("RUN", "testops", "run", f"{feature.title()} demo execution",
                  f"Synthetic execution {sid('RUN')} ran {sid('TEST')} on 2026-09-08 in demo-staging. Outcome: {outcome}. Duration: 42 seconds. Recorded failure category: {cause}. This fictional result does not change the supplied CSV metrics.",
                  facts={"status": outcome, "failure_category": cause})
        chat = add("CHAT", "slack", "discussion", f"{feature.title()} earlier discussion",
                   f"Earlier fictional Slack discussion: the proposed confirmation window is 15 seconds. This proposal was not approved. Do not treat this discussion as the release requirement.",
                   1, {"confirmation_window_seconds": 15}, entity, "2026-07-01T12:00:00Z")
        chat["approval_status"] = "superseded"
        decision = add("DECISION", "confluence", "decision", f"{feature.title()} approved decision",
                       f"{owner} approved a 30-second confirmation window for fictional {project} on September 8. This supersedes the earlier 15-second Slack proposal. The design and requirement are authoritative for this demo release.",
                       5, {"confirmation_window_seconds": 30}, entity)
        person = add("PERSON", "sharepoint", "person", f"{owner} QE ownership",
                     f"{owner} is a fictional QE lead for {project}. Skills: API validation, test design and failure triage. Contact the project QE owner to confirm missing release evidence; no real contact details are supplied.")
        defect = add("DEFECT", "jira", "defect", f"{feature.title()} triage record",
                     f"Fictional triage for {sid('RUN')}: outcome {outcome}; cause {cause}. A passing run is not proof that all product requirements are covered. Triage owner: {owner}. Production impact is unknown.", 4)

        def link(source, target, relation):
            quote = f"{source['source_id']} {relation} {target['source_id']}."
            source["content"] += " " + quote
            source["relationships"].append({"target": target["source_id"], "type": relation,
                                             "evidence_source_id": source["source_id"], "evidence_quote": quote})

        for source, target, relation in [
            (spec, req, "REFINES"), (mapping, spec, "DETAILS"), (pr, req, "IMPLEMENTS"),
            (pr, person, "APPROVED_BY"), (feature_doc, req, "COVERS"), (step, feature_doc, "BINDS"),
            (test, feature_doc, "AUTOMATES"), (run, test, "EXECUTES"), (defect, run, "ANALYZES"),
            (decision, chat, "SUPERSEDES"), (decision, req, "GOVERNS"), (decision, person, "APPROVED_BY"),
            (chat, req, "DISCUSSES"), (person, req, "OWNS"), (test, mapping, "VALIDATES"),
        ]:
            link(source, target, relation)
    return docs


def write_exports():
    docs = synthetic_documents()
    folder = ROOT / "data/synthetic"
    folder.mkdir(parents=True, exist_ok=True)
    for code, project, *_ in SCENARIOS:
        (folder / f"{code.lower()}.json").write_text(
            json.dumps([d for d in docs if d["project"] == project], indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"synthetic_documents": len(docs), "relationships": sum(len(d["relationships"]) for d in docs)}))


if __name__ == "__main__":
    write_exports()
