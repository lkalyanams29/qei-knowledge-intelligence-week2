# Payment Idempotency triage and recovery runbook

> SYNTHETIC — not a real enterprise record or MCP response.

- Source ID: `SYN-BSP-RUNBOOK-302`
- Project: BSP Services
- Source: confluence
- Owner: Mira Chen (fictional)
- Updated: 2026-09-09T14:00:00Z
- Document review status: approved
- Connection: planned native MCP; not connected.

---

SYNTHETIC DOCUMENT: BSP Services; Payment Idempotency triage and recovery runbook.

## When to use

For the fictional payment idempotency incident. Two concurrent retries returned different payment identifiers when a stale replica was used for the reservation lookup.

## Read-only diagnosis

Capture the masked correlation identifier and environment. Compare the source requirement, observed result and affected revision. Classify product, automation or environment cause without guessing.

## Demo mitigation

Route reservation reads to the writer in demo-staging; do not replay captured payment payloads.

## Demo rollback

Disable the retry optimization with the demo feature flag and verify a single ledger row using a masked request identifier.

## Escalation and safety

Escalation owner: Mira Chen, fictional QE lead. These are documentation examples, not permission for an agent to operate production. Request human approval before any state-changing recovery action.

SYN-BSP-RUNBOOK-302 DIAGNOSES SYN-BSP-BUG-202.
