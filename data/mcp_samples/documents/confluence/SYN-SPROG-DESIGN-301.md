# Entitlement Activation design and decisions

> SYNTHETIC — not a real enterprise record or MCP response.

- Source ID: `SYN-SPROG-DESIGN-301`
- Project: SPROG
- Source: confluence
- Owner: Theo Diaz (fictional)
- Updated: 2026-09-09T14:00:00Z
- Document review status: approved
- Connection: planned native MCP; not connected.

---

SYNTHETIC DOCUMENT: SPROG; Entitlement Activation design and decisions.

## Purpose

Keep API, database and UI entitlement state consistent after an activation event.

## Approved demo design

Activation uses an event version and a correlation identifier. The projection applies only newer versions, and the UI reads the committed projection rather than assuming success from request acceptance. Duplicate events are acknowledged without repeated side effects.

## Verification boundary

The projection remains deactivated at version 8 and no extra activation notification is sent.

## Failure and trust boundaries

Validate authorization before state changes. Treat downstream timeouts as unknown outcomes until reconciled with source evidence. A tool's search excerpt is not a complete design document.

## Decision record

Reviewed by fictional QE owner Theo Diaz. The Jira story defines acceptance; this page explains the design. A contradiction must be reported rather than silently merged.

SYN-SPROG-DESIGN-301 EXPLAINS SYN-SPROG-STORY-201.
