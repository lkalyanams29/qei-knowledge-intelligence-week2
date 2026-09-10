from __future__ import annotations
import copy
from dataclasses import replace
from datetime import datetime, timezone
import json
import unittest
from unittest.mock import patch

from data.mock_data import synthetic_documents
from graph_builder import build_graph, eligible_documents, link_entities, load_corpus, query_plan, traverse
from graph_rag import GraphRAG
from llm import Selection, select_claims
from settings import QueryOptions, freshness


class PythonRAGTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = load_corpus()
        cls.rag = GraphRAG(cls.corpus)
        cls.options = QueryOptions(now=datetime(2026, 9, 10, 12, tzinfo=timezone.utc))

    def test_synthetic_generation_deterministic(self):
        self.assertEqual(synthetic_documents(), synthetic_documents())
        self.assertEqual(len(synthetic_documents()), 72)
        self.assertTrue(all(d["synthetic"] and d["source_id"].startswith("SYN-") for d in synthetic_documents()))

    def test_seven_synthetic_sources(self):
        self.assertEqual({d["source_type"] for d in synthetic_documents()},
                         {"jira", "confluence", "sharepoint", "bitbucket", "slack", "katalon", "testops"})

    def test_graph_edges_have_citable_evidence(self):
        docs = {d["source_id"]: d for d in synthetic_documents()}
        for doc in docs.values():
            for rel in doc["relationships"]:
                self.assertIn(rel["target"], docs)
                self.assertIn(rel["evidence_quote"], doc["content"])
                self.assertEqual(rel["evidence_source_id"], doc["source_id"])

    def test_three_hops_find_execution(self):
        result = self.rag.answer("Which execution outcome is linked to SYN-BSP-REQ-001?", self.options)
        run = next(e for e in result["evidence"] if e["source_id"] == "SYN-BSP-RUN-001")
        self.assertEqual(run["hop"], 3)

    def test_exact_id_not_adjacent(self):
        result = self.rag.answer("Show SYN-BSP-REQ-999", self.options)
        self.assertEqual(result["status"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(result["evidence"], [])

    def test_cross_project_refuses(self):
        result = self.rag.answer("Show SYN-BSP-REQ-001", replace(self.options, project="Salesforce"))
        self.assertEqual(result["evidence"], [])

    def test_private_scope_denied_before_graph(self):
        corpus = copy.deepcopy(self.corpus)
        for doc in corpus["documents"]:
            if doc.get("synthetic") and doc["project"] == "BSP Services":
                doc["access_scope"] = "project:BSP Services"
        rag = GraphRAG(corpus)
        denied = rag.answer("Show SYN-BSP-REQ-001", self.options)
        self.assertNotIn("SYN-BSP-PR-001", json.dumps(denied))
        self.assertEqual(denied["evidence"], [])
        allowed = rag.answer("Show SYN-BSP-REQ-001", replace(self.options, grants=frozenset({"BSP Services"})))
        self.assertTrue(allowed["evidence"])

    def test_unavailable_source_not_attached(self):
        result = self.rag.answer("Which execution outcome is linked to SYN-BSP-REQ-001?",
                                 replace(self.options, unavailable=frozenset({"testops"})))
        self.assertEqual(result["status"], "SOURCE_UNAVAILABLE")
        self.assertTrue(all(e["source_type"] != "testops" for e in result["evidence"]))

    def test_conflict_disclosed_preferred_authority(self):
        result = self.rag.answer("What confirmation window governs SYN-BSP-REQ-001?", self.options)
        self.assertEqual(result["status"], "CONFLICTING_EVIDENCE")
        self.assertIn(result["conflicts"][0]["preferred_source_id"], {"SYN-BSP-REQ-001", "SYN-BSP-DECISION-001"})

    def test_missing_artifact_not_invented(self):
        result = self.rag.answer("Which step definition supports KT-101-TC-001?", self.options)
        self.assertEqual(result["status"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(result["claims"], [])

    def test_synthetic_not_current_production(self):
        result = self.rag.answer("What is the current production status of SYN-BSP-RUN-001?", self.options)
        self.assertEqual(result["claims"], [])

    def test_stale_csv_refuses_current(self):
        result = self.rag.answer("What is the current status of KT-101-TC-001?", self.options)
        self.assertEqual(result["status"], "INSUFFICIENT_EVIDENCE")

    def test_date_only_and_missing_freshness(self):
        doc = {"updated_at": "2026-09-01", "source_type": "confluence", "document_type": "specification"}
        self.assertEqual(freshness(doc, self.options.now), "current")
        self.assertEqual(freshness({**doc, "updated_at": None}, self.options.now), "unknown")

    def test_ambiguous_alias_clarifies(self):
        docs = {"A": {"title": "Release checklist"}, "B": {"title": "Release checklist"}}
        seeds, error = link_entities('Explain "Release checklist"', docs)
        self.assertEqual(seeds, [])
        self.assertIn("Ambiguous", error)

    def test_node_hop_context_budgets(self):
        opts = replace(self.options, max_nodes=5, max_hops=1, top_k=2, max_context_words=250)
        result = self.rag.answer("Show SYN-BSP-REQ-001", opts)
        self.assertLessEqual(len(result["evidence"]), 2)
        self.assertLessEqual(sum(len(e["content"].split()) for e in result["evidence"]), 250)
        expanded = next(t for t in result["trace"] if t["stage"] == "expand")
        self.assertLessEqual(expanded["visited_records"], 5)

    def test_same_corpus_and_budget_baselines(self):
        for strategy in ("graph", "hybrid", "vector"):
            result = self.rag.answer("Which pull request implements SYN-BSP-REQ-001?", self.options, strategy)
            attach = next(t for t in result["trace"] if t["stage"] == "attach")
            self.assertEqual(attach["top_k"], 8)
            self.assertEqual(attach["max_context_words"], 1400)

    def test_quotes_exact_source_and_owner_answer(self):
        result = self.rag.answer("Who approved SYN-WEB-PR-001?", self.options)
        lookup = {e["chunk_id"]: e for e in result["evidence"]}
        for claim in result["claims"]:
            self.assertIn(claim["quote"], lookup[claim["chunk_id"]]["content"])
        self.assertTrue(any("Nora Kim approved" in c["quote"] for c in result["claims"]))

    def test_injection_quarantined(self):
        corpus = copy.deepcopy(self.corpus)
        for doc in corpus["documents"]:
            if doc["id"] == "SYN-BSP-REQ-001":
                doc["injection_flag"] = True
        result = GraphRAG(corpus).answer("Show SYN-BSP-REQ-001", self.options)
        self.assertEqual(result["evidence"], [])

    def test_model_failure_safe_fallback(self):
        with patch("graph_rag.select_claims", side_effect=TimeoutError):
            result = self.rag.answer("Who approved SYN-WEB-PR-001?", replace(self.options, use_model=True))
        self.assertEqual(result["generation"], "extractive-fallback")
        self.assertTrue(result["claims"])

    def test_model_empty_selection_refuses(self):
        with patch("graph_rag.select_claims", return_value=[]):
            result = self.rag.answer("Who approved SYN-WEB-PR-001?", replace(self.options, use_model=True))
        self.assertEqual(result["status"], "INSUFFICIENT_EVIDENCE")

    def test_invalid_model_indices_rejected(self):
        class Fake:
            def invoke(self, messages): return {"selected": [99]}
        with self.assertRaises(ValueError):
            select_claims("question", [{"quote": "source", "source_id": "a"}], Fake())
        with self.assertRaises(ValueError):
            Selection.model_validate({"selected": [True]})

    def test_validation(self):
        with self.assertRaises(ValueError): self.rag.answer("x")
        with self.assertRaises(ValueError): QueryOptions(max_hops=9)

    def test_original_csv_run_membership_preserved(self):
        result = self.rag.answer("Which tests executed in RUN-00001?", self.options)
        self.assertTrue(any(c["source_id"] == "RUN-00001" and "Test identifiers in this run:" in c["quote"]
                            for c in result["claims"]))

    def test_outage_does_not_override_current_state_refusal(self):
        result = self.rag.answer("What is the current production status of SYN-BSP-RUN-001?",
                                 replace(self.options, unavailable=frozenset({"slack"})))
        self.assertEqual(result["claims"], [])

    def test_invalid_relationships_fail_closed(self):
        from scripts.ingest import validate, validate_relationships
        docs = [validate(d) for d in synthetic_documents()]
        validate_relationships(docs)
        docs[0]["access_scope"] = "project:BSP Services"
        with self.assertRaises(ValueError): validate_relationships(docs)
        docs = [validate(d) for d in synthetic_documents()]
        docs[1]["relationships"][0]["evidence_quote"] = "invented relationship"
        with self.assertRaises(ValueError): validate_relationships(docs)


if __name__ == "__main__":
    unittest.main()
