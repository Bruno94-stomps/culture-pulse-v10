#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Widget Dictionary - Culture Pulse V9.1
Define a relação entre os insights das engines e os componentes visuais do Next.js.
"""

from typing import Dict, Any, List

WIDGET_DICTIONARY = {
    "cultural_circles": {
        "id": "cultural_circles",
        "name": "Radar de Círculos Culturais",
        "component": "RadarChart",
        "engine": "CulturalCirclesProcessor",
        "description": "Visualização dos 16 círculos de influência da cultura brasileira.",
        "data_shape": {"labels": "List[str]", "values": "List[float]"}
    },
    "alma_brasileira": {
        "id": "alma_brasileira",
        "name": "Índice Alma Brasileira",
        "component": "GaugeChart",
        "engine": "AlmaBrasileiraAnalyzer",
        "description": "Nível de autenticidade e conexão com a identidade nacional.",
        "data_shape": {"score": "float", "markers": "List[str]"}
    },
    "emerging_trends": {
        "id": "emerging_trends",
        "name": "Perfis Emergentes",
        "component": "TrendWaveCard",
        "engine": "EmergingProfilesEngine",
        "description": "Sinais fracos que indicam novos comportamentos antes do mainstream.",
        "data_shape": {"profiles": "List[Dict]", "growth_rate": "float"}
    },
    "tension_hotspots": {
        "id": "tension_hotspots",
        "name": "Mapa de Tensões Culturais",
        "component": "TensionHeatmap",
        "engine": "TensionDetectorEngine",
        "description": "Identifica zonas de atrito e conflito de narrativa nas redes.",
        "data_shape": {"tensions": "List[Dict]", "criticality": "str"}
    },
    "quadrant_matrix": {
        "id": "quadrant_matrix",
        "name": "Matriz de Sinais (Novidade x Relevância)",
        "component": "ScatterPlotMatrix",
        "engine": "QuadrantEngine",
        "description": "Classifica termos entre 'Flash in the Pan', 'Lendas', 'Emergentes' ou 'Modas'.",
        "data_shape": {"points": "List[Dict]"}
    },
    "sentiment_velocity": {
        "id": "sentiment_velocity",
        "name": "Velocidade de Sentimento",
        "component": "AreaChart",
        "engine": "SentimentAnalysisEngine",
        "description": "Acompanha o humor do público em tempo real e sua oscilação.",
        "data_shape": {"timeline": "List[str]", "sentiment": "List[float]"}
    },
    "competitive_overlap": {
        "id": "competitive_overlap",
        "name": "Crossover de Público",
        "component": "VennDiagram",
        "engine": "SegmentComparisonEngine",
        "description": "Onde o seu público encontra o público de outros setores.",
        "data_shape": {"overlap_pct": "float", "common_terms": "List[str]"}
    }
}

SCENARIO_MAPPING = {
    "Lançamento de Produto": {
        "primary": ["emerging_trends", "quadrant_matrix", "sentiment_velocity"],
        "discovery": ["cultural_circles", "competitive_overlap"],
        "layout_strategy": "AGRESSIVE"
    },
    "Pesquisa de Mercado": {
        "primary": ["cultural_circles", "alma_brasileira", "quadrant_matrix"],
        "discovery": ["emerging_trends", "competitive_overlap"],
        "layout_strategy": "ANALYTIC"
    },
    "Crise de Reputação": {
        "primary": ["tension_hotspots", "sentiment_velocity", "alma_brasileira"],
        "discovery": ["quadrant_matrix", "cultural_circles"],
        "layout_strategy": "CRITICAL"
    }
}

def get_widget_config(scenario: str) -> Dict[str, Any]:
    """Retorna a configuração de widgets recomendada para um cenário"""
    mapping = SCENARIO_MAPPING.get(scenario, SCENARIO_MAPPING["Pesquisa de Mercado"])
    
    widgets = []
    for widget_id in mapping["primary"]:
        config = WIDGET_DICTIONARY[widget_id].copy()
        config["priority"] = "HIGH"
        widgets.append(config)
        
    for widget_id in mapping["discovery"]:
        config = WIDGET_DICTIONARY[widget_id].copy()
        config["priority"] = "MEDIUM"
        widgets.append(config)
        
    return {
        "layout_strategy": mapping["layout_strategy"],
        "widgets": widgets
    }
