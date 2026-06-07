import pytest
from datetime import datetime, timedelta

from autonomous_agent.weak_signals_detector import WeakSignalsDetector
from core.intelligence.business_synthesizer import BusinessSynthesizer, BusinessContext

try:
    from core.classifiers.authenticity_analyzer import AuthenticityAnalyzer
except ImportError:
    AuthenticityAnalyzer = None


def test_phase1_weak_signal_to_business_synthesis():
    detector = WeakSignalsDetector()

    now = datetime.now()
    data_points = [
        {
            "title": "A nova onda de cultura urbana no Rio",
            "content": "O movimento de funk e arte de rua cresce em periferias e uniões locais.",
            "timestamp": (now - timedelta(days=3)).isoformat(),
            "content_type": "article",
            "plataforma": "news_rss",
            "momentum": 60,
            "volume": 120,
            "sentiment": 0.7,
            "relevancia_cultural": 0.85,
        },
        {
            "title": "Funk e moda nas ruas do Nordeste",
            "content": "A cultura periférica combina música, moda e inovação social.",
            "timestamp": (now - timedelta(days=1)).isoformat(),
            "content_type": "article",
            "plataforma": "youtube",
            "momentum": 78,
            "volume": 150,
            "sentiment": 0.65,
            "relevancia_cultural": 0.9,
        },
        {
            "title": "Comunidade local fortalece evento cultural",
            "content": "A economia criativa se une com ações de rua e tecnologia social.",
            "timestamp": now.isoformat(),
            "content_type": "article",
            "plataforma": "reddit",
            "momentum": 55,
            "volume": 95,
            "sentiment": 0.6,
            "relevancia_cultural": 0.8,
        },
    ]

    result = detector.detect_weak_signals(data_points, timeframe=7, user_intent="Pesquisa de Mercado")

    assert isinstance(result, dict)
    assert "signals_by_strength" in result
    assert "recommendations" in result
    assert isinstance(result["signals_by_strength"], dict)
    assert set(result["signals_by_strength"].keys()) == {"weak_signals", "medium_signals", "strong_signals"}
    assert isinstance(result["recommendations"], list)

    signal_bucket = result["signals_by_strength"]["strong_signals"]
    assert isinstance(signal_bucket, list)


def test_phase1_business_synthesizer_integration():
    if AuthenticityAnalyzer is None or not hasattr(AuthenticityAnalyzer(), 'analyze_authenticity'):
        pytest.skip("AuthenticityAnalyzer not available in this environment")

    synthesizer = BusinessSynthesizer()
    context = BusinessContext(
        scenario_type="Pesquisa de Mercado",
        target_audience="Público periférico urbano",
        business_objective="Mapear tendências culturais emergentes",
        opportunities_sought=["Conexão local", "Inovação social"],
        constraints=["Ética de dados"],
        success_metrics=["Engajamento", "Relevância"],
    )

    signals = [
        {
            "termo": "cultura urbana",
            "plataforma": "youtube",
            "relevancia_cultural": 0.85,
            "momentum": 75,
            "dados_extras": {"evidence": [{"platform": "youtube", "thumbnail": True, "views": 2000}]},
        }
    ]

    enriched = synthesizer.analyze_cultural_signals(signals, context)
    assert isinstance(enriched, list)
    assert all(isinstance(item, dict) for item in enriched)
    assert len(enriched) == 1
    assert "recommendation" in enriched[0]
