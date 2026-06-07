"""
api/endpoints/graph_network.py — FASE 4: F-9 Network Graph Data API
====================================================================
REST endpoint for the Next.js frontend to render a network graph
visualization using D3.js or ECharts.

Uses ``get_graph_builder()`` singleton to produce a data-driven graph
from real signal co-occurrence data.  Falls back to static affinity
tables when fewer than 10 real co-occurrence edges are available.

Routes:
  POST /api/v8/graph/network         — Full network for signal batch (real co-occurrence)
  GET  /api/v8/graph/circles-network — 16-circle network (real or static fallback)
"""

import logging
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v8/graph", tags=["Network Graph (F-9)"])


# ── Models ───────────────────────────────────────────────────────────────

class GenericResponse(BaseModel):
    status: str = "success"
    data: Any = None
    metadata: Dict[str, Any] = {}


class NetworkRequest(BaseModel):
    signals: List[Dict[str, Any]] = Field(
        ..., min_length=1, max_length=200,
        description="Signals to build network from. Each must have 'termo' and ideally 'circulo'.",
    )
    include_influence: bool = Field(
        True, description="Run GNN influence scoring (requires torch).",
    )


class NetworkNode(BaseModel):
    id: str
    label: str
    type: str  # "circle" | "signal"
    size: float = 1.0
    color: Optional[str] = None
    metadata: Dict[str, Any] = {}


class NetworkEdge(BaseModel):
    source: str
    target: str
    weight: float = 1.0
    type: str = "affinity"  # "affinity" | "co-occurrence" | "signal-circle"
    label: Optional[str] = None


# ── Constants ────────────────────────────────────────────────────────────

CIRCULOS = [
    "Música Popular", "Gastronomia", "Moda & Estilo", "Esporte",
    "Tecnologia", "Religiosidade", "Humor & Memes", "Natureza",
    "Arte Urbana", "Festas & Eventos", "Cinema & Séries",
    "Literatura", "Saúde & Bem-Estar", "Educação",
    "Mobilidade Urbana", "Empreendedorismo",
]

CIRCLE_COLORS = {
    "Música Popular": "#e74c3c", "Gastronomia": "#e67e22",
    "Moda & Estilo": "#9b59b6", "Esporte": "#2ecc71",
    "Tecnologia": "#3498db", "Religiosidade": "#f1c40f",
    "Humor & Memes": "#1abc9c", "Natureza": "#27ae60",
    "Arte Urbana": "#e91e63", "Festas & Eventos": "#ff5722",
    "Cinema & Séries": "#795548", "Literatura": "#607d8b",
    "Saúde & Bem-Estar": "#00bcd4", "Educação": "#ff9800",
    "Mobilidade Urbana": "#9e9e9e", "Empreendedorismo": "#673ab7",
}

AFINIDADES = {
    "Música Popular":    ["Festas & Eventos", "Humor & Memes", "Arte Urbana"],
    "Gastronomia":       ["Saúde & Bem-Estar", "Natureza", "Empreendedorismo"],
    "Moda & Estilo":     ["Arte Urbana", "Cinema & Séries", "Empreendedorismo"],
    "Esporte":           ["Saúde & Bem-Estar", "Mobilidade Urbana", "Festas & Eventos"],
    "Tecnologia":        ["Empreendedorismo", "Educação", "Mobilidade Urbana"],
    "Religiosidade":     ["Música Popular", "Festas & Eventos", "Literatura"],
    "Humor & Memes":     ["Música Popular", "Cinema & Séries", "Tecnologia"],
    "Natureza":          ["Saúde & Bem-Estar", "Gastronomia", "Esporte"],
    "Arte Urbana":       ["Música Popular", "Moda & Estilo", "Cinema & Séries"],
    "Festas & Eventos":  ["Música Popular", "Gastronomia", "Esporte"],
    "Cinema & Séries":   ["Humor & Memes", "Arte Urbana", "Literatura"],
    "Literatura":        ["Educação", "Cinema & Séries", "Religiosidade"],
    "Saúde & Bem-Estar": ["Esporte", "Gastronomia", "Natureza"],
    "Educação":          ["Tecnologia", "Literatura", "Empreendedorismo"],
    "Mobilidade Urbana": ["Tecnologia", "Esporte", "Empreendedorismo"],
    "Empreendedorismo":  ["Tecnologia", "Educação", "Moda & Estilo"],
}


# ── Helpers ──────────────────────────────────────────────────────────────

def _build_circle_nodes() -> List[dict]:
    """Build the 16 cultural circle nodes."""
    nodes = []
    for c in CIRCULOS:
        nodes.append({
            "id": f"circle:{c}",
            "label": c,
            "type": "circle",
            "size": 3.0,
            "color": CIRCLE_COLORS.get(c, "#999999"),
            "metadata": {"neighbors": AFINIDADES.get(c, [])},
        })
    return nodes


def _build_affinity_edges() -> List[dict]:
    """Build edges between culturally adjacent circles."""
    edges = []
    seen = set()
    for src, neighbors in AFINIDADES.items():
        for dst in neighbors:
            key = tuple(sorted([src, dst]))
            if key not in seen:
                seen.add(key)
                edges.append({
                    "source": f"circle:{src}",
                    "target": f"circle:{dst}",
                    "weight": 0.7,
                    "type": "affinity",
                    "label": None,
                })
    return edges


def _assign_circle(signal: dict) -> str:
    """Get circle for a signal — use existing or classify."""
    circulo = signal.get("circulo", "")
    if circulo and circulo in CIRCULOS:
        return circulo
    # Attempt classification via circles processor
    try:
        from core.intelligence.circles_processor import CulturalCirclesProcessor
        proc = CulturalCirclesProcessor()
        text = signal.get("termo", "") + " " + signal.get("descricao", "")
        result = proc.process_text(text)
        if result and isinstance(result, dict):
            top = result.get("circulo_principal", "")
            if top in CIRCULOS:
                return top
    except Exception:
        pass
    return "geral"


def _build_signal_network(signals: List[dict]) -> tuple:
    """Build nodes and edges from signals, connecting to circles and to each other via co-occurrence."""
    signal_nodes = []
    signal_edges = []
    circle_signal_count = {}  # circle → count of signals

    for i, sig in enumerate(signals):
        termo = sig.get("termo", f"signal_{i}")
        circulo = _assign_circle(sig)
        momentum = float(sig.get("momentum", sig.get("score", 0.5)))
        plataforma = sig.get("plataforma", "unknown")

        node_id = f"signal:{termo}:{i}"
        signal_nodes.append({
            "id": node_id,
            "label": termo,
            "type": "signal",
            "size": max(0.5, min(momentum / 25.0, 4.0)),  # scale node size
            "color": CIRCLE_COLORS.get(circulo, "#999999"),
            "metadata": {
                "plataforma": plataforma,
                "circulo": circulo,
                "momentum": momentum,
            },
        })

        # Edge: signal → circle
        if circulo in CIRCULOS:
            signal_edges.append({
                "source": node_id,
                "target": f"circle:{circulo}",
                "weight": momentum / 100.0,
                "type": "signal-circle",
                "label": None,
            })
            circle_signal_count[circulo] = circle_signal_count.get(circulo, 0) + 1

    # Co-occurrence edges: signals sharing the same circle
    by_circle = {}
    for n in signal_nodes:
        c = n["metadata"].get("circulo", "")
        by_circle.setdefault(c, []).append(n["id"])
    for c, ids in by_circle.items():
        if len(ids) >= 2:
            for j in range(len(ids)):
                for k in range(j + 1, min(j + 4, len(ids))):  # limit edges
                    signal_edges.append({
                        "source": ids[j],
                        "target": ids[k],
                        "weight": 0.3,
                        "type": "co-occurrence",
                        "label": c,
                    })

    return signal_nodes, signal_edges, circle_signal_count


# ── Endpoints ────────────────────────────────────────────────────────────

@router.get("/circles-network", response_model=GenericResponse)
async def circles_network():
    """
    16-circle cultural network using real co-occurrence data when available.

    Uses ``get_graph_builder()`` to return the real graph if enough
    co-occurrence data has been accumulated (≥ 10 edges), otherwise
    falls back to the static affinity network.
    """
    try:
        from core.engines.graph_builder import get_graph_builder
        builder = get_graph_builder()
        graph = builder.build()

        nodes = []
        for gn in graph.nodes:
            nodes.append({
                "id": f"circle:{gn.node_id}",
                "label": gn.node_id,
                "type": "circle",
                "size": 3.0,
                "color": CIRCLE_COLORS.get(gn.node_id, "#999999"),
                "metadata": gn.metadata or {},
            })

        edges = []
        seen = set()
        for ge in graph.edges:
            key = tuple(sorted([ge.source, ge.target]))
            if key not in seen:
                seen.add(key)
                edges.append({
                    "source": f"circle:{ge.source}",
                    "target": f"circle:{ge.target}",
                    "weight": round(ge.weight, 3),
                    "type": ge.edge_type,
                    "label": None,
                })

        return GenericResponse(
            data={
                "nodes": nodes,
                "edges": edges,
                "node_count": len(nodes),
                "edge_count": len(edges),
                "graph_is_real": graph.is_real,
                "graph_stats": graph.stats,
                "layout_hint": "force-directed",
            },
            metadata={
                "type": "real-co-occurrence" if graph.is_real else "static-affinity-fallback",
                "circles": len(nodes),
            },
        )
    except Exception:
        # Fallback to static if graph_builder unavailable
        nodes = _build_circle_nodes()
        edges = _build_affinity_edges()
        return GenericResponse(
            data={
                "nodes": nodes,
                "edges": edges,
                "node_count": len(nodes),
                "edge_count": len(edges),
                "graph_is_real": False,
                "layout_hint": "force-directed",
            },
            metadata={"type": "static-affinity", "circles": 16},
        )


@router.post("/network", response_model=GenericResponse)
async def signal_network(req: NetworkRequest):
    """
    F-9 Network Graph: Build full network from a batch of signals.

    Uses ``get_graph_builder()`` to accumulate real co-occurrence data
    and produce a data-driven graph.  Falls back to static affinities
    when fewer than 10 real edges are available.

    Returns:
    - 16 circle nodes (always present)
    - Signal nodes (sized by momentum)
    - Real co-occurrence / affinity edges (circle ↔ circle)
    - Signal-circle edges (signal → its circle)
    - Co-occurrence edges (signals in same circle)
    - Optionally: GNN influence scores per node
    """
    t0 = time.time()

    # Feed signals into the graph builder for real co-occurrence
    try:
        from core.engines.graph_builder import get_graph_builder
        builder = get_graph_builder()
        for sig in req.signals:
            circulo = _assign_circle(sig)
            builder.add_signal({
                "termo": sig.get("termo", ""),
                "circulo": circulo,
                "momentum": float(sig.get("momentum", sig.get("score", 0.5))),
                "timestamp": sig.get("timestamp", time.time()),
            })

        # Build the real graph
        graph = builder.build()

        # Circle nodes from builder
        circle_nodes = []
        for gn in graph.nodes:
            circle_nodes.append({
                "id": f"circle:{gn.node_id}",
                "label": gn.node_id,
                "type": "circle",
                "size": 3.0,
                "color": CIRCLE_COLORS.get(gn.node_id, "#999999"),
                "metadata": gn.metadata or {},
            })

        # Circle-circle edges from real co-occurrence graph
        circle_edges = []
        seen = set()
        for ge in graph.edges:
            key = tuple(sorted([ge.source, ge.target]))
            if key not in seen:
                seen.add(key)
                circle_edges.append({
                    "source": f"circle:{ge.source}",
                    "target": f"circle:{ge.target}",
                    "weight": round(ge.weight, 3),
                    "type": ge.edge_type,
                    "label": None,
                })

        graph_is_real = graph.is_real
        graph_stats = graph.stats

    except Exception as exc:
        logger.debug("graph_builder not available, using static fallback: %s", exc)
        circle_nodes = _build_circle_nodes()
        circle_edges = _build_affinity_edges()
        graph_is_real = False
        graph_stats = {}

    # Signal layer (individual signal nodes + signal-circle edges)
    signal_nodes, signal_edges, circle_counts = _build_signal_network(req.signals)

    # Update circle node sizes based on signal count
    for cn in circle_nodes:
        circle_name = cn["label"]
        count = circle_counts.get(circle_name, 0)
        cn["size"] = 3.0 + count * 0.5
        cn["metadata"]["signal_count"] = count

    all_nodes = circle_nodes + signal_nodes
    all_edges = circle_edges + signal_edges

    # Optional: GNN influence via graph_builder
    influence_data = None
    if req.include_influence:
        try:
            from core.engines.graph_builder import get_graph_builder
            gb = get_graph_builder()
            # Pick most active circle for analysis seed
            if circle_counts:
                top_circle = max(circle_counts, key=circle_counts.get)
                analysis = gb.analyze({"termo": "network_batch", "circulo": top_circle})
                if analysis:
                    influence_data = {
                        "influence_scores": analysis.influence_scores,
                        "communities": analysis.communities,
                        "central_nodes": analysis.central_nodes,
                        "graph_is_real": analysis.graph_is_real,
                    }
        except Exception as exc:
            logger.debug("GNN influence not available: %s", exc)
            influence_data = {"error": str(exc), "note": "GNN influence requires accumulated signal data"}

    duration = time.time() - t0

    return GenericResponse(
        data={
            "nodes": all_nodes,
            "edges": all_edges,
            "node_count": len(all_nodes),
            "edge_count": len(all_edges),
            "circle_signal_distribution": circle_counts,
            "influence": influence_data,
            "graph_is_real": graph_is_real,
            "graph_stats": graph_stats,
            "layout_hint": "force-directed",
        },
        metadata={
            "duration_s": round(duration, 3),
            "signal_count": len(req.signals),
            "endpoint": "F-9 network graph",
            "data_source": "real-co-occurrence" if graph_is_real else "static-affinity-fallback",
        },
    )
