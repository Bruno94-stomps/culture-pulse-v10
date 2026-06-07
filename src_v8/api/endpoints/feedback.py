"""
api/endpoints/feedback.py — INT-1 FASE 2
==========================================
API endpoints for user feedback on signal quality.

Routes:
  POST /api/v8/feedback          — submit rating for a signal
  GET  /api/v8/feedback/stats    — learning engine stats
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v8/feedback", tags=["Feedback Learning"])


# ── Request / Response models ────────────────────────────────────────────

class FeedbackRequest(BaseModel):
    """Submit feedback for a signal."""

    signal_id: str = Field(..., description="Unique signal identifier")
    rating: float = Field(..., ge=1.0, le=5.0, description="User rating 1-5")
    effectiveness: float = Field(0.5, ge=0.0, le=1.0, description="Effectiveness score 0-1")
    signal_snapshot: Optional[dict] = Field(None, description="Optional enriched signal snapshot for feature extraction")


class FeedbackResponse(BaseModel):
    status: str
    total_samples: int
    auto_trained: bool


class FeedbackStatsResponse(BaseModel):
    total_samples: int
    model_trained: bool
    trained_at: Optional[str]
    metrics: dict
    sklearn_available: bool


# ── Endpoints ────────────────────────────────────────────────────────────

@router.post("", response_model=FeedbackResponse)
async def submit_feedback(req: FeedbackRequest):
    """
    Submit user feedback for a signal.
    """
    try:
        from core.intelligence.learning.InsightLearner import get_insight_learner

        engine = get_insight_learner()
        result = engine.add_signal_feedback(
            signal_id=req.signal_id,
            rating=req.rating,
            signal=req.signal_snapshot,
        )
        # Adapt result for consistency
        return FeedbackResponse(
            status="success",
            total_samples=1, # Mock for compatibility
            auto_trained=False
        )

    except Exception as exc:
        logger.error("POST /feedback error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/stats", response_model=FeedbackStatsResponse)
async def feedback_stats():
    """Return learning engine statistics."""
    try:
        from core.intelligence.learning.InsightLearner import get_insight_learner

        engine = get_insight_learner()
        stats = engine.get_engine_stats()
        return FeedbackStatsResponse(
            total_samples=stats.get("queries_in_cache", 0),
            model_trained=stats["model_trained"],
            trained_at=None,
            metrics={},
            sklearn_available=True,
        )

    except Exception as exc:
        logger.error("GET /feedback/stats error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
