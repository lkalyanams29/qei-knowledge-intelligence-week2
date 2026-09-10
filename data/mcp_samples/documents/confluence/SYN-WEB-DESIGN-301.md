# Checkout Recovery design and decisions

> SYNTHETIC — not a real enterprise record or MCP response.

- Source ID: `SYN-WEB-DESIGN-301`
- Project: WebOps
- Source: confluence
- Owner: Nora Kim (fictional)
- Updated: 2026-09-09T14:00:00Z
- Document review status: approved
- Connection: planned native MCP; not connected.

---

SYNTHETIC DOCUMENT: WebOps; Checkout Recovery design and decisions.

## Purpose

Recover a customer's cart after session expiry without exposing another customer's cart or preserving invalid prices.

## Approved demo design

The recovery service binds the token to account and cart identifiers. Reauthentication precedes cart lookup. A recovered cart is revalidated against pricing and inventory services, and token consumption is recorded atomically with order creation.

## Verification boundary

The screen shows the refreshed price and explains the discount removal before order confirmation.

## Failure and trust boundaries

Validate authorization before state changes. Treat downstream timeouts as unknown outcomes until reconciled with source evidence. A tool's search excerpt is not a complete design document.

## Decision record

Reviewed by fictional QE owner Nora Kim. The Jira story defines acceptance; this page explains the design. A contradiction must be reported rather than silently merged.

SYN-WEB-DESIGN-301 EXPLAINS SYN-WEB-STORY-201.
