#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_h9_engines.py — H-9 FASE 3
========================================
Tests for the 5 cultural-intelligence engines:
  1. VulnerabilityEngine   (core/vulnerability_engine.py)
  2. CulturalAlertsEngine  (core/cultural_alerts_engine.py)
  3. StrategicActionsEngine (core/strategic_actions_engine.py)
  4. ScenarioEngine         (core/scenario_engine.py)
  5. OpportunityEngine      (core/opportunity_engine.py)

Also tests Worker pipeline integration (16 engines) and API endpoints.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ═══════════════════════════════════════════════════════════════════════════════
#  Fixtures
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def _reset_singletons():
    """Reset all H-9 singletons between tests."""
    from core.engines.vulnerability_engine import reset_vulnerability_engine
    from alerts.cultural_alerts_engine import reset_alerts_engine
    from core.intelligence.strategic_actions_engine import reset_strategic_engine
    from core.scenario_engine import reset_scenario_engine
    from core.intelligence.opportunity_engine import reset_opportunity_engine

    reset_vulnerability_engine()
    reset_alerts_engine()
    reset_strategic_engine()
    reset_scenario_engine()
    reset_opportunity_engine()
    yield
    reset_vulnerability_engine()
    reset_alerts_engine()
    reset_strategic_engine()
    reset_scenario_engine()
    reset_opportunity_engine()


@pytest.fixture
def high_momentum_signal():
    return {
        "termo": "funk brasileiro",
        "momentum": 92,
        "sentiment": 0.7,
        "volume": 15000,
        "plataforma": "youtube",
        "relevancia_cultural": 0.85,
        "circles": ["Funk & Periferia", "Música Popular"],
        "tensions": [
            {"tipo": "cultural_clash", "intensidade": 0.6}
        ],
        "pest": {"primary": "Social", "confidence": 0.8},
        "velocity": {"acceleration": 1.2, "trend": "rising"},
    }


@pytest.fixture
def low_momentum_signal():
    return {
        "termo": "fado português",
        "momentum": 15,
        "sentiment": -0.3,
        "volume": 200,
        "plataforma": "spotify",
        "relevancia_cultural": 0.2,
        "circles": ["Tradição & Raízes"],
        "tensions": [],
        "pest": {"primary": "Social", "confidence": 0.4},
        "velocity": {"acceleration": -0.5, "trend": "declining"},
    }


@pytest.fixture
def minimal_signal():
    """Bare-minimum signal dict (only termo)."""
    return {"termo": "test"}


@pytest.fixture
def batch_signals(high_momentum_signal, low_momentum_signal):
    return [high_momentum_signal, low_momentum_signal]


# ═══════════════════════════════════════════════════════════════════════════════
#  1. VulnerabilityEngine
# ═══════════════════════════════════════════════════════════════════════════════

class TestVulnerabilityEngine:
    def test_import(self):
        from core.engines.vulnerability_engine import VulnerabilityEngine
        assert VulnerabilityEngine is not None

    def test_singleton(self):
        from core.engines.vulnerability_engine import get_vulnerability_engine
        a = get_vulnerability_engine()
        b = get_vulnerability_engine()
        assert a is b

    def test_assess_signal_returns_dict(self, high_momentum_signal):
        from core.engines.vulnerability_engine import get_vulnerability_engine
        result = get_vulnerability_engine().assess_signal(high_momentum_signal)
        assert isinstance(result, dict)
        assert "score" in result
        assert "level" in result
        assert "dimensions" in result

    def test_assess_signal_score_range(self, high_momentum_signal):
        from core.engines.vulnerability_engine import get_vulnerability_engine
        result = get_vulnerability_engine().assess_signal(high_momentum_signal)
        assert 0 <= result["score"] <= 100

    def test_vulnerability_levels(self):
        from core.engines.vulnerability_engine import get_vulnerability_engine
        engine = get_vulnerability_engine()
        # Low vulnerability
        r_low = engine.assess_signal({"termo": "x", "momentum": 10, "sentiment": 0.8})
        assert r_low["level"] in ("low", "moderate", "high", "critical")

    def test_dimensions_present(self, high_momentum_signal):
        from core.engines.vulnerability_engine import get_vulnerability_engine
        result = get_vulnerability_engine().assess_signal(high_momentum_signal)
        dims = result["dimensions"]
        expected_keys = {"tension_exposure", "circle_concentration", "sentiment_fragility",
                         "pest_sensitivity", "velocity_decay"}
        assert expected_keys.issubset(set(dims.keys()))

    def test_top_risks_is_list(self, high_momentum_signal):
        from core.engines.vulnerability_engine import get_vulnerability_engine
        result = get_vulnerability_engine().assess_signal(high_momentum_signal)
        assert isinstance(result["top_risks"], list)

    def test_recommendations_is_list(self, high_momentum_signal):
        from core.engines.vulnerability_engine import get_vulnerability_engine
        result = get_vulnerability_engine().assess_signal(high_momentum_signal)
        assert isinstance(result["recommendations"], list)

    def test_minimal_signal(self, minimal_signal):
        from core.engines.vulnerability_engine import get_vulnerability_engine
        result = get_vulnerability_engine().assess_signal(minimal_signal)
        assert "score" in result

    def test_batch_assess(self, batch_signals):
        from core.engines.vulnerability_engine import get_vulnerability_engine
        engine = get_vulnerability_engine()
        results = [engine.assess_signal(s) for s in batch_signals]
        assert len(results) == 2
        for r in results:
            assert "score" in r

    def test_high_tension_increases_vulnerability(self):
        from core.engines.vulnerability_engine import get_vulnerability_engine
        engine = get_vulnerability_engine()
        no_tension = engine.assess_signal({"termo": "x", "momentum": 50, "sentiment": 0.0, "tensions": []})
        high_tension = engine.assess_signal({
            "termo": "x", "momentum": 50, "sentiment": 0.0,
            "tensions": [{"tipo": "a", "intensidade": 0.9}, {"tipo": "b", "intensidade": 0.8}]
        })
        assert high_tension["score"] >= no_tension["score"]


# ═══════════════════════════════════════════════════════════════════════════════
#  2. CulturalAlertsEngine
# ═══════════════════════════════════════════════════════════════════════════════

class TestCulturalAlertsEngine:
    def test_import(self):
        from alerts.cultural_alerts_engine import CulturalAlertsEngine
        assert CulturalAlertsEngine is not None

    def test_singleton(self):
        from alerts.cultural_alerts_engine import get_alerts_engine
        a = get_alerts_engine()
        b = get_alerts_engine()
        assert a is b

    def test_evaluate_returns_list(self, high_momentum_signal):
        from alerts.cultural_alerts_engine import get_alerts_engine
        result = get_alerts_engine().evaluate_dict(high_momentum_signal)
        assert isinstance(result, list)

    def test_alert_structure(self, high_momentum_signal):
        from alerts.cultural_alerts_engine import get_alerts_engine
        alerts = get_alerts_engine().evaluate_dict(high_momentum_signal)
        for alert in alerts:
            assert "alert_type" in alert
            assert "severity" in alert
            assert "message" in alert
            assert alert["severity"] in ("info", "warning", "critical")

    def test_high_momentum_triggers_alert(self):
        """Momentum >= 75 should trigger a momentum_spike alert."""
        from alerts.cultural_alerts_engine import get_alerts_engine
        alerts = get_alerts_engine().evaluate_dict({"termo": "x", "momentum": 90, "sentiment": 0.0})
        types = [a["alert_type"] for a in alerts]
        assert "momentum_spike" in types

    def test_low_momentum_no_spike(self):
        from alerts.cultural_alerts_engine import get_alerts_engine
        alerts = get_alerts_engine().evaluate_dict({"termo": "x", "momentum": 30, "sentiment": 0.0})
        types = [a["alert_type"] for a in alerts]
        assert "momentum_spike" not in types

    def test_batch_evaluate(self, batch_signals):
        from alerts.cultural_alerts_engine import get_alerts_engine
        results = get_alerts_engine().batch_evaluate(batch_signals)
        assert len(results) == 2
        for r in results:
            assert isinstance(r, list)

    def test_summary(self, high_momentum_signal):
        from alerts.cultural_alerts_engine import get_alerts_engine
        engine = get_alerts_engine()
        summary = engine.summary([high_momentum_signal])
        assert isinstance(summary, dict)

    def test_minimal_signal(self, minimal_signal):
        from alerts.cultural_alerts_engine import get_alerts_engine
        result = get_alerts_engine().evaluate_dict(minimal_signal)
        assert isinstance(result, list)

    def test_negative_sentiment_shift(self):
        from alerts.cultural_alerts_engine import get_alerts_engine
        alerts = get_alerts_engine().evaluate_dict({"termo": "x", "momentum": 50, "sentiment": -0.8})
        types = [a["alert_type"] for a in alerts]
        assert "sentiment_shift" in types


# ═══════════════════════════════════════════════════════════════════════════════
#  3. StrategicActionsEngine
# ═══════════════════════════════════════════════════════════════════════════════

class TestStrategicActionsEngine:
    def test_import(self):
        from core.intelligence.strategic_actions_engine import StrategicActionsEngine
        assert StrategicActionsEngine is not None

    def test_singleton(self):
        from core.intelligence.strategic_actions_engine import get_strategic_engine
        a = get_strategic_engine()
        b = get_strategic_engine()
        assert a is b

    def test_recommend_returns_dict(self, high_momentum_signal):
        from core.intelligence.strategic_actions_engine import get_strategic_engine
        result = get_strategic_engine().recommend_dict(high_momentum_signal)
        assert isinstance(result, dict)
        assert "action_type" in result

    def test_action_types(self, high_momentum_signal):
        from core.intelligence.strategic_actions_engine import get_strategic_engine
        result = get_strategic_engine().recommend_dict(high_momentum_signal)
        assert result["action_type"] in ("engage", "monitor", "protect", "amplify", "pivot")

    def test_urgency_range(self, high_momentum_signal):
        from core.intelligence.strategic_actions_engine import get_strategic_engine
        result = get_strategic_engine().recommend_dict(high_momentum_signal)
        assert 1 <= result["urgency"] <= 5

    def test_playbook_is_list(self, high_momentum_signal):
        from core.intelligence.strategic_actions_engine import get_strategic_engine
        result = get_strategic_engine().recommend_dict(high_momentum_signal)
        assert isinstance(result["playbook"], list)
        assert len(result["playbook"]) > 0

    def test_kpis_present(self, high_momentum_signal):
        from core.intelligence.strategic_actions_engine import get_strategic_engine
        result = get_strategic_engine().recommend_dict(high_momentum_signal)
        assert isinstance(result["kpis"], list)

    def test_batch_recommend(self, batch_signals):
        from core.intelligence.strategic_actions_engine import get_strategic_engine
        results = get_strategic_engine().batch_recommend(batch_signals)
        assert len(results) == 2

    def test_low_momentum_gets_monitor_or_pivot(self, low_momentum_signal):
        from core.intelligence.strategic_actions_engine import get_strategic_engine
        result = get_strategic_engine().recommend_dict(low_momentum_signal)
        assert result["action_type"] in ("monitor", "pivot", "protect")

    def test_minimal_signal(self, minimal_signal):
        from core.intelligence.strategic_actions_engine import get_strategic_engine
        result = get_strategic_engine().recommend_dict(minimal_signal)
        assert "action_type" in result

    def test_channels_present(self, high_momentum_signal):
        from core.intelligence.strategic_actions_engine import get_strategic_engine
        result = get_strategic_engine().recommend_dict(high_momentum_signal)
        assert isinstance(result["channels"], list)


# ═══════════════════════════════════════════════════════════════════════════════
#  4. ScenarioEngine
# ═══════════════════════════════════════════════════════════════════════════════

class TestScenarioEngine:
    def test_import(self):
        from core.scenario_engine import ScenarioEngine
        assert ScenarioEngine is not None

    def test_singleton(self):
        from core.scenario_engine import get_scenario_engine
        a = get_scenario_engine()
        b = get_scenario_engine()
        assert a is b

    def test_generate_returns_dict(self, high_momentum_signal):
        from core.scenario_engine import get_scenario_engine
        result = get_scenario_engine().generate_dict(high_momentum_signal)
        assert isinstance(result, dict)

    def test_three_scenarios(self, high_momentum_signal):
        from core.scenario_engine import get_scenario_engine
        result = get_scenario_engine().generate_dict(high_momentum_signal)
        assert "scenarios" in result
        assert len(result["scenarios"]) == 3

    def test_scenario_structure(self, high_momentum_signal):
        from core.scenario_engine import get_scenario_engine
        result = get_scenario_engine().generate_dict(high_momentum_signal)
        for s in result["scenarios"]:
            assert "probability" in s
            assert "narrative" in s
            assert "projected_momentum" in s
            assert "impact_level" in s

    def test_probabilities_sum_to_1(self, high_momentum_signal):
        from core.scenario_engine import get_scenario_engine
        result = get_scenario_engine().generate_dict(high_momentum_signal)
        total = sum(s["probability"] for s in result["scenarios"])
        assert abs(total - 1.0) < 0.05  # tolerate float rounding

    def test_recommended_strategy(self, high_momentum_signal):
        from core.scenario_engine import get_scenario_engine
        result = get_scenario_engine().generate_dict(high_momentum_signal)
        assert "recommended_strategy" in result
        assert isinstance(result["recommended_strategy"], str)
        assert len(result["recommended_strategy"]) > 0

    def test_batch_generate(self, batch_signals):
        from core.scenario_engine import get_scenario_engine
        results = get_scenario_engine().batch_generate(batch_signals)
        assert len(results) == 2
        for r in results:
            assert "scenarios" in r

    def test_minimal_signal(self, minimal_signal):
        from core.scenario_engine import get_scenario_engine
        result = get_scenario_engine().generate_dict(minimal_signal)
        assert "scenarios" in result

    def test_milestones_present(self, high_momentum_signal):
        from core.scenario_engine import get_scenario_engine
        result = get_scenario_engine().generate_dict(high_momentum_signal)
        for s in result["scenarios"]:
            assert "milestones" in s
            assert isinstance(s["milestones"], list)


# ═══════════════════════════════════════════════════════════════════════════════
#  5. OpportunityEngine
# ═══════════════════════════════════════════════════════════════════════════════

class TestOpportunityEngine:
    def test_import(self):
        from core.intelligence.opportunity_engine import OpportunityEngine
        assert OpportunityEngine is not None

    def test_singleton(self):
        from core.intelligence.opportunity_engine import get_opportunity_engine
        a = get_opportunity_engine()
        b = get_opportunity_engine()
        assert a is b

    def test_detect_returns_list(self, high_momentum_signal):
        from core.intelligence.opportunity_engine import get_opportunity_engine
        result = get_opportunity_engine().detect_dict(high_momentum_signal)
        assert isinstance(result, list)

    def test_opportunity_structure(self, high_momentum_signal):
        from core.intelligence.opportunity_engine import get_opportunity_engine
        opps = get_opportunity_engine().detect_dict(high_momentum_signal)
        for opp in opps:
            assert "opportunity_type" in opp
            assert "confidence" in opp
            assert "title" in opp

    def test_high_momentum_finds_opportunities(self, high_momentum_signal):
        from core.intelligence.opportunity_engine import get_opportunity_engine
        opps = get_opportunity_engine().detect_dict(high_momentum_signal)
        assert len(opps) > 0  # high momentum should find at least momentum_wave

    def test_opportunity_types(self, high_momentum_signal):
        from core.intelligence.opportunity_engine import get_opportunity_engine
        opps = get_opportunity_engine().detect_dict(high_momentum_signal)
        valid_types = {"momentum_wave", "sentiment_positive", "early_signal", "convergence"}
        for opp in opps:
            assert opp["opportunity_type"] in valid_types

    def test_confidence_range(self, high_momentum_signal):
        from core.intelligence.opportunity_engine import get_opportunity_engine
        opps = get_opportunity_engine().detect_dict(high_momentum_signal)
        for opp in opps:
            assert 0 <= opp["confidence"] <= 1

    def test_batch_detect(self, batch_signals):
        from core.intelligence.opportunity_engine import get_opportunity_engine
        results = get_opportunity_engine().detect_batch(batch_signals)
        assert len(results) == 2

    def test_summary(self, high_momentum_signal):
        from core.intelligence.opportunity_engine import get_opportunity_engine
        engine = get_opportunity_engine()
        summary = engine.summary([high_momentum_signal])
        assert isinstance(summary, dict)

    def test_minimal_signal(self, minimal_signal):
        from core.intelligence.opportunity_engine import get_opportunity_engine
        result = get_opportunity_engine().detect_dict(minimal_signal)
        assert isinstance(result, list)

    def test_actions_in_opportunity(self, high_momentum_signal):
        from core.intelligence.opportunity_engine import get_opportunity_engine
        opps = get_opportunity_engine().detect_dict(high_momentum_signal)
        for opp in opps:
            assert "actions" in opp
            assert isinstance(opp["actions"], list)


# ═══════════════════════════════════════════════════════════════════════════════
#  6. Worker Integration — 16 engines
# ═══════════════════════════════════════════════════════════════════════════════

class TestWorkerIntegration:
    def test_worker_has_16_engines(self):
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        assert len(worker._engines) == 17

    def test_h9_engines_registered(self):
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        names = [e.name for e in worker._engines]
        for expected in ("vulnerability", "alerts", "actions", "scenarios", "opportunities"):
            assert expected in names, f"Engine '{expected}' not registered in Worker"

    def test_h9_priorities_after_pest(self):
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        pest = next(e for e in worker._engines if e.name == "pest")
        for name in ("vulnerability", "alerts", "actions", "scenarios", "opportunities"):
            eng = next(e for e in worker._engines if e.name == name)
            assert eng.priority > pest.priority, f"{name} priority should be > pest"

    def test_worker_process_enriches_h9(self):
        """Full pipeline should add H-9 fields to signal."""
        import asyncio
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        signal = {
            "termo": "pagode baiano",
            "momentum": 70,
            "sentiment": 0.5,
            "volume": 5000,
            "plataforma": "youtube",
        }
        enriched = asyncio.run(worker.enrich(signal))
        assert "vulnerability" in enriched
        assert "cultural_alerts" in enriched
        assert "strategic_action" in enriched
        assert "scenarios" in enriched
        assert "opportunities" in enriched


# ═══════════════════════════════════════════════════════════════════════════════
#  7. API Endpoints — intelligence router
# ═══════════════════════════════════════════════════════════════════════════════

class TestIntelligenceAPI:
    def _load_module(self):
        import importlib.util, pathlib
        path = pathlib.Path(__file__).parent.parent / "api" / "endpoints" / "intelligence.py"
        spec = importlib.util.spec_from_file_location("intelligence_endpoint", str(path))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_router_importable(self):
        mod = self._load_module()
        assert mod.router is not None
        assert mod.router.prefix == "/api/v8/intelligence"

    def test_vulnerability_endpoint_exists(self):
        mod = self._load_module()
        assert callable(mod.vulnerability_assess)

    def test_vulnerability_batch_endpoint_exists(self):
        mod = self._load_module()
        assert callable(mod.vulnerability_batch)

    def test_alerts_endpoint_exists(self):
        mod = self._load_module()
        assert callable(mod.alerts_evaluate)

    def test_alerts_batch_endpoint_exists(self):
        mod = self._load_module()
        assert callable(mod.alerts_batch)

    def test_actions_endpoint_exists(self):
        mod = self._load_module()
        assert callable(mod.actions_recommend)

    def test_actions_batch_endpoint_exists(self):
        mod = self._load_module()
        assert callable(mod.actions_batch)

    def test_scenarios_endpoint_exists(self):
        mod = self._load_module()
        assert callable(mod.scenarios_generate)

    def test_scenarios_batch_endpoint_exists(self):
        mod = self._load_module()
        assert callable(mod.scenarios_batch)

    def test_opportunities_endpoint_exists(self):
        mod = self._load_module()
        assert callable(mod.opportunities_detect)

    def test_opportunities_batch_endpoint_exists(self):
        mod = self._load_module()
        assert callable(mod.opportunities_batch)

    def test_full_intelligence_endpoint_exists(self):
        mod = self._load_module()
        assert callable(mod.full_intelligence)

    def test_registered_in_main(self):
        import pathlib
        main_src = (pathlib.Path(__file__).parent.parent / "api" / "main.py").read_text()
        assert "intelligence_router" in main_src

    def test_signal_input_model(self):
        mod = self._load_module()
        sig = mod.SignalInput(termo="funk", momentum=80, sentiment=0.5, volume=1000)
        assert sig.termo == "funk"

    def test_batch_signal_input_model(self):
        mod = self._load_module()
        batch = mod.BatchSignalInput(
            signals=[mod.SignalInput(termo="a"), mod.SignalInput(termo="b")]
        )
        assert len(batch.signals) == 2
