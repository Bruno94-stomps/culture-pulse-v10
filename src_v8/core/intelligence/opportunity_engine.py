#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Opportunity Detector Engine — Culture Pulse V9.1
==================================================
Detecta oportunidades culturais acionáveis a partir de sinais enriquecidos.
Identifica janelas de oportunidade baseadas em:
  - Momentum ascendente + sentimento positivo
  - Lacunas de mercado (círculos sub-representados)
  - Convergência de tendências (múltiplos sinais no mesmo tema)
  - Early signals (sinais novos com alta aceleração)

Diferente do automated_insights_generation.py::OpportunityDetector (que é
genérico e acoplado ao gerador de insights), este engine é focado, testável
e plugável no Worker pipeline.

Cada oportunidade tem: tipo, confiança, janela temporal, potencial de impacto
e ações recomendadas.

Uso:
    from core.intelligence.opportunity_engine import get_opportunity_engine
    engine = get_opportunity_engine()
    opportunities = engine.detect(signal)
    # ou para batch:
    all_opps = engine.detect_batch(signals)
"""

import logging
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
#  Constants
# ═══════════════════════════════════════════════════════════════════════════════

OPPORTUNITY_TYPES = [
    "momentum_wave",        # Onda de momentum crescente
    "sentiment_positive",   # Sentimento muito positivo = oportunidade
    "cultural_gap",         # Lacuna em círculo cultural
    "early_signal",         # Sinal novo acelerando rapidamente
    "convergence",          # Múltiplos fatores positivos convergindo
]


@dataclass
class CulturalOpportunity:
    """Uma oportunidade cultural detectada."""

    opportunity_type: str
    confidence: float  # 0-1
    title: str
    description: str
    window_weeks: int  # Janela estimada em semanas
    potential: str  # low / medium / high
    actions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ═══════════════════════════════════════════════════════════════════════════════
#  INT-F: Cross-engine helpers (vulnerability + signal_nature)
# ═══════════════════════════════════════════════════════════════════════════════


def _is_blocked_by_nature(signal: dict) -> bool:
    """
    INT-F: Bloquear oportunidades em sinais SIMULAÇÃO/APROPRIAÇÃO com
    alta confiança — não há oportunidade genuína nestes sinais.
    """
    nature = signal.get("signal_nature") or {}
    if not isinstance(nature, dict):
        return False
    categoria = nature.get("categoria", "")
    confianca = nature.get("confianca", 0)
    try:
        confianca = float(confianca)
    except (TypeError, ValueError):
        confianca = 0
    # Bloquear se SIMULAÇÃO/APROPRIAÇÃO com confiança > 60%
    if categoria in ("SIMULAÇÃO", "APROPRIAÇÃO") and confianca > 0.6:
        return True
    return False


def _adjust_confidence_by_vulnerability(confidence: float, signal: dict) -> float:
    """
    INT-F: Reduzir confiança de oportunidade quando vulnerability é alta.
    Quanto maior a vulnerabilidade, menor a confiança na oportunidade.
    """
    vuln = signal.get("vulnerability") or {}
    if not isinstance(vuln, dict):
        return confidence
    vuln_score = 0
    try:
        vuln_score = float(vuln.get("overall_score", 0))
    except (TypeError, ValueError):
        return confidence
    # vuln_score 0-100: >60 = penalidade forte, >40 = penalidade leve
    if vuln_score > 60:
        confidence *= 0.7  # -30%
    elif vuln_score > 40:
        confidence *= 0.85  # -15%
    # Nature ORGÂNICO com alta confiança → boost +10%
    nature = signal.get("signal_nature") or {}
    if isinstance(nature, dict):
        if nature.get("categoria") == "ORGÂNICO" and nature.get("confianca", 0) > 0.7:
            confidence *= 1.10
    return min(1.0, confidence)


# ═══════════════════════════════════════════════════════════════════════════════
#  Detectors
# ═══════════════════════════════════════════════════════════════════════════════


def _detect_momentum_wave(signal: dict) -> Optional[CulturalOpportunity]:
    """
    Detectar onda de momentum crescente.

    INT-F: Vulnerability alta reduz confiança; SIMULAÇÃO/APROPRIAÇÃO bloqueiam.
    """
    # INT-F: Bloquear sinais não confiáveis
    if _is_blocked_by_nature(signal):
        return None

    momentum = 0
    try:
        momentum = float(signal.get("momentum", 0))
    except (TypeError, ValueError):
        return None

    velocity = signal.get("velocity") or signal.get("velocity_features") or {}
    trend = 0
    if isinstance(velocity, dict):
        try:
            trend = float(velocity.get("trend", velocity.get("velocity_trend", 0)))
        except (TypeError, ValueError):
            pass

    if momentum >= 50 and trend > 0.2:
        termo = signal.get("termo", "sinal")
        confidence = min(1.0, (momentum / 100.0 + trend) / 1.5)
        confidence = _adjust_confidence_by_vulnerability(confidence, signal)  # INT-F
        window = max(2, 12 - int(momentum / 10))
        return CulturalOpportunity(
            opportunity_type="momentum_wave",
            confidence=round(confidence, 2),
            title=f"Onda de momentum em '{termo}'",
            description=f"Momentum {momentum:.0f} com tendência ascendente ({trend:.2f}). Janela de {window} semanas.",
            window_weeks=window,
            potential="high" if momentum > 70 else "medium",
            actions=[
                "Criar conteúdo alinhado ao movimento cultural.",
                "Buscar parcerias com criadores do nicho.",
                "Investir em mídia durante a janela de oportunidade.",
            ],
        )
    return None


def _detect_sentiment_positive(signal: dict) -> Optional[CulturalOpportunity]:
    """
    Detectar oportunidade por sentimento muito positivo.

    INT-F: SIMULAÇÃO/APROPRIAÇÃO bloqueiam; vulnerability reduz confiança.
    """
    if _is_blocked_by_nature(signal):
        return None

    sent_data = signal.get("sentimento") or signal.get("sentiment")
    if sent_data is None:
        return None

    if isinstance(sent_data, dict):
        score = sent_data.get("compound", sent_data.get("score", 0))
    else:
        try:
            score = float(sent_data)
        except (TypeError, ValueError):
            return None

    if score > 0.5:
        termo = signal.get("termo", "sinal")
        confidence = min(1.0, score)
        confidence = _adjust_confidence_by_vulnerability(confidence, signal)  # INT-F
        return CulturalOpportunity(
            opportunity_type="sentiment_positive",
            confidence=round(confidence, 2),
            title=f"Sentimento muito positivo para '{termo}'",
            description=f"Score de sentimento {score:.2f} — momento ideal para associação de marca.",
            window_weeks=8,
            potential="medium" if score < 0.7 else "high",
            actions=[
                "Associar marca ao sentimento positivo.",
                "Amplificar conteúdo user-generated positivo.",
                "Lançar iniciativas de co-criação.",
            ],
        )
    return None


def _detect_early_signal(signal: dict) -> Optional[CulturalOpportunity]:
    """
    Detectar sinal novo com alta aceleração (early mover advantage).

    INT-F: Bloqueado por SIMULAÇÃO/APROPRIAÇÃO; vulnerability ajusta confiança.
    """
    if _is_blocked_by_nature(signal):
        return None

    momentum = 0
    try:
        momentum = float(signal.get("momentum", 0))
    except (TypeError, ValueError):
        return None

    velocity = signal.get("velocity") or signal.get("velocity_features") or {}
    trend = 0
    if isinstance(velocity, dict):
        try:
            trend = float(velocity.get("trend", velocity.get("velocity_trend", 0)))
        except (TypeError, ValueError):
            pass

    # Momentum ainda baixo MAS acelerando rápido = early signal
    if 10 <= momentum <= 40 and trend > 0.4:
        termo = signal.get("termo", "sinal")
        confidence = min(1.0, trend * 0.8)
        confidence = _adjust_confidence_by_vulnerability(confidence, signal)  # INT-F
        return CulturalOpportunity(
            opportunity_type="early_signal",
            confidence=round(confidence, 2),
            title=f"Sinal emergente detectado: '{termo}'",
            description=f"Momentum baixo ({momentum:.0f}) mas acelerando rapidamente (trend={trend:.2f}). Vantagem de primeiro movimento.",
            window_weeks=16,
            potential="high",
            actions=[
                "Estabelecer presença antes da competição.",
                "Documentar e mapear o movimento emergente.",
                "Preparar conteúdo para quando atingir mainstream.",
                "Investir em relacionamento com comunidade original.",
            ],
        )
    return None


def _detect_convergence(signal: dict) -> Optional[CulturalOpportunity]:
    """
    Detectar convergência de fatores positivos.

    INT-F: Bloqueado por SIMULAÇÃO/APROPRIAÇÃO; vulnerability ajusta confiança.
    INT-C: topic_assignment conta como fator positivo se alta confiança.
    """
    if _is_blocked_by_nature(signal):
        return None

    # Precisamos de pelo menos 3 fatores positivos convergindo
    positive_factors = 0
    details = []

    # Momentum
    momentum = 0
    try:
        momentum = float(signal.get("momentum", 0))
    except (TypeError, ValueError):
        pass
    if momentum > 40:
        positive_factors += 1
        details.append(f"momentum={momentum:.0f}")

    # Sentimento
    sent_data = signal.get("sentimento") or signal.get("sentiment")
    score = 0
    if isinstance(sent_data, dict):
        score = sent_data.get("compound", sent_data.get("score", 0))
    elif sent_data is not None:
        try:
            score = float(sent_data)
        except (TypeError, ValueError):
            pass
    if score > 0.2:
        positive_factors += 1
        details.append(f"sentiment={score:.2f}")

    # Velocity trend
    velocity = signal.get("velocity") or signal.get("velocity_features") or {}
    trend = 0
    if isinstance(velocity, dict):
        try:
            trend = float(velocity.get("trend", velocity.get("velocity_trend", 0)))
        except (TypeError, ValueError):
            pass
    if trend > 0.1:
        positive_factors += 1
        details.append(f"trend={trend:.2f}")

    # PEST favorável (Social/Technological)
    pest = signal.get("pest_classification") or {}
    if pest.get("primary") in ("Social", "Technological"):
        positive_factors += 1
        details.append(f"pest={pest.get('primary')}")

    # INT-C: Topic assignment com alta confiança = sinal temático claro
    topic = signal.get("topic_assignment") or {}
    if isinstance(topic, dict):
        topic_conf = 0
        try:
            topic_conf = float(topic.get("confidence", 0))
        except (TypeError, ValueError):
            pass
        if topic_conf > 0.7:
            positive_factors += 1
            topic_name = topic.get("topic_name", "definido")
            details.append(f"topic={topic_name}")

    # INT-F: Nature ORGÂNICO com confiança conta como fator
    nature = signal.get("signal_nature") or {}
    if isinstance(nature, dict):
        if nature.get("categoria") == "ORGÂNICO" and nature.get("confianca", 0) > 0.6:
            positive_factors += 1
            details.append("nature=ORGÂNICO")

    if positive_factors >= 3:
        termo = signal.get("termo", "sinal")
        confidence = min(1.0, positive_factors * 0.25)
        confidence = _adjust_confidence_by_vulnerability(confidence, signal)  # INT-F
        return CulturalOpportunity(
            opportunity_type="convergence",
            confidence=round(confidence, 2),
            title=f"Convergência de fatores positivos em '{termo}'",
            description=f"{positive_factors} fatores favoráveis: {', '.join(details)}.",
            window_weeks=8,
            potential="high" if positive_factors >= 4 else "medium",
            actions=[
                "Ação imediata — múltiplos sinais favorecem investimento.",
                "Coordenar esforços cross-channel.",
                "Medir e documentar resultados para replicar padrão.",
            ],
        )
    return None


# ═══════════════════════════════════════════════════════════════════════════════
#  Engine
# ═══════════════════════════════════════════════════════════════════════════════

_ALL_DETECTORS = [
    _detect_momentum_wave,
    _detect_sentiment_positive,
    _detect_early_signal,
    _detect_convergence,
]


class OpportunityEngine:
    """Detecta oportunidades culturais em sinais enriquecidos."""

    OPPORTUNITY_TYPES = OPPORTUNITY_TYPES

    def __init__(self) -> None:
        self._detectors = list(_ALL_DETECTORS)

    def detect(self, signal: dict) -> List[CulturalOpportunity]:
        """Detectar oportunidades em um sinal."""
        opportunities: List[CulturalOpportunity] = []
        for detector in self._detectors:
            try:
                opp = detector(signal)
                if opp is not None:
                    opportunities.append(opp)
            except Exception as exc:  # pragma: no cover
                logger.warning("opportunity detector %s error: %s", detector.__name__, exc)
        # Ordenar por confiança descendente
        opportunities.sort(key=lambda o: o.confidence, reverse=True)
        return opportunities

    def detect_dict(self, signal: dict) -> List[Dict[str, Any]]:
        """Detectar e retornar list of dicts."""
        return [o.to_dict() for o in self.detect(signal)]

    def detect_batch(self, signals: List[dict]) -> List[List[Dict[str, Any]]]:
        """Detectar oportunidades em múltiplos sinais."""
        return [self.detect_dict(s) for s in signals]

    def summary(self, signals: List[dict]) -> Dict[str, Any]:
        """Resumo de oportunidades para múltiplos sinais."""
        all_opps: List[CulturalOpportunity] = []
        for s in signals:
            all_opps.extend(self.detect(s))

        by_type: Dict[str, int] = {}
        total_high = 0
        for o in all_opps:
            by_type[o.opportunity_type] = by_type.get(o.opportunity_type, 0) + 1
            if o.potential == "high":
                total_high += 1

        return {
            "total_opportunities": len(all_opps),
            "by_type": by_type,
            "high_potential_count": total_high,
            "avg_confidence": round(
                sum(o.confidence for o in all_opps) / max(1, len(all_opps)), 2
            ),
        }


# ═══════════════════════════════════════════════════════════════════════════════
#  Singleton
# ═══════════════════════════════════════════════════════════════════════════════

_engine: Optional[OpportunityEngine] = None


def get_opportunity_engine() -> OpportunityEngine:
    global _engine
    if _engine is None:
        _engine = OpportunityEngine()
    return _engine


def reset_opportunity_engine() -> None:
    global _engine
    _engine = None
