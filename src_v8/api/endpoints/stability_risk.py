"""
api/endpoints/stability_risk.py — Stability × Nature × Risk Integration
=========================================================================
REST endpoints that expose the three integration paths:
  • Caminho 1 — RiskEngine with 5 factors (including cluster_stability)
  • Caminho 2 — Nature × Stability decision matrix (5×5)
  • Caminho 3 — Combined enrichment context

Endpoints:
  POST /api/v8/stability-risk/assess   — Single signal integrated assessment
  POST /api/v8/stability-risk/portfolio — Batch portfolio assessment
  GET  /api/v8/stability-risk/matrix    — Full 5×5 Nature × Stability matrix
  GET  /api/v8/stability-risk/status    — Current cluster stability status
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v8/stability-risk", tags=["Stability × Risk Integration"])


# ── Request / Response models ────────────────────────────────────────────────

class SignalAssessRequest(BaseModel):
    """Single signal for integrated assessment."""
    termo: str = Field(..., description="Signal term")
    circulo: str = Field(default="geral", description="Cultural circle")
    plataforma: str = Field(default="unknown", description="Source platform")
    texto: str = Field(default="", description="Signal text content")
    sentimento: Optional[float] = Field(default=None, description="Sentiment score -1..1")
    stability_status: Optional[str] = Field(
        default=None,
        description="Override stability status: estável, emergindo, fragmentando, instável, sem_dados"
    )
    signal_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Full signal dict (overrides individual fields)"
    )


class PortfolioRequest(BaseModel):
    """Batch of signals for portfolio risk."""
    signals: List[Dict[str, Any]] = Field(..., description="List of signal dicts")
    stability_status: Optional[str] = Field(
        default=None,
        description="Override stability status for all signals"
    )


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/assess")
async def assess_signal(request: SignalAssessRequest) -> Dict[str, Any]:
    """
    Integrated Stability × Nature × Risk assessment for a single signal.

    Combines:
      - Signal Nature classification (ORGÂNICO / COMERCIAL / etc.)
      - Cluster Stability status (estável / emergindo / etc.)
      - Risk Assessment (5 factors including cluster stability)
      - Decision matrix recommendation
    """
    try:
        from core.classifiers.signal_nature_classifier import SignalNatureClassifier
        from core.engines.risk_engine import get_risk_engine
        from core.clustering.stability import get_stability_analyzer, StabilityStatus

        # Build signal dict
        signal = request.signal_data or {
            "termo": request.termo,
            "circulo": request.circulo,
            "plataforma": request.plataforma,
            "texto": request.texto,
        }
        if request.sentimento is not None:
            signal["sentimento"] = request.sentimento

        # Get stability status
        if request.stability_status:
            stability_status = request.stability_status
        else:
            analyzer = get_stability_analyzer()
            latest = analyzer.latest_comparison()
            stability_status = latest.status.value

        # Inject stability into signal for RiskEngine
        signal["stability_context"] = {"status": stability_status}

        # Nature classification
        classifier = SignalNatureClassifier()
        nature_result = classifier.classify(
            termo=signal.get("termo", ""),
            mencoes=[signal.get("texto", "")],
            contextos=[signal.get("circulo", "geral")],
            plataformas=[signal.get("plataforma", "unknown")],
            tensoes=[],
            demografico={},
            velocity=0.0,
            volume=0,
            sentiment=request.sentimento or 0.5,
        )

        # Matrix recommendation (Caminho 2)
        recommendation = classifier.get_stability_recommendation(
            nature_result, stability_status, bot_risk_level="LOW"
        )

        # Risk assessment with 5 factors (Caminho 1)
        signal["signal_nature"] = {
            "categoria": nature_result.categoria,
            "confianca": nature_result.confianca,
            "score_organico": nature_result.score_organico,
            "score_comercial": nature_result.score_comercial,
            "score_apropriacao": nature_result.score_apropriacao,
        }
        risk_engine = get_risk_engine()
        risk_result = risk_engine.assess_dict(signal)

        return {
            "status": "success",
            "data": {
                "nature": {
                    "categoria": nature_result.categoria,
                    "confianca": round(nature_result.confianca, 3),
                    "score_organico": nature_result.score_organico,
                    "score_comercial": nature_result.score_comercial,
                    "score_apropriacao": nature_result.score_apropriacao,
                    "evidencias": nature_result.evidencias[:5],
                    "flags": nature_result.flags[:5],
                },
                "stability": {
                    "status": stability_status,
                },
                "recommendation": recommendation,
                "risk": risk_result,
            },
            "metadata": {
                "integration": "Stability × Nature × Risk (Caminhos 1+2+3)",
                "risk_factors_count": 5,
                "matrix_size": "5×5",
            },
        }

    except Exception as e:
        logger.error(f"stability-risk assess error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/portfolio")
async def assess_portfolio(request: PortfolioRequest) -> Dict[str, Any]:
    """
    Portfolio-level risk assessment with stability context.
    Aggregates risk across multiple signals including cluster stability.
    """
    try:
        from core.engines.risk_engine import get_risk_engine
        from core.clustering import get_stability_analyzer

        if request.stability_status:
            stability_status = request.stability_status
        else:
            analyzer = get_stability_analyzer()
            latest = analyzer.latest_comparison()
            stability_status = latest.status.value

        # Inject stability context into all signals
        for sig in request.signals:
            if "stability_context" not in sig:
                sig["stability_context"] = {"status": stability_status}

        risk_engine = get_risk_engine()
        portfolio = risk_engine.aggregate_risk(request.signals)
        individual = risk_engine.batch_assess(request.signals)

        return {
            "status": "success",
            "data": {
                "portfolio": portfolio,
                "individual_assessments": individual,
                "stability_status": stability_status,
            },
            "metadata": {
                "signal_count": len(request.signals),
                "integration": "Portfolio + Stability (Caminho 1)",
            },
        }

    except Exception as e:
        logger.error(f"stability-risk portfolio error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/matrix")
async def get_decision_matrix() -> Dict[str, Any]:
    """
    Return the full 5×5 Nature × Stability decision matrix (Caminho 2).
    Used by dashboard to render the heatmap/table.
    """
    try:
        from core.classifiers.signal_nature_classifier import SignalNatureClassifier

        matrix = SignalNatureClassifier.get_stability_matrix_full()

        return {
            "status": "success",
            "data": {
                "matrix": matrix,
                "natures": ["ORGÂNICO", "RESONÂNCIA", "COMERCIAL", "SIMULAÇÃO", "APROPRIAÇÃO"],
                "stabilities": ["estável", "emergindo", "fragmentando", "instável", "sem_dados"],
            },
            "metadata": {
                "total_cells": len(matrix),
                "dimensions": "5×5 (Nature × Stability)",
            },
        }

    except Exception as e:
        logger.error(f"stability-risk matrix error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_stability_status() -> Dict[str, Any]:
    """
    Return current cluster stability status from the singleton analyzer.
    """
    try:
        from core.clustering import get_stability_analyzer

        analyzer = get_stability_analyzer()
        latest = analyzer.latest_comparison()

        return {
            "status": "success",
            "data": {
                "stability_status": latest.status.value,
                "badge": latest.badge_emoji,
                "description": latest.badge_description,
                "ari_score": latest.ari_score,
                "nmi_score": latest.nmi_score,
                "n_clusters_prev": latest.n_clusters_prev,
                "n_clusters_curr": latest.n_clusters_curr,
                "new_clusters": latest.new_clusters,
                "lost_clusters": latest.lost_clusters,
                "snapshot_count": analyzer.snapshot_count,
                "history": analyzer.history(),
            },
        }

    except Exception as e:
        logger.error(f"stability-risk status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
