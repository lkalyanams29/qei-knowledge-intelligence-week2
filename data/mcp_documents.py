"""Generate original QE documentation for planned native-MCP source ingestion.

This is QEI's normalized fixture format, NOT a native server response schema.
No server, account, tool name or endpoint is invented or contacted.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRANCH_URL = "https://github.com/lkalyanams29/qei-knowledge-intelligence-week2/blob/codex/python-streamlit-graphrag/"
DATASET = "qei-native-mcp-documentation-v1"
UPDATED = "2026-09-09T14:00:00Z"

# Fictional requirements, not recommendations or descriptions of real systems.
SCENARIOS = [
    {"code": "BSP", "project": "BSP Services", "owner": "Mira Chen", "feature": "payment idempotency",
     "goal": "Prevent duplicate payment ledger entries when an authorized client retries a request.",
     "criteria": ["AC1: An authenticated payment request with a new idempotency key creates exactly one ledger row.",
                  "AC2: The same key and unchanged payload within 30 seconds returns the original payment identifier without a second debit.",
                  "AC3: Reusing the key with a different amount returns a conflict response and does not change the ledger.",
                  "AC4: A caller without payment scope receives an authorization error before any ledger write."],
     "design": "The gateway validates payment scope before reserving a composite tenant-and-idempotency key. The ledger transaction and reservation commit together. A reservation stores a payload digest, not a card number. The confirmation window is 30 seconds, matching the earlier demo requirement.",
     "defect": "Two concurrent retries returned different payment identifiers when a stale replica was used for the reservation lookup.",
     "reproduce": "Submit two authorized identical requests concurrently against a deliberately lagging demo replica. Compare payment identifiers and ledger row count.",
     "expected": "Both responses reference one payment identifier and the ledger contains one row.",
     "severity": "High", "triage": "Product concurrency defect; fix pending. This is separate from the earlier expired-certificate sample incident.",
     "mitigation": "Route reservation reads to the writer in demo-staging; do not replay captured payment payloads.",
     "rollback": "Disable the retry optimization with the demo feature flag and verify a single ledger row using a masked request identifier.",
     "coverage": "Exercise repeated, concurrent and cross-tenant keys; changed amounts; boundary timings of 29, 30 and 31 seconds; expired authorization; and writer failure.",
     "data": "Use fictional account DEMO-PAYER-001 and generated nonfinancial amounts. Validate payments.idempotency_key and ledger counts with a read-only fixture.",
     "gate": "No duplicate ledger writes in the concurrency suite; payment-scope negative tests pass; rollback rehearsal evidence is attached."},
    {"code": "SF", "project": "Salesforce", "owner": "Owen Shah", "feature": "opportunity approval",
     "goal": "Prevent an opportunity from closing before an authorized manager approves the matching revision.",
     "criteria": ["AC1: A sales representative can request approval but cannot approve their own opportunity.",
                  "AC2: Closing is blocked until a manager approval references the active opportunity revision.",
                  "AC3: Editing the opportunity amount invalidates an earlier approval and creates a new approval request.",
                  "AC4: Duplicate approval callbacks do not create duplicate approval audit entries."],
     "design": "Approval state is keyed by opportunity revision. A manager's approval stores the approved revision and actor role. The close transition compares that revision with the active record before changing stage. Duplicate callbacks use a stable event identifier.",
     "defect": "An approval for revision 3 was accepted after the amount was edited to revision 4.",
     "reproduce": "Approve a fictional opportunity, edit its amount, then attempt the close transition without seeking another approval.",
     "expected": "The close transition is blocked and a revision-4 manager approval is requested.",
     "severity": "High", "triage": "Product workflow defect; awaiting correction. A successful login test does not cover this approval rule.",
     "mitigation": "Keep affected fictional opportunities in pending-approval state and request a new approval after edits.",
     "rollback": "Restore the previous approval validation rule in the demo sandbox and retain audit evidence for every attempted transition.",
     "coverage": "Cover representative, manager and read-only roles; approval rejection; edited amounts; duplicate callbacks; stale approvals; and stage-transition audit records.",
     "data": "Use fictional opportunity DEMO-OPP-001, synthetic manager/representative personas and opportunity.approval_status. Do not copy customer opportunity data.",
     "gate": "Revision mismatch and self-approval tests pass; no unapproved close transitions remain; a manager and QE owner sign the demo evidence pack."},
    {"code": "WEB", "project": "WebOps", "owner": "Nora Kim", "feature": "checkout recovery",
     "goal": "Recover a customer's cart after session expiry without exposing another customer's cart or preserving invalid prices.",
     "criteria": ["AC1: After reauthentication, a recovery token restores only the cart belonging to the same fictional account.",
                  "AC2: A token issued to a different account is rejected and reveals no cart contents.",
                  "AC3: Recovered line items are repriced and unavailable inventory is clearly flagged before checkout.",
                  "AC4: A consumed recovery token cannot be replayed to create a second order."],
     "design": "The recovery service binds the token to account and cart identifiers. Reauthentication precedes cart lookup. A recovered cart is revalidated against pricing and inventory services, and token consumption is recorded atomically with order creation.",
     "defect": "The recovery screen displayed a cached discount even after the pricing service returned its removal.",
     "reproduce": "Create a demo cart with a discount, expire the session, remove the discount in the stub and recover the cart after login.",
     "expected": "The screen shows the refreshed price and explains the discount removal before order confirmation.",
     "severity": "Medium", "triage": "Product presentation defect; repricing mismatch is unresolved in the demo scenario.",
     "mitigation": "Require a full cart refresh before confirmation and show a changed-price notice.",
     "rollback": "Turn off cart auto-recovery in the demo configuration and direct the synthetic shopper to rebuild the cart.",
     "coverage": "Test same-account and cross-account tokens, expired and replayed tokens, changed inventory, removed promotions and interruption during order creation.",
     "data": "Use fictional shopper DEMO-SHOPPER-001, synthetic catalog items and checkout.recovery_token. No real customer sessions or tokens are recorded.",
     "gate": "Cross-account isolation and token-replay checks pass; the repricing defect is resolved or explicitly blocks the demo release."},
    {"code": "MYKC", "project": "MyKC", "owner": "Eli Park", "feature": "sponsor enrollment",
     "goal": "Submit one enrollment for a sponsor even when the browser retries after a timeout.",
     "criteria": ["AC1: A valid sponsor request creates one enrollment record and a confirmation reference.",
                  "AC2: A retry with the same enrollment key returns the existing reference instead of creating another record.",
                  "AC3: Required-field validation occurs before submission and is repeated by the server.",
                  "AC4: A duplicate business identifier routes the user to review rather than silently updating the existing sponsor."],
     "design": "The browser retains a generated enrollment key for a single submission journey. The service checks required fields and business identifiers before committing an enrollment. Retry responses reuse the existing confirmation reference; duplicate identities require an explicit review path.",
     "defect": "The confirmation test clicked an outdated element locator after the review page was redesigned.",
     "reproduce": "Execute the old demo page-object locator against the redesigned enrollment review screen.",
     "expected": "The test selects the stable confirmation control and verifies the returned enrollment reference.",
     "severity": "Medium", "triage": "Automation locator defect; this does not establish a product enrollment failure.",
     "mitigation": "Update the shared page object to the approved stable test identifier and rerun the affected journey.",
     "rollback": "Revert the page-object change if it selects a different control; preserve the failed-run screenshot without personal data.",
     "coverage": "Cover repeated submits, transport timeout, duplicate business identity, keyboard validation, server validation and the review-to-confirmation transition.",
     "data": "Use fictional sponsor DEMO-SPONSOR-001, a generated enrollment key and sponsor.enrollment_key. Do not use real sponsor names or addresses.",
     "gate": "The shared locator fix is reviewed; duplicate-enrollment and required-field scenarios pass; the automation-only failure is documented separately."},
    {"code": "CXE", "project": "CXE", "owner": "Asha Rao", "feature": "accessible sign in",
     "goal": "Allow the complete fictional sign-in journey using a keyboard with clear validation and predictable focus.",
     "criteria": ["AC1: Keyboard focus reaches each sign-in control in a predictable order with a visible indicator.",
                  "AC2: Invalid input produces a textual error associated with the relevant field.",
                  "AC3: After a failed submit, focus moves to the error summary and the password value is not exposed in logs.",
                  "AC4: Successful sign-in preserves the requested destination while rejecting external redirect destinations."],
     "design": "The sign-in form uses associated labels, a focusable error summary and an allowlisted return destination. Error rendering does not replace the entire form node. The synthetic accessibility audit records field and focus outcomes, never password values.",
     "defect": "After invalid credentials, focus moved to the page body instead of the error summary.",
     "reproduce": "Navigate the demo sign-in form with a keyboard, submit invalid synthetic credentials and inspect the focused element.",
     "expected": "The error summary receives focus and links to the invalid field without revealing the entered password.",
     "severity": "High", "triage": "Product accessibility defect; the demo does not claim legal accessibility certification.",
     "mitigation": "Restore focus to the error summary after rendering and rerun the keyboard journey checks.",
     "rollback": "Restore the previous error-rendering component in the demo environment if focus ordering regresses.",
     "coverage": "Cover keyboard-only navigation, visible focus, field error association, repeated failed submits, destination preservation and external-redirect rejection.",
     "data": "Use fictional identity DEMO-CXE-USER-001 and synthetic invalid inputs. Store only focus outcomes in identity.accessibility_audit, not credentials.",
     "gate": "Keyboard journey and error-focus checks pass; redirect rejection is verified; manual assistive-technology review is recorded as pending, not fabricated."},
    {"code": "SPROG", "project": "SPROG", "owner": "Theo Diaz", "feature": "entitlement activation",
     "goal": "Keep API, database and UI entitlement state consistent after an activation event.",
     "criteria": ["AC1: An authorized activation request creates one pending entitlement event with a correlation identifier.",
                  "AC2: The UI shows pending until the committed entitlement state is available; it does not imply immediate activation.",
                  "AC3: Duplicate activation events do not create duplicate entitlements or notifications.",
                  "AC4: An out-of-order deactivate event cannot be overwritten by an older activation event."],
     "design": "Activation uses an event version and a correlation identifier. The projection applies only newer versions, and the UI reads the committed projection rather than assuming success from request acceptance. Duplicate events are acknowledged without repeated side effects.",
     "defect": "A delayed activation event overwrote a newer deactivation state in the read projection.",
     "reproduce": "Publish a demo deactivation event with version 8, then deliver a delayed activation event with version 7.",
     "expected": "The projection remains deactivated at version 8 and no extra activation notification is sent.",
     "severity": "High", "triage": "Product event-ordering defect; correction and replay verification are pending.",
     "mitigation": "Pause the demo event consumer, inspect version checks and replay only the approved synthetic event sequence.",
     "rollback": "Restore the last validated projection snapshot and replay the synthetic journal in version order before resuming the consumer.",
     "coverage": "Combine API contract tests, projection queries and UI journey checks for pending states, duplicate events, out-of-order delivery and consumer restart.",
     "data": "Use fictional entitlement DEMO-ENTITLEMENT-001 and synthetic events with versions 7 and 8. Validate entitlement.activation_state through a read-only fixture.",
     "gate": "Out-of-order and duplicate-event tests pass across API, UI and database; projection recovery is demonstrated with a synthetic journal."},
]


def documentation_records():
    docs = []
    for scenario in SCENARIOS:
        code, project, owner = (scenario[key] for key in ("code", "project", "owner"))
        make_id = lambda kind, number: f"SYN-{code}-{kind}-{number}"

        def add(source, kind, number, doc_type, title, sections, authority, native, approval="approved", facts=None):
            sid = make_id(kind, number)
            body = "\n\n".join(f"## {heading}\n\n{text}" for heading, text in sections)
            content = f"SYNTHETIC DOCUMENT: {project}; {title}.\n\n{body}"
            doc = {
                "source_type": source, "source_id": sid, "project": project, "document_type": doc_type,
                "title": title, "content": content, "authoritative_level": authority,
                "created_at": "2026-09-02T09:00:00Z", "updated_at": UPDATED,
                "url": BRANCH_URL+f"data/mcp_samples/documents/{source}/{sid}.md",
                "access_scope": "public", "owner": owner+" (fictional)", "synthetic": True,
                "dataset": DATASET, "approval_status": approval, "version": "1.0",
                "facts": facts or {}, "relationships": [], "aliases": [title, f"{project} {title}"],
                "mcp_provenance": {
                    "mode": "synthetic_fixture", "intended_transport": "native_mcp",
                    "server_key": "atlassian_rovo" if source in {"jira", "confluence"} else "sharepoint_native",
                    "server_connected": False, "tool_name": None, "tool_schema_version": None,
                    "native_locator": native, "native_url": None, "retrieved_at": None,
                    "source_permissions_verified": False, "content_complete": True,
                    "normalization_schema": "qei-document-v1",
                    "notice": "QEI-owned synthetic mapping fields, not a captured native MCP response. Public only because fictional.",
                },
            }
            if source == "jira": doc["aliases"].append(native["issue_key"])
            docs.append(doc)
            return doc

        story = add("jira", "STORY", 201, "requirement", f"{scenario['feature'].title()} guardrail story", [
            ("User story", scenario["goal"]),
            ("Acceptance criteria", "\n".join(scenario["criteria"])),
            ("Delivery scope", f"Status: Ready for QE. Priority: High. Release: September synthetic demo. Owner: {owner}. This adds detailed guardrails to the existing demo requirement; no live Jira issue exists."),
            ("Definition of done", "Attach reviewed acceptance evidence and a negative-path result. Missing evidence blocks sign-off; this document does not assert that tests already passed."),
        ], 5, {"resource_kind": "issue", "site_alias": "synthetic-atlassian", "project_key": "SYN"+code,
                "issue_key": f"SYN{code}-201", "issue_type": "Story", "status": "Ready for QE", "priority": "High"})
        bug = add("jira", "BUG", 202, "defect", f"{scenario['feature'].title()} defect investigation", [
            ("Observed in fictional test", scenario["defect"]), ("Reproduction", scenario["reproduce"]),
            ("Expected result", scenario["expected"]), ("Triage", scenario["triage"]),
            ("Disposition", f"Status: Open. Severity: {scenario['severity']}. Assignee: {owner}. Evidence is synthetic. Do not mark this defect resolved without a new reviewed result."),
        ], 4, {"resource_kind": "issue", "site_alias": "synthetic-atlassian", "project_key": "SYN"+code,
                "issue_key": f"SYN{code}-202", "issue_type": "Bug", "status": "Open", "severity": scenario["severity"]},
                approval="triaged", facts={"defect_status": "Open"})
        design = add("confluence", "DESIGN", 301, "specification", f"{scenario['feature'].title()} design and decisions", [
            ("Purpose", scenario["goal"]), ("Approved demo design", scenario["design"]),
            ("Verification boundary", scenario["expected"]),
            ("Failure and trust boundaries", "Validate authorization before state changes. Treat downstream timeouts as unknown outcomes until reconciled with source evidence. A tool's search excerpt is not a complete design document."),
            ("Decision record", f"Reviewed by fictional QE owner {owner}. The Jira story defines acceptance; this page explains the design. A contradiction must be reported rather than silently merged."),
        ], 4, {"resource_kind": "page", "site_alias": "synthetic-atlassian", "space_key": "QE"+code,
                "page_id": f"syn-{code.lower()}-design-301", "parent_page_id": f"syn-{code.lower()}-space-home", "version": 1})
        runbook = add("confluence", "RUNBOOK", 302, "runbook", f"{scenario['feature'].title()} triage and recovery runbook", [
            ("When to use", f"For the fictional {scenario['feature']} incident. {scenario['defect']}"),
            ("Read-only diagnosis", "Capture the masked correlation identifier and environment. Compare the source requirement, observed result and affected revision. Classify product, automation or environment cause without guessing."),
            ("Demo mitigation", scenario["mitigation"]), ("Demo rollback", scenario["rollback"]),
            ("Escalation and safety", f"Escalation owner: {owner}, fictional QE lead. These are documentation examples, not permission for an agent to operate production. Request human approval before any state-changing recovery action."),
        ], 4, {"resource_kind": "page", "site_alias": "synthetic-atlassian", "space_key": "QE"+code,
                "page_id": f"syn-{code.lower()}-runbook-302", "parent_page_id": f"syn-{code.lower()}-space-home", "version": 1})
        strategy = add("sharepoint", "PLAN", 401, "test_strategy", f"{scenario['feature'].title()} QE test strategy", [
            ("Objective", scenario["goal"]), ("Coverage and boundaries", scenario["coverage"]),
            ("Test data and database validation", scenario["data"]),
            ("Execution evidence", "Record test identifier, source revision, environment, observed outcome and duration. Link the exact acceptance criterion. A planned test is not proof of executed coverage; synthetic results never modify the supplied TestOps CSV."),
            ("Review", f"Document owner: {owner}. Review status: approved as a fictional test plan, not execution sign-off. Keep automation defects separate from product failures."),
        ], 4, {"resource_kind": "drive_item", "site_id": f"syn-site-{code.lower()}", "drive_id": "syn-qe-library",
                "item_id": f"syn-{code.lower()}-plan-401", "library": "QE Documentation", "file_name": f"{code}-QE-Test-Strategy.md",
                "version_label": "1.0", "content_type": "text/markdown", "etag": f"synthetic-{code.lower()}-plan-v1"})
        checklist = add("sharepoint", "RELEASE", 402, "release_checklist", f"{scenario['feature'].title()} release evidence checklist", [
            ("Entry criteria", "The Jira acceptance criteria and Confluence design must reference the same reviewed scope. Source access and evidence freshness must be checked before a release review."),
            ("Exit criteria", scenario["gate"]),
            ("Outstanding evidence", f"The linked synthetic Jira bug remains open. Execution sign-off: pending. Security review: pending. QE reviewer: {owner}. No production release approval is provided by this checklist."),
            ("Evidence package", "Include cited requirement and design versions, test results, defect disposition and a reviewed rollback record. If a document is unavailable through MCP, report the missing evidence; do not infer approval from its filename."),
        ], 4, {"resource_kind": "drive_item", "site_id": f"syn-site-{code.lower()}", "drive_id": "syn-qe-library",
                "item_id": f"syn-{code.lower()}-release-402", "library": "QE Documentation", "file_name": f"{code}-Release-Evidence.md",
                "version_label": "0.9", "content_type": "text/markdown", "etag": f"synthetic-{code.lower()}-release-v09"},
                approval="pending", facts={"release_approval": "Pending"})
        checklist["version"] = "0.9"

        def link(source, target_id, relation):
            quote = f"{source['source_id']} {relation} {target_id}."
            source["content"] += "\n\n"+quote
            source["relationships"].append({"target": target_id, "type": relation,
                                             "evidence_source_id": source["source_id"], "evidence_quote": quote})

        for source, target, relation in [
            (story, f"SYN-{code}-REQ-001", "DETAILS"), (bug, story["source_id"], "AFFECTS_VALIDATION_OF"),
            (design, story["source_id"], "EXPLAINS"), (runbook, bug["source_id"], "DIAGNOSES"),
            (strategy, story["source_id"], "PLANS_COVERAGE"), (strategy, design["source_id"], "USES_DESIGN"),
            (checklist, story["source_id"], "REQUIRES_EVIDENCE_FOR"), (checklist, strategy["source_id"], "REQUIRES_PLAN"),
            (checklist, bug["source_id"], "BLOCKED_BY"), (checklist, runbook["source_id"], "REQUIRES_ROLLBACK_REVIEW"),
        ]:
            link(source, target, relation)
    return docs


def write_exports():
    records = documentation_records()
    folder = ROOT/"data/mcp_samples"
    folder.mkdir(parents=True, exist_ok=True)
    for source in ("jira", "confluence", "sharepoint"):
        selected = [d for d in records if d["source_type"] == source]
        (folder/f"{source}.json").write_text(json.dumps(selected, indent=2)+"\n", encoding="utf-8")
        doc_folder = folder/"documents"/source
        doc_folder.mkdir(parents=True, exist_ok=True)
        for doc in selected:
            metadata = (f"# {doc['title']}\n\n> SYNTHETIC — not a real enterprise record or MCP response.\n\n"
                        f"- Source ID: `{doc['source_id']}`\n- Project: {doc['project']}\n"
                        f"- Source: {source}\n- Owner: {doc['owner']}\n"
                        f"- Updated: {doc['updated_at']}\n- Document review status: {doc['approval_status']}\n"
                        "- Connection: planned native MCP; not connected.\n\n---\n\n")
            (doc_folder/f"{doc['source_id']}.md").write_text(metadata+doc["content"]+"\n", encoding="utf-8")
    inventory = {"dataset": DATASET, "synthetic": True, "native_servers_connected": False,
                 "records": len(records), "by_source": dict(Counter(d["source_type"] for d in records)),
                 "relationships": sum(len(d["relationships"]) for d in records),
                 "projects": [s["project"] for s in SCENARIOS]}
    # Inventory is outside the normalized-export folder to avoid ingesting it as a document array.
    (ROOT/"docs/mcp-dataset-inventory.json").write_text(json.dumps(inventory, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(inventory))


if __name__ == "__main__":
    write_exports()
