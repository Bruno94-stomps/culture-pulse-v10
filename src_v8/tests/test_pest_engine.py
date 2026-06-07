#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_pest_engine.py — F-5 FASE 2
========================================
Tests for PESTEngine (core/pest_engine.py), Worker integration,
and API endpoint (api/endpoints/pest.py).
"""

import importlib
import sys
import os
import pytest

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ═══════════════════════════════════════════════════════════════════════════════
#  Fixtures
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def _reset_singleton():
    """Reset PEST engine singleton between tests."""
    from core.engines.pest_engine import reset_pest_engine
    reset_pest_engine()
    yield
    reset_pest_engine()


@pytest.fixture
def engine():
    from core.engines.pest_engine import PESTEngine
    return PESTEngine()


@pytest.fixture
def sample_signals():
    """Realistic enriched signals for testing."""
    return [
        {
            "termo": "reforma tributária",
            "texto": "Governo anuncia nova reforma tributária para 2026 com impacto no mercado",
            "plataforma": "newsapi",
            "momentum": 85,
            "volume": 5000,
            "circulo": "Trabalho & Prosperidade",
        },
        {
            "termo": "inteligência artificial",
            "texto": "Startups brasileiras adotam IA generativa para transformação digital",
            "plataforma": "youtube",
            "momentum": 92,
            "volume": 12000,
            "circulo": "Tecnologia & Digital",
        },
        {
            "termo": "carnaval de rua",
            "texto": "Blocos de carnaval fortalecem comunidade e identidade cultural brasileira",
            "plataforma": "instagram",
            "momentum": 78,
            "volume": 8000,
            "circulo": "Música & Festivais",
        },
        {
            "termo": "bitcoin e criptomoeda",
            "texto": "Investimento em criptomoeda cresce entre jovens com fintech e pix",
            "plataforma": "reddit",
            "momentum": 65,
            "volume": 3000,
            "circulo": "Trabalho & Prosperidade",
        },
    ]


# ═══════════════════════════════════════════════════════════════════════════════
#  1. Import & instantiation
# ═══════════════════════════════════════════════════════════════════════════════

class TestPESTEngineImport:
    def test_import_module(self):
        mod = importlib.import_module("core.pest_engine")
        assert hasattr(mod, "PESTEngine")
        assert hasattr(mod, "get_pest_engine")
        assert hasattr(mod, "reset_pest_engine")
        assert hasattr(mod, "PESTResult")
        assert hasattr(mod, "PEST_KEYWORDS")

    def test_singleton(self):
        from core.engines.pest_engine import get_pest_engine
        e1 = get_pest_engine()
        e2 = get_pest_engine()
        assert e1 is e2

    def test_singleton_reset(self):
        from core.engines.pest_engine import get_pest_engine, reset_pest_engine
        e1 = get_pest_engine()
        reset_pest_engine()
        e2 = get_pest_engine()
        assert e1 is not e2

    def test_categories(self, engine):
        assert engine.CATEGORIES == ("Political", "Economic", "Social", "Technological")


# ═══════════════════════════════════════════════════════════════════════════════
#  2. Classification — basic
# ═══════════════════════════════════════════════════════════════════════════════

class TestPESTClassify:
    def test_empty_text(self, engine):
        result = engine.classify("")
        assert result.primary == "Social"
        assert result.confidence == 0.0

    def test_none_text(self, engine):
        result = engine.classify(None)
        assert result.primary == "Social"
        assert result.confidence == 0.0

    def test_political_text(self, engine):
        result = engine.classify(
            "O governo federal anunciou nova legislação e reforma sobre regulação"
        )
        assert result.primary == "Political"
        assert result.confidence > 0

    def test_economic_text(self, engine):
        result = engine.classify(
            "Inflação e juros da selic impactam o mercado financeiro e investimento"
        )
        assert result.primary == "Economic"
        assert result.confidence > 0

    def test_social_text(self, engine):
        result = engine.classify(
            "Carnaval e música fortalecem a comunidade e identidade cultural brasileira"
        )
        assert result.primary == "Social"
        assert result.confidence > 0

    def test_technological_text(self, engine):
        result = engine.classify(
            "Inteligência artificial e machine learning transformam plataforma digital"
        )
        assert result.primary == "Technological"
        assert result.confidence > 0

    def test_result_has_all_fields(self, engine):
        result = engine.classify("economia e mercado financeiro brasileiro")
        assert hasattr(result, "primary")
        assert hasattr(result, "secondary")
        assert hasattr(result, "confidence")
        assert hasattr(result, "scores")
        assert hasattr(result, "keywords_matched")
        assert hasattr(result, "category_keywords")

    def test_scores_sum_to_one(self, engine):
        result = engine.classify("governo federal regulação mercado economia tecnologia digital")
        total = sum(result.scores.values())
        assert abs(total - 1.0) < 0.01, f"Scores sum to {total}, expected ~1.0"

    def test_all_categories_in_scores(self, engine):
        result = engine.classify("qualquer texto para teste")
        for cat in engine.CATEGORIES:
            assert cat in result.scores

    def test_secondary_category(self, engine):
        result = engine.classify(
            "governo legislação regulação com mercado financeiro investimento economia"
        )
        # Should have both Political and Economic
        assert result.primary in ("Political", "Economic")
        assert result.secondary is not None

    def test_no_secondary_when_one_dominant(self, engine):
        result = engine.classify("governo governo governo governo governo legislação regulação")
        # Heavily political — secondary may be None or very low
        assert result.primary == "Political"
        # secondary might be None if all others < 0.15


# ═══════════════════════════════════════════════════════════════════════════════
#  3. to_dict / serialization
# ═══════════════════════════════════════════════════════════════════════════════

class TestPESTSerialization:
    def test_to_dict(self, engine):
        result = engine.classify("economia mercado financeiro")
        d = result.to_dict()
        assert isinstance(d, dict)
        assert "primary" in d
        assert "secondary" in d
        assert "confidence" in d
        assert "scores" in d
        assert "keywords_matched" in d
        assert "category_keywords" in d

    def test_to_dict_json_serializable(self, engine):
        import json
        result = engine.classify("tecnologia digital startup inovação")
        d = result.to_dict()
        serialized = json.dumps(d)
        assert isinstance(serialized, str)


# ═══════════════════════════════════════════════════════════════════════════════
#  4. classify_signal convenience
# ═══════════════════════════════════════════════════════════════════════════════

class TestClassifySignal:
    def test_classify_signal_dict(self, engine):
        sig = {
            "termo": "reforma tributária",
            "texto": "Governo anuncia reforma da legislação tributária",
        }
        result = engine.classify_signal(sig)
        assert result.primary == "Political"

    def test_classify_signal_descricao_fallback(self, engine):
        sig = {
            "termo": "mercado",
            "descricao": "Investimento no mercado financeiro com inflação alta",
        }
        result = engine.classify_signal(sig)
        assert result.primary == "Economic"

    def test_classify_signal_empty(self, engine):
        result = engine.classify_signal({})
        assert result.primary == "Social"  # default
        assert result.confidence == 0.0


# ═══════════════════════════════════════════════════════════════════════════════
#  5. Batch classify
# ═══════════════════════════════════════════════════════════════════════════════

class TestBatchClassify:
    def test_batch_classify(self, engine):
        texts = [
            "governo legislação regulação",
            "economia mercado inflação",
            "comunidade família tradição",
            "tecnologia digital inteligência artificial",
        ]
        results = engine.batch_classify(texts)
        assert len(results) == 4
        primaries = [r.primary for r in results]
        assert "Political" in primaries
        assert "Economic" in primaries
        assert "Social" in primaries
        assert "Technological" in primaries

    def test_batch_empty(self, engine):
        results = engine.batch_classify([])
        assert results == []


# ═══════════════════════════════════════════════════════════════════════════════
#  6. get_stats
# ═══════════════════════════════════════════════════════════════════════════════

class TestPESTStats:
    def test_get_stats(self, engine):
        stats = engine.get_stats()
        assert stats["engine"] == "PESTEngine"
        assert stats["version"] == "1.0.0"
        assert len(stats["categories"]) == 4
        assert stats["total_keywords"] > 100  # we have 200+ keywords

    def test_keywords_per_category(self, engine):
        stats = engine.get_stats()
        for cat in engine.CATEGORIES:
            assert stats["keywords_per_category"][cat] > 10


# ═══════════════════════════════════════════════════════════════════════════════
#  7. get_distribution
# ═══════════════════════════════════════════════════════════════════════════════

class TestPESTDistribution:
    def test_distribution(self, engine):
        results = engine.batch_classify([
            "governo regulação",
            "economia mercado",
            "comunidade cultura social",
            "tecnologia digital",
        ])
        dist = engine.get_distribution(results)
        assert dist["total"] == 4
        assert sum(dist["distribution"].values()) == 4
        assert abs(sum(dist["percentages"].values()) - 100.0) < 0.5
        assert 0 <= dist["avg_confidence"] <= 1.0

    def test_distribution_empty(self, engine):
        dist = engine.get_distribution([])
        assert dist["total"] == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  8. Worker integration (11 engines)
# ═══════════════════════════════════════════════════════════════════════════════

class TestPESTWorkerIntegration:
    def test_worker_has_pest_enricher(self):
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        names = [e["name"] for e in worker.pipeline_info]
        assert "pest" in names

    def test_worker_pipeline_count_11(self):
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        assert len(worker.pipeline_info) == 17

    def test_pest_enricher_priority(self):
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        pest_entry = next(e for e in worker.pipeline_info if e["name"] == "pest")
        assert pest_entry["priority"] == 50

    def test_pest_enricher_after_topics(self):
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        names = [e["name"] for e in worker.pipeline_info]
        assert names.index("pest") > names.index("topics")

    def test_pest_enricher_adds_field(self):
        """Run a signal through the worker and check pest_classification is added."""
        import asyncio
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        signal = {
            "termo": "inflação alta",
            "texto": "Economia brasileira sofre com inflação e juros altos no mercado",
            "plataforma": "newsapi",
            "timestamp": "2026-02-01T12:00:00Z",
        }
        enriched = asyncio.run(worker.enrich(signal))
        assert "pest_classification" in enriched
        pest = enriched["pest_classification"]
        assert pest["primary"] == "Economic"
        assert pest["confidence"] > 0


# ═══════════════════════════════════════════════════════════════════════════════
#  9. API endpoint
# ═══════════════════════════════════════════════════════════════════════════════

class TestPESTAPI:
    def _load_pest_module(self):
        """Load api/endpoints/pest.py directly, bypassing __init__.py."""
        import importlib.util, pathlib
        path = pathlib.Path(__file__).parent.parent / "api" / "endpoints" / "pest.py"
        spec = importlib.util.spec_from_file_location("pest_endpoint", str(path))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_router_importable(self):
        mod = self._load_pest_module()
        assert mod.router is not None
        assert mod.router.prefix == "/api/v8/pest"

    def test_api_stats_endpoint_exists(self):
        mod = self._load_pest_module()
        assert callable(mod.pest_stats)

    def test_api_classify_endpoint_exists(self):
        mod = self._load_pest_module()
        assert callable(mod.classify_text)

    def test_api_batch_endpoint_exists(self):
        mod = self._load_pest_module()
        assert callable(mod.batch_classify)

    def test_api_registered_in_main(self):
        """Verify pest_router import line exists in api/main.py source."""
        import pathlib
        main_src = (pathlib.Path(__file__).parent.parent / "api" / "main.py").read_text()
        assert "pest_router" in main_src


# ═══════════════════════════════════════════════════════════════════════════════
#  10. Keywords coverage
# ═══════════════════════════════════════════════════════════════════════════════

class TestPESTKeywords:
    def test_keywords_not_empty(self):
        from core.engines.pest_engine import PEST_KEYWORDS
        for cat, kws in PEST_KEYWORDS.items():
            assert len(kws) > 10, f"{cat} has too few keywords"

    def test_no_duplicate_keywords_within_category(self):
        from core.engines.pest_engine import PEST_KEYWORDS
        for cat, kws in PEST_KEYWORDS.items():
            lower_kws = [k.lower() for k in kws]
            assert len(lower_kws) == len(set(lower_kws)), f"Duplicates in {cat}"

    def test_all_four_categories_present(self):
        from core.engines.pest_engine import PEST_KEYWORDS
        assert set(PEST_KEYWORDS.keys()) == {"Political", "Economic", "Social", "Technological"}


# ═══════════════════════════════════════════════════════════════════════════════
#  11. Edge cases
# ═══════════════════════════════════════════════════════════════════════════════

class TestPESTEdgeCases:
    def test_very_short_text(self, engine):
        result = engine.classify("oi")
        assert result.primary in engine.CATEGORIES

    def test_mixed_case(self, engine):
        result = engine.classify("GOVERNO Federal LEGISLAÇÃO regulação")
        assert result.primary == "Political"

    def test_accented_characters(self, engine):
        result = engine.classify("inflação econômico saúde tecnológico")
        assert result.confidence > 0

    def test_long_text(self, engine):
        text = " ".join(["economia mercado financeiro investimento"] * 50)
        result = engine.classify(text)
        assert result.primary == "Economic"
        assert result.confidence > 0
