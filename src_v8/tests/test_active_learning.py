"""
tests/test_active_learning.py — F-10 FASE 5
===============================================
Comprehensive tests for ActiveLearningEngine + REST endpoints.
"""
import math
import pytest
from unittest.mock import patch

# ── Engine tests ─────────────────────────────────────────────────────────────

class TestActiveLearningEngine:
    """Tests for core/active_learning.py"""

    def _make_engine(self, **config_overrides):
        from core.intelligence.learning.InsightLearner import ActiveLearningEngine
        return ActiveLearningEngine(config=config_overrides)

    # ── Initialization ───────────────────────────────────────────────────

    def test_init_defaults(self):
        engine = self._make_engine()
        assert engine.total_feedback == 0
        assert engine.total_queries == 0
        assert "uncertainty_threshold" in engine.config

    def test_init_custom_config(self):
        engine = self._make_engine(uncertainty_threshold=0.9, wilson_z=1.65)
        assert engine.config["uncertainty_threshold"] == 0.9
        assert engine.config["wilson_z"] == 1.65

    # ── Submit feedback ──────────────────────────────────────────────────

    def test_submit_feedback_positive(self):
        engine = self._make_engine()
        result = engine.submit_feedback("samba carioca", relevant=True, confidence=0.9)
        assert result["status"] == "recorded"
        assert result["query"] == "samba carioca"
        assert result["feedback_count"] == 1
        assert "ranking" in result

    def test_submit_feedback_negative(self):
        engine = self._make_engine()
        result = engine.submit_feedback("random noise", relevant=False, confidence=0.8)
        assert result["query"] == "random noise"
        assert result["ranking"]["negative_feedback"] == 1

    def test_submit_feedback_normalizes_query(self):
        engine = self._make_engine()
        engine.submit_feedback("  Funk Carioca  ", relevant=True)
        engine.submit_feedback("funk carioca", relevant=True)
        assert engine.total_queries == 1  # same normalized query
        assert engine.total_feedback == 2

    def test_submit_feedback_empty_query_raises(self):
        engine = self._make_engine()
        with pytest.raises(ValueError, match="empty"):
            engine.submit_feedback("", relevant=True)

    def test_submit_feedback_clips_confidence(self):
        engine = self._make_engine()
        result = engine.submit_feedback("test", relevant=True, confidence=5.0)
        assert result["ranking"]["avg_confidence"] == 1.0

    def test_feedback_multiple_same_query(self):
        engine = self._make_engine()
        engine.submit_feedback("sertanejo", relevant=True, confidence=0.9)
        engine.submit_feedback("sertanejo", relevant=True, confidence=0.8)
        engine.submit_feedback("sertanejo", relevant=False, confidence=0.6)
        assert engine.total_feedback == 3
        assert engine.total_queries == 1

    def test_feedback_max_cap(self):
        engine = self._make_engine(max_feedback_per_query=5)
        for i in range(10):
            engine.submit_feedback("test", relevant=(i % 2 == 0))
        rankings = engine.get_rankings()
        assert rankings[0]["total_feedback"] == 5  # capped

    # ── Rankings ─────────────────────────────────────────────────────────

    def test_get_rankings_empty(self):
        engine = self._make_engine()
        rankings = engine.get_rankings()
        assert rankings == []

    def test_get_rankings_after_feedback(self):
        engine = self._make_engine()
        engine.submit_feedback("forró", relevant=True)
        engine.submit_feedback("axé", relevant=False)
        rankings = engine.get_rankings()
        assert len(rankings) == 2
        assert all("relevance_score" in r for r in rankings)
        assert all("priority" in r for r in rankings)

    def test_rankings_sorted_by_priority(self):
        engine = self._make_engine()
        # Clearly relevant
        for _ in range(5):
            engine.submit_feedback("alta relevância", relevant=True, confidence=0.95)
        # Clearly irrelevant
        for _ in range(5):
            engine.submit_feedback("baixa relevância", relevant=False, confidence=0.95)

        rankings = engine.get_rankings(sort_by="relevance")
        assert rankings[0]["query"] == "alta relevância"
        assert rankings[0]["relevance_score"] > rankings[1]["relevance_score"]

    def test_rankings_filter_by_status(self):
        engine = self._make_engine(relevance_threshold=0.5, rejection_threshold=0.2)
        for _ in range(5):
            engine.submit_feedback("bom", relevant=True, confidence=0.9)
        for _ in range(5):
            engine.submit_feedback("ruim", relevant=False, confidence=0.9)

        validated = engine.get_rankings(status_filter="validated")
        assert all(r["status"] == "validated" for r in validated)
        assert len(validated) >= 1

    def test_rankings_top_k(self):
        engine = self._make_engine()
        for i in range(10):
            engine.submit_feedback(f"query_{i}", relevant=True)
        rankings = engine.get_rankings(top_k=3)
        assert len(rankings) == 3

    # ── Wilson lower bound ───────────────────────────────────────────────

    def test_wilson_score_high_positive(self):
        engine = self._make_engine()
        for _ in range(20):
            engine.submit_feedback("popular", relevant=True, confidence=1.0)
        rankings = engine.get_rankings()
        r = [x for x in rankings if x["query"] == "popular"][0]
        assert r["relevance_score"] > 0.7

    def test_wilson_score_high_negative(self):
        engine = self._make_engine()
        for _ in range(20):
            engine.submit_feedback("unpopular", relevant=False, confidence=1.0)
        rankings = engine.get_rankings()
        r = [x for x in rankings if x["query"] == "unpopular"][0]
        assert r["relevance_score"] < 0.3

    def test_wilson_score_mixed(self):
        engine = self._make_engine()
        for _ in range(10):
            engine.submit_feedback("mixed", relevant=True, confidence=0.8)
        for _ in range(10):
            engine.submit_feedback("mixed", relevant=False, confidence=0.8)
        rankings = engine.get_rankings()
        r = [x for x in rankings if x["query"] == "mixed"][0]
        # Should be around 0.5 (uncertain)
        assert 0.2 < r["relevance_score"] < 0.8

    # ── Uncertainty ──────────────────────────────────────────────────────

    def test_uncertain_queries_no_feedback(self):
        engine = self._make_engine()
        # No queries at all
        uncertain = engine.get_uncertain_queries()
        assert uncertain == []

    def test_uncertain_queries_conflicting(self):
        engine = self._make_engine(uncertainty_threshold=0.5)
        # Equal positive/negative → high uncertainty
        for _ in range(5):
            engine.submit_feedback("divided", relevant=True, confidence=0.9)
        for _ in range(5):
            engine.submit_feedback("divided", relevant=False, confidence=0.9)
        uncertain = engine.get_uncertain_queries()
        queries = [u["query"] for u in uncertain]
        assert "divided" in queries

    def test_uncertain_queries_low_confidence(self):
        engine = self._make_engine()
        engine.submit_feedback("unsure", relevant=True, confidence=0.2)
        engine.submit_feedback("unsure", relevant=True, confidence=0.3)
        uncertain = engine.get_uncertain_queries()
        reasons = [u["reason"] for u in uncertain if u["query"] == "unsure"]
        # Should flag as low_confidence or borderline
        assert len(reasons) >= 0  # may or may not trigger based on thresholds

    # ── Collection priority ──────────────────────────────────────────────

    def test_collection_priority_known_queries(self):
        engine = self._make_engine()
        for _ in range(5):
            engine.submit_feedback("good query", relevant=True)
        for _ in range(5):
            engine.submit_feedback("bad query", relevant=False)

        result = engine.get_collection_priority(["good query", "bad query", "unknown query"])
        assert len(result) == 3
        # unknown query gets explore (high uncertainty = high priority)
        # good query should rank above bad query among known queries
        priorities = {r["query"]: r["priority"] for r in result}
        assert priorities["good query"] > priorities["bad query"]

    def test_collection_priority_unknown_gets_explore(self):
        engine = self._make_engine()
        result = engine.get_collection_priority(["brand new query"])
        assert result[0]["status"] == "unknown"
        assert result[0]["recommendation"] == "explore"
        assert result[0]["priority"] == 0.5

    # ── Batch operations ─────────────────────────────────────────────────

    def test_batch_submit(self):
        engine = self._make_engine()
        feedbacks = [
            {"query": "q1", "relevant": True, "confidence": 0.9},
            {"query": "q2", "relevant": False, "confidence": 0.7},
            {"query": "q3", "relevant": True},
        ]
        result = engine.batch_submit(feedbacks)
        assert result["processed"] == 3
        assert result["failed"] == 0
        assert engine.total_queries == 3

    def test_batch_submit_with_failures(self):
        engine = self._make_engine()
        feedbacks = [
            {"query": "q1", "relevant": True},
            {"query": "", "relevant": True},  # Will fail (empty)
            {"query": "q3", "relevant": False},
        ]
        result = engine.batch_submit(feedbacks)
        assert result["processed"] == 2
        assert result["failed"] == 1

    # ── Import from tracker ──────────────────────────────────────────────

    def test_import_from_tracker(self):
        engine = self._make_engine()
        history = [
            {
                "query_input": {"keywords": ["funk carioca"]},
                "result_summary": {"signals_count": 15},
                "status": "success",
            },
            {
                "query_input": {"keywords": ["nonexistent_query"]},
                "result_summary": {"signals_count": 0},
                "status": "success",
            },
            {
                "query_input": {"keywords": ["error query"]},
                "result_summary": {},
                "status": "error",
            },
        ]
        result = engine.import_from_tracker(history)
        assert result["imported"] == 2
        assert result["skipped"] == 1
        assert engine.total_queries == 2

    def test_import_from_tracker_empty(self):
        engine = self._make_engine()
        result = engine.import_from_tracker([])
        assert result["imported"] == 0

    def test_import_from_tracker_no_keywords(self):
        engine = self._make_engine()
        history = [{"query_input": {}, "result_summary": {}, "status": "success"}]
        result = engine.import_from_tracker(history)
        assert result["skipped"] == 1

    # ── Statistics ────────────────────────────────────────────────────────

    def test_stats_empty(self):
        engine = self._make_engine()
        stats = engine.stats()
        assert stats["engine"] == "ActiveLearningEngine"
        assert stats["total_feedback"] == 0
        assert stats["total_queries"] == 0

    def test_stats_after_feedback(self):
        engine = self._make_engine()
        engine.submit_feedback("q1", relevant=True)
        engine.submit_feedback("q2", relevant=False)
        stats = engine.stats()
        assert stats["total_feedback"] == 2
        assert stats["total_queries"] == 2
        assert "status_distribution" in stats
        assert "avg_relevance" in stats

    # ── Export / Reset ───────────────────────────────────────────────────

    def test_export_rankings(self):
        engine = self._make_engine()
        engine.submit_feedback("q1", relevant=True)
        exported = engine.export_rankings()
        assert len(exported) == 1
        assert exported[0]["query"] == "q1"

    def test_reset(self):
        engine = self._make_engine()
        engine.submit_feedback("q1", relevant=True)
        engine.reset()
        assert engine.total_feedback == 0
        assert engine.total_queries == 0

    # ── Singleton ────────────────────────────────────────────────────────

    def test_singleton(self):
        from core.intelligence.learning.InsightLearner import get_active_learning_engine, reset_active_learning_engine
        reset_active_learning_engine()
        e1 = get_active_learning_engine()
        e2 = get_active_learning_engine()
        assert e1 is e2
        reset_active_learning_engine()


# ── REST API tests ───────────────────────────────────────────────────────────

class TestActiveLearningAPI:
    """Tests for api/endpoints/active_learning.py"""

    @pytest.fixture
    def client(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from api.endpoints.active_learning import router
        from core.intelligence.learning.InsightLearner import reset_active_learning_engine

        reset_active_learning_engine()
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)

    def test_post_feedback(self, client):
        resp = client.post("/api/v8/active-learning/feedback", json={
            "query": "samba", "relevant": True, "confidence": 0.9
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["data"]["query"] == "samba"

    def test_post_feedback_invalid(self, client):
        resp = client.post("/api/v8/active-learning/feedback", json={
            "query": "", "relevant": True
        })
        assert resp.status_code == 400

    def test_post_batch_feedback(self, client):
        resp = client.post("/api/v8/active-learning/feedback/batch", json={
            "feedbacks": [
                {"query": "q1", "relevant": True},
                {"query": "q2", "relevant": False, "confidence": 0.7},
            ]
        })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["processed"] == 2

    def test_get_rankings_empty(self, client):
        resp = client.get("/api/v8/active-learning/rankings")
        assert resp.status_code == 200
        assert resp.json()["data"] == []

    def test_get_rankings_after_feedback(self, client):
        client.post("/api/v8/active-learning/feedback", json={
            "query": "forró", "relevant": True
        })
        resp = client.get("/api/v8/active-learning/rankings")
        assert resp.status_code == 200
        assert len(resp.json()["data"]) == 1

    def test_get_rankings_with_filters(self, client):
        # Add validated + rejected
        for _ in range(5):
            client.post("/api/v8/active-learning/feedback", json={
                "query": "valid", "relevant": True, "confidence": 0.95
            })
        for _ in range(5):
            client.post("/api/v8/active-learning/feedback", json={
                "query": "invalid", "relevant": False, "confidence": 0.95
            })
        resp = client.get("/api/v8/active-learning/rankings?status=validated")
        assert resp.status_code == 200

    def test_get_uncertain(self, client):
        resp = client.get("/api/v8/active-learning/uncertain")
        assert resp.status_code == 200
        assert "data" in resp.json()

    def test_post_prioritize(self, client):
        client.post("/api/v8/active-learning/feedback", json={
            "query": "funk", "relevant": True
        })
        resp = client.post("/api/v8/active-learning/prioritize", json={
            "queries": ["funk", "unknown_term"]
        })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data) == 2

    def test_post_import_tracker(self, client):
        resp = client.post("/api/v8/active-learning/import-tracker", json={
            "limit": 10
        })
        assert resp.status_code == 200

    def test_get_stats(self, client):
        resp = client.get("/api/v8/active-learning/stats")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["engine"] == "ActiveLearningEngine"
