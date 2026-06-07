#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REST Endpoints — Industry Weights (F-13)
==========================================
CRUD + learning para pesos de relevância por indústria/círculo cultural.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from core.engines.industry_weights import (
    CIRCULOS,
    INDUSTRIES,
    get_industry_weights_engine,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v8/industry",
    tags=["Industry Weights"],
)


# ═══════════════════════════════════════════════════════════════════════════════
#  Request / Response Models
# ═══════════════════════════════════════════════════════════════════════════════

class WeightFeedbackRequest(BaseModel):
    industry: str
    circle: str
    useful: bool
    signal_id: str = ""

class BatchFeedbackRequest(BaseModel):
    feedbacks: List[WeightFeedbackRequest]

class ApplyWeightRequest(BaseModel):
    industry: str
    circle: str
    base_momentum: float

class RankSignalsRequest(BaseModel):
    industry: str
    signals: List[Dict[str, Any]]
    use_learned: bool = True

class ABTestRequest(BaseModel):
    industry: str
    signals: List[Dict[str, Any]]
    ground_truth: Dict[str, bool]


# ═══════════════════════════════════════════════════════════════════════════════
#  Endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/industries")
async def list_industries():
    """List all supported industries."""
    engine = get_industry_weights_engine()
    return {
        "status": "success",
        "data": {
            "industries": engine.industries,
            "circles": engine.circles,
            "total_industries": len(engine.industries),
            "total_circles": len(engine.circles),
        },
    }


@router.get("/weights/{industry}")
async def get_weights(
    industry: str,
    use_learned: bool = Query(True, description="Use learned weights if available"),
):
    """Get circle weights for a specific industry."""
    engine = get_industry_weights_engine()
    try:
        weights = engine.get_weights(industry, use_learned=use_learned)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "status": "success",
        "data": {
            "industry": industry,
            "weights": weights,
            "use_learned": use_learned,
        },
    }


@router.get("/weights")
async def get_all_weights(
    use_learned: bool = Query(True, description="Use learned weights if available"),
):
    """Get weights for all industries."""
    engine = get_industry_weights_engine()
    return {
        "status": "success",
        "data": engine.get_all_weights(use_learned=use_learned),
    }


@router.post("/feedback")
async def submit_feedback(req: WeightFeedbackRequest):
    """Submit feedback on a signal's usefulness for an industry."""
    engine = get_industry_weights_engine()
    try:
        result = engine.submit_feedback(
            industry=req.industry,
            circle=req.circle,
            useful=req.useful,
            signal_id=req.signal_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {"status": "success", "data": result}


@router.post("/feedback/batch")
async def submit_batch_feedback(req: BatchFeedbackRequest):
    """Submit multiple feedbacks at once."""
    engine = get_industry_weights_engine()
    items = [fb.model_dump() for fb in req.feedbacks]
    result = engine.batch_feedback(items)
    return {"status": "success", "data": result}


@router.post("/apply")
async def apply_weight(req: ApplyWeightRequest):
    """Apply industry weight to a base momentum."""
    engine = get_industry_weights_engine()
    try:
        result = engine.apply_industry_weight(
            industry=req.industry,
            circle=req.circle,
            base_momentum=req.base_momentum,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {"status": "success", "data": result}


@router.post("/rank")
async def rank_signals(req: RankSignalsRequest):
    """Rank signals by relevance for a specific industry."""
    engine = get_industry_weights_engine()
    try:
        ranked = engine.rank_signals_for_industry(
            industry=req.industry,
            signals=req.signals,
            use_learned=req.use_learned,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {"status": "success", "data": {"ranked_signals": ranked}}


@router.post("/ab-test")
async def run_ab_test(req: ABTestRequest):
    """Run A/B test comparing default vs learned weights."""
    engine = get_industry_weights_engine()
    try:
        result = engine.run_ab_test(
            industry=req.industry,
            signals=req.signals,
            ground_truth=req.ground_truth,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {"status": "success", "data": result}


@router.get("/ab-test/history")
async def ab_test_history():
    """Get A/B test history."""
    engine = get_industry_weights_engine()
    return {
        "status": "success",
        "data": {"tests": engine.get_ab_history()},
    }


@router.get("/export")
async def export_weights():
    """Export all weights (default + learned)."""
    engine = get_industry_weights_engine()
    return {"status": "success", "data": engine.export_weights()}


@router.get("/stats")
async def get_stats():
    """Get engine statistics."""
    engine = get_industry_weights_engine()
    return {"status": "success", "data": engine.stats()}
