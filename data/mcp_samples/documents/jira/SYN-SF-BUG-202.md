# Opportunity Approval defect investigation

> SYNTHETIC — not a real enterprise record or MCP response.

- Source ID: `SYN-SF-BUG-202`
- Project: Salesforce
- Source: jira
- Owner: Owen Shah (fictional)
- Updated: 2026-09-09T14:00:00Z
- Document review status: triaged
- Connection: planned native MCP; not connected.

---

SYNTHETIC DOCUMENT: Salesforce; Opportunity Approval defect investigation.

## Observed in fictional test

An approval for revision 3 was accepted after the amount was edited to revision 4.

## Reproduction

Approve a fictional opportunity, edit its amount, then attempt the close transition without seeking another approval.

## Expected result

The close transition is blocked and a revision-4 manager approval is requested.

## Triage

Product workflow defect; awaiting correction. A successful login test does not cover this approval rule.

## Disposition

Status: Open. Severity: High. Assignee: Owen Shah. Evidence is synthetic. Do not mark this defect resolved without a new reviewed result.

SYN-SF-BUG-202 AFFECTS_VALIDATION_OF SYN-SF-STORY-201.
