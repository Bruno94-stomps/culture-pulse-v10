#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S3.4 │ P18B — Ward Clustering: Sinais Fracos → Sinais Fortes
Culture Pulse V9.0 — Sprint 3, Passo 4

PROBLEMA:
  Sinais culturais são tratados isoladamente. Não há mecanismo para detectar
  quando múltiplos sinais fracos (de termos/plataformas diferentes) apontam
  para a mesma direção cultural — o que constitui um "sinal forte" emergente.

SOLUÇÃO (Paper B — Mühlroth 2023):
  1. Representar sinais como embeddings (BERTimbau fine-tuned S3.3 ou TF-IDF)
  2. AgglomerativeClustering(linkage='ward', threshold=auto)
  3. Threshold dinâmico: quantil z=0.05 das distâncias inter-cluster
  4. signal_strength = nº de plataformas DISTINTAS no cluster
  5. Clusters com signal_strength > média → candidatos a "sinal forte"

ARQUITETURA:
  ┌──────────────────────────────────────────────────────────────────────┐
  │ Input: List[Dict] — sinais culturais (termo, plataforma, raw_data)  │
  │                                                                     │
  │ Step 1 — Embedding                                                  │
  │   ├── Preferred: BERTimbau fine-tuned (S3.3) → 768d                │
  │   └── Fallback:  TF-IDF → Nd sparse (if BERT unavailable)          │
  │                                                                     │
  │ Step 2 — Distance Matrix                                            │
  │   └── scipy.spatial.distance.pdist(embeddings, 'euclidean')         │
  │                                                                     │
  │ Step 3 — Dynamic Threshold                                          │
  │   └── z=0.05 quantile of pairwise distances                        │
  │   └── OR: Silhouette-guided search over [2..sqrt(N)] clusters       │
  │                                                                     │
  │ Step 4 — Ward Clustering                                            │
  │   └── AgglomerativeClustering(linkage='ward', threshold=dynamic)    │
  │                                                                     │
  │ Step 5 — Signal Strength                                            │
  │   └── For each cluster: count DISTINCT platforms                    │
  │   └── Clusters above mean → "sinais fortes"                        │
  │                                                                     │
  │ Output: List[SignalCluster] with metadata                           │
  └──────────────────────────────────────────────────────────────────────┘

DADOS DISPONÍVEIS (Supabase cultural_signals):
  - 189 sinais, 30 termos, 8 plataformas
  - Columns: id, termo, plataforma, circulo, score, regiao, raw_data, ts
  - raw_data contém: narrativa, momentum, volume, sentiment, alma_score,
    evidencias, explicacao, s23_scaled, s22_novelty/ner, etc.

CRITÉRIO DE ACEITE:
  Em 7 dias de operação (ou na base atual de 189 sinais):
  ≥5 "sinais fortes" identificados com ≥3 plataformas distintas cada

REFERÊNCIAS:
  Mühlroth & Grottke (2023) — A systematic literature review of weak signals
  Ward (1963) — Hierarchical grouping to optimize an objective function

USO:
  from core.engines.signal_aggregator import (
      SignalAggregator, SignalCluster,
      run_ward_clustering, compute_signal_strength,
  )

Autor: Culture Pulse Team
Data: 2026-02-20
Sprint: S3.4 │ P18B
"""

import json
import logging
import math
import os
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════

# Minimum cluster signal strength to be considered "sinal forte"
MIN_STRONG_SIGNAL_PLATFORMS = 3

# Quantile for dynamic threshold (z=0.05 from Mühlroth paper)
DISTANCE_QUANTILE = 0.05

# Silhouette search range
MIN_K = 2
MAX_K_RATIO = 0.5  # max k = N * ratio (cap to avoid over-fragmenting)

# Embedding modes
EMBED_BERT = "bert_finetuned"
EMBED_TFIDF = "tfidf_fallback"

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ═══════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class SignalCluster:
    """A cluster of related cultural signals that may form a strong signal."""
    cluster_id: int
    size: int
    distinct_platforms: int
    platform_list: List[str]
    distinct_termos: int
    termo_list: List[str]
    circulo_distribution: Dict[str, int]
    dominant_circulo: str
    signal_strength: float      # Composite strength score
    is_strong: bool             # strength ≥ threshold
    centroid_idx: int           # index of signal closest to centroid
    mean_score: float           # average signal score in cluster
    mean_momentum: float        # average momentum
    mean_sentiment: float       # average sentiment
    member_ids: List[int]       # Supabase IDs of signals in this cluster
    narrative_summary: str      # Combined narrative insight


@dataclass
class ClusteringResult:
    """Full result of a Ward clustering run."""
    n_signals: int
    n_clusters: int
    n_strong: int
    embedding_mode: str
    distance_threshold: float
    silhouette_score: float
    calinski_harabasz: float
    clusters: List[SignalCluster]
    strong_clusters: List[SignalCluster]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


# ═══════════════════════════════════════════════════════════════════════
# EMBEDDING GENERATION
# ═══════════════════════════════════════════════════════════════════════

def _build_text_from_signal(signal: Dict) -> str:
    """
    Construct text representation from a cultural signal dict.
    Combines: termo + narrativa (or explicacao) from raw_data.
    """
    termo = signal.get("termo", "")
    raw = signal.get("raw_data", {})
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            raw = {}
    
    narrativa = raw.get("narrativa", raw.get("explicacao", ""))
    
    # Build composite text
    parts = [termo]
    if narrativa:
        parts.append(narrativa)
    
    # Add enrichment context if available
    enrichment = raw.get("enrichment_context", "")
    if enrichment:
        parts.append(enrichment)
    
    return ". ".join(parts)


def embed_signals_bert(
    signals: List[Dict],
    model_dir: str = "models/bertimbau_cultural_v1",
    max_len: int = 128,
    batch_size: int = 32,
) -> np.ndarray:
    """
    Generate domain-adapted 768d embeddings using fine-tuned BERTimbau (S3.3).
    
    Returns:
        np.ndarray shape (N, 768)
    """
    import importlib.util

    # Direct import to avoid core/__init__.py (torch_geometric issue)
    finetuner_path = PROJECT_ROOT / "core" / "bert_finetuner.py"
    spec = importlib.util.spec_from_file_location("bert_finetuner", str(finetuner_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    load_finetuned_model = mod.load_finetuned_model
    extract_domain_embeddings = mod.extract_domain_embeddings

    model_path = PROJECT_ROOT / model_dir
    if not (model_path / "finetuned_weights.pt").exists():
        raise FileNotFoundError(
            f"Fine-tuned model not found at {model_path}. Run S3.3 first."
        )

    model = load_finetuned_model(str(model_path))
    texts = [_build_text_from_signal(s) for s in signals]
    
    embeddings = extract_domain_embeddings(model, texts, max_len=max_len, batch_size=batch_size)
    logger.info(f"🔤 BERT embeddings: {embeddings.shape} from {len(texts)} signals")
    return embeddings


def embed_signals_tfidf(signals: List[Dict]) -> np.ndarray:
    """
    TF-IDF fallback embeddings (no BERT required).
    
    Returns:
        np.ndarray shape (N, D) — dense, via TruncatedSVD for Ward compatibility.
    """
    from sklearn.decomposition import TruncatedSVD
    from sklearn.feature_extraction.text import TfidfVectorizer

    texts = [_build_text_from_signal(s) for s in signals]
    
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95,
        sublinear_tf=True,
    )
    tfidf_matrix = vectorizer.fit_transform(texts)
    
    # Reduce to dense for Ward (Ward requires dense/euclidean)
    n_components = min(100, tfidf_matrix.shape[1] - 1, tfidf_matrix.shape[0] - 1)
    if n_components < 2:
        n_components = 2
    
    svd = TruncatedSVD(n_components=n_components, random_state=42)
    dense_embeddings = svd.fit_transform(tfidf_matrix)
    
    explained_var = svd.explained_variance_ratio_.sum()
    logger.info(
        f"📊 TF-IDF embeddings: {dense_embeddings.shape} "
        f"(SVD explains {explained_var:.1%} variance)"
    )
    return dense_embeddings


def embed_signals(
    signals: List[Dict],
    mode: str = "auto",
    model_dir: str = "models/bertimbau_cultural_v1",
) -> Tuple[np.ndarray, str]:
    """
    Embed signals using best available method.
    
    Args:
        signals: list of cultural signal dicts
        mode: "bert_finetuned", "tfidf_fallback", or "auto" (try BERT, fallback TF-IDF)
    
    Returns:
        (embeddings, mode_used)
    """
    if mode == "auto":
        try:
            emb = embed_signals_bert(signals, model_dir=model_dir)
            return emb, EMBED_BERT
        except Exception as e:
            logger.warning(f"⚠️ BERT embedding failed ({e}), falling back to TF-IDF")
            emb = embed_signals_tfidf(signals)
            return emb, EMBED_TFIDF
    elif mode == EMBED_BERT:
        return embed_signals_bert(signals, model_dir=model_dir), EMBED_BERT
    else:
        return embed_signals_tfidf(signals), EMBED_TFIDF


# ═══════════════════════════════════════════════════════════════════════
# DYNAMIC THRESHOLD COMPUTATION
# ═══════════════════════════════════════════════════════════════════════

def compute_dynamic_threshold(
    embeddings: np.ndarray,
    quantile: float = DISTANCE_QUANTILE,
) -> float:
    """
    Compute Ward-compatible distance threshold using quantile of pairwise distances.
    
    From Mühlroth 2023: use z=0.05 quantile to set threshold dynamically
    based on corpus density. Lower quantile → more clusters (finer granularity).
    
    Args:
        embeddings: (N, D) matrix
        quantile: percentile of distances to use as threshold (0.05 = 5th percentile)
    
    Returns:
        float: distance threshold for AgglomerativeClustering
    """
    from scipy.spatial.distance import pdist

    if len(embeddings) < 3:
        return 1.0  # fallback
    
    distances = pdist(embeddings, metric="euclidean")
    
    # Use percentile from higher end to get meaningful clusters
    # The threshold means: merge clusters whose distance < threshold
    # Higher threshold → fewer clusters; lower → more clusters
    # Mühlroth uses z=0.05 (5th percentile) as the CUTOFF — 
    # meaning we keep clusters that are tight (within 5th percentile of distances)
    # In practice, we want a moderate number of clusters, so we use a higher quantile
    # to allow merging up to a reasonable distance.
    
    # Strategy: use median × scaling factor based on quantile
    # OR: silhouette-guided search (more robust)
    q_val = np.quantile(distances, 1.0 - quantile)  # 95th percentile for cutoff
    median_dist = np.median(distances)
    
    # Threshold = blend of quantile and median
    threshold = 0.6 * q_val + 0.4 * median_dist
    
    logger.info(
        f"📏 Threshold: {threshold:.4f} "
        f"(q{quantile}={np.quantile(distances, quantile):.4f}, "
        f"median={median_dist:.4f}, "
        f"q{1-quantile}={q_val:.4f})"
    )
    return threshold


def find_optimal_k_silhouette(
    embeddings: np.ndarray,
    min_k: int = MIN_K,
    max_k: Optional[int] = None,
) -> Tuple[int, float]:
    """
    Find optimal number of clusters via silhouette analysis.
    
    Scans k from min_k to max_k, picks k with highest silhouette score.
    
    Returns:
        (best_k, best_silhouette)
    """
    from sklearn.cluster import AgglomerativeClustering
    from sklearn.metrics import silhouette_score

    n = len(embeddings)
    if max_k is None:
        max_k = max(min_k + 1, min(int(n * MAX_K_RATIO), int(math.sqrt(n)) + 3))
    max_k = min(max_k, n - 1)
    
    if max_k < min_k:
        return min_k, -1.0
    
    best_k, best_sil = min_k, -1.0
    scores = {}
    
    for k in range(min_k, max_k + 1):
        model = AgglomerativeClustering(n_clusters=k, linkage="ward")
        labels = model.fit_predict(embeddings)
        
        if len(set(labels)) < 2:
            continue
        
        sil = silhouette_score(embeddings, labels, metric="euclidean")
        scores[k] = sil
        
        if sil > best_sil:
            best_sil = sil
            best_k = k
    
    logger.info(
        f"🔍 Silhouette search: best k={best_k} (sil={best_sil:.4f}), "
        f"scanned {min_k}..{max_k}"
    )
    return best_k, best_sil


# ═══════════════════════════════════════════════════════════════════════
# WARD CLUSTERING ENGINE
# ═══════════════════════════════════════════════════════════════════════

def run_ward_clustering(
    embeddings: np.ndarray,
    method: str = "silhouette",
    quantile: float = DISTANCE_QUANTILE,
    n_clusters: Optional[int] = None,
) -> Tuple[np.ndarray, dict]:
    """
    Run Agglomerative Clustering with Ward linkage.
    
    Three modes:
      1. "silhouette" — search for optimal k via silhouette (recommended)
      2. "threshold"  — dynamic threshold from distance quantile (Mühlroth)
      3. "fixed"      — use n_clusters directly
    
    Returns:
        (labels, info_dict) where labels.shape = (N,)
    """
    from sklearn.cluster import AgglomerativeClustering
    from sklearn.metrics import calinski_harabasz_score, silhouette_score

    n = len(embeddings)
    info = {"method": method, "n_signals": n}
    
    if method == "silhouette":
        best_k, best_sil = find_optimal_k_silhouette(embeddings)
        model = AgglomerativeClustering(n_clusters=best_k, linkage="ward")
        labels = model.fit_predict(embeddings)
        info["n_clusters"] = best_k
        info["silhouette"] = best_sil
        info["distance_threshold"] = -1.0  # not used in this mode
        
    elif method == "threshold":
        threshold = compute_dynamic_threshold(embeddings, quantile)
        model = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=threshold,
            linkage="ward",
        )
        labels = model.fit_predict(embeddings)
        info["n_clusters"] = len(set(labels))
        info["distance_threshold"] = threshold
        
        if len(set(labels)) >= 2:
            info["silhouette"] = silhouette_score(embeddings, labels, metric="euclidean")
        else:
            info["silhouette"] = -1.0
    
    elif method == "fixed":
        if n_clusters is None:
            n_clusters = max(2, int(math.sqrt(n)))
        model = AgglomerativeClustering(n_clusters=n_clusters, linkage="ward")
        labels = model.fit_predict(embeddings)
        info["n_clusters"] = n_clusters
        info["distance_threshold"] = -1.0
        
        if len(set(labels)) >= 2:
            info["silhouette"] = silhouette_score(embeddings, labels, metric="euclidean")
        else:
            info["silhouette"] = -1.0
    
    else:
        raise ValueError(f"Unknown method: {method}. Use 'silhouette', 'threshold', or 'fixed'.")
    
    # Calinski-Harabasz (higher = better-defined clusters)
    if len(set(labels)) >= 2:
        info["calinski_harabasz"] = calinski_harabasz_score(embeddings, labels)
    else:
        info["calinski_harabasz"] = 0.0
    
    logger.info(
        f"🌲 Ward clustering: {info['n_clusters']} clusters, "
        f"sil={info.get('silhouette', -1):.4f}, "
        f"CH={info.get('calinski_harabasz', 0):.1f}"
    )
    return labels, info


# ═══════════════════════════════════════════════════════════════════════
# SIGNAL STRENGTH COMPUTATION
# ═══════════════════════════════════════════════════════════════════════

def compute_signal_strength(
    cluster_signals: List[Dict],
) -> Tuple[float, Dict[str, Any]]:
    """
    Compute signal strength for a cluster following Mühlroth (2023).
    
    Signal strength = weighted count of distinct platforms.
    Weight accounts for platform diversity and volume.
    
    A signal in Reddit + YouTube + NewsAPI is stronger than 3× YouTube
    because it indicates genuine cultural pervasion, not viral echo.
    
    Returns:
        (strength_score, detail_dict)
    """
    platforms = [s.get("plataforma", "unknown") for s in cluster_signals]
    distinct = list(set(platforms))
    n_distinct = len(distinct)
    
    # Platform weights (higher = more signal about genuine cultural interest)
    PLATFORM_WEIGHTS = {
        "YouTube": 1.0,
        "Reddit": 1.2,      # Community discussion → strong signal
        "NewsAPI": 1.3,      # Mainstream coverage → very strong
        "Spotify": 0.9,      # Music-specific, narrower
        "Instagram/Threads": 1.0,
        "Meetup": 1.1,       # Physical events → genuine interest
        "IBGE": 1.4,         # Official data → highest weight
        "internal": 0.3,     # Internal (model logs) → low signal
    }
    
    # Weighted distinct platform count
    weighted_distinct = sum(
        PLATFORM_WEIGHTS.get(p, 1.0) for p in distinct
    )
    
    # Volume factor: log-scaled total signals
    volume_factor = math.log1p(len(cluster_signals))
    
    # Composite strength
    strength = weighted_distinct * (1 + 0.2 * volume_factor)
    
    # Aggregate metrics from raw_data
    momenta, sentiments, scores = [], [], []
    for s in cluster_signals:
        raw = s.get("raw_data", {})
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                raw = {}
        momenta.append(raw.get("momentum", 0.0) or 0.0)
        sentiments.append(raw.get("sentiment", 0.5) or 0.5)
        scores.append(s.get("score", 0.0) or 0.0)
    
    detail = {
        "n_signals": len(cluster_signals),
        "distinct_platforms": n_distinct,
        "platform_list": distinct,
        "weighted_distinct": round(weighted_distinct, 3),
        "volume_factor": round(volume_factor, 3),
        "strength": round(strength, 3),
        "mean_momentum": round(np.mean(momenta), 3) if momenta else 0.0,
        "mean_sentiment": round(np.mean(sentiments), 3) if sentiments else 0.5,
        "mean_score": round(np.mean(scores), 3) if scores else 0.0,
    }
    return strength, detail


# ═══════════════════════════════════════════════════════════════════════
# CLUSTER NARRATIVE GENERATION
# ═══════════════════════════════════════════════════════════════════════

def _generate_cluster_narrative(
    cluster_signals: List[Dict],
    dominant_circulo: str,
    strength_detail: Dict,
) -> str:
    """Generate a human-readable narrative summary for a cluster."""
    termos = list(set(s.get("termo", "") for s in cluster_signals))
    plats = strength_detail["platform_list"]
    n_plats = strength_detail["distinct_platforms"]
    n_sigs = strength_detail["n_signals"]
    mom = strength_detail["mean_momentum"]
    sent = strength_detail["mean_sentiment"]
    
    # Sentiment description
    if sent > 0.65:
        sent_desc = "sentimento predominantemente positivo"
    elif sent < 0.35:
        sent_desc = "sentimento predominantemente negativo"
    else:
        sent_desc = "sentimento neutro/misto"
    
    # Momentum description
    if mom > 60:
        mom_desc = "alto momentum"
    elif mom > 30:
        mom_desc = "momentum moderado"
    else:
        mom_desc = "baixo momentum"
    
    # Strong signal assessment
    if n_plats >= MIN_STRONG_SIGNAL_PLATFORMS:
        strength_desc = (
            f"SINAL FORTE — convergência em {n_plats} plataformas distintas "
            f"({', '.join(plats)})"
        )
    else:
        strength_desc = (
            f"Sinal emergente — detectado em {n_plats} plataforma(s) "
            f"({', '.join(plats)})"
        )
    
    narrative = (
        f"Cluster no círculo '{dominant_circulo}' agrupa {n_sigs} sinais sobre "
        f"'{', '.join(termos[:5])}'. {strength_desc}. "
        f"Com {mom_desc} e {sent_desc}."
    )
    return narrative


# ═══════════════════════════════════════════════════════════════════════
# FULL PIPELINE — SignalAggregator class
# ═══════════════════════════════════════════════════════════════════════

class SignalAggregator:
    """
    Ward-linkage clustering pipeline for detecting strong cultural signals.
    
    Paper: Mühlroth & Grottke (2023) — weak signal aggregation.
    
    Usage:
        agg = SignalAggregator(embed_mode="auto")
        result = agg.aggregate(signals)
        for sc in result.strong_clusters:
            print(f"🔥 {sc.narrative_summary}")
    """
    
    def __init__(
        self,
        embed_mode: str = "auto",
        cluster_method: str = "silhouette",
        min_strong_platforms: int = MIN_STRONG_SIGNAL_PLATFORMS,
        distance_quantile: float = DISTANCE_QUANTILE,
        model_dir: str = "models/bertimbau_cultural_v1",
    ):
        self.embed_mode = embed_mode
        self.cluster_method = cluster_method
        self.min_strong_platforms = min_strong_platforms
        self.distance_quantile = distance_quantile
        self.model_dir = model_dir
    
    def aggregate(
        self,
        signals: List[Dict],
        n_clusters: Optional[int] = None,
    ) -> ClusteringResult:
        """
        Full pipeline: embed → cluster → compute strength → identify strong signals.
        
        Args:
            signals: list of cultural signal dicts (from Supabase or collectors)
            n_clusters: override cluster count (only for method="fixed")
        
        Returns:
            ClusteringResult with all clusters and strong signal identification
        """
        t0 = time.time()
        n = len(signals)
        
        if n < 3:
            logger.warning(f"⚠️ Only {n} signals — too few for clustering")
            return ClusteringResult(
                n_signals=n, n_clusters=0, n_strong=0,
                embedding_mode="none", distance_threshold=0.0,
                silhouette_score=-1.0, calinski_harabasz=0.0,
                clusters=[], strong_clusters=[],
            )
        
        # Step 1: Embed
        embeddings, mode_used = embed_signals(
            signals, mode=self.embed_mode, model_dir=self.model_dir
        )
        
        # Step 2-3: Cluster
        labels, cluster_info = run_ward_clustering(
            embeddings,
            method=self.cluster_method,
            quantile=self.distance_quantile,
            n_clusters=n_clusters,
        )
        
        # Step 4: Build cluster objects
        clusters = self._build_clusters(signals, embeddings, labels)
        
        # Step 5: Identify strong signals
        mean_strength = np.mean([c.signal_strength for c in clusters]) if clusters else 0.0
        strong_clusters = [
            c for c in clusters
            if c.distinct_platforms >= self.min_strong_platforms and c.is_strong
        ]
        
        elapsed = time.time() - t0
        
        result = ClusteringResult(
            n_signals=n,
            n_clusters=cluster_info["n_clusters"],
            n_strong=len(strong_clusters),
            embedding_mode=mode_used,
            distance_threshold=cluster_info.get("distance_threshold", -1.0),
            silhouette_score=cluster_info.get("silhouette", -1.0),
            calinski_harabasz=cluster_info.get("calinski_harabasz", 0.0),
            clusters=clusters,
            strong_clusters=strong_clusters,
        )
        
        logger.info(
            f"✅ Aggregation complete: {n} signals → {result.n_clusters} clusters "
            f"({result.n_strong} strong) in {elapsed:.1f}s "
            f"[{mode_used}, sil={result.silhouette_score:.4f}]"
        )
        return result
    
    def _build_clusters(
        self,
        signals: List[Dict],
        embeddings: np.ndarray,
        labels: np.ndarray,
    ) -> List[SignalCluster]:
        """Build SignalCluster objects from clustering labels."""
        unique_labels = sorted(set(labels))
        clusters = []
        
        # Compute mean strength for "is_strong" threshold
        # Two-pass: first compute strengths, then decide threshold
        pre_strengths = []
        cluster_data = []
        
        for cid in unique_labels:
            mask = labels == cid
            cluster_signals = [signals[i] for i in range(len(signals)) if mask[i]]
            cluster_embs = embeddings[mask]
            
            strength, strength_detail = compute_signal_strength(cluster_signals)
            pre_strengths.append(strength)
            cluster_data.append((cid, cluster_signals, cluster_embs, strength, strength_detail))
        
        mean_strength = np.mean(pre_strengths) if pre_strengths else 0.0
        
        for cid, cluster_signals, cluster_embs, strength, detail in cluster_data:
            # Termo distribution
            termos = [s.get("termo", "") for s in cluster_signals]
            termo_counts = Counter(termos)
            
            # Circle distribution
            circulos = [s.get("circulo", "unknown") for s in cluster_signals if s.get("circulo")]
            circ_counts = Counter(circulos)
            dominant = circ_counts.most_common(1)[0][0] if circ_counts else "unknown"
            
            # Centroid: signal closest to mean embedding
            centroid_emb = cluster_embs.mean(axis=0)
            dists_to_centroid = np.linalg.norm(cluster_embs - centroid_emb, axis=1)
            centroid_idx = int(np.argmin(dists_to_centroid))
            
            # Member IDs
            member_ids = [int(s.get("id", -1)) for s in cluster_signals]
            
            # Is strong?
            # Primary criterion (Mühlroth 2023): distinct platforms ≥ threshold
            # Secondary criterion: above-average strength OR ≥2 distinct termos
            is_strong = (
                detail["distinct_platforms"] >= self.min_strong_platforms
                and (strength >= mean_strength or len(set(termos)) >= 2)
            )
            
            narrative = _generate_cluster_narrative(cluster_signals, dominant, detail)
            
            sc = SignalCluster(
                cluster_id=cid,
                size=len(cluster_signals),
                distinct_platforms=detail["distinct_platforms"],
                platform_list=detail["platform_list"],
                distinct_termos=len(set(termos)),
                termo_list=list(set(termos)),
                circulo_distribution=dict(circ_counts),
                dominant_circulo=dominant,
                signal_strength=round(strength, 3),
                is_strong=is_strong,
                centroid_idx=centroid_idx,
                mean_score=detail["mean_score"],
                mean_momentum=detail["mean_momentum"],
                mean_sentiment=detail["mean_sentiment"],
                member_ids=member_ids,
                narrative_summary=narrative,
            )
            clusters.append(sc)
        
        # Sort by strength descending
        clusters.sort(key=lambda c: c.signal_strength, reverse=True)
        return clusters
    
    def to_dict(self, result: ClusteringResult) -> Dict:
        """Serialize ClusteringResult to JSON-safe dict."""
        def _safe(v):
            """Convert numpy types to native Python."""
            if isinstance(v, (np.integer,)):
                return int(v)
            if isinstance(v, (np.floating,)):
                return float(v)
            if isinstance(v, np.ndarray):
                return v.tolist()
            return v

        return {
            "n_signals": _safe(result.n_signals),
            "n_clusters": _safe(result.n_clusters),
            "n_strong": _safe(result.n_strong),
            "embedding_mode": result.embedding_mode,
            "distance_threshold": _safe(result.distance_threshold),
            "silhouette_score": round(float(result.silhouette_score), 4),
            "calinski_harabasz": round(float(result.calinski_harabasz), 2),
            "timestamp": result.timestamp,
            "clusters": [
                {
                    "cluster_id": _safe(c.cluster_id),
                    "size": _safe(c.size),
                    "distinct_platforms": _safe(c.distinct_platforms),
                    "platform_list": c.platform_list,
                    "distinct_termos": _safe(c.distinct_termos),
                    "termo_list": c.termo_list,
                    "circulo_distribution": c.circulo_distribution,
                    "dominant_circulo": c.dominant_circulo,
                    "signal_strength": float(c.signal_strength),
                    "is_strong": c.is_strong,
                    "mean_score": float(c.mean_score),
                    "mean_momentum": float(c.mean_momentum),
                    "mean_sentiment": float(c.mean_sentiment),
                    "member_ids": [int(x) for x in c.member_ids],
                    "narrative_summary": c.narrative_summary,
                }
                for c in result.clusters
            ],
            "strong_clusters": [
                {
                    "cluster_id": _safe(c.cluster_id),
                    "size": _safe(c.size),
                    "signal_strength": float(c.signal_strength),
                    "distinct_platforms": _safe(c.distinct_platforms),
                    "platform_list": c.platform_list,
                    "termo_list": c.termo_list,
                    "narrative_summary": c.narrative_summary,
                }
                for c in result.strong_clusters
            ],
        }


# ═══════════════════════════════════════════════════════════════════════
# SUPABASE INTEGRATION
# ═══════════════════════════════════════════════════════════════════════

def fetch_signals_from_supabase(
    limit: int = 500,
    exclude_internal: bool = True,
) -> List[Dict]:
    """
    Fetch cultural signals from Supabase for clustering.
    
    Returns:
        list of signal dicts with id, termo, plataforma, circulo, score, raw_data, ts
    """
    import requests
    
    sb_url = os.environ.get(
        "SUPABASE_URL", "https://wsizqmnnicpgblopmxyv.supabase.co"
    )
    sb_key = os.environ.get("SUPABASE_SERVICE_KEY", os.environ.get("SUPABASE_KEY", ""))
    
    if not sb_key:
        raise ValueError("SUPABASE_SERVICE_KEY not set in environment")
    
    headers = {
        "apikey": sb_key,
        "Authorization": f"Bearer {sb_key}",
    }
    
    url = f"{sb_url}/rest/v1/cultural_signals"
    params = {
        "select": "id,termo,plataforma,circulo,score,regiao,raw_data,ts",
        "limit": str(limit),
        "order": "id.desc",
    }
    
    if exclude_internal:
        params["plataforma"] = "neq.internal"
    
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    signals = resp.json()
    
    logger.info(f"📥 Fetched {len(signals)} signals from Supabase")
    return signals


def log_clustering_to_supabase(
    result_dict: Dict,
    table: str = "training_logs",
) -> bool:
    """
    Log clustering results to Supabase training_logs table.
    """
    import requests
    
    sb_url = os.environ.get(
        "SUPABASE_URL", "https://wsizqmnnicpgblopmxyv.supabase.co"
    )
    sb_key = os.environ.get("SUPABASE_SERVICE_KEY", os.environ.get("SUPABASE_KEY", ""))
    
    if not sb_key:
        logger.warning("⚠️ No SUPABASE_SERVICE_KEY — skipping log")
        return False
    
    headers = {
        "apikey": sb_key,
        "Authorization": f"Bearer {sb_key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }
    
    payload = {
        "experiment": "S3.4_ward_clustering",
        "metrics": {
            "n_signals": result_dict["n_signals"],
            "n_clusters": result_dict["n_clusters"],
            "n_strong": result_dict["n_strong"],
            "embedding_mode": result_dict["embedding_mode"],
            "silhouette_score": result_dict["silhouette_score"],
            "calinski_harabasz": result_dict["calinski_harabasz"],
            "strong_cluster_summaries": [
                {
                    "id": sc["cluster_id"],
                    "strength": sc["signal_strength"],
                    "platforms": sc["distinct_platforms"],
                    "termos": sc["termo_list"],
                }
                for sc in result_dict["strong_clusters"]
            ],
        },
        "created_at": datetime.utcnow().isoformat(),
    }
    
    url = f"{sb_url}/rest/v1/{table}"
    try:
        resp = requests.post(url, headers=headers, json=payload)
        if resp.status_code in (200, 201):
            logger.info(f"📤 Logged to Supabase {table}")
            return True
        else:
            logger.warning(f"⚠️ Supabase log: HTTP {resp.status_code} — {resp.text[:200]}")
            return False
    except Exception as e:
        logger.warning(f"⚠️ Supabase log failed: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════
# STANDALONE TEST / MODULE CHECK
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    print("=" * 65)
    print("  S3.4 — Signal Aggregator (Ward Clustering): module check")
    print("=" * 65)
    
    # Quick check with synthetic data
    from sklearn.datasets import make_blobs
    
    X, y_true = make_blobs(n_samples=50, centers=5, n_features=10, random_state=42)
    
    # Simulate signals
    fake_signals = []
    plats = ["YouTube", "Reddit", "NewsAPI", "Spotify", "Meetup", "Instagram/Threads", "IBGE"]
    termos_fake = ["funk", "samba", "pagode", "trap", "sertanejo"]
    
    for i in range(len(X)):
        fake_signals.append({
            "id": i + 1,
            "termo": termos_fake[y_true[i] % len(termos_fake)],
            "plataforma": plats[i % len(plats)],
            "circulo": "música",
            "score": 0.7,
            "raw_data": {
                "momentum": float(np.random.uniform(10, 90)),
                "sentiment": float(np.random.uniform(0.3, 0.9)),
                "narrativa": f"Sinal cultural sobre {termos_fake[y_true[i] % len(termos_fake)]}",
            },
        })
    
    # Test with TF-IDF (no BERT dependency for module check)
    agg = SignalAggregator(embed_mode="tfidf_fallback", cluster_method="silhouette")
    result = agg.aggregate(fake_signals)
    
    print(f"\n  Signals:  {result.n_signals}")
    print(f"  Clusters: {result.n_clusters}")
    print(f"  Strong:   {result.n_strong}")
    print(f"  Silhouette: {result.silhouette_score:.4f}")
    print(f"  Calinski-Harabasz: {result.calinski_harabasz:.1f}")
    
    for sc in result.strong_clusters[:3]:
        print(f"\n  🔥 Cluster {sc.cluster_id}: strength={sc.signal_strength:.2f}")
        print(f"     Platforms: {sc.distinct_platforms} ({sc.platform_list})")
        print(f"     Termos: {sc.termo_list}")
        print(f"     {sc.narrative_summary[:120]}...")
    
    print(f"\n  ✅ Module loads OK — {len(result.clusters)} clusters built")
