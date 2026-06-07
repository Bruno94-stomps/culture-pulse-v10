"""
api/endpoints/pipeline.py — Pipeline Management + Engine Gap Endpoints
=======================================================================
REST endpoints that expose the 6 Worker engines previously without
dedicated REST API access, plus pipeline management endpoints.

Engines now exposed:
  - momentum    (Worker priority 10 — via circles, now standalone)
  - tension     (Worker priority 22 — standalone analysis)
  - nature      (Worker priority 25 — signal nature classification)
  - velocity    (Worker priority 35 — velocity computation)
  - graph/GNN   (Worker priority 40 — graph propagation analysis)
  - stability   (F-2 — cluster stability comparison)

Pipeline management:
  GET  /api/v8/pipeline/status    — Worker pipeline info (all 16 engines)
  POST /api/v8/pipeline/enrich    — Enrich single signal through full pipeline
  GET  /api/v8/pipeline/engines   — List engines + stats

Engine-specific:
  POST /api/v8/momentum/compute    — Compute momentum for a signal
  POST /api/v8/tension/analyze     — Tension analysis on text
  POST /api/v8/nature/classify     — Signal nature classification
  POST /api/v8/velocity/compute    — Velocity features for signals
  POST /api/v8/graph/analyze       — GNN graph analysis for a signal
  POST /api/v8/stability/compare   — Cluster stability comparison
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Pipeline & Engines"])


# ── Pydantic models ──────────────────────────────────────────────────────

class GenericResponse(BaseModel):
    status: str = "success"
    data: Any = None
    metadata: Dict[str, Any] = {}


class MomentumRequest(BaseModel):
    platform: str = Field(..., min_length=1, description="Platform name (youtube, reddit, spotify, etc.)")
    volume: int = Field(0, ge=0)
    engagement: float = Field(0.0, ge=0.0)
    cultural_score: float = Field(0.0, ge=0.0)
    popularity: float = Field(0.0, ge=0.0)
    diversity: float = Field(0.0, ge=0.0)
    regional_spread: float = Field(0.0, ge=0.0, le=1.0)
    termo: str = ""


class TensionRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Signal text to analyze")
    sentiment: float = Field(0.5, ge=0.0, le=1.0)
    circle: str = ""
    plataforma: str = ""


class NatureRequest(BaseModel):
    termo: str = Field(..., min_length=1)
    mencoes: List[str] = Field(default_factory=list)
    contextos: List[str] = Field(default_factory=list)
    plataformas: List[str] = Field(default_factory=list)
    tensoes: List[Dict[str, Any]] = Field(default_factory=list)
    demografico: Dict[str, Any] = Field(default_factory=dict)
    velocity: float = 0.0
    volume: int = 0
    sentiment: float = 0.5


class VelocityRequest(BaseModel):
    signals: List[Dict[str, Any]] = Field(..., min_length=1, description="List of signal dicts")


class GraphRequest(BaseModel):
    termo: str = Field(..., min_length=1)
    circulo: str = Field("geral")
    score: float = Field(0.5, ge=0.0, le=1.0)


class StabilityRequest(BaseModel):
    clusters_current: Dict[str, List[str]] = Field(..., description="Current clusters: {label: [signal_ids]}")
    clusters_previous: Dict[str, List[str]] = Field(..., description="Previous clusters: {label: [signal_ids]}")


class EnrichRequest(BaseModel):
    signal: Dict[str, Any] = Field(..., description="Raw signal dict to enrich")
    onboarding_context: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional onboarding/business context to guide narrative enrichment.",
    )


# ── Pipeline Management ──────────────────────────────────────────────────

@router.get("/api/v8/pipeline/status", response_model=GenericResponse)
async def pipeline_status():
    """Get current Worker pipeline status: engines, order, stats."""
    try:
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        info = worker.pipeline_info
        return GenericResponse(
            data={
                "engine_count": len(info),
                "engines": info,
                "stats": worker._stats,
            },
            metadata={"timestamp": time.time()},
        )
    except Exception as exc:
        logger.warning("pipeline_status error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/api/v8/pipeline/engines", response_model=GenericResponse)
async def pipeline_engines():
    """List all registered engines with priority and enabled flag."""
    try:
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        engines = []
        for e in worker._engines:
            engines.append({
                "name": e.name,
                "priority": e.priority,
                "enabled": e.enabled,
                "required": e.required,
                "timeout": e.timeout,
            })
        return GenericResponse(
            data={"engines": engines, "total": len(engines)},
            metadata={"timestamp": time.time()},
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/api/v8/pipeline/enrich", response_model=GenericResponse)
async def pipeline_enrich(req: EnrichRequest):
    """Enrich a single signal through the full Worker pipeline (all 16 engines).

    The request may include `onboarding_context` to ensure the dashboard
    narrative enricher receives the user's onboarding/business intent.
    """
    try:
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()

        signal = {**req.signal}
        if req.onboarding_context is not None:
            signal["onboarding_context"] = req.onboarding_context

        enriched = await worker.enrich(signal)
        return GenericResponse(
            data=enriched,
            metadata={
                "engines_applied": enriched.get("_enrichment", {}).get("engines_applied", []),
                "engines_failed": enriched.get("_enrichment", {}).get("engines_failed", []),
                "duration": enriched.get("_enrichment", {}).get("duration", 0),
            },
        )
    except Exception as exc:
        logger.warning("pipeline_enrich error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ── Momentum ─────────────────────────────────────────────────────────────

@router.post("/api/v8/momentum/compute", response_model=GenericResponse)
async def compute_momentum(req: MomentumRequest):
    """Compute unified momentum score for a signal (INT-3 formula)."""
    try:
        from core.engines.momentum import compute_collector_momentum
        score = compute_collector_momentum(
            platform=req.platform,
            volume=req.volume,
            engagement=req.engagement,
            cultural_score=req.cultural_score,
            popularity=req.popularity,
            diversity=req.diversity,
            regional_spread=req.regional_spread,
            termo=req.termo,
        )
        return GenericResponse(
            data={"momentum": round(score, 2), "platform": req.platform, "termo": req.termo},
            metadata={"formula": "W_RES=0.40, W_VEL=0.40, W_DIS=0.20", "range": "0-100"},
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── Tension ──────────────────────────────────────────────────────────────

@router.post("/api/v8/tension/analyze", response_model=GenericResponse)
async def analyze_tension(req: TensionRequest):
    """Analyze cultural tensions in a signal text."""
    try:
        from core.engines.tension_engine import get_tension_engine
        engine = get_tension_engine()
        result = engine.analyze(
            text=req.text,
            sentiment=req.sentiment,
            circle=req.circle,
            plataforma=req.plataforma,
        )
        return GenericResponse(
            data={
                "score": result.score,
                "level": result.level.value if hasattr(result.level, "value") else str(result.level),
                "types": [t.value if hasattr(t, "value") else str(t) for t in result.types],
                "alerts": result.alerts,
                "keywords_found": result.keywords_found,
                "description": result.description,
            },
            metadata={"engine": "TensionEngine", "version": "1.0"},
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── Nature ───────────────────────────────────────────────────────────────

@router.post("/api/v8/nature/classify", response_model=GenericResponse)
async def classify_nature(req: NatureRequest):
    """Classify the cultural nature of a signal (authentic/simulated/commercial/astroturf)."""
    try:
        from core.classifiers.signal_nature_classifier import SignalNatureClassifier
        classifier = SignalNatureClassifier()
        result = classifier.classify(
            termo=req.termo,
            mencoes=req.mencoes,
            contextos=req.contextos,
            plataformas=req.plataformas,
            tensoes=req.tensoes,
            demografico=req.demografico,
            velocity=req.velocity,
            volume=req.volume,
            sentiment=req.sentiment,
        )
        return GenericResponse(
            data={
                "nature": result.nature,
                "confidence": result.confidence,
                "bot_risk": result.bot_risk,
                "commercial_risk": result.commercial_risk,
                "authenticity_score": result.authenticity_score,
                "evidencias": result.evidencias,
                "flags": result.flags,
                "nuances": result.nuances,
            },
            metadata={"engine": "SignalNatureClassifier"},
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── Velocity ─────────────────────────────────────────────────────────────

@router.post("/api/v8/velocity/compute", response_model=GenericResponse)
async def compute_velocity(req: VelocityRequest):
    """Compute velocity features for a batch of signals."""
    try:
        from core.engines.velocity_computer import VelocityComputer
        vc = VelocityComputer()
        enriched = vc.compute(req.signals)
        return GenericResponse(
            data={"signals": enriched, "count": len(enriched)},
            metadata={"engine": "VelocityComputer", "features": [
                "sequence_position", "interaction_type", "velocity",
                "acceleration", "momentum_weighted_velocity",
            ]},
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── Graph / GNN ──────────────────────────────────────────────────────────

@router.post("/api/v8/graph/analyze", response_model=GenericResponse)
async def analyze_graph(req: GraphRequest):
    """Run GNN graph analysis for a signal using the real co-occurrence graph builder.

    Uses ``get_graph_builder()`` singleton which accumulates real signal
    co-occurrence data, instead of static affinity tables.  Falls back to
    static affinities automatically when fewer than 10 real edges exist.
    """
    try:
        from core.engines.graph_builder import get_graph_builder, CIRCULOS

        circulo = req.circulo
        if circulo not in CIRCULOS:
            circulo = "geral"

        if circulo == "geral":
            return GenericResponse(
                data={"message": "Circle must be one of the 16 cultural circles for GNN analysis."},
                metadata={"available_circles": CIRCULOS},
            )

        builder = get_graph_builder()

        # Feed the request signal into the builder so it contributes to the graph
        builder.add_signal({
            "termo": req.termo,
            "circulo": circulo,
            "momentum": float(req.score),
            "timestamp": time.time(),
        })

        # Build graph (uses co-occurrence + temporal + semantic edges; falls back to static if < 10 real edges)
        graph = builder.build()

        # Analyze via GNN
        analysis = builder.analyze({
            "termo": req.termo,
            "circulo": circulo,
            "momentum": float(req.score),
        })

        # Collect neighbor circles from real edges
        vizinhos = sorted({
            e.target if e.source == circulo else e.source
            for e in graph.edges
            if circulo in (e.source, e.target)
        })

        graph_result = {
            "graph_nodes": len(graph.nodes),
            "graph_edges": len(graph.edges),
            "graph_is_real": graph.is_real,
            "graph_stats": graph.stats,
            "graph_neighbors": vizinhos,
            "termo": req.termo,
            "circulo": circulo,
        }

        if analysis is not None:
            graph_result["influence_scores"] = analysis.influence_scores
            graph_result["community_count"] = len(analysis.communities) if analysis.communities else 0
            graph_result["communities"] = analysis.communities
            graph_result["central_nodes"] = analysis.central_nodes
            graph_result["propagation_paths_count"] = len(analysis.propagation_paths) if analysis.propagation_paths else 0

        return GenericResponse(
            data=graph_result,
            metadata={
                "engine": "CulturalGraphBuilder",
                "model": "co-occurrence + GCN+GAT (when torch available)",
                "graph_is_real": graph.is_real,
            },
        )
    except ImportError as exc:
        raise HTTPException(
            status_code=501,
            detail=f"Graph dependencies not available: {exc}.",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── Cluster Stability ────────────────────────────────────────────────────

@router.post("/api/v8/stability/compare", response_model=GenericResponse)
async def compare_stability(req: StabilityRequest):
    """Compare two cluster snapshots (T vs T-1) for stability metrics."""
    try:
        from core.clustering import compare_clusters
        result = compare_clusters(
            current_clusters=req.clusters_current,
            previous_clusters=req.clusters_previous,
        )
        return GenericResponse(
            data={
                "ari_score": result.ari_score,
                "nmi_score": result.nmi_score,
                "status": result.status.value if hasattr(result.status, "value") else str(result.status),
                "description": result.description,
                "clusters_gained": result.clusters_gained,
                "clusters_lost": result.clusters_lost,
                "cluster_size_changes": result.cluster_size_changes,
            },
            metadata={"engine": "ClusterStability", "version": "1.0"},
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
