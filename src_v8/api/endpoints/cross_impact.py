#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REST Endpoints — Cross-Impact Matrix (F-14)
=============================================
CIM + Causal Chains + Morphological Analysis via REST.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from core.cross_impact import get_cross_impact_engine

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v8/cross-impact",
    tags=["Cross-Impact Matrix"],
)


# ═══════════════════════════════════════════════════════════════════════════════
#  Request Models
# ═══════════════════════════════════════════════════════════════════════════════

class RecordImpactRequest(BaseModel):
    source: str
    target: str
    strength: float = 0.5
    signal_id: str = ""

class BatchRecordRequest(BaseModel):
    impacts: List[RecordImpactRequest]

class PESTResultsRequest(BaseModel):
    pest_results: List[Dict[str, Any]]

class MorphoStatesRequest(BaseModel):
    states: Dict[str, List[str]]


# ═══════════════════════════════════════════════════════════════════════════════
#  Endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/record")
async def record_impact(req: RecordImpactRequest):
    """Record an observed impact between two PEST dimensions."""
    engine = get_cross_impact_engine()
    try:
        result = engine.record_impact(
            source=req.source,
            target=req.target,
            strength=req.strength,
            signal_id=req.signal_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"status": "success", "data": result}


@router.post("/record/batch")
async def batch_record(req: BatchRecordRequest):
    """Record multiple impacts at once."""
    engine = get_cross_impact_engine()
    items = [imp.model_dump() for imp in req.impacts]
    result = engine.batch_record(items)
    return {"status": "success", "data": result}


@router.post("/record/pest-results")
async def record_from_pest(req: PESTResultsRequest):
    """Infer impacts from PEST classification results (primary → secondary)."""
    engine = get_cross_impact_engine()
    result = engine.record_from_pest_results(req.pest_results)
    return {"status": "success", "data": result}


@router.get("/matrix")
async def get_matrix():
    """Get the 4×4 cross-impact matrix."""
    engine = get_cross_impact_engine()
    return {"status": "success", "data": engine.get_matrix()}


@router.get("/strongest")
async def strongest_impacts(
    top_n: int = Query(5, description="Number of top impacts"),
):
    """Get the strongest impact pairs."""
    engine = get_cross_impact_engine()
    return {
        "status": "success",
        "data": {"impacts": engine.get_strongest_impacts(top_n=top_n)},
    }


@router.get("/chains")
async def causal_chains(
    min_strength: float = Query(0.3, description="Minimum strength for chain links"),
):
    """Detect causal chains through PEST dimensions."""
    engine = get_cross_impact_engine()
    return {
        "status": "success",
        "data": {"chains": engine.detect_causal_chains(min_strength=min_strength)},
    }


@router.get("/morphological/states")
async def get_morpho_states():
    """Get current morphological analysis states."""
    engine = get_cross_impact_engine()
    return {"status": "success", "data": engine.get_morphological_states()}


@router.post("/morphological/states")
async def set_morpho_states(req: MorphoStatesRequest):
    """Set custom morphological analysis states."""
    engine = get_cross_impact_engine()
    engine.set_morphological_states(req.states)
    return {
        "status": "success",
        "data": engine.get_morphological_states(),
    }


@router.get("/morphological/scenarios")
async def generate_scenarios(
    max_scenarios: int = Query(10, description="Max scenarios to generate"),
):
    """Generate morphological scenarios from PEST state combinations."""
    engine = get_cross_impact_engine()
    return {
        "status": "success",
        "data": {"scenarios": engine.generate_scenarios(max_scenarios=max_scenarios)},
    }


@router.get("/export")
async def export_data():
    """Export all CIM data."""
    engine = get_cross_impact_engine()
    return {"status": "success", "data": engine.export_data()}


@router.get("/stats")
async def get_stats():
    """Get engine statistics."""
    engine = get_cross_impact_engine()
    return {"status": "success", "data": engine.stats()}
