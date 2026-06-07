"""
api/endpoints/cluster_labels.py — F-4 FASE 3
==============================================
REST API for TF-IDF cluster labelling.

Routes:
  POST /api/v8/clusters/label          — label clusters from grouped signals
  POST /api/v8/clusters/label-flat     — label from flat list (uses cluster_key)
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v8/clusters", tags=["Cluster Labels (F-4)"])


# ── Request / Response models ─────────────────────────────────────────

class ClusterSignal(BaseModel):
    """Minimal signal for cluster labelling."""
    termo: str = Field(..., min_length=1)
    texto: Optional[str] = None
    circulo: Optional[str] = None
    reliability: Optional[str] = Field("MEDIA", description="Nível de veracidade: BAIXA, MEDIA ou ALTA")
    cluster_id: Optional[str] = Field(None, description="Identificador único do cluster")


class ClusterLabelInfo(BaseModel):
    """Detailed labels for a cluster."""
    label: str
    keywords: List[str]
    size: int
    reliability_tier: str
    tfidf_scores: Optional[List[List[Any]]] = None


class ClusterLabelRequest(BaseModel):
    """Pre-grouped signals by cluster id."""
    clusters: Dict[str, List[ClusterSignal]] = Field(
        ..., description="Map of cluster_id → list of signals"
    )


class FlatLabelRequest(BaseModel):
    """Flat list + key for auto-grouping."""
    signals: List[dict] = Field(..., min_length=1, max_length=500)
    cluster_key: str = Field("cluster_id", description="Dict key holding cluster id")


class ClusterLabelResponse(BaseModel):
    status: str
    labels: Dict[str, ClusterLabelInfo]
    total_clusters: int


class StabilityRequest(BaseModel):
    """Request for cluster stability comparison."""
    signals_prev: List[dict] = Field(..., description="Signals from period T-1")
    signals_curr: List[dict] = Field(..., description="Signals from period T")
    cluster_key: str = Field("cluster_id", description="Key for clustering")


# ── Endpoints ─────────────────────────────────────────────────────────

@router.post("/label", response_model=ClusterLabelResponse)
async def label_clusters(req: ClusterLabelRequest):
    """Label pre-grouped clusters via TF-IDF."""
    try:
        from core.clustering import get_cluster_labeler

        labeler = get_cluster_labeler()
        # Convert Pydantic models to plain dicts
        signals_by_cluster: Dict[str, List[dict]] = {
            cid: [s.dict() for s in sigs] for cid, sigs in req.clusters.items()
        }
        labels = labeler.label_clusters(signals_by_cluster)
        return ClusterLabelResponse(
            status="success",
            labels=labels,
            total_clusters=len(labels),
        )
    except Exception as exc:
        logger.error("POST /clusters/label error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/label-flat", response_model=ClusterLabelResponse)
async def label_flat(req: FlatLabelRequest):
    """Label clusters from a flat signal list (auto-grouped by cluster_key)."""
    try:
        from core.clustering import get_cluster_labeler

        labeler = get_cluster_labeler()
        # Ensure signals are dicts
        labels = labeler.label_from_flat_signals(req.signals, cluster_key=req.cluster_key)
        return ClusterLabelResponse(
            status="success",
            labels=labels,
            total_clusters=len(labels),
        )
    except Exception as exc:
        logger.error("POST /clusters/label-flat error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/stability", tags=["Stability Analytics (F-2)"])
async def check_stability(req: StabilityRequest):
    """Compare cluster stability between two periods."""
    try:
        from core.clustering import compare_signal_clusters

        result = compare_signal_clusters(
            req.signals_prev,
            req.signals_curr,
            cluster_key=req.cluster_key
        )
        return {
            "status": "success",
            "metrics": result.to_dict(),
            "interpretation": {
                "badge": result.badge_emoji,
                "message": result.badge_description,
                "status": result.status
            }
        }
    except Exception as exc:
        logger.error("POST /clusters/stability error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
