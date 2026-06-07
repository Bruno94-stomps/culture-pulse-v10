"""
api/endpoints/recall.py — F-11 FASE 5
========================================
REST API for Recall Histórico (signal prediction tracking).

Routes:
  POST /api/v8/recall/predict          — register signal as prediction
  POST /api/v8/recall/predict/batch    — register multiple predictions
  POST /api/v8/recall/validate         — validate outcome (became trend?)
  POST /api/v8/recall/validate/batch   — validate multiple outcomes
  GET  /api/v8/recall/metrics          — compute recall metrics
  GET  /api/v8/recall/history          — metrics time series
  GET  /api/v8/recall/predictions      — list predictions + outcomes
  GET  /api/v8/recall/retrain-baseline — get baseline for retrain decisions
  GET  /api/v8/recall/stats            — engine statistics
"""
from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v8/recall", tags=["Recall Histórico"])


# ── Request / Response models ────────────────────────────────────────────

class PredictionRequest(BaseModel):
    signal_id: str = Field(..., description="Unique signal identifier")
    termo: str = Field(..., description="Signal search term")
    circle: str = Field("", description="Cultural circle")
    momentum: float = Field(0.0, ge=0.0, description="Momentum at detection")
    source: str = Field("system", description="Detection source")
    metadata: Optional[dict] = Field(None, description="Additional context")


class BatchPredictionRequest(BaseModel):
    signals: List[PredictionRequest] = Field(..., min_length=1, max_length=500)


class ValidationRequest(BaseModel):
    signal_id: str = Field(..., description="Signal to validate")
    became_trend: bool = Field(..., description="Did it become a trend?")
    validation_source: str = Field("manual", description="How validated")
    trend_evidence: str = Field("", description="Evidence description")
    confidence: float = Field(1.0, ge=0.0, le=1.0)


class BatchValidationRequest(BaseModel):
    outcomes: List[ValidationRequest] = Field(..., min_length=1, max_length=500)


# ── Endpoints ────────────────────────────────────────────────────────────

@router.post("/predict")
async def register_prediction(req: PredictionRequest):
    """Register a signal as a prediction (system detected it as emerging)."""
    try:
        from core.engines.recall_engine import get_recall_engine

        engine = get_recall_engine()
        result = engine.register_prediction(
            signal_id=req.signal_id,
            termo=req.termo,
            circle=req.circle,
            momentum=req.momentum,
            source=req.source,
            metadata=req.metadata or {},
        )
        return {"status": "success", "data": result}

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error("POST /recall/predict error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/predict/batch")
async def register_batch_predictions(req: BatchPredictionRequest):
    """Register multiple signals as predictions."""
    try:
        from core.engines.recall_engine import get_recall_engine

        engine = get_recall_engine()
        signals = [s.model_dump() for s in req.signals]
        result = engine.register_batch(signals)
        return {"status": "success", "data": result}

    except Exception as exc:
        logger.error("POST /recall/predict/batch error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/validate")
async def validate_outcome(req: ValidationRequest):
    """Validate whether a predicted signal became a trend."""
    try:
        from core.engines.recall_engine import get_recall_engine

        engine = get_recall_engine()
        result = engine.validate_outcome(
            signal_id=req.signal_id,
            became_trend=req.became_trend,
            validation_source=req.validation_source,
            trend_evidence=req.trend_evidence,
            confidence=req.confidence,
        )
        return {"status": "success", "data": result}

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error("POST /recall/validate error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/validate/batch")
async def validate_batch_outcomes(req: BatchValidationRequest):
    """Validate multiple outcomes at once."""
    try:
        from core.engines.recall_engine import get_recall_engine

        engine = get_recall_engine()
        outcomes = [o.model_dump() for o in req.outcomes]
        result = engine.validate_batch(outcomes)
        return {"status": "success", "data": result}

    except Exception as exc:
        logger.error("POST /recall/validate/batch error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/metrics")
async def get_recall_metrics(window_days: Optional[int] = None):
    """
    Compute recall metrics: precision, hit rate, F1.

    'X% dos sinais viraram tendência em N dias.'
    """
    try:
        from core.engines.recall_engine import get_recall_engine

        engine = get_recall_engine()
        metrics = engine.compute_metrics(window_days=window_days)
        return {"status": "success", "data": metrics}

    except Exception as exc:
        logger.error("GET /recall/metrics error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/history")
async def get_metrics_history():
    """Return historical metrics for dashboard time series."""
    try:
        from core.engines.recall_engine import get_recall_engine

        engine = get_recall_engine()
        history = engine.get_metrics_history()
        return {
            "status": "success",
            "data": history,
            "metadata": {"count": len(history)},
        }

    except Exception as exc:
        logger.error("GET /recall/history error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/predictions")
async def get_predictions(validated_only: bool = False, limit: int = 50):
    """List predictions with their outcomes."""
    try:
        from core.engines.recall_engine import get_recall_engine

        engine = get_recall_engine()
        preds = engine.get_prediction_list(
            validated_only=validated_only,
            limit=limit,
        )
        return {
            "status": "success",
            "data": preds,
            "metadata": {"count": len(preds)},
        }

    except Exception as exc:
        logger.error("GET /recall/predictions error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/retrain-baseline")
async def get_retrain_baseline():
    """
    Get recall baseline for retrain decisions.

    Used by dashboard to show current model quality
    and by RetrainTrigger to decide if retraining is needed.
    """
    try:
        from core.engines.recall_engine import get_recall_engine

        engine = get_recall_engine()
        baseline = engine.get_retrain_baseline()
        return {"status": "success", "data": baseline}

    except Exception as exc:
        logger.error("GET /recall/retrain-baseline error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/stats")
async def recall_stats():
    """Return recall engine statistics."""
    try:
        from core.engines.recall_engine import get_recall_engine

        engine = get_recall_engine()
        return {"status": "success", "data": engine.stats()}

    except Exception as exc:
        logger.error("GET /recall/stats error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
