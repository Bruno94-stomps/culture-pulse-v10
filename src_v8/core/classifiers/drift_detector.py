#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S2.4 │ P14 — LSDD Cultural Drift Detector
Culture Pulse V9.0 — Sprint 2, Passo 4

PROBLEMA:
  Sem detecção de drift, o modelo pode "envelhecer" silenciosamente
  enquanto a cultura muda (novas gírias, novos movimentos, novos termos).

  O `monitoring/context_drift_detector.py` existente usa cosine distance
  termo a termo — útil mas limitado. NÃO detecta shift de distribuição.

SOLUÇÃO:
  LSDD (Least-Squares Density Difference) via alibi-detect:
  - Detecta mudanças na *distribuição conjunta* de features
  - Não compara termos isolados — compara a "forma" do espaço de features
  - Mais sensível a mudanças sutis e graduais
  - Teste estatístico com p-value (p < 0.05 = drift)

PIPELINE:
  1. Carrega features S2.2+S2.3 dos 186 sinais (referência)
  2. Novos sinais coletados → extrai mesmas features
  3. LSDD compara distribuição referência vs corrente
  4. Se drift detectado → alerta + log em Supabase

INTEGRAÇÃO:
  - core/drift_detector.py (ESTE ARQUIVO) — classe CulturalDriftDetector
  - api/endpoints/streaming.py — checar drift a cada N batches
  - dashboard badge — "⚠️ Drift detectado"
  - Supabase drift_events — log via REST API

Autor: Culture Pulse Team
Data: 2026-02-19
Sprint: S2.4 │ P14
"""

import json
import logging
import math
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════
# LAZY IMPORTS — alibi-detect é pesado, não carregar até precisar
# ═══════════════════════════════════════════════════════════════════════

_LSDDDrift = None


def _get_lsdd_class():
    """Lazy import para alibi_detect.cd.LSDDDrift."""
    global _LSDDDrift
    if _LSDDDrift is None:
        try:
            from alibi_detect.cd import LSDDDrift
            _LSDDDrift = LSDDDrift
            logger.info("✅ alibi-detect LSDDDrift loaded (PyTorch backend)")
        except ImportError as e:
            raise ImportError(
                "alibi-detect não instalado. Execute: pip install alibi-detect\n"
                f"Erro original: {e}"
            )
    return _LSDDDrift


# ═══════════════════════════════════════════════════════════════════════
# FEATURE VECTOR BUILDER
# ═══════════════════════════════════════════════════════════════════════
# Constrói vetor de features numérico a partir dos dados S2.2+S2.3
# para alimentar o LSDD detector.

# Features usadas (8 dimensões):
FEATURE_COLUMNS = [
    # S2.3 scaled features (já na mesma escala)
    "momentum_scaled",
    "volume_scaled",
    "sentiment_scaled",
    "score_scaled",
    # S2.2 features (já em 0-1)
    "novelty_score",
    "signal_strength",
    "composite_rank_score",
    "ner_penalty",
]


def build_feature_vector(signal: dict) -> Optional[np.ndarray]:
    """
    Extrai vetor de 8 features de um sinal do Supabase.

    Args:
        signal: dict com raw_data contendo s22_features e s23_scaled

    Returns:
        np.ndarray shape (8,) float32, or None se dados insuficientes
    """
    rd = signal.get("raw_data", {}) or {}
    s22 = rd.get("s22_features", {}) or {}
    s23 = rd.get("s23_scaled", {}) or {}

    vec = []
    missing = 0
    for col in FEATURE_COLUMNS:
        val = s23.get(col) or s22.get(col)
        if val is not None and isinstance(val, (int, float)):
            vec.append(float(val))
        else:
            vec.append(0.0)
            missing += 1

    # Se mais de 50% missing, rejeitar
    if missing > len(FEATURE_COLUMNS) // 2:
        return None

    return np.array(vec, dtype=np.float32)


def build_feature_matrix(signals: List[dict]) -> Tuple[np.ndarray, List[int]]:
    """
    Constrói matriz de features a partir de lista de sinais.

    Returns:
        X: np.ndarray shape (n_valid, 8) float32
        valid_ids: list of signal ids included
    """
    vectors = []
    valid_ids = []

    for s in signals:
        vec = build_feature_vector(s)
        if vec is not None:
            vectors.append(vec)
            valid_ids.append(s.get("id", -1))

    if not vectors:
        return np.empty((0, len(FEATURE_COLUMNS)), dtype=np.float32), []

    X = np.stack(vectors)
    return X, valid_ids


# ═══════════════════════════════════════════════════════════════════════
# DRIFT ALERT
# ═══════════════════════════════════════════════════════════════════════

class DriftAlert:
    """Represents a detected cultural drift event."""

    def __init__(
        self,
        is_drift: bool,
        p_value: float,
        threshold: float,
        severity: str,
        n_reference: int,
        n_current: int,
        feature_stats: Dict[str, Any],
        timestamp: Optional[datetime] = None,
        recommendation: str = "",
    ):
        self.is_drift = is_drift
        self.p_value = p_value
        self.threshold = threshold
        self.severity = severity
        self.n_reference = n_reference
        self.n_current = n_current
        self.feature_stats = feature_stats
        self.timestamp = timestamp or datetime.now()
        self.recommendation = recommendation

    def to_dict(self) -> dict:
        return {
            "is_drift": self.is_drift,
            "p_value": round(self.p_value, 6),
            "threshold": self.threshold,
            "severity": self.severity,
            "n_reference": self.n_reference,
            "n_current": self.n_current,
            "feature_stats": self.feature_stats,
            "timestamp": self.timestamp.isoformat(),
            "recommendation": self.recommendation,
        }

    def __repr__(self):
        emoji = "🌊" if self.is_drift else "✅"
        return (
            f"{emoji} DriftAlert(drift={self.is_drift}, p={self.p_value:.4f}, "
            f"severity={self.severity}, ref={self.n_reference}, cur={self.n_current})"
        )


# ═══════════════════════════════════════════════════════════════════════
# CULTURAL DRIFT DETECTOR
# ═══════════════════════════════════════════════════════════════════════

class CulturalDriftDetector:
    """
    LSDD-based drift detector for Culture Pulse signals.

    Compares the joint distribution of cultural features between a reference
    window (e.g., last 7 days of established signals) and the current batch
    of incoming signals.

    Unlike per-term cosine drift (monitoring/context_drift_detector.py),
    this detects shifts in the *entire feature space* — catching subtle
    cultural movements that affect multiple dimensions simultaneously.

    Attributes:
        p_val: Significance level (default 0.05)
        backend: 'pytorch' (default) or 'tensorflow'
        min_reference: Minimum reference samples (default 30)
        min_current: Minimum current samples for a check (default 10)
        detector: The fitted LSDDDrift object (None until fit())
        x_ref: Reference feature matrix
        alert_history: List of past DriftAlert objects
    """

    def __init__(
        self,
        p_val: float = 0.05,
        backend: str = "pytorch",
        min_reference: int = 30,
        min_current: int = 10,
    ):
        self.p_val = p_val
        self.backend = backend
        self.min_reference = min_reference
        self.min_current = min_current

        self.detector = None
        self.x_ref: Optional[np.ndarray] = None
        self.ref_ids: List[int] = []
        self.fitted_at: Optional[datetime] = None
        self.alert_history: List[DriftAlert] = []
        self.check_count = 0

        logger.info(
            f"CulturalDriftDetector initialized (p_val={p_val}, "
            f"backend={backend}, min_ref={min_reference})"
        )

    # ─── FIT ────────────────────────────────────────────────────────

    def fit(self, signals: List[dict]) -> bool:
        """
        Fit the detector with reference signals.

        Args:
            signals: List of Supabase signal dicts with raw_data

        Returns:
            True if fit successful, False otherwise
        """
        X_ref, valid_ids = build_feature_matrix(signals)

        if len(valid_ids) < self.min_reference:
            logger.warning(
                f"Insufficient reference signals: {len(valid_ids)} < {self.min_reference}"
            )
            return False

        self.x_ref = X_ref
        self.ref_ids = valid_ids

        LSDDDrift = _get_lsdd_class()
        self.detector = LSDDDrift(
            X_ref,
            backend=self.backend,
            p_val=self.p_val,
        )

        self.fitted_at = datetime.now()
        logger.info(
            f"✅ Detector fitted with {len(valid_ids)} reference signals "
            f"({X_ref.shape[1]} features)"
        )
        return True

    def fit_from_matrix(self, X_ref: np.ndarray) -> bool:
        """
        Fit directly from a feature matrix (for testing).

        Args:
            X_ref: np.ndarray shape (n, d) float32
        """
        if X_ref.shape[0] < self.min_reference:
            logger.warning(
                f"Insufficient reference samples: {X_ref.shape[0]} < {self.min_reference}"
            )
            return False

        self.x_ref = X_ref
        self.ref_ids = list(range(X_ref.shape[0]))

        LSDDDrift = _get_lsdd_class()
        self.detector = LSDDDrift(
            X_ref,
            backend=self.backend,
            p_val=self.p_val,
        )

        self.fitted_at = datetime.now()
        logger.info(f"✅ Detector fitted with matrix shape {X_ref.shape}")
        return True

    # ─── CHECK ──────────────────────────────────────────────────────

    def check(
        self,
        signals: Optional[List[dict]] = None,
        X_current: Optional[np.ndarray] = None,
    ) -> DriftAlert:
        """
        Check for drift in current signals vs reference.

        Args:
            signals: List of new signal dicts (mutually exclusive with X_current)
            X_current: Feature matrix of current batch (mutually exclusive with signals)

        Returns:
            DriftAlert with is_drift, p_value, severity, etc.
        """
        if self.detector is None:
            raise RuntimeError("Detector not fitted. Call fit() first.")

        # Build feature matrix
        if X_current is not None:
            pass  # Use provided matrix
        elif signals is not None:
            X_current, _ = build_feature_matrix(signals)
        else:
            raise ValueError("Provide either signals or X_current")

        n_current = X_current.shape[0]
        if n_current < self.min_current:
            logger.warning(
                f"Too few current samples: {n_current} < {self.min_current}. "
                "Returning no-drift alert."
            )
            return DriftAlert(
                is_drift=False,
                p_value=1.0,
                threshold=self.p_val,
                severity="none",
                n_reference=self.x_ref.shape[0],
                n_current=n_current,
                feature_stats={},
                recommendation="Dados insuficientes para verificação de drift.",
            )

        # Run LSDD test
        self.check_count += 1
        t0 = time.time()
        result = self.detector.predict(X_current)
        elapsed = time.time() - t0

        is_drift = bool(result["data"]["is_drift"])
        p_value = float(result["data"]["p_val"])

        # Compute per-feature stats (which features shifted most)
        feature_stats = self._compute_feature_stats(X_current)
        feature_stats["check_elapsed_ms"] = round(elapsed * 1000, 1)
        feature_stats["check_number"] = self.check_count

        # Severity
        severity = self._classify_severity(p_value, is_drift)

        # Recommendation
        recommendation = self._generate_recommendation(
            is_drift, p_value, severity, feature_stats
        )

        alert = DriftAlert(
            is_drift=is_drift,
            p_value=p_value,
            threshold=self.p_val,
            severity=severity,
            n_reference=self.x_ref.shape[0],
            n_current=n_current,
            feature_stats=feature_stats,
            recommendation=recommendation,
        )

        self.alert_history.append(alert)

        if is_drift:
            logger.warning(f"🌊 DRIFT DETECTED: {alert}")
        else:
            logger.info(f"✅ No drift: p_value={p_value:.4f}")

        return alert

    # ─── PER-FEATURE ANALYSIS ──────────────────────────────────────

    def _compute_feature_stats(self, X_current: np.ndarray) -> Dict[str, Any]:
        """
        Compute per-feature shift statistics.

        For each feature dimension, compare reference mean/std vs current mean/std
        to help understand WHICH features are drifting.
        """
        stats = {}

        ref_means = np.mean(self.x_ref, axis=0)
        ref_stds = np.std(self.x_ref, axis=0)
        cur_means = np.mean(X_current, axis=0)
        cur_stds = np.std(X_current, axis=0)

        feature_shifts = []
        for i, col in enumerate(FEATURE_COLUMNS):
            shift = abs(cur_means[i] - ref_means[i])
            normalized_shift = shift / (ref_stds[i] + 1e-8)

            feature_shifts.append({
                "feature": col,
                "ref_mean": round(float(ref_means[i]), 4),
                "ref_std": round(float(ref_stds[i]), 4),
                "cur_mean": round(float(cur_means[i]), 4),
                "cur_std": round(float(cur_stds[i]), 4),
                "abs_shift": round(float(shift), 4),
                "normalized_shift": round(float(normalized_shift), 4),
            })

        # Sort by normalized shift (which features moved most)
        feature_shifts.sort(key=lambda x: x["normalized_shift"], reverse=True)

        stats["feature_shifts"] = feature_shifts
        stats["top_shifted_feature"] = feature_shifts[0]["feature"] if feature_shifts else None
        stats["max_normalized_shift"] = feature_shifts[0]["normalized_shift"] if feature_shifts else 0.0

        return stats

    # ─── SEVERITY ──────────────────────────────────────────────────

    @staticmethod
    def _classify_severity(p_value: float, is_drift: bool) -> str:
        """
        Classify drift severity based on p-value.

        Thresholds:
          none:     p > 0.05 (no drift)
          low:      0.01 < p ≤ 0.05
          medium:   0.001 < p ≤ 0.01
          high:     0.0001 < p ≤ 0.001
          critical: p ≤ 0.0001
        """
        if not is_drift:
            return "none"
        if p_value > 0.01:
            return "low"
        if p_value > 0.001:
            return "medium"
        if p_value > 0.0001:
            return "high"
        return "critical"

    # ─── RECOMMENDATION ───────────────────────────────────────────

    @staticmethod
    def _generate_recommendation(
        is_drift: bool, p_value: float, severity: str,
        feature_stats: Dict[str, Any]
    ) -> str:
        """Generate actionable recommendation based on drift analysis."""
        if not is_drift:
            return "Nenhum drift detectado. Distribuição de features estável."

        top_feature = feature_stats.get("top_shifted_feature", "?")
        max_shift = feature_stats.get("max_normalized_shift", 0)

        base = f"🌊 Drift cultural detectado (p={p_value:.4f}, severity={severity}). "
        base += f"Feature mais afetada: {top_feature} (shift={max_shift:.2f}σ). "

        if severity == "low":
            return base + "Monitorar nas próximas 24h."
        elif severity == "medium":
            return base + "Revisar análises recentes. Considerar recalibrar pipeline."
        elif severity == "high":
            return base + "⚠️ AÇÃO: Recalibrar referência do detector com dados recentes."
        else:  # critical
            return base + "🚨 URGENTE: Vocabulário cultural mudou significativamente. Retreino necessário."

    # ─── REFIT ─────────────────────────────────────────────────────

    def refit(self, new_signals: List[dict]) -> bool:
        """
        Refit detector with new reference data (after drift detected).

        In production, call this when drift is confirmed and new data
        represents the "new normal".
        """
        logger.info("🔄 Refitting detector with new reference data...")
        return self.fit(new_signals)

    # ─── SUMMARY ───────────────────────────────────────────────────

    def get_summary(self) -> Dict[str, Any]:
        """Return summary of detector state and history."""
        recent_alerts = self.alert_history[-20:]  # Last 20

        drift_count = sum(1 for a in recent_alerts if a.is_drift)
        total_checks = len(recent_alerts)

        return {
            "fitted": self.detector is not None,
            "fitted_at": self.fitted_at.isoformat() if self.fitted_at else None,
            "n_reference": self.x_ref.shape[0] if self.x_ref is not None else 0,
            "n_features": len(FEATURE_COLUMNS),
            "feature_columns": FEATURE_COLUMNS,
            "p_val_threshold": self.p_val,
            "total_checks": self.check_count,
            "recent_checks": total_checks,
            "recent_drifts": drift_count,
            "drift_rate": drift_count / total_checks if total_checks > 0 else 0.0,
            "last_alert": self.alert_history[-1].to_dict() if self.alert_history else None,
        }

    # ─── DASHBOARD BADGE ───────────────────────────────────────────

    def get_dashboard_badge(self) -> Dict[str, str]:
        """
        Generate badge data for Streamlit dashboard.

        Returns dict with: status, emoji, color, message
        """
        if not self.alert_history:
            return {
                "status": "unknown",
                "emoji": "❓",
                "color": "gray",
                "message": "Drift detector: sem verificações ainda",
            }

        last = self.alert_history[-1]
        if not last.is_drift:
            return {
                "status": "stable",
                "emoji": "✅",
                "color": "green",
                "message": f"Distribuição estável (p={last.p_value:.3f})",
            }

        color_map = {
            "low": "yellow",
            "medium": "orange",
            "high": "red",
            "critical": "red",
        }

        return {
            "status": "drift_detected",
            "emoji": "⚠️",
            "color": color_map.get(last.severity, "orange"),
            "message": f"Drift detectado — {last.severity} (p={last.p_value:.4f})",
        }


# ═══════════════════════════════════════════════════════════════════════
# SUPABASE INTEGRATION
# ═══════════════════════════════════════════════════════════════════════

SUPABASE_URL = os.getenv(
    "SUPABASE_URL", "https://wsizqmnnicpgblopmxyv.supabase.co"
)
SUPABASE_KEY = os.getenv(
    "SUPABASE_SERVICE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndzaXpxbW5uaWNwZ2Jsb3BteHl2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MTQ0MDExNiwiZXhwIjoyMDg3MDE2MTE2fQ."
    "ca8oGhfR1Ek7t5n9fmCS3O5UaaCBUhqRAIJtavc5QpE"
)


def _supabase_headers(prefer: str = "") -> dict:
    h = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    if prefer:
        h["Prefer"] = prefer
    return h


def fetch_reference_signals() -> List[dict]:
    """Fetch all signals from Supabase to build reference distribution."""
    import requests

    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/cultural_signals?select=*&order=id.asc",
        headers=_supabase_headers(),
    )
    r.raise_for_status()
    signals = r.json()
    logger.info(f"📥 Fetched {len(signals)} reference signals")
    return signals


def log_drift_event(alert: DriftAlert) -> bool:
    """
    Log drift event to Supabase.

    Since we can't create tables via REST, we store in a dedicated
    signal entry with tipo='drift_event'.
    We PATCH the first signal's raw_data.drift_events list.
    """
    import requests

    # Fetch current drift_events from signal id=1
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/cultural_signals?id=eq.1&select=raw_data",
        headers=_supabase_headers(),
    )
    if r.status_code != 200 or not r.json():
        logger.warning("Could not fetch signal #1 for drift_events log")
        return False

    raw = r.json()[0].get("raw_data", {}) or {}
    events = raw.get("drift_events", [])
    if not isinstance(events, list):
        events = []

    # Append new event (keep last 50)
    events.append(alert.to_dict())
    events = events[-50:]

    raw["drift_events"] = events

    r2 = requests.patch(
        f"{SUPABASE_URL}/rest/v1/cultural_signals?id=eq.1",
        headers=_supabase_headers(prefer="return=minimal"),
        json={"raw_data": raw},
    )

    ok = r2.status_code in (200, 204)
    if ok:
        logger.info(f"📝 Drift event logged to Supabase (total: {len(events)})")
    return ok


# ═══════════════════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════════════════

def create_detector_from_supabase(
    p_val: float = 0.05,
) -> Tuple[CulturalDriftDetector, int]:
    """
    Factory: create and fit a detector from current Supabase signals.

    Returns:
        (detector, n_reference) tuple
    """
    signals = fetch_reference_signals()
    detector = CulturalDriftDetector(p_val=p_val)
    ok = detector.fit(signals)

    if not ok:
        raise RuntimeError(
            f"Failed to fit detector. Need ≥{detector.min_reference} signals with features."
        )

    return detector, len(signals)
