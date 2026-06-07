#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cultural Alerts Engine — Culture Pulse V9.1
=============================================
Gera alertas culturais inteligentes a partir de sinais enriquecidos.
Detecta condições que requerem atenção imediata:
  - Spike de momentum (sinal viralizando)
  - Drift de sentimento (mudança brusca de sentimento)
  - Nova tensão cultural (tensão inédita detectada)
  - Oportunidade temporal (janela se fechando)
  - Saturação de círculo (excesso de sinais em um círculo)

Cada alerta possui severidade (info/warning/critical), tipo, contexto e
ações recomendadas.

Uso:
    from alerts.cultural_alerts_engine import get_alerts_engine
    engine = get_alerts_engine()
    alerts = engine.evaluate(signal)
    # alerts = [{"type": "momentum_spike", "severity": "critical", "message": ..., ...}]
"""

import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
#  Constants
# ═══════════════════════════════════════════════════════════════════════════════

ALERT_SEVERITIES = ["info", "warning", "critical"]

ALERT_TYPES = [
    "momentum_spike",
    "sentiment_shift",
    "new_tension",
    "temporal_opportunity",
    "circle_saturation",
    "velocity_acceleration",
]

# Thresholds configuráveis
DEFAULT_THRESHOLDS = {
    "momentum_spike_min": 75.0,
    "sentiment_shift_delta": 0.4,
    "tension_count_warning": 2,
    "tension_count_critical": 4,
    "velocity_acceleration_min": 0.6,
    "circle_saturation_count": 10,
}


@dataclass
class CulturalAlert:
    """Um alerta cultural gerado por condição detectada."""

    alert_type: str
    severity: str  # info / warning / critical
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    action: str = ""
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ═══════════════════════════════════════════════════════════════════════════════
#  Rule Evaluators
# ═══════════════════════════════════════════════════════════════════════════════


def _check_momentum_spike(signal: dict, thresholds: dict) -> Optional[CulturalAlert]:
    """
    Alerta se momentum está muito alto (sinal viralizando).

    INT-C: Inclui topic_assignment no contexto do alerta para
    contextualizar em qual tema a viralização está ocorrendo.
    """
    momentum = signal.get("momentum", 0)
    try:
        momentum = float(momentum)
    except (TypeError, ValueError):
        return None

    threshold = thresholds.get("momentum_spike_min", 75.0)
    if momentum >= threshold:
        severity = "critical" if momentum >= 90 else "warning"
        context: Dict[str, Any] = {"momentum": momentum, "threshold": threshold}

        # INT-C: Enriquecer contexto com topic
        topic = signal.get("topic_assignment") or {}
        if isinstance(topic, dict) and topic.get("topic_name"):
            context["topic"] = topic["topic_name"]
            context["topic_confidence"] = topic.get("confidence", 0)

        topic_suffix = ""
        if context.get("topic"):
            topic_suffix = f" Tema: {context['topic']}."

        return CulturalAlert(
            alert_type="momentum_spike",
            severity=severity,
            message=f"Sinal com momentum {momentum:.0f} — possível viralização.{topic_suffix}",
            context=context,
            action="Monitorar em tempo real e preparar resposta de marca.",
        )
    return None


def _check_sentiment_shift(signal: dict, thresholds: dict) -> Optional[CulturalAlert]:
    """Alerta se sentimento é muito negativo ou mudou bruscamente."""
    sentiment = signal.get("sentimento") or signal.get("sentiment")
    if sentiment is None:
        return None

    if isinstance(sentiment, dict):
        score = sentiment.get("compound", sentiment.get("score", 0))
    else:
        try:
            score = float(sentiment)
        except (TypeError, ValueError):
            return None

    delta = thresholds.get("sentiment_shift_delta", 0.4)
    if score < -delta:
        severity = "critical" if score < -0.7 else "warning"
        return CulturalAlert(
            alert_type="sentiment_shift",
            severity=severity,
            message=f"Sentimento negativo forte ({score:.2f}) detectado.",
            context={"sentiment_score": score},
            action="Avaliar causa do sentimento negativo e preparar comunicação.",
        )
    return None


def _check_new_tension(signal: dict, thresholds: dict) -> Optional[CulturalAlert]:
    """Alerta se tensões culturais estão acima do limite."""
    tensions = signal.get("tensoes_culturais") or signal.get("tensions") or []
    if isinstance(tensions, dict):
        tensions = tensions.get("tensions", [])
    count = len(tensions) if isinstance(tensions, list) else 0

    critical_threshold = thresholds.get("tension_count_critical", 4)
    warning_threshold = thresholds.get("tension_count_warning", 2)

    if count >= critical_threshold:
        return CulturalAlert(
            alert_type="new_tension",
            severity="critical",
            message=f"{count} tensões culturais ativas — risco de crise cultural.",
            context={"tension_count": count},
            action="Convocar equipe de gestão de crise cultural.",
        )
    if count >= warning_threshold:
        return CulturalAlert(
            alert_type="new_tension",
            severity="warning",
            message=f"{count} tensões culturais detectadas.",
            context={"tension_count": count},
            action="Monitorar evolução das tensões e preparar posicionamento.",
        )
    return None


def _check_velocity_acceleration(signal: dict, thresholds: dict) -> Optional[CulturalAlert]:
    """Alerta se velocidade está acelerando rapidamente."""
    velocity = signal.get("velocity") or signal.get("velocity_features") or {}
    if isinstance(velocity, dict):
        trend = velocity.get("trend", velocity.get("velocity_trend", 0))
    else:
        trend = 0

    try:
        trend = float(trend)
    except (TypeError, ValueError):
        return None

    threshold = thresholds.get("velocity_acceleration_min", 0.6)
    if trend >= threshold:
        return CulturalAlert(
            alert_type="velocity_acceleration",
            severity="warning",
            message=f"Aceleração cultural rápida (trend={trend:.2f}) — janela de oportunidade.",
            context={"velocity_trend": trend},
            action="Aproveitar momentum atual com ações rápidas de conteúdo.",
        )
    return None


def _check_temporal_opportunity(signal: dict, _thresholds: dict) -> Optional[CulturalAlert]:
    """Alerta se o sinal tem janela temporal (baseado em PEST + momentum)."""
    pest = signal.get("pest_classification") or {}
    momentum = signal.get("momentum", 0)
    try:
        momentum = float(momentum)
    except (TypeError, ValueError):
        momentum = 0

    primary = pest.get("primary", "")
    # Political/Economic com momentum médio-alto = janela temporal
    if primary in ("Political", "Economic") and momentum > 50:
        return CulturalAlert(
            alert_type="temporal_opportunity",
            severity="info",
            message=f"Janela temporal aberta — sinal {primary} com momentum {momentum:.0f}.",
            context={"pest_category": primary, "momentum": momentum},
            action="Avaliar ação rápida antes que contexto mude.",
        )
    return None


def _check_active_signal(signal: dict, _thresholds: dict) -> Optional[CulturalAlert]:
    """Alerta informativo sempre presente para sinais activos — garante resposta não-vazia."""
    termo = signal.get("termo", "desconhecido")
    momentum = signal.get("momentum", 0)
    plataforma = signal.get("plataforma", "desconhecida")
    try:
        momentum = float(momentum)
    except (TypeError, ValueError):
        momentum = 0

    # Só dispara se nenhum alerta crítico já foi gerado (este checker roda por último)
    if momentum < 75:
        return CulturalAlert(
            alert_type="active_signal",
            severity="info",
            message=f'Sinal "{termo}" ativo em {plataforma} (momentum {momentum:.0f}/100).',
            context={"termo": termo, "plataforma": plataforma, "momentum": momentum},
            action="Acompanhar evolução do sinal nas próximas 24h.",
        )
    return None


def _check_cluster_fragmentation(signal: dict, _thresholds: dict) -> Optional[CulturalAlert]:
    """
    Alerta se o cluster cultural deste sinal está se fragmentando ou instável.
    Integração direta com o novo módulo core.clustering (V9.9).
    """
    stability = signal.get("stability_context") or signal.get("cluster_stability") or {}
    status = str(stability.get("status", "")).lower()

    if status in ("fragmentando", "instável"):
        severity = "critical" if status == "instável" else "warning"
        termo = signal.get("termo", "desconhecido")
        
        return CulturalAlert(
            alert_type="cluster_fragmentation",
            severity=severity,
            message=f"Instabilidade detectada: O cluster do termo '{termo}' está {status}.",
            context={
                "status": status,
                "ari_score": stability.get("ari_score"),
                "badge": stability.get("badge")
            },
            action="Realizar re-clustering imediato e validar consistência dos sinais."
        )
    return None


# ═══════════════════════════════════════════════════════════════════════════════
#  Engine
# ═══════════════════════════════════════════════════════════════════════════════

_ALL_CHECKERS = [
    _check_momentum_spike,
    _check_sentiment_shift,
    _check_new_tension,
    _check_velocity_acceleration,
    _check_temporal_opportunity,
    _check_cluster_fragmentation,  # Nova regra de estabilidade (V9.9)
    _check_active_signal,
]


class CulturalAlertsEngine:
    """
    Gera alertas culturais a partir de sinais enriquecidos.
    Sincronizado com AlertConfig para evitar dualidade de thresholds na V9.9.
    """

    ALERT_TYPES = ALERT_TYPES

    def __init__(self, thresholds: Optional[Dict[str, float]] = None) -> None:
        # Sincronização proativa com AlertConfig global
        try:
            from alerts.alert_config import get_default_config
            sys_config = get_default_config()
            
            # Unificar thresholds da API com os thresholds de inteligência
            config_thresholds = {
                "momentum_spike_min": sys_config.thresholds.high_momentum,
                "sentiment_shift_delta": abs(sys_config.thresholds.negative_sentiment),
            }
            self._thresholds = {**DEFAULT_THRESHOLDS, **config_thresholds, **(thresholds or {})}
        except Exception:
            self._thresholds = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
            
        self._checkers = list(_ALL_CHECKERS)

    def evaluate(self, signal: dict) -> List[CulturalAlert]:
        """
        Avaliar um sinal e retornar lista de alertas.

        INT-C: Todos os alertas gerados recebem topic_assignment no contexto
        para contextualização temática downstream.
        """
        alerts: List[CulturalAlert] = []
        for checker in self._checkers:
            try:
                alert = checker(signal, self._thresholds)
                if alert is not None:
                    alerts.append(alert)
            except Exception as exc:  # pragma: no cover
                logger.warning("alert checker %s error: %s", checker.__name__, exc)

        # INT-C: Injetar topic_assignment no contexto de todos os alertas
        topic = signal.get("topic_assignment") or {}
        if isinstance(topic, dict) and topic.get("topic_name"):
            for alert in alerts:
                if "topic" not in alert.context:
                    alert.context["topic"] = topic["topic_name"]
                    alert.context["topic_confidence"] = topic.get("confidence", 0)

        return alerts

    def evaluate_dict(self, signal: dict) -> List[Dict[str, Any]]:
        """Avaliar e retornar list of dicts."""
        return [a.to_dict() for a in self.evaluate(signal)]

    def batch_evaluate(self, signals: List[dict]) -> List[List[Dict[str, Any]]]:
        """Avaliar múltiplos sinais."""
        return [self.evaluate_dict(s) for s in signals]

    def summary(self, signals: List[dict]) -> Dict[str, Any]:
        """Resumo de alertas por severidade para múltiplos sinais."""
        all_alerts: List[CulturalAlert] = []
        for s in signals:
            all_alerts.extend(self.evaluate(s))

        by_severity = {"info": 0, "warning": 0, "critical": 0}
        by_type: Dict[str, int] = {}
        for a in all_alerts:
            by_severity[a.severity] = by_severity.get(a.severity, 0) + 1
            by_type[a.alert_type] = by_type.get(a.alert_type, 0) + 1

        return {
            "total_alerts": len(all_alerts),
            "by_severity": by_severity,
            "by_type": by_type,
            "critical_count": by_severity["critical"],
        }


# ═══════════════════════════════════════════════════════════════════════════════
#  Singleton
# ═══════════════════════════════════════════════════════════════════════════════

_engine: Optional[CulturalAlertsEngine] = None


def get_alerts_engine() -> CulturalAlertsEngine:
    global _engine
    if _engine is None:
        _engine = CulturalAlertsEngine()
    return _engine


def reset_alerts_engine() -> None:
    global _engine
    _engine = None
