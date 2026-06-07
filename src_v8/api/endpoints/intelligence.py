"""
api/endpoints/intelligence.py — H-9 FASE 3
============================================
Unified REST API for the 5 cultural-intelligence engines:

  GET  /api/v8/intelligence/vulnerability   — assess vulnerability of a signal
  POST /api/v8/intelligence/vulnerability/batch — batch assess
  GET  /api/v8/intelligence/alerts          — evaluate cultural alerts
  POST /api/v8/intelligence/alerts/batch    — batch evaluate
  GET  /api/v8/intelligence/actions         — recommend strategic action
  POST /api/v8/intelligence/actions/batch   — batch recommend
  GET  /api/v8/intelligence/scenarios       — generate future scenarios
  POST /api/v8/intelligence/scenarios/batch — batch generate
  GET  /api/v8/intelligence/opportunities   — detect opportunities
  POST /api/v8/intelligence/opportunities/batch — batch detect
  GET  /api/v8/intelligence/full            — full analysis pipeline (all 5)
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v8/intelligence", tags=["Cultural Intelligence (H-9)"])


# ── Shared request / response models ─────────────────────────────────

class SignalInput(BaseModel):
    """Minimal signal representation accepted by all engines.

    momentum aceita tanto escala 0-1 (frontend/Supabase) quanto 0-100 (pipeline interno).
    A normalização para 0-100 é feita em _to_dict() antes de chamar os engines.
    """
    termo: str = Field(..., min_length=1, description="Search term / topic")
    momentum: float = Field(0.0, ge=0, le=100, description="Momentum score 0-100 (or 0-1, auto-normalized)")
    sentiment: float = Field(0.0, ge=-1, le=1, description="Sentiment -1 to 1")
    volume: int = Field(0, ge=0, description="Volume of mentions")
    plataforma: str = Field("unknown", description="Source platform")
    relevancia_cultural: float = Field(0.0, ge=0, le=1, description="Cultural relevance 0-1")
    # Optional enriched fields (if available from prior pipeline stages)
    tensions: Optional[List[Dict[str, Any]]] = None
    circles: Optional[List[str]] = None
    pest: Optional[Dict[str, Any]] = None
    velocity: Optional[Dict[str, Any]] = None

    class Config:
        # Allow momentum values in 0-1 range even though field says le=100
        # (Pydantic v1 coercion is fine; validation happens after _to_dict normalises)
        extra = "allow"


class BatchSignalInput(BaseModel):
    """Multiple signals for batch endpoints."""
    signals: List[SignalInput] = Field(..., min_length=1, max_length=200)


class GenericResponse(BaseModel):
    status: str
    data: Any


# ── helpers ───────────────────────────────────────────────────────────

def _to_dict(sig: SignalInput) -> dict:
    d = sig.dict()
    # flatten optionals — remove None values so engines see clean dicts
    d = {k: v for k, v in d.items() if v is not None}

    # Normalise momentum: frontend/Supabase sends 0-1, engines expect 0-100.
    # If value is in [0, 1] range (and not obviously already 0-100), scale it up.
    momentum = d.get("momentum", 0)
    if isinstance(momentum, (int, float)) and 0 <= momentum <= 1:
        d["momentum"] = float(momentum) * 100.0

    return d


# ── Vulnerability ─────────────────────────────────────────────────────

@router.get("/vulnerability", response_model=GenericResponse)
async def vulnerability_assess(
    termo: str,
    momentum: float = 0.0,
    sentiment: float = 0.0,
    volume: int = 0,
    plataforma: str = "unknown",
):
    """Assess cultural vulnerability of a single signal (query params)."""
    try:
        from core.engines.vulnerability_engine import get_vulnerability_engine

        engine = get_vulnerability_engine()
        signal = {
            "termo": termo,
            "momentum": momentum,
            "sentiment": sentiment,
            "volume": volume,
            "plataforma": plataforma,
        }
        result = engine.assess_signal(signal)
        return GenericResponse(status="success", data=result)
    except Exception as exc:
        logger.error("GET /intelligence/vulnerability error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/vulnerability/batch", response_model=GenericResponse)
async def vulnerability_batch(req: BatchSignalInput):
    """Batch vulnerability assessment."""
    try:
        from core.engines.vulnerability_engine import get_vulnerability_engine

        engine = get_vulnerability_engine()
        results = [engine.assess_signal(_to_dict(s)) for s in req.signals]
        return GenericResponse(status="success", data={"total": len(results), "results": results})
    except Exception as exc:
        logger.error("POST /intelligence/vulnerability/batch error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ── Alerts ────────────────────────────────────────────────────────────

@router.get("/alerts", response_model=GenericResponse)
async def alerts_evaluate(
    termo: str,
    momentum: float = 0.0,
    sentiment: float = 0.0,
    volume: int = 0,
    plataforma: str = "unknown",
):
    """Evaluate cultural alerts for a single signal."""
    try:
        from alerts.cultural_alerts_engine import get_alerts_engine

        engine = get_alerts_engine()
        signal = {
            "termo": termo,
            "momentum": momentum,
            "sentiment": sentiment,
            "volume": volume,
            "plataforma": plataforma,
        }
        result = engine.evaluate_dict(signal)
        return GenericResponse(status="success", data=result)
    except Exception as exc:
        logger.error("GET /intelligence/alerts error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/alerts/batch", response_model=GenericResponse)
async def alerts_batch(req: BatchSignalInput):
    """Batch cultural alerts evaluation."""
    try:
        from alerts.cultural_alerts_engine import get_alerts_engine

        engine = get_alerts_engine()
        results = engine.batch_evaluate([_to_dict(s) for s in req.signals])
        return GenericResponse(status="success", data={"total": len(results), "results": results})
    except Exception as exc:
        logger.error("POST /intelligence/alerts/batch error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ── Strategic Actions ─────────────────────────────────────────────────

@router.get("/actions", response_model=GenericResponse)
async def actions_recommend(
    termo: str,
    momentum: float = 0.0,
    sentiment: float = 0.0,
    volume: int = 0,
    plataforma: str = "unknown",
):
    """Recommend strategic action for a single signal."""
    try:
        from core.intelligence.strategic_actions_engine import get_strategic_engine

        engine = get_strategic_engine()
        signal = {
            "termo": termo,
            "momentum": momentum,
            "sentiment": sentiment,
            "volume": volume,
            "plataforma": plataforma,
        }
        result = engine.recommend_dict(signal)
        return GenericResponse(status="success", data=result)
    except Exception as exc:
        logger.error("GET /intelligence/actions error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/actions/batch", response_model=GenericResponse)
async def actions_batch(req: BatchSignalInput):
    """Batch strategic action recommendations."""
    try:
        from core.intelligence.strategic_actions_engine import get_strategic_engine

        engine = get_strategic_engine()
        results = engine.batch_recommend([_to_dict(s) for s in req.signals])
        return GenericResponse(status="success", data={"total": len(results), "results": results})
    except Exception as exc:
        logger.error("POST /intelligence/actions/batch error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ── Scenarios ─────────────────────────────────────────────────────────

@router.get("/scenarios", response_model=GenericResponse)
async def scenarios_generate(
    termo: str,
    momentum: float = 0.0,
    sentiment: float = 0.0,
    volume: int = 0,
    plataforma: str = "unknown",
):
    """Generate cultural scenarios (optimistic / baseline / pessimistic)."""
    try:
        from core.scenario_engine import get_scenario_engine

        engine = get_scenario_engine()
        signal = {
            "termo": termo,
            "momentum": momentum,
            "sentiment": sentiment,
            "volume": volume,
            "plataforma": plataforma,
        }
        result = engine.generate_dict(signal)
        return GenericResponse(status="success", data=result)
    except Exception as exc:
        logger.error("GET /intelligence/scenarios error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/scenarios/batch", response_model=GenericResponse)
async def scenarios_batch(req: BatchSignalInput):
    """Batch scenario generation."""
    try:
        from core.scenario_engine import get_scenario_engine

        engine = get_scenario_engine()
        results = engine.batch_generate([_to_dict(s) for s in req.signals])
        return GenericResponse(status="success", data={"total": len(results), "results": results})
    except Exception as exc:
        logger.error("POST /intelligence/scenarios/batch error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ── Opportunities ─────────────────────────────────────────────────────

@router.get("/opportunities", response_model=GenericResponse)
async def opportunities_detect(
    termo: str,
    momentum: float = 0.0,
    sentiment: float = 0.0,
    volume: int = 0,
    plataforma: str = "unknown",
):
    """Detect cultural opportunities for a single signal."""
    try:
        from core.intelligence.opportunity_engine import get_opportunity_engine

        engine = get_opportunity_engine()
        signal = {
            "termo": termo,
            "momentum": momentum,
            "sentiment": sentiment,
            "volume": volume,
            "plataforma": plataforma,
        }
        result = engine.detect_dict(signal)
        return GenericResponse(status="success", data=result)
    except Exception as exc:
        logger.error("GET /intelligence/opportunities error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/opportunities/batch", response_model=GenericResponse)
async def opportunities_batch(req: BatchSignalInput):
    """Batch opportunity detection."""
    try:
        from core.intelligence.opportunity_engine import get_opportunity_engine

        engine = get_opportunity_engine()
        results = engine.detect_batch([_to_dict(s) for s in req.signals])
        return GenericResponse(status="success", data={"total": len(results), "results": results})
    except Exception as exc:
        logger.error("POST /intelligence/opportunities/batch error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ── Full Analysis (all 5 at once) ────────────────────────────────────

@router.post("/full", response_model=GenericResponse)
async def full_intelligence(sig: SignalInput):
    """Run all 5 intelligence engines on a single signal."""
    try:
        from core.engines.vulnerability_engine import get_vulnerability_engine
        from alerts.cultural_alerts_engine import get_alerts_engine
        from core.intelligence.strategic_actions_engine import get_strategic_engine
        from core.scenario_engine import get_scenario_engine
        from core.intelligence.opportunity_engine import get_opportunity_engine

        d = _to_dict(sig)

        result = {
            "signal": d,
            "vulnerability": get_vulnerability_engine().assess_signal(d),
            "cultural_alerts": get_alerts_engine().evaluate_dict(d),
            "strategic_action": get_strategic_engine().recommend_dict(d),
            "scenarios": get_scenario_engine().generate_dict(d),
            "opportunities": get_opportunity_engine().detect_dict(d),
        }

        return GenericResponse(status="success", data=result)
    except Exception as exc:
        logger.error("POST /intelligence/full error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
