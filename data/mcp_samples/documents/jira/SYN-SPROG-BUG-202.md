# Entitlement Activation defect investigation

> SYNTHETIC — not a real enterprise record or MCP response.

- Source ID: `SYN-SPROG-BUG-202`
- Project: SPROG
- Source: jira
- Owner: Theo Diaz (fictional)
- Updated: 2026-09-09T14:00:00Z
- Document review status: triaged
- Connection: planned native MCP; not connected.

---

SYNTHETIC DOCUMENT: SPROG; Entitlement Activation defect investigation.

## Observed in fictional test

A delayed activation event overwrote a newer deactivation state in the read projection.

## Reproduction

Publish a demo deactivation event with version 8, then deliver a delayed activation event with version 7.

## Expected result

The projection remains deactivated at version 8 and no extra activation notification is sent.

## Triage

Product event-ordering defect; correction and replay verification are pending.

## Disposition

Status: Open. Severity: High. Assignee: Theo Diaz. Evidence is synthetic. Do not mark this defect resolved without a new reviewed result.

SYN-SPROG-BUG-202 AFFECTS_VALIDATION_OF SYN-SPROG-STORY-201.
