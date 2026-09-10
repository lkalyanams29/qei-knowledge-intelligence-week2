# Checkout Recovery guardrail story

> SYNTHETIC — not a real enterprise record or MCP response.

- Source ID: `SYN-WEB-STORY-201`
- Project: WebOps
- Source: jira
- Owner: Nora Kim (fictional)
- Updated: 2026-09-09T14:00:00Z
- Document review status: approved
- Connection: planned native MCP; not connected.

---

SYNTHETIC DOCUMENT: WebOps; Checkout Recovery guardrail story.

## User story

Recover a customer's cart after session expiry without exposing another customer's cart or preserving invalid prices.

## Acceptance criteria

AC1: After reauthentication, a recovery token restores only the cart belonging to the same fictional account.
AC2: A token issued to a different account is rejected and reveals no cart contents.
AC3: Recovered line items are repriced and unavailable inventory is clearly flagged before checkout.
AC4: A consumed recovery token cannot be replayed to create a second order.

## Delivery scope

Status: Ready for QE. Priority: High. Release: September synthetic demo. Owner: Nora Kim. This adds detailed guardrails to the existing demo requirement; no live Jira issue exists.

## Definition of done

Attach reviewed acceptance evidence and a negative-path result. Missing evidence blocks sign-off; this document does not assert that tests already passed.

SYN-WEB-STORY-201 DETAILS SYN-WEB-REQ-001.
