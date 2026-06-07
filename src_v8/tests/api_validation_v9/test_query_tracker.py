"""
Tests for F-1 — Query Tracking Supabase
=========================================
Tests the QueryTracker module (core/query_tracker.py) for:
  - Tracking queries to local buffer (Supabase unavailable)
  - Context manager auto-timing
  - History and stats from local buffer
  - Convenience functions
  - Integration: dashboard _track_query helper
"""
from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures — reset module singleton between test classes to prevent leakage
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _reset_tracker_singleton(monkeypatch):
    """Reset the module-level _default_tracker and mask Supabase env vars
    before each test so that trackers created with empty strings don't
    accidentally pick up real credentials from .env."""
    import core.query_tracker as mod
    mod._default_tracker = None
    # Mask env vars so QueryTracker(supabase_url="", supabase_key="") stays offline
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)
    yield
    mod._default_tracker = None


# ─────────────────────────────────────────────────────────────────────────────
# Test QueryTracker core
# ─────────────────────────────────────────────────────────────────────────────

class TestQueryTrackerInit:
    """Test QueryTracker construction."""

    def test_import(self):
        from core.models.query_tracker import QueryTracker
        tracker = QueryTracker()
        assert tracker is not None

    def test_singleton(self):
        from core.models.query_tracker import get_tracker
        t1 = get_tracker()
        t2 = get_tracker()
        assert t1 is t2

    def test_default_table_name(self):
        from core.models.query_tracker import QueryTracker
        assert QueryTracker.TABLE_NAME == "query_log"

    def test_valid_query_types(self):
        from core.models.query_tracker import VALID_QUERY_TYPES
        assert "brand_analysis" in VALID_QUERY_TYPES
        assert "dashboard_collect" in VALID_QUERY_TYPES
        assert "api_endpoint" in VALID_QUERY_TYPES
        assert "worker_enrichment" in VALID_QUERY_TYPES

    def test_valid_sources(self):
        from core.models.query_tracker import VALID_SOURCES
        assert "dashboard" in VALID_SOURCES
        assert "api" in VALID_SOURCES
        assert "worker" in VALID_SOURCES


class TestQueryTrackerLocalBuffer:
    """Test tracking to local buffer when Supabase is unavailable."""

    def test_track_returns_false_no_supabase(self):
        from core.models.query_tracker import QueryTracker
        tracker = QueryTracker(supabase_url="", supabase_key="")
        result = tracker.track(
            query_type="brand_analysis",
            query_input={"brand": "Havaianas"},
        )
        assert result is False

    def test_track_adds_to_local_buffer(self):
        from core.models.query_tracker import QueryTracker
        tracker = QueryTracker(supabase_url="", supabase_key="")
        tracker.track(query_type="brand_analysis", query_input={"brand": "Nike"})
        buf = tracker.get_local_buffer()
        assert len(buf) == 1
        assert buf[0]["query_type"] == "brand_analysis"
        assert buf[0]["query_input"]["brand"] == "Nike"

    def test_track_multiple_queries(self):
        from core.models.query_tracker import QueryTracker
        tracker = QueryTracker(supabase_url="", supabase_key="")
        for i in range(5):
            tracker.track(query_type="tfidf_search", query_input={"term": f"t{i}"})
        assert len(tracker.get_local_buffer()) == 5

    def test_buffer_limit_enforced(self):
        from core.models.query_tracker import QueryTracker
        tracker = QueryTracker(supabase_url="", supabase_key="")
        tracker._max_buffer = 10
        for i in range(20):
            tracker.track(query_type="trend_query", query_input={"i": i})
        assert len(tracker.get_local_buffer()) <= 10

    def test_clear_buffer(self):
        from core.models.query_tracker import QueryTracker
        tracker = QueryTracker(supabase_url="", supabase_key="")
        tracker.track(query_type="brand_analysis", query_input={})
        tracker.clear_local_buffer()
        assert len(tracker.get_local_buffer()) == 0

    def test_invalid_query_type_falls_to_custom(self):
        from core.models.query_tracker import QueryTracker
        tracker = QueryTracker(supabase_url="", supabase_key="")
        tracker.track(query_type="invalid_type", query_input={})
        buf = tracker.get_local_buffer()
        assert buf[0]["query_type"] == "custom"

    def test_invalid_source_falls_to_dashboard(self):
        from core.models.query_tracker import QueryTracker
        tracker = QueryTracker(supabase_url="", supabase_key="")
        tracker.track(query_type="brand_analysis", query_input={}, source="invalid")
        buf = tracker.get_local_buffer()
        assert buf[0]["source"] == "dashboard"

    def test_all_fields_populated(self):
        from core.models.query_tracker import QueryTracker
        tracker = QueryTracker(supabase_url="", supabase_key="")
        tracker.track(
            query_type="brand_analysis",
            query_input={"brand": "X"},
            result_summary={"score": 0.8},
            source="api",
            plan="pro",
            enriched=True,
            duration_ms=500,
            status="success",
            user_id="user-123",
        )
        row = tracker.get_local_buffer()[0]
        assert row["query_type"] == "brand_analysis"
        assert row["query_input"]["brand"] == "X"
        assert row["result_summary"]["score"] == 0.8
        assert row["source"] == "api"
        assert row["plan"] == "pro"
        assert row["enriched"] is True
        assert row["duration_ms"] == 500
        assert row["status"] == "success"
        assert row["user_id"] == "user-123"
        assert "ts" in row

    def test_error_tracking(self):
        from core.models.query_tracker import QueryTracker
        tracker = QueryTracker(supabase_url="", supabase_key="")
        tracker.track(
            query_type="brand_analysis",
            query_input={},
            status="error",
            error_detail="API timeout",
        )
        row = tracker.get_local_buffer()[0]
        assert row["status"] == "error"
        assert row["error_detail"] == "API timeout"


class TestQueryTrackerHistory:
    """Test history reading from local buffer."""

    def _tracker_with_data(self):
        from core.models.query_tracker import QueryTracker
        tracker = QueryTracker(supabase_url="", supabase_key="")
        tracker.track(query_type="brand_analysis", query_input={}, plan="free")
        tracker.track(query_type="tfidf_search", query_input={}, plan="pro")
        tracker.track(query_type="brand_analysis", query_input={}, plan="pro")
        return tracker

    def test_get_all_history(self):
        tracker = self._tracker_with_data()
        history = tracker.get_history()
        assert len(history) == 3

    def test_filter_by_plan(self):
        tracker = self._tracker_with_data()
        history = tracker.get_history(plan="pro")
        assert len(history) == 2

    def test_filter_by_query_type(self):
        tracker = self._tracker_with_data()
        history = tracker.get_history(query_type="brand_analysis")
        assert len(history) == 2

    def test_limit(self):
        tracker = self._tracker_with_data()
        history = tracker.get_history(limit=1)
        assert len(history) == 1


class TestQueryTrackerStats:
    """Test stats computation from local buffer."""

    def test_empty_stats(self):
        from core.models.query_tracker import QueryTracker
        tracker = QueryTracker(supabase_url="", supabase_key="")
        stats = tracker.get_stats()
        assert stats["source"] == "local_buffer"
        assert stats["total_queries"] == 0

    def test_stats_with_data(self):
        from core.models.query_tracker import QueryTracker
        tracker = QueryTracker(supabase_url="", supabase_key="")
        tracker.track(query_type="brand_analysis", query_input={}, duration_ms=100)
        tracker.track(query_type="brand_analysis", query_input={}, duration_ms=200)
        tracker.track(query_type="tfidf_search", query_input={}, status="error")

        stats = tracker.get_stats()
        assert stats["total_queries"] == 3
        assert stats["by_type"]["brand_analysis"] == 2
        assert stats["by_type"]["tfidf_search"] == 1
        assert stats["by_status"]["success"] == 2
        assert stats["by_status"]["error"] == 1
        assert stats["avg_duration_ms"] == 150  # (100+200) / 2


class TestTrackingContext:
    """Test the context manager for auto-timed tracking."""

    def test_context_records_duration(self):
        from core.models.query_tracker import QueryTracker
        tracker = QueryTracker(supabase_url="", supabase_key="")

        with tracker.track_context("brand_analysis", {"brand": "X"}) as ctx:
            time.sleep(0.05)  # 50ms
            ctx.set_result({"score": 0.9})

        buf = tracker.get_local_buffer()
        assert len(buf) == 1
        assert buf[0]["duration_ms"] >= 40  # at least ~50ms
        assert buf[0]["result_summary"]["score"] == 0.9

    def test_context_records_error(self):
        from core.models.query_tracker import QueryTracker
        tracker = QueryTracker(supabase_url="", supabase_key="")

        try:
            with tracker.track_context("tfidf_search", {"term": "Y"}) as ctx:
                raise ValueError("test error")
        except ValueError:
            pass

        buf = tracker.get_local_buffer()
        assert len(buf) == 1
        assert buf[0]["status"] == "error"
        assert "test error" in buf[0]["error_detail"]

    def test_context_manual_error(self):
        from core.models.query_tracker import QueryTracker
        tracker = QueryTracker(supabase_url="", supabase_key="")

        with tracker.track_context("trend_query", {}) as ctx:
            ctx.set_error("timeout exceeded")

        buf = tracker.get_local_buffer()
        assert buf[0]["status"] == "error"
        assert buf[0]["error_detail"] == "timeout exceeded"


class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_track_dashboard_query(self):
        from core.models.query_tracker import track_dashboard_query, get_tracker
        tracker = get_tracker()
        tracker.clear_local_buffer()

        result = track_dashboard_query(
            query_type="dashboard_collect",
            query_input={"brand": "Havaianas"},
            duration_ms=800,
        )
        # Without Supabase, returns False (buffered locally)
        assert result is False
        buf = tracker.get_local_buffer()
        assert len(buf) >= 1
        assert buf[-1]["source"] == "dashboard"

    def test_track_api_query(self):
        from core.models.query_tracker import track_api_query, get_tracker
        tracker = get_tracker()
        tracker.clear_local_buffer()

        track_api_query(
            endpoint="/api/v8/analysis/brand",
            query_input={"brand": "Nike"},
            plan="pro",
            duration_ms=200,
        )
        buf = tracker.get_local_buffer()
        assert buf[-1]["query_type"] == "api_endpoint"
        assert buf[-1]["source"] == "api"
        assert buf[-1]["query_input"]["endpoint"] == "/api/v8/analysis/brand"

    def test_track_worker_query(self):
        from core.models.query_tracker import track_worker_query, get_tracker
        tracker = get_tracker()
        tracker.clear_local_buffer()

        track_worker_query(
            query_input={"signal_id": "abc"},
            result_summary={"enriched": True},
            duration_ms=50,
        )
        buf = tracker.get_local_buffer()
        assert buf[-1]["query_type"] == "worker_enrichment"
        assert buf[-1]["source"] == "worker"
        assert buf[-1]["enriched"] is True


class TestIsAvailable:
    """Test availability check."""

    def test_unavailable_no_env(self):
        from core.models.query_tracker import QueryTracker
        tracker = QueryTracker(supabase_url="", supabase_key="")
        assert tracker.is_available is False


# ─────────────────────────────────────────────────────────────────────────────
# Test Dashboard _track_query integration
# ─────────────────────────────────────────────────────────────────────────────

class TestDashboardTrackQueryIntegration:
    """Test the dashboard's _track_query helper doesn't crash."""

    def test_track_query_never_raises(self):
        """_track_query should never raise, even if everything fails."""
        import sys
        mock_st = MagicMock()
        mock_st.session_state = MagicMock()
        mock_st.session_state.get.return_value = "free"
        mock_st.cache_data = lambda **kw: (lambda f: f)
        mock_st.cache_resource = lambda **kw: (lambda f: f)

        with patch.dict(sys.modules, {"streamlit": mock_st}):
            from dashboard.cultural_dashboard_integrated_v11 import CulturePulseDashboardV9
            instance = object.__new__(CulturePulseDashboardV9)

            # Should not raise even with broken tracker
            instance._track_query(
                "brand_analysis",
                {"brand": "Test"},
                {"score": 0.5},
                enriched=False,
                start_time=time.time() - 1,
            )
            # No assertion needed — just verifying no exception


# ─────────────────────────────────────────────────────────────────────────────
# Count
# ─────────────────────────────────────────────────────────────────────────────
# TestQueryTrackerInit:              5
# TestQueryTrackerLocalBuffer:       9
# TestQueryTrackerHistory:           4
# TestQueryTrackerStats:             2
# TestTrackingContext:                3
# TestConvenienceFunctions:          3
# TestIsAvailable:                   1
# TestDashboardTrackQueryIntegration: 1
# ─────────────────────────────────────────────────────────────────
# TOTAL:                            28
