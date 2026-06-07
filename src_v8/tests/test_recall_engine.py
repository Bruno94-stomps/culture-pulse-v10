"""
tests/test_recall_engine.py — F-11 FASE 5
=============================================
Comprehensive tests for RecallEngine + REST endpoints.
"""
import pytest


class TestRecallEngine:
    """Tests for core/recall_engine.py"""

    def _make_engine(self, **config_overrides):
        from core.engines.recall_engine import RecallEngine
        return RecallEngine(config=config_overrides)

    # ── Initialization ───────────────────────────────────────────────────

    def test_init_defaults(self):
        engine = self._make_engine()
        assert engine.total_predictions == 0
        assert engine.total_validated == 0

    def test_init_custom_config(self):
        engine = self._make_engine(windows_days=[7, 14])
        assert engine.config["windows_days"] == [7, 14]

    # ── Register predictions ─────────────────────────────────────────────

    def test_register_prediction(self):
        engine = self._make_engine()
        result = engine.register_prediction(
            signal_id="sig001",
            termo="funk carioca",
            circle="Música Popular",
            momentum=0.85,
        )
        assert result["status"] == "registered"
        assert result["signal_id"] == "sig001"
        assert engine.total_predictions == 1

    def test_register_prediction_empty_id_raises(self):
        engine = self._make_engine()
        with pytest.raises(ValueError, match="required"):
            engine.register_prediction(signal_id="", termo="test")

    def test_register_prediction_empty_termo_raises(self):
        engine = self._make_engine()
        with pytest.raises(ValueError, match="required"):
            engine.register_prediction(signal_id="sig001", termo="")

    def test_register_prediction_duplicate_updates(self):
        engine = self._make_engine()
        engine.register_prediction(signal_id="sig001", termo="v1")
        engine.register_prediction(signal_id="sig001", termo="v2")
        assert engine.total_predictions == 1

    def test_register_prediction_max_cap(self):
        engine = self._make_engine(max_predictions=5)
        for i in range(10):
            engine.register_prediction(signal_id=f"sig{i:03d}", termo=f"term{i}")
        assert engine.total_predictions == 5

    def test_register_batch(self):
        engine = self._make_engine()
        signals = [
            {"signal_id": "s1", "termo": "samba"},
            {"signal_id": "s2", "termo": "forró"},
            {"signal_id": "s3", "termo": "axé"},
        ]
        result = engine.register_batch(signals)
        assert result["registered"] == 3
        assert result["failed"] == 0

    def test_register_batch_with_failures(self):
        engine = self._make_engine()
        signals = [
            {"signal_id": "s1", "termo": "samba"},
            {"signal_id": "", "termo": ""},  # Will fail
        ]
        result = engine.register_batch(signals)
        assert result["registered"] == 1
        assert result["failed"] == 1

    # ── Validate outcomes ────────────────────────────────────────────────

    def test_validate_outcome_became_trend(self):
        engine = self._make_engine()
        engine.register_prediction(signal_id="sig001", termo="test")
        result = engine.validate_outcome(
            signal_id="sig001",
            became_trend=True,
            trend_evidence="Google Trends peak",
        )
        assert result["status"] == "validated"
        assert result["became_trend"] is True
        assert engine.total_validated == 1

    def test_validate_outcome_not_trend(self):
        engine = self._make_engine()
        engine.register_prediction(signal_id="sig001", termo="test")
        result = engine.validate_outcome(signal_id="sig001", became_trend=False)
        assert result["became_trend"] is False

    def test_validate_unknown_signal_raises(self):
        engine = self._make_engine()
        with pytest.raises(ValueError, match="not found"):
            engine.validate_outcome(signal_id="nonexistent", became_trend=True)

    def test_validate_batch(self):
        engine = self._make_engine()
        engine.register_prediction(signal_id="s1", termo="a")
        engine.register_prediction(signal_id="s2", termo="b")
        result = engine.validate_batch([
            {"signal_id": "s1", "became_trend": True},
            {"signal_id": "s2", "became_trend": False},
        ])
        assert result["validated"] == 2

    def test_validate_batch_with_failures(self):
        engine = self._make_engine()
        engine.register_prediction(signal_id="s1", termo="a")
        result = engine.validate_batch([
            {"signal_id": "s1", "became_trend": True},
            {"signal_id": "s_unknown", "became_trend": False},
        ])
        assert result["validated"] == 1
        assert result["failed"] == 1

    # ── Metrics computation ──────────────────────────────────────────────

    def test_metrics_empty(self):
        engine = self._make_engine()
        metrics = engine.compute_metrics()
        assert "all_time" in metrics
        assert metrics["all_time"]["total_predictions"] == 0

    def test_metrics_with_data(self):
        engine = self._make_engine()
        for i in range(10):
            engine.register_prediction(
                signal_id=f"sig{i:03d}",
                termo=f"term{i}",
                momentum=0.5 + i * 0.05,
            )
        # Validate 7 as trends, 3 as not
        for i in range(7):
            engine.validate_outcome(signal_id=f"sig{i:03d}", became_trend=True)
        for i in range(7, 10):
            engine.validate_outcome(signal_id=f"sig{i:03d}", became_trend=False)

        metrics = engine.compute_metrics()
        all_time = metrics["all_time"]
        assert all_time["total_predictions"] == 10
        assert all_time["true_positives"] == 7
        assert all_time["false_positives"] == 3
        assert all_time["precision"] == 0.7
        assert all_time["hit_rate_pct"] == 70.0

    def test_metrics_specific_window(self):
        engine = self._make_engine()
        engine.register_prediction(signal_id="s1", termo="t1")
        engine.validate_outcome(signal_id="s1", became_trend=True)
        metrics = engine.compute_metrics(window_days=30)
        assert "30d" in metrics

    def test_metrics_multiple_windows(self):
        engine = self._make_engine(windows_days=[7, 30, 90])
        engine.register_prediction(signal_id="s1", termo="t1")
        metrics = engine.compute_metrics()
        assert "7d" in metrics
        assert "30d" in metrics
        assert "90d" in metrics
        assert "all_time" in metrics

    def test_metrics_unvalidated(self):
        engine = self._make_engine()
        engine.register_prediction(signal_id="s1", termo="t1")
        # Don't validate
        metrics = engine.compute_metrics()
        assert metrics["all_time"]["unvalidated"] == 1

    def test_precision_100_percent(self):
        engine = self._make_engine()
        for i in range(5):
            engine.register_prediction(signal_id=f"s{i}", termo=f"t{i}")
            engine.validate_outcome(signal_id=f"s{i}", became_trend=True)
        metrics = engine.compute_metrics()
        assert metrics["all_time"]["precision"] == 1.0
        assert metrics["all_time"]["hit_rate_pct"] == 100.0

    def test_precision_0_percent(self):
        engine = self._make_engine()
        for i in range(5):
            engine.register_prediction(signal_id=f"s{i}", termo=f"t{i}")
            engine.validate_outcome(signal_id=f"s{i}", became_trend=False)
        metrics = engine.compute_metrics()
        assert metrics["all_time"]["precision"] == 0.0

    # ── History ──────────────────────────────────────────────────────────

    def test_metrics_history(self):
        engine = self._make_engine()
        engine.register_prediction(signal_id="s1", termo="t1")
        engine.compute_metrics()
        engine.compute_metrics()
        history = engine.get_metrics_history()
        assert len(history) == 2

    def test_get_prediction_list(self):
        engine = self._make_engine()
        engine.register_prediction(signal_id="s1", termo="t1")
        engine.register_prediction(signal_id="s2", termo="t2")
        engine.validate_outcome(signal_id="s1", became_trend=True)
        preds = engine.get_prediction_list()
        assert len(preds) == 2
        assert preds[0]["outcome"] is not None  # s1 validated
        assert preds[1]["outcome"] is None  # s2 not validated

    def test_get_prediction_list_validated_only(self):
        engine = self._make_engine()
        engine.register_prediction(signal_id="s1", termo="t1")
        engine.register_prediction(signal_id="s2", termo="t2")
        engine.validate_outcome(signal_id="s1", became_trend=True)
        preds = engine.get_prediction_list(validated_only=True)
        assert len(preds) == 1

    # ── Retrain baseline ─────────────────────────────────────────────────

    def test_retrain_baseline_insufficient(self):
        engine = self._make_engine()
        baseline = engine.get_retrain_baseline()
        assert baseline["recommendation"] == "insufficient_data"

    def test_retrain_baseline_healthy(self):
        engine = self._make_engine()
        for i in range(15):
            engine.register_prediction(signal_id=f"s{i}", termo=f"t{i}")
            engine.validate_outcome(signal_id=f"s{i}", became_trend=(i < 10))
        baseline = engine.get_retrain_baseline()
        # 10/15 = 0.667 precision → healthy
        assert baseline["recommendation"] == "healthy"

    def test_retrain_baseline_needs_retrain(self):
        engine = self._make_engine()
        for i in range(15):
            engine.register_prediction(signal_id=f"s{i}", termo=f"t{i}")
            engine.validate_outcome(signal_id=f"s{i}", became_trend=(i < 3))
        baseline = engine.get_retrain_baseline()
        # 3/15 = 0.2 precision → retrain_recommended
        assert baseline["recommendation"] == "retrain_recommended"

    # ── Stats / Reset ────────────────────────────────────────────────────

    def test_stats(self):
        engine = self._make_engine()
        engine.register_prediction(signal_id="s1", termo="t1")
        engine.validate_outcome(signal_id="s1", became_trend=True)
        stats = engine.stats()
        assert stats["engine"] == "RecallEngine"
        assert stats["total_predictions"] == 1
        assert stats["total_validated"] == 1

    def test_reset(self):
        engine = self._make_engine()
        engine.register_prediction(signal_id="s1", termo="t1")
        engine.reset()
        assert engine.total_predictions == 0

    # ── Singleton ────────────────────────────────────────────────────────

    def test_singleton(self):
        from core.engines.recall_engine import get_recall_engine, reset_recall_engine
        reset_recall_engine()
        e1 = get_recall_engine()
        e2 = get_recall_engine()
        assert e1 is e2
        reset_recall_engine()


# ── REST API tests ───────────────────────────────────────────────────────────

class TestRecallAPI:
    """Tests for api/endpoints/recall.py"""

    @pytest.fixture
    def client(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from api.endpoints.recall import router
        from core.engines.recall_engine import reset_recall_engine

        reset_recall_engine()
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)

    def test_post_predict(self, client):
        resp = client.post("/api/v8/recall/predict", json={
            "signal_id": "sig001", "termo": "samba"
        })
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "registered"

    def test_post_predict_invalid(self, client):
        resp = client.post("/api/v8/recall/predict", json={
            "signal_id": "", "termo": "test"
        })
        assert resp.status_code == 400

    def test_post_predict_batch(self, client):
        resp = client.post("/api/v8/recall/predict/batch", json={
            "signals": [
                {"signal_id": "s1", "termo": "samba"},
                {"signal_id": "s2", "termo": "forró"},
            ]
        })
        assert resp.status_code == 200
        assert resp.json()["data"]["registered"] == 2

    def test_post_validate(self, client):
        client.post("/api/v8/recall/predict", json={
            "signal_id": "sig001", "termo": "samba"
        })
        resp = client.post("/api/v8/recall/validate", json={
            "signal_id": "sig001", "became_trend": True
        })
        assert resp.status_code == 200
        assert resp.json()["data"]["became_trend"] is True

    def test_post_validate_unknown(self, client):
        resp = client.post("/api/v8/recall/validate", json={
            "signal_id": "nonexistent", "became_trend": True
        })
        assert resp.status_code == 400

    def test_post_validate_batch(self, client):
        client.post("/api/v8/recall/predict", json={"signal_id": "s1", "termo": "a"})
        client.post("/api/v8/recall/predict", json={"signal_id": "s2", "termo": "b"})
        resp = client.post("/api/v8/recall/validate/batch", json={
            "outcomes": [
                {"signal_id": "s1", "became_trend": True},
                {"signal_id": "s2", "became_trend": False},
            ]
        })
        assert resp.status_code == 200

    def test_get_metrics(self, client):
        resp = client.get("/api/v8/recall/metrics")
        assert resp.status_code == 200
        assert "all_time" in resp.json()["data"]

    def test_get_history(self, client):
        resp = client.get("/api/v8/recall/history")
        assert resp.status_code == 200

    def test_get_predictions(self, client):
        client.post("/api/v8/recall/predict", json={
            "signal_id": "s1", "termo": "t1"
        })
        resp = client.get("/api/v8/recall/predictions")
        assert resp.status_code == 200
        assert len(resp.json()["data"]) == 1

    def test_get_retrain_baseline(self, client):
        resp = client.get("/api/v8/recall/retrain-baseline")
        assert resp.status_code == 200
        assert "recommendation" in resp.json()["data"]

    def test_get_stats(self, client):
        resp = client.get("/api/v8/recall/stats")
        assert resp.status_code == 200
        assert resp.json()["data"]["engine"] == "RecallEngine"
