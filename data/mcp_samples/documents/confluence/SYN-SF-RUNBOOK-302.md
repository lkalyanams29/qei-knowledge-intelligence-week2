# Opportunity Approval triage and recovery runbook

> SYNTHETIC — not a real enterprise record or MCP response.

- Source ID: `SYN-SF-RUNBOOK-302`
- Project: Salesforce
- Source: confluence
- Owner: Owen Shah (fictional)
- Updated: 2026-09-09T14:00:00Z
- Document review status: approved
- Connection: planned native MCP; not connected.

---

SYNTHETIC DOCUMENT: Salesforce; Opportunity Approval triage and recovery runbook.

## When to use

For the fictional opportunity approval incident. An approval for revision 3 was accepted after the amount was edited to revision 4.

## Read-only diagnosis

Capture the masked correlation identifier and environment. Compare the source requirement, observed result and affected revision. Classify product, automation or environment cause without guessing.

## Demo mitigation

Keep affected fictional opportunities in pending-approval state and request a new approval after edits.

## Demo rollback

Restore the previous approval validation rule in the demo sandbox and retain audit evidence for every attempted transition.

## Escalation and safety

Escalation owner: Owen Shah, fictional QE lead. These are documentation examples, not permission for an agent to operate production. Request human approval before any state-changing recovery action.

SYN-SF-RUNBOOK-302 DIAGNOSES SYN-SF-BUG-202.
