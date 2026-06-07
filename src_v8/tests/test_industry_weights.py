#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests — Industry Weights Engine + REST (F-13)
===============================================
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

# ═══════════════════════════════════════════════════════════════════════════════
#  Engine Tests
# ═══════════════════════════════════════════════════════════════════════════════

from core.engines.industry_weights import (
    CIRCULOS,
    INDUSTRIES,
    DEFAULT_WEIGHTS,
    IndustryWeightsEngine,
    get_industry_weights_engine,
    reset_industry_weights_engine,
)


class TestIndustryWeightsEngine:
    """Tests for IndustryWeightsEngine."""

    def setup_method(self):
        reset_industry_weights_engine()
        self.engine = IndustryWeightsEngine()

    # ── Initialization ────────────────────────────────────────────────────

    def test_init(self):
        assert self.engine is not None
        assert self.engine.total_feedback == 0

    def test_industries_list(self):
        assert len(self.engine.industries) == 15
        assert "Tecnologia" in self.engine.industries
        assert "Beleza & Cosméticos" in self.engine.industries

    def test_circles_list(self):
        assert len(self.engine.circles) == 16
        assert "Música Popular" in self.engine.circles
        assert "Empreendedorismo" in self.engine.circles

    def test_default_weights_defined(self):
        """All 15 industries must have default weights."""
        assert len(DEFAULT_WEIGHTS) == 15
        for ind in INDUSTRIES:
            assert ind in DEFAULT_WEIGHTS

    # ── Get weights ───────────────────────────────────────────────────────

    def test_get_weights_basic(self):
        w = self.engine.get_weights("Tecnologia")
        assert len(w) == 16
        assert w["Tecnologia"] == 1.0
        assert w["Empreendedorismo"] == 0.8

    def test_get_weights_all_circles_present(self):
        w = self.engine.get_weights("Alimentação & Bebidas")
        for circle in CIRCULOS:
            assert circle in w
            assert 0.0 <= w[circle] <= 1.0

    def test_get_weights_unknown_industry_raises(self):
        with pytest.raises(ValueError, match="Unknown industry"):
            self.engine.get_weights("Não Existe")

    def test_get_all_weights(self):
        all_w = self.engine.get_all_weights()
        assert len(all_w) == 15
        for ind in INDUSTRIES:
            assert ind in all_w
            assert len(all_w[ind]) == 16

    def test_get_weights_unmapped_circle_uses_default(self):
        """Circle not explicitly mapped gets default_circle_weight."""
        w = self.engine.get_weights("Tecnologia")
        # "Religiosidade" is NOT in Tecnologia's DEFAULT_WEIGHTS
        assert w["Religiosidade"] == 0.2  # default_circle_weight

    # ── Apply weight ──────────────────────────────────────────────────────

    def test_apply_industry_weight(self):
        result = self.engine.apply_industry_weight("Tecnologia", "Tecnologia", 0.8)
        assert result["weight"] == 1.0
        assert result["weighted_momentum"] == 0.8
        assert result["weight_source"] == "default"

    def test_apply_industry_weight_low(self):
        result = self.engine.apply_industry_weight("Tecnologia", "Arte Urbana", 1.0)
        assert result["weight"] == 0.3
        assert result["weighted_momentum"] == 0.3

    # ── Rank signals ──────────────────────────────────────────────────────

    def test_rank_signals_for_industry(self):
        signals = [
            {"signal_id": "s1", "circle": "Tecnologia", "momentum": 0.5},
            {"signal_id": "s2", "circle": "Religiosidade", "momentum": 0.9},
            {"signal_id": "s3", "circle": "Empreendedorismo", "momentum": 0.7},
        ]
        ranked = self.engine.rank_signals_for_industry("Tecnologia", signals)
        # s3: 0.7 * 0.8 = 0.56, s1: 0.5 * 1.0 = 0.5, s2: 0.9 * 0.2 = 0.18
        assert ranked[0]["signal_id"] == "s3"
        assert ranked[1]["signal_id"] == "s1"
        assert ranked[2]["signal_id"] == "s2"

    def test_rank_signals_with_circulo_key(self):
        signals = [{"id": "x", "circulo": "Gastronomia", "momentum": 0.8}]
        ranked = self.engine.rank_signals_for_industry("Alimentação & Bebidas", signals)
        assert ranked[0]["industry_weight"] == 1.0

    # ── Feedback ──────────────────────────────────────────────────────────

    def test_submit_feedback_positive(self):
        result = self.engine.submit_feedback("Tecnologia", "Humor & Memes", True)
        assert result["status"] == "recorded"
        assert result["feedback_count"] == 1
        assert self.engine.total_feedback == 1

    def test_submit_feedback_negative(self):
        result = self.engine.submit_feedback("Tecnologia", "Humor & Memes", False)
        assert result["status"] == "recorded"
        assert result["new_weight"] < result["default_weight"]

    def test_submit_feedback_invalid_industry(self):
        with pytest.raises(ValueError, match="Unknown industry"):
            self.engine.submit_feedback("NãoExiste", "Tecnologia", True)

    def test_submit_feedback_invalid_circle(self):
        with pytest.raises(ValueError, match="Unknown circle"):
            self.engine.submit_feedback("Tecnologia", "NãoExiste", True)

    def test_feedback_learning_effect(self):
        """After sufficient positive feedback, learned weight should rise."""
        for _ in range(5):
            self.engine.submit_feedback("Tecnologia", "Religiosidade", True)
        # Default is 0.2; after 5 positive feedbacks, should be > 0.2
        w = self.engine.get_weights("Tecnologia", use_learned=True)
        assert w["Religiosidade"] > 0.2

    def test_feedback_negative_learning(self):
        """After sufficient negative feedback, learned weight should drop."""
        for _ in range(5):
            self.engine.submit_feedback("Tecnologia", "Tecnologia", False)
        w = self.engine.get_weights("Tecnologia", use_learned=True)
        assert w["Tecnologia"] < 1.0

    def test_feedback_below_min_uses_default(self):
        """Before min_feedback_to_learn, use default."""
        # min_feedback_to_learn = 3
        self.engine.submit_feedback("Tecnologia", "Religiosidade", True)
        self.engine.submit_feedback("Tecnologia", "Religiosidade", True)
        # Only 2 feedbacks, need 3
        w = self.engine.get_weights("Tecnologia", use_learned=True)
        assert w["Religiosidade"] == 0.2  # still default

    def test_feedback_at_min_uses_learned(self):
        """At min_feedback_to_learn, switch to learned."""
        for _ in range(3):
            self.engine.submit_feedback("Tecnologia", "Religiosidade", True)
        w = self.engine.get_weights("Tecnologia", use_learned=True)
        assert w["Religiosidade"] > 0.2

    def test_max_feedback_cap(self):
        """Feedback store caps at max_feedback_per_pair."""
        engine = IndustryWeightsEngine({"max_feedback_per_pair": 5})
        for _ in range(10):
            engine.submit_feedback("Tecnologia", "Tecnologia", True)
        pair = ("Tecnologia", "Tecnologia")
        assert len(engine._feedback_store[pair]) == 5

    def test_batch_feedback(self):
        items = [
            {"industry": "Tecnologia", "circle": "Humor & Memes", "useful": True},
            {"industry": "Educação", "circle": "Literatura", "useful": False},
            {"industry": "INVALID", "circle": "Tecnologia", "useful": True},
        ]
        result = self.engine.batch_feedback(items)
        assert result["processed"] == 2
        assert result["failed"] == 1

    # ── A/B Testing ───────────────────────────────────────────────────────

    def test_ab_test_basic(self):
        signals = [
            {"signal_id": "s1", "circle": "Tecnologia", "momentum": 0.8},
            {"signal_id": "s2", "circle": "Humor & Memes", "momentum": 0.6},
        ]
        ground_truth = {"s1": True, "s2": False}
        result = self.engine.run_ab_test("Tecnologia", signals, ground_truth)
        assert "winner" in result
        assert result["industry"] == "Tecnologia"
        assert result["sample_size"] == 2

    def test_ab_test_history(self):
        signals = [{"signal_id": "s1", "circle": "Tecnologia", "momentum": 0.5}]
        self.engine.run_ab_test("Tecnologia", signals, {"s1": True})
        self.engine.run_ab_test("Educação", signals, {"s1": False})
        history = self.engine.get_ab_history()
        assert len(history) == 2

    def test_ab_test_invalid_industry(self):
        with pytest.raises(ValueError):
            self.engine.run_ab_test("NãoExiste", [], {})

    # ── Stats & Export ────────────────────────────────────────────────────

    def test_stats(self):
        s = self.engine.stats()
        assert s["total_industries"] == 15
        assert s["total_circles"] == 16
        assert s["total_weight_pairs"] == 240  # 15 × 16
        assert s["total_feedback"] == 0

    def test_stats_after_feedback(self):
        self.engine.submit_feedback("Tecnologia", "Tecnologia", True)
        s = self.engine.stats()
        assert s["total_feedback"] == 1
        assert s["feedback_pairs_active"] == 1

    def test_export_weights(self):
        exp = self.engine.export_weights()
        assert "default" in exp
        assert "learned" in exp
        assert len(exp["default"]) == 15

    def test_export_after_learning(self):
        self.engine.submit_feedback("Tecnologia", "Humor & Memes", True)
        exp = self.engine.export_weights()
        assert "Tecnologia" in exp["learned"]
        assert "Humor & Memes" in exp["learned"]["Tecnologia"]

    # ── Reset ─────────────────────────────────────────────────────────────

    def test_reset(self):
        self.engine.submit_feedback("Tecnologia", "Tecnologia", True)
        self.engine.reset()
        assert self.engine.total_feedback == 0
        s = self.engine.stats()
        assert s["learned_weight_pairs"] == 0

    # ── Singleton ─────────────────────────────────────────────────────────

    def test_singleton(self):
        reset_industry_weights_engine()
        e1 = get_industry_weights_engine()
        e2 = get_industry_weights_engine()
        assert e1 is e2

    def test_singleton_reset(self):
        e1 = get_industry_weights_engine()
        reset_industry_weights_engine()
        e2 = get_industry_weights_engine()
        assert e1 is not e2


# ═══════════════════════════════════════════════════════════════════════════════
#  API Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestIndustryWeightsAPI:
    """Tests for Industry Weights REST endpoints."""

    @pytest.fixture
    def client(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from api.endpoints.industry import router as industry_router

        reset_industry_weights_engine()
        app = FastAPI()
        app.include_router(industry_router)
        return TestClient(app)

    def setup_method(self):
        reset_industry_weights_engine()

    # ── GET /industries ───────────────────────────────────────────────────

    def test_list_industries(self, client):
        r = client.get("/api/v8/industry/industries")
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["total_industries"] == 15
        assert data["total_circles"] == 16

    # ── GET /weights/{industry} ───────────────────────────────────────────

    def test_get_weights(self, client):
        r = client.get("/api/v8/industry/weights/Tecnologia")
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["industry"] == "Tecnologia"
        assert len(data["weights"]) == 16

    def test_get_weights_invalid(self, client):
        r = client.get("/api/v8/industry/weights/Invalid")
        assert r.status_code == 400

    # ── GET /weights ──────────────────────────────────────────────────────

    def test_get_all_weights(self, client):
        r = client.get("/api/v8/industry/weights")
        assert r.status_code == 200
        data = r.json()["data"]
        assert len(data) == 15

    # ── POST /feedback ────────────────────────────────────────────────────

    def test_submit_feedback(self, client):
        r = client.post(
            "/api/v8/industry/feedback",
            json={"industry": "Tecnologia", "circle": "Humor & Memes", "useful": True},
        )
        assert r.status_code == 200
        assert r.json()["data"]["status"] == "recorded"

    def test_submit_feedback_invalid(self, client):
        r = client.post(
            "/api/v8/industry/feedback",
            json={"industry": "NãoExiste", "circle": "Tecnologia", "useful": True},
        )
        assert r.status_code == 400

    # ── POST /feedback/batch ──────────────────────────────────────────────

    def test_batch_feedback(self, client):
        r = client.post(
            "/api/v8/industry/feedback/batch",
            json={
                "feedbacks": [
                    {"industry": "Tecnologia", "circle": "Tecnologia", "useful": True},
                    {"industry": "Educação", "circle": "Literatura", "useful": False},
                ]
            },
        )
        assert r.status_code == 200
        assert r.json()["data"]["processed"] == 2

    # ── POST /apply ───────────────────────────────────────────────────────

    def test_apply_weight(self, client):
        r = client.post(
            "/api/v8/industry/apply",
            json={"industry": "Tecnologia", "circle": "Tecnologia", "base_momentum": 0.9},
        )
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["weighted_momentum"] == 0.9  # 0.9 * 1.0

    # ── POST /rank ────────────────────────────────────────────────────────

    def test_rank_signals(self, client):
        r = client.post(
            "/api/v8/industry/rank",
            json={
                "industry": "Tecnologia",
                "signals": [
                    {"signal_id": "s1", "circle": "Tecnologia", "momentum": 0.5},
                    {"signal_id": "s2", "circle": "Empreendedorismo", "momentum": 0.7},
                ],
            },
        )
        assert r.status_code == 200
        ranked = r.json()["data"]["ranked_signals"]
        assert ranked[0]["signal_id"] == "s2"

    # ── POST /ab-test ─────────────────────────────────────────────────────

    def test_ab_test(self, client):
        r = client.post(
            "/api/v8/industry/ab-test",
            json={
                "industry": "Tecnologia",
                "signals": [
                    {"signal_id": "s1", "circle": "Tecnologia", "momentum": 0.5},
                ],
                "ground_truth": {"s1": True},
            },
        )
        assert r.status_code == 200
        assert "winner" in r.json()["data"]

    # ── GET /ab-test/history ──────────────────────────────────────────────

    def test_ab_history(self, client):
        r = client.get("/api/v8/industry/ab-test/history")
        assert r.status_code == 200

    # ── GET /export ───────────────────────────────────────────────────────

    def test_export(self, client):
        r = client.get("/api/v8/industry/export")
        assert r.status_code == 200
        data = r.json()["data"]
        assert "default" in data
        assert "learned" in data

    # ── GET /stats ────────────────────────────────────────────────────────

    def test_stats(self, client):
        r = client.get("/api/v8/industry/stats")
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["total_industries"] == 15
