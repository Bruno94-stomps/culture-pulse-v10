#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unknown Circle Detector — Culture Pulse V9.1  (Sprint S4.3)
==============================================================
Engine que detecta candidatos a novos círculos culturais a partir de
sinais classificados como "emergente_desconhecido" pelo circles_processor.

Fluxo:
  1. Sinais com max_circle_score < threshold → marcados "emergente_desconhecido"
  2. Acumulados em Redis list `unknown_signals_queue`
  3. Periodicamente (ou on-demand): Ward clustering sobre TF-IDF dos termos
  4. Clusters com ≥ MIN_CLUSTER_SIZE sinais → candidatos a novo círculo
  5. Alerta: "🆕 Possível novo círculo cultural detectado: [tema]"

Integração:
  - Worker: registrado como enricher (priority=15, após circles mas antes de tfidf)
  - API:    GET  /api/v8/circles/unknown     → lista sinais desconhecidos
            GET  /api/v8/circles/candidates  → clusters candidatos
            POST /api/v8/circles/promote     → promover cluster a círculo
  - Dashboard: painel com contagem, clusters, botão de promoção

Dependências:
  - scikit-learn (TfidfVectorizer, AgglomerativeClustering)
  - numpy
  - redis.asyncio (para fila de sinais)
"""

from __future__ import annotations

import json
import logging
import os
import time
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# ── Constantes ────────────────────────────────────────────────────────────────

UNKNOWN_QUEUE_KEY = "unknown_signals_queue"
UNKNOWN_QUEUE_MAX = 1000          # máx sinais na fila
CANDIDATES_KEY = "unknown_circle_candidates"
MIN_CLUSTER_SIZE = 10             # mínimo de sinais para formar candidato
MAX_CLUSTERS = 15                 # máximo de clusters a tentar
CANDIDATE_TTL = 86400 * 7        # 7 dias de TTL para candidatos

# ── Redis imports ────────────────────────────────────────────────────────────

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    try:
        import aioredis  # type: ignore
        REDIS_AVAILABLE = True
    except ImportError:
        REDIS_AVAILABLE = False

# ── sklearn imports (lazy) ───────────────────────────────────────────────────

_SKLEARN_AVAILABLE = False
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import AgglomerativeClustering
    from sklearn.metrics import silhouette_score
    _SKLEARN_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ scikit-learn não disponível — clustering desabilitado")

# ── HDBSCAN import (optional upgrade) ───────────────────────────────────────

_HDBSCAN_AVAILABLE = False
try:
    import hdbscan as _hdbscan
    _HDBSCAN_AVAILABLE = True
except ImportError:
    pass  # silent — falls back to Ward


# ── Dataclasses ──────────────────────────────────────────────────────────────

@dataclass
class ClusterCandidate:
    """Candidato a novo círculo cultural."""
    cluster_id: int
    size: int                         # número de sinais no cluster
    top_terms: List[str]              # termos mais frequentes
    suggested_name: str               # nome sugerido baseado nos termos
    avg_score: float                  # score médio dos sinais
    platforms: List[str]              # plataformas de origem
    sample_texts: List[str]           # textos de amostra (até 5)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "cluster_id": self.cluster_id,
            "size": self.size,
            "top_terms": self.top_terms,
            "suggested_name": self.suggested_name,
            "avg_score": self.avg_score,
            "platforms": self.platforms,
            "sample_texts": self.sample_texts[:5],
            "created_at": self.created_at,
        }


@dataclass
class UnknownSignalEntry:
    """Sinal armazenado na fila de desconhecidos."""
    termo: str
    texto: str
    plataforma: str
    score: float
    top_scores: List[Tuple[str, float]]
    rejection_reason: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "termo": self.termo,
            "texto": self.texto,
            "plataforma": self.plataforma,
            "score": self.score,
            "top_scores": self.top_scores,
            "rejection_reason": self.rejection_reason,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "UnknownSignalEntry":
        return cls(
            termo=d.get("termo", ""),
            texto=d.get("texto", ""),
            plataforma=d.get("plataforma", ""),
            score=d.get("score", 0),
            top_scores=d.get("top_scores", []),
            rejection_reason=d.get("rejection_reason", ""),
            timestamp=d.get("timestamp", time.time()),
        )


# ── UnknownCircleDetector ────────────────────────────────────────────────────

class UnknownCircleDetector:
    """
    Detecta candidatos a novos círculos culturais via Ward clustering
    sobre sinais classificados como emergente_desconhecido.
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        min_cluster_size: int = MIN_CLUSTER_SIZE,
        max_clusters: int = MAX_CLUSTERS,
    ):
        self._redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._min_cluster_size = min_cluster_size
        self._max_clusters = max_clusters
        self._redis: Optional[object] = None
        # In-memory fallback quando Redis não está disponível
        self._local_queue: List[UnknownSignalEntry] = []
        self._local_candidates: List[ClusterCandidate] = []

    # ── Redis connection ─────────────────────────────────────────────────

    async def _get_redis(self):
        if self._redis is not None:
            try:
                await self._redis.ping()  # type: ignore
                return self._redis
            except Exception:
                self._redis = None
        if not REDIS_AVAILABLE:
            return None
        try:
            self._redis = await aioredis.from_url(
                self._redis_url, decode_responses=True
            )
            await self._redis.ping()  # type: ignore
            return self._redis
        except Exception:
            return None

    # ── Queue operations ─────────────────────────────────────────────────

    async def push_unknown_signal(self, signal: dict) -> bool:
        """
        Adiciona sinal desconhecido na fila (Redis ou local).
        Chamado pelo enricher quando is_unknown=True.
        """
        entry = UnknownSignalEntry(
            termo=signal.get("termo", ""),
            texto=signal.get("texto", signal.get("descricao", signal.get("termo", ""))),
            plataforma=signal.get("plataforma", "unknown"),
            score=signal.get("circle_score", 0),
            top_scores=signal.get("top_scores", []),
            rejection_reason=signal.get("rejection_reason", ""),
        )

        r = await self._get_redis()
        if r is not None:
            try:
                payload = json.dumps(entry.to_dict(), ensure_ascii=False, default=str)
                await r.lpush(UNKNOWN_QUEUE_KEY, payload)  # type: ignore
                await r.ltrim(UNKNOWN_QUEUE_KEY, 0, UNKNOWN_QUEUE_MAX - 1)  # type: ignore
                logger.debug(f"📥 Sinal desconhecido enfileirado: {entry.termo}")
                return True
            except Exception as exc:
                logger.warning(f"⚠️ Erro ao enfileirar sinal desconhecido: {exc}")

        # Fallback local
        self._local_queue.append(entry)
        if len(self._local_queue) > UNKNOWN_QUEUE_MAX:
            self._local_queue = self._local_queue[-UNKNOWN_QUEUE_MAX:]
        return True

    async def get_unknown_signals(self, count: int = 100) -> List[dict]:
        """Lê sinais desconhecidos da fila."""
        r = await self._get_redis()
        if r is not None:
            try:
                items = await r.lrange(UNKNOWN_QUEUE_KEY, 0, count - 1)  # type: ignore
                return [json.loads(item) for item in items]
            except Exception as exc:
                logger.warning(f"⚠️ Erro ao ler fila de desconhecidos: {exc}")

        return [e.to_dict() for e in self._local_queue[-count:]]

    async def get_queue_size(self) -> int:
        """Retorna tamanho da fila de desconhecidos."""
        r = await self._get_redis()
        if r is not None:
            try:
                return await r.llen(UNKNOWN_QUEUE_KEY)  # type: ignore
            except Exception:
                pass
        return len(self._local_queue)

    # ── Clustering ───────────────────────────────────────────────────────

    async def detect_candidates(self) -> List[ClusterCandidate]:
        """
        Executa clustering sobre sinais acumulados na fila.
        Estratégia:
          1. Se HDBSCAN disponível → usa HDBSCAN (não precisa definir n_clusters,
             detecta ruído, formas arbitrárias, hierárquico).
          2. Senão → Ward AgglomerativeClustering (fallback).
        Retorna lista de ClusterCandidate (clusters com >= min_cluster_size).
        """
        if not _SKLEARN_AVAILABLE:
            logger.warning("⚠️ scikit-learn não disponível — clustering impossível")
            return []

        signals = await self.get_unknown_signals(count=UNKNOWN_QUEUE_MAX)
        if len(signals) < self._min_cluster_size:
            logger.info(
                f"📊 Poucos sinais desconhecidos ({len(signals)}) "
                f"— mínimo {self._min_cluster_size} para clustering"
            )
            return []

        # Construir corpus de textos
        texts = []
        entries = []
        for s in signals:
            text = s.get("texto", "") or s.get("termo", "")
            if text.strip():
                texts.append(text)
                entries.append(s)

        if len(texts) < self._min_cluster_size:
            return []

        # TF-IDF
        try:
            vectorizer = TfidfVectorizer(
                max_features=500,
                stop_words=None,  # PT-BR: usamos vocabulário aberto
                min_df=2,
                max_df=0.95,
                ngram_range=(1, 2),
            )
            tfidf_matrix = vectorizer.fit_transform(texts)
        except ValueError as exc:
            logger.warning(f"⚠️ TF-IDF falhou: {exc}")
            return []

        # Escolher algoritmo de clustering
        n_samples = tfidf_matrix.shape[0]
        dense_matrix = tfidf_matrix.toarray()

        if _HDBSCAN_AVAILABLE and n_samples >= self._min_cluster_size * 2:
            # ── HDBSCAN (preferred) ──────────────────────────────────────
            try:
                clusterer = _hdbscan.HDBSCAN(
                    min_cluster_size=max(self._min_cluster_size, 3),
                    min_samples=max(self._min_cluster_size // 3, 2),
                    metric="euclidean",
                    cluster_selection_method="eom",
                )
                labels = clusterer.fit_predict(dense_matrix)
                probabilities = (
                    clusterer.probabilities_
                    if hasattr(clusterer, "probabilities_")
                    else None
                )
                algo_used = "HDBSCAN"

                # Número de clusters reais (excluindo -1 = ruído)
                unique_labels = set(labels)
                n_clusters_found = len(unique_labels) - (1 if -1 in unique_labels else 0)
                n_noise = int((labels == -1).sum())
                logger.info(
                    f"🔬 HDBSCAN: {n_clusters_found} clusters, "
                    f"{n_noise} ruído de {n_samples} sinais"
                )

                # Silhouette score (se ≥ 2 clusters e pontos não-ruído)
                valid_mask = labels != -1
                if n_clusters_found >= 2 and valid_mask.sum() > n_clusters_found:
                    sil = silhouette_score(dense_matrix[valid_mask], labels[valid_mask])
                    logger.info(f"📊 Silhouette Score: {sil:.3f}")

            except Exception as exc:
                logger.warning(f"⚠️ HDBSCAN falhou, falling back to Ward: {exc}")
                labels, algo_used, probabilities = self._ward_fallback(
                    dense_matrix, n_samples
                )
        else:
            # ── Ward Agglomerative (fallback) ────────────────────────────
            labels, algo_used, probabilities = self._ward_fallback(
                dense_matrix, n_samples
            )

        if labels is None:
            return []

        # Extrair candidatos
        feature_names = vectorizer.get_feature_names_out()
        candidates = self._extract_candidates_from_labels(
            labels, texts, entries, tfidf_matrix, feature_names
        )

        # Persistir candidatos no Redis
        await self._save_candidates(candidates)

        logger.info(
            f"🔍 Clustering ({algo_used}): {len(texts)} sinais → "
            f"{len(set(labels)) - (1 if -1 in labels else 0)} clusters → "
            f"{len(candidates)} candidatos (min_size={self._min_cluster_size})"
        )

        return candidates

    def _ward_fallback(
        self, dense_matrix: np.ndarray, n_samples: int
    ) -> tuple:
        """Fallback Ward AgglomerativeClustering."""
        max_k = min(self._max_clusters, n_samples // max(self._min_cluster_size // 2, 2))
        n_clusters = max(2, min(max_k, 8))
        try:
            clustering = AgglomerativeClustering(
                n_clusters=n_clusters,
                linkage="ward",
            )
            labels = clustering.fit_predict(dense_matrix)
            return labels, "Ward", None
        except Exception as exc:
            logger.warning(f"⚠️ Ward clustering falhou: {exc}")
            return None, "Ward", None

    def _extract_candidates_from_labels(
        self,
        labels: np.ndarray,
        texts: List[str],
        entries: List[dict],
        tfidf_matrix,
        feature_names: np.ndarray,
    ) -> List[ClusterCandidate]:
        """Extrai ClusterCandidate a partir de labels de clustering."""
        candidates = []
        unique_labels = set(labels)

        for cluster_id in unique_labels:
            if cluster_id == -1:
                continue  # skip noise (HDBSCAN)

            mask = labels == cluster_id
            cluster_size = int(mask.sum())

            if cluster_size < self._min_cluster_size:
                continue

            # Textos do cluster
            cluster_texts = [texts[i] for i in range(len(texts)) if mask[i]]
            cluster_entries = [entries[i] for i in range(len(entries)) if mask[i]]

            # Top termos por TF-IDF médio
            cluster_tfidf = tfidf_matrix[mask].toarray().mean(axis=0)
            top_indices = cluster_tfidf.argsort()[-10:][::-1]
            top_terms = [feature_names[i] for i in top_indices if cluster_tfidf[i] > 0]

            # Score médio
            scores = [e.get("score", 0) for e in cluster_entries]
            avg_score = float(np.mean(scores)) if scores else 0.0

            # Plataformas
            platforms = list(set(e.get("plataforma", "") for e in cluster_entries))

            # Nome sugerido: top 2 termos capitalizados
            suggested_name = " & ".join(
                t.title() for t in top_terms[:2]
            ) if top_terms else f"Cluster_{cluster_id}"

            candidate = ClusterCandidate(
                cluster_id=cluster_id,
                size=cluster_size,
                top_terms=top_terms[:10],
                suggested_name=suggested_name,
                avg_score=avg_score,
                platforms=platforms,
                sample_texts=cluster_texts[:5],
            )
            candidates.append(candidate)

        # Ordenar por tamanho (maior primeiro)
        candidates.sort(key=lambda c: c.size, reverse=True)
        return candidates

    async def _save_candidates(self, candidates: List[ClusterCandidate]):
        """Salva candidatos no Redis."""
        r = await self._get_redis()
        payload = json.dumps(
            [c.to_dict() for c in candidates],
            ensure_ascii=False,
            default=str,
        )
        if r is not None:
            try:
                await r.set(CANDIDATES_KEY, payload, ex=CANDIDATE_TTL)  # type: ignore
            except Exception as exc:
                logger.warning(f"⚠️ Erro ao salvar candidatos: {exc}")

        self._local_candidates = candidates

    async def get_candidates(self) -> List[dict]:
        """Retorna candidatos salvos."""
        r = await self._get_redis()
        if r is not None:
            try:
                raw = await r.get(CANDIDATES_KEY)  # type: ignore
                if raw:
                    return json.loads(raw)
            except Exception:
                pass

        return [c.to_dict() for c in self._local_candidates]

    # ── Promotion ────────────────────────────────────────────────────────

    async def promote_candidate(
        self,
        cluster_id: int,
        circle_name: str,
        circle_keywords: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Promove um cluster candidato a novo círculo cultural.

        Na prática, retorna os dados necessários para que o admin
        registre o novo círculo no circles_processor. A promoção
        real é feita pelo admin via configuração.

        Args:
            cluster_id: ID do cluster a promover
            circle_name: Nome escolhido para o novo círculo
            circle_keywords: Keywords (se None, usa top_terms do cluster)

        Returns:
            Dict com dados do novo círculo proposto
        """
        candidates = await self.get_candidates()
        target = None
        for c in candidates:
            if c.get("cluster_id") == cluster_id:
                target = c
                break

        if target is None:
            return {
                "status": "error",
                "message": f"Cluster {cluster_id} não encontrado nos candidatos",
            }

        keywords = circle_keywords or target.get("top_terms", [])

        proposal = {
            "status": "success",
            "proposed_circle": {
                "name": circle_name,
                "keywords": keywords,
                "weight": 0.7,  # peso conservador para novo círculo
                "level": "externos",  # começa como externo
                "description": f"Círculo emergente detectado automaticamente. "
                               f"Baseado em {target['size']} sinais de "
                               f"{', '.join(target.get('platforms', []))}.",
                "source_cluster": {
                    "cluster_id": cluster_id,
                    "size": target["size"],
                    "avg_score": target.get("avg_score", 0),
                    "top_terms": target.get("top_terms", []),
                    "sample_texts": target.get("sample_texts", []),
                },
            },
            "action_required": (
                "Adicionar este círculo em core/circles_processor.py → "
                "_initialize_cultural_circles() → 'externos'"
            ),
        }

        logger.info(
            f"🆕 Cluster {cluster_id} promovido como proposta de novo círculo: "
            f"'{circle_name}' ({target['size']} sinais)"
        )

        return proposal

    # ── Stats ────────────────────────────────────────────────────────────

    async def get_stats(self) -> dict:
        """Retorna estatísticas do detector."""
        queue_size = await self.get_queue_size()
        candidates = await self.get_candidates()
        return {
            "queue_size": queue_size,
            "candidates_count": len(candidates),
            "candidates": candidates,
            "min_cluster_size": self._min_cluster_size,
            "max_clusters": self._max_clusters,
            "sklearn_available": _SKLEARN_AVAILABLE,
            "hdbscan_available": _HDBSCAN_AVAILABLE,
            "clustering_algo": "HDBSCAN" if _HDBSCAN_AVAILABLE else "Ward",
            "redis_available": REDIS_AVAILABLE,
        }


# ── Singleton global ─────────────────────────────────────────────────────────

_detector: Optional[UnknownCircleDetector] = None


def get_unknown_circle_detector() -> UnknownCircleDetector:
    """Retorna singleton do detector."""
    global _detector
    if _detector is None:
        _detector = UnknownCircleDetector()
    return _detector


# ── CLI standalone ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import asyncio

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    )

    async def main():
        detector = get_unknown_circle_detector()
        print("🔍 Unknown Circle Detector — Culture Pulse V9.1 (S4.3)")
        print("=" * 55)

        stats = await detector.get_stats()
        print(f"📊 Fila de desconhecidos: {stats['queue_size']} sinais")
        print(f"🔬 sklearn disponível: {stats['sklearn_available']}")
        print(f"📡 Redis disponível: {stats['redis_available']}")

        if stats["queue_size"] >= MIN_CLUSTER_SIZE:
            print(f"\n🔍 Executando clustering...")
            candidates = await detector.detect_candidates()
            for c in candidates:
                print(
                    f"  🆕 Cluster {c.cluster_id}: {c.size} sinais "
                    f"— '{c.suggested_name}' "
                    f"(avg_score={c.avg_score:.3f})"
                )
                print(f"     Termos: {', '.join(c.top_terms[:5])}")
        else:
            print(f"\n⏳ Poucos sinais — aguardando acumular ≥{MIN_CLUSTER_SIZE}")

    asyncio.run(main())
