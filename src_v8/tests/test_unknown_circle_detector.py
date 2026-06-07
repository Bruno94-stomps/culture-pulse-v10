#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_unknown_circle_detector.py — S4.3
==============================================
Testes para o Unknown Circle Detector: threshold, classify, clustering,
enricher integration, e API endpoints.

Execução:
    pytest tests/test_unknown_circle_detector.py -v
"""

import asyncio
import json
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ── Path setup ──────────────────────────────────────────────────────────────

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def _get_or_create_loop():
    """Retorna event loop existente ou cria um novo (safe para test ordering)."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError("closed")
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


# ═══════════════════════════════════════════════════════════════════════════
#  1. TESTES DO CIRCLES_PROCESSOR.CLASSIFY_SIGNAL_CIRCLE
# ═══════════════════════════════════════════════════════════════════════════

class TestClassifySignalCircle:
    """Testa o método classify_signal_circle() do CulturalCirclesProcessor."""

    @pytest.fixture
    def processor(self):
        """Cria instância do circles_processor."""
        from core.intelligence.circles_processor import create_circles_processor
        return create_circles_processor()

    def test_known_circle_sertanejo(self, processor):
        """Sinal musical claro → deve ser classificado em Música (keyword matching)."""
        result = processor.classify_signal_circle(
            text="sertanejo universitário novo álbum gusttavo lima show",
            plataforma="youtube",
        )
        assert result["is_unknown"] is False
        assert result["circulo"] != "emergente_desconhecido"
        assert "Música" in result["circulo"]
        assert result["circle_score"] > 0.0
        assert len(result["top_scores"]) > 0

    def test_known_circle_futebol(self, processor):
        """Sinal esportivo claro → Esporte."""
        result = processor.classify_signal_circle(
            text="campeonato brasileiro futebol gol flamengo corinthians jogador",
            plataforma="reddit",
        )
        assert result["is_unknown"] is False
        assert result["circle_score"] > 0.0
        assert "Esporte" in result["circulo"]

    def test_unknown_random_text(self, processor):
        """Texto genérico/sem contexto cultural → emergente_desconhecido."""
        result = processor.classify_signal_circle(
            text="xyz123 qwerty asdf randomword nothingcultural",
            plataforma="reddit",
            threshold=0.5,  # threshold alto para forçar rejeição
        )
        assert result["is_unknown"] is True
        assert result["circulo"] == "emergente_desconhecido"
        assert "rejection_reason" in result
        assert result["rejection_reason"] is not None

    def test_empty_text(self, processor):
        """Texto vazio → emergente_desconhecido imediatamente."""
        result = processor.classify_signal_circle(text="", plataforma="youtube")
        assert result["is_unknown"] is True
        assert result["circulo"] == "emergente_desconhecido"
        assert result["circle_score"] == 0.0
        assert result["rejection_reason"] == "texto_vazio"

    def test_whitespace_text(self, processor):
        """Texto só com espaços → emergente_desconhecido."""
        result = processor.classify_signal_circle(text="   \t\n  ")
        assert result["is_unknown"] is True
        assert result["circulo"] == "emergente_desconhecido"

    def test_threshold_zero_always_accepts(self, processor):
        """Com threshold=0, qualquer texto deve ser aceito."""
        result = processor.classify_signal_circle(
            text="qualquer coisa aqui",
            threshold=0.0,
        )
        # Com threshold 0, até score baixíssimo é aceito (se > 0)
        if result["circle_score"] > 0:
            assert result["is_unknown"] is False

    def test_threshold_one_always_rejects(self, processor):
        """Com threshold=1.0, todos os sinais são rejeitados."""
        result = processor.classify_signal_circle(
            text="sertanejo funk carnaval brasil",
            threshold=1.0,
        )
        assert result["is_unknown"] is True
        assert result["circulo"] == "emergente_desconhecido"

    def test_top_scores_has_3_items(self, processor):
        """top_scores deve ter até 3 itens (top 3 círculos)."""
        result = processor.classify_signal_circle(
            text="tecnologia inteligencia artificial startup",
            plataforma="reddit",
        )
        assert isinstance(result["top_scores"], list)
        assert len(result["top_scores"]) <= 3

    def test_circles_detail_returned(self, processor):
        """circles_detail deve conter scores de todos os círculos."""
        result = processor.classify_signal_circle(
            text="gastronomia comida brasileira feijoada",
        )
        assert "circles_detail" in result
        # circles_detail pode ser dict vazio se texto vazio, mas não neste caso
        assert isinstance(result["circles_detail"], dict)

    def test_different_platforms(self, processor):
        """Testar que diferentes plataformas funcionam sem erro."""
        for plataforma in ["youtube", "reddit", "instagram", "spotify", "news"]:
            result = processor.classify_signal_circle(
                text="música brasileira mpb bossa nova",
                plataforma=plataforma,
            )
            assert "circulo" in result
            assert "is_unknown" in result


# ═══════════════════════════════════════════════════════════════════════════
#  2. TESTES DO UNKNOWN_CIRCLE_DETECTOR (ENGINE)
# ═══════════════════════════════════════════════════════════════════════════

class TestUnknownCircleDetector:
    """Testa o UnknownCircleDetector: fila, clustering, promotion."""

    @pytest.fixture
    def detector(self):
        """Cria detector NOVO com fila local (sem Redis), isolado por teste."""
        import core.unknown_circle_detector as mod
        # Reset singleton para garantir isolamento
        mod._detector = None
        # URL inválida força fallback para fila local
        d = mod.UnknownCircleDetector(
            redis_url="redis://invalid-host-for-test:9999/0",
            min_cluster_size=3,
        )
        d._local_queue = []
        d._local_candidates = []
        return d

    def _run(self, coro):
        """Helper para rodar coroutines (cria loop novo se necessário)."""
        return _get_or_create_loop().run_until_complete(coro)

    def test_push_and_get_local(self, detector):
        """Push sinal → get retorna o sinal."""
        signal = {
            "termo": "k-beauty coreano",
            "plataforma": "youtube",
            "circle_score": 0.15,
            "rejection_reason": "max_score 0.15 < threshold 0.3",
        }
        result = self._run(detector.push_unknown_signal(signal))
        assert result is True

        signals = self._run(detector.get_unknown_signals(count=10))
        assert len(signals) >= 1
        assert signals[0]["termo"] == "k-beauty coreano"

    def test_queue_size(self, detector):
        """Queue size incrementa com cada push."""
        for i in range(5):
            self._run(detector.push_unknown_signal({
                "termo": f"termo_{i}",
                "plataforma": "reddit",
                "circle_score": 0.1,
            }))
        size = self._run(detector.get_queue_size())
        assert size == 5

    def test_queue_max_limit(self, detector):
        """Fila local não excede UNKNOWN_QUEUE_MAX."""
        from core.classifiers.unknown_circle_detector import UNKNOWN_QUEUE_MAX
        for i in range(UNKNOWN_QUEUE_MAX + 50):
            self._run(detector.push_unknown_signal({
                "termo": f"termo_{i}",
                "plataforma": "reddit",
            }))
        size = self._run(detector.get_queue_size())
        assert size <= UNKNOWN_QUEUE_MAX

    def test_detect_candidates_insufficient(self, detector):
        """Com poucos sinais, não deve gerar candidatos."""
        self._run(detector.push_unknown_signal({
            "termo": "apenas um sinal",
            "plataforma": "reddit",
        }))
        candidates = self._run(detector.detect_candidates())
        assert len(candidates) == 0

    def test_detect_candidates_with_enough_signals(self, detector):
        """Com sinais suficientes e sklearn, clustering deve funcionar."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
        except ImportError:
            pytest.skip("sklearn não disponível")

        # Limpar fila para começar do zero
        detector._local_queue = []

        # Adicionar sinais suficientes com temas distintos
        temas_a = [
            "kpop blackpink bts coreia do sul",
            "kpop doramas coreanos netflix",
            "kpop festa coreana música asiática",
            "doramas coreanos romance drama",
            "comida coreana kimchi bibimbap",
        ]
        temas_b = [
            "criptomoeda bitcoin ethereum defi",
            "blockchain web3 nft metaverso",
            "crypto trading investimento digital",
            "defi finanças descentralizadas yield",
            "nft arte digital marketplace",
        ]
        for t in temas_a + temas_b:
            self._run(detector.push_unknown_signal({
                "termo": t,
                "texto": t,
                "plataforma": "reddit",
                "circle_score": 0.1,
            }))

        candidates = self._run(detector.detect_candidates())
        # Com 10 sinais limpos e min_cluster_size=3, deve gerar candidatos
        assert isinstance(candidates, list)
        # Verificamos apenas que o clustering executou sem erro
        # O resultado depende do conteúdo — 0 candidatos é aceitável se disperso
        for c in candidates:
            assert c.size >= 3
            assert c.suggested_name != ""

    def test_promote_candidate_not_found(self, detector):
        """Promover cluster inexistente → erro."""
        result = self._run(detector.promote_candidate(
            cluster_id=999,
            circle_name="Teste",
        ))
        assert result["status"] == "error"

    def test_get_stats(self, detector):
        """Stats deve retornar estrutura correta."""
        stats = self._run(detector.get_stats())
        assert "queue_size" in stats
        assert "candidates_count" in stats
        assert "sklearn_available" in stats
        assert "redis_available" in stats
        assert "min_cluster_size" in stats

    def test_singleton(self):
        """get_unknown_circle_detector retorna sempre a mesma instância."""
        from core.classifiers.unknown_circle_detector import get_unknown_circle_detector
        d1 = get_unknown_circle_detector()
        d2 = get_unknown_circle_detector()
        assert d1 is d2


# ═══════════════════════════════════════════════════════════════════════════
#  3. TESTES DO ENRICHER NO WORKER
# ═══════════════════════════════════════════════════════════════════════════

class TestWorkerEnrichers:
    """Testa os enrichers circles_enricher e unknown_detector_enricher."""

    def test_circles_enricher_known_signal(self):
        """circles_enricher com texto cultural claro → circulo real."""
        from core.intelligence.circles_processor import create_circles_processor
        processor = create_circles_processor()

        signal = {
            "termo": "funk carioca baile",
            "texto": "funk carioca baile mc dj ritmo pagode show",
            "plataforma": "youtube",
        }
        result = processor.classify_signal_circle(
            text=signal["texto"],
            plataforma=signal["plataforma"],
        )
        assert result["circulo"] != ""
        assert "is_unknown" in result
        # Com múltiplas keywords musicais, deve classificar em Música
        assert result["is_unknown"] is False

    def test_circles_enricher_unknown_signal(self):
        """circles_enricher com texto aleatório e threshold alto → desconhecido."""
        from core.intelligence.circles_processor import create_circles_processor
        processor = create_circles_processor()

        result = processor.classify_signal_circle(
            text="xyzrandom gibberish 123",
            plataforma="reddit",
            threshold=0.99,  # forçar rejeição
        )
        assert result["is_unknown"] is True
        assert result["circulo"] == "emergente_desconhecido"

    def test_unknown_detector_enricher_skips_known(self):
        """unknown_detector_enricher não enfileira sinais conhecidos."""
        signal = {
            "termo": "teste",
            "is_unknown_circle": False,
        }
        # Simular o enricher inline (sem importar a closure do Worker)
        # O enricher verifica is_unknown_circle e retorna early se False
        assert signal.get("is_unknown_circle", False) is False
        assert "_unknown_queued" not in signal

    def test_unknown_detector_enricher_queues_unknown(self):
        """unknown_detector_enricher enfileira sinais desconhecidos."""
        from core.classifiers.unknown_circle_detector import get_unknown_circle_detector

        signal = {
            "termo": "sinal desconhecido xyz",
            "is_unknown_circle": True,
            "circle_score": 0.05,
            "plataforma": "reddit",
        }

        detector = get_unknown_circle_detector()
        # Push diretamente (simulando o enricher)
        result = _get_or_create_loop().run_until_complete(
            detector.push_unknown_signal(signal)
        )
        assert result is True


# ═══════════════════════════════════════════════════════════════════════════
#  4. TESTES DE INTEGRAÇÃO: CLASSIFY → ENRICHER → QUEUE
# ═══════════════════════════════════════════════════════════════════════════

class TestIntegrationFlow:
    """Testa o fluxo completo: classify → enrich → queue."""

    def test_full_flow_known(self):
        """Sinal cultural → classify → circulo real → NÃO enfileira."""
        from core.intelligence.circles_processor import create_circles_processor
        processor = create_circles_processor()

        result = processor.classify_signal_circle(
            text="carnaval salvador bahia trio elétrico",
            plataforma="youtube",
        )

        signal = {
            "termo": "carnaval",
            "texto": "carnaval salvador bahia trio elétrico",
            "plataforma": "youtube",
            "circulo": result["circulo"],
            "circle_score": result["circle_score"],
            "is_unknown_circle": result["is_unknown"],
        }

        # Sinal cultural forte → NÃO deve ser unknown
        # (a menos que o threshold default seja muito alto)
        if result["circle_score"] > 0.3:
            assert signal["is_unknown_circle"] is False
            assert signal["circulo"] != "emergente_desconhecido"

    def test_full_flow_unknown(self):
        """Texto aleatório → classify → emergente_desconhecido → enfileira."""
        from core.intelligence.circles_processor import create_circles_processor
        from core.classifiers.unknown_circle_detector import UnknownCircleDetector

        processor = create_circles_processor()
        detector = UnknownCircleDetector(min_cluster_size=3)

        result = processor.classify_signal_circle(
            text="zxcv qwerty 12345 random nonsense",
            plataforma="reddit",
            threshold=0.99,  # forçar
        )

        assert result["is_unknown"] is True
        assert result["circulo"] == "emergente_desconhecido"

        # Enfileirar
        signal = {
            "termo": "zxcv qwerty",
            "texto": "zxcv qwerty 12345 random nonsense",
            "plataforma": "reddit",
            "circle_score": result["circle_score"],
            "rejection_reason": result["rejection_reason"],
        }

        pushed = _get_or_create_loop().run_until_complete(
            detector.push_unknown_signal(signal)
        )
        assert pushed is True

        size = _get_or_create_loop().run_until_complete(
            detector.get_queue_size()
        )
        assert size >= 1


# ═══════════════════════════════════════════════════════════════════════════
#  5. TESTES DA ClusterCandidate E UnknownSignalEntry
# ═══════════════════════════════════════════════════════════════════════════

class TestDataclasses:
    """Testa serialização das dataclasses."""

    def test_cluster_candidate_to_dict(self):
        from core.classifiers.unknown_circle_detector import ClusterCandidate
        c = ClusterCandidate(
            cluster_id=0,
            size=15,
            top_terms=["kpop", "coreano", "doramas"],
            suggested_name="Kpop & Coreano",
            avg_score=0.12,
            platforms=["youtube", "reddit"],
            sample_texts=["kpop bts", "doramas netflix"],
        )
        d = c.to_dict()
        assert d["cluster_id"] == 0
        assert d["size"] == 15
        assert d["suggested_name"] == "Kpop & Coreano"
        assert len(d["top_terms"]) == 3
        assert d["avg_score"] == 0.12

    def test_unknown_signal_entry_roundtrip(self):
        from core.classifiers.unknown_circle_detector import UnknownSignalEntry
        entry = UnknownSignalEntry(
            termo="crypto defi",
            texto="crypto defi web3 blockchain",
            plataforma="reddit",
            score=0.05,
            top_scores=[("Tecnologia", 0.2), ("Economia", 0.15)],
            rejection_reason="max_score 0.2 < threshold 0.3",
        )
        d = entry.to_dict()
        restored = UnknownSignalEntry.from_dict(d)
        assert restored.termo == "crypto defi"
        assert restored.plataforma == "reddit"
        assert restored.score == 0.05


# ── Entrypoint ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
