#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Strategic Actions Engine — Culture Pulse V9.1
===============================================
Gera ações estratégicas recomendadas para cada sinal cultural,
combinando dados de múltiplos enrichers para produzir playbooks acionáveis.

Para cada sinal, gera:
  - Tipo de ação (engage / monitor / protect / amplify / pivot)
  - Urgência (1-5)
  - Playbook steps (lista de passos concretos)
  - Canais recomendados
  - KPIs sugeridos
  - Estimativa de impacto

Usa os dados de: circles, sentiment, PEST, tension, velocity, vulnerability.

Uso:
    from core.intelligence.strategic_actions_engine import get_strategic_engine
    engine = get_strategic_engine()
    action = engine.recommend(signal)
    # action = {"action_type": "amplify", "urgency": 4, "playbook": [...], ...}
"""

import logging
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
#  Constants
# ═══════════════════════════════════════════════════════════════════════════════

ACTION_TYPES = ["engage", "monitor", "protect", "amplify", "pivot"]

CHANNEL_MAP = {
    "youtube": ["YouTube Shorts", "YouTube Community", "Influencer Collabs"],
    "reddit": ["Reddit AMAs", "Community Posts", "Subreddit Partnerships"],
    "spotify": ["Playlists Curadas", "Podcast Sponsorship", "Audio Ads"],
    "newsapi": ["Press Release", "Op-Ed", "Media Briefing"],
    "instagram": ["Reels", "Stories", "Creator Partnerships"],
    "google_trends": ["SEO Content", "Google Ads", "Blog Posts"],
}

PEST_ACTION_MAP = {
    "Political": {
        "action_type": "monitor",
        "playbook_prefix": "Acompanhar regulamentação e posicionamento institucional.",
    },
    "Economic": {
        "action_type": "protect",
        "playbook_prefix": "Avaliar impacto financeiro e ajustar pricing/comunicação.",
    },
    "Social": {
        "action_type": "engage",
        "playbook_prefix": "Engajar com comunidade e amplificar vozes culturais.",
    },
    "Technological": {
        "action_type": "amplify",
        "playbook_prefix": "Adotar tecnologia e liderar narrativa de inovação.",
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
#  Dataclass
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class StrategicAction:
    """Ação estratégica recomendada para um sinal."""

    action_type: str  # engage / monitor / protect / amplify / pivot
    urgency: int  # 1-5
    title: str
    playbook: List[str] = field(default_factory=list)
    channels: List[str] = field(default_factory=list)
    kpis: List[str] = field(default_factory=list)
    impact_estimate: str = "medium"  # low / medium / high
    rationale: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ═══════════════════════════════════════════════════════════════════════════════
#  Decision Logic
# ═══════════════════════════════════════════════════════════════════════════════


def _determine_action_type(signal: dict) -> str:
    """Determinar tipo de ação com base nos dados enriquecidos."""
    momentum = 0
    try:
        momentum = float(signal.get("momentum", 0))
    except (TypeError, ValueError):
        pass

    sentiment = 0
    sent_data = signal.get("sentimento") or signal.get("sentiment")
    if isinstance(sent_data, dict):
        sentiment = sent_data.get("compound", sent_data.get("score", 0))
    elif sent_data is not None:
        try:
            sentiment = float(sent_data)
        except (TypeError, ValueError):
            pass

    vuln = signal.get("vulnerability") or {}
    vuln_level = vuln.get("level", "moderate") if isinstance(vuln, dict) else "moderate"

    # Decision tree
    if vuln_level == "critical":
        return "protect"
    if momentum >= 70 and sentiment > 0:
        return "amplify"
    if momentum >= 50 and sentiment < -0.3:
        return "pivot"
    if momentum < 30:
        return "monitor"
    return "engage"


def _determine_urgency(signal: dict) -> int:
    """Urgência de 1 (baixa) a 5 (imediata)."""
    momentum = 0
    try:
        momentum = float(signal.get("momentum", 0))
    except (TypeError, ValueError):
        pass

    velocity = signal.get("velocity") or signal.get("velocity_features") or {}
    trend = 0
    if isinstance(velocity, dict):
        try:
            trend = float(velocity.get("trend", velocity.get("velocity_trend", 0)))
        except (TypeError, ValueError):
            pass

    vuln = signal.get("vulnerability") or {}
    vuln_score = 0
    if isinstance(vuln, dict):
        try:
            vuln_score = float(vuln.get("score", 0))
        except (TypeError, ValueError):
            pass

    # Urgência baseada em momentum + trend + vulnerabilidade
    urgency_score = (momentum / 25.0) + (max(0, trend) * 2) + (vuln_score / 50.0)
    return max(1, min(5, round(urgency_score)))


def _build_playbook(action_type: str, signal: dict) -> List[str]:
    """Gerar passos do playbook baseado no tipo de ação."""
    pest = signal.get("pest_classification") or {}
    primary = pest.get("primary", "Social")
    pest_info = PEST_ACTION_MAP.get(primary, PEST_ACTION_MAP["Social"])

    termo = signal.get("termo", "sinal cultural")

    playbooks = {
        "engage": [
            f"1. Mapear comunidade ativa em torno de '{termo}'.",
            "2. Identificar influenciadores e criadores de conteúdo relevantes.",
            "3. Criar conteúdo autêntico alinhado com o movimento cultural.",
            "4. Lançar campanha de engajamento em 72h.",
            f"5. {pest_info['playbook_prefix']}",
        ],
        "monitor": [
            f"1. Configurar alertas automáticos para '{termo}'.",
            "2. Acompanhar evolução de momentum semanal.",
            "3. Preparar cenários de resposta (otimista/base/pessimista).",
            "4. Revisar posição em 7 dias.",
        ],
        "protect": [
            "1. Ativar protocolo de gestão de crise cultural.",
            f"2. Avaliar exposição da marca a '{termo}'.",
            "3. Preparar comunicação defensiva.",
            "4. Monitorar sentimento em tempo real (intervalo 1h).",
            "5. Reunião de alinhamento com stakeholders em 24h.",
        ],
        "amplify": [
            f"1. Intensificar presença em canais onde '{termo}' está crescendo.",
            "2. Aumentar investimento em conteúdo relacionado.",
            "3. Buscar co-criação com comunidade cultural.",
            "4. Medir share-of-voice vs competidores.",
            "5. Escalar ações que estão funcionando.",
        ],
        "pivot": [
            f"1. Reavaliar posicionamento em relação a '{termo}'.",
            "2. Testar nova narrativa com grupo piloto.",
            "3. Ajustar tom de comunicação (de neutro para empático).",
            "4. Monitorar recepção da nova abordagem.",
            "5. Iterar baseado em feedback em 48h.",
        ],
    }

    return playbooks.get(action_type, playbooks["monitor"])


def _suggest_channels(signal: dict) -> List[str]:
    """Sugerir canais com base na plataforma de origem."""
    plataforma = signal.get("plataforma", "").lower()
    channels = CHANNEL_MAP.get(plataforma, ["Social Media", "Content Marketing"])
    return channels[:3]


def _suggest_kpis(action_type: str) -> List[str]:
    """KPIs sugeridos por tipo de ação."""
    kpi_map = {
        "engage": ["Engagement Rate", "Share of Voice", "Sentiment Score"],
        "monitor": ["Momentum Trend", "Mention Volume", "Sentiment Delta"],
        "protect": ["Crisis Sentiment", "Brand Health Score", "Response Time"],
        "amplify": ["Reach Growth", "Content Virality", "Community Growth"],
        "pivot": ["Perception Shift", "New Audience Reach", "Sentiment Recovery"],
    }
    return kpi_map.get(action_type, ["Momentum", "Sentiment", "Reach"])


def _estimate_impact(action_type: str, signal: dict) -> str:
    """Estimar impacto da ação."""
    momentum = 0
    try:
        momentum = float(signal.get("momentum", 0))
    except (TypeError, ValueError):
        pass

    if action_type == "amplify" and momentum > 70:
        return "high"
    if action_type in ("protect", "pivot"):
        return "high"
    if momentum > 50:
        return "medium"
    return "low"


# ═══════════════════════════════════════════════════════════════════════════════
#  Engine
# ═══════════════════════════════════════════════════════════════════════════════


class StrategicActionsEngine:
    """Gera ações estratégicas para sinais culturais."""

    ACTION_TYPES = ACTION_TYPES

    def __init__(self) -> None:
        pass

    def recommend(self, signal: dict) -> StrategicAction:
        """Gerar recomendação de ação para um sinal."""
        action_type = _determine_action_type(signal)
        urgency = _determine_urgency(signal)
        termo = signal.get("termo", "sinal cultural")

        title_map = {
            "engage": f"Engajar com movimento '{termo}'",
            "monitor": f"Monitorar evolução de '{termo}'",
            "protect": f"Proteger marca contra risco em '{termo}'",
            "amplify": f"Amplificar presença em '{termo}'",
            "pivot": f"Reposicionar narrativa sobre '{termo}'",
        }

        return StrategicAction(
            action_type=action_type,
            urgency=urgency,
            title=title_map.get(action_type, f"Ação para '{termo}'"),
            playbook=_build_playbook(action_type, signal),
            channels=_suggest_channels(signal),
            kpis=_suggest_kpis(action_type),
            impact_estimate=_estimate_impact(action_type, signal),
            rationale=f"Baseado em momentum, sentimento e contexto PEST de '{termo}'.",
        )

    def recommend_dict(self, signal: dict) -> Dict[str, Any]:
        """Convenience: recommend and return dict."""
        return self.recommend(signal).to_dict()

    def batch_recommend(self, signals: List[dict]) -> List[Dict[str, Any]]:
        """Gerar recomendações para múltiplos sinais."""
        return [self.recommend_dict(s) for s in signals]


# ═══════════════════════════════════════════════════════════════════════════════
#  Singleton
# ═══════════════════════════════════════════════════════════════════════════════

_engine: Optional[StrategicActionsEngine] = None


def get_strategic_engine() -> StrategicActionsEngine:
    global _engine
    if _engine is None:
        _engine = StrategicActionsEngine()
    return _engine


def reset_strategic_engine() -> None:
    global _engine
    _engine = None
