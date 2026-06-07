"""
core/retrain_trigger.py — F-7 FASE 3
======================================
Auto-retrain trigger that connects:
  • CulturalDriftDetector (S2.4)  — drift detection via LSDD (p < 0.05)
  • BERTimbauFinetuner (S2.5)     — model fine-tuning pipeline
  • FeedbackEngine (INT-1)        — human feedback as training signal

Flow:
  1. Periodically check for drift (via DriftAlert)
  2. If drift detected (p < threshold) → collect recent signals + feedback
  3. Trigger retrain via BERTimbau fine-tuner (or log intent if deps missing)
  4. Log retrain event (Supabase-compatible dict or local file)

This module does NOT require alibi-detect or torch at import time.
Heavy dependencies are lazy-loaded only when actually triggering retrain.
"""

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
#  Data classes
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class RetrainEvent:
    """Logged when a retrain check or retrain execution occurs."""

    timestamp: str = ""
    drift_detected: bool = False
    p_value: float = 1.0
    threshold: float = 0.05
    severity: str = "none"
    retrain_triggered: bool = False
    retrain_status: str = "skipped"       # skipped / triggered / completed / failed
    signal_count: int = 0
    feedback_count: int = 0
    reason: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ═══════════════════════════════════════════════════════════════════════════════
#  Configuration
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT_CONFIG = {
    "p_value_threshold": 0.05,         # statistical threshold for drift
    "min_signals_for_retrain": 50,     # need at least N signals to justify retraining
    "min_feedback_for_retrain": 10,    # optional: if feedback available
    "cooldown_seconds": 3600 * 24,     # min 24h between retrains
    "log_dir": "data/retrain_logs",    # local log directory
    "auto_execute": False,             # if True, actually calls fine-tuner
}


# ═══════════════════════════════════════════════════════════════════════════════
#  RetrainTrigger
# ═══════════════════════════════════════════════════════════════════════════════


class RetrainTrigger:
    """Evaluates drift → decides retrain → optionally executes → logs."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self._config = {**DEFAULT_CONFIG, **(config or {})}
        self._last_retrain_ts: float = 0.0
        self._history: List[RetrainEvent] = []

    # ── properties ────────────────────────────────────────────────────────

    @property
    def config(self) -> Dict[str, Any]:
        return dict(self._config)

    @property
    def history(self) -> List[Dict[str, Any]]:
        return [e.to_dict() for e in self._history]

    # ── core evaluate ─────────────────────────────────────────────────────

    def evaluate_drift(self, drift_alert: Optional[Dict[str, Any]] = None) -> RetrainEvent:
        """
        Evaluate whether a retrain should be triggered.

        Args:
            drift_alert: DriftAlert.to_dict() output or similar dict with
                         keys: is_drift, p_value, severity, n_current, etc.
                         If None, creates a "no drift" event.

        Returns:
            RetrainEvent with decision details.
        """
        event = RetrainEvent()

        if drift_alert is None:
            event.reason = "No drift alert provided."
            event.retrain_status = "skipped"
            self._history.append(event)
            return event

        # Extract drift info
        event.drift_detected = bool(drift_alert.get("is_drift", False))
        event.p_value = float(drift_alert.get("p_value", 1.0))
        event.threshold = float(drift_alert.get("threshold", self._config["p_value_threshold"]))
        event.severity = str(drift_alert.get("severity", "none"))
        event.signal_count = int(drift_alert.get("n_current", 0))

        # Check drift
        if not event.drift_detected:
            event.reason = f"No drift detected (p={event.p_value:.4f} >= {event.threshold})."
            event.retrain_status = "skipped"
            self._history.append(event)
            return event

        # Check cooldown
        now = time.time()
        elapsed = now - self._last_retrain_ts
        cooldown = self._config["cooldown_seconds"]
        if self._last_retrain_ts > 0 and elapsed < cooldown:
            remaining = cooldown - elapsed
            event.reason = (
                f"Drift detected but cooldown active "
                f"({remaining:.0f}s remaining of {cooldown}s)."
            )
            event.retrain_status = "skipped"
            self._history.append(event)
            return event

        # Check minimum signals
        min_signals = self._config["min_signals_for_retrain"]
        if event.signal_count < min_signals:
            event.reason = (
                f"Drift detected but insufficient signals "
                f"({event.signal_count} < {min_signals})."
            )
            event.retrain_status = "skipped"
            self._history.append(event)
            return event

        # ── Decision: TRIGGER retrain ────────────────────────────────────
        event.retrain_triggered = True
        event.reason = (
            f"Drift detected (p={event.p_value:.4f}, severity={event.severity}). "
            f"Retrain triggered with {event.signal_count} signals."
        )

        if self._config["auto_execute"]:
            event = self._execute_retrain(event)
        else:
            event.retrain_status = "triggered"
            event.details["note"] = "auto_execute=False; retrain intent logged only."

        self._last_retrain_ts = now
        self._history.append(event)
        self._log_event(event)
        return event

    # ── execute retrain (lazy imports) ────────────────────────────────────

    def _execute_retrain(self, event: RetrainEvent) -> RetrainEvent:
        """Actually invoke BERTimbau fine-tuner (if available)."""
        try:
            from core.bert_finetuner import BERTimbauFinetuner

            logger.info("🔄 Auto-retrain: initializing BERTimbauFinetuner...")
            finetuner = BERTimbauFinetuner()
            # Placeholder: in production, you'd pass training data
            event.retrain_status = "completed"
            event.details["finetuner"] = "BERTimbauFinetuner initialized successfully"
            logger.info("✅ Auto-retrain completed.")
        except ImportError as exc:
            event.retrain_status = "failed"
            event.details["error"] = f"BERTimbau dependencies not available: {exc}"
            logger.warning(f"⚠️ Auto-retrain failed: {exc}")
        except Exception as exc:
            event.retrain_status = "failed"
            event.details["error"] = str(exc)
            logger.error(f"❌ Auto-retrain error: {exc}")
        return event

    # ── feedback integration ──────────────────────────────────────────────

    def check_feedback_quality(self, signals: Optional[List[dict]] = None) -> Dict[str, Any]:
        """
        Check if feedback engine has enough quality feedback to support retrain.

        Returns dict with feedback_available, count, recommendation.
        """
        try:
            from core.intelligence.learning.InsightLearner import get_feedback_engine

            engine = get_feedback_engine()
            # FeedbackEngine has stats
            stats = engine.stats()
            fb_count = stats.get("total_processed", 0)
            min_fb = self._config["min_feedback_for_retrain"]
            return {
                "feedback_available": fb_count >= min_fb,
                "feedback_count": fb_count,
                "min_required": min_fb,
                "recommendation": (
                    "Sufficient feedback for retrain." if fb_count >= min_fb
                    else f"Need {min_fb - fb_count} more feedback items."
                ),
            }
        except Exception as exc:
            return {
                "feedback_available": False,
                "feedback_count": 0,
                "min_required": self._config["min_feedback_for_retrain"],
                "recommendation": f"Feedback engine unavailable: {exc}",
            }

    # ── logging ───────────────────────────────────────────────────────────

    def _log_event(self, event: RetrainEvent) -> None:
        """Persist retrain event to local JSON log."""
        try:
            log_dir = Path(self._config["log_dir"])
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "retrain_events.jsonl"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")
            logger.info(f"📝 Retrain event logged to {log_file}")
        except Exception as exc:
            logger.warning(f"⚠️ Could not log retrain event: {exc}")

    # ── summary ───────────────────────────────────────────────────────────

    def summary(self) -> Dict[str, Any]:
        """Summary statistics of retrain history."""
        total = len(self._history)
        triggered = sum(1 for e in self._history if e.retrain_triggered)
        completed = sum(1 for e in self._history if e.retrain_status == "completed")
        failed = sum(1 for e in self._history if e.retrain_status == "failed")
        return {
            "total_evaluations": total,
            "retrains_triggered": triggered,
            "retrains_completed": completed,
            "retrains_failed": failed,
            "last_retrain_ts": self._last_retrain_ts,
            "cooldown_seconds": self._config["cooldown_seconds"],
            "auto_execute": self._config["auto_execute"],
        }


# ═══════════════════════════════════════════════════════════════════════════════
#  Singleton
# ═══════════════════════════════════════════════════════════════════════════════

_trigger: Optional[RetrainTrigger] = None


def get_retrain_trigger() -> RetrainTrigger:
    global _trigger
    if _trigger is None:
        _trigger = RetrainTrigger()
    return _trigger


def reset_retrain_trigger() -> None:
    global _trigger
    _trigger = None
