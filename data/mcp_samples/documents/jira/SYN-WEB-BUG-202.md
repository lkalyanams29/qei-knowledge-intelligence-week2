# Checkout Recovery defect investigation

> SYNTHETIC — not a real enterprise record or MCP response.

- Source ID: `SYN-WEB-BUG-202`
- Project: WebOps
- Source: jira
- Owner: Nora Kim (fictional)
- Updated: 2026-09-09T14:00:00Z
- Document review status: triaged
- Connection: planned native MCP; not connected.

---

SYNTHETIC DOCUMENT: WebOps; Checkout Recovery defect investigation.

## Observed in fictional test

The recovery screen displayed a cached discount even after the pricing service returned its removal.

## Reproduction

Create a demo cart with a discount, expire the session, remove the discount in the stub and recover the cart after login.

## Expected result

The screen shows the refreshed price and explains the discount removal before order confirmation.

## Triage

Product presentation defect; repricing mismatch is unresolved in the demo scenario.

## Disposition

Status: Open. Severity: Medium. Assignee: Nora Kim. Evidence is synthetic. Do not mark this defect resolved without a new reviewed result.

SYN-WEB-BUG-202 AFFECTS_VALIDATION_OF SYN-WEB-STORY-201.
