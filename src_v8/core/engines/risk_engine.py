"""
core/risk_engine.py — F-6 FASE 3
==================================
Risk Assessment Framework that combines:
  • VulnerabilityEngine (H-9) — vulnerability score & dimensions
  • CulturalAlertsEngine (H-9) — alert count & severity
  • PESTEngine (F-5)           — macro-environment sensitivity
into a unified risk profile per signal.

Risk levels:
  1 (negligible) — 2 (low) — 3 (moderate) — 4 (high) — 5 (critical)

Outputs:
  RiskAssessment — overall risk score, risk level, breakdown, mitigation actions
"""

import logging
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from core.clustering import StabilityStatus

logger = logging.getLogger(__name__)


# ── StabilityStatus → risk score mapping ─────────────────────────────────────
STABILITY_RISK_MAP: Dict[str, float] = {
    StabilityStatus.ESTAVEL.value: 0.0,        # 🟢 Clusters stable — no added risk
    StabilityStatus.EMERGINDO.value: 25.0,      # 🔵 New clusters appearing — moderate uncertainty
    StabilityStatus.FRAGMENTANDO.value: 55.0,   # 🟡 Clusters dissolving — high risk
    StabilityStatus.INSTAVEL.value: 85.0,       # 🔴 ARI < 0.40 — critical instability
    StabilityStatus.SEM_DADOS.value: 40.0,      # ⚪ No data — conservative uncertainty penalty
}


# ═══════════════════════════════════════════════════════════════════════════════
#  Data classes
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class RiskFactor:
    """Individual risk factor."""

    name: str
    score: float          # 0-100
    weight: float         # 0-1
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RiskAssessment:
    """Complete risk assessment for one signal."""

    overall_score: float              # 0-100
    risk_level: int                   # 1-5
    risk_label: str                   # negligible / low / moderate / high / critical
    factors: List[RiskFactor] = field(default_factory=list)
    alert_summary: Dict[str, int] = field(default_factory=dict)  # severity → count
    mitigation_actions: List[str] = field(default_factory=list)
    confidence: float = 0.0           # 0-1 confidence in assessment

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_score": round(self.overall_score, 2),
            "risk_level": self.risk_level,
            "risk_label": self.risk_label,
            "factors": [f.to_dict() for f in self.factors],
            "alert_summary": self.alert_summary,
            "mitigation_actions": self.mitigation_actions,
            "confidence": round(self.confidence, 3),
        }


# ═══════════════════════════════════════════════════════════════════════════════
#  Weights & thresholds
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT_WEIGHTS = {
    "vulnerability": 0.30,
    "alert_severity": 0.20,
    "pest_exposure": 0.15,
    "sentiment_risk": 0.15,
    "cluster_stability": 0.20,
}

LEVEL_THRESHOLDS = [
    (20, 1, "negligible"),
    (40, 2, "low"),
    (60, 3, "moderate"),
    (80, 4, "high"),
    (101, 5, "critical"),
]

MITIGATION_MAP = {
    1: ["Continue monitoring — no immediate action needed."],
    2: ["Increase monitoring cadence.", "Review cultural positioning."],
    3: [
        "Activate alert monitoring dashboard.",
        "Prepare contingency content plan.",
        "Brief brand team on potential cultural shifts.",
    ],
    4: [
        "Convene crisis response team.",
        "Pause scheduled cultural campaigns.",
        "Engage community management for sentiment repair.",
        "Draft public positioning statement.",
    ],
    5: [
        "IMMEDIATE: Escalate to C-level.",
        "Pause ALL cultural campaigns.",
        "Activate full crisis communications protocol.",
        "Deploy real-time sentiment monitoring.",
        "Prepare media response strategy.",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
#  RiskEngine
# ═══════════════════════════════════════════════════════════════════════════════


class RiskEngine:
    """Unified risk assessment combining vulnerability, alerts, and PEST."""

    def __init__(self, weights: Optional[Dict[str, float]] = None) -> None:
        self._weights = weights or dict(DEFAULT_WEIGHTS)

    # ── helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def _vulnerability_score(signal: dict) -> float:
        """Extract vulnerability score (0-100) from signal or compute inline."""
        vuln = signal.get("vulnerability")
        if isinstance(vuln, dict):
            return float(vuln.get("score", 0))
        # Compute inline if not yet enriched
        try:
            from core.engines.vulnerability_engine import get_vulnerability_engine

            result = get_vulnerability_engine().assess_signal(signal)
            return float(result.get("score", 0))
        except Exception:
            return 0.0

    @staticmethod
    def _alert_severity_score(signal: dict) -> float:
        """Score based on cultural alerts severity (0-100)."""
        alerts = signal.get("cultural_alerts")
        if not isinstance(alerts, list):
            try:
                from alerts.cultural_alerts_engine import get_alerts_engine

                alerts = get_alerts_engine().evaluate_dict(signal)
            except Exception:
                return 0.0

        if not alerts:
            return 0.0

        severity_scores = {"info": 10, "warning": 40, "critical": 80}
        total = sum(severity_scores.get(a.get("severity", "info"), 10) for a in alerts)
        # Normalize: cap at 100
        return min(total, 100.0)

    @staticmethod
    def _pest_exposure_score(signal: dict) -> float:
        """Score based on PEST sensitivity (0-100)."""
        pest = signal.get("pest")
        if isinstance(pest, dict):
            conf = float(pest.get("confidence", 0))
            # Higher confidence in Political/Economic → higher risk
            primary = pest.get("primary", "Social")
            risk_multiplier = {"Political": 1.5, "Economic": 1.3, "Social": 0.8, "Technological": 1.0}
            return min(conf * 100 * risk_multiplier.get(primary, 1.0), 100.0)
        return 0.0

    @staticmethod
    def _sentiment_risk_score(signal: dict) -> float:
        """Negative sentiment → higher risk (0-100)."""
        raw = signal.get("sentimento") or signal.get("sentiment")
        if isinstance(raw, dict):
            val = raw.get("compound", raw.get("score", 0))
        elif raw is not None:
            try:
                val = float(raw)
            except (TypeError, ValueError):
                val = 0
        else:
            val = 0
        # sentiment ranges -1 to 1; negative = risk
        risk = max(0.0, -val) * 100  # -0.5 → 50
        return min(risk, 100.0)

    @staticmethod
    def _stability_risk_score(signal: dict) -> float:
        """Cluster instability → higher risk (0-100).

        Reads from signal['stability_context']['status'] (set by Worker
        enricher) or signal['cluster_stability'] if injected directly.
        Falls back to SEM_DADOS (conservative 40) when absent.
        """
        # Try stability_context (set by Worker pipeline — Caminho 3)
        ctx = signal.get("stability_context")
        if isinstance(ctx, dict):
            status_str = ctx.get("status", StabilityStatus.SEM_DADOS.value)
            return STABILITY_RISK_MAP.get(status_str, 40.0)

        # Try direct cluster_stability field
        cs = signal.get("cluster_stability")
        if isinstance(cs, dict):
            status_str = cs.get("status", StabilityStatus.SEM_DADOS.value)
            return STABILITY_RISK_MAP.get(status_str, 40.0)

        # No stability data — conservative penalty
        return STABILITY_RISK_MAP[StabilityStatus.SEM_DADOS.value]

    # ── main assess ──────────────────────────────────────────────────────

    def assess(self, signal: dict) -> RiskAssessment:
        """Full risk assessment for a single signal."""
        factors: List[RiskFactor] = []

        v_score = self._vulnerability_score(signal)
        factors.append(RiskFactor("vulnerability", v_score, self._weights["vulnerability"],
                                  "Cultural vulnerability exposure"))

        a_score = self._alert_severity_score(signal)
        factors.append(RiskFactor("alert_severity", a_score, self._weights["alert_severity"],
                                  "Severity of cultural alerts"))

        p_score = self._pest_exposure_score(signal)
        factors.append(RiskFactor("pest_exposure", p_score, self._weights["pest_exposure"],
                                  "Macro-environment (PEST) exposure"))

        s_score = self._sentiment_risk_score(signal)
        factors.append(RiskFactor("sentiment_risk", s_score, self._weights["sentiment_risk"],
                                  "Negative sentiment risk"))

        cs_score = self._stability_risk_score(signal)
        factors.append(RiskFactor("cluster_stability", cs_score,
                                  self._weights.get("cluster_stability", 0.20),
                                  "Cluster instability risk (F-2)"))

        # Weighted overall
        overall = sum(f.score * f.weight for f in factors)
        overall = min(max(overall, 0), 100)

        # Level
        risk_level, risk_label = 1, "negligible"
        for threshold, level, label in LEVEL_THRESHOLDS:
            if overall < threshold:
                risk_level, risk_label = level, label
                break

        # Alert summary
        alerts = signal.get("cultural_alerts") or []
        alert_summary: Dict[str, int] = {}
        for a in alerts:
            sev = a.get("severity", "info") if isinstance(a, dict) else "info"
            alert_summary[sev] = alert_summary.get(sev, 0) + 1

        # Confidence: higher when more data is available
        data_coverage = sum([
            1 if signal.get("vulnerability") else 0,
            1 if signal.get("cultural_alerts") else 0,
            1 if signal.get("pest") else 0,
            1 if (signal.get("sentimento") or signal.get("sentiment")) else 0,
            1 if (signal.get("stability_context") or signal.get("cluster_stability")) else 0,
        ])
        confidence = data_coverage / 5.0

        return RiskAssessment(
            overall_score=overall,
            risk_level=risk_level,
            risk_label=risk_label,
            factors=factors,
            alert_summary=alert_summary,
            mitigation_actions=MITIGATION_MAP.get(risk_level, []),
            confidence=confidence,
        )

    def assess_dict(self, signal: dict) -> Dict[str, Any]:
        return self.assess(signal).to_dict()

    def batch_assess(self, signals: List[dict]) -> List[Dict[str, Any]]:
        return [self.assess_dict(s) for s in signals]

    def aggregate_risk(self, signals: List[dict]) -> Dict[str, Any]:
        """Portfolio-level risk: aggregate risk across multiple signals."""
        if not signals:
            return {"overall_score": 0, "risk_level": 1, "risk_label": "negligible",
                    "signal_count": 0, "level_distribution": {}}

        assessments = [self.assess(s) for s in signals]
        avg_score = sum(a.overall_score for a in assessments) / len(assessments)
        max_score = max(a.overall_score for a in assessments)

        # Portfolio risk: weighted avg (70%) + max (30%) — punishes outliers
        portfolio_score = 0.7 * avg_score + 0.3 * max_score

        risk_level, risk_label = 1, "negligible"
        for threshold, level, label in LEVEL_THRESHOLDS:
            if portfolio_score < threshold:
                risk_level, risk_label = level, label
                break

        dist: Dict[str, int] = {}
        for a in assessments:
            dist[a.risk_label] = dist.get(a.risk_label, 0) + 1

        return {
            "overall_score": round(portfolio_score, 2),
            "risk_level": risk_level,
            "risk_label": risk_label,
            "signal_count": len(signals),
            "average_score": round(avg_score, 2),
            "max_score": round(max_score, 2),
            "level_distribution": dist,
            "mitigation_actions": MITIGATION_MAP.get(risk_level, []),
        }


# ═══════════════════════════════════════════════════════════════════════════════
#  Singleton
# ═══════════════════════════════════════════════════════════════════════════════

_engine: Optional[RiskEngine] = None


def get_risk_engine() -> RiskEngine:
    global _engine
    if _engine is None:
        _engine = RiskEngine()
    return _engine


def reset_risk_engine() -> None:
    global _engine
    _engine = None
