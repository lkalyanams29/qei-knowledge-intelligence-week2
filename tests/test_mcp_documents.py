"""Fixture/normalization tests; none invokes or pretends to test a native server."""
from collections import Counter
from dataclasses import replace
from datetime import datetime, timezone
import json
import unittest

from data.mcp_documents import DATASET, ROOT, documentation_records
from graph_builder import eligible_documents, link_entities, load_corpus
from graph_rag import GraphRAG
from scripts.ingest import validate, validate_relationships
from settings import QueryOptions


class MCPDocumentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = documentation_records()
        cls.corpus = load_corpus()
        cls.engine = GraphRAG(cls.corpus)
        cls.options = QueryOptions(now=datetime(2026, 9, 10, 12, tzinfo=timezone.utc))

    def test_deterministic_counts(self):
        self.assertEqual(self.records, documentation_records())
        self.assertEqual(Counter(d["source_type"] for d in self.records), {"jira": 12, "confluence": 12, "sharepoint": 12})
        self.assertEqual(len({d["project"] for d in self.records}), 6)
        self.assertEqual(sum(len(d["relationships"]) for d in self.records), 60)

    def test_fixture_not_claimed_as_native_response(self):
        for doc in self.records:
            metadata = doc["mcp_provenance"]
            self.assertTrue(doc["synthetic"])
            self.assertEqual(doc["dataset"], DATASET)
            self.assertEqual(metadata["mode"], "synthetic_fixture")
            self.assertFalse(metadata["server_connected"])
            self.assertFalse(metadata["source_permissions_verified"])
            self.assertIsNone(metadata["tool_name"])
            self.assertIsNone(metadata["native_url"])
            self.assertIsNone(metadata["retrieved_at"])

    def test_readable_files_match_indexed_content(self):
        for doc in self.records:
            path = ROOT/"data/mcp_samples/documents"/doc["source_type"]/(doc["source_id"]+".md")
            text = path.read_text(encoding="utf-8")
            self.assertIn(doc["content"], text)
            self.assertIn("SYNTHETIC", text)
            self.assertIn("/blob/codex/python-streamlit-graphrag/", doc["url"])

    def test_all_relationships_valid_with_existing_corpus(self):
        validate_relationships(self.corpus["documents"])
        indexed = {d["id"] for d in self.corpus["documents"] if d.get("dataset") == DATASET}
        self.assertEqual(indexed, {d["source_id"] for d in self.records})
        for doc in self.records: validate(doc)

    def test_native_jira_key_resolves_and_full_acceptance_list_is_cited(self):
        result = self.engine.answer("What acceptance criteria are documented for SYNBSP-201?", self.options)
        evidence = next(e for e in result["evidence"] if e["source_id"] == "SYN-BSP-STORY-201")
        self.assertEqual(evidence["mcp_provenance"]["native_locator"]["issue_key"], "SYNBSP-201")
        quote = next(c["quote"] for c in result["claims"] if c["source_id"] == "SYN-BSP-STORY-201")
        self.assertIn("AC1:", quote)
        self.assertIn("AC4:", quote)
        self.assertIn(quote, evidence["content"])

    def test_cross_source_design_and_plan_retrieved(self):
        result = self.engine.answer("Which Confluence design and SharePoint test plan support SYNSF-201?", self.options)
        actual = {e["source_id"] for e in result["evidence"]}
        self.assertTrue({"SYN-SF-DESIGN-301", "SYN-SF-PLAN-401"}.issubset(actual))

    def test_jira_key_does_not_bypass_project_filter(self):
        result = self.engine.answer("Show SYNBSP-201", replace(self.options, project="Salesforce"))
        self.assertEqual(result["evidence"], [])

    def test_ambiguous_native_key_requires_clarification(self):
        documents = {"SYN-A-001": {"aliases": ["DEMO-123"]}, "SYN-B-001": {"aliases": ["DEMO-123"]}}
        seeds, error = link_entities("Show DEMO-123", documents)
        self.assertEqual(seeds, [])
        self.assertIn("Ambiguous", error)

    def test_planning_config_never_enables_a_server(self):
        config = json.loads((ROOT/"config/mcp_sources.json").read_text(encoding="utf-8"))
        for source in config["sources"]:
            self.assertFalse(source["enabled"])
            self.assertIsNone(source["endpoint"])
            self.assertEqual(source["tool_bindings"], {})
            self.assertEqual(source["allowed_intents"], ["search", "fetch"])

    def test_pending_checklists_are_not_release_signoffs(self):
        checklists = [d for d in self.records if d["document_type"] == "release_checklist"]
        self.assertEqual(len(checklists), 6)
        self.assertTrue(all(d["approval_status"] == "pending" and d["facts"]["release_approval"] == "Pending" for d in checklists))


if __name__ == "__main__":
    unittest.main()
