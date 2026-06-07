#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_cluster_labeler.py — F-4 FASE 3
=============================================
Tests for ClusterLabeler (core/cluster_labeler.py) + API endpoint.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ═══════════════════════════════════════════════════════════════════════════════
#  Fixtures
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def _reset():
    from core.clustering import reset_cluster_labeler
    reset_cluster_labeler()
    yield
    reset_cluster_labeler()


@pytest.fixture
def labeler():
    from core.clustering import ClusterLabeler
    return ClusterLabeler()


@pytest.fixture
def grouped_signals():
    """Pre-grouped clusters."""
    return {
        "cluster_0": [
            {"termo": "funk carioca", "plataforma": "youtube"},
            {"termo": "baile funk", "plataforma": "spotify"},
            {"termo": "mc kevin", "plataforma": "youtube"},
        ],
        "cluster_1": [
            {"termo": "inteligência artificial", "plataforma": "reddit"},
            {"termo": "machine learning", "plataforma": "newsapi"},
            {"termo": "startup tecnologia", "plataforma": "youtube"},
        ],
        "cluster_2": [
            {"termo": "carnaval 2025", "plataforma": "instagram"},
            {"termo": "bloco de rua", "plataforma": "meetup"},
            {"termo": "samba enredo", "plataforma": "spotify"},
        ],
    }


@pytest.fixture
def flat_signals():
    """Flat list with cluster_id key."""
    return [
        {"termo": "funk", "cluster_id": "0"},
        {"termo": "baile", "cluster_id": "0"},
        {"termo": "IA", "cluster_id": "1"},
        {"termo": "tecnologia", "cluster_id": "1"},
    ]


# ═══════════════════════════════════════════════════════════════════════════════
#  1. Core functionality
# ═══════════════════════════════════════════════════════════════════════════════

class TestClusterLabelerCore:
    def test_import(self):
        from core.clustering import ClusterLabeler
        assert ClusterLabeler is not None

    def test_singleton(self):
        from core.clustering import get_cluster_labeler
        a = get_cluster_labeler()
        b = get_cluster_labeler()
        assert a is b

    def test_label_clusters_returns_dict(self, labeler, grouped_signals):
        labels = labeler.label_clusters(grouped_signals)
        assert isinstance(labels, dict)

    def test_label_clusters_keys_match(self, labeler, grouped_signals):
        labels = labeler.label_clusters(grouped_signals)
        assert set(labels.keys()) == set(grouped_signals.keys())

    def test_labels_are_dicts_with_label_key(self, labeler, grouped_signals):
        labels = labeler.label_clusters(grouped_signals)
        for v in labels.values():
            assert isinstance(v, dict)
            assert "label" in v
            assert isinstance(v["label"], str)
            assert len(v["label"]) > 0

    def test_labels_not_identical(self, labeler, grouped_signals):
        """Different clusters should get different labels."""
        labels = labeler.label_clusters(grouped_signals)
        label_strs = [v["label"] for v in labels.values()]
        assert len(set(label_strs)) == len(label_strs), "All cluster labels should be unique"

    def test_label_from_flat_signals(self, labeler, flat_signals):
        labels = labeler.label_from_flat_signals(flat_signals, cluster_key="cluster_id")
        assert isinstance(labels, dict)
        assert "0" in labels
        assert "1" in labels

    def test_empty_cluster_handled(self, labeler):
        labels = labeler.label_clusters({"empty": []})
        assert "empty" in labels


# ═══════════════════════════════════════════════════════════════════════════════
#  2. TF-IDF internals
# ═══════════════════════════════════════════════════════════════════════════════

class TestClusterLabelerTFIDF:
    def test_tokenize_removes_stopwords(self):
        from core.clustering import _tokenize
        tokens = _tokenize("o que é isso de novo para mim")
        # Portuguese stopwords like "o", "que", "é", "isso", "de", "para" should be removed
        for sw in ["que", "isso", "para"]:
            assert sw not in tokens

    def test_tokenize_lowercases(self):
        from core.clustering import _tokenize
        tokens = _tokenize("FUNK Brasileiro CARIOCA")
        for t in tokens:
            assert t == t.lower()

    def test_compute_tfidf_not_empty(self):
        from core.clustering import _compute_tfidf
        docs = {"a": ["funk", "baile", "carioca"], "b": ["samba", "carnaval", "baile"]}
        tfidf = _compute_tfidf(docs)
        assert len(tfidf) > 0

    def test_category_hints_coverage(self):
        from core.clustering import _CATEGORY_HINTS
        hints = _CATEGORY_HINTS
        assert "funk" in hints
        assert any("tecnolog" in k or "digital" in k for k in hints)


# ═══════════════════════════════════════════════════════════════════════════════
#  3. Edge cases
# ═══════════════════════════════════════════════════════════════════════════════

class TestClusterLabelerEdgeCases:
    def test_single_signal_cluster(self, labeler):
        labels = labeler.label_clusters({"solo": [{"termo": "funk"}]})
        assert "solo" in labels

    def test_single_word_terms(self, labeler):
        labels = labeler.label_clusters({"c": [{"termo": "a"}, {"termo": "b"}]})
        assert "c" in labels

    def test_duplicate_terms(self, labeler):
        sigs = [{"termo": "funk"}, {"termo": "funk"}, {"termo": "funk"}]
        labels = labeler.label_clusters({"dup": sigs})
        assert "dup" in labels

    def test_unicode_terms(self, labeler):
        sigs = [{"termo": "música eletrônica"}, {"termo": "açaí cultural"}]
        labels = labeler.label_clusters({"uni": sigs})
        assert "uni" in labels

    def test_flat_signals_missing_key(self, labeler):
        """Signals missing cluster_key are skipped — empty result expected."""
        sigs = [{"termo": "funk"}, {"termo": "samba"}]
        labels = labeler.label_from_flat_signals(sigs, cluster_key="missing_key")
        assert isinstance(labels, dict)
        # No signals have 'missing_key', so result is empty
        assert len(labels) == 0

    def test_many_clusters(self, labeler):
        """Stress test with 20 clusters."""
        clusters = {f"c_{i}": [{"termo": f"word_{i}_{j}"} for j in range(5)] for i in range(20)}
        labels = labeler.label_clusters(clusters)
        assert len(labels) == 20


# ═══════════════════════════════════════════════════════════════════════════════
#  4. API endpoint
# ═══════════════════════════════════════════════════════════════════════════════

class TestClusterLabelsAPI:
    def _load_module(self):
        import importlib.util, pathlib
        path = pathlib.Path(__file__).parent.parent / "api" / "endpoints" / "cluster_labels.py"
        spec = importlib.util.spec_from_file_location("cluster_labels_endpoint", str(path))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_router_importable(self):
        mod = self._load_module()
        assert mod.router is not None
        assert mod.router.prefix == "/api/v8/clusters"

    def test_label_endpoint_exists(self):
        mod = self._load_module()
        assert callable(mod.label_clusters)

    def test_label_flat_endpoint_exists(self):
        mod = self._load_module()
        assert callable(mod.label_flat)

    def test_registered_in_main(self):
        import pathlib
        main_src = (pathlib.Path(__file__).parent.parent / "api" / "main.py").read_text()
        assert "cluster_labels_router" in main_src

    def test_request_model(self):
        mod = self._load_module()
        sig = mod.ClusterSignal(termo="funk")
        assert sig.termo == "funk"
