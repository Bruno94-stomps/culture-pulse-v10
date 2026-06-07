"""
Tests for F-2 — Cluster Stability Temporal
=============================================
Tests the ClusterStabilityAnalyzer and compare_clusters()
from core.clustering.py.
"""
from __future__ import annotations

import pytest


# ═════════════════════════════════════════════════════════════════════════════
# Import & basic tests
# ═════════════════════════════════════════════════════════════════════════════

class TestClusterStabilityImport:
    """Verify module loads correctly."""

    def test_import_compare(self):
        from core.clustering import compare_clusters
        assert callable(compare_clusters)

    def test_import_status_enum(self):
        from core.clustering import StabilityStatus
        assert StabilityStatus.ESTAVEL.value == "estável"
        assert StabilityStatus.EMERGINDO.value == "emergindo"
        assert StabilityStatus.FRAGMENTANDO.value == "fragmentando"
        assert StabilityStatus.INSTAVEL.value == "instável"
        assert StabilityStatus.SEM_DADOS.value == "sem_dados"

    def test_import_analyzer_class(self):
        from core.clustering import ClusterStabilityAnalyzer
        assert ClusterStabilityAnalyzer is not None

    def test_import_convenience(self):
        from core.clustering import compare_signal_clusters
        assert callable(compare_signal_clusters)

    def test_singleton(self):
        from core.clustering import get_stability_analyzer
        a1 = get_stability_analyzer()
        a2 = get_stability_analyzer()
        assert a1 is a2


# ═════════════════════════════════════════════════════════════════════════════
# compare_clusters() tests
# ═════════════════════════════════════════════════════════════════════════════

class TestCompareIdentical:
    """Identical labels → estável, ARI=1, NMI=1."""

    def test_identical_labels(self):
        from core.clustering import compare_clusters, StabilityStatus
        result = compare_clusters(
            [0, 0, 1, 1, 2, 2, 3, 3],
            [0, 0, 1, 1, 2, 2, 3, 3],
        )
        assert result.ari_score == pytest.approx(1.0)
        assert result.nmi_score == pytest.approx(1.0)
        assert result.status == StabilityStatus.ESTAVEL

    def test_identical_badge(self):
        from core.clustering import compare_clusters
        result = compare_clusters([0, 0, 1, 1, 2], [0, 0, 1, 1, 2])
        assert result.badge_emoji == "🟢"


class TestCompareRandom:
    """Completely different labels → instável or very low ARI."""

    def test_random_labels(self):
        from core.clustering import compare_clusters, StabilityStatus
        result = compare_clusters(
            [0, 0, 0, 1, 1, 1, 2, 2],
            [3, 4, 5, 3, 4, 5, 3, 4],
        )
        assert result.ari_score < 0.4
        assert result.status in (StabilityStatus.INSTAVEL, StabilityStatus.FRAGMENTANDO)

    def test_random_badge_is_red_or_yellow(self):
        from core.clustering import compare_clusters
        result = compare_clusters(
            [0, 0, 0, 1, 1, 1, 2, 2],
            [3, 4, 5, 3, 4, 5, 3, 4],
        )
        assert result.badge_emoji in ("🔴", "🟡")


class TestComparePartialOverlap:
    """Moderate overlap → fragmentando or emergindo."""

    def test_new_clusters_emergindo(self):
        from core.clustering import compare_clusters, StabilityStatus
        # T-1: clusters {0, 1}; T: clusters {0, 1, 2} — new cluster 2 emerged
        result = compare_clusters(
            [0, 0, 0, 1, 1, 1, 0, 1],
            [0, 0, 2, 1, 1, 2, 0, 1],
        )
        assert 2 in result.new_clusters
        # If ARI moderate + new clusters → emergindo
        if result.ari_score >= 0.4:
            assert result.status in (StabilityStatus.EMERGINDO, StabilityStatus.ESTAVEL)

    def test_lost_clusters_fragmentando(self):
        from core.clustering import compare_clusters, StabilityStatus
        # T-1: clusters {0, 1, 2}; T: clusters {0, 1} — cluster 2 lost
        result = compare_clusters(
            [0, 0, 1, 1, 2, 2, 0, 1],
            [0, 0, 1, 1, 0, 1, 0, 1],
        )
        assert 2 in result.lost_clusters


class TestEdgeCases:
    """Edge cases: too few samples, different lengths, noise."""

    def test_too_few_samples(self):
        from core.clustering import compare_clusters, StabilityStatus
        result = compare_clusters([0, 1], [0, 1])
        assert result.status == StabilityStatus.SEM_DADOS

    def test_different_lengths(self):
        from core.clustering import compare_clusters, StabilityStatus
        result = compare_clusters([0, 1, 2], [0, 1])
        assert result.status == StabilityStatus.SEM_DADOS

    def test_empty_labels(self):
        from core.clustering import compare_clusters, StabilityStatus
        result = compare_clusters([], [])
        assert result.status == StabilityStatus.SEM_DADOS

    def test_all_noise_filtered(self):
        from core.clustering import compare_clusters, StabilityStatus
        result = compare_clusters(
            [-1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1],
        )
        assert result.status == StabilityStatus.SEM_DADOS

    def test_noise_partial_filter(self):
        from core.clustering import compare_clusters
        result = compare_clusters(
            [0, 0, -1, 1, 1, 1, 0],
            [0, 0, -1, 1, 1, 1, 0],
        )
        # After filtering noise, 6 points remain → should work
        assert result.ari_score == pytest.approx(1.0)


class TestStabilityResult:
    """Test StabilityResult.to_dict()."""

    def test_to_dict_keys(self):
        from core.clustering import compare_clusters
        result = compare_clusters(
            [0, 0, 1, 1, 2, 2, 3, 3],
            [0, 0, 1, 1, 2, 2, 3, 3],
        )
        d = result.to_dict()
        expected_keys = {
            "ari_score", "nmi_score", "status", "badge_emoji",
            "badge_description", "n_clusters_prev", "n_clusters_curr",
            "new_clusters", "lost_clusters", "persistent_clusters", "sample_size",
        }
        assert set(d.keys()) == expected_keys

    def test_to_dict_status_is_string(self):
        from core.clustering import compare_clusters
        d = compare_clusters([0, 0, 1, 1, 2], [0, 0, 1, 1, 2]).to_dict()
        assert isinstance(d["status"], str)

    def test_cluster_counts(self):
        from core.clustering import compare_clusters
        result = compare_clusters(
            [0, 0, 1, 1, 2, 2, 3, 3],
            [0, 0, 1, 1, 4, 4, 5, 5],
        )
        assert result.n_clusters_prev == 4
        assert result.n_clusters_curr == 4
        # Persistent: {0, 1}; New: {4, 5}; Lost: {2, 3}
        assert 0 in result.persistent_clusters
        assert 1 in result.persistent_clusters
        assert 4 in result.new_clusters or 5 in result.new_clusters
        assert 2 in result.lost_clusters or 3 in result.lost_clusters


# ═════════════════════════════════════════════════════════════════════════════
# ClusterStabilityAnalyzer (stateful) tests
# ═════════════════════════════════════════════════════════════════════════════

class TestClusterStabilityAnalyzer:
    """Test the stateful analyzer with push_snapshot()."""

    def _analyzer(self):
        from core.clustering import ClusterStabilityAnalyzer
        return ClusterStabilityAnalyzer()

    def test_no_snapshots(self):
        from core.clustering import StabilityStatus
        a = self._analyzer()
        result = a.latest_comparison()
        assert result.status == StabilityStatus.SEM_DADOS

    def test_single_snapshot(self):
        from core.clustering import StabilityStatus
        a = self._analyzer()
        a.push_snapshot("t1", [0, 0, 1, 1, 2])
        result = a.latest_comparison()
        assert result.status == StabilityStatus.SEM_DADOS

    def test_two_identical_snapshots(self):
        from core.clustering import StabilityStatus
        a = self._analyzer()
        a.push_snapshot("t1", [0, 0, 1, 1, 2, 2])
        a.push_snapshot("t2", [0, 0, 1, 1, 2, 2])
        result = a.latest_comparison()
        assert result.status == StabilityStatus.ESTAVEL

    def test_three_snapshots_uses_last_two(self):
        a = self._analyzer()
        a.push_snapshot("t1", [0, 0, 1, 1, 2, 2])
        a.push_snapshot("t2", [3, 3, 4, 4, 5, 5])
        a.push_snapshot("t3", [3, 3, 4, 4, 5, 5])
        result = a.latest_comparison()
        # t2 vs t3 — identical
        assert result.ari_score == pytest.approx(1.0)

    def test_history(self):
        a = self._analyzer()
        a.push_snapshot("week1", [0, 0, 1])
        a.push_snapshot("week2", [0, 1, 1])
        h = a.history()
        assert len(h) == 2
        assert h[0]["period_id"] == "week1"
        assert h[1]["period_id"] == "week2"

    def test_snapshot_count(self):
        a = self._analyzer()
        assert a.snapshot_count == 0
        a.push_snapshot("t1", [0, 1])
        assert a.snapshot_count == 1

    def test_max_snapshots_enforced(self):
        a = self._analyzer()
        a.MAX_SNAPSHOTS = 5
        for i in range(10):
            a.push_snapshot(f"t{i}", [0, 1, 2])
        assert a.snapshot_count == 5

    def test_clear(self):
        a = self._analyzer()
        a.push_snapshot("t1", [0, 1])
        a.clear()
        assert a.snapshot_count == 0

    def test_different_length_snapshots_padded(self):
        """Snapshots of different length should be handled (padded with -1)."""
        a = self._analyzer()
        a.push_snapshot("t1", [0, 0, 1, 1, 2])
        a.push_snapshot("t2", [0, 0, 1, 1, 2, 3, 3])  # longer
        result = a.latest_comparison()
        # Should not crash; padded points are noise
        assert result.status is not None


# ═════════════════════════════════════════════════════════════════════════════
# compare_signal_clusters() tests
# ═════════════════════════════════════════════════════════════════════════════

class TestCompareSignalClusters:
    """Test signal-based comparison."""

    def test_matching_signals(self):
        from core.clustering import compare_signal_clusters, StabilityStatus
        prev = [
            {"termo": "funk", "cluster_id": 0},
            {"termo": "samba", "cluster_id": 0},
            {"termo": "forró", "cluster_id": 1},
            {"termo": "tech", "cluster_id": 1},
            {"termo": "moda", "cluster_id": 2},
        ]
        curr = [
            {"termo": "funk", "cluster_id": 0},
            {"termo": "samba", "cluster_id": 0},
            {"termo": "forró", "cluster_id": 1},
            {"termo": "tech", "cluster_id": 1},
            {"termo": "moda", "cluster_id": 2},
        ]
        result = compare_signal_clusters(prev, curr)
        assert result.ari_score == pytest.approx(1.0)
        assert result.status == StabilityStatus.ESTAVEL

    def test_no_common_signals(self):
        from core.clustering import compare_signal_clusters, StabilityStatus
        prev = [{"termo": "a", "cluster_id": 0}]
        curr = [{"termo": "b", "cluster_id": 0}]
        result = compare_signal_clusters(prev, curr)
        assert result.status == StabilityStatus.SEM_DADOS

    def test_custom_keys(self):
        from core.clustering import compare_signal_clusters
        prev = [
            {"id": "s1", "group": 0},
            {"id": "s2", "group": 0},
            {"id": "s3", "group": 1},
            {"id": "s4", "group": 1},
            {"id": "s5", "group": 2},
        ]
        curr = [
            {"id": "s1", "group": 0},
            {"id": "s2", "group": 0},
            {"id": "s3", "group": 1},
            {"id": "s4", "group": 1},
            {"id": "s5", "group": 2},
        ]
        result = compare_signal_clusters(
            prev, curr, cluster_key="group", match_key="id"
        )
        assert result.ari_score == pytest.approx(1.0)


# ═════════════════════════════════════════════════════════════════════════════
# Badge/UI tests
# ═════════════════════════════════════════════════════════════════════════════

class TestBadges:
    """Test badge emojis and descriptions."""

    def test_all_statuses_have_badges(self):
        from core.clustering import BADGE_EMOJI, BADGE_DESCRIPTION, StabilityStatus
        for status in StabilityStatus:
            assert status in BADGE_EMOJI
            assert status in BADGE_DESCRIPTION
            assert len(BADGE_EMOJI[status]) > 0
            assert len(BADGE_DESCRIPTION[status]) > 0

    def test_estavel_green(self):
        from core.clustering import BADGE_EMOJI, StabilityStatus
        assert BADGE_EMOJI[StabilityStatus.ESTAVEL] == "🟢"

    def test_instavel_red(self):
        from core.clustering import BADGE_EMOJI, StabilityStatus
        assert BADGE_EMOJI[StabilityStatus.INSTAVEL] == "🔴"


# ═════════════════════════════════════════════════════════════════════════════
# Count
# ═════════════════════════════════════════════════════════════════════════════
# TestClusterStabilityImport:     5
# TestCompareIdentical:           2
# TestCompareRandom:              2
# TestComparePartialOverlap:      2
# TestEdgeCases:                  5
# TestStabilityResult:            3
# TestClusterStabilityAnalyzer:   9
# TestCompareSignalClusters:      3
# TestBadges:                     3
# ═════════════════════════════════════════════════════════════════════════════
# TOTAL:                         34
