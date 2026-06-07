#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests — Cross-Impact Matrix Engine + REST (F-14)
==================================================
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

from core.cross_impact import (
    PEST_CATEGORIES,
    CrossImpactEngine,
    get_cross_impact_engine,
    reset_cross_impact_engine,
    DEFAULT_MORPHOLOGICAL_STATES,
)


class TestCrossImpactEngine:
    """Tests for CrossImpactEngine."""

    def setup_method(self):
        reset_cross_impact_engine()
        self.engine = CrossImpactEngine()

    # ── Initialization ────────────────────────────────────────────────────

    def test_init(self):
        assert self.engine is not None
        assert self.engine.total_observations == 0

    def test_categories(self):
        assert len(self.engine.categories) == 4
        assert "Political" in self.engine.categories
        assert "Economic" in self.engine.categories
        assert "Social" in self.engine.categories
        assert "Technological" in self.engine.categories

    def test_default_morpho_states(self):
        states = self.engine.get_morphological_states()
        assert len(states) == 4
        for cat in PEST_CATEGORIES:
            assert cat in states
            assert len(states[cat]) == 4

    # ── Record impact ─────────────────────────────────────────────────────

    def test_record_impact_basic(self):
        r = self.engine.record_impact("Political", "Economic", 0.7)
        assert r["status"] == "recorded"
        assert r["source"] == "Political"
        assert r["target"] == "Economic"
        assert r["strength"] == 0.7
        assert self.engine.total_observations == 1

    def test_record_impact_clips_strength(self):
        r = self.engine.record_impact("Political", "Social", 1.5)
        assert r["strength"] == 1.0

    def test_record_impact_negative_clips(self):
        r = self.engine.record_impact("Political", "Social", -0.5)
        assert r["strength"] == 0.0

    def test_record_impact_invalid_source(self):
        with pytest.raises(ValueError, match="Invalid source"):
            self.engine.record_impact("Invalid", "Economic", 0.5)

    def test_record_impact_invalid_target(self):
        with pytest.raises(ValueError, match="Invalid target"):
            self.engine.record_impact("Political", "Invalid", 0.5)

    def test_record_impact_same_source_target(self):
        with pytest.raises(ValueError, match="different"):
            self.engine.record_impact("Political", "Political", 0.5)

    def test_record_multiple(self):
        self.engine.record_impact("Political", "Economic", 0.6)
        self.engine.record_impact("Political", "Economic", 0.8)
        self.engine.record_impact("Social", "Technological", 0.4)
        assert self.engine.total_observations == 3

    def test_max_entries_cap(self):
        engine = CrossImpactEngine({"max_entries_per_pair": 5})
        for i in range(10):
            engine.record_impact("Political", "Economic", 0.5)
        pair = ("Political", "Economic")
        assert len(engine._observations[pair]) == 5

    # ── Record from PEST results ──────────────────────────────────────────

    def test_record_from_pest_results(self):
        results = [
            {"primary": "Political", "secondary": "Economic", "confidence": 0.8},
            {"primary": "Social", "secondary": "Technological", "confidence": 0.6},
            {"primary": "Economic", "secondary": None, "confidence": 0.9},  # skipped
        ]
        r = self.engine.record_from_pest_results(results)
        assert r["recorded"] == 2
        assert r["skipped"] == 1
        assert self.engine.total_observations == 2

    def test_record_from_pest_same_primary_secondary(self):
        results = [
            {"primary": "Social", "secondary": "Social", "confidence": 0.5},
        ]
        r = self.engine.record_from_pest_results(results)
        assert r["skipped"] == 1

    def test_batch_record(self):
        impacts = [
            {"source": "Political", "target": "Economic", "strength": 0.7},
            {"source": "Social", "target": "Technological", "strength": 0.5},
            {"source": "Invalid", "target": "Economic", "strength": 0.3},
        ]
        r = self.engine.batch_record(impacts)
        assert r["recorded"] == 2
        assert r["failed"] == 1

    # ── Matrix ────────────────────────────────────────────────────────────

    def test_matrix_empty(self):
        data = self.engine.get_matrix()
        assert "matrix" in data
        assert "details" in data
        matrix = data["matrix"]
        for src in PEST_CATEGORIES:
            for tgt in PEST_CATEGORIES:
                assert matrix[src][tgt] == 0.0

    def test_matrix_with_data(self):
        self.engine.record_impact("Political", "Economic", 0.6)
        self.engine.record_impact("Political", "Economic", 0.8)
        data = self.engine.get_matrix()
        matrix = data["matrix"]
        assert matrix["Political"]["Economic"] == 0.7  # avg of 0.6 and 0.8
        # Diagonal always 0
        assert matrix["Political"]["Political"] == 0.0

    def test_matrix_details_significance(self):
        # Need min_observations (default=3) to be significant
        for _ in range(3):
            self.engine.record_impact("Political", "Economic", 0.7)
        data = self.engine.get_matrix()
        details = data["details"]
        assert details["Political"]["Economic"]["significant"] is True

        # Only 1 observation = not significant
        self.engine.record_impact("Social", "Technological", 0.5)
        data = self.engine.get_matrix()
        details = data["details"]
        assert details["Social"]["Technological"]["significant"] is False

    # ── Strongest impacts ─────────────────────────────────────────────────

    def test_strongest_impacts_empty(self):
        result = self.engine.get_strongest_impacts()
        assert result == []

    def test_strongest_impacts(self):
        for _ in range(5):
            self.engine.record_impact("Political", "Economic", 0.9)
        for _ in range(5):
            self.engine.record_impact("Social", "Technological", 0.3)
        result = self.engine.get_strongest_impacts(top_n=2)
        assert len(result) == 2
        assert result[0]["source"] == "Political"
        assert result[0]["avg_strength"] > result[1]["avg_strength"]

    # ── Causal chains ─────────────────────────────────────────────────────

    def test_causal_chains_empty(self):
        chains = self.engine.detect_causal_chains()
        assert chains == []

    def test_causal_chains_basic(self):
        # Create P→E and E→S with enough observations
        for _ in range(5):
            self.engine.record_impact("Political", "Economic", 0.7)
        for _ in range(5):
            self.engine.record_impact("Economic", "Social", 0.6)
        chains = self.engine.detect_causal_chains(min_strength=0.3)
        # Should find P→E→S
        chain_strs = [" → ".join(c["chain"]) for c in chains]
        assert any("Political" in s and "Economic" in s and "Social" in s for s in chain_strs)

    def test_causal_chains_no_loops(self):
        """Chains should not revisit nodes."""
        for _ in range(5):
            self.engine.record_impact("Political", "Economic", 0.7)
            self.engine.record_impact("Economic", "Political", 0.6)
        chains = self.engine.detect_causal_chains(min_strength=0.3)
        for chain in chains:
            assert len(chain["chain"]) == len(set(chain["chain"]))

    # ── Morphological Analysis ────────────────────────────────────────────

    def test_set_morphological_states(self):
        custom = {
            "Political": ["Estado A", "Estado B"],
            "Economic": ["Boom", "Bust"],
        }
        self.engine.set_morphological_states(custom)
        states = self.engine.get_morphological_states()
        assert states["Political"] == ["Estado A", "Estado B"]
        assert states["Economic"] == ["Boom", "Bust"]
        # Untouched categories keep defaults
        assert len(states["Social"]) == 4

    def test_generate_scenarios(self):
        scenarios = self.engine.generate_scenarios(max_scenarios=5)
        assert isinstance(scenarios, list)
        for s in scenarios:
            assert "name" in s
            assert "dimensions" in s
            assert "plausibility" in s
            assert len(s["dimensions"]) == 4

    def test_generate_scenarios_with_impact_data(self):
        """Scenarios should exist and reflect recorded impacts."""
        for _ in range(5):
            self.engine.record_impact("Political", "Economic", 0.9)
            self.engine.record_impact("Economic", "Social", 0.7)
            self.engine.record_impact("Social", "Technological", 0.6)
        scenarios = self.engine.generate_scenarios(max_scenarios=10)
        assert len(scenarios) > 0
        # Plausibilities should be non-negative
        for s in scenarios:
            assert s["plausibility"] >= 0.0

    def test_generate_scenarios_custom_states(self):
        self.engine.set_morphological_states({
            "Political": ["Estado P1", "Estado P2"],
            "Economic": ["Estado E1", "Estado E2"],
            "Social": ["Estado S1", "Estado S2"],
            "Technological": ["Estado T1", "Estado T2"],
        })
        scenarios = self.engine.generate_scenarios(max_scenarios=20)
        # 2^4 = 16 combinations max
        assert len(scenarios) <= 16

    # ── Stats & Export ────────────────────────────────────────────────────

    def test_stats(self):
        s = self.engine.stats()
        assert s["engine"] == "CrossImpactEngine"
        assert s["total_observations"] == 0
        assert s["matrix_size"] == "4x4"
        assert len(s["categories"]) == 4

    def test_stats_after_records(self):
        self.engine.record_impact("Political", "Economic", 0.5)
        s = self.engine.stats()
        assert s["total_observations"] == 1
        assert s["active_pairs"] == 1
        assert "Political→Economic" in s["observation_counts"]

    def test_export(self):
        self.engine.record_impact("Political", "Economic", 0.7)
        exp = self.engine.export_data()
        assert "matrix" in exp
        assert "observations_count" in exp
        assert "morphological_states" in exp

    # ── Reset ─────────────────────────────────────────────────────────────

    def test_reset(self):
        self.engine.record_impact("Political", "Economic", 0.5)
        self.engine.reset()
        assert self.engine.total_observations == 0
        data = self.engine.get_matrix()
        assert data["total_observations"] == 0

    # ── Singleton ─────────────────────────────────────────────────────────

    def test_singleton(self):
        reset_cross_impact_engine()
        e1 = get_cross_impact_engine()
        e2 = get_cross_impact_engine()
        assert e1 is e2

    def test_singleton_reset(self):
        e1 = get_cross_impact_engine()
        reset_cross_impact_engine()
        e2 = get_cross_impact_engine()
        assert e1 is not e2


# ═══════════════════════════════════════════════════════════════════════════════
#  API Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestCrossImpactAPI:
    """Tests for Cross-Impact Matrix REST endpoints."""

    @pytest.fixture
    def client(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from api.endpoints.cross_impact import router as cross_impact_router

        reset_cross_impact_engine()
        app = FastAPI()
        app.include_router(cross_impact_router)
        return TestClient(app)

    def setup_method(self):
        reset_cross_impact_engine()

    # ── POST /record ──────────────────────────────────────────────────────

    def test_record(self, client):
        r = client.post(
            "/api/v8/cross-impact/record",
            json={"source": "Political", "target": "Economic", "strength": 0.7},
        )
        assert r.status_code == 200
        assert r.json()["data"]["status"] == "recorded"

    def test_record_invalid(self, client):
        r = client.post(
            "/api/v8/cross-impact/record",
            json={"source": "Invalid", "target": "Economic", "strength": 0.5},
        )
        assert r.status_code == 400

    def test_record_same_source_target(self, client):
        r = client.post(
            "/api/v8/cross-impact/record",
            json={"source": "Political", "target": "Political", "strength": 0.5},
        )
        assert r.status_code == 400

    # ── POST /record/batch ────────────────────────────────────────────────

    def test_batch_record(self, client):
        r = client.post(
            "/api/v8/cross-impact/record/batch",
            json={
                "impacts": [
                    {"source": "Political", "target": "Economic", "strength": 0.7},
                    {"source": "Social", "target": "Technological", "strength": 0.5},
                ]
            },
        )
        assert r.status_code == 200
        assert r.json()["data"]["recorded"] == 2

    # ── POST /record/pest-results ─────────────────────────────────────────

    def test_record_from_pest(self, client):
        r = client.post(
            "/api/v8/cross-impact/record/pest-results",
            json={
                "pest_results": [
                    {"primary": "Political", "secondary": "Economic", "confidence": 0.8},
                    {"primary": "Social", "secondary": None, "confidence": 0.5},
                ]
            },
        )
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["recorded"] == 1
        assert data["skipped"] == 1

    # ── GET /matrix ───────────────────────────────────────────────────────

    def test_get_matrix(self, client):
        r = client.get("/api/v8/cross-impact/matrix")
        assert r.status_code == 200
        data = r.json()["data"]
        assert "matrix" in data
        assert len(data["matrix"]) == 4

    # ── GET /strongest ────────────────────────────────────────────────────

    def test_strongest(self, client):
        r = client.get("/api/v8/cross-impact/strongest")
        assert r.status_code == 200

    # ── GET /chains ───────────────────────────────────────────────────────

    def test_chains(self, client):
        r = client.get("/api/v8/cross-impact/chains")
        assert r.status_code == 200
        assert "chains" in r.json()["data"]

    # ── GET /morphological/states ─────────────────────────────────────────

    def test_get_morpho_states(self, client):
        r = client.get("/api/v8/cross-impact/morphological/states")
        assert r.status_code == 200
        data = r.json()["data"]
        assert len(data) == 4

    # ── POST /morphological/states ────────────────────────────────────────

    def test_set_morpho_states(self, client):
        r = client.post(
            "/api/v8/cross-impact/morphological/states",
            json={"states": {"Political": ["Estado A", "Estado B"]}},
        )
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["Political"] == ["Estado A", "Estado B"]

    # ── GET /morphological/scenarios ──────────────────────────────────────

    def test_scenarios(self, client):
        r = client.get("/api/v8/cross-impact/morphological/scenarios")
        assert r.status_code == 200
        data = r.json()["data"]
        assert "scenarios" in data

    # ── GET /export ───────────────────────────────────────────────────────

    def test_export(self, client):
        r = client.get("/api/v8/cross-impact/export")
        assert r.status_code == 200
        data = r.json()["data"]
        assert "matrix" in data

    # ── GET /stats ────────────────────────────────────────────────────────

    def test_stats(self, client):
        r = client.get("/api/v8/cross-impact/stats")
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["engine"] == "CrossImpactEngine"
        assert data["total_observations"] == 0
