# Opportunity Approval guardrail story

> SYNTHETIC — not a real enterprise record or MCP response.

- Source ID: `SYN-SF-STORY-201`
- Project: Salesforce
- Source: jira
- Owner: Owen Shah (fictional)
- Updated: 2026-09-09T14:00:00Z
- Document review status: approved
- Connection: planned native MCP; not connected.

---

SYNTHETIC DOCUMENT: Salesforce; Opportunity Approval guardrail story.

## User story

Prevent an opportunity from closing before an authorized manager approves the matching revision.

## Acceptance criteria

AC1: A sales representative can request approval but cannot approve their own opportunity.
AC2: Closing is blocked until a manager approval references the active opportunity revision.
AC3: Editing the opportunity amount invalidates an earlier approval and creates a new approval request.
AC4: Duplicate approval callbacks do not create duplicate approval audit entries.

## Delivery scope

Status: Ready for QE. Priority: High. Release: September synthetic demo. Owner: Owen Shah. This adds detailed guardrails to the existing demo requirement; no live Jira issue exists.

## Definition of done

Attach reviewed acceptance evidence and a negative-path result. Missing evidence blocks sign-off; this document does not assert that tests already passed.

SYN-SF-STORY-201 DETAILS SYN-SF-REQ-001.
