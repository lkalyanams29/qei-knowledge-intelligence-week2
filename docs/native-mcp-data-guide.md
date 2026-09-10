# Synthetic Jira, Confluence and SharePoint documentation

## What was generated

This extension adds **36 fictional documents** across BSP Services, Salesforce, WebOps, MyKC, CXE and SPROG. There are two documents per source per project:

| Source | Documents | Content |
|---|---:|---|
| Jira | 12 | Six guardrail stories with four acceptance criteria each; six defect investigations with reproduction, expected outcome, severity and disposition |
| Confluence | 12 | Six designs/decision pages; six diagnosis, mitigation and recovery runbooks |
| SharePoint | 12 | Six QE test strategies; six release-evidence checklists with pending sign-off |

The records have **60 source-supported relationships**. They extend the previous synthetic stories without inventing links to the user-supplied CSV. Combined with the existing inputs, the index has **362 source records, 108 synthetic records and 4,420 relationships**. Original CSV counts remain unchanged.

The topics are domain-specific: payment idempotency, opportunity revision approval, checkout recovery, sponsor enrollment, accessible sign-in and entitlement event ordering. The MyKC locator issue is classified as automation-related, not proof of a product defect. Open defects and pending release checklists deliberately exercise safe fallback and incomplete evidence.

## Where to find the data

- Normalized JSON: `data/mcp_samples/jira.json`, `confluence.json`, `sharepoint.json`.
- Human-readable source bodies: `data/mcp_samples/documents/<source>/<source-id>.md`.
- Generator: `data/mcp_documents.py`.
- Machine-readable inventory: `docs/mcp-dataset-inventory.json`.
- Planned native-MCP configuration: `config/mcp_sources.json`.

These are local synthetic exports, **not issues or pages created in a real tenant**, and **not captured responses from a native MCP server**. All people, identifiers, schemas, incidents and sign-off states are fictional. Citation URLs point to actual Markdown files on the development branch, not invented Jira or SharePoint domains. The fixture snapshots use source update time September 9, 2026; no retrieval timestamp is fabricated.

## Native MCP architecture assumption

```text
Jira + Confluence native MCP       SharePoint native MCP
          (future)                        (future)
               \                        /
                verified, read-only tool calls
                         ↓
           provider-specific response normalization
                         ↓
          QEI document + provenance + resolved scope
                         ↓
            existing ingestion / graph / retrieval
```

Atlassian provides a Rovo MCP server for Jira and Confluence, subject to user permissions and organization controls. The future adapter must respect those controls and restrict itself to the required read/search operations. [Atlassian Rovo MCP overview](https://support.atlassian.com/security-and-access-policies/docs/understand-atlassian-rovo-mcp-server/), [permission controls](https://support.atlassian.com/security-and-access-policies/docs/Configure-Atlassian-Rovo-MCP-server-permission/).

Microsoft documents a Work IQ SharePoint MCP offering in preview. The exact tenant-approved offering, identity method, availability and tools must be verified when connecting; this fixture does not assume a universally available endpoint or interchangeable SharePoint tool schemas. [Microsoft Work IQ SharePoint MCP](https://learn.microsoft.com/en-us/connectors/workiqsharepoint/).

No native servers were installed or connected in this change. No OAuth consent, source writes, account creation or tenant access occurred. `enabled` remains false; endpoint and tool bindings are empty. Changing the planning JSON does not implement or activate a transport client.

## Mapping contract—not a vendor response schema

The `mcp_provenance` object is an **application-owned normalization contract**. Its field names describe what QEI needs; a real adapter must map the discovered provider schema into these fields after validation.

| QEI field | Fixture meaning | Future native-read mapping |
|---|---|---|
| `source_id` | Globally namespaced `SYN-...` record | Stable tenant/source/native-ID composite; do not rely on display title |
| `aliases` | Synthetic Jira key such as `SYNBSP-201` | Authorized native keys; resolve duplicate keys with tenant/project context |
| `native_locator` | Invented issue, page or drive-item metadata | Actual returned identifiers; do not assume these fixture keys equal provider field names |
| `url` / `native_url` | Real GitHub source file / null | Original authorized source URL, validated as a citation target |
| `version`, `updated_at` | Fictional source revision/time | Actual source revision/update time, not ingestion time |
| `retrieved_at` | Null: no retrieval occurred | Actual successful fetch time |
| `tool_name`, `tool_schema_version` | Null: no tool was called | Discovered and allowlisted tool identity/schema snapshot |
| `content_complete` | True for the complete local Markdown body | True only after full fetch/extraction succeeds; snippets and truncated output are partial |
| `source_permissions_verified` | False: no tenant permission check occurred | Must establish source-authorized visibility before serving real evidence |
| `access_scope` | Public solely because the record is fictional | Resolved source ACL; never copy fixture public visibility to a real document |

Jira fixtures include issue type, key, project, status and priority/severity. Confluence fixtures include space, page, parent and revision. SharePoint fixtures include site, drive, item, library, filename, content type and version/eTag examples. SharePoint bodies are Markdown text for this demo; the fixture does not implement DOCX/PDF extraction.

## Requirements before enabling live ingestion

1. Select the tenant-approved native MCP servers and authorize only required read/search access. Keep credentials and tokens in the approved secret store.
2. Discover real tools and schemas. MCP `tools/list` supports pagination; its opaque cursors must be followed without guessing their format. Source-search result pagination is tool-specific and must be learned from that tool's schema, not assumed to share MCP listing fields. [MCP pagination specification](https://modelcontextprotocol.io/specification/2025-11-25/server/utilities/pagination).
3. Fetch full authorized issue/page/document content. Preserve native IDs, original URL, revision, source time and extraction completeness. Do not index an error, denied response, title-only search hit or truncated snippet as full evidence.
4. Normalize rich text through a provider-specific adapter, then use the existing validated document contract. These fixtures intentionally do not invent Jira ADF, Confluence body or SharePoint download response shapes.
5. Resolve effective authorization and inheritance before caching, indexing, graph traversal or model calls. Unknown permissions must fail closed. Revalidate revocations and deletions; scoped caches must not leak content between users.
6. Define incremental synchronization from capabilities actually provided. Handle changed versions, duplicate IDs, deletes, denied documents, rate limits, timeouts and partial pages. Do not invent delta tokens or persist opaque MCP listing cursors as sync checkpoints.
7. Keep source mutation tools outside the QE retrieval path. A recovery runbook is knowledge to cite, not authorization to run its state-changing steps.
8. Validate with captured, sanitized responses and tenant-approved test accounts before claiming integration. The current tests validate fixtures and local retrieval only.

## Regenerate and try it

```sh
python -m data.mcp_documents
python scripts/ingest.py
python -m unittest discover -s tests -p "test_*.py"
python compare.py
python -m streamlit run ui.py
```

The new documents appear in the existing corpus and evidence graph. Example questions are included in the Ask QE dropdown:

- `What acceptance criteria are documented for SYNBSP-201?`
- `Which Confluence design and SharePoint test plan support SYNSF-201?`
- `What does the release checklist for SYN-WEB-RELEASE-402 require?`
- `What does the runbook for SYN-MYKC-RUNBOOK-302 say about the locator failure?`
- `What keyboard focus checks are in the test strategy SYN-CXE-PLAN-401?`
- `What is the expected result of the event-ordering defect SYNSPROG-202?`

The adapter contract allows future native-MCP data to use the same graph/retrieval path without representing today's local fixtures as live connections. No additional dependencies or remote model calls are needed for this extension.
