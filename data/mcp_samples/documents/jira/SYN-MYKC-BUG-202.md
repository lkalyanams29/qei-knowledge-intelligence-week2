# Sponsor Enrollment defect investigation

> SYNTHETIC — not a real enterprise record or MCP response.

- Source ID: `SYN-MYKC-BUG-202`
- Project: MyKC
- Source: jira
- Owner: Eli Park (fictional)
- Updated: 2026-09-09T14:00:00Z
- Document review status: triaged
- Connection: planned native MCP; not connected.

---

SYNTHETIC DOCUMENT: MyKC; Sponsor Enrollment defect investigation.

## Observed in fictional test

The confirmation test clicked an outdated element locator after the review page was redesigned.

## Reproduction

Execute the old demo page-object locator against the redesigned enrollment review screen.

## Expected result

The test selects the stable confirmation control and verifies the returned enrollment reference.

## Triage

Automation locator defect; this does not establish a product enrollment failure.

## Disposition

Status: Open. Severity: Medium. Assignee: Eli Park. Evidence is synthetic. Do not mark this defect resolved without a new reviewed result.

SYN-MYKC-BUG-202 AFFECTS_VALIDATION_OF SYN-MYKC-STORY-201.
