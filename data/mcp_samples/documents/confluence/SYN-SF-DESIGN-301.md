# Opportunity Approval design and decisions

> SYNTHETIC — not a real enterprise record or MCP response.

- Source ID: `SYN-SF-DESIGN-301`
- Project: Salesforce
- Source: confluence
- Owner: Owen Shah (fictional)
- Updated: 2026-09-09T14:00:00Z
- Document review status: approved
- Connection: planned native MCP; not connected.

---

SYNTHETIC DOCUMENT: Salesforce; Opportunity Approval design and decisions.

## Purpose

Prevent an opportunity from closing before an authorized manager approves the matching revision.

## Approved demo design

Approval state is keyed by opportunity revision. A manager's approval stores the approved revision and actor role. The close transition compares that revision with the active record before changing stage. Duplicate callbacks use a stable event identifier.

## Verification boundary

The close transition is blocked and a revision-4 manager approval is requested.

## Failure and trust boundaries

Validate authorization before state changes. Treat downstream timeouts as unknown outcomes until reconciled with source evidence. A tool's search excerpt is not a complete design document.

## Decision record

Reviewed by fictional QE owner Owen Shah. The Jira story defines acceptance; this page explains the design. A contradiction must be reported rather than silently merged.

SYN-SF-DESIGN-301 EXPLAINS SYN-SF-STORY-201.
