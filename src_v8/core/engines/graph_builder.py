"""
core/graph_builder.py — INT-4A: Real Co-occurrence Graph Builder
=================================================================
Builds a **real** cultural graph from actual signal data instead of
using static affinity maps.

Three graph construction strategies:
  1. Co-occurrence graph: signals sharing the same circle/topic create edges
  2. Temporal proximity: signals close in time get weighted connections
  3. Semantic similarity: signals with similar termos (Jaccard on tokens)

The builder accumulates signal data over time and can persist/load
the graph for incremental updates.

INT-4B: Includes a simple training loop for the GNN (unsupervised
        link prediction objective — predict missing edges).

INT-4C: Provides a `build_and_analyze()` function that the Worker
        graph_enricher can call instead of the static affinity map.

Usage:
    builder = get_graph_builder()
    builder.add_signals(signals)
    graph_data = builder.build()  # returns nodes, edges, features
    result = builder.analyze(signal)  # run GNN on the built graph
"""

import logging
import math
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────

CIRCULOS = [
    "Música Popular", "Gastronomia", "Moda & Estilo", "Esporte",
    "Tecnologia", "Religiosidade", "Humor & Memes", "Natureza",
    "Arte Urbana", "Festas & Eventos", "Cinema & Séries",
    "Literatura", "Saúde & Bem-Estar", "Educação",
    "Mobilidade Urbana", "Empreendedorismo",
]

CIRCLE_INDEX = {c: i for i, c in enumerate(CIRCULOS)}

# Fallback affinity (used only when insufficient real data)
STATIC_AFFINITIES = {
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

# Minimum edges to consider graph "real" (not fallback)
MIN_REAL_EDGES = 10


# ── Data structures ──────────────────────────────────────────────────────

@dataclass
class GraphEdge:
    source: str
    target: str
    weight: float = 1.0
    edge_type: str = "co-occurrence"  # co-occurrence | temporal | semantic | affinity


@dataclass
class GraphNode:
    node_id: str
    node_type: str = "circle"  # circle | signal
    features: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BuiltGraph:
    """Result of graph building."""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    node_count: int
    edge_count: int
    is_real: bool  # True if built from actual co-occurrence data
    stats: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GNNAnalysisResult:
    """Result of GNN analysis on a signal."""
    influence_scores: Dict[str, float]
    communities: List[List[str]]
    central_nodes: List[str]
    propagation_paths: List[Dict[str, Any]]
    training_loss: Optional[float] = None
    graph_is_real: bool = False


# ── Graph Builder ────────────────────────────────────────────────────────

class CulturalGraphBuilder:
    """
    Builds a real cultural graph from signal co-occurrence data.

    Accumulates signals and computes:
    - Circle co-occurrence weights (how often circles appear together in signals)
    - Temporal proximity edges (signals close in time)
    - Term similarity edges (Jaccard on tokenized termos)
    """

    def __init__(
        self,
        temporal_window_hours: float = 24.0,
        min_jaccard: float = 0.15,
        max_signals: int = 5000,
    ):
        self.temporal_window_hours = temporal_window_hours
        self.min_jaccard = min_jaccard
        self.max_signals = max_signals

        # Accumulated data
        self._signals: List[dict] = []
        self._co_occurrence: Dict[Tuple[str, str], float] = defaultdict(float)
        self._circle_counts: Dict[str, int] = defaultdict(int)
        self._built_graph: Optional[BuiltGraph] = None

    @property
    def signal_count(self) -> int:
        return len(self._signals)

    def add_signal(self, signal: dict) -> None:
        """Add a single signal to the accumulator."""
        self._signals.append(signal)
        if len(self._signals) > self.max_signals:
            self._signals = self._signals[-self.max_signals:]
        self._built_graph = None  # invalidate cache

    def add_signals(self, signals: List[dict]) -> None:
        """Add a batch of signals."""
        for s in signals:
            self.add_signal(s)

    def reset(self) -> None:
        """Clear all accumulated data."""
        self._signals.clear()
        self._co_occurrence.clear()
        self._circle_counts.clear()
        self._built_graph = None

    # ── Build ────────────────────────────────────────────────────────

    def build(self) -> BuiltGraph:
        """Build the graph from accumulated signals."""
        if self._built_graph is not None:
            return self._built_graph

        nodes = []
        edges = []

        # 1. Build circle nodes with feature vectors
        self._compute_co_occurrence()
        for c in CIRCULOS:
            count = self._circle_counts.get(c, 0)
            features = [0.0] * 16
            idx = CIRCLE_INDEX.get(c, 0)
            features[idx] = count / max(len(self._signals), 1)
            nodes.append(GraphNode(
                node_id=c,
                node_type="circle",
                features=features,
                metadata={"signal_count": count},
            ))

        # 2. Co-occurrence edges (real data)
        for (c1, c2), weight in self._co_occurrence.items():
            edges.append(GraphEdge(
                source=c1, target=c2,
                weight=weight, edge_type="co-occurrence",
            ))

        # 3. If insufficient real edges, add static affinity fallback
        is_real = len(edges) >= MIN_REAL_EDGES
        if not is_real:
            seen = {(e.source, e.target) for e in edges}
            for src, neighbors in STATIC_AFFINITIES.items():
                for dst in neighbors:
                    key = tuple(sorted([src, dst]))
                    if key not in seen:
                        seen.add(key)
                        edges.append(GraphEdge(
                            source=src, target=dst,
                            weight=0.5, edge_type="affinity",
                        ))

        # 4. Temporal proximity edges (for signal nodes)
        temporal_edges = self._compute_temporal_edges()
        edges.extend(temporal_edges)

        # 5. Semantic similarity edges
        semantic_edges = self._compute_semantic_edges()
        edges.extend(semantic_edges)

        self._built_graph = BuiltGraph(
            nodes=nodes,
            edges=edges,
            node_count=len(nodes),
            edge_count=len(edges),
            is_real=is_real,
            stats={
                "total_signals": len(self._signals),
                "co_occurrence_edges": sum(1 for e in edges if e.edge_type == "co-occurrence"),
                "temporal_edges": sum(1 for e in edges if e.edge_type == "temporal"),
                "semantic_edges": sum(1 for e in edges if e.edge_type == "semantic"),
                "affinity_edges": sum(1 for e in edges if e.edge_type == "affinity"),
            },
        )
        return self._built_graph

    def _compute_co_occurrence(self) -> None:
        """Compute circle co-occurrence from signals."""
        self._co_occurrence.clear()
        self._circle_counts.clear()

        # Group signals by a time window to find co-occurring circles
        for sig in self._signals:
            circulo = sig.get("circulo", "")
            if circulo in CIRCLE_INDEX:
                self._circle_counts[circulo] += 1

        # Pairwise co-occurrence: signals from different circles in same time bucket
        buckets = defaultdict(set)  # bucket_key → set of circles
        for sig in self._signals:
            ts = sig.get("timestamp", sig.get("ts", 0))
            if isinstance(ts, str):
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    ts = dt.timestamp()
                except Exception:
                    ts = 0
            bucket = int(float(ts) / (self.temporal_window_hours * 3600))
            circulo = sig.get("circulo", "")
            if circulo in CIRCLE_INDEX:
                buckets[bucket].add(circulo)

        # Count co-occurrences
        for bucket_circles in buckets.values():
            circles_list = sorted(bucket_circles)
            for i in range(len(circles_list)):
                for j in range(i + 1, len(circles_list)):
                    key = (circles_list[i], circles_list[j])
                    self._co_occurrence[key] += 1.0

        # Normalize weights to [0, 1]
        if self._co_occurrence:
            max_w = max(self._co_occurrence.values())
            if max_w > 0:
                for k in self._co_occurrence:
                    self._co_occurrence[k] /= max_w

    def _compute_temporal_edges(self) -> List[GraphEdge]:
        """Find signals close in time and create edges."""
        edges = []
        if len(self._signals) < 2:
            return edges

        # Sort by timestamp
        timed = []
        for sig in self._signals[-200:]:  # limit for performance
            ts = sig.get("timestamp", sig.get("ts", 0))
            if isinstance(ts, str):
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    ts = dt.timestamp()
                except Exception:
                    ts = 0
            timed.append((float(ts), sig.get("termo", "")))
        timed.sort(key=lambda x: x[0])

        window_secs = self.temporal_window_hours * 3600
        for i in range(len(timed)):
            for j in range(i + 1, min(i + 5, len(timed))):
                delta = abs(timed[j][0] - timed[i][0])
                if delta < window_secs and timed[i][1] != timed[j][1]:
                    weight = 1.0 - (delta / window_secs)
                    edges.append(GraphEdge(
                        source=timed[i][1], target=timed[j][1],
                        weight=max(0.1, weight), edge_type="temporal",
                    ))
        return edges

    def _compute_semantic_edges(self) -> List[GraphEdge]:
        """Find signals with similar terms using Jaccard similarity."""
        edges = []
        termos = []
        for sig in self._signals[-200:]:
            t = sig.get("termo", "")
            if t:
                tokens = set(t.lower().split())
                termos.append((t, tokens))

        seen = set()
        for i in range(len(termos)):
            for j in range(i + 1, len(termos)):
                if termos[i][0] == termos[j][0]:
                    continue
                intersection = termos[i][1] & termos[j][1]
                union = termos[i][1] | termos[j][1]
                if union:
                    jaccard = len(intersection) / len(union)
                    if jaccard >= self.min_jaccard:
                        key = tuple(sorted([termos[i][0], termos[j][0]]))
                        if key not in seen:
                            seen.add(key)
                            edges.append(GraphEdge(
                                source=termos[i][0], target=termos[j][0],
                                weight=jaccard, edge_type="semantic",
                            ))
        return edges

    # ── INT-4B: Training Loop ────────────────────────────────────────

    def train(self, epochs: int = 10, lr: float = 0.01) -> Dict[str, Any]:
        """
        INT-4B: Simple unsupervised training loop.

        Uses link prediction: mask some edges, train GNN to predict them.
        Returns training metrics.
        """
        if len(self._signals) < 3:
            return {"status": "skipped", "reason": "insufficient signals", "epochs": 0}

        graph = self.build()
        if not graph.is_real:
            return {"status": "skipped", "reason": "graph not real (only static edges)", "epochs": 0}

        if graph.edge_count < 3:
            return {"status": "skipped", "reason": "too few edges", "epochs": 0}

        try:
            import numpy as np
            import torch
            import torch.nn.functional as F
            from core.engines.cultural_graph_analyzer import CulturalGNN

            # Build node features matrix
            node_ids = [n.node_id for n in graph.nodes]
            node_to_idx = {nid: i for i, nid in enumerate(node_ids)}

            features_np = np.array([n.features for n in graph.nodes], dtype=np.float32)
            if features_np.shape[1] == 0:
                features_np = np.eye(len(node_ids), dtype=np.float32)

            x = torch.from_numpy(features_np)
            input_dim = x.shape[1]

            # Build edge index (only edges between circle nodes)
            src_list, dst_list = [], []
            for e in graph.edges:
                if e.source in node_to_idx and e.target in node_to_idx:
                    si, ti = node_to_idx[e.source], node_to_idx[e.target]
                    src_list.extend([si, ti])
                    dst_list.extend([ti, si])

            if len(src_list) < 2:
                return {"status": "skipped", "reason": "no valid edges for training", "epochs": 0}

            edge_index = torch.tensor([src_list, dst_list], dtype=torch.long)

            # Model
            model = CulturalGNN(input_dim=input_dim, hidden_dim=64, output_dim=32)
            optimizer = torch.optim.Adam(model.parameters(), lr=lr)

            # Training: link prediction (dot product between node embeddings)
            losses = []
            model.train()
            for epoch in range(epochs):
                optimizer.zero_grad()
                z = model(x, edge_index)

                # Positive edges
                pos_src = edge_index[0]
                pos_dst = edge_index[1]
                pos_score = (z[pos_src] * z[pos_dst]).sum(dim=1)
                pos_loss = F.binary_cross_entropy_with_logits(
                    pos_score, torch.ones_like(pos_score)
                )

                # Negative sampling (random pairs)
                neg_src = torch.randint(0, len(node_ids), (len(pos_src),))
                neg_dst = torch.randint(0, len(node_ids), (len(pos_src),))
                neg_score = (z[neg_src] * z[neg_dst]).sum(dim=1)
                neg_loss = F.binary_cross_entropy_with_logits(
                    neg_score, torch.zeros_like(neg_score)
                )

                loss = pos_loss + neg_loss
                loss.backward()
                optimizer.step()
                losses.append(float(loss.item()))

            return {
                "status": "completed",
                "epochs": epochs,
                "final_loss": round(losses[-1], 4) if losses else None,
                "loss_history": [round(l, 4) for l in losses],
                "node_count": len(node_ids),
                "edge_count": len(src_list) // 2,
            }

        except ImportError as exc:
            return {"status": "skipped", "reason": f"torch not available: {exc}", "epochs": 0}
        except Exception as exc:
            return {"status": "error", "reason": str(exc), "epochs": 0}

    # ── INT-4C: Analyze signal using built graph ─────────────────────

    def analyze(self, signal: dict) -> GNNAnalysisResult:
        """
        INT-4C: Analyze a signal using the real co-occurrence graph.

        Falls back to static affinity if insufficient data.
        """
        graph = self.build()
        circulo = signal.get("circulo", "geral")

        try:
            import numpy as np
            from core.engines.cultural_graph_analyzer import CulturalGraphAnalyzer

            INPUT_DIM = max(16, len(graph.nodes))
            analyzer = CulturalGraphAnalyzer(input_dim=INPUT_DIM)

            # Add nodes
            for node in graph.nodes:
                features = node.features
                if len(features) < INPUT_DIM:
                    features = features + [0.0] * (INPUT_DIM - len(features))
                feat_np = np.array(features[:INPUT_DIM], dtype=np.float32)
                analyzer.add_cultural_node(node.node_id, feat_np, [])

            # Add edges
            for edge in graph.edges:
                if edge.source in [n.node_id for n in graph.nodes] and \
                   edge.target in [n.node_id for n in graph.nodes]:
                    try:
                        analyzer.cultural_graph.add_edge(
                            edge.source, edge.target, weight=edge.weight)
                    except Exception:
                        pass

            # Run propagation
            initial_state = {}
            if circulo in CIRCLE_INDEX:
                initial_state[circulo] = float(signal.get("momentum", signal.get("score", 0.5)))

            propagation = analyzer.analyze_cultural_propagation(
                initial_state=initial_state, steps=3,
            )

            if propagation:
                return GNNAnalysisResult(
                    influence_scores=propagation.influence_scores,
                    communities=propagation.community_structure,
                    central_nodes=propagation.central_nodes,
                    propagation_paths=[
                        {"source": p[0], "target": p[1], "weight": round(p[2], 3)}
                        for p in propagation.propagation_paths[:20]
                    ],
                    graph_is_real=graph.is_real,
                )
            else:
                return GNNAnalysisResult(
                    influence_scores={},
                    communities=[],
                    central_nodes=[],
                    propagation_paths=[],
                    graph_is_real=graph.is_real,
                )

        except ImportError:
            # No torch — return empty result
            return GNNAnalysisResult(
                influence_scores={},
                communities=[],
                central_nodes=[],
                propagation_paths=[],
                graph_is_real=False,
            )
        except Exception as exc:
            logger.warning("graph_builder.analyze error: %s", exc)
            return GNNAnalysisResult(
                influence_scores={},
                communities=[],
                central_nodes=[],
                propagation_paths=[],
                graph_is_real=False,
            )

    def to_dict(self) -> dict:
        """Serialize graph state for persistence."""
        graph = self.build()
        return {
            "nodes": [{"id": n.node_id, "type": n.node_type, "features": n.features, "metadata": n.metadata}
                      for n in graph.nodes],
            "edges": [{"source": e.source, "target": e.target, "weight": e.weight, "type": e.edge_type}
                      for e in graph.edges],
            "stats": graph.stats,
            "is_real": graph.is_real,
            "signal_count": len(self._signals),
        }


# ── Singleton ────────────────────────────────────────────────────────────

_graph_builder_instance: Optional[CulturalGraphBuilder] = None


def get_graph_builder() -> CulturalGraphBuilder:
    """Get or create the singleton graph builder."""
    global _graph_builder_instance
    if _graph_builder_instance is None:
        _graph_builder_instance = CulturalGraphBuilder()
    return _graph_builder_instance


def reset_graph_builder() -> None:
    """Reset the singleton (for testing)."""
    global _graph_builder_instance
    _graph_builder_instance = None
