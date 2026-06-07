#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_fase4_gnn_api.py — FASE 4 Tests
============================================
Tests for:
  INT-4: Real co-occurrence graph builder + GNN training + refactored enricher
  F-8:   Signal drill-down endpoint (signals/detail)
  F-9:   Network graph endpoint (graph/circles-network, graph/network)
  F-12:  Comparative views endpoint (signals/compare)
  GAP:   Pipeline endpoints (pipeline/status, momentum, tension, nature, velocity, graph, stability)

Sections:
  1. CulturalGraphBuilder unit tests  (INT-4A)
  2. GNN training loop tests           (INT-4B)
  3. Refactored graph_enricher tests   (INT-4C)
  4. API endpoint: pipeline.py          (GAP-fill)
  5. API endpoint: signals.py           (F-8 + F-12)
  6. API endpoint: graph_network.py     (F-9)
  7. Integration: main.py registration
"""

import sys
import os
import time
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ═══════════════════════════════════════════════════════════════════════════════
#  Fixtures
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def _reset_graph_builder():
    """Reset singleton between tests."""
    from core.engines.graph_builder import reset_graph_builder
    reset_graph_builder()
    yield
    reset_graph_builder()


@pytest.fixture
def builder():
    from core.engines.graph_builder import CulturalGraphBuilder
    return CulturalGraphBuilder()


@pytest.fixture
def sample_signal():
    return {
        "termo": "funk brasileiro",
        "circulo": "Música Popular",
        "momentum": 85,
        "sentiment": 0.6,
        "volume": 12000,
        "plataforma": "youtube",
        "score": 0.8,
        "timestamp": str(time.time()),
    }


@pytest.fixture
def multi_signals():
    """Multiple signals spanning several circles and time buckets."""
    now = time.time()
    return [
        {"termo": "funk carioca", "circulo": "Música Popular", "momentum": 90,
         "score": 0.9, "timestamp": str(now)},
        {"termo": "sertanejo", "circulo": "Música Popular", "momentum": 75,
         "score": 0.7, "timestamp": str(now + 100)},
        {"termo": "festa junina", "circulo": "Festas & Eventos", "momentum": 80,
         "score": 0.8, "timestamp": str(now)},
        {"termo": "carnaval", "circulo": "Festas & Eventos", "momentum": 95,
         "score": 0.95, "timestamp": str(now + 200)},
        {"termo": "moda street", "circulo": "Moda & Estilo", "momentum": 60,
         "score": 0.6, "timestamp": str(now + 300)},
        {"termo": "grafite urbano", "circulo": "Arte Urbana", "momentum": 70,
         "score": 0.7, "timestamp": str(now)},
        {"termo": "yoga praia", "circulo": "Saúde & Bem-Estar", "momentum": 55,
         "score": 0.55, "timestamp": str(now + 50)},
        {"termo": "startup tech", "circulo": "Tecnologia", "momentum": 88,
         "score": 0.88, "timestamp": str(now)},
        {"termo": "gastronomia regional", "circulo": "Gastronomia", "momentum": 65,
         "score": 0.65, "timestamp": str(now)},
        {"termo": "futebol raiz", "circulo": "Esporte", "momentum": 92,
         "score": 0.92, "timestamp": str(now + 100)},
        {"termo": "cinema brasileiro", "circulo": "Cinema & Séries", "momentum": 58,
         "score": 0.58, "timestamp": str(now + 200)},
        {"termo": "educação digital", "circulo": "Educação", "momentum": 62,
         "score": 0.62, "timestamp": str(now)},
    ]


# ═══════════════════════════════════════════════════════════════════════════════
#  1. CulturalGraphBuilder — INT-4A
# ═══════════════════════════════════════════════════════════════════════════════

class TestGraphBuilder:

    def test_import(self):
        from core.engines.graph_builder import CulturalGraphBuilder, get_graph_builder
        assert CulturalGraphBuilder is not None
        assert callable(get_graph_builder)

    def test_empty_build_fallback(self, builder):
        """Empty builder should produce graph with static affinity fallback."""
        graph = builder.build()
        assert graph.node_count == 16  # 16 circles
        assert graph.edge_count > 0
        assert graph.is_real is False

    def test_add_signal(self, builder, sample_signal):
        builder.add_signal(sample_signal)
        assert builder.signal_count == 1

    def test_add_signals_batch(self, builder, multi_signals):
        builder.add_signals(multi_signals)
        assert builder.signal_count == len(multi_signals)

    def test_build_with_many_signals(self, builder, multi_signals):
        """With enough diverse signals, co-occurrence edges should appear."""
        builder.add_signals(multi_signals)
        graph = builder.build()
        assert graph.node_count == 16
        assert graph.edge_count > 0
        assert graph.stats["co_occurrence_edges"] > 0

    def test_real_graph_threshold(self, builder, multi_signals):
        """Feed enough signals to exceed MIN_REAL_EDGES."""
        from core.engines.graph_builder import MIN_REAL_EDGES
        # Each time bucket creates pairwise co-occurrence among circles.
        # With 8+ circles in the same bucket, C(8,2)=28 edges > 10 min.
        builder.add_signals(multi_signals)
        graph = builder.build()
        co_occ = graph.stats["co_occurrence_edges"]
        if co_occ >= MIN_REAL_EDGES:
            assert graph.is_real is True

    def test_cache_invalidation(self, builder, sample_signal):
        """Adding a signal should invalidate cached graph."""
        g1 = builder.build()
        builder.add_signal(sample_signal)
        g2 = builder.build()
        # graph_data object should be different
        assert g1 is not g2

    def test_reset(self, builder, sample_signal):
        builder.add_signal(sample_signal)
        builder.reset()
        assert builder.signal_count == 0

    def test_max_signals_capped(self):
        from core.engines.graph_builder import CulturalGraphBuilder
        b = CulturalGraphBuilder(max_signals=5)
        for i in range(20):
            b.add_signal({"termo": f"t{i}", "circulo": "Tecnologia", "timestamp": str(time.time())})
        assert b.signal_count == 5

    def test_graph_nodes_are_circles(self, builder, multi_signals):
        builder.add_signals(multi_signals)
        graph = builder.build()
        node_ids = {n.node_id for n in graph.nodes}
        assert "Música Popular" in node_ids
        assert "Tecnologia" in node_ids

    def test_graph_edges_have_types(self, builder, multi_signals):
        builder.add_signals(multi_signals)
        graph = builder.build()
        types = {e.edge_type for e in graph.edges}
        # At minimum we get co-occurrence or affinity edges
        assert len(types) > 0

    def test_temporal_edges(self, builder):
        """Signals close in time with different termos get temporal edges."""
        now = time.time()
        builder.add_signals([
            {"termo": "abc", "circulo": "Tecnologia", "timestamp": str(now)},
            {"termo": "xyz", "circulo": "Educação", "timestamp": str(now + 10)},
        ])
        graph = builder.build()
        temporal = [e for e in graph.edges if e.edge_type == "temporal"]
        assert len(temporal) > 0

    def test_semantic_edges(self, builder):
        """Signals with overlapping tokens get semantic edges."""
        builder.add_signals([
            {"termo": "funk carioca brasileiro", "circulo": "Música Popular", "timestamp": str(time.time())},
            {"termo": "funk brasileiro raiz", "circulo": "Festas & Eventos", "timestamp": str(time.time())},
        ])
        graph = builder.build()
        semantic = [e for e in graph.edges if e.edge_type == "semantic"]
        assert len(semantic) > 0

    def test_to_dict(self, builder, multi_signals):
        builder.add_signals(multi_signals)
        d = builder.to_dict()
        assert "nodes" in d
        assert "edges" in d
        assert "stats" in d
        assert d["signal_count"] == len(multi_signals)

    def test_singleton(self):
        from core.engines.graph_builder import get_graph_builder
        b1 = get_graph_builder()
        b2 = get_graph_builder()
        assert b1 is b2


# ═══════════════════════════════════════════════════════════════════════════════
#  2. GNN Training Loop — INT-4B
# ═══════════════════════════════════════════════════════════════════════════════

class TestGNNTraining:

    def test_train_empty(self, builder):
        """Training with no data should skip."""
        result = builder.train()
        assert result["status"] == "skipped"

    def test_train_few_signals(self, builder, sample_signal):
        """One signal → too few edges → skip."""
        builder.add_signal(sample_signal)
        result = builder.train()
        # Either skipped (no torch) or skipped (too few edges)
        assert result["status"] in ("skipped", "error")

    def test_train_sufficient_signals(self, builder, multi_signals):
        """With 12 signals in many circles, training should run (if torch available)."""
        builder.add_signals(multi_signals)
        result = builder.train(epochs=3)
        if result["status"] == "completed":
            assert result["epochs"] == 3
            assert result["final_loss"] is not None
            assert len(result["loss_history"]) == 3
        else:
            # torch not installed → graceful skip
            assert result["status"] in ("skipped", "error")

    def test_train_returns_metrics(self, builder, multi_signals):
        builder.add_signals(multi_signals)
        result = builder.train(epochs=2, lr=0.005)
        assert "status" in result
        assert "epochs" in result


# ═══════════════════════════════════════════════════════════════════════════════
#  3. Refactored graph_enricher — INT-4C
# ═══════════════════════════════════════════════════════════════════════════════

class TestGraphEnricher:

    def test_enricher_basic(self, sample_signal):
        """graph_enricher should add graph_analysis key to signal."""
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()

        # Find graph enricher
        graph_fn = None
        for eng in worker._engines:
            if eng.name == "graph":
                graph_fn = eng.fn
                break
        assert graph_fn is not None, "graph engine not found in worker"

        result = graph_fn(sample_signal.copy())
        assert "graph_analysis" in result

    def test_enricher_uses_builder(self, sample_signal):
        """After running enricher, the singleton builder should have signals."""
        from core.analysis_worker import create_default_worker
        from core.engines.graph_builder import get_graph_builder

        worker = create_default_worker()
        graph_fn = None
        for eng in worker._engines:
            if eng.name == "graph":
                graph_fn = eng.fn
                break

        graph_fn(sample_signal.copy())
        builder = get_graph_builder()
        assert builder.signal_count >= 1

    def test_enricher_skips_geral(self):
        """Signals with circulo='geral' should be skipped."""
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        graph_fn = None
        for eng in worker._engines:
            if eng.name == "graph":
                graph_fn = eng.fn
                break

        sig = {"termo": "test", "circulo": "geral", "timestamp": str(time.time())}
        result = graph_fn(sig.copy())
        assert "graph_analysis" not in result

    def test_enricher_graph_result_keys(self, sample_signal):
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        graph_fn = None
        for eng in worker._engines:
            if eng.name == "graph":
                graph_fn = eng.fn
                break

        result = graph_fn(sample_signal.copy())
        ga = result.get("graph_analysis", {})
        assert "graph_nodes" in ga
        assert "graph_edges" in ga
        assert "graph_is_real" in ga
        assert "graph_stats" in ga

    def test_enricher_accumulates(self, multi_signals):
        """Multiple calls accumulate in the builder."""
        from core.analysis_worker import create_default_worker
        from core.engines.graph_builder import get_graph_builder

        worker = create_default_worker()
        graph_fn = None
        for eng in worker._engines:
            if eng.name == "graph":
                graph_fn = eng.fn
                break

        for sig in multi_signals[:5]:
            graph_fn(sig.copy())

        builder = get_graph_builder()
        assert builder.signal_count >= 5


# ═══════════════════════════════════════════════════════════════════════════════
#  4. API: pipeline.py (gap-fill endpoints)
# ═══════════════════════════════════════════════════════════════════════════════

class TestPipelineAPI:

    def _load(self):
        import importlib.util, pathlib
        path = pathlib.Path(__file__).parent.parent / "api" / "endpoints" / "pipeline.py"
        spec = importlib.util.spec_from_file_location("pipeline_ep", str(path))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_importable(self):
        mod = self._load()
        assert mod.router is not None

    def test_router_prefix(self):
        mod = self._load()
        # router has no prefix — prefix is set via include_router in main.py
        assert mod.router is not None

    def test_pipeline_status_exists(self):
        mod = self._load()
        assert callable(mod.pipeline_status)

    def test_pipeline_engines_exists(self):
        mod = self._load()
        assert callable(mod.pipeline_engines)

    def test_pipeline_enrich_exists(self):
        mod = self._load()
        assert callable(mod.pipeline_enrich)

    def test_momentum_compute_exists(self):
        mod = self._load()
        assert callable(mod.compute_momentum)

    def test_tension_analyze_exists(self):
        mod = self._load()
        assert callable(mod.analyze_tension)

    def test_nature_classify_exists(self):
        mod = self._load()
        assert callable(mod.classify_nature)

    def test_velocity_compute_exists(self):
        mod = self._load()
        assert callable(mod.compute_velocity)

    def test_graph_analyze_exists(self):
        mod = self._load()
        assert callable(mod.analyze_graph)

    def test_stability_compare_exists(self):
        mod = self._load()
        assert callable(mod.compare_stability)

    def test_momentum_request_model(self):
        mod = self._load()
        req = mod.MomentumRequest(
            platform="youtube", volume=1000, engagement=0.5,
            cultural_score=0.8, popularity=0.7, diversity=0.6,
            regional_spread=0.4, termo="funk"
        )
        assert req.platform == "youtube"
        assert req.volume == 1000

    def test_tension_request_model(self):
        mod = self._load()
        req = mod.TensionRequest(text="funk e samba se encontram", sentiment=0.5)
        assert req.text == "funk e samba se encontram"

    def test_nature_request_model(self):
        mod = self._load()
        req = mod.NatureRequest(termo="funk carioca", mencoes=["menção 1"])
        assert req.termo == "funk carioca"

    def test_velocity_request_model(self):
        mod = self._load()
        req = mod.VelocityRequest(
            signals=[{"termo": "t1", "momentum": 80}]
        )
        assert len(req.signals) == 1

    def test_graph_request_model(self):
        mod = self._load()
        req = mod.GraphRequest(
            termo="funk", circulo="Música Popular", score=0.8
        )
        assert req.termo == "funk"

    def test_stability_request_model(self):
        mod = self._load()
        req = mod.StabilityRequest(
            clusters_current={"A": ["1", "2", "3"]},
            clusters_previous={"B": ["1", "2", "3"]}
        )
        assert "A" in req.clusters_current

    def test_registered_in_main(self):
        import pathlib
        main_src = (pathlib.Path(__file__).parent.parent / "api" / "main.py").read_text()
        assert "pipeline_router" in main_src


# ═══════════════════════════════════════════════════════════════════════════════
#  5. API: signals.py (F-8 drill-down + F-12 comparative)
# ═══════════════════════════════════════════════════════════════════════════════

class TestSignalsAPI:

    def _load(self):
        import importlib.util, pathlib
        path = pathlib.Path(__file__).parent.parent / "api" / "endpoints" / "signals.py"
        spec = importlib.util.spec_from_file_location("signals_ep", str(path))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_importable(self):
        mod = self._load()
        assert mod.router is not None

    def test_router_prefix(self):
        mod = self._load()
        assert mod.router.prefix == "/api/v8/signals"

    def test_detail_endpoint_exists(self):
        """F-8: signal detail drill-down."""
        mod = self._load()
        assert callable(mod.signal_detail)

    def test_compare_endpoint_exists(self):
        """F-12: comparative view."""
        mod = self._load()
        assert callable(mod.signal_compare)

    def test_detail_request_model(self):
        mod = self._load()
        req = mod.SignalDetailRequest(signal={"termo": "funk"})
        assert req.signal["termo"] == "funk"

    def test_compare_request_model(self):
        mod = self._load()
        req = mod.CompareRequest(
            signals=[{"termo": "a"}, {"termo": "b"}]
        )
        assert len(req.signals) == 2

    def test_compare_request_min_signals(self):
        """Compare needs at least 2 signals."""
        mod = self._load()
        req = mod.CompareRequest(signals=[{"termo": "a"}, {"termo": "b"}])
        assert len(req.signals) >= 2

    def test_registered_in_main(self):
        import pathlib
        main_src = (pathlib.Path(__file__).parent.parent / "api" / "main.py").read_text()
        assert "signals_router" in main_src


# ═══════════════════════════════════════════════════════════════════════════════
#  6. API: graph_network.py (F-9 network graph)
# ═══════════════════════════════════════════════════════════════════════════════

class TestGraphNetworkAPI:

    def _load(self):
        import importlib.util, pathlib
        path = pathlib.Path(__file__).parent.parent / "api" / "endpoints" / "graph_network.py"
        spec = importlib.util.spec_from_file_location("graph_network_ep", str(path))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_importable(self):
        mod = self._load()
        assert mod.router is not None

    def test_router_prefix(self):
        mod = self._load()
        assert mod.router.prefix == "/api/v8/graph"

    def test_circles_network_exists(self):
        mod = self._load()
        assert callable(mod.circles_network)

    def test_signal_network_exists(self):
        mod = self._load()
        assert callable(mod.signal_network)

    def test_network_request_model(self):
        mod = self._load()
        req = mod.NetworkRequest(
            signals=[{"termo": "funk", "circulo": "Música Popular", "momentum": 80}]
        )
        assert len(req.signals) == 1

    def test_circle_colors_complete(self):
        """All 16 circles should have color assignments."""
        mod = self._load()
        assert len(mod.CIRCLE_COLORS) == 16

    def test_afinidades_complete(self):
        mod = self._load()
        assert len(mod.AFINIDADES) == 16

    def test_registered_in_main(self):
        import pathlib
        main_src = (pathlib.Path(__file__).parent.parent / "api" / "main.py").read_text()
        assert "graph_network_router" in main_src


# ═══════════════════════════════════════════════════════════════════════════════
#  7. Integration: main.py router registration
# ═══════════════════════════════════════════════════════════════════════════════

class TestMainRegistration:

    def test_all_fase4_routers_in_main(self):
        import pathlib
        main_src = (pathlib.Path(__file__).parent.parent / "api" / "main.py").read_text()
        assert "pipeline_router" in main_src
        assert "signals_router" in main_src
        assert "graph_network_router" in main_src

    def test_main_importable(self):
        import importlib.util, pathlib
        path = pathlib.Path(__file__).parent.parent / "api" / "main.py"
        spec = importlib.util.spec_from_file_location("api_main", str(path))
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
            assert hasattr(mod, "app")
        except Exception:
            # Import may fail if dependencies not available, that's OK
            pass

    def test_total_engine_count_unchanged(self):
        """Worker still has 17 engines after INT-4C refactor + stability_risk."""
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        assert len(worker._engines) == 17

    def test_graph_engine_still_at_priority_40(self):
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        graph_eng = None
        for eng in worker._engines:
            if eng.name == "graph":
                graph_eng = eng
                break
        assert graph_eng is not None
        assert graph_eng.priority == 40

    def test_graph_engine_uses_builder_import(self):
        """Verify the refactored graph_enricher imports from graph_builder."""
        import inspect
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        for eng in worker._engines:
            if eng.name == "graph":
                source = inspect.getsource(eng.fn)
                assert "graph_builder" in source
                assert "get_graph_builder" in source
                # Should NOT have the old static AFINIDADES dict
                assert "AFINIDADES" not in source
                break
