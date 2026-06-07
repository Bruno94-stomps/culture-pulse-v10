#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core Module - Culture Pulse V9.1  (DT-1: Lazy Imports)
=======================================================
Sistema central de análise cultural brasileira.

🎯 MÓDULOS PRINCIPAIS:
- CulturalEngine: Orquestração principal
- CulturalCirclesProcessor: 16 Círculos Culturais
- TFIDFCulturalAnalyzer: Análise TF-IDF especializada
- AlmaBrasileiraAnalyzer: Sistema Alma Brasileira
- CulturalGraphAnalyzer: Análise de grafos culturais (requer torch_geometric)
- TemporalCulturalAnalyzer: Padrões temporais
- AuthenticityAnalyzer: Análise de autenticidade
- CulturalComputingEngine: Polaridade cultural

✅ DT-1 (22/Fev/2026): Lazy imports via PEP 562 __getattr__.
   Antes: `import core` carregava TODOS os módulos (incluindo torch_geometric).
   Agora: módulos são carregados sob demanda na primeira referência.
   Isso permite que `from core.intelligence.circles_processor import X` funcione sem
   acionar importação de `torch_geometric` ou outros pacotes pesados.

Uso:
    # Import direto (preferido — não aciona __init__.py eager):
    from core.engines.cultural_engine import CulturalEngine
    
    # Import via __init__.py (funciona, lazy):
    from core import CulturalEngine
    
    engine = CulturalEngine()
"""

import importlib
from typing import Any

# ── Mapeamento lazy: nome exportado → (módulo, atributo) ──────────────────────
_LAZY_IMPORTS: dict = {
    # cultural_engine
    "CulturalEngine":          (".cultural_engine", "CulturalEngine"),
    "CulturalAnalysisResult":  (".cultural_engine", "CulturalAnalysisResult"),
    "create_cultural_engine":  (".cultural_engine", "create_cultural_engine"),

    # circles_processor
    "CulturalCirclesProcessor": (".circles_processor", "CulturalCirclesProcessor"),
    "create_circles_processor": (".circles_processor", "create_circles_processor"),

    # tfidf_analyzer
    "TFIDFCulturalAnalyzer":   (".tfidf_analyzer", "TFIDFCulturalAnalyzer"),
    "create_tfidf_analyzer":   (".tfidf_analyzer", "create_tfidf_analyzer"),

    # alma_brasileira
    "AlmaBrasileiraAnalyzer":  (".alma_brasileira", "AlmaBrasileiraAnalyzer"),
    "create_alma_analyzer":    (".alma_brasileira", "create_alma_analyzer"),

    # cultural_computing_engine
    "CulturalComputingEngine": (".cultural_computing_engine", "CulturalComputingEngine"),
    "PolarityAnalysis":        (".cultural_computing_engine", "PolarityAnalysis"),

    # cultural_graph_analyzer (requer torch_geometric — SÓ carrega se pedido)
    "CulturalGraphAnalyzer":   (".cultural_graph_analyzer", "CulturalGraphAnalyzer"),
    "CulturalPropagation":     (".cultural_graph_analyzer", "CulturalPropagation"),
    "AgentBehavior":           (".cultural_graph_analyzer", "AgentBehavior"),

    # temporal_cultural_analyzer
    "TemporalCulturalAnalyzer": (".temporal_cultural_analyzer", "TemporalCulturalAnalyzer"),
    "TemporalPattern":          (".temporal_cultural_analyzer", "TemporalPattern"),
    "CulturalDecay":            (".temporal_cultural_analyzer", "CulturalDecay"),
    "SeasonalityAnalysis":      (".temporal_cultural_analyzer", "SeasonalityAnalysis"),

    # authenticity_analyzer
    "AuthenticityAnalyzer":    (".authenticity_analyzer", "AuthenticityAnalyzer"),
    "AuthenticityResult":      (".authenticity_analyzer", "AuthenticityResult"),

    # async_processing
    "run_async_batch":         (".async_processing", "run_async_batch"),
    "run_api_batch":           (".async_processing", "run_api_batch"),
    "run_parallel_functions":  (".async_processing", "run_parallel_functions"),

    # validation_metrics
    "confidence_interval":     (".validation_metrics", "confidence_interval"),
    "calculate_metrics":       (".validation_metrics", "calculate_metrics"),
    "classification_metrics":  (".validation_metrics", "classification_metrics"),
    "risk_assessment":         (".validation_metrics", "risk_assessment"),
    "generate_validation_report": (".validation_metrics", "generate_validation_report"),
    "ValidationReport":        (".validation_metrics", "ValidationReport"),
}

# ── Cache de atributos já resolvidos ──────────────────────────────────────────
_RESOLVED: dict = {}


def __getattr__(name: str) -> Any:
    """
    PEP 562 — lazy module attribute access.
    Chamado quando `from core import X` ou `core.X` não encontra `X` no namespace.
    """
    if name in _RESOLVED:
        return _RESOLVED[name]

    if name in _LAZY_IMPORTS:
        module_path, attr_name = _LAZY_IMPORTS[name]
        module = importlib.import_module(module_path, package=__name__)
        value = getattr(module, attr_name)
        _RESOLVED[name] = value
        return value

    raise AttributeError(f"module 'core' has no attribute {name!r}")


# ── __all__ para autocomplete e documentação ──────────────────────────────────
__all__ = list(_LAZY_IMPORTS.keys())

# ── Metadados ─────────────────────────────────────────────────────────────────
__version__ = '9.1.0'
__status__ = 'Production Ready - Lazy Imports (DT-1)'

# ── Configurações padrão ──────────────────────────────────────────────────────
CORE_CONFIG = {
    'circles_count': 16,
    'cultural_categories': 6,
    'regional_modifiers': 5,
    'tfidf_max_features': 1000,
    'alma_values_count': 7,
    'advanced_metrics': True,
    'integrated_systems': True,
    'lazy_imports': True,  # DT-1
}


def get_core_info() -> dict:
    """Retorna informações sobre o módulo core."""
    return {
        'version': __version__,
        'status': __status__,
        'modules': len(__all__),
        'config': CORE_CONFIG,
        'lazy': True,
        'description': 'Sistema central de análise cultural brasileira',
    }


def setup_cultural_analysis() -> dict:
    """
    Setup rápido para análise cultural.
    NOTA: Carrega TODOS os módulos sob demanda. Pode ser lento na primeira chamada.
    """
    # Importação explícita aqui para que Pylance não reclame de nomes indefinidos
    from .cultural_engine import create_cultural_engine as _ce
    from .circles_processor import create_circles_processor as _cp
    from .tfidf_analyzer import create_tfidf_analyzer as _ta
    from .alma_brasileira import create_alma_analyzer as _aa
    from .cultural_computing_engine import CulturalComputingEngine as _CCE
    from .cultural_graph_analyzer import CulturalGraphAnalyzer as _CGA
    from .temporal_cultural_analyzer import TemporalCulturalAnalyzer as _TCA
    from .authenticity_analyzer import AuthenticityAnalyzer as _AA

    return {
        'engine': _ce(),
        'circles': _cp(),
        'tfidf': _ta(),
        'alma': _aa(),
        'computing': _CCE(),
        'graph': _CGA(),
        'temporal': _TCA(),
        'authenticity': _AA(),
    }


if __name__ == "__main__":
    import asyncio

    async def demo_core():
        print("🧠 CORE SYSTEM V9.1 - Demonstração (Lazy Imports)")
        print("=" * 50)

        components = setup_cultural_analysis()

        for name, obj in components.items():
            print(f"  ✅ {name}: {type(obj).__name__}")

        print(f"\n🚀 CORE V9.1 pronto — {len(_RESOLVED)} módulos carregados sob demanda")

    asyncio.run(demo_core())
