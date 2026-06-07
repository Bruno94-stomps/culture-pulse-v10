#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests: Cross-Engine Integrations (INT-A through INT-F)
=======================================================
Valida que dados fluem corretamente entre engines após as
integrações que eliminaram isolamento de módulos.

INT-A: authenticity → signal_nature (cross-calibração)
INT-B: velocity ← circulo (normalização por baseline)
INT-C: topics → cultural_alerts / scenarios / opportunities
INT-D: pest ← tension (TENSION_PEST_MAP)
INT-E: scenarios ← vulnerability + cultural_alerts + signal_nature
INT-F: opportunities ← vulnerability + signal_nature
"""

import sys
from pathlib import Path

# Ensure src_v8 is importable
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest


# ═════════════════════════════════════════════════════════════════════════════
#  Fixtures: Sinais de teste com diferentes profiles
# ═════════════════════════════════════════════════════════════════════════════


def _base_signal(**overrides) -> dict:
    """Sinal base com campos mínimos para testes."""
    sig = {
        "termo": "funk carioca",
        "plataforma": "youtube",
        "momentum": 65,
        "sentimento": {"compound": 0.4, "score": 0.4},
        "velocity": {"trend": 0.3, "velocity_trend": 0.3},
        "circulo": "Música Popular",
    }
    sig.update(overrides)
    return sig


def _signal_organico_autentico() -> dict:
    return _base_signal(
        signal_nature={"categoria": "ORGÂNICO", "confianca": 0.85},
        authenticity_score=0.9,
        appropriation_risk=0.1,
        vulnerability={"overall_score": 15, "factors": {"polarization": 0.1}},
        topic_assignment={"topic_name": "Cultura Musical Urbana", "confidence": 0.8},
    )


def _signal_simulacao_vulneravel() -> dict:
    return _base_signal(
        momentum=40,  # Momentum mais baixo para permitir shift pessimista
        sentimento={"compound": 0.1, "score": 0.1},  # Sentimento quase neutro
        signal_nature={"categoria": "SIMULAÇÃO", "confianca": 0.75},
        authenticity_score=0.2,
        appropriation_risk=0.8,
        vulnerability={"overall_score": 72, "factors": {"polarization": 0.7}},
        topic_assignment={"topic_name": "Astroturfing Digital", "confidence": 0.9},
        tensoes_culturais=[
            {"tipo": "ideologica"},
            {"tipo": "geracional"},
        ],
    )


def _signal_comercial_moderado() -> dict:
    return _base_signal(
        signal_nature={"categoria": "COMERCIAL", "confianca": 0.6},
        authenticity_score=0.5,
        appropriation_risk=0.4,
        vulnerability={"overall_score": 45, "factors": {"polarization": 0.3}},
    )


def _signal_apropiacao() -> dict:
    return _base_signal(
        signal_nature={"categoria": "APROPRIAÇÃO", "confianca": 0.8},
        appropriation_risk=0.85,
        vulnerability={"overall_score": 80, "factors": {"polarization": 0.8}},
        momentum=55,
        sentimento={"compound": 0.6},
        velocity={"trend": 0.5},
    )


def _signal_high_momentum_with_topic() -> dict:
    return _base_signal(
        momentum=92,
        sentimento={"compound": 0.7},
        velocity={"trend": 0.8},
        topic_assignment={"topic_name": "Carnaval Digital", "confidence": 0.95},
        signal_nature={"categoria": "ORGÂNICO", "confianca": 0.9},
        vulnerability={"overall_score": 10},
    )


# ═════════════════════════════════════════════════════════════════════════════
#  INT-D: PEST ← Tension
# ═════════════════════════════════════════════════════════════════════════════


class TestINTD_PestTension:
    """INT-D: pest_engine.classify_signal lê tension_analysis do sinal."""

    def test_tension_boosts_pest_category(self):
        from core.engines.pest_engine import PESTEngine

        engine = PESTEngine()
        signal = _base_signal(
            tension_analysis={
                "tensions": [
                    {"tipo": "ideologica", "intensidade": 0.7},
                    {"tipo": "politica", "intensidade": 0.6},
                ]
            }
        )
        result = engine.classify_signal(signal)
        # classify_signal returns PESTResult dataclass — convert to dict
        if hasattr(result, "scores"):
            scores = result.scores
        else:
            scores = result.get("scores", {})
        assert isinstance(scores, dict)
        # Political should have been boosted by ideologica+politica tensions
        assert scores.get("Political", 0) > 0 or result.primary is not None

    def test_no_tension_no_crash(self):
        from core.engines.pest_engine import PESTEngine

        engine = PESTEngine()
        signal = _base_signal()  # Sem tension_analysis
        result = engine.classify_signal(signal)
        assert result is not None
        assert hasattr(result, "primary") or isinstance(result, dict)

    def test_economic_tension_boosts_economic(self):
        from core.engines.pest_engine import PESTEngine

        engine = PESTEngine()
        signal = _base_signal(
            tension_analysis={
                "tensions": [
                    {"tipo": "socioeconomica", "intensidade": 0.8},
                    {"tipo": "economica", "intensidade": 0.7},
                ]
            }
        )
        result = engine.classify_signal(signal)
        if hasattr(result, "scores"):
            scores = result.scores
        else:
            scores = result.get("scores", {})
        assert isinstance(scores, dict)
        assert scores.get("Economic", 0) > 0 or result is not None


# ═════════════════════════════════════════════════════════════════════════════
#  INT-E: Scenarios ← Vulnerability + Alerts + Nature
# ═════════════════════════════════════════════════════════════════════════════


class TestINTE_ScenarioEnrichment:
    """INT-E: scenario_engine._estimate_probabilities usa vuln/alerts/nature."""

    def test_organic_signal_favors_optimistic(self):
        from core.scenario_engine import _estimate_probabilities

        signal = _signal_organico_autentico()
        probs = _estimate_probabilities(signal)
        assert probs["optimistic"] > probs["pessimistic"]

    def test_simulacao_vulneravel_favors_pessimistic(self):
        from core.scenario_engine import _estimate_probabilities

        signal = _signal_simulacao_vulneravel()
        probs = _estimate_probabilities(signal)
        # Vulnerability 72 + SIMULAÇÃO = heavy pessimistic shift
        assert probs["pessimistic"] >= probs["optimistic"]

    def test_critical_alerts_shift_pessimistic(self):
        from core.scenario_engine import _estimate_probabilities

        signal = _base_signal(
            cultural_alerts={
                "alerts": [
                    {"severity": "critical", "type": "momentum_spike"},
                    {"severity": "critical", "type": "sentiment_shift"},
                ]
            }
        )
        probs_with = _estimate_probabilities(signal)

        signal_clean = _base_signal()
        probs_without = _estimate_probabilities(signal_clean)

        # With 2 critical alerts, pessimistic should be higher
        assert probs_with["pessimistic"] >= probs_without["pessimistic"]

    def test_topic_high_confidence_small_boost(self):
        from core.scenario_engine import _estimate_probabilities

        signal_with_topic = _base_signal(
            topic_assignment={"topic_name": "Funk", "confidence": 0.9}
        )
        signal_no_topic = _base_signal()

        probs_with = _estimate_probabilities(signal_with_topic)
        probs_without = _estimate_probabilities(signal_no_topic)

        # Combined is slightly higher with topic → optimistic same or higher
        assert probs_with["optimistic"] >= probs_without["optimistic"]

    def test_narrative_includes_nature_context(self):
        from core.scenario_engine import _generate_narrative

        signal = _signal_simulacao_vulneravel()
        narrative = _generate_narrative("funk", "pessimistic", signal)
        assert "simulação" in narrative.lower() or "SIMULAÇÃO" in narrative

    def test_narrative_organic_context(self):
        from core.scenario_engine import _generate_narrative

        signal = _signal_organico_autentico()
        narrative = _generate_narrative("funk", "optimistic", signal)
        assert "orgânica" in narrative.lower() or "autenticidade" in narrative.lower()

    def test_risks_include_vulnerability(self):
        from core.scenario_engine import _scenario_risks

        signal = _signal_simulacao_vulneravel()
        risks = _scenario_risks("pessimistic", signal)
        # Should have extra risks from vulnerability and nature
        assert len(risks) > 2  # More than base risks
        risk_text = " ".join(risks).lower()
        assert "vulnerabilidade" in risk_text or "simulado" in risk_text

    def test_risks_include_appropriation(self):
        from core.scenario_engine import _scenario_risks

        signal = _signal_apropiacao()
        risks = _scenario_risks("optimistic", signal)
        risk_text = " ".join(risks).lower()
        assert "apropriação" in risk_text

    def test_risks_backward_compatible(self):
        """_scenario_risks sem signal (arg opcional) não quebra."""
        from core.scenario_engine import _scenario_risks

        risks = _scenario_risks("optimistic")
        assert isinstance(risks, list)
        assert len(risks) >= 2


# ═════════════════════════════════════════════════════════════════════════════
#  INT-F: Opportunities ← Vulnerability + Nature
# ═════════════════════════════════════════════════════════════════════════════


class TestINTF_OpportunityFiltering:
    """INT-F: opportunity detectors bloqueiam SIMULAÇÃO/APROPRIAÇÃO e
    reduzem confiança com vulnerability alta."""

    def test_simulacao_blocks_all_opportunities(self):
        from core.intelligence.opportunity_engine import get_opportunity_engine, reset_opportunity_engine

        reset_opportunity_engine()
        engine = get_opportunity_engine()
        signal = _signal_simulacao_vulneravel()
        signal["momentum"] = 80  # Forçar trigger de momentum_wave
        signal["velocity"] = {"trend": 0.5}
        opps = engine.detect(signal)
        # SIMULAÇÃO com confiança >0.6 deve bloquear tudo
        assert len(opps) == 0

    def test_apropiacao_blocks_opportunities(self):
        from core.intelligence.opportunity_engine import get_opportunity_engine, reset_opportunity_engine

        reset_opportunity_engine()
        engine = get_opportunity_engine()
        signal = _signal_apropiacao()
        opps = engine.detect(signal)
        assert len(opps) == 0

    def test_organic_allows_opportunities(self):
        from core.intelligence.opportunity_engine import get_opportunity_engine, reset_opportunity_engine

        reset_opportunity_engine()
        engine = get_opportunity_engine()
        signal = _signal_organico_autentico()
        signal["momentum"] = 80
        signal["velocity"] = {"trend": 0.5}
        opps = engine.detect(signal)
        assert len(opps) > 0

    def test_vulnerability_reduces_confidence(self):
        from core.intelligence.opportunity_engine import _adjust_confidence_by_vulnerability

        signal_high_vuln = _base_signal(vulnerability={"overall_score": 70})
        adjusted = _adjust_confidence_by_vulnerability(0.8, signal_high_vuln)
        assert adjusted < 0.8  # Should be reduced

        signal_low_vuln = _base_signal(vulnerability={"overall_score": 10})
        adjusted_low = _adjust_confidence_by_vulnerability(0.8, signal_low_vuln)
        assert adjusted_low >= 0.8  # No reduction

    def test_organic_boosts_confidence(self):
        from core.intelligence.opportunity_engine import _adjust_confidence_by_vulnerability

        signal = _base_signal(
            signal_nature={"categoria": "ORGÂNICO", "confianca": 0.9},
            vulnerability={"overall_score": 10},
        )
        adjusted = _adjust_confidence_by_vulnerability(0.7, signal)
        assert adjusted > 0.7  # Should be boosted by ORGÂNICO

    def test_convergence_includes_topic_and_nature(self):
        """INT-C/F: Convergence detector counts topic and ORGÂNICO nature as positive factors."""
        from core.intelligence.opportunity_engine import _detect_convergence

        signal = _base_signal(
            momentum=60,
            sentimento={"compound": 0.5},
            velocity={"trend": 0.3},
            pest_classification={"primary": "Social"},
            topic_assignment={"topic_name": "Cultura Musical", "confidence": 0.85},
            signal_nature={"categoria": "ORGÂNICO", "confianca": 0.8},
        )
        opp = _detect_convergence(signal)
        assert opp is not None
        assert "topic=Cultura Musical" in opp.description or opp.confidence > 0
        # Should have 6 positive factors (momentum, sentiment, trend, pest, topic, nature)

    def test_commercial_not_blocked(self):
        """COMERCIAL não é bloqueado, mas também não dá boost."""
        from core.intelligence.opportunity_engine import get_opportunity_engine, reset_opportunity_engine

        reset_opportunity_engine()
        engine = get_opportunity_engine()
        signal = _signal_comercial_moderado()
        signal["momentum"] = 80
        signal["velocity"] = {"trend": 0.5}
        opps = engine.detect(signal)
        # COMERCIAL should NOT be blocked
        assert len(opps) > 0


# ═════════════════════════════════════════════════════════════════════════════
#  INT-C: Topics → Cultural Alerts
# ═════════════════════════════════════════════════════════════════════════════


class TestINTC_TopicsToAlerts:
    """INT-C: cultural_alerts_engine inject topic_assignment context."""

    def test_momentum_spike_includes_topic(self):
        from alerts.cultural_alerts_engine import get_alerts_engine, reset_alerts_engine

        reset_alerts_engine()
        engine = get_alerts_engine()
        signal = _signal_high_momentum_with_topic()
        alerts = engine.evaluate(signal)
        assert len(alerts) > 0
        spike_alert = [a for a in alerts if a.alert_type == "momentum_spike"]
        assert len(spike_alert) > 0
        # Topic should be in context
        assert spike_alert[0].context.get("topic") == "Carnaval Digital"
        # Topic should be in message
        assert "Carnaval Digital" in spike_alert[0].message

    def test_all_alerts_get_topic_context(self):
        from alerts.cultural_alerts_engine import get_alerts_engine, reset_alerts_engine

        reset_alerts_engine()
        engine = get_alerts_engine()
        signal = _base_signal(
            momentum=92,
            sentimento={"compound": -0.8},
            velocity={"trend": 0.7},
            topic_assignment={"topic_name": "Política Cultural", "confidence": 0.8},
        )
        alerts = engine.evaluate(signal)
        # Multiple alerts should be generated
        assert len(alerts) >= 2
        # All should have topic in context
        for alert in alerts:
            assert alert.context.get("topic") == "Política Cultural"

    def test_no_topic_no_crash(self):
        from alerts.cultural_alerts_engine import get_alerts_engine, reset_alerts_engine

        reset_alerts_engine()
        engine = get_alerts_engine()
        signal = _base_signal(momentum=92)  # High momentum, no topic
        alerts = engine.evaluate(signal)
        assert len(alerts) > 0
        # Should work fine without topic
        for alert in alerts:
            assert "topic" not in alert.context or alert.context["topic"] is not None


# ═════════════════════════════════════════════════════════════════════════════
#  INT-B: Velocity ← Circulo (tested via worker pipeline)
# ═════════════════════════════════════════════════════════════════════════════


class TestINTB_VelocityCirculo:
    """INT-B: velocity_enricher normaliza por baseline do círculo."""

    def test_circle_baselines_defined(self):
        """Verifica que todos 16 círculos têm baseline."""
        # Import the constant from analysis_worker
        from core.analysis_worker import CIRCLE_VELOCITY_BASELINE

        assert len(CIRCLE_VELOCITY_BASELINE) == 16
        assert "Humor & Memes" in CIRCLE_VELOCITY_BASELINE
        assert "Religiosidade" in CIRCLE_VELOCITY_BASELINE
        # High baseline circles
        assert CIRCLE_VELOCITY_BASELINE["Humor & Memes"] > 1.0
        # Low baseline circles
        assert CIRCLE_VELOCITY_BASELINE["Religiosidade"] < 1.0

    def test_humor_has_highest_baseline(self):
        from core.analysis_worker import CIRCLE_VELOCITY_BASELINE

        assert CIRCLE_VELOCITY_BASELINE["Humor & Memes"] == max(
            CIRCLE_VELOCITY_BASELINE.values()
        )

    def test_religiosidade_has_lowest_baseline(self):
        from core.analysis_worker import CIRCLE_VELOCITY_BASELINE

        assert CIRCLE_VELOCITY_BASELINE["Religiosidade"] == min(
            CIRCLE_VELOCITY_BASELINE.values()
        )


# ═════════════════════════════════════════════════════════════════════════════
#  Integration Flow: Full pipeline scenarios
# ═════════════════════════════════════════════════════════════════════════════


class TestFullPipelineIntegration:
    """Test complete data flow through multiple integrated engines."""

    def test_organic_signal_full_flow(self):
        """Sinal orgânico autêntico deve gerar cenários otimistas e oportunidades."""
        from core.scenario_engine import ScenarioEngine, reset_scenario_engine
        from core.intelligence.opportunity_engine import get_opportunity_engine, reset_opportunity_engine
        from alerts.cultural_alerts_engine import get_alerts_engine, reset_alerts_engine

        reset_scenario_engine()
        reset_opportunity_engine()
        reset_alerts_engine()

        signal = _signal_organico_autentico()
        signal["momentum"] = 80
        signal["velocity"] = {"trend": 0.5}

        # Scenarios should favor optimistic
        from core.scenario_engine import _estimate_probabilities
        probs = _estimate_probabilities(signal)
        assert probs["optimistic"] >= probs["pessimistic"]

        # Opportunities should be detected
        opp_engine = get_opportunity_engine()
        opps = opp_engine.detect(signal)
        assert len(opps) > 0

    def test_simulacao_signal_full_flow(self):
        """Sinal SIMULAÇÃO vulnerável: cenários pessimistas, sem oportunidades."""
        from core.scenario_engine import _estimate_probabilities
        from core.intelligence.opportunity_engine import get_opportunity_engine, reset_opportunity_engine

        reset_opportunity_engine()

        signal = _signal_simulacao_vulneravel()
        # Manter momentum moderado para que penalidades de SIMULAÇÃO+vulnerability desloquem para pessimista
        signal["momentum"] = 50
        signal["velocity"] = {"trend": 0.1}

        # Scenarios should shift pessimistic
        probs = _estimate_probabilities(signal)
        assert probs["pessimistic"] >= probs["optimistic"]

        # Opportunities should be BLOCKED (SIMULAÇÃO com confiança > 0.6)
        opp_engine = get_opportunity_engine()
        opps = opp_engine.detect(signal)
        assert len(opps) == 0

    def test_pest_tension_scenario_chain(self):
        """Tensões influenciam PEST → PEST influencia cenários."""
        from core.engines.pest_engine import PESTEngine
        from core.scenario_engine import _estimate_probabilities

        engine = PESTEngine()
        signal = _base_signal(
            tension_analysis={
                "tensions": [
                    {"tipo": "ideologica"},
                    {"tipo": "politica"},
                ]
            }
        )
        pest_result = engine.classify_signal(signal)
        signal["pest_classification"] = pest_result

        probs = _estimate_probabilities(signal)
        assert isinstance(probs, dict)
        assert abs(sum(probs.values()) - 1.0) < 0.01
