"""
api/endpoints/risk.py — F-6 + F-7 FASE 3
==========================================
REST API for risk assessment and auto-retrain trigger.

Routes:
  POST /api/v8/risk/assess           — assess risk for a single signal
  POST /api/v8/risk/batch            — batch risk assessment
  POST /api/v8/risk/aggregate        — portfolio-level aggregate risk
  GET  /api/v8/risk/retrain/status   — retrain trigger status/summary
  POST /api/v8/risk/retrain/evaluate — evaluate drift alert for retrain
  GET  /api/v8/risk/retrain/feedback — check feedback quality for retrain
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v8/risk", tags=["Risk Assessment & Retrain (F-6/F-7)"])


# ── Request / Response models ─────────────────────────────────────────

class RiskSignalInput(BaseModel):
    termo: str = Field(..., min_length=1)
    momentum: float = Field(0.0, ge=0, le=100)
    sentiment: float = Field(0.0, ge=-1, le=1)
    volume: int = Field(0, ge=0)
    plataforma: str = "unknown"
    vulnerability: Optional[Dict[str, Any]] = None
    cultural_alerts: Optional[List[Dict[str, Any]]] = None
    pest: Optional[Dict[str, Any]] = None


class RiskBatchInput(BaseModel):
    signals: List[RiskSignalInput] = Field(..., min_length=1, max_length=200)


class DriftAlertInput(BaseModel):
    is_drift: bool = False
    p_value: float = Field(1.0, ge=0, le=1)
    threshold: float = Field(0.05, ge=0, le=1)
    severity: str = "none"
    n_current: int = Field(0, ge=0)
    n_reference: int = Field(0, ge=0)
    feature_stats: Optional[Dict[str, Any]] = None


class GenericResponse(BaseModel):
    status: str
    data: Any


# ── helpers ───────────────────────────────────────────────────────────

def _to_dict(sig: RiskSignalInput) -> dict:
    d = sig.dict()
    return {k: v for k, v in d.items() if v is not None}


# ── Risk Assessment (F-6) ────────────────────────────────────────────

@router.post("/assess", response_model=GenericResponse)
async def risk_assess(sig: RiskSignalInput):
    """Assess risk for a single signal."""
    try:
        from core.engines.risk_engine import get_risk_engine

        result = get_risk_engine().assess_dict(_to_dict(sig))
        return GenericResponse(status="success", data=result)
    except Exception as exc:
        logger.error("POST /risk/assess error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/batch", response_model=GenericResponse)
async def risk_batch(req: RiskBatchInput):
    """Batch risk assessment."""
    try:
        from core.engines.risk_engine import get_risk_engine

        results = get_risk_engine().batch_assess([_to_dict(s) for s in req.signals])
        return GenericResponse(status="success", data={"total": len(results), "results": results})
    except Exception as exc:
        logger.error("POST /risk/batch error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/aggregate", response_model=GenericResponse)
async def risk_aggregate(req: RiskBatchInput):
    """Portfolio-level aggregate risk across multiple signals."""
    try:
        from core.engines.risk_engine import get_risk_engine

        result = get_risk_engine().aggregate_risk([_to_dict(s) for s in req.signals])
        return GenericResponse(status="success", data=result)
    except Exception as exc:
        logger.error("POST /risk/aggregate error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ── Retrain Trigger (F-7) ────────────────────────────────────────────

@router.get("/retrain/status", response_model=GenericResponse)
async def retrain_status():
    """Get retrain trigger summary/status."""
    try:
        from core.classifiers.retrain_trigger import get_retrain_trigger

        return GenericResponse(status="success", data=get_retrain_trigger().summary())
    except Exception as exc:
        logger.error("GET /risk/retrain/status error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/retrain/evaluate", response_model=GenericResponse)
async def retrain_evaluate(alert: DriftAlertInput):
    """Evaluate drift alert and decide if retrain should be triggered."""
    try:
        from core.classifiers.retrain_trigger import get_retrain_trigger

        event = get_retrain_trigger().evaluate_drift(alert.dict())
        return GenericResponse(status="success", data=event.to_dict())
    except Exception as exc:
        logger.error("POST /risk/retrain/evaluate error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/retrain/feedback", response_model=GenericResponse)
async def retrain_feedback_check():
    """Check feedback quality for potential retrain."""
    try:
        from core.classifiers.retrain_trigger import get_retrain_trigger

        result = get_retrain_trigger().check_feedback_quality()
        return GenericResponse(status="success", data=result)
    except Exception as exc:
        logger.error("GET /risk/retrain/feedback error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
