"""
tests/test_topic_engine.py — INT-2 FASE 2
============================================
Tests for TopicEngine (core/topic_engine.py) and its integration
as topic_enricher in the AnalysisWorker pipeline.

Run:
    pytest tests/test_topic_engine.py -v
"""
from __future__ import annotations

import sys, os
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1: IMPORTS & BASICS
# ═════════════════════════════════════════════════════════════════════════════

class TestTopicEngineImport:
    """Verify module loads correctly."""

    def test_import_engine(self):
        from core.intelligence.topic_engine import TopicEngine
        assert TopicEngine is not None

    def test_import_singleton(self):
        from core.intelligence.topic_engine import get_topic_engine
        assert callable(get_topic_engine)

    def test_import_dataclasses(self):
        from core.intelligence.topic_engine import MacroTopic, TopicAssignment
        assert MacroTopic is not None
        assert TopicAssignment is not None

    def test_import_constants(self):
        from core.intelligence.topic_engine import (
            DEFAULT_N_TOPICS,
            MIN_DOCS_TO_FIT,
            MAX_BUFFER_SIZE,
            REFIT_INTERVAL,
            STOPWORDS_PT,
        )
        assert DEFAULT_N_TOPICS == 8
        assert MIN_DOCS_TO_FIT == 20
        assert MAX_BUFFER_SIZE == 2000
        assert REFIT_INTERVAL == 50
        assert "é" in STOPWORDS_PT

    def test_singleton_same_instance(self):
        from core.intelligence.topic_engine import get_topic_engine
        e1 = get_topic_engine()
        e2 = get_topic_engine()
        assert e1 is e2

    def test_has_sklearn_flag(self):
        from core.intelligence.topic_engine import _HAS_SKLEARN
        assert isinstance(_HAS_SKLEARN, bool)


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2: DATACLASSES
# ═════════════════════════════════════════════════════════════════════════════

class TestDataclasses:
    """Test MacroTopic and TopicAssignment."""

    def test_macro_topic_to_dict(self):
        from core.intelligence.topic_engine import MacroTopic
        mt = MacroTopic(
            topic_id=0,
            label="Topic-0",
            top_terms=["funk", "carioca"],
            top_weights=[0.123456, 0.098765],
            n_documents=10,
        )
        d = mt.to_dict()
        assert d["topic_id"] == 0
        assert d["label"] == "Topic-0"
        assert d["top_terms"] == ["funk", "carioca"]
        assert d["top_weights"] == [0.1235, 0.0988]  # rounded to 4dp
        assert d["n_documents"] == 10

    def test_topic_assignment_to_dict(self):
        from core.intelligence.topic_engine import TopicAssignment
        ta = TopicAssignment(
            macro_topic=2,
            macro_label="Topic-2",
            top_terms=["sertanejo", "caipira"],
            confidence=0.876543,
        )
        d = ta.to_dict()
        assert d["macro_topic"] == 2
        assert d["confidence"] == 0.8765


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3: BUFFER MANAGEMENT
# ═════════════════════════════════════════════════════════════════════════════

class TestBufferManagement:
    """Test add_document and buffer logic."""

    def _fresh_engine(self):
        from core.intelligence.topic_engine import TopicEngine
        return TopicEngine(n_topics=4)

    def test_add_document_basic(self):
        engine = self._fresh_engine()
        engine.add_document("funk carioca baile")
        assert engine.buffer_size == 1

    def test_add_empty_doc_ignored(self):
        engine = self._fresh_engine()
        engine.add_document("")
        engine.add_document("   ")
        assert engine.buffer_size == 0

    def test_add_multiple(self):
        engine = self._fresh_engine()
        for i in range(10):
            engine.add_document(f"documento cultural numero {i}")
        assert engine.buffer_size == 10

    def test_buffer_trimmed_at_max(self):
        from core.intelligence.topic_engine import MAX_BUFFER_SIZE
        engine = self._fresh_engine()
        for i in range(MAX_BUFFER_SIZE + 50):
            engine.add_document(f"doc{i} cultural texto exemplo")
        assert engine.buffer_size <= MAX_BUFFER_SIZE

    def test_documents_lowercased(self):
        engine = self._fresh_engine()
        engine.add_document("FUNK Carioca BAILE")
        assert engine._buffer[0] == "funk carioca baile"


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 4: FIT
# ═════════════════════════════════════════════════════════════════════════════

class TestFit:
    """Test LDA fitting."""

    def _fresh_engine(self):
        from core.intelligence.topic_engine import TopicEngine
        return TopicEngine(n_topics=3)

    def test_fit_insufficient_docs(self):
        engine = self._fresh_engine()
        for i in range(5):
            engine.add_document(f"doc {i}")
        result = engine.fit()
        assert result["status"] == "insufficient_docs"
        assert engine.is_fitted is False

    def test_fit_sufficient_docs(self):
        """With enough diverse docs, LDA fits successfully."""
        engine = self._fresh_engine()
        docs = [
            # Topic 1: music
            "funk carioca baile pancadão ritmo",
            "sertanejo universitário viola modão caipira",
            "bossa nova jazz samba acordes harmonia",
            "pagode samba roda cerveja boteco mesa",
            "rock brasileiro legião urbana renato russo",
            "mpb caetano veloso gilberto gil tropicália",
            "forró xote baião luiz gonzaga",
            # Topic 2: food
            "feijoada arroz feijão comida brasileira",
            "churrasco picanha costela carvão gaúcho",
            "acarajé vatapá bahia dendê pimenta",
            "pão queijo minas gerais café manhã",
            "açaí tapioca mandioca amazônia",
            # Topic 3: sports
            "futebol gol campeonato brasileiro série",
            "seleção brasileira copa mundo fifa",
            "corinthians flamengo palmeiras são paulo",
            "vôlei basquete olimpíadas atleta treino",
            "fórmula piloto corrida automobilismo pista",
            "surf praia onda litoral brasileiro",
            "capoeira luta dança cultura afro",
            "jiu jitsu artes marciais academia treino",
        ]
        for d in docs:
            engine.add_document(d)

        result = engine.fit()
        assert result["status"] == "ok"
        assert result["n_topics"] >= 1
        assert engine.is_fitted is True

    def test_fit_creates_topics(self):
        """After fitting, topics list is populated."""
        engine = self._fresh_engine()
        docs = [
            "funk carioca baile pancadão ritmo dança",
            "sertanejo universitário viola modão caipira",
            "bossa nova jazz samba acordes harmonia",
            "feijoada arroz feijão comida brasileira",
            "churrasco picanha costela carvão gaúcho",
            "acarajé vatapá bahia dendê pimenta",
            "futebol gol campeonato brasileiro série",
            "seleção brasileira copa mundo fifa",
            "capoeira luta dança cultura afro brasileira",
            "rock brasileiro legião urbana renato russo",
            "pagode samba roda cerveja boteco mesa",
            "forró xote baião luiz gonzaga nordeste",
            "pão queijo minas gerais café manhã delícia",
            "açaí tapioca mandioca amazônia fruta",
            "surf praia onda litoral brasileiro verão",
            "jiu jitsu artes marciais academia treino",
            "vôlei basquete olimpíadas atleta medalha",
            "fórmula piloto corrida automobilismo pista",
            "carnaval bloco trio elétrico axé",
            "festa junina quadrilha fogueira milho",
            "hip hop rap periferias rima batalha",
            "circo teatro palhaço espetáculo artes",
            "cinema nacional filme documentário roteiro",
            "grafite street arte mural urbano",
            "literatura cordel poesia nordestina xilogravura",
        ]
        for d in docs:
            engine.add_document(d)
        engine.fit()
        hierarchy = engine.get_hierarchy()
        assert hierarchy["n_topics"] >= 1
        assert len(hierarchy["topics"]) >= 1

    def test_fit_increments_count(self):
        engine = self._fresh_engine()
        docs = [f"documento cultural diverso numero {i} arte musica" for i in range(25)]
        for d in docs:
            engine.add_document(d)
        engine.fit()
        assert engine._fit_count >= 1
        engine.fit()
        assert engine._fit_count >= 2


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 5: PREDICT
# ═════════════════════════════════════════════════════════════════════════════

class TestPredict:
    """Test topic prediction."""

    def _fresh_engine(self):
        from core.intelligence.topic_engine import TopicEngine
        return TopicEngine(n_topics=3)

    def test_predict_before_fit(self):
        engine = self._fresh_engine()
        assignment = engine.predict("funk carioca")
        assert assignment.macro_topic == -1
        assert assignment.macro_label == "not_fitted"
        assert assignment.confidence == 0.0

    def test_predict_after_fit(self):
        """After fitting, predict returns a valid assignment."""
        engine = self._fresh_engine()
        docs = [
            "funk carioca baile pancadão ritmo dança",
            "sertanejo universitário viola modão caipira",
            "bossa nova jazz samba acordes harmonia",
            "feijoada arroz feijão comida brasileira",
            "churrasco picanha costela carvão gaúcho",
            "acarajé vatapá bahia dendê pimenta",
            "futebol gol campeonato brasileiro série",
            "seleção brasileira copa mundo fifa",
            "capoeira luta dança cultura afro brasileira",
            "rock brasileiro legião urbana renato russo",
            "pagode samba roda cerveja boteco mesa",
            "forró xote baião luiz gonzaga nordeste",
            "pão queijo minas gerais café manhã delícia",
            "açaí tapioca mandioca amazônia fruta",
            "surf praia onda litoral brasileiro verão",
            "jiu jitsu artes marciais academia treino",
            "vôlei basquete olimpíadas atleta medalha",
            "fórmula piloto corrida automobilismo pista",
            "carnaval bloco trio elétrico axé",
            "festa junina quadrilha fogueira milho",
        ]
        for d in docs:
            engine.add_document(d)
        engine.fit()

        assignment = engine.predict("funk carioca baile")
        assert assignment.macro_topic >= 0
        assert assignment.confidence > 0.0
        assert isinstance(assignment.top_terms, list)

    def test_predict_to_dict(self):
        """TopicAssignment.to_dict() returns correct format."""
        from core.intelligence.topic_engine import TopicAssignment
        ta = TopicAssignment(
            macro_topic=1,
            macro_label="Topic-1",
            top_terms=["funk", "baile"],
            confidence=0.7,
        )
        d = ta.to_dict()
        assert d["macro_topic"] == 1
        assert d["macro_label"] == "Topic-1"
        assert d["top_terms"] == ["funk", "baile"]
        assert d["confidence"] == 0.7


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 6: STATS & HIERARCHY
# ═════════════════════════════════════════════════════════════════════════════

class TestStatsAndHierarchy:
    """Test get_stats and get_hierarchy."""

    def _fresh_engine(self):
        from core.intelligence.topic_engine import TopicEngine
        return TopicEngine(n_topics=4)

    def test_stats_initial(self):
        engine = self._fresh_engine()
        stats = engine.get_stats()
        assert stats["n_topics"] == 4
        assert stats["buffer_size"] == 0
        assert stats["is_fitted"] is False
        assert stats["fitted_at"] is None
        assert stats["fit_count"] == 0
        assert stats["sklearn_available"] is True

    def test_stats_after_docs(self):
        engine = self._fresh_engine()
        engine.add_document("teste cultural")
        stats = engine.get_stats()
        assert stats["buffer_size"] == 1
        assert stats["docs_since_last_fit"] == 1

    def test_hierarchy_empty_before_fit(self):
        engine = self._fresh_engine()
        h = engine.get_hierarchy()
        assert h["n_topics"] == 0
        assert h["topics"] == []

    def test_hierarchy_after_fit(self):
        engine = self._fresh_engine()
        docs = [
            "funk carioca baile pancadão ritmo dança",
            "sertanejo universitário viola modão caipira",
            "bossa nova jazz samba acordes harmonia",
            "feijoada arroz feijão comida brasileira",
            "churrasco picanha costela carvão gaúcho",
            "acarajé vatapá bahia dendê pimenta",
            "futebol gol campeonato brasileiro série",
            "seleção brasileira copa mundo fifa",
            "capoeira luta dança cultura afro brasileira",
            "rock brasileiro legião urbana renato russo",
            "pagode samba roda cerveja boteco mesa",
            "forró xote baião luiz gonzaga nordeste",
            "pão queijo minas gerais café manhã delícia",
            "açaí tapioca mandioca amazônia fruta",
            "surf praia onda litoral brasileiro verão",
            "jiu jitsu artes marciais academia treino",
            "vôlei basquete olimpíadas atleta medalha",
            "fórmula piloto corrida automobilismo pista",
            "carnaval bloco trio elétrico axé",
            "festa junina quadrilha fogueira milho",
            "hip hop rap periferias rima batalha",
            "circo teatro palhaço espetáculo artes",
            "cinema nacional filme documentário roteiro",
            "grafite street arte mural urbano",
            "literatura cordel poesia nordestina xilogravura",
        ]
        for d in docs:
            engine.add_document(d)
        engine.fit()
        h = engine.get_hierarchy()
        assert h["n_topics"] >= 1
        assert h["fit_count"] >= 1
        assert h["fitted_at"] is not None

    def test_is_fitted_property(self):
        engine = self._fresh_engine()
        assert engine.is_fitted is False

    def test_buffer_size_property(self):
        engine = self._fresh_engine()
        assert engine.buffer_size == 0
        engine.add_document("teste")
        assert engine.buffer_size == 1


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 7: WORKER INTEGRATION
# ═════════════════════════════════════════════════════════════════════════════

class TestTopicEnricherInWorker:
    """Test that topic_enricher is properly registered in the Worker pipeline."""

    def test_worker_has_10_engines(self):
        """Worker default tem 17 engines registradas (inclui stability_risk)."""
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        assert len(worker._engines) == 17

    def test_topics_registered_at_priority_48(self):
        """topic_enricher está no pipeline com prioridade 48."""
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        tp = [e for e in worker._engines if e.name == "topics"]
        assert len(tp) == 1
        assert tp[0].priority == 48

    def test_topics_after_feedback(self):
        """topics (48) comes after feedback (45) in pipeline order."""
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        names = [e.name for e in worker._engines]
        assert names.index("feedback") < names.index("topics")

    def test_topics_is_second_to_last_engine(self):
        """topics is before the H-9 block in the pipeline (pest precedes H-9)."""
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        names = [e.name for e in worker._engines]
        # topics at index 9, pest at 10, then 5 H-9 engines
        assert names.index("topics") < names.index("pest")
        assert names.index("pest") < names.index("vulnerability")

    def test_full_pipeline_order(self):
        """Complete pipeline order with 17 engines."""
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        names = [e.name for e in worker._engines]
        expected = [
            "circles",           # 10
            "unknown_detector",  # 15
            "sentiment",         # 20
            "tension",           # 22
            "nature",            # 25
            "authenticity",      # 30
            "velocity",          # 35
            "graph",             # 40
            "feedback",          # 45
            "topics",            # 48
            "pest",              # 50
            "vulnerability",     # 52
            "alerts",            # 54
            "actions",           # 56
            "scenarios",         # 58
            "opportunities",     # 60
            "stability_risk",    # 62
        ]
        assert names == expected

    def test_topic_enricher_enriches_signal(self):
        """Run topic_enricher on a sample signal."""
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        tp_engine = [e for e in worker._engines if e.name == "topics"][0]

        signal = {
            "termo": "funk carioca",
            "texto": "O funk carioca domina as paradas de sucesso",
            "plataforma": "YouTube",
        }
        result = tp_engine.fn(signal.copy())
        assert isinstance(result, dict)
        assert "topic_assignment" in result
        ta = result["topic_assignment"]
        assert "macro_topic" in ta
        assert "macro_label" in ta

    def test_topic_enricher_handles_empty_signal(self):
        """Empty signal passes through without error."""
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        tp_engine = [e for e in worker._engines if e.name == "topics"][0]

        result = tp_engine.fn({})
        assert isinstance(result, dict)

    def test_topic_enricher_no_texto_field(self):
        """Signal without texto field doesn't crash."""
        from core.analysis_worker import create_default_worker
        worker = create_default_worker()
        tp_engine = [e for e in worker._engines if e.name == "topics"][0]

        result = tp_engine.fn({"termo": "sertanejo", "plataforma": "Spotify"})
        assert isinstance(result, dict)
