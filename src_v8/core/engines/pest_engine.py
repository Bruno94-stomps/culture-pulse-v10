#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PEST Engine — Culture Pulse V9.2 (F-5)
==========================================
Classifica cada sinal cultural numa dimensão PEST:
Political, Economic, Social, Technological.

Design:
  - Keyword matching com dicionários PT-BR culturais
  - Score de confiança por densidade de keywords
  - Suporte a multi-label (sinal pode ter dimensão primária + secundária)
  - Singleton thread-safe via get_pest_engine()

Pipeline position: priority 50 (após topics/48)

Output por sinal:
  {
    "primary": "Social",
    "secondary": "Technological" | null,
    "confidence": 0.82,
    "scores": {"Political": 0.1, "Economic": 0.2, "Social": 0.82, "Technological": 0.45},
    "keywords_matched": ["comunidade", "identidade", ...],
    "category_keywords": {"Social": [...], "Technological": [...]},
  }
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ── PEST Keywords — Portuguese-BR Cultural Context ───────────────────────────

PEST_KEYWORDS: Dict[str, List[str]] = {
    "Political": [
        # Política, regulação, governo
        "política", "político", "governo", "governança", "regulação",
        "legislação", "lei", "decreto", "reforma", "eleição",
        "democracia", "censura", "liberdade", "direitos", "cidadania",
        "voto", "parlamento", "congresso", "senado", "câmara",
        "ministério", "prefeitura", "estado", "federal", "municipal",
        "partido", "oposição", "situação", "protesto", "manifestação",
        "polarização", "ideologia", "esquerda", "direita", "centro",
        "corrupção", "transparência", "accountability", "impeachment",
        "stf", "supremo", "constituição", "mp", "ministério público",
        "lgpd", "privacidade", "regulamentação", "compliance",
        "marco civil", "fake news", "desinformação", "propaganda",
        "soberania", "geopolítica", "diplomacia", "sanção",
    ],
    "Economic": [
        # Economia, mercado, finanças
        "economia", "econômico", "mercado", "financeiro", "finança",
        "inflação", "juros", "selic", "câmbio", "dólar", "real",
        "pib", "recessão", "crescimento", "investimento", "ação",
        "bolsa", "ibovespa", "startup", "empreendedorismo", "negócio",
        "comércio", "exportação", "importação", "indústria",
        "emprego", "desemprego", "salário", "renda", "classe média",
        "pobreza", "desigualdade", "gini", "distribuição",
        "pix", "fintech", "banco", "crédito", "dívida",
        "varejo", "atacado", "e-commerce", "marketplace",
        "preço", "custo", "lucro", "margem", "receita",
        "imposto", "tributação", "reforma tributária",
        "commodities", "agronegócio", "safra", "mineração",
        "criptomoeda", "bitcoin", "blockchain", "token",
        "consumo", "poder de compra", "cesta básica",
    ],
    "Social": [
        # Sociedade, cultura, comportamento
        "social", "sociedade", "cultura", "cultural", "comunidade",
        "família", "tradição", "identidade", "pertencimento",
        "diversidade", "inclusão", "equidade", "igualdade",
        "gênero", "feminismo", "machismo", "lgbtqia", "lgbtq",
        "racismo", "antirracismo", "negro", "indígena", "quilombola",
        "favela", "periferia", "periférico", "subúrbio",
        "religião", "fé", "espiritualidade", "igreja",
        "educação", "escola", "universidade", "analfabetismo",
        "saúde", "mental", "bem-estar", "wellness",
        "juventude", "jovem", "idoso", "geracional",
        "música", "funk", "sertanejo", "pagode", "rap", "hip-hop",
        "futebol", "carnaval", "festa", "celebração",
        "gastronomia", "comida", "culinária", "receita",
        "moda", "estilo", "beleza", "corpo", "autoestima",
        "sustentabilidade", "meio ambiente", "ecologia", "clima",
        "voluntariado", "ong", "ativismo", "movimento social",
        "migração", "urbanização", "rural", "sertão", "interior",
        "regionalismo", "nordeste", "sudeste", "sul", "norte",
        "comportamento", "tendência", "lifestyle", "valores",
    ],
    "Technological": [
        # Tecnologia, digital, inovação
        "tecnologia", "tecnológico", "digital", "digitalização",
        "inteligência artificial", "ia", "machine learning", "ml",
        "algoritmo", "automação", "robô", "robótica",
        "internet", "rede social", "plataforma", "app", "aplicativo",
        "smartphone", "celular", "mobile", "wearable",
        "5g", "fibra", "conectividade", "banda larga",
        "metaverso", "realidade virtual", "vr", "realidade aumentada", "ar",
        "iot", "internet das coisas", "smart home", "casa inteligente",
        "streaming", "youtube", "tiktok", "instagram", "twitter",
        "spotify", "podcast", "creator", "influencer", "influenciador",
        "dados", "big data", "analytics", "dashboard",
        "cloud", "nuvem", "saas", "api",
        "cibersegurança", "hacker", "ransomware", "vírus",
        "startup", "unicórnio", "scaleup", "aceleradora",
        "inovação", "disrupção", "transformação digital",
        "chatgpt", "gpt", "llm", "generativa", "copilot",
        "deepfake", "synthetic", "código", "programação",
        "open source", "github", "dev", "developer",
        "edtech", "healthtech", "agrotech", "fintech",
    ],
}

# Pre-compiled regex patterns for efficiency
_PATTERNS: Dict[str, re.Pattern] = {}


def _get_pattern(category: str) -> re.Pattern:
    """Lazy-compile regex for a PEST category."""
    if category not in _PATTERNS:
        keywords = PEST_KEYWORDS[category]
        # Sort by length (longest first) so multi-word phrases match before sub-words
        sorted_kw = sorted(keywords, key=len, reverse=True)
        escaped = [re.escape(k) for k in sorted_kw]
        _PATTERNS[category] = re.compile(
            r"\b(?:" + "|".join(escaped) + r")\b",
            re.IGNORECASE,
        )
    return _PATTERNS[category]


# ── Dataclass ────────────────────────────────────────────────────────────────

@dataclass
class PESTResult:
    """Result of a PEST classification."""

    primary: str  # "Political" | "Economic" | "Social" | "Technological"
    secondary: Optional[str] = None
    confidence: float = 0.0
    scores: Dict[str, float] = field(default_factory=dict)
    keywords_matched: List[str] = field(default_factory=list)
    category_keywords: Dict[str, List[str]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ── Engine ───────────────────────────────────────────────────────────────────

class PESTEngine:
    """
    Classifies cultural signals into PEST dimensions using
    keyword matching against PT-BR cultural dictionaries.

    Thread-safe, stateless (no training required).
    """

    CATEGORIES = ("Political", "Economic", "Social", "Technological")

    def __init__(self) -> None:
        self._total_keywords = {
            cat: len(PEST_KEYWORDS[cat]) for cat in self.CATEGORIES
        }
        logger.info("🏛️  PESTEngine initialized (%s keywords total)",
                     sum(self._total_keywords.values()))

    # ── Public API ───────────────────────────────────────────────────────

    def classify(self, text: str) -> PESTResult:
        """
        Classify a text into PEST dimensions.

        Args:
            text: Free-form Portuguese text (signal termo + description).

        Returns:
            PESTResult with primary/secondary categories, confidence, scores.
        """
        if not text or not text.strip():
            return PESTResult(
                primary="Social",
                confidence=0.0,
                scores={c: 0.0 for c in self.CATEGORIES},
            )

        text_lower = text.lower()
        cat_matches: Dict[str, List[str]] = {}
        cat_scores: Dict[str, float] = {}

        for cat in self.CATEGORIES:
            pattern = _get_pattern(cat)
            matches = pattern.findall(text_lower)
            unique = list(dict.fromkeys(m.lower() for m in matches))
            cat_matches[cat] = unique
            # Score = unique keyword density (capped at 1.0)
            if unique:
                raw = len(unique) / max(self._total_keywords[cat], 1)
                # Boost by match count vs text length ratio
                word_count = max(len(text_lower.split()), 1)
                coverage = min(len(matches) / word_count, 0.5)
                cat_scores[cat] = min(raw + coverage, 1.0)
            else:
                cat_scores[cat] = 0.0

        # Normalize scores to sum ≤ 1.0 if any matches
        total = sum(cat_scores.values())
        if total > 0:
            for cat in self.CATEGORIES:
                cat_scores[cat] = round(cat_scores[cat] / total, 4)

        # Determine primary / secondary
        ranked = sorted(self.CATEGORIES, key=lambda c: cat_scores[c], reverse=True)
        primary = ranked[0]
        primary_score = cat_scores[primary]
        secondary = ranked[1] if cat_scores[ranked[1]] >= 0.15 else None

        # Confidence = primary score (higher = more distinct)
        confidence = round(primary_score, 4)

        # Collect all matched keywords across categories
        all_kw = []
        cat_kw_out: Dict[str, List[str]] = {}
        for cat in self.CATEGORIES:
            if cat_matches[cat]:
                all_kw.extend(cat_matches[cat])
                cat_kw_out[cat] = cat_matches[cat]

        return PESTResult(
            primary=primary,
            secondary=secondary,
            confidence=confidence,
            scores=cat_scores,
            keywords_matched=list(dict.fromkeys(all_kw)),
            category_keywords=cat_kw_out,
        )

    def classify_signal(self, signal: dict) -> PESTResult:
        """
        Convenience: classify from a signal dict.
        Reads 'termo' + 'texto'/'descricao' for full text.

        INT-D: Also reads tension_analysis and signal_nature from upstream
        enrichers to boost/confirm PEST scores. A "tensão ideológica" detected
        by tension_engine reinforces Political; a "tensão socioeconômica"
        reinforces Economic, etc.
        """
        termo = signal.get("termo", "")
        texto = signal.get("texto", signal.get("descricao", ""))
        full_text = f"{termo} {texto}".strip()
        result = self.classify(full_text)

        # ── INT-D: Cross-reference with tension_analysis ─────────────────
        tension = signal.get("tension_analysis", {})
        if tension and isinstance(tension, dict):
            # Tension types map to PEST dimensions
            TENSION_PEST_MAP = {
                "ideologica": "Political",
                "politica": "Political",
                "geracional": "Social",
                "regional": "Social",
                "socioeconomica": "Economic",
                "economica": "Economic",
                "tecnologica": "Technological",
                "tradicao_modernidade": "Social",
            }
            tensions_list = tension.get("tensions", [])
            if isinstance(tensions_list, list):
                for t in tensions_list:
                    t_type = ""
                    if isinstance(t, dict):
                        t_type = t.get("type", "").lower()
                    elif isinstance(t, str):
                        t_type = t.lower()
                    mapped = TENSION_PEST_MAP.get(t_type)
                    if mapped and mapped in result.scores:
                        # Boost the mapped category by 0.05 (capped at 1.0)
                        result.scores[mapped] = min(1.0, result.scores[mapped] + 0.05)

            # Re-evaluate primary/secondary after boost
            if any(result.scores.values()):
                ranked = sorted(self.CATEGORIES, key=lambda c: result.scores.get(c, 0), reverse=True)
                result.primary = ranked[0]
                result.secondary = ranked[1] if result.scores.get(ranked[1], 0) >= 0.15 else None
                result.confidence = round(result.scores.get(result.primary, 0), 4)

        return result

    def batch_classify(self, texts: List[str]) -> List[PESTResult]:
        """Classify multiple texts."""
        return [self.classify(t) for t in texts]

    def get_stats(self) -> Dict[str, Any]:
        """Return engine statistics."""
        return {
            "engine": "PESTEngine",
            "version": "1.0.0",
            "categories": list(self.CATEGORIES),
            "keywords_per_category": dict(self._total_keywords),
            "total_keywords": sum(self._total_keywords.values()),
        }

    def get_distribution(self, results: List[PESTResult]) -> Dict[str, Any]:
        """
        Compute distribution statistics from a batch of results.

        Returns:
            Dict with counts, percentages, avg_confidence per category.
        """
        if not results:
            return {
                "total": 0,
                "distribution": {c: 0 for c in self.CATEGORIES},
                "percentages": {c: 0.0 for c in self.CATEGORIES},
                "avg_confidence": 0.0,
            }

        counts = {c: 0 for c in self.CATEGORIES}
        conf_sum = 0.0
        for r in results:
            counts[r.primary] = counts.get(r.primary, 0) + 1
            conf_sum += r.confidence

        total = len(results)
        percentages = {c: round(counts[c] / total * 100, 1) for c in self.CATEGORIES}
        avg_conf = round(conf_sum / total, 4)

        return {
            "total": total,
            "distribution": counts,
            "percentages": percentages,
            "avg_confidence": avg_conf,
        }


# ── Singleton ────────────────────────────────────────────────────────────────

_engine: Optional[PESTEngine] = None


def get_pest_engine() -> PESTEngine:
    """Get or create singleton PESTEngine instance."""
    global _engine
    if _engine is None:
        _engine = PESTEngine()
    return _engine


def reset_pest_engine() -> None:
    """Reset singleton (for testing)."""
    global _engine, _PATTERNS
    _engine = None
    _PATTERNS.clear()
