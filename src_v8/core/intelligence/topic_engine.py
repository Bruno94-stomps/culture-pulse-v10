"""
core/topic_engine.py — INT-2 FASE 2
=====================================
Slim topic modeling engine for the Worker pipeline.

Reactivated from: dormant/core/hierarchical_topic_modeler.py (416 lines)
Slim version: ~280 lines, incremental batch fit, single-signal predict.

Purpose:
  1. Fit macro-topics on accumulated signal texts (LDA via sklearn)
  2. Predict topic assignment for individual signals in Worker
  3. Expose current topic hierarchy via API

Worker integration:
  topic_enricher at priority=48 — last enricher, adds topic assignment
  signal["topic_assignment"] = {macro_topic, macro_label, top_terms, confidence}

API integration:
  GET /api/v8/topics          — current topic hierarchy
  GET /api/v8/topics/stats    — modeler stats
"""
from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

import numpy as np

logger = logging.getLogger(__name__)

# ── sklearn components ───────────────────────────────────────────────────
try:
    from sklearn.decomposition import LatentDirichletAllocation
    from sklearn.feature_extraction.text import CountVectorizer

    _HAS_SKLEARN = True
except ImportError:
    _HAS_SKLEARN = False
    logger.warning("sklearn not available — TopicEngine will use fallback mode")


# ── Constants ────────────────────────────────────────────────────────────

DEFAULT_N_TOPICS = 8
MIN_DOCS_TO_FIT = 20
MAX_BUFFER_SIZE = 2000
TOP_TERMS_PER_TOPIC = 10
REFIT_INTERVAL = 50  # refit every N new documents

# Portuguese stopwords (cultural context)
STOPWORDS_PT: Set[str] = {
    "é", "do", "da", "de", "para", "com", "em", "no", "na", "um", "uma",
    "esse", "essa", "isso", "aquele", "aquela", "muito", "mais", "bem",
    "já", "ainda", "só", "também", "mas", "porque", "quando", "onde", "vai",
    "ter", "ser", "está", "estão", "foram", "foi", "como", "por", "sobre",
    "que", "não", "se", "ao", "os", "as", "dos", "das", "nos", "nas",
    "pelo", "pela", "pelos", "pelas", "entre", "até", "depois", "antes",
    "pode", "tem", "todo", "toda", "todos", "todas", "cada", "outro", "outra",
}


# ── Dataclasses ──────────────────────────────────────────────────────────

@dataclass
class MacroTopic:
    """One macro-level topic."""

    topic_id: int
    label: str
    top_terms: List[str]
    top_weights: List[float]
    n_documents: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic_id": self.topic_id,
            "label": self.label,
            "top_terms": self.top_terms,
            "top_weights": [round(w, 4) for w in self.top_weights],
            "n_documents": self.n_documents,
        }


@dataclass
class TopicAssignment:
    """Topic assignment for a single signal."""

    macro_topic: int
    macro_label: str
    top_terms: List[str]
    confidence: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "macro_topic": self.macro_topic,
            "macro_label": self.macro_label,
            "top_terms": self.top_terms,
            "confidence": round(self.confidence, 4),
        }


# ── Engine ───────────────────────────────────────────────────────────────

class TopicEngine:
    """
    Lightweight topic modeling engine with incremental buffering.

    Usage:
        engine = TopicEngine(n_topics=8)
        engine.add_document("funk carioca baile")
        assignment = engine.predict("novo hit funk")
    """

    def __init__(self, n_topics: int = DEFAULT_N_TOPICS) -> None:
        self.n_topics = n_topics
        self._buffer: List[str] = []
        self._vectorizer: Optional[Any] = None  # CountVectorizer
        self._lda: Optional[Any] = None  # LatentDirichletAllocation
        self._topics: List[MacroTopic] = []
        self._fitted_at: Optional[str] = None
        self._fit_count: int = 0
        self._docs_since_last_fit: int = 0
        self._doc_assignments: Dict[int, int] = {}  # doc_idx → topic_id
        logger.info("TopicEngine initialized: n_topics=%d, sklearn=%s", n_topics, _HAS_SKLEARN)

    # ── Buffer management ────────────────────────────────────────────────

    def add_document(self, text: str) -> None:
        """Add document text to buffer. Triggers refit if threshold reached."""
        if not text or not text.strip():
            return
        self._buffer.append(text.strip().lower())
        self._docs_since_last_fit += 1

        # Trim buffer if over limit
        if len(self._buffer) > MAX_BUFFER_SIZE:
            self._buffer = self._buffer[-MAX_BUFFER_SIZE:]

        # Auto-refit
        if (
            _HAS_SKLEARN
            and len(self._buffer) >= MIN_DOCS_TO_FIT
            and self._docs_since_last_fit >= REFIT_INTERVAL
        ):
            self.fit()

    # ── Fit ──────────────────────────────────────────────────────────────

    def fit(self) -> Dict[str, Any]:
        """
        Fit LDA on buffered documents.

        Returns dict with topic summary or error status.
        """
        if not _HAS_SKLEARN:
            return {"status": "sklearn_unavailable"}

        n = len(self._buffer)
        if n < MIN_DOCS_TO_FIT:
            return {"status": "insufficient_docs", "n_docs": n, "min_required": MIN_DOCS_TO_FIT}

        try:
            self._vectorizer = CountVectorizer(
                max_features=1000,
                stop_words=list(STOPWORDS_PT),
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.95,
            )
            X = self._vectorizer.fit_transform(self._buffer)

            actual_topics = min(self.n_topics, n - 1)
            self._lda = LatentDirichletAllocation(
                n_components=actual_topics,
                random_state=42,
                max_iter=30,
                learning_method="online",
            )
            doc_topic_dist = self._lda.fit_transform(X)

            # Extract topics
            feature_names = self._vectorizer.get_feature_names_out()
            topics: List[MacroTopic] = []

            # Count documents per topic
            doc_assignments = np.argmax(doc_topic_dist, axis=1)
            topic_counts = defaultdict(int)
            for t in doc_assignments:
                topic_counts[int(t)] += 1

            for idx in range(actual_topics):
                component = self._lda.components_[idx]
                top_indices = component.argsort()[-TOP_TERMS_PER_TOPIC:][::-1]
                top_terms = [feature_names[i] for i in top_indices]
                top_weights = [float(component[i]) for i in top_indices]

                topics.append(MacroTopic(
                    topic_id=idx,
                    label=f"Topic-{idx}",
                    top_terms=top_terms,
                    top_weights=top_weights,
                    n_documents=topic_counts.get(idx, 0),
                ))

            self._topics = topics
            self._fitted_at = datetime.utcnow().isoformat()
            self._fit_count += 1
            self._docs_since_last_fit = 0

            logger.info("TopicEngine fit: %d topics from %d docs (fit #%d)", actual_topics, n, self._fit_count)

            return {
                "status": "ok",
                "n_topics": actual_topics,
                "n_docs": n,
                "fit_count": self._fit_count,
            }

        except Exception as exc:
            logger.warning("TopicEngine.fit error: %s", exc)
            return {"status": "error", "message": str(exc)}

    # ── Predict ──────────────────────────────────────────────────────────

    def predict(self, text: str) -> TopicAssignment:
        """
        Assign a single document/signal to the most likely topic.

        Returns TopicAssignment (with fallback if model not fitted).
        """
        if self._lda is None or self._vectorizer is None:
            return TopicAssignment(
                macro_topic=-1,
                macro_label="not_fitted",
                top_terms=[],
                confidence=0.0,
            )

        try:
            X = self._vectorizer.transform([text.lower()])
            dist = self._lda.transform(X)[0]
            top_idx = int(np.argmax(dist))
            confidence = float(dist[top_idx])

            topic = self._topics[top_idx] if top_idx < len(self._topics) else None

            return TopicAssignment(
                macro_topic=top_idx,
                macro_label=topic.label if topic else f"Topic-{top_idx}",
                top_terms=topic.top_terms[:5] if topic else [],
                confidence=confidence,
            )
        except Exception as exc:
            logger.warning("TopicEngine.predict error: %s", exc)
            return TopicAssignment(
                macro_topic=-1,
                macro_label="error",
                top_terms=[],
                confidence=0.0,
            )

    # ── Hierarchy ────────────────────────────────────────────────────────

    def get_hierarchy(self) -> Dict[str, Any]:
        """Return current topic hierarchy for API/dashboard."""
        return {
            "n_topics": len(self._topics),
            "total_documents": len(self._buffer),
            "fitted_at": self._fitted_at,
            "fit_count": self._fit_count,
            "topics": [t.to_dict() for t in self._topics],
        }

    # ── Stats ────────────────────────────────────────────────────────────

    def get_stats(self) -> Dict[str, Any]:
        """Return engine stats."""
        return {
            "n_topics": self.n_topics,
            "buffer_size": len(self._buffer),
            "is_fitted": self._lda is not None,
            "fitted_at": self._fitted_at,
            "fit_count": self._fit_count,
            "docs_since_last_fit": self._docs_since_last_fit,
            "min_docs_to_fit": MIN_DOCS_TO_FIT,
            "refit_interval": REFIT_INTERVAL,
            "sklearn_available": _HAS_SKLEARN,
        }

    @property
    def is_fitted(self) -> bool:
        return self._lda is not None

    @property
    def buffer_size(self) -> int:
        return len(self._buffer)


# ── Module singleton ─────────────────────────────────────────────────────

_engine: Optional[TopicEngine] = None


def get_topic_engine() -> TopicEngine:
    """Module-level singleton."""
    global _engine
    if _engine is None:
        _engine = TopicEngine()
    return _engine
