"""
tests/test_feedback_engine.py — INT-1 FASE 2
==============================================
Tests for FeedbackEngine (core/feedback_engine.py) and its integration
as feedback_enricher in the AnalysisWorker pipeline.

Run:
    pytest tests/test_feedback_engine.py -v
"""
from __future__ import annotations

import sys, os
import pytest
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1: IMPORTS & BASICS
# ═════════════════════════════════════════════════════════════════════════════

class TestFeedbackEngineImport:
    """Verify module loads correctly."""

    def test_import_engine(self):
        from core.intelligence.learning.InsightLearner import FeedbackEngine
        assert FeedbackEngine is not None

    def test_import_singleton(self):
        from core.intelligence.learning.InsightLearner import get_feedback_engine
        assert callable(get_feedback_engine)

    def test_import_dataclass(self):
        from core.intelligence.learning.InsightLearner import FeedbackSample
        assert FeedbackSample is not None

    def test_import_constants(self):
        from core.intelligence.learning.InsightLearner import (
            MIN_SAMPLES_TO_TRAIN,
            N_FEATURES,
            FEATURE_NAMES,
            PLATFORM_INDEX,
        )
        assert MIN_SAMPLES_TO_TRAIN == 15
        assert N_FEATURES == 8
        assert len(FEATURE_NAMES) == 8
        assert "youtube" in PLATFORM_INDEX

    def test_singleton_same_instance(self):
        """Module singleton returns same object."""
        from core.intelligence.learning.InsightLearner import get_feedback_engine
        e1 = get_feedback_engine()
        e2 = get_feedback_engine()
        assert e1 is e2

    def test_has_sklearn_flag(self):
        from core.intelligence.learning.InsightLearner import _HAS_SKLEARN
        assert isinstance(_HAS_SKLEARN, bool)


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2: FEATURE EXTRACTION
# ═════════════════════════════════════════════════════════════════════════════

class TestFeatureExtraction:
    """Test extract_features static method."""

    def _engine(self):
        from core.intelligence.learning.InsightLearner import FeedbackEngine
        return FeedbackEngine()

    def test_empty_signal_returns_defaults(self):
        engine = self._engine()
        feats = engine.extract_features({})
        assert feats.shape == (8,)
        # tension=0, platform_idx=0, velocity=0
        assert feats[0] == 0.0  # tension
        assert feats[7] == 0.0  # platform_idx (unknown)

    def test_plataforma_youtube(self):
        engine = self._engine()
        feats = engine.extract_features({"plataforma": "YouTube"})
        assert feats[7] == pytest.approx(0.1)

    def test_plataforma_reddit(self):
        engine = self._engine()
        feats = engine.extract_features({"plataforma": "Reddit"})
        assert feats[7] == pytest.approx(0.2)

    def test_tension_score_extracted(self):
        engine = self._engine()
        feats = engine.extract_features({
            "tension_analysis": {"tension_score": 0.85}
        })
        assert feats[0] == pytest.approx(0.85)

    def test_sentiment_alma_normalized(self):
        engine = self._engine()
        feats = engine.extract_features({
            "sentiment_detail": {"alma_score": 75}
        })
        assert feats[1] == pytest.approx(0.75)

    def test_authenticity_score(self):
        engine = self._engine()
        feats = engine.extract_features({
            "authenticity_result": {"score": 0.9}
        })
        assert feats[2] == pytest.approx(0.9)

    def test_momentum_normalized(self):
        engine = self._engine()
        feats = engine.extract_features({
            "raw_data": {"momentum": 80}
        })
        assert feats[3] == pytest.approx(0.8)

    def test_volume_log_nonzero(self):
        engine = self._engine()
        feats = engine.extract_features({
            "raw_data": {"volume": 1000}
        })
        assert feats[4] > 0.0

    def test_circles_matched(self):
        engine = self._engine()
        feats = engine.extract_features({
            "circles_detail": {"n_circles_matched": 4}
        })
        assert feats[5] == pytest.approx(4.0 / 16.0)

    def test_velocity_extracted(self):
        engine = self._engine()
        feats = engine.extract_features({
            "velocity_features": {"velocity": 0.65}
        })
        assert feats[6] == pytest.approx(0.65)

    def test_full_signal(self):
        """Fully populated signal produces nonzero features."""
        engine = self._engine()
        feats = engine.extract_features({
            "tension_analysis": {"tension_score": 0.5},
            "sentiment_detail": {"alma_score": 60},
            "authenticity_result": {"score": 0.7},
            "raw_data": {"momentum": 70, "volume": 500},
            "circles_detail": {"n_circles_matched": 3},
            "velocity_features": {"velocity": 0.4},
            "plataforma": "spotify",
        })
        assert all(f > 0 for f in feats)


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3: FEEDBACK SAMPLE
# ═════════════════════════════════════════════════════════════════════════════

class TestFeedbackSample:
    """Test FeedbackSample dataclass."""

    def test_quality_target_min(self):
        from core.intelligence.learning.InsightLearner import FeedbackSample
        s = FeedbackSample(signal_id="s1", rating=1.0, effectiveness=0.5)
        assert s.quality_target() == pytest.approx(0.0)

    def test_quality_target_max(self):
        from core.intelligence.learning.InsightLearner import FeedbackSample
        s = FeedbackSample(signal_id="s2", rating=5.0, effectiveness=1.0)
        assert s.quality_target() == pytest.approx(1.0)

    def test_quality_target_mid(self):
        from core.intelligence.learning.InsightLearner import FeedbackSample
        s = FeedbackSample(signal_id="s3", rating=3.0, effectiveness=0.5)
        assert s.quality_target() == pytest.approx(0.5)

    def test_defaults(self):
        from core.intelligence.learning.InsightLearner import FeedbackSample
        s = FeedbackSample(signal_id="s4", rating=2.0, effectiveness=0.3)
        assert s.features.shape == (8,)
        assert s.timestamp  # non-empty


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 4: ADD FEEDBACK & PREDICT
# ═════════════════════════════════════════════════════════════════════════════

class TestAddFeedbackAndPredict:
    """Test core engine operations."""

    def _fresh_engine(self):
        from core.intelligence.learning.InsightLearner import FeedbackEngine
        return FeedbackEngine()

    def test_add_feedback_basic(self):
        engine = self._fresh_engine()
        result = engine.add_feedback("sig1", rating=4.0, effectiveness=0.8)
        assert result["status"] == "recorded"
        assert result["total_samples"] == 1
        assert result["auto_trained"] is False

    def test_add_feedback_increments(self):
        engine = self._fresh_engine()
        for i in range(5):
            result = engine.add_feedback(f"sig{i}", rating=3.0)
        assert result["total_samples"] == 5

    def test_predict_before_training(self):
        engine = self._fresh_engine()
        pred = engine.predict({"plataforma": "YouTube"})
        assert pred["status"] == "not_trained"
        assert pred["predicted_quality"] == pytest.approx(0.5)
        assert pred["confidence"] == pytest.approx(0.0)

    def test_rating_clamped(self):
        """Rating clamped to [1,5]."""
        engine = self._fresh_engine()
        engine.add_feedback("s1", rating=0.0)
        assert engine._samples[-1].rating == 1.0
        engine.add_feedback("s2", rating=10.0)
        assert engine._samples[-1].rating == 5.0

    def test_effectiveness_clamped(self):
        """Effectiveness clamped to [0,1]."""
        engine = self._fresh_engine()
        engine.add_feedback("s1", rating=3.0, effectiveness=-1.0)
        assert engine._samples[-1].effectiveness == 0.0
        engine.add_feedback("s2", rating=3.0, effectiveness=2.0)
        assert engine._samples[-1].effectiveness == 1.0

    def test_auto_train_at_threshold(self):
        """Auto-trains at MIN_SAMPLES_TO_TRAIN."""
        from core.intelligence.learning.InsightLearner import MIN_SAMPLES_TO_TRAIN
        engine = self._fresh_engine()

        for i in range(MIN_SAMPLES_TO_TRAIN - 1):
            result = engine.add_feedback(
                f"sig{i}",
                rating=float(1 + (i % 5)),
                signal={"plataforma": "YouTube", "raw_data": {"momentum": i * 5, "volume": i * 10}},
            )
            assert result["auto_trained"] is False

        # The Nth sample triggers training
        result = engine.add_feedback(
            f"sig_{MIN_SAMPLES_TO_TRAIN}",
            rating=4.0,
            signal={"plataforma": "Reddit", "raw_data": {"momentum": 80, "volume": 200}},
        )
        assert result["auto_trained"] is True
        assert engine.is_trained is True

    def test_predict_after_training(self):
        """After training, predict returns ok status with real score."""
        from core.intelligence.learning.InsightLearner import MIN_SAMPLES_TO_TRAIN
        engine = self._fresh_engine()

        for i in range(MIN_SAMPLES_TO_TRAIN):
            engine.add_feedback(
                f"sig{i}",
                rating=float(1 + (i % 5)),
                signal={
                    "plataforma": ["youtube", "reddit", "spotify"][i % 3],
                    "raw_data": {"momentum": i * 5, "volume": i * 10},
                    "tension_analysis": {"tension_score": (i % 10) / 10},
                },
            )

        pred = engine.predict({
            "plataforma": "YouTube",
            "raw_data": {"momentum": 50, "volume": 100},
        })
        assert pred["status"] == "ok"
        assert 0.0 <= pred["predicted_quality"] <= 1.0
        assert 0.0 <= pred["confidence"] <= 1.0

    def test_signal_snapshot_used(self):
        """Passing signal=dict uses its features."""
        engine = self._fresh_engine()
        sig = {
            "plataforma": "spotify",
            "tension_analysis": {"tension_score": 0.9},
            "raw_data": {"momentum": 100, "volume": 5000},
        }
        engine.add_feedback("s1", rating=5.0, signal=sig)
        sample = engine._samples[-1]
        assert sample.features[0] == pytest.approx(0.9)  # tension
        assert sample.features[7] == pytest.approx(0.3)  # spotify idx


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 5: STATS & PROPERTIES
# ═════════════════════════════════════════════════════════════════════════════

class TestStatsAndProperties:
    """Test get_stats and properties."""

    def _fresh_engine(self):
        from core.intelligence.learning.InsightLearner import FeedbackEngine
        return FeedbackEngine()

    def test_stats_initial(self):
        engine = self._fresh_engine()
        stats = engine.get_stats()
        assert stats["total_samples"] == 0
        assert stats["model_trained"] is False
        assert stats["trained_at"] is None
        assert stats["sklearn_available"] is True
        assert "feature_names" in stats
        assert len(stats["feature_names"]) == 8

    def test_stats_after_feedback(self):
        engine = self._fresh_engine()
        engine.add_feedback("s1", rating=3.0)
        stats = engine.get_stats()
        assert stats["total_samples"] == 1

    def test_sample_count_property(self):
        engine = self._fresh_engine()
        assert engine.sample_count == 0
        engine.add_feedback("s1", rating=3.0)
        assert engine.sample_count == 1

    def test_is_trained_property(self):
        engine = self._fresh_engine()
        assert engine.is_trained is False


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 6: WORKER INTEGRATION
# ═════════════════════════════════════════════════════════════════════════════

class TestFeedbackEnricherInWorker:
    """Test that feedback_enricher is properly registered in the Worker pipeline."""

    def test_worker_has_10_engines(self):
        """Worker default tem 17 engines registradas (inclui stability_risk)."""
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        assert len(worker._engines) == 17

    def test_feedback_registered_at_priority_45(self):
        """feedback_enricher está no pipeline com prioridade 45."""
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        fb = [e for e in worker._engines if e.name == "feedback"]
        assert len(fb) == 1
        assert fb[0].priority == 45

    def test_feedback_after_graph(self):
        """feedback comes after graph (40) in pipeline order."""
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        names = [e.name for e in worker._engines]
        assert names.index("graph") < names.index("feedback")

    def test_feedback_enricher_enriches_signal(self):
        """Run feedback_enricher on a sample signal."""
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        fb_engine = [e for e in worker._engines if e.name == "feedback"][0]

        signal = {
            "termo": "cultura digital",
            "plataforma": "YouTube",
            "raw_data": {"momentum": 50, "volume": 100},
        }
        result = fb_engine.fn(signal.copy())
        assert isinstance(result, dict)
        assert "feedback_prediction" in result
        fp = result["feedback_prediction"]
        assert "predicted_quality" in fp
        assert "status" in fp

    def test_feedback_enricher_handles_empty_signal(self):
        """Empty signal passes through without error."""
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        fb_engine = [e for e in worker._engines if e.name == "feedback"][0]

        result = fb_engine.fn({})
        assert isinstance(result, dict)
        assert "feedback_prediction" in result
