#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cluster Stability Analyzer — Culture Pulse V9.2 (F-2)
=========================================================
Compares cluster assignments between two time periods (T vs T-1)
using standard metrics: ARI (Adjusted Rand Index) and NMI
(Normalized Mutual Information).

Produces a stability assessment with:
  - ari_score: -1..1 (1 = identical, 0 = random, <0 = worse than random)
  - nmi_score: 0..1 (1 = identical, 0 = no mutual info)
  - status:  estável | fragmentando | emergindo | instável | sem_dados
  - new_clusters: list of cluster IDs that appeared in T but not T-1
  - lost_clusters: list of cluster IDs that disappeared
  - badge_emoji: visual badge for dashboard

Academic basis:
  - Adjusted Rand Index (Hubert & Arabie 1985)
  - Normalized Mutual Information (Strehl & Ghosh 2002)
  - Threshold calibration follows Vinh et al. 2010

Usage:
    from core.clustering import compare_clusters, StabilityStatus

    result = compare_clusters(labels_prev=[0,0,1,1,2], labels_curr=[0,0,1,1,3])
    # result.status == StabilityStatus.ESTAVEL
    # result.ari_score ~ 0.8+
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from config import config

logger = logging.getLogger(__name__)

# ── Optional dependency ──────────────────────────────────────────────────────
try:
    from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("⚠️ scikit-learn não disponível — ClusterStability em modo fallback")


# ── Enums & Dataclasses ─────────────────────────────────────────────────────

class StabilityStatus(str, Enum):
    """Stability classification for dashboard badge."""
    ESTAVEL = "estável"
    EMERGINDO = "emergindo"
    FRAGMENTANDO = "fragmentando"
    INSTAVEL = "instável"
    SEM_DADOS = "sem_dados"


BADGE_EMOJI: Dict[StabilityStatus, str] = {
    StabilityStatus.ESTAVEL:      "🟢",
    StabilityStatus.EMERGINDO:    "🔵",
    StabilityStatus.FRAGMENTANDO: "🟡",
    StabilityStatus.INSTAVEL:     "🔴",
    StabilityStatus.SEM_DADOS:    "⚪",
}

BADGE_DESCRIPTION: Dict[StabilityStatus, str] = {
    StabilityStatus.ESTAVEL:      "Clusters estáveis — padrão cultural persistente",
    StabilityStatus.EMERGINDO:    "Novos clusters emergindo — tendência nascente",
    StabilityStatus.FRAGMENTANDO: "Clusters se fragmentando — atenção necessária",
    StabilityStatus.INSTAVEL:     "Alta instabilidade — clusters muito diferentes entre períodos",
    StabilityStatus.SEM_DADOS:    "Sem dados suficientes para comparação",
}


@dataclass
class StabilityResult:
    """Result of cluster stability comparison."""
    ari_score: float = 0.0                  # Adjusted Rand Index (-1..1)
    nmi_score: float = 0.0                  # Normalized Mutual Info (0..1)
    status: StabilityStatus = StabilityStatus.SEM_DADOS
    badge_emoji: str = "⚪"
    badge_description: str = ""
    n_clusters_prev: int = 0
    n_clusters_curr: int = 0
    new_clusters: List[int] = field(default_factory=list)
    lost_clusters: List[int] = field(default_factory=list)
    persistent_clusters: List[int] = field(default_factory=list)
    sample_size: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ari_score": round(self.ari_score, 4),
            "nmi_score": round(self.nmi_score, 4),
            "status": self.status.value,
            "badge_emoji": self.badge_emoji,
            "badge_description": self.badge_description,
            "n_clusters_prev": self.n_clusters_prev,
            "n_clusters_curr": self.n_clusters_curr,
            "new_clusters": self.new_clusters,
            "lost_clusters": self.lost_clusters,
            "persistent_clusters": self.persistent_clusters,
            "sample_size": self.sample_size,
        }


# ── Thresholds ───────────────────────────────────────────────────────────────
#
# ARI thresholds (calibrated per Vinh et al. 2010), aligned with V9.9 Reliability
#   > HIGH_THRESHOLD  →  estável
#   > MEDIUM_THRESHOLD →  emergindo/fragmentando
#   ≤ MEDIUM_THRESHOLD →  instável

try:
    ARI_STABLE_THRESHOLD = getattr(config.env, "RELIABILITY_THRESHOLD_HIGH", 0.70)
    ARI_MODERATE_THRESHOLD = getattr(config.env, "RELIABILITY_THRESHOLD_MEDIUM", 0.40)
except AttributeError:
    # Fallback if config structure is unexpected
    ARI_STABLE_THRESHOLD = 0.70
    ARI_MODERATE_THRESHOLD = 0.40

MIN_SAMPLES_FOR_COMPARISON = 5


# ── Core comparison function ─────────────────────────────────────────────────

def compare_clusters(
    labels_prev: List[int],
    labels_curr: List[int],
    *,
    noise_label: int = -1,
) -> StabilityResult:
    """
    Compare cluster assignments between two periods.

    Both lists must have the same length (one entry per data point).
    Points with label == noise_label are excluded from comparison.

    Args:
        labels_prev: Cluster labels from period T-1
        labels_curr: Cluster labels from period T
        noise_label: Label value representing noise/unassigned points

    Returns:
        StabilityResult with ARI, NMI, status, badge
    """
    if len(labels_prev) != len(labels_curr):
        logger.warning("⚠️ labels_prev and labels_curr have different lengths")
        return StabilityResult(
            status=StabilityStatus.SEM_DADOS,
            badge_emoji=BADGE_EMOJI[StabilityStatus.SEM_DADOS],
            badge_description="Erro: listas de labels com tamanhos diferentes",
        )

    if len(labels_prev) < MIN_SAMPLES_FOR_COMPARISON:
        return StabilityResult(
            status=StabilityStatus.SEM_DADOS,
            badge_emoji=BADGE_EMOJI[StabilityStatus.SEM_DADOS],
            badge_description=f"Poucos dados ({len(labels_prev)} < {MIN_SAMPLES_FOR_COMPARISON})",
            sample_size=len(labels_prev),
        )

    # Filter out noise points
    filtered_prev = []
    filtered_curr = []
    for lp, lc in zip(labels_prev, labels_curr):
        if lp != noise_label and lc != noise_label:
            filtered_prev.append(lp)
            filtered_curr.append(lc)

    if len(filtered_prev) < MIN_SAMPLES_FOR_COMPARISON:
        return StabilityResult(
            status=StabilityStatus.SEM_DADOS,
            badge_emoji=BADGE_EMOJI[StabilityStatus.SEM_DADOS],
            badge_description="Poucos dados após filtrar ruído",
            sample_size=len(filtered_prev),
        )

    # Compute cluster sets
    clusters_prev: Set[int] = set(labels_prev) - {noise_label}
    clusters_curr: Set[int] = set(labels_curr) - {noise_label}
    new_clusters = sorted(clusters_curr - clusters_prev)
    lost_clusters = sorted(clusters_prev - clusters_curr)
    persistent = sorted(clusters_prev & clusters_curr)

    # Compute ARI and NMI
    if SKLEARN_AVAILABLE:
        ari = adjusted_rand_score(filtered_prev, filtered_curr)
        nmi = normalized_mutual_info_score(
            filtered_prev, filtered_curr, average_method="arithmetic"
        )
    else:
        # Fallback: simple Jaccard-like overlap
        ari, nmi = _fallback_scores(filtered_prev, filtered_curr)

    # Classify status
    status = _classify_stability(
        ari=ari,
        n_prev=len(clusters_prev),
        n_curr=len(clusters_curr),
        new_count=len(new_clusters),
        lost_count=len(lost_clusters),
    )

    return StabilityResult(
        ari_score=ari,
        nmi_score=nmi,
        status=status,
        badge_emoji=BADGE_EMOJI[status],
        badge_description=BADGE_DESCRIPTION[status],
        n_clusters_prev=len(clusters_prev),
        n_clusters_curr=len(clusters_curr),
        new_clusters=new_clusters,
        lost_clusters=lost_clusters,
        persistent_clusters=persistent,
        sample_size=len(filtered_prev),
    )


def _classify_stability(
    *,
    ari: float,
    n_prev: int,
    n_curr: int,
    new_count: int,
    lost_count: int,
) -> StabilityStatus:
    """
    Classify stability status based on ARI + structural changes.

    Logic:
      - ARI > 0.70 → estável (regardless of minor structural changes)
      - ARI in [0.40, 0.70]:
          - more new than lost → emergindo
          - more lost than new → fragmentando
          - balanced → fragmentando (conservative)
      - ARI < 0.40 → instável
    """
    if ari >= ARI_STABLE_THRESHOLD:
        return StabilityStatus.ESTAVEL

    if ari >= ARI_MODERATE_THRESHOLD:
        if new_count > lost_count:
            return StabilityStatus.EMERGINDO
        else:
            return StabilityStatus.FRAGMENTANDO

    return StabilityStatus.INSTAVEL


def _fallback_scores(
    labels_a: List[int], labels_b: List[int]
) -> Tuple[float, float]:
    """
    Fallback ARI/NMI approximation when sklearn is unavailable.
    Uses simple pair-counting approach.
    """
    n = len(labels_a)
    if n < 2:
        return 0.0, 0.0

    # Count pairs that agree/disagree
    agree_same = 0
    agree_diff = 0
    total_pairs = 0
    for i in range(n):
        for j in range(i + 1, n):
            same_a = labels_a[i] == labels_a[j]
            same_b = labels_b[i] == labels_b[j]
            if same_a and same_b:
                agree_same += 1
            elif not same_a and not same_b:
                agree_diff += 1
            total_pairs += 1

    if total_pairs == 0:
        return 0.0, 0.0

    # Simple Rand Index (not adjusted, but a reasonable fallback)
    rand_index = (agree_same + agree_diff) / total_pairs
    # Scale to [-1, 1] range like ARI (approximate)
    approx_ari = 2.0 * rand_index - 1.0
    # NMI approximation = same as rand (rough)
    return approx_ari, rand_index


# ── Convenience: compare from signal lists ───────────────────────────────────

def compare_signal_clusters(
    signals_prev: List[Dict[str, Any]],
    signals_curr: List[Dict[str, Any]],
    *,
    cluster_key: str = "cluster_id",
    match_key: str = "termo",
    noise_label: int = -1,
) -> StabilityResult:
    """
    Compare clusters from two lists of enriched signals.

    Matches signals by `match_key` (default: "termo"), extracts
    `cluster_key` (default: "cluster_id"), and computes stability.

    Args:
        signals_prev: Enriched signals from period T-1
        signals_curr: Enriched signals from period T
        cluster_key:  Dict key containing cluster assignment
        match_key:    Dict key to match signals across periods

    Returns:
        StabilityResult
    """
    # Build lookup: match_key → cluster_id for each period
    prev_map = {
        s.get(match_key): s.get(cluster_key, noise_label)
        for s in signals_prev
        if s.get(match_key)
    }
    curr_map = {
        s.get(match_key): s.get(cluster_key, noise_label)
        for s in signals_curr
        if s.get(match_key)
    }

    # Find common keys (signals present in both periods)
    common_keys = sorted(set(prev_map.keys()) & set(curr_map.keys()))

    if len(common_keys) < MIN_SAMPLES_FOR_COMPARISON:
        return StabilityResult(
            status=StabilityStatus.SEM_DADOS,
            badge_emoji=BADGE_EMOJI[StabilityStatus.SEM_DADOS],
            badge_description=f"Poucos sinais em comum ({len(common_keys)})",
            sample_size=len(common_keys),
        )

    labels_prev = [prev_map[k] for k in common_keys]
    labels_curr = [curr_map[k] for k in common_keys]

    return compare_clusters(labels_prev, labels_curr, noise_label=noise_label)


# ── Module-level singleton analyzer ─────────────────────────────────────────

class ClusterStabilityAnalyzer:
    """
    Stateful analyzer that stores snapshots and compares across time.

    Usage:
        analyzer = ClusterStabilityAnalyzer()
        analyzer.push_snapshot("2026-02-22", [0, 0, 1, 1, 2, 2])
        analyzer.push_snapshot("2026-02-23", [0, 0, 1, 1, 3, 3])
        result = analyzer.latest_comparison()
        # result.status == StabilityStatus.EMERGINDO
    """

    MAX_SNAPSHOTS = 30  # keep last N snapshots

    def __init__(self) -> None:
        self._snapshots: List[Tuple[str, List[int]]] = []

    def push_snapshot(self, period_id: str, labels: List[int]) -> None:
        """Store a cluster snapshot for a given period."""
        self._snapshots.append((period_id, list(labels)))
        if len(self._snapshots) > self.MAX_SNAPSHOTS:
            self._snapshots = self._snapshots[-self.MAX_SNAPSHOTS:]

    def latest_comparison(self) -> StabilityResult:
        """Compare the two most recent snapshots."""
        if len(self._snapshots) < 2:
            return StabilityResult(
                status=StabilityStatus.SEM_DADOS,
                badge_emoji=BADGE_EMOJI[StabilityStatus.SEM_DADOS],
                badge_description="Precisa de pelo menos 2 snapshots",
            )
        _, prev_labels = self._snapshots[-2]
        _, curr_labels = self._snapshots[-1]

        # Ensure same length (pad shorter with noise)
        max_len = max(len(prev_labels), len(curr_labels))
        padded_prev = prev_labels + [-1] * (max_len - len(prev_labels))
        padded_curr = curr_labels + [-1] * (max_len - len(curr_labels))

        return compare_clusters(padded_prev, padded_curr)

    def history(self) -> List[Dict[str, Any]]:
        """Return list of all snapshots with period IDs."""
        return [
            {"period_id": pid, "n_labels": len(labels), "n_clusters": len(set(labels) - {-1})}
            for pid, labels in self._snapshots
        ]

    @property
    def snapshot_count(self) -> int:
        return len(self._snapshots)

    def clear(self) -> None:
        self._snapshots.clear()


# ── Module singleton ─────────────────────────────────────────────────────────

_default_analyzer: Optional[ClusterStabilityAnalyzer] = None


def get_stability_analyzer() -> ClusterStabilityAnalyzer:
    """Get or create module-level singleton."""
    global _default_analyzer
    if _default_analyzer is None:
        _default_analyzer = ClusterStabilityAnalyzer()
    return _default_analyzer
