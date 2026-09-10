# Accessible Sign In guardrail story

> SYNTHETIC — not a real enterprise record or MCP response.

- Source ID: `SYN-CXE-STORY-201`
- Project: CXE
- Source: jira
- Owner: Asha Rao (fictional)
- Updated: 2026-09-09T14:00:00Z
- Document review status: approved
- Connection: planned native MCP; not connected.

---

SYNTHETIC DOCUMENT: CXE; Accessible Sign In guardrail story.

## User story

Allow the complete fictional sign-in journey using a keyboard with clear validation and predictable focus.

## Acceptance criteria

AC1: Keyboard focus reaches each sign-in control in a predictable order with a visible indicator.
AC2: Invalid input produces a textual error associated with the relevant field.
AC3: After a failed submit, focus moves to the error summary and the password value is not exposed in logs.
AC4: Successful sign-in preserves the requested destination while rejecting external redirect destinations.

## Delivery scope

Status: Ready for QE. Priority: High. Release: September synthetic demo. Owner: Asha Rao. This adds detailed guardrails to the existing demo requirement; no live Jira issue exists.

## Definition of done

Attach reviewed acceptance evidence and a negative-path result. Missing evidence blocks sign-off; this document does not assert that tests already passed.

SYN-CXE-STORY-201 DETAILS SYN-CXE-REQ-001.
