# Accessible Sign In defect investigation

> SYNTHETIC — not a real enterprise record or MCP response.

- Source ID: `SYN-CXE-BUG-202`
- Project: CXE
- Source: jira
- Owner: Asha Rao (fictional)
- Updated: 2026-09-09T14:00:00Z
- Document review status: triaged
- Connection: planned native MCP; not connected.

---

SYNTHETIC DOCUMENT: CXE; Accessible Sign In defect investigation.

## Observed in fictional test

After invalid credentials, focus moved to the page body instead of the error summary.

## Reproduction

Navigate the demo sign-in form with a keyboard, submit invalid synthetic credentials and inspect the focused element.

## Expected result

The error summary receives focus and links to the invalid field without revealing the entered password.

## Triage

Product accessibility defect; the demo does not claim legal accessibility certification.

## Disposition

Status: Open. Severity: High. Assignee: Asha Rao. Evidence is synthetic. Do not mark this defect resolved without a new reviewed result.

SYN-CXE-BUG-202 AFFECTS_VALIDATION_OF SYN-CXE-STORY-201.
