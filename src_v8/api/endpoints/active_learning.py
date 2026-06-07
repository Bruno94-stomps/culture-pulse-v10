"""
api/endpoints/active_learning.py — F-10 FASE 5
=================================================
REST API for Active Learning (human-in-the-loop query refinement).

Routes:
  POST /api/v8/active-learning/feedback      — submit relevance feedback
  POST /api/v8/active-learning/feedback/batch — submit multiple feedbacks
  GET  /api/v8/active-learning/rankings       — get query rankings
  GET  /api/v8/active-learning/uncertain      — get queries needing review
  POST /api/v8/active-learning/prioritize     — re-rank queries for collection
  POST /api/v8/active-learning/import-tracker — import from QueryTracker
  GET  /api/v8/active-learning/stats          — engine statistics
"""
from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v8/active-learning", tags=["Active Learning"])


# ── Request / Response models ────────────────────────────────────────────

class FeedbackRequest(BaseModel):
    """Submit relevance feedback for a query."""
    query: str = Field(..., description="Search query/term to evaluate")
    relevant: bool = Field(..., description="True if query produces relevant results")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Analyst confidence 0-1")
    source: str = Field("analyst", description="Feedback source: analyst, auto, system")
    notes: str = Field("", description="Optional notes")


class BatchFeedbackRequest(BaseModel):
    """Submit multiple feedbacks at once."""
    feedbacks: List[FeedbackRequest] = Field(..., min_length=1, max_length=100)


class PrioritizeRequest(BaseModel):
    """Re-rank queries for next collection cycle."""
    queries: List[str] = Field(..., min_length=1, max_length=500)


class ImportTrackerRequest(BaseModel):
    """Import query history from QueryTracker."""
    limit: int = Field(100, ge=1, le=1000, description="Max entries to import")
    plan: Optional[str] = Field(None, description="Filter by plan tier")


# ── Endpoints ────────────────────────────────────────────────────────────

@router.post("/feedback")
async def submit_feedback(req: FeedbackRequest):
    """
    Submit relevance feedback for a search query.

    The analyst rates a query as relevant or irrelevant.
    The engine updates the query's ranking using Wilson lower bound
    and identifies queries needing further review.
    """
    try:
        from core.intelligence.learning.InsightLearner import get_insight_learner

        engine = get_insight_learner()
        result = engine.submit_query_feedback(
            query=req.query,
            relevant=req.relevant,
            confidence=req.confidence,
            notes=req.notes,
        )
        return {"status": "success", "data": result}

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error("POST /active-learning/feedback error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/feedback/batch")
async def submit_batch_feedback(req: BatchFeedbackRequest):
    """Submit multiple relevance feedbacks at once."""
    try:
        from core.intelligence.learning.InsightLearner import get_insight_learner

        engine = get_insight_learner()
        feedbacks = [fb.model_dump() for fb in req.feedbacks]
        result = engine.submit_batch_feedback(feedbacks)
        return {"status": "success", "data": result}

    except Exception as exc:
        logger.error("POST /active-learning/feedback/batch error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/rankings")
async def get_rankings(
    top_k: int = 50,
):
    """
    Get query rankings sorted by relevance.
    """
    try:
        from core.intelligence.learning.InsightLearner import get_insight_learner

        engine = get_insight_learner()
        rankings = engine.get_query_rankings(
            limit=top_k,
        )
        return {
            "status": "success",
            "data": rankings,
            "metadata": {"count": len(rankings)},
        }

    except Exception as exc:
        logger.error("GET /active-learning/rankings error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/uncertain")
async def get_uncertain_queries(top_k: int = 10):
    """
    Get queries that need human review (uncertainty sampling).
    """
    try:
        from core.intelligence.learning.InsightLearner import get_insight_learner

        engine = get_insight_learner()
        uncertain = engine.get_uncertain_queries(top_k=top_k)
        return {
            "status": "success",
            "data": uncertain,
            "metadata": {"count": len(uncertain)},
        }

    except Exception as exc:
        logger.error("GET /active-learning/uncertain error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/prioritize")
async def prioritize_queries(req: PrioritizeRequest):
    """
    Re-rank a list of queries for the next data collection cycle.
    """
    try:
        from core.intelligence.learning.InsightLearner import get_insight_learner

        engine = get_insight_learner()
        result = engine.prioritize_queries(req.queries)
        return {
            "status": "success",
            "data": result,
        }

    except Exception as exc:
        logger.error("POST /active-learning/prioritize error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/import-tracker")
async def import_from_tracker(req: ImportTrackerRequest):
    """
    Import query history from QueryTracker (F-1) as auto-feedback.

    Queries that produced signals are marked as relevant;
    queries with no results are marked as irrelevant.
    """
    try:
        from core.intelligence.learning.InsightLearner import get_active_learning_engine
        from core.models.query_tracker import get_tracker

        tracker = get_tracker()
        history = tracker.get_history(
            limit=req.limit,
            plan=req.plan,
        )

        engine = get_active_learning_engine()
        result = engine.import_from_tracker(history)
        return {"status": "success", "data": result}

    except Exception as exc:
        logger.error("POST /active-learning/import-tracker error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/stats")
async def active_learning_stats():
    """Return active learning engine statistics."""
    try:
        from core.intelligence.learning.InsightLearner import get_insight_learner

        engine = get_insight_learner()
        return {"status": "success", "data": engine.get_engine_stats()}

    except Exception as exc:
        logger.error("GET /active-learning/stats error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
