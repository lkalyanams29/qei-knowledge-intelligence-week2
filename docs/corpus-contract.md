# Corpus ownership and import contract

The user approved public upload of the sample dataset. This permission does not extend to future enterprise exports. Keep those outside the public Git index and deploy them only into an appropriately restricted environment.

## Source inventory

| Input | Ownership and authority | Use |
|---|---|---|
| `katalon_testops_sample_dataset.csv` | User-supplied sample, L3 | Observed test results and recorded run links |
| `qei-architecture.txt` and `config/projects.json` | User design brief, L2 | Intended project types and testing strategies |
| `public-notes.json` | Short attributed summaries of official public docs, L5 within product-documentation scope | Tool behavior and permission concepts |
| `data/synthetic/*.json` | User-requested fictional demonstration corpus, explicitly labeled synthetic | Cross-source QE traceability, authority conflicts and failure scenarios |
| `data/mcp_samples/*.json` | Additional fictional Jira/Confluence/SharePoint documentation with readable Markdown | Future native-MCP mapping fixtures, not captured tool output |

The CSV is frozen, not a live TestOps feed. Its names and execution records are treated as sample evidence. Public documentation about Slack or Confluence is not evidence of access to a company's Slack or Confluence content. CXE and SPROG have design profiles but no execution rows; they are not silently equated with WebOps or MyKC.

Every generated CSV record carries `source_rows`, so an aggregate can be traced to every contributing row. The original-source link selects the first row; inspect the complete row list for aggregate reconciliation. Repository links track `main`, so this POC is not an immutable external citation archive; the evaluation's corpus hash ties a run to normalized content.

## Normalized export schema

Import a JSON array of documents. Required fields:

```json
[
  {
    "source_type": "jira",
    "source_id": "REPLACE-WITH-NAMESPACED-ID",
    "project": "BSP Services",
    "document_type": "requirement",
    "title": "Replace with approved source title",
    "authoritative_level": 5,
    "updated_at": null,
    "url": "https://your-approved-source.example/document",
    "access_scope": "project:BSP Services",
    "owner": "Source owner",
    "content": "Replace with authorized source text",
    "relationships": [],
    "facts": {}
  }
]
```

This is a schema illustration, not a business record and not ingested. Source types are `jira`, `confluence`, `sharepoint`, `bitbucket`, `slack`, `katalon`, `testops`, and `architecture`. Source IDs must be globally unique in the corpus. Preserve original URLs and real source update times; never substitute ingestion time for freshness. Unknown dates are `null`.

Relationships are `{ "target": "existing-source-id", "type": "IMPLEMENTS", "evidence_source_id": "this-source-id", "evidence_quote": "Exact supporting text from this source." }`. Declare links only when recorded by a source; similarity is not a relationship. The referenced quote must occur in source content. CSV-derived relationships use original row provenance instead. Missing targets, unsupported assertions and links between synthetic and non-synthetic records fail ingestion. For conflict detection, give records the same `entity_id` and a structured `facts` object with comparable fields. Conflicts without structured assertions may not be detected; operators must verify that facts match source text.

Synthetic records also include `synthetic: true`, `dataset`, `approval_status`, `version` and `created_at`. They use `SYN-` IDs and real GitHub export URLs. Synthetic tests and runs do not imply execution coverage of the original CSV. CXE and SPROG now have fictional executions, but still have no supplied CSV rows.

The documentation fixtures also retain a QEI-owned `mcp_provenance` object and synthetic native-key aliases. Its locator fields are examples to map after discovering an actual server's schema; they are not a declaration of that server's output format. `source_permissions_verified: false` and null tool/retrieval fields explicitly indicate no native read occurred. Public scope applies only because these records are fictional. Never reuse it for actual MCP results. See [native MCP data guide](native-mcp-data-guide.md).

Use `public` only for explicitly approved public information. Restricted exports require `project:<exact project name>`. Missing/invalid scopes fail validation. The import process assumes an authorized operator has resolved source ACLs and inherited restrictions; it does not call vendor permission APIs. Derived summaries must be at least as restricted as all contributing records, and public text must not reveal restricted identifiers or content.

## Cleaning and snapshots

Ingestion decodes HTML entities, removes scripts/styles/tags, normalizes whitespace, validates required fields, rejects invalid dates and negative/non-finite durations, and deduplicates execution IDs. Chunk windows never cross document boundaries. The build fails on malformed input instead of replacing the index with partly validated content.

The corpus is English and small enough for a reproducible JSON store. The generated `data/index.json` contains source metadata, chunks, BM25 counts, 96-dimensional vectors and their fitted projection. Its corpus hash covers content and metadata, including permissions, dates and relationships. Loading the app reads this snapshot; it does not refetch vendor history. The first launch builds it from included files if absent. Rebuild after an approved export update. Recommended future cadence is nightly, but no scheduler is implemented.

## Authority and freshness

Authority levels 1–5 are operator-assigned metadata, not automatic truth scores. L5 approved domain sources can outweigh informal discussion, but an official tool manual cannot establish an application's requirements. This POC's CSV is L3 and its design profiles L2.

TestOps observations become dated after 7 days; product documentation after 180 days; other records after 30 days. Unknown dates are explicitly shown. Historical queries can use dated sources, while questions about current behavior abstain when no current evidence exists. These cutoffs are in `freshness()` and should become organization-level configuration for production.

## Identity and deployment

The sample corpus is publication-approved. The active Python/Streamlit public demo has no login and grants no private scopes. `QueryOptions.grants` exists for trusted server-side integration and tests only; the UI never supplies grants. A real enterprise deployment must implement verified identity mapping before serving private sources. The old Sites dispatcher settings apply only to the archived React version, not to this Python app.

Document scope filters run before ranking and graph expansion, and metadata links are filtered to eligible neighbors. This is coarse project-level authorization; it is not a replacement for per-document source ACL synchronization. Do not publish private test fixtures or indexes in this public repository.
