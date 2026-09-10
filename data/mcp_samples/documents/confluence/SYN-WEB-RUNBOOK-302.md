# Checkout Recovery triage and recovery runbook

> SYNTHETIC — not a real enterprise record or MCP response.

- Source ID: `SYN-WEB-RUNBOOK-302`
- Project: WebOps
- Source: confluence
- Owner: Nora Kim (fictional)
- Updated: 2026-09-09T14:00:00Z
- Document review status: approved
- Connection: planned native MCP; not connected.

---

SYNTHETIC DOCUMENT: WebOps; Checkout Recovery triage and recovery runbook.

## When to use

For the fictional checkout recovery incident. The recovery screen displayed a cached discount even after the pricing service returned its removal.

## Read-only diagnosis

Capture the masked correlation identifier and environment. Compare the source requirement, observed result and affected revision. Classify product, automation or environment cause without guessing.

## Demo mitigation

Require a full cart refresh before confirmation and show a changed-price notice.

## Demo rollback

Turn off cart auto-recovery in the demo configuration and direct the synthetic shopper to rebuild the cart.

## Escalation and safety

Escalation owner: Nora Kim, fictional QE lead. These are documentation examples, not permission for an agent to operate production. Request human approval before any state-changing recovery action.

SYN-WEB-RUNBOOK-302 DIAGNOSES SYN-WEB-BUG-202.
