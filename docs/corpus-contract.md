# Corpus ownership and import contract

The user approved public upload of the sample dataset. This permission does not extend to future enterprise exports. Keep those outside the public Git index and deploy them only into an appropriately restricted environment.

## Source inventory

| Input | Ownership and authority | Use |
|---|---|---|
| `katalon_testops_sample_dataset.csv` | User-supplied sample, L3 | Observed test results and recorded run links |
| `qei-architecture.txt` and `config/projects.json` | User design brief, L2 | Intended project types and testing strategies |
| `public-notes.json` | Short attributed summaries of official public docs, L5 within product-documentation scope | Tool behavior and permission concepts |

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

Relationships are `{ "target": "existing-source-id", "type": "implements" }`. Declare links only when recorded by a source; similarity is not a relationship. For conflict detection, give records the same `entity_id` and a structured `facts` object with comparable fields. Conflicts without structured assertions may not be detected.

Use `public` only for explicitly approved public information. Restricted exports require `project:<exact project name>`. Missing/invalid scopes fail validation. The import process assumes an authorized operator has resolved source ACLs and inherited restrictions; it does not call vendor permission APIs. Derived summaries must be at least as restricted as all contributing records, and public text must not reveal restricted identifiers or content.

## Cleaning and snapshots

Ingestion decodes HTML entities, removes scripts/styles/tags, normalizes whitespace, validates required fields, rejects invalid dates and negative/non-finite durations, and deduplicates execution IDs. Chunk windows never cross document boundaries. The build fails on malformed input instead of replacing the index with partly validated content.

The corpus is English and small enough for a reproducible JSON store. The index contains source metadata, chunks, BM25 counts, 96-dimensional vectors and their fitted projection. Loading a page reads this snapshot; it does not refetch vendor history. Rebuild after an approved export update. Recommended future cadence is nightly, but no scheduler is implemented.

## Authority and freshness

Authority levels 1–5 are operator-assigned metadata, not automatic truth scores. L5 approved domain sources can outweigh informal discussion, but an official tool manual cannot establish an application's requirements. This POC's CSV is L3 and its design profiles L2.

TestOps observations become dated after 7 days; product documentation after 180 days; other records after 30 days. Unknown dates are explicitly shown. Historical queries can use dated sources, while questions about current behavior abstain when no current evidence exists. These cutoffs are in `freshness()` and should become organization-level configuration for production.

## Identity and deployment

The sample corpus is publication-approved. For restricted documents, default sessions have no project grants. Only enable `QEI_TRUST_SITES_IDENTITY=true` behind the trusted Sites dispatcher, which supplies authenticated user IDs. Map those IDs to exact projects with server secret `QEI_USER_PROJECTS`. Never trust that header from a raw public server or accept browser-submitted project grants.

Document scope filters run before ranking and graph expansion, and metadata links are filtered to eligible neighbors. This is coarse project-level authorization; it is not a replacement for per-document source ACL synchronization. Do not publish private test fixtures or indexes in this public repository.
