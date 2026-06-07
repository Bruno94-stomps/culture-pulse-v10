#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_risk_retrain.py — F-6 + F-7 FASE 3
================================================
Tests for RiskEngine (core/risk_engine.py) and RetrainTrigger (core/retrain_trigger.py).
Also covers api/endpoints/risk.py.
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
    from core.engines.risk_engine import reset_risk_engine
    from core.classifiers.retrain_trigger import reset_retrain_trigger

    reset_risk_engine()
    reset_retrain_trigger()
    yield
    reset_risk_engine()
    reset_retrain_trigger()


@pytest.fixture
def risk_engine():
    from core.engines.risk_engine import RiskEngine
    return RiskEngine()


@pytest.fixture
def retrain_trigger():
    from core.classifiers.retrain_trigger import RetrainTrigger
    return RetrainTrigger({"auto_execute": False, "cooldown_seconds": 0})


@pytest.fixture
def enriched_signal():
    return {
        "termo": "funk carioca",
        "momentum": 80,
        "sentiment": -0.4,
        "volume": 8000,
        "plataforma": "youtube",
        "vulnerability": {"score": 65, "level": "high"},
        "cultural_alerts": [
            {"alert_type": "momentum_spike", "severity": "warning", "message": "High momentum"},
            {"alert_type": "sentiment_shift", "severity": "critical", "message": "Negative shift"},
        ],
        "pest": {"primary": "Political", "confidence": 0.7},
    }


@pytest.fixture
def safe_signal():
    return {
        "termo": "bossa nova",
        "momentum": 30,
        "sentiment": 0.6,
        "volume": 500,
        "plataforma": "spotify",
    }


@pytest.fixture
def drift_alert_positive():
    """Simulated DriftAlert.to_dict() showing drift detected."""
    return {
        "is_drift": True,
        "p_value": 0.01,
        "threshold": 0.05,
        "severity": "high",
        "n_current": 100,
        "n_reference": 186,
        "feature_stats": {"mean_shift": 0.3},
    }


@pytest.fixture
def drift_alert_negative():
    """Simulated DriftAlert.to_dict() showing no drift."""
    return {
        "is_drift": False,
        "p_value": 0.42,
        "threshold": 0.05,
        "severity": "none",
        "n_current": 50,
        "n_reference": 186,
    }


# ═══════════════════════════════════════════════════════════════════════════════
#  1. RiskEngine — core
# ═══════════════════════════════════════════════════════════════════════════════

class TestRiskEngine:
    def test_import(self):
        from core.engines.risk_engine import RiskEngine
        assert RiskEngine is not None

    def test_singleton(self):
        from core.engines.risk_engine import get_risk_engine
        a = get_risk_engine()
        b = get_risk_engine()
        assert a is b

    def test_assess_returns_dict(self, risk_engine, enriched_signal):
        result = risk_engine.assess_dict(enriched_signal)
        assert isinstance(result, dict)
        assert "overall_score" in result
        assert "risk_level" in result
        assert "risk_label" in result

    def test_risk_score_range(self, risk_engine, enriched_signal):
        result = risk_engine.assess_dict(enriched_signal)
        assert 0 <= result["overall_score"] <= 100

    def test_risk_level_range(self, risk_engine, enriched_signal):
        result = risk_engine.assess_dict(enriched_signal)
        assert result["risk_level"] in (1, 2, 3, 4, 5)

    def test_risk_labels(self, risk_engine, enriched_signal):
        result = risk_engine.assess_dict(enriched_signal)
        assert result["risk_label"] in ("negligible", "low", "moderate", "high", "critical")

    def test_factors_present(self, risk_engine, enriched_signal):
        result = risk_engine.assess_dict(enriched_signal)
        factors = result["factors"]
        assert len(factors) == 5
        names = [f["name"] for f in factors]
        assert "vulnerability" in names
        assert "alert_severity" in names
        assert "pest_exposure" in names
        assert "sentiment_risk" in names
        assert "cluster_stability" in names

    def test_enriched_higher_risk_than_safe(self, risk_engine, enriched_signal, safe_signal):
        r1 = risk_engine.assess_dict(enriched_signal)
        r2 = risk_engine.assess_dict(safe_signal)
        assert r1["overall_score"] > r2["overall_score"]

    def test_mitigation_actions(self, risk_engine, enriched_signal):
        result = risk_engine.assess_dict(enriched_signal)
        assert isinstance(result["mitigation_actions"], list)
        assert len(result["mitigation_actions"]) > 0

    def test_confidence(self, risk_engine, enriched_signal):
        result = risk_engine.assess_dict(enriched_signal)
        assert 0 <= result["confidence"] <= 1

    def test_batch_assess(self, risk_engine, enriched_signal, safe_signal):
        results = risk_engine.batch_assess([enriched_signal, safe_signal])
        assert len(results) == 2

    def test_aggregate_risk(self, risk_engine, enriched_signal, safe_signal):
        result = risk_engine.aggregate_risk([enriched_signal, safe_signal])
        assert "overall_score" in result
        assert "signal_count" in result
        assert result["signal_count"] == 2
        assert "level_distribution" in result

    def test_aggregate_empty(self, risk_engine):
        result = risk_engine.aggregate_risk([])
        assert result["signal_count"] == 0
        assert result["risk_level"] == 1

    def test_minimal_signal(self, risk_engine):
        result = risk_engine.assess_dict({"termo": "test"})
        assert "overall_score" in result

    def test_negative_sentiment_increases_risk(self, risk_engine):
        pos = risk_engine.assess_dict({"termo": "x", "sentiment": 0.8})
        neg = risk_engine.assess_dict({"termo": "x", "sentiment": -0.8})
        assert neg["overall_score"] > pos["overall_score"]

    def test_political_pest_higher_than_social(self, risk_engine):
        political = risk_engine.assess_dict(
            {"termo": "x", "pest": {"primary": "Political", "confidence": 0.8}}
        )
        social = risk_engine.assess_dict(
            {"termo": "x", "pest": {"primary": "Social", "confidence": 0.8}}
        )
        assert political["overall_score"] > social["overall_score"]


# ═══════════════════════════════════════════════════════════════════════════════
#  2. RetrainTrigger — core
# ═══════════════════════════════════════════════════════════════════════════════

class TestRetrainTrigger:
    def test_import(self):
        from core.classifiers.retrain_trigger import RetrainTrigger
        assert RetrainTrigger is not None

    def test_singleton(self):
        from core.classifiers.retrain_trigger import get_retrain_trigger
        a = get_retrain_trigger()
        b = get_retrain_trigger()
        assert a is b

    def test_evaluate_no_drift(self, retrain_trigger, drift_alert_negative):
        event = retrain_trigger.evaluate_drift(drift_alert_negative)
        assert event.drift_detected is False
        assert event.retrain_triggered is False
        assert event.retrain_status == "skipped"

    def test_evaluate_drift_triggers_retrain(self, retrain_trigger, drift_alert_positive):
        event = retrain_trigger.evaluate_drift(drift_alert_positive)
        assert event.drift_detected is True
        assert event.retrain_triggered is True
        assert event.retrain_status == "triggered"  # auto_execute=False

    def test_evaluate_none_alert(self, retrain_trigger):
        event = retrain_trigger.evaluate_drift(None)
        assert event.retrain_status == "skipped"
        assert "No drift alert" in event.reason

    def test_cooldown_blocks_retrain(self):
        from core.classifiers.retrain_trigger import RetrainTrigger
        trigger = RetrainTrigger({"auto_execute": False, "cooldown_seconds": 999999})
        alert = {"is_drift": True, "p_value": 0.01, "severity": "high", "n_current": 100}

        # First should trigger
        e1 = trigger.evaluate_drift(alert)
        assert e1.retrain_triggered is True

        # Second should be blocked by cooldown
        e2 = trigger.evaluate_drift(alert)
        assert e2.retrain_triggered is False
        assert "cooldown" in e2.reason.lower()

    def test_min_signals_blocks_retrain(self):
        from core.classifiers.retrain_trigger import RetrainTrigger
        trigger = RetrainTrigger({"min_signals_for_retrain": 200, "cooldown_seconds": 0})
        alert = {"is_drift": True, "p_value": 0.01, "severity": "high", "n_current": 50}
        event = trigger.evaluate_drift(alert)
        assert event.retrain_triggered is False
        assert "insufficient" in event.reason.lower()

    def test_history_tracked(self, retrain_trigger, drift_alert_positive, drift_alert_negative):
        retrain_trigger.evaluate_drift(drift_alert_positive)
        retrain_trigger.evaluate_drift(drift_alert_negative)
        assert len(retrain_trigger.history) == 2

    def test_summary(self, retrain_trigger, drift_alert_positive):
        retrain_trigger.evaluate_drift(drift_alert_positive)
        summary = retrain_trigger.summary()
        assert isinstance(summary, dict)
        assert "total_evaluations" in summary
        assert summary["total_evaluations"] == 1
        assert summary["retrains_triggered"] == 1

    def test_config(self, retrain_trigger):
        config = retrain_trigger.config
        assert "p_value_threshold" in config
        assert "min_signals_for_retrain" in config
        assert "cooldown_seconds" in config

    def test_check_feedback_quality(self, retrain_trigger):
        result = retrain_trigger.check_feedback_quality()
        assert isinstance(result, dict)
        assert "feedback_available" in result
        assert "feedback_count" in result

    def test_retrain_event_to_dict(self):
        from core.classifiers.retrain_trigger import RetrainEvent
        event = RetrainEvent(drift_detected=True, p_value=0.02, retrain_status="triggered")
        d = event.to_dict()
        assert isinstance(d, dict)
        assert d["drift_detected"] is True
        assert d["p_value"] == 0.02


# ═══════════════════════════════════════════════════════════════════════════════
#  3. API endpoints
# ═══════════════════════════════════════════════════════════════════════════════

class TestRiskAPI:
    def _load_module(self):
        import importlib.util, pathlib
        path = pathlib.Path(__file__).parent.parent / "api" / "endpoints" / "risk.py"
        spec = importlib.util.spec_from_file_location("risk_endpoint", str(path))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_router_importable(self):
        mod = self._load_module()
        assert mod.router is not None
        assert mod.router.prefix == "/api/v8/risk"

    def test_assess_endpoint_exists(self):
        mod = self._load_module()
        assert callable(mod.risk_assess)

    def test_batch_endpoint_exists(self):
        mod = self._load_module()
        assert callable(mod.risk_batch)

    def test_aggregate_endpoint_exists(self):
        mod = self._load_module()
        assert callable(mod.risk_aggregate)

    def test_retrain_status_endpoint_exists(self):
        mod = self._load_module()
        assert callable(mod.retrain_status)

    def test_retrain_evaluate_endpoint_exists(self):
        mod = self._load_module()
        assert callable(mod.retrain_evaluate)

    def test_retrain_feedback_endpoint_exists(self):
        mod = self._load_module()
        assert callable(mod.retrain_feedback_check)

    def test_registered_in_main(self):
        import pathlib
        main_src = (pathlib.Path(__file__).parent.parent / "api" / "main.py").read_text()
        assert "risk_router" in main_src

    def test_request_model(self):
        mod = self._load_module()
        sig = mod.RiskSignalInput(termo="funk", momentum=80, sentiment=-0.3, volume=5000)
        assert sig.termo == "funk"

    def test_drift_alert_model(self):
        mod = self._load_module()
        alert = mod.DriftAlertInput(is_drift=True, p_value=0.01, severity="high", n_current=100)
        assert alert.is_drift is True
