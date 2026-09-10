# Payment Idempotency defect investigation

> SYNTHETIC — not a real enterprise record or MCP response.

- Source ID: `SYN-BSP-BUG-202`
- Project: BSP Services
- Source: jira
- Owner: Mira Chen (fictional)
- Updated: 2026-09-09T14:00:00Z
- Document review status: triaged
- Connection: planned native MCP; not connected.

---

SYNTHETIC DOCUMENT: BSP Services; Payment Idempotency defect investigation.

## Observed in fictional test

Two concurrent retries returned different payment identifiers when a stale replica was used for the reservation lookup.

## Reproduction

Submit two authorized identical requests concurrently against a deliberately lagging demo replica. Compare payment identifiers and ledger row count.

## Expected result

Both responses reference one payment identifier and the ledger contains one row.

## Triage

Product concurrency defect; fix pending. This is separate from the earlier expired-certificate sample incident.

## Disposition

Status: Open. Severity: High. Assignee: Mira Chen. Evidence is synthetic. Do not mark this defect resolved without a new reviewed result.

SYN-BSP-BUG-202 AFFECTS_VALIDATION_OF SYN-BSP-STORY-201.
