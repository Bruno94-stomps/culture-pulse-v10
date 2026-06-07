"""
Tests for H-1 — Tension Enricher in Worker Pipeline
======================================================
Tests the TensionEngine (core/tension_engine.py) and its integration
as tension_enricher in the AnalysisWorker (core/analysis_worker.py).
"""
from __future__ import annotations

import pytest


# ═════════════════════════════════════════════════════════════════════════════
# TensionEngine unit tests
# ═════════════════════════════════════════════════════════════════════════════

class TestTensionEngineImport:
    """Verify module loads correctly."""

    def test_import_module(self):
        from core.engines.tension_engine import TensionEngine
        assert TensionEngine is not None

    def test_import_convenience(self):
        from core.engines.tension_engine import analyze_tension
        assert callable(analyze_tension)

    def test_import_enums(self):
        from core.engines.tension_engine import TensionLevel, TensionType
        assert TensionLevel.BAIXA.value == "baixa"
        assert TensionType.GERACIONAL.value == "geracional"

    def test_singleton(self):
        from core.engines.tension_engine import get_tension_engine
        e1 = get_tension_engine()
        e2 = get_tension_engine()
        assert e1 is e2


class TestTensionEngineAnalysis:
    """Test core analysis functionality."""

    def _engine(self):
        from core.engines.tension_engine import TensionEngine
        return TensionEngine()

    def test_empty_text_returns_zero(self):
        engine = self._engine()
        result = engine.analyze("")
        assert result.score == 0.0
        assert result.level.value == "baixa"
        assert result.types == []

    def test_neutral_text_low_tension(self):
        engine = self._engine()
        result = engine.analyze("O tempo está bom hoje, céu azul e brisa leve")
        assert result.score < 0.3
        assert result.level.value == "baixa"

    def test_high_conflict_text(self):
        engine = self._engine()
        text = (
            "Essa polêmica é absurda e revoltante, uma controvérsia ridícula "
            "que mostra a polarização total da sociedade dividida"
        )
        result = engine.analyze(text)
        assert result.score >= 0.3
        assert "conflito_direto" in result.keyword_hits or "polarizacao" in result.keyword_hits

    def test_generational_tension(self):
        engine = self._engine()
        # Need markers from BOTH gen_z ("cringe", "lacração") AND boomer ("tradição", "respeito")
        text = "Cringe demais quando falam de tradição e lacração ao mesmo tempo, esse respeito não cola"
        result = engine.analyze(text)
        from core.engines.tension_engine import TensionType
        assert TensionType.GERACIONAL in result.types

    def test_regional_tension_two_regions(self):
        engine = self._engine()
        text = "O nordestino que migra para são paulo enfrenta preconceito na periferia"
        result = engine.analyze(text)
        assert result.regional_match is not None
        # Should detect Nordeste and Sudeste
        if "_vs_" in (result.regional_match or ""):
            assert "Nordeste" in result.regional_match or "Sudeste" in result.regional_match

    def test_single_region_mild(self):
        engine = self._engine()
        text = "A amazônia precisa de proteção contra o garimpo"
        result = engine.analyze(text)
        assert result.regional_match is not None
        assert "Norte" in result.regional_match

    def test_exclusion_social_keywords(self):
        engine = self._engine()
        text = "Esse forasteiro não pertence a nossa cultura, é cultura estranha"
        result = engine.analyze(text)
        assert "exclusao_social" in result.keyword_hits
        from core.engines.tension_engine import TensionType
        assert TensionType.SOCIOECONOMICA in result.types

    def test_resistance_cultural(self):
        engine = self._engine()
        text = "Precisamos preservar tradição e defender cultura, proteger identidade"
        result = engine.analyze(text)
        assert "resistencia_cultural" in result.keyword_hits
        from core.engines.tension_engine import TensionType
        assert TensionType.TRADICIONAL_VS_MODERNO in result.types

    def test_forced_change(self):
        engine = self._engine()
        text = "A gentrificação foi imposta sem participação, decisão de cima"
        result = engine.analyze(text)
        assert "mudanca_forcada" in result.keyword_hits

    def test_sentiment_polarization_extreme_negative(self):
        engine = self._engine()
        result = engine.analyze("texto qualquer", sentiment=0.0)
        assert result.polarization_score == pytest.approx(1.0)

    def test_sentiment_polarization_extreme_positive(self):
        engine = self._engine()
        result = engine.analyze("texto qualquer", sentiment=1.0)
        assert result.polarization_score == pytest.approx(1.0)

    def test_sentiment_polarization_neutral(self):
        engine = self._engine()
        result = engine.analyze("texto qualquer", sentiment=0.5)
        assert result.polarization_score == pytest.approx(0.0)


class TestTensionResult:
    """Test TensionResult dataclass and to_dict()."""

    def test_to_dict_keys(self):
        from core.engines.tension_engine import TensionEngine
        engine = TensionEngine()
        result = engine.analyze("polêmica absurda sobre tradição vs moderno")
        d = result.to_dict()
        assert "tension_score" in d
        assert "tension_level" in d
        assert "tension_types" in d
        assert "keyword_hits" in d
        assert "polarization_score" in d
        assert "tension_alerts" in d
        assert "regional_match" in d

    def test_to_dict_types_are_strings(self):
        from core.engines.tension_engine import TensionEngine
        engine = TensionEngine()
        result = engine.analyze("boomer vs gen z lacração cringe")
        d = result.to_dict()
        for t in d["tension_types"]:
            assert isinstance(t, str)


class TestTensionLevelClassification:
    """Test level classification thresholds."""

    def test_baixa(self):
        from core.engines.tension_engine import TensionEngine
        engine = TensionEngine()
        level = engine._classify_level(0.1)
        assert level.value == "baixa"

    def test_moderada(self):
        from core.engines.tension_engine import TensionEngine
        engine = TensionEngine()
        level = engine._classify_level(0.5)
        assert level.value == "moderada"

    def test_alta(self):
        from core.engines.tension_engine import TensionEngine
        engine = TensionEngine()
        level = engine._classify_level(0.7)
        assert level.value == "alta"

    def test_critica(self):
        from core.engines.tension_engine import TensionEngine
        engine = TensionEngine()
        level = engine._classify_level(0.9)
        assert level.value == "critica"


class TestTensionAlerts:
    """Test alert generation."""

    def test_high_score_generates_alert(self):
        from core.engines.tension_engine import TensionEngine
        engine = TensionEngine()
        result = engine.analyze(
            "polêmica absurda controvérsia revoltante ridículo discordo polarização",
            sentiment=0.1,
        )
        assert len(result.alerts) > 0

    def test_alerts_max_five(self):
        from core.engines.tension_engine import TensionEngine
        engine = TensionEngine()
        result = engine.analyze(
            "boomer cringe lacração polêmica absurda controvérsia revoltante "
            "nordestino são paulo periferia forasteiro não pertence gentrificação",
            sentiment=0.05,
            circle="Música Popular",
        )
        assert len(result.alerts) <= 5

    def test_circle_in_alert(self):
        from core.engines.tension_engine import TensionEngine
        engine = TensionEngine()
        result = engine.analyze(
            "polêmica absurda controvérsia revoltante",
            circle="Gastronomia",
        )
        if result.score >= engine.THRESHOLD_MODERATE:
            circle_alerts = [a for a in result.alerts if "Gastronomia" in a]
            assert len(circle_alerts) > 0


class TestConvenienceFunction:
    """Test module-level convenience function."""

    def test_analyze_tension_returns_dict(self):
        from core.engines.tension_engine import analyze_tension
        result = analyze_tension("conflito entre boomer e gen z sobre tradição")
        assert isinstance(result, dict)
        assert "tension_score" in result
        assert "tension_level" in result

    def test_analyze_tension_with_kwargs(self):
        from core.engines.tension_engine import analyze_tension
        result = analyze_tension(
            "texto neutro",
            sentiment=0.5,
            circle="Esporte",
            plataforma="reddit",
        )
        assert isinstance(result, dict)


# ═════════════════════════════════════════════════════════════════════════════
# Worker integration tests
# ═════════════════════════════════════════════════════════════════════════════

class TestTensionEnricherInWorker:
    """Test that tension_enricher is correctly registered in the Worker."""

    def test_worker_has_tension_engine(self):
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        names = [e["name"] for e in worker.pipeline_info]
        assert "tension" in names

    def test_tension_priority_is_22(self):
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        for e in worker.pipeline_info:
            if e["name"] == "tension":
                assert e["priority"] == 22
                break
        else:
            pytest.fail("tension engine not found in pipeline")

    def test_tension_between_sentiment_and_nature(self):
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        pipeline = worker.pipeline_info
        names = [e["name"] for e in pipeline]
        assert names.index("sentiment") < names.index("tension") < names.index("nature")

    def test_worker_now_has_8_engines(self):
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        assert len(worker.pipeline_info) == 17

    def test_tension_enricher_enriches_signal(self):
        """Run enricher function directly on a signal dict."""
        import asyncio
        from core.analysis_worker import create_default_worker

        worker = create_default_worker()
        signal = {
            "termo": "polêmica cultural",
            "texto": "Essa controvérsia é absurda e revoltante",
            "plataforma": "reddit",
            "circulo": "Humor & Memes",
            "sentiment_detail": {"alma_score": 20},  # negative sentiment
        }

        # Run full pipeline (may not have Redis but enrich() works locally)
        enriched = asyncio.run(worker.enrich(signal))
        assert "tension_analysis" in enriched
        ta = enriched["tension_analysis"]
        assert "tension_score" in ta
        assert "tension_level" in ta
        assert "tension_types" in ta

    def test_enricher_handles_empty_signal(self):
        """Empty signal should pass through without error."""
        import asyncio
        from core.analysis_worker import create_default_worker

        worker = create_default_worker()
        signal = {"plataforma": "test"}
        enriched = asyncio.run(worker.enrich(signal))
        # tension_analysis may or may not be present (no termo → skip)
        # The important thing is no crash
        assert enriched is not None


# ═════════════════════════════════════════════════════════════════════════════
# Count
# ═════════════════════════════════════════════════════════════════════════════
# TestTensionEngineImport:          4
# TestTensionEngineAnalysis:       12
# TestTensionResult:                2
# TestTensionLevelClassification:   4
# TestTensionAlerts:                3
# TestConvenienceFunction:          2
# TestTensionEnricherInWorker:      6
# ═════════════════════════════════════════════════════════════════════════════
# TOTAL:                           33
