"""
api/endpoints/topics.py — INT-2 FASE 2
========================================
API endpoints for topic modelling.

Routes:
  GET  /api/v8/topics          — current topic hierarchy
  GET  /api/v8/topics/stats    — topic engine stats
"""
from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v8/topics", tags=["Topic Modelling"])


# ── Response models ──────────────────────────────────────────────────────

class TopicItem(BaseModel):
    topic_id: int
    label: str
    top_terms: List[str]
    top_weights: List[float]
    n_documents: int


class TopicHierarchyResponse(BaseModel):
    status: str
    n_topics: int
    topics: List[TopicItem]


class TopicStatsResponse(BaseModel):
    total_documents: int
    model_fitted: bool
    fitted_at: Optional[str]
    n_topics: int
    sklearn_available: bool


# ── Endpoints ────────────────────────────────────────────────────────────

@router.get("", response_model=TopicHierarchyResponse)
async def topic_hierarchy():
    """
    Return the current topic hierarchy.

    Returns the list of macro-topics discovered by the
    incremental LDA engine, with top terms and weights.
    """
    try:
        from core.intelligence.topic_engine import get_topic_engine

        engine = get_topic_engine()
        hierarchy = engine.get_hierarchy()
        topics = [
            TopicItem(
                topic_id=t["topic_id"],
                label=t["label"],
                top_terms=t["top_terms"],
                top_weights=t["top_weights"],
                n_documents=t["n_documents"],
            )
            for t in hierarchy.get("topics", [])
        ]
        return TopicHierarchyResponse(
            status="ok",
            n_topics=len(topics),
            topics=topics,
        )

    except Exception as exc:
        logger.error("GET /topics error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/stats", response_model=TopicStatsResponse)
async def topic_stats():
    """Return topic engine statistics."""
    try:
        from core.intelligence.topic_engine import get_topic_engine

        engine = get_topic_engine()
        stats = engine.get_stats()
        return TopicStatsResponse(
            total_documents=stats["buffer_size"],
            model_fitted=stats["is_fitted"],
            fitted_at=stats.get("fitted_at"),
            n_topics=stats["n_topics"],
            sklearn_available=stats["sklearn_available"],
        )

    except Exception as exc:
        logger.error("GET /topics/stats error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
