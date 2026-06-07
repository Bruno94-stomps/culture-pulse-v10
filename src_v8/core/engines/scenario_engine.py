#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scenario Planning Engine — Culture Pulse V9.1
===============================================
Gera cenários futuros (otimista, base, pessimista) para sinais culturais,
usando dados do pipeline enriquecido (momentum, PEST, tensões, velocity).

Diferente do dormant/core/scenario_planning_engine.py (que usava Prophet/LSTM),
esta versão opera com heurísticas leves e determinísticas, adequadas para
execução inline no Worker pipeline.

Para cada sinal, gera 3 cenários:
  - Otimista: crescimento sustentado, adoção mainstream
  - Base: estabilidade, manutenção do nível atual
  - Pessimista: declínio, fadiga cultural

Cada cenário tem: probabilidade, horizonte, impacto, milestones e narrativa.

Uso:
    from core.scenario_engine import get_scenario_engine
    engine = get_scenario_engine()
    scenarios = engine.generate(signal)
"""

import logging
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime

# Import do Monitoramento Integrado (V9.1 Bridge)
try:
    from monitoring.integrated_monitoring import IntegratedMonitoring
    monitoring_service = IntegratedMonitoring()
except ImportError:
    monitoring_service = None

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
#  Dataclasses
# ═══════════════════════════════════════════════════════════════════════════════

SCENARIO_TYPES = ["optimistic", "baseline", "pessimistic"]


@dataclass
class ScenarioMilestone:
    """Marco temporal dentro de um cenário."""
    week: int
    event: str
    probability: float  # 0-1


@dataclass
class CulturalScenario:
    """Um cenário futuro para um sinal cultural."""

    scenario_type: str  # optimistic / baseline / pessimistic
    probability: float  # 0-1 (soma dos 3 ≈ 1.0)
    horizon_weeks: int
    narrative: str
    projected_momentum: float
    impact_level: str  # low / medium / high
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ScenarioSet:
    """Conjunto dos 3 cenários para um sinal."""

    signal_termo: str
    scenarios: List[CulturalScenario] = field(default_factory=list)
    recommended_strategy: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal_termo": self.signal_termo,
            "scenarios": [s.to_dict() for s in self.scenarios],
            "recommended_strategy": self.recommended_strategy,
        }


# ═══════════════════════════════════════════════════════════════════════════════
#  Probability Estimator
# ═══════════════════════════════════════════════════════════════════════════════


def _estimate_probabilities(signal: dict) -> Dict[str, float]:
    """
    Estimar probabilidade de cada cenário com base em dados do sinal.

    INT-E: Agora consome vulnerability, cultural_alerts e signal_nature
    para ajustar probabilidades. Sinais vulneráveis/com alertas críticos
    deslocam probabilidade para cenário pessimista. Sinais ORGÂNICOS com
    alta autenticidade favorecem cenário otimista.
    """
    momentum = 0
    try:
        # V9.1: Injetar inteligência de Drift real nas probabilidades
        termo = signal.get("termo", "")
        drift_score = 0
        
        if monitoring_service:
            all_drifts = monitoring_service.get_latest_drift()
            # Se houver drift detectado para este termo, aumentamos a incerteza
            drift_score = all_drifts.get(termo, {}).get("drift_score", 0)
            
        momentum = float(signal.get("momentum", 0))
        
        # Ajuste dinâmico: Se drift > 0.6, o cenário pessimista (fadiga) ganha peso corporal
        base_optimistic = 0.3 + (momentum / 200)
        base_pessimistic = 0.2 + (drift_score * 0.5) # Drift alto = risco de fadiga repentina
        
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

    velocity = signal.get("velocity") or signal.get("velocity_features") or {}
    trend = 0
    if isinstance(velocity, dict):
        try:
            trend = float(velocity.get("trend", velocity.get("velocity_trend", 0)))
        except (TypeError, ValueError):
            pass

    # Score combinado base: momentum + sentiment + velocity
    combined = (momentum / 100.0) * 0.4 + ((sentiment + 1) / 2) * 0.3 + (max(-1, min(1, trend)) + 1) / 2 * 0.3

    # ── INT-E: Ajuste por vulnerability ──────────────────────────────────
    vuln = signal.get("vulnerability") or {}
    if isinstance(vuln, dict):
        vuln_score = vuln.get("overall_score", 0)
        try:
            vuln_score = float(vuln_score)
        except (TypeError, ValueError):
            vuln_score = 0
        # Vulnerabilidade alta (>60) puxa combinado para baixo
        if vuln_score > 60:
            combined -= 0.10
        elif vuln_score > 40:
            combined -= 0.05

    # ── INT-E: Ajuste por cultural_alerts ────────────────────────────────
    alerts = signal.get("cultural_alerts") or {}
    if isinstance(alerts, dict):
        alert_list = alerts.get("alerts", [])
        if isinstance(alert_list, list):
            critical_count = sum(
                1 for a in alert_list
                if isinstance(a, dict) and a.get("severity") == "critical"
            )
            warning_count = sum(
                1 for a in alert_list
                if isinstance(a, dict) and a.get("severity") == "warning"
            )
            combined -= critical_count * 0.08 + warning_count * 0.03

    # ── INT-E: Ajuste por signal_nature ──────────────────────────────────
    nature = signal.get("signal_nature") or {}
    if isinstance(nature, dict):
        categoria = nature.get("categoria", "")
        confianca = nature.get("confianca", 0.5)
        # ORGÂNICO com alta confiança → boost otimista
        if categoria == "ORGÂNICO" and confianca > 0.6:
            combined += 0.05
        # SIMULAÇÃO/APROPRIAÇÃO → penalidade
        elif categoria in ("SIMULAÇÃO", "APROPRIAÇÃO"):
            combined -= 0.08
        elif categoria == "COMERCIAL":
            combined -= 0.03

    # ── INT-C: Ajuste por topic_assignment ───────────────────────────────
    topic = signal.get("topic_assignment") or {}
    if isinstance(topic, dict):
        topic_confidence = topic.get("confidence", 0)
        try:
            topic_confidence = float(topic_confidence)
        except (TypeError, ValueError):
            topic_confidence = 0
        # Tópico com alta confiança = sinal mais definido → cenários mais confiáveis
        if topic_confidence > 0.7:
            combined += 0.02  # pequeno boost de estabilidade

    # Clamp
    combined = max(0.0, min(1.0, combined))

    # Mapear para probabilidades (devem somar ≈ 1.0)
    if combined > 0.65:
        return {"optimistic": 0.50, "baseline": 0.35, "pessimistic": 0.15}
    if combined > 0.45:
        return {"optimistic": 0.30, "baseline": 0.45, "pessimistic": 0.25}
    if combined > 0.30:
        return {"optimistic": 0.20, "baseline": 0.40, "pessimistic": 0.40}
    return {"optimistic": 0.10, "baseline": 0.30, "pessimistic": 0.60}


def _project_momentum(current: float, scenario_type: str, horizon: int) -> float:
    """Projetar momentum futuro."""
    multipliers = {
        "optimistic": 1.0 + (0.03 * horizon),
        "baseline": 1.0,
        "pessimistic": 1.0 - (0.04 * horizon),
    }
    projected = current * multipliers.get(scenario_type, 1.0)
    return round(max(0.0, min(100.0, projected)), 1)


# ═══════════════════════════════════════════════════════════════════════════════
#  Narrative Generator
# ═══════════════════════════════════════════════════════════════════════════════


def _generate_narrative(termo: str, scenario_type: str, signal: dict) -> str:
    """
    Gerar narrativa textual para o cenário.

    INT-E: Narrativas agora incorporam signal_nature, vulnerability e
    topic_assignment para contexto mais rico e acionável.
    """
    pest = signal.get("pest_classification") or {}
    pest_primary = pest.get("primary", "Cultural")

    # ── INT-E: Contexto adicional de nature e vulnerability ──────────────
    nature = signal.get("signal_nature") or {}
    categoria = nature.get("categoria", "") if isinstance(nature, dict) else ""
    nature_ctx = ""
    if categoria == "ORGÂNICO":
        nature_ctx = " Com origem orgânica, o sinal carrega autenticidade cultural elevada."
    elif categoria == "SIMULAÇÃO":
        nature_ctx = " Atenção: sinal identificado como simulação — validar autenticidade antes de agir."
    elif categoria == "APROPRIAÇÃO":
        nature_ctx = " Sinal com marcadores de apropriação cultural — risco reputacional elevado."
    elif categoria == "COMERCIAL":
        nature_ctx = " Sinal de natureza comercial — monitorar percepção de autenticidade."

    vuln = signal.get("vulnerability") or {}
    vuln_score = 0
    if isinstance(vuln, dict):
        try:
            vuln_score = float(vuln.get("overall_score", 0))
        except (TypeError, ValueError):
            vuln_score = 0
    vuln_ctx = ""
    if vuln_score > 60:
        vuln_ctx = f" Vulnerabilidade alta ({vuln_score:.0f}/100) amplifica riscos neste cenário."
    elif vuln_score > 40:
        vuln_ctx = f" Vulnerabilidade moderada ({vuln_score:.0f}/100) requer monitoramento."

    topic = signal.get("topic_assignment") or {}
    topic_name = topic.get("topic_name", "") if isinstance(topic, dict) else ""
    topic_ctx = f" Tema dominante: {topic_name}." if topic_name else ""

    # ── Narrativas com contexto enriquecido ──────────────────────────────
    narratives = {
        "optimistic": (
            f"'{termo}' ganha tração mainstream nos próximos meses. "
            f"Impulsionado por fatores {pest_primary}, o sinal evolui de nicho "
            f"para tendência consolidada, abrindo oportunidades de marca."
            f"{nature_ctx}{topic_ctx}"
        ),
        "baseline": (
            f"'{termo}' mantém relevância atual sem crescimento significativo. "
            f"O contexto {pest_primary} permanece estável, exigindo monitoramento "
            f"contínuo sem necessidade de ação urgente."
            f"{nature_ctx}{vuln_ctx}{topic_ctx}"
        ),
        "pessimistic": (
            f"'{termo}' perde momentum gradualmente. Fadiga cultural ou mudanças "
            f"no contexto {pest_primary} reduzem relevância, requerendo "
            f"reposicionamento estratégico."
            f"{nature_ctx}{vuln_ctx}{topic_ctx}"
        ),
    }
    return narratives.get(scenario_type, f"Cenário para '{termo}'.")


def _generate_milestones(scenario_type: str, horizon: int) -> List[Dict[str, Any]]:
    """Gerar marcos temporais para o cenário."""
    milestone_templates = {
        "optimistic": [
            {"week": max(1, horizon // 4), "event": "Adoção por early adopters mainstream", "probability": 0.7},
            {"week": max(2, horizon // 2), "event": "Cobertura em mídia nacional", "probability": 0.5},
            {"week": horizon, "event": "Consolidação como tendência cultural", "probability": 0.4},
        ],
        "baseline": [
            {"week": max(1, horizon // 3), "event": "Manutenção de engajamento estável", "probability": 0.8},
            {"week": max(2, horizon * 2 // 3), "event": "Possível saturação de nicho", "probability": 0.5},
            {"week": horizon, "event": "Estabilidade sem crescimento", "probability": 0.6},
        ],
        "pessimistic": [
            {"week": max(1, horizon // 4), "event": "Primeiros sinais de fadiga cultural", "probability": 0.6},
            {"week": max(2, horizon // 2), "event": "Queda mensurável de engajamento", "probability": 0.5},
            {"week": horizon, "event": "Irrelevância cultural", "probability": 0.3},
        ],
    }
    return milestone_templates.get(scenario_type, [])


def _scenario_risks(scenario_type: str, signal: dict = None) -> List[str]:
    """
    Riscos associados a cada cenário.

    INT-E: Riscos agora contextualizados por vulnerability e signal_nature.
    """
    base_risks = {
        "optimistic": [
            "Crescimento rápido pode atrair concorrência",
            "Risco de autenticidade se marcas entrarem agressivamente",
        ],
        "baseline": [
            "Estagnação pode evoluir para declínio",
            "Competidores podem capturar o espaço cultural",
        ],
        "pessimistic": [
            "Perda de investimento em conteúdo atual",
            "Dificuldade de reposicionamento tardio",
        ],
    }
    risks = list(base_risks.get(scenario_type, []))

    # ── INT-E: Riscos adicionais por vulnerability e nature ──────────────
    if signal:
        vuln = signal.get("vulnerability") or {}
        if isinstance(vuln, dict):
            vuln_score = 0
            try:
                vuln_score = float(vuln.get("overall_score", 0))
            except (TypeError, ValueError):
                pass
            if vuln_score > 60:
                risks.append("Alta vulnerabilidade cultural — exposição a crises reputacionais")
            factors = vuln.get("factors") or {}
            if isinstance(factors, dict) and factors.get("polarization", 0) > 0.6:
                risks.append("Polarização elevada — risco de backlash em posicionamento")

        nature = signal.get("signal_nature") or {}
        if isinstance(nature, dict):
            cat = nature.get("categoria", "")
            if cat == "APROPRIAÇÃO":
                risks.append("Sinal de apropriação cultural — risco legal e reputacional severo")
            elif cat == "SIMULAÇÃO":
                risks.append("Sinal simulado — decisões baseadas em dados artificiais")

    return risks


def _scenario_opportunities(scenario_type: str) -> List[str]:
    """Oportunidades associadas a cada cenário."""
    opps = {
        "optimistic": [
            "Liderança cultural no segmento",
            "Expansão para mercados adjacentes",
            "Fortalecimento de brand equity cultural",
        ],
        "baseline": [
            "Manutenção de posição com custo reduzido",
            "Tempo para preparar próxima onda cultural",
        ],
        "pessimistic": [
            "Aprendizado para futuros ciclos culturais",
            "Realocar recursos para sinais emergentes",
        ],
    }
    return opps.get(scenario_type, [])


# ═══════════════════════════════════════════════════════════════════════════════
#  Engine
# ═══════════════════════════════════════════════════════════════════════════════


class ScenarioEngine:
    """Gera cenários futuros para sinais culturais."""

    SCENARIO_TYPES = SCENARIO_TYPES

    def __init__(self, default_horizon: int = 12) -> None:
        self._default_horizon = default_horizon  # weeks

    def generate(self, signal: dict, horizon: Optional[int] = None) -> ScenarioSet:
        """Gerar 3 cenários para um sinal cultural."""
        h = horizon or self._default_horizon
        termo = signal.get("termo", "sinal")
        momentum = 0
        try:
            momentum = float(signal.get("momentum", 0))
        except (TypeError, ValueError):
            pass

        probs = _estimate_probabilities(signal)
        scenarios: List[CulturalScenario] = []

        for stype in SCENARIO_TYPES:
            impact = "high" if stype == "optimistic" and momentum > 60 else (
                "low" if stype == "pessimistic" and momentum < 30 else "medium"
            )
            scenarios.append(
                CulturalScenario(
                    scenario_type=stype,
                    probability=round(probs[stype], 2),
                    horizon_weeks=h,
                    narrative=_generate_narrative(termo, stype, signal),
                    projected_momentum=_project_momentum(momentum, stype, h),
                    impact_level=impact,
                    milestones=_generate_milestones(stype, h),
                    risks=_scenario_risks(stype, signal),
                    opportunities=_scenario_opportunities(stype),
                )
            )

        # Estratégia recomendada baseada no cenário mais provável
        most_probable = max(scenarios, key=lambda s: s.probability)
        strategy_map = {
            "optimistic": "Investir e amplificar presença cultural.",
            "baseline": "Manter monitoramento e preparar contingências.",
            "pessimistic": "Reposicionar e diversificar portfolio cultural.",
        }

        return ScenarioSet(
            signal_termo=termo,
            scenarios=scenarios,
            recommended_strategy=strategy_map.get(most_probable.scenario_type, "Monitorar."),
        )

    def generate_dict(self, signal: dict, horizon: Optional[int] = None) -> Dict[str, Any]:
        """Convenience: generate and return dict."""
        return self.generate(signal, horizon).to_dict()

    def batch_generate(self, signals: List[dict], horizon: Optional[int] = None) -> List[Dict[str, Any]]:
        """Gerar cenários para múltiplos sinais."""
        return [self.generate_dict(s, horizon) for s in signals]


# ═══════════════════════════════════════════════════════════════════════════════
#  Singleton
# ═══════════════════════════════════════════════════════════════════════════════

_engine: Optional[ScenarioEngine] = None


def get_scenario_engine() -> ScenarioEngine:
    global _engine
    if _engine is None:
        _engine = ScenarioEngine()
    return _engine


def reset_scenario_engine() -> None:
    global _engine
    _engine = None
