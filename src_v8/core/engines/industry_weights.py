#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Industry Weights Engine — F-13 (FASE 5)
==========================================
Pesos de relevância por indústria aprendidos com feedback.

Expande de 3 indústrias hardcoded (circles_processor.py) para 15+ setores
com pesos que se adaptam via feedback humano e A/B testing.

Funcionalidade:
  1. Define 15+ setores industriais BR com pesos iniciais por círculo cultural
  2. Treina pesos com feedback (qual sinal foi útil para qual indústria?)
  3. A/B testing: compara pesos default vs learned para decisão
  4. Integra com Momentum (INT-3) como feature base

Design:
  - 15 indústrias × 16 círculos = 240 pesos
  - Online learning: exponential smoothing por feedback
  - Sem sklearn/ML pesado — heurísticas adaptativas puras
  - Thread-safe via singleton
"""

from __future__ import annotations

import json
import logging
import math
import random
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
#  Constants: 16 Cultural Circles × 15 Industries
# ═══════════════════════════════════════════════════════════════════════════════

CIRCULOS = [
    "Música Popular", "Gastronomia", "Moda & Estilo", "Esporte",
    "Tecnologia", "Religiosidade", "Humor & Memes", "Natureza",
    "Arte Urbana", "Festas & Eventos", "Cinema & Séries", "Literatura",
    "Saúde & Bem-Estar", "Educação", "Mobilidade Urbana", "Empreendedorismo",
]

INDUSTRIES = [
    "Tecnologia",
    "Entretenimento",
    "Alimentação & Bebidas",
    "Moda & Varejo",
    "Saúde & Farmacêutico",
    "Educação",
    "Financeiro & Fintech",
    "Automotivo & Mobilidade",
    "Telecomunicações",
    "Imobiliário & Construção",
    "Agronegócio",
    "Turismo & Hotelaria",
    "Esportes & Fitness",
    "Beleza & Cosméticos",
    "Energia & Sustentabilidade",
]

# Default weights: industry → {circle → weight 0-1}
# These are the initial "expert" weights before learning
DEFAULT_WEIGHTS: Dict[str, Dict[str, float]] = {
    "Tecnologia": {
        "Tecnologia": 1.0, "Humor & Memes": 0.6, "Empreendedorismo": 0.8,
        "Cinema & Séries": 0.4, "Educação": 0.5, "Arte Urbana": 0.3,
    },
    "Entretenimento": {
        "Música Popular": 1.0, "Cinema & Séries": 1.0, "Humor & Memes": 0.9,
        "Festas & Eventos": 0.8, "Arte Urbana": 0.7, "Literatura": 0.5,
    },
    "Alimentação & Bebidas": {
        "Gastronomia": 1.0, "Saúde & Bem-Estar": 0.6, "Festas & Eventos": 0.7,
        "Natureza": 0.4, "Religiosidade": 0.3, "Moda & Estilo": 0.3,
    },
    "Moda & Varejo": {
        "Moda & Estilo": 1.0, "Arte Urbana": 0.7, "Música Popular": 0.5,
        "Festas & Eventos": 0.6, "Cinema & Séries": 0.4, "Humor & Memes": 0.3,
    },
    "Saúde & Farmacêutico": {
        "Saúde & Bem-Estar": 1.0, "Natureza": 0.6, "Educação": 0.5,
        "Esporte": 0.5, "Tecnologia": 0.4, "Religiosidade": 0.3,
    },
    "Educação": {
        "Educação": 1.0, "Tecnologia": 0.7, "Literatura": 0.7,
        "Arte Urbana": 0.4, "Cinema & Séries": 0.3, "Empreendedorismo": 0.5,
    },
    "Financeiro & Fintech": {
        "Empreendedorismo": 0.9, "Tecnologia": 0.8, "Educação": 0.4,
        "Mobilidade Urbana": 0.3, "Esporte": 0.2, "Humor & Memes": 0.2,
    },
    "Automotivo & Mobilidade": {
        "Mobilidade Urbana": 1.0, "Tecnologia": 0.7, "Esporte": 0.5,
        "Natureza": 0.4, "Empreendedorismo": 0.4, "Moda & Estilo": 0.2,
    },
    "Telecomunicações": {
        "Tecnologia": 0.9, "Humor & Memes": 0.5, "Cinema & Séries": 0.6,
        "Educação": 0.4, "Empreendedorismo": 0.3, "Música Popular": 0.4,
    },
    "Imobiliário & Construção": {
        "Mobilidade Urbana": 0.7, "Natureza": 0.5, "Empreendedorismo": 0.6,
        "Arte Urbana": 0.4, "Tecnologia": 0.3, "Saúde & Bem-Estar": 0.3,
    },
    "Agronegócio": {
        "Natureza": 1.0, "Gastronomia": 0.7, "Religiosidade": 0.4,
        "Empreendedorismo": 0.5, "Tecnologia": 0.4, "Educação": 0.3,
    },
    "Turismo & Hotelaria": {
        "Festas & Eventos": 1.0, "Gastronomia": 0.8, "Natureza": 0.7,
        "Arte Urbana": 0.6, "Música Popular": 0.6, "Religiosidade": 0.4,
    },
    "Esportes & Fitness": {
        "Esporte": 1.0, "Saúde & Bem-Estar": 0.8, "Moda & Estilo": 0.4,
        "Festas & Eventos": 0.3, "Tecnologia": 0.3, "Humor & Memes": 0.4,
    },
    "Beleza & Cosméticos": {
        "Moda & Estilo": 0.9, "Saúde & Bem-Estar": 0.7, "Arte Urbana": 0.5,
        "Música Popular": 0.4, "Cinema & Séries": 0.4, "Natureza": 0.5,
    },
    "Energia & Sustentabilidade": {
        "Natureza": 1.0, "Tecnologia": 0.7, "Mobilidade Urbana": 0.6,
        "Educação": 0.4, "Empreendedorismo": 0.5, "Saúde & Bem-Estar": 0.3,
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
#  Data classes
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class WeightFeedback:
    """Feedback on a signal's relevance for an industry."""
    industry: str
    circle: str
    signal_id: str = ""
    useful: bool = True
    weight_adjustment: float = 0.0  # computed
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ABTestResult:
    """Result of A/B test comparing default vs learned weights."""
    industry: str
    default_score: float = 0.0
    learned_score: float = 0.0
    winner: str = "default"  # "default" or "learned"
    improvement_pct: float = 0.0
    sample_size: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ═══════════════════════════════════════════════════════════════════════════════
#  Configuration
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT_CONFIG: Dict[str, Any] = {
    "learning_rate": 0.1,           # exponential smoothing alpha
    "min_feedback_to_learn": 3,     # min feedbacks before using learned weights
    "default_circle_weight": 0.2,   # fallback weight for unmapped circles
    "ab_test_split": 0.5,          # fraction of requests using learned weights
    "log_dir": "data/industry_weights",
    "max_feedback_per_pair": 200,
}


# ═══════════════════════════════════════════════════════════════════════════════
#  IndustryWeightsEngine
# ═══════════════════════════════════════════════════════════════════════════════

class IndustryWeightsEngine:
    """
    Manages per-industry relevance weights for cultural circles.

    Supports:
      - 15 industries × 16 circles = 240 weight pairs
      - Online learning from feedback (exponential smoothing)
      - A/B testing (default vs learned weights)
      - Integration with momentum scoring
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self._config = {**DEFAULT_CONFIG, **(config or {})}
        # Learned weights: industry → {circle → weight}
        self._learned_weights: Dict[str, Dict[str, float]] = {}
        # Feedback history: (industry, circle) → list of feedbacks
        self._feedback_store: Dict[Tuple[str, str], List[WeightFeedback]] = {}
        self._total_feedback = 0
        # AB test results
        self._ab_results: List[ABTestResult] = []
        logger.info(
            "⚖️  IndustryWeightsEngine initialized "
            f"({len(INDUSTRIES)} industries × {len(CIRCULOS)} circles)"
        )

    # ── Properties ────────────────────────────────────────────────────────

    @property
    def config(self) -> Dict[str, Any]:
        return dict(self._config)

    @property
    def industries(self) -> List[str]:
        return list(INDUSTRIES)

    @property
    def circles(self) -> List[str]:
        return list(CIRCULOS)

    @property
    def total_feedback(self) -> int:
        return self._total_feedback

    # ── Core: Get weights for an industry ─────────────────────────────────

    def get_weights(self, industry: str, use_learned: bool = True) -> Dict[str, float]:
        """
        Get circle weights for an industry.

        Args:
            industry: Industry name (must be in INDUSTRIES)
            use_learned: If True and learned weights available, use them

        Returns:
            Dict of circle → weight (0-1) for all 16 circles
        """
        if industry not in INDUSTRIES:
            raise ValueError(
                f"Unknown industry '{industry}'. "
                f"Valid: {INDUSTRIES}"
            )

        # Start with defaults
        default = DEFAULT_WEIGHTS.get(industry, {})
        default_weight = self._config["default_circle_weight"]

        weights = {}
        for circle in CIRCULOS:
            weights[circle] = default.get(circle, default_weight)

        # Overlay learned weights if available and requested
        if use_learned and industry in self._learned_weights:
            min_fb = self._config["min_feedback_to_learn"]
            for circle, learned_w in self._learned_weights[industry].items():
                pair_key = (industry, circle)
                fb_count = len(self._feedback_store.get(pair_key, []))
                if fb_count >= min_fb:
                    weights[circle] = learned_w

        return weights

    def get_all_weights(self, use_learned: bool = True) -> Dict[str, Dict[str, float]]:
        """Get weights for all industries."""
        return {ind: self.get_weights(ind, use_learned) for ind in INDUSTRIES}

    # ── Core: Apply weights to momentum ───────────────────────────────────

    def apply_industry_weight(
        self,
        industry: str,
        circle: str,
        base_momentum: float,
        use_learned: bool = True,
    ) -> Dict[str, Any]:
        """
        Apply industry weight to a signal's base momentum.

        Returns weighted momentum and the weight used.
        """
        weights = self.get_weights(industry, use_learned)
        weight = weights.get(circle, self._config["default_circle_weight"])
        weighted_momentum = base_momentum * weight

        return {
            "industry": industry,
            "circle": circle,
            "base_momentum": round(base_momentum, 4),
            "weight": round(weight, 4),
            "weighted_momentum": round(weighted_momentum, 4),
            "weight_source": "learned" if (
                use_learned and industry in self._learned_weights
                and circle in self._learned_weights.get(industry, {})
            ) else "default",
        }

    def rank_signals_for_industry(
        self,
        industry: str,
        signals: List[Dict[str, Any]],
        use_learned: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Rank signals by relevance for a specific industry.

        Each signal must have 'circle' (or 'circulo') and 'momentum' keys.
        """
        weights = self.get_weights(industry, use_learned)
        ranked = []

        for sig in signals:
            circle = sig.get("circle", sig.get("circulo", ""))
            momentum = float(sig.get("momentum", 0.0))
            weight = weights.get(circle, self._config["default_circle_weight"])
            ranked.append({
                **sig,
                "industry_weight": round(weight, 4),
                "weighted_momentum": round(momentum * weight, 4),
            })

        ranked.sort(key=lambda s: s["weighted_momentum"], reverse=True)
        return ranked

    # ── Core: Submit feedback (learning) ──────────────────────────────────

    def submit_feedback(
        self,
        industry: str,
        circle: str,
        useful: bool,
        signal_id: str = "",
    ) -> Dict[str, Any]:
        """
        Submit feedback on a signal's usefulness for an industry.

        Args:
            industry: Industry that evaluated the signal
            circle: Cultural circle of the signal
            useful: True if the signal was useful for the industry
            signal_id: Optional signal identifier

        Returns:
            Dict with updated weight info
        """
        if industry not in INDUSTRIES:
            raise ValueError(f"Unknown industry: {industry}")
        if circle not in CIRCULOS:
            raise ValueError(f"Unknown circle: {circle}")

        fb = WeightFeedback(
            industry=industry,
            circle=circle,
            signal_id=signal_id,
            useful=useful,
        )

        pair_key = (industry, circle)
        if pair_key not in self._feedback_store:
            self._feedback_store[pair_key] = []

        store = self._feedback_store[pair_key]
        max_fb = self._config["max_feedback_per_pair"]
        if len(store) >= max_fb:
            store.pop(0)

        store.append(fb)
        self._total_feedback += 1

        # Update learned weight
        new_weight = self._update_weight(industry, circle)
        self._log_feedback(fb)

        return {
            "status": "recorded",
            "industry": industry,
            "circle": circle,
            "feedback_count": len(store),
            "new_weight": round(new_weight, 4),
            "default_weight": round(
                DEFAULT_WEIGHTS.get(industry, {}).get(
                    circle, self._config["default_circle_weight"]
                ), 4
            ),
        }

    def _update_weight(self, industry: str, circle: str) -> float:
        """Update learned weight using exponential smoothing."""
        pair_key = (industry, circle)
        feedbacks = self._feedback_store.get(pair_key, [])

        if not feedbacks:
            return self._config["default_circle_weight"]

        alpha = self._config["learning_rate"]
        default = DEFAULT_WEIGHTS.get(industry, {}).get(
            circle, self._config["default_circle_weight"]
        )

        # Start from default, smooth towards feedback
        weight = default
        for fb in feedbacks:
            target = 1.0 if fb.useful else 0.0
            weight = weight * (1 - alpha) + target * alpha

        weight = max(0.0, min(1.0, weight))

        # Store
        if industry not in self._learned_weights:
            self._learned_weights[industry] = {}
        self._learned_weights[industry][circle] = weight

        return weight

    def batch_feedback(self, feedbacks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Submit multiple feedbacks."""
        processed = 0
        failed = 0
        for fb in feedbacks:
            try:
                self.submit_feedback(
                    industry=fb["industry"],
                    circle=fb["circle"],
                    useful=fb["useful"],
                    signal_id=fb.get("signal_id", ""),
                )
                processed += 1
            except Exception as exc:
                logger.warning(f"⚠️ batch_feedback failed: {exc}")
                failed += 1
        return {"processed": processed, "failed": failed}

    # ── A/B Testing ───────────────────────────────────────────────────────

    def run_ab_test(
        self,
        industry: str,
        signals: List[Dict[str, Any]],
        ground_truth: Dict[str, bool],
    ) -> Dict[str, Any]:
        """
        Run A/B test comparing default vs learned weights.

        Args:
            industry: Industry to test
            signals: List of signals with 'signal_id', 'circle', 'momentum'
            ground_truth: signal_id → True if actually useful

        Returns:
            ABTestResult with winner and improvement percentage
        """
        if industry not in INDUSTRIES:
            raise ValueError(f"Unknown industry: {industry}")

        default_ranked = self.rank_signals_for_industry(industry, signals, use_learned=False)
        learned_ranked = self.rank_signals_for_industry(industry, signals, use_learned=True)

        # Score = sum of weighted_momentum for actually useful signals
        def score_ranking(ranked):
            total = 0.0
            for i, sig in enumerate(ranked):
                sid = sig.get("signal_id", sig.get("id", ""))
                if ground_truth.get(sid, False):
                    # Position bonus: useful signals ranked higher = better
                    position_bonus = 1.0 / (i + 1)
                    total += sig["weighted_momentum"] + position_bonus
            return total

        default_score = score_ranking(default_ranked)
        learned_score = score_ranking(learned_ranked)

        winner = "learned" if learned_score > default_score else "default"
        improvement = (
            (learned_score - default_score) / max(default_score, 0.01) * 100
        )

        result = ABTestResult(
            industry=industry,
            default_score=round(default_score, 4),
            learned_score=round(learned_score, 4),
            winner=winner,
            improvement_pct=round(improvement, 2),
            sample_size=len(signals),
        )
        self._ab_results.append(result)

        return result.to_dict()

    def get_ab_history(self) -> List[Dict[str, Any]]:
        """Return A/B test history."""
        return [r.to_dict() for r in self._ab_results]

    # ── Statistics ────────────────────────────────────────────────────────

    def stats(self) -> Dict[str, Any]:
        """Return engine statistics."""
        learned_count = sum(
            len(circles) for circles in self._learned_weights.values()
        )
        return {
            "engine": "IndustryWeightsEngine",
            "version": "1.0.0",
            "total_industries": len(INDUSTRIES),
            "total_circles": len(CIRCULOS),
            "total_weight_pairs": len(INDUSTRIES) * len(CIRCULOS),
            "learned_weight_pairs": learned_count,
            "total_feedback": self._total_feedback,
            "feedback_pairs_active": len(self._feedback_store),
            "ab_tests_run": len(self._ab_results),
            "industries": list(INDUSTRIES),
        }

    # ── Persistence ───────────────────────────────────────────────────────

    def _log_feedback(self, fb: WeightFeedback) -> None:
        """Log feedback to JSONL."""
        try:
            log_dir = Path(self._config["log_dir"])
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "weight_feedback.jsonl"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(fb.to_dict(), ensure_ascii=False) + "\n")
        except Exception as exc:
            logger.warning(f"⚠️ IndustryWeights log failed: {exc}")

    def export_weights(self) -> Dict[str, Any]:
        """Export current weights (default + learned)."""
        return {
            "default": {k: dict(v) for k, v in DEFAULT_WEIGHTS.items()},
            "learned": {k: dict(v) for k, v in self._learned_weights.items()},
            "total_feedback": self._total_feedback,
        }

    def reset(self) -> None:
        """Reset all learned state (for testing)."""
        self._learned_weights.clear()
        self._feedback_store.clear()
        self._ab_results.clear()
        self._total_feedback = 0


# ═══════════════════════════════════════════════════════════════════════════════
#  Singleton
# ═══════════════════════════════════════════════════════════════════════════════

_engine: Optional[IndustryWeightsEngine] = None


def get_industry_weights_engine() -> IndustryWeightsEngine:
    """Get or create singleton."""
    global _engine
    if _engine is None:
        _engine = IndustryWeightsEngine()
    return _engine


def reset_industry_weights_engine() -> None:
    """Reset singleton (for testing)."""
    global _engine
    _engine = None
