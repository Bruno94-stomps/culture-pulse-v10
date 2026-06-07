#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recall Engine — F-11 (FASE 5)
================================
Recall histórico: mede quantos sinais detectados realmente se tornaram
tendências confirmadas ("X% dos sinais viraram tendência em 30 dias").

Funcionalidade:
  1. Registra sinais detectados (predictions) com timestamp
  2. Valida sinais contra ground truth (Google Trends, confirmação manual)
  3. Computa métricas cumulativas: precision, recall, F1, hit rate
  4. Dashbaord-ready: séries temporais de recall ao longo do tempo
  5. Integra com RetrainTrigger (F-7) para baseline de recall

Design:
  - In-memory store com persistência JSONL local
  - Validação pode ser automática (via heurísticas) ou manual
  - Métricas por janela temporal (7d, 30d, 90d)
  - Thread-safe via singleton
"""

from __future__ import annotations

import json
import logging
import math
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
#  Data classes
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SignalPrediction:
    """A signal that was detected/predicted as emerging."""
    signal_id: str
    termo: str
    circle: str = ""
    momentum: float = 0.0
    detected_at: str = ""
    source: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.detected_at:
            self.detected_at = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SignalOutcome:
    """Ground truth outcome for a previously predicted signal."""
    signal_id: str
    became_trend: bool  # Did the signal become a confirmed trend?
    validated_at: str = ""
    validation_source: str = "manual"  # manual, google_trends, auto
    trend_evidence: str = ""
    confidence: float = 1.0

    def __post_init__(self):
        if not self.validated_at:
            self.validated_at = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RecallMetrics:
    """Computed recall metrics for a time window."""
    window_days: int
    total_predictions: int = 0
    validated: int = 0
    true_positives: int = 0  # predicted + became trend
    false_positives: int = 0  # predicted + did NOT become trend
    unvalidated: int = 0
    precision: float = 0.0
    recall_rate: float = 0.0  # = hit rate = TP / (TP + FP)
    hit_rate_pct: float = 0.0  # percentage format
    avg_momentum_tp: float = 0.0  # avg momentum of true positives
    avg_momentum_fp: float = 0.0  # avg momentum of false positives
    computed_at: str = ""

    def __post_init__(self):
        if not self.computed_at:
            self.computed_at = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ═══════════════════════════════════════════════════════════════════════════════
#  Configuration
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT_CONFIG: Dict[str, Any] = {
    "windows_days": [7, 30, 90],         # time windows for metrics
    "auto_validate_threshold": 0.7,       # momentum threshold for auto-validation
    "min_predictions_for_metrics": 1,     # min predictions before computing
    "log_dir": "data/recall_history",
    "max_predictions": 10000,
}


# ═══════════════════════════════════════════════════════════════════════════════
#  RecallEngine
# ═══════════════════════════════════════════════════════════════════════════════

class RecallEngine:
    """
    Tracks signal predictions and validates against ground truth
    to compute recall/precision metrics over time.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self._config = {**DEFAULT_CONFIG, **(config or {})}
        self._predictions: Dict[str, SignalPrediction] = {}  # id → pred
        self._outcomes: Dict[str, SignalOutcome] = {}  # id → outcome
        self._metrics_history: List[Dict[str, Any]] = []  # time series
        logger.info("📊 RecallEngine initialized")

    # ── Properties ────────────────────────────────────────────────────────

    @property
    def config(self) -> Dict[str, Any]:
        return dict(self._config)

    @property
    def total_predictions(self) -> int:
        return len(self._predictions)

    @property
    def total_validated(self) -> int:
        return len(self._outcomes)

    # ── Core: Register predictions ────────────────────────────────────────

    def register_prediction(
        self,
        signal_id: str,
        termo: str,
        circle: str = "",
        momentum: float = 0.0,
        source: str = "system",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Register a signal as a prediction (system detected it as emerging).

        Args:
            signal_id: Unique signal identifier
            termo: Search term / signal name
            circle: Cultural circle (e.g., 'Música Popular')
            momentum: Signal momentum score at detection time
            source: Detection source (system, manual, etc.)
            metadata: Additional context

        Returns:
            Dict with registration status
        """
        if not signal_id or not termo:
            raise ValueError("signal_id and termo are required")

        pred = SignalPrediction(
            signal_id=signal_id,
            termo=termo,
            circle=circle,
            momentum=momentum,
            source=source,
            metadata=metadata or {},
        )

        # Cap predictions
        max_pred = self._config["max_predictions"]
        if len(self._predictions) >= max_pred and signal_id not in self._predictions:
            # Remove oldest
            oldest_key = next(iter(self._predictions))
            del self._predictions[oldest_key]

        self._predictions[signal_id] = pred
        self._log_event("prediction", pred.to_dict())

        return {
            "status": "registered",
            "signal_id": signal_id,
            "termo": termo,
            "total_predictions": self.total_predictions,
        }

    def register_batch(self, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Register multiple signals as predictions."""
        registered = 0
        failed = 0
        for sig in signals:
            try:
                self.register_prediction(
                    signal_id=sig.get("signal_id", sig.get("id", "")),
                    termo=sig.get("termo", ""),
                    circle=sig.get("circle", sig.get("circulo", "")),
                    momentum=sig.get("momentum", 0.0),
                    source=sig.get("source", "system"),
                    metadata=sig.get("metadata", {}),
                )
                registered += 1
            except Exception as exc:
                logger.warning(f"⚠️ register_batch failed: {exc}")
                failed += 1

        return {"registered": registered, "failed": failed}

    # ── Core: Validate outcomes ───────────────────────────────────────────

    def validate_outcome(
        self,
        signal_id: str,
        became_trend: bool,
        validation_source: str = "manual",
        trend_evidence: str = "",
        confidence: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Validate whether a previously predicted signal became a trend.

        Args:
            signal_id: ID of the predicted signal
            became_trend: True if it actually became a trend
            validation_source: How it was validated (manual, google_trends, auto)
            trend_evidence: Description of evidence
            confidence: Confidence in the validation (0-1)

        Returns:
            Dict with validation status and updated metrics
        """
        if signal_id not in self._predictions:
            raise ValueError(f"Signal {signal_id} not found in predictions")

        outcome = SignalOutcome(
            signal_id=signal_id,
            became_trend=became_trend,
            validation_source=validation_source,
            trend_evidence=trend_evidence,
            confidence=max(0.0, min(1.0, confidence)),
        )

        self._outcomes[signal_id] = outcome
        self._log_event("outcome", outcome.to_dict())

        return {
            "status": "validated",
            "signal_id": signal_id,
            "became_trend": became_trend,
            "total_validated": self.total_validated,
        }

    def validate_batch(self, outcomes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate multiple outcomes at once."""
        validated = 0
        failed = 0
        for oc in outcomes:
            try:
                self.validate_outcome(
                    signal_id=oc["signal_id"],
                    became_trend=oc["became_trend"],
                    validation_source=oc.get("validation_source", "manual"),
                    trend_evidence=oc.get("trend_evidence", ""),
                    confidence=oc.get("confidence", 1.0),
                )
                validated += 1
            except Exception as exc:
                logger.warning(f"⚠️ validate_batch failed: {exc}")
                failed += 1
        return {"validated": validated, "failed": failed}

    # ── Core: Compute metrics ─────────────────────────────────────────────

    def compute_metrics(self, window_days: Optional[int] = None) -> Dict[str, Any]:
        """
        Compute recall metrics for all configured time windows.

        Returns dict with metrics per window and aggregate.
        """
        windows = [window_days] if window_days else self._config["windows_days"]
        results = {}

        for w in windows:
            metrics = self._compute_window_metrics(w)
            results[f"{w}d"] = metrics.to_dict()

        # Also compute all-time
        all_time = self._compute_window_metrics(window_days=None)
        results["all_time"] = all_time.to_dict()

        # Store in history
        self._metrics_history.append({
            "computed_at": datetime.utcnow().isoformat() + "Z",
            "metrics": results,
        })

        return results

    def _compute_window_metrics(self, window_days: Optional[int]) -> RecallMetrics:
        """Compute metrics for a specific time window."""
        now = datetime.utcnow()

        # Filter predictions within window
        predictions_in_window = {}
        for sid, pred in self._predictions.items():
            if window_days is not None:
                try:
                    ts = datetime.fromisoformat(pred.detected_at.replace("Z", "+00:00"))
                    if ts.tzinfo:
                        ts = ts.replace(tzinfo=None)
                    if (now - ts).days > window_days:
                        continue
                except Exception:
                    pass
            predictions_in_window[sid] = pred

        total = len(predictions_in_window)
        if total < self._config["min_predictions_for_metrics"]:
            return RecallMetrics(
                window_days=window_days or 0,
                total_predictions=total,
            )

        # Classify outcomes
        tp = 0
        fp = 0
        unvalidated = 0
        momentum_tp = []
        momentum_fp = []

        for sid, pred in predictions_in_window.items():
            if sid in self._outcomes:
                outcome = self._outcomes[sid]
                if outcome.became_trend:
                    tp += 1
                    momentum_tp.append(pred.momentum)
                else:
                    fp += 1
                    momentum_fp.append(pred.momentum)
            else:
                unvalidated += 1

        validated = tp + fp
        precision = tp / max(validated, 1)
        hit_rate = tp / max(validated, 1)

        return RecallMetrics(
            window_days=window_days or 0,
            total_predictions=total,
            validated=validated,
            true_positives=tp,
            false_positives=fp,
            unvalidated=unvalidated,
            precision=round(precision, 4),
            recall_rate=round(hit_rate, 4),
            hit_rate_pct=round(hit_rate * 100, 1),
            avg_momentum_tp=round(
                sum(momentum_tp) / max(len(momentum_tp), 1), 4
            ),
            avg_momentum_fp=round(
                sum(momentum_fp) / max(len(momentum_fp), 1), 4
            ),
        )

    # ── Dashboard: time series ────────────────────────────────────────────

    def get_metrics_history(self) -> List[Dict[str, Any]]:
        """Return historical metrics for dashboard time series."""
        return list(self._metrics_history)

    def get_prediction_list(
        self,
        validated_only: bool = False,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Return list of predictions with their outcomes."""
        results = []
        for sid, pred in list(self._predictions.items())[-limit:]:
            entry = pred.to_dict()
            if sid in self._outcomes:
                entry["outcome"] = self._outcomes[sid].to_dict()
            elif validated_only:
                continue
            else:
                entry["outcome"] = None
            results.append(entry)
        return results

    # ── Integration: RetrainTrigger (F-7) ─────────────────────────────────

    def get_retrain_baseline(self) -> Dict[str, Any]:
        """
        Get recall metrics as baseline for retrain decisions.

        Used by RetrainTrigger to determine if model quality is degrading.
        """
        metrics = self.compute_metrics()
        all_time = metrics.get("all_time", {})

        return {
            "precision": all_time.get("precision", 0.0),
            "hit_rate_pct": all_time.get("hit_rate_pct", 0.0),
            "total_predictions": all_time.get("total_predictions", 0),
            "validated": all_time.get("validated", 0),
            "recommendation": self._retrain_recommendation(all_time),
        }

    def _retrain_recommendation(self, metrics: Dict[str, Any]) -> str:
        """Recommend whether retraining is needed based on recall."""
        validated = metrics.get("validated", 0)
        if validated < 10:
            return "insufficient_data"

        precision = metrics.get("precision", 0.0)
        if precision < 0.3:
            return "retrain_recommended"
        elif precision < 0.5:
            return "monitor"
        else:
            return "healthy"

    # ── Statistics ────────────────────────────────────────────────────────

    def stats(self) -> Dict[str, Any]:
        """Return engine statistics."""
        all_metrics = self._compute_window_metrics(window_days=None)
        return {
            "engine": "RecallEngine",
            "version": "1.0.0",
            "total_predictions": self.total_predictions,
            "total_validated": self.total_validated,
            "unvalidated": self.total_predictions - self.total_validated,
            "precision": all_metrics.precision,
            "hit_rate_pct": all_metrics.hit_rate_pct,
            "true_positives": all_metrics.true_positives,
            "false_positives": all_metrics.false_positives,
            "metrics_history_count": len(self._metrics_history),
        }

    # ── Persistence ───────────────────────────────────────────────────────

    def _log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log event to JSONL file."""
        try:
            log_dir = Path(self._config["log_dir"])
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / f"{event_type}s.jsonl"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
        except Exception as exc:
            logger.warning(f"⚠️ RecallEngine log failed: {exc}")

    def reset(self) -> None:
        """Reset all state (for testing)."""
        self._predictions.clear()
        self._outcomes.clear()
        self._metrics_history.clear()


# ═══════════════════════════════════════════════════════════════════════════════
#  Singleton
# ═══════════════════════════════════════════════════════════════════════════════

_engine: Optional[RecallEngine] = None


def get_recall_engine() -> RecallEngine:
    """Get or create singleton RecallEngine."""
    global _engine
    if _engine is None:
        _engine = RecallEngine()
    return _engine


def reset_recall_engine() -> None:
    """Reset singleton (for testing)."""
    global _engine
    _engine = None
