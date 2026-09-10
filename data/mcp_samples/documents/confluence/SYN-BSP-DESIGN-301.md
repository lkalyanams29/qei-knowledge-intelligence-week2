# Payment Idempotency design and decisions

> SYNTHETIC — not a real enterprise record or MCP response.

- Source ID: `SYN-BSP-DESIGN-301`
- Project: BSP Services
- Source: confluence
- Owner: Mira Chen (fictional)
- Updated: 2026-09-09T14:00:00Z
- Document review status: approved
- Connection: planned native MCP; not connected.

---

SYNTHETIC DOCUMENT: BSP Services; Payment Idempotency design and decisions.

## Purpose

Prevent duplicate payment ledger entries when an authorized client retries a request.

## Approved demo design

The gateway validates payment scope before reserving a composite tenant-and-idempotency key. The ledger transaction and reservation commit together. A reservation stores a payload digest, not a card number. The confirmation window is 30 seconds, matching the earlier demo requirement.

## Verification boundary

Both responses reference one payment identifier and the ledger contains one row.

## Failure and trust boundaries

Validate authorization before state changes. Treat downstream timeouts as unknown outcomes until reconciled with source evidence. A tool's search excerpt is not a complete design document.

## Decision record

Reviewed by fictional QE owner Mira Chen. The Jira story defines acceptance; this page explains the design. A contradiction must be reported rather than silently merged.

SYN-BSP-DESIGN-301 EXPLAINS SYN-BSP-STORY-201.
