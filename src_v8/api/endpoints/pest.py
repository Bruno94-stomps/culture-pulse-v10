"""
api/endpoints/pest.py — F-5 FASE 2
====================================
API endpoints for PEST classification of cultural signals.

Routes:
  GET  /api/v8/pest/stats         — engine statistics
  POST /api/v8/pest/classify      — classify free text
  POST /api/v8/pest/batch         — classify multiple texts
"""
from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v8/pest", tags=["PEST Classification"])


# ── Request / Response models ────────────────────────────────────────────

class PESTClassifyRequest(BaseModel):
    """Classify a single text."""
    text: str = Field(..., min_length=1, description="Text to classify")


class PESTBatchRequest(BaseModel):
    """Classify multiple texts."""
    texts: List[str] = Field(..., min_items=1, max_items=100, description="Texts to classify")


class PESTClassifyResponse(BaseModel):
    status: str
    primary: str
    secondary: Optional[str]
    confidence: float
    scores: dict
    keywords_matched: List[str]


class PESTStatsResponse(BaseModel):
    engine: str
    version: str
    categories: List[str]
    keywords_per_category: dict
    total_keywords: int


class PESTBatchResponse(BaseModel):
    status: str
    total: int
    results: List[dict]
    distribution: dict


# ── Endpoints ────────────────────────────────────────────────────────────

@router.get("/stats", response_model=PESTStatsResponse)
async def pest_stats():
    """Return PEST engine statistics."""
    try:
        from core.engines.pest_engine import get_pest_engine

        engine = get_pest_engine()
        return PESTStatsResponse(**engine.get_stats())

    except Exception as exc:
        logger.error("GET /pest/stats error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/classify", response_model=PESTClassifyResponse)
async def classify_text(req: PESTClassifyRequest):
    """Classify a text into PEST dimensions."""
    try:
        from core.engines.pest_engine import get_pest_engine

        engine = get_pest_engine()
        result = engine.classify(req.text)
        return PESTClassifyResponse(
            status="success",
            primary=result.primary,
            secondary=result.secondary,
            confidence=result.confidence,
            scores=result.scores,
            keywords_matched=result.keywords_matched,
        )

    except Exception as exc:
        logger.error("POST /pest/classify error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/batch", response_model=PESTBatchResponse)
async def batch_classify(req: PESTBatchRequest):
    """Classify multiple texts into PEST dimensions."""
    try:
        from core.engines.pest_engine import get_pest_engine

        engine = get_pest_engine()
        results = engine.batch_classify(req.texts)
        dist = engine.get_distribution(results)

        return PESTBatchResponse(
            status="success",
            total=len(results),
            results=[r.to_dict() for r in results],
            distribution=dist,
        )

    except Exception as exc:
        logger.error("POST /pest/batch error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
