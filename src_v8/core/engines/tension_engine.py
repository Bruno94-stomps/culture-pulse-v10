#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tension Engine — Culture Pulse V9.2 (H-1)
=============================================
Slim sync adapter for cultural tension detection, designed to run
as an enricher in the AnalysisWorker pipeline.

Reactivates the dormant ``tension_detection_engine`` concepts in a
Worker-friendly format: **sync**, **single-signal**, **dict→dict**.

Pipeline position: priority 22 (after sentiment/20, before nature/25)

Capabilities:
  - Detect tension types in signal text (keyword-based)
  - Compute tension score (0–1) from keyword density + sentiment polarization
  - Classify tension level: baixa / moderada / alta / crítica
  - Identify specific tension categories: geracional, regional, socioeconômica,
    ideológica, tradicional_vs_moderno, urbano_vs_rural
  - Generate per-signal tension_indicators and micro-alerts

Source: dormant/core/tension_detection_engine.py (1059 lines → slim ~320 lines)
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ── Enums ────────────────────────────────────────────────────────────────────

class TensionLevel(str, Enum):
    BAIXA = "baixa"
    MODERADA = "moderada"
    ALTA = "alta"
    CRITICA = "critica"


class TensionType(str, Enum):
    GERACIONAL = "geracional"
    REGIONAL = "regional"
    SOCIOECONOMICA = "socioeconomica"
    IDEOLOGICA = "ideologica"
    TRADICIONAL_VS_MODERNO = "tradicional_vs_moderno"
    URBANO_VS_RURAL = "urbano_vs_rural"


# ── Dataclasses ──────────────────────────────────────────────────────────────

@dataclass
class TensionResult:
    """Result of tension analysis on a single signal."""
    score: float = 0.0                              # 0–1
    level: TensionLevel = TensionLevel.BAIXA
    types: List[TensionType] = field(default_factory=list)
    keyword_hits: Dict[str, int] = field(default_factory=dict)
    polarization_score: float = 0.0
    alerts: List[str] = field(default_factory=list)
    regional_match: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tension_score": round(self.score, 3),
            "tension_level": self.level.value,
            "tension_types": [t.value for t in self.types],
            "keyword_hits": self.keyword_hits,
            "polarization_score": round(self.polarization_score, 3),
            "tension_alerts": self.alerts,
            "regional_match": self.regional_match,
        }


# ── Keyword dictionaries ────────────────────────────────────────────────────

TENSION_KEYWORDS: Dict[str, List[str]] = {
    "conflito_direto": [
        "contra", "versus", "briga", "discussão", "polêmica", "controvérsia",
        "discordo", "absurdo", "ridículo", "inaceitável", "revoltante",
        "vergonha", "escândalo",
    ],
    "polarizacao": [
        "nós vs eles", "nosso vs deles", "verdadeiro vs falso",
        "certo vs errado", "tradicional vs moderno", "antigo vs novo",
        "esquerda", "direita", "polarização", "dividido",
    ],
    "exclusao_social": [
        "não pertence", "não é nosso", "invasor", "forasteiro",
        "não entende", "não é daqui", "cultura estranha",
        "elitismo", "periferias ignoradas",
    ],
    "resistencia_cultural": [
        "preservar tradição", "manter costume", "resistir mudança",
        "defender cultura", "proteger identidade", "não perder raiz",
        "patrimônio ameaçado",
    ],
    "mudanca_forcada": [
        "imposto", "forçado", "obrigado", "sem escolha",
        "não consultaram", "decisão de cima", "sem participação",
        "gentrificação",
    ],
}

GENERATIONAL_MARKERS: Dict[str, List[str]] = {
    "gen_z": ["cringe", "boomer", "lacração", "problematizar", "cancelar", "tiktok"],
    "millennial": ["networking", "lifestyle", "wellness", "mindfulness", "startup"],
    "gen_x": ["responsabilidade", "disciplina", "compromisso", "experiência"],
    "boomer": ["respeito", "tradição", "hierarquia", "no meu tempo"],
}

REGIONAL_PATTERNS: Dict[str, List[str]] = {
    "Norte": ["amazônia", "floresta", "garimpo", "indígena", "manaus", "belém"],
    "Nordeste": ["nordestino", "seca", "sertão", "forró", "carnaval", "salvador", "recife"],
    "Centro-Oeste": ["agronegócio", "soja", "pantanal", "cerrado", "goiânia", "brasília"],
    "Sudeste": ["periferia", "favela", "gentrificação", "são paulo", "rio de janeiro"],
    "Sul": ["gaúcho", "chimarrão", "colonização", "curitiba", "porto alegre", "separatismo"],
}

# Pares de tensão geracional
_GENERATIONAL_TENSIONS = [
    ("gen_z", "boomer"),
    ("gen_z", "gen_x"),
    ("millennial", "boomer"),
]


# ── Engine ───────────────────────────────────────────────────────────────────

class TensionEngine:
    """
    Lightweight tension detection engine for single-signal enrichment.

    Usage:
        engine = TensionEngine()
        result = engine.analyze(text, sentiment=0.3, circle="Música Popular")
        # result.score, result.level, result.types ...
    """

    # ── Thresholds ───────────────────────────────────────────────────────
    THRESHOLD_LOW = 0.25
    THRESHOLD_MODERATE = 0.45
    THRESHOLD_HIGH = 0.65
    THRESHOLD_CRITICAL = 0.85

    # ── Weights for final score ──────────────────────────────────────────
    W_KEYWORD = 0.45
    W_POLARIZATION = 0.30
    W_GENERATIONAL = 0.15
    W_REGIONAL = 0.10

    def __init__(self) -> None:
        self._compiled_patterns: Dict[str, List[re.Pattern]] = {}
        self._compile_patterns()
        logger.debug("TensionEngine inicializado")

    # ── Pattern compilation ──────────────────────────────────────────────

    def _compile_patterns(self) -> None:
        """Pre-compile regex patterns for keyword matching."""
        for category, keywords in TENSION_KEYWORDS.items():
            self._compiled_patterns[category] = [
                re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE)
                for kw in keywords
            ]

    # ── Main analysis ────────────────────────────────────────────────────

    def analyze(
        self,
        text: str,
        *,
        sentiment: float = 0.5,
        circle: str = "",
        plataforma: str = "",
    ) -> TensionResult:
        """
        Analyze a single signal's text for cultural tensions.

        Args:
            text:        Signal text (termo + descricao concatenated)
            sentiment:   0-1 sentiment score (0=negative, 1=positive)
            circle:      Cultural circle name (e.g. "Música Popular")
            plataforma:  Platform name (e.g. "youtube", "reddit")

        Returns:
            TensionResult with score, level, types, alerts
        """
        if not text or not text.strip():
            return TensionResult()

        text_lower = text.lower()

        # 1. Keyword analysis
        keyword_hits, keyword_score = self._keyword_analysis(text_lower)

        # 2. Polarization from sentiment
        polarization_score = self._compute_polarization(sentiment)

        # 3. Generational tension detection
        gen_score, gen_types = self._generational_analysis(text_lower)

        # 4. Regional tension detection
        regional_score, regional_match = self._regional_analysis(text_lower)

        # 5. Composite score
        composite = (
            self.W_KEYWORD * keyword_score
            + self.W_POLARIZATION * polarization_score
            + self.W_GENERATIONAL * gen_score
            + self.W_REGIONAL * regional_score
        )
        composite = min(1.0, max(0.0, composite))

        # 6. Classify level
        level = self._classify_level(composite)

        # 7. Collect tension types
        types: List[TensionType] = []
        if gen_types:
            types.append(TensionType.GERACIONAL)
        if regional_match:
            types.append(TensionType.REGIONAL)
        if keyword_hits.get("polarizacao", 0) > 0:
            types.append(TensionType.IDEOLOGICA)
        if keyword_hits.get("exclusao_social", 0) > 0:
            types.append(TensionType.SOCIOECONOMICA)
        if keyword_hits.get("resistencia_cultural", 0) > 0:
            types.append(TensionType.TRADICIONAL_VS_MODERNO)
        if keyword_hits.get("mudanca_forcada", 0) > 0:
            types.append(TensionType.URBANO_VS_RURAL)
        # deduplicate preserving order
        seen = set()
        types = [t for t in types if t not in seen and not seen.add(t)]

        # 8. Generate alerts
        alerts = self._generate_alerts(composite, types, keyword_hits, circle)

        return TensionResult(
            score=composite,
            level=level,
            types=types,
            keyword_hits=keyword_hits,
            polarization_score=polarization_score,
            alerts=alerts,
            regional_match=regional_match,
        )

    # ── Sub-analyses ─────────────────────────────────────────────────────

    def _keyword_analysis(self, text_lower: str) -> Tuple[Dict[str, int], float]:
        """Count keyword hits per category, return (hits_dict, normalized_score)."""
        hits: Dict[str, int] = {}
        total_hits = 0
        for category, patterns in self._compiled_patterns.items():
            count = sum(1 for p in patterns if p.search(text_lower))
            if count > 0:
                hits[category] = count
                total_hits += count
        # Normalize: 0 hits → 0.0, 5+ hits → 1.0
        score = min(total_hits / 5.0, 1.0)
        return hits, score

    def _compute_polarization(self, sentiment: float) -> float:
        """
        Compute polarization from sentiment.
        Extreme sentiments (near 0 or 1) indicate stronger polarization.
        Neutral (0.5) = no polarization.
        """
        return abs(sentiment - 0.5) * 2.0  # 0→1, 0.5→0, 1→1

    def _generational_analysis(self, text_lower: str) -> Tuple[float, List[str]]:
        """Detect generational tension markers."""
        gen_counts: Dict[str, int] = {}
        for gen, markers in GENERATIONAL_MARKERS.items():
            count = sum(1 for m in markers if m in text_lower)
            if count > 0:
                gen_counts[gen] = count

        if len(gen_counts) < 2:
            return 0.0, []

        # Multiple generations present → possible tension
        tension_pairs = []
        for gen_a, gen_b in _GENERATIONAL_TENSIONS:
            if gen_a in gen_counts and gen_b in gen_counts:
                tension_pairs.append(f"{gen_a}_vs_{gen_b}")

        if not tension_pairs:
            return 0.2, list(gen_counts.keys())  # mild — multiple gens but no conflict pair

        # Strong generational tension
        score = min(0.6 + 0.2 * len(tension_pairs), 1.0)
        return score, tension_pairs

    def _regional_analysis(self, text_lower: str) -> Tuple[float, Optional[str]]:
        """Detect regional tension indicators."""
        region_hits: Dict[str, int] = {}
        for region, keywords in REGIONAL_PATTERNS.items():
            count = sum(1 for kw in keywords if kw in text_lower)
            if count > 0:
                region_hits[region] = count

        if not region_hits:
            return 0.0, None

        # If 2+ regions mentioned → possible inter-regional tension
        if len(region_hits) >= 2:
            top_regions = sorted(region_hits, key=region_hits.get, reverse=True)[:2]
            return 0.6, f"{top_regions[0]}_vs_{top_regions[1]}"

        # Single region — mild regional awareness
        top_region = max(region_hits, key=region_hits.get)
        return 0.2, top_region

    def _classify_level(self, score: float) -> TensionLevel:
        """Classify tension level from composite score."""
        if score >= self.THRESHOLD_CRITICAL:
            return TensionLevel.CRITICA
        elif score >= self.THRESHOLD_HIGH:
            return TensionLevel.ALTA
        elif score >= self.THRESHOLD_MODERATE:
            return TensionLevel.MODERADA
        else:
            return TensionLevel.BAIXA

    def _generate_alerts(
        self,
        score: float,
        types: List[TensionType],
        keyword_hits: Dict[str, int],
        circle: str,
    ) -> List[str]:
        """Generate human-readable tension alerts."""
        alerts: List[str] = []

        if score >= self.THRESHOLD_HIGH:
            alerts.append(
                f"⚠️ Tensão ALTA detectada (score={score:.2f})"
            )
        elif score >= self.THRESHOLD_MODERATE:
            alerts.append(
                f"🔶 Tensão MODERADA detectada (score={score:.2f})"
            )

        for t in types:
            if t == TensionType.GERACIONAL:
                alerts.append("👥 Tensão geracional: conflito entre gerações detectado")
            elif t == TensionType.REGIONAL:
                alerts.append("🗺️ Tensão regional: referências a múltiplas regiões em conflito")
            elif t == TensionType.IDEOLOGICA:
                alerts.append("⚡ Polarização ideológica detectada")
            elif t == TensionType.SOCIOECONOMICA:
                alerts.append("💰 Tensão socioeconômica: exclusão social detectada")
            elif t == TensionType.TRADICIONAL_VS_MODERNO:
                alerts.append("🔄 Tensão tradição vs modernidade")
            elif t == TensionType.URBANO_VS_RURAL:
                alerts.append("🏙️ Tensão urbano vs rural / mudança forçada")

        if circle and score >= self.THRESHOLD_MODERATE:
            alerts.append(f"📍 Círculo afetado: {circle}")

        return alerts[:5]  # limit to 5 alerts max


# ── Module-level singleton ───────────────────────────────────────────────────

_default_engine: Optional[TensionEngine] = None


def get_tension_engine() -> TensionEngine:
    """Get or create module-level singleton."""
    global _default_engine
    if _default_engine is None:
        _default_engine = TensionEngine()
    return _default_engine


def analyze_tension(
    text: str,
    *,
    sentiment: float = 0.5,
    circle: str = "",
    plataforma: str = "",
) -> Dict[str, Any]:
    """
    Convenience: analyze tension on text and return dict.

    >>> result = analyze_tension("conflito entre boomer e gen z sobre tradição")
    >>> result["tension_level"]
    'moderada'
    """
    engine = get_tension_engine()
    return engine.analyze(
        text, sentiment=sentiment, circle=circle, plataforma=plataforma
    ).to_dict()
