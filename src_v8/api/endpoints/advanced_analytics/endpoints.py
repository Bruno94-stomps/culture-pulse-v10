#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Analytics Engine Implementation - Culture Pulse V9.0
Expõe as lógicas de Quadrantes, Executivo e Multiplicadores para o Next.js
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Any, Optional
import logging
from core.advanced_analytics.quadrant_engine import compute_novelty_score, compute_relevance_score, classify_quadrant, compute_signal_strength
from core.advanced_analytics.executive_engine import ExecutiveSummarySynchronizer
from core.advanced_analytics.onboarding_logic import SEGMENTOS, OBJETIVOS, AUDIENCIAS, FONTES, CIRCULOS_CULTURAIS
from core.advanced_analytics.segment_comparison_engine import compare_signal_across_segments
from core.advanced_analytics.learning_utils import LearningAnalytics
from core.advanced_analytics.widget_dictionary import WIDGET_DICTIONARY, SCENARIO_MAPPING, get_widget_config

router = APIRouter(prefix="/analytics", tags=["Advanced Analytics"])
logger = logging.getLogger(__name__)
exec_sync = ExecutiveSummarySynchronizer()

@router.get("/quadrant")
async def get_signal_quadrant(limit: int = 50):
    """
    Retorna dados formatados para o gráfico de quadrantes (Relevância x Novidade)
    """
    try:
        # Aqui integraríamos com o banco de dados (Supabase/Redis)
        # Mock para demonstração de integração do motor migrado
        mock_signals = [
            {"termo": "Inteligência Artificial", "score": 0.9, "ts": "2024-03-15T10:00:00Z", "raw_data": {"momentum": 85, "volume": 12000}},
            {"termo": "Bio-hacking", "score": 0.4, "ts": "2024-03-14T10:00:00Z", "raw_data": {"momentum": 70, "velocity": 45}},
            {"termo": "Samba de Raiz", "score": 0.8, "ts": "2024-03-10T10:00:00Z", "raw_data": {"momentum": 20, "volume": 50000}}
        ]
        
        results = []
        for sig in mock_signals:
            novelty = compute_novelty_score(sig)
            relevance = compute_relevance_score(sig)
            results.append({
                "term": sig["termo"],
                "x": novelty,
                "y": relevance,
                "strength": compute_signal_strength(novelty, relevance),
                "quadrant": classify_quadrant(novelty, relevance)
            })
            
        return {"status": "success", "data": results}
    except Exception as e:
        logger.error(f"Erro no quadrant: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/executive-summary")
async def sync_executive_summary(config: Dict[str, Any], results: Optional[Dict[str, Any]] = None):
    """
    Sincroniza e gera o resumo executivo com recomendações
    """
    try:
        data = exec_sync.sync_executive_data(config, results)
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"Erro no executive summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/onboarding-options")
async def get_onboarding_options():
    """
    Retorna as opções de configuração para o onboarding do Next.js
    """
    return {
        "status": "success",
        "data": {
            "segments": SEGMENTOS,
            "objectives": OBJETIVOS,
            "audiences": AUDIENCIAS,
            "sources": FONTES,
            "cultural_circles": CIRCULOS_CULTURAIS
        }
    }

@router.post("/compare-segments")
async def compare_segments_api(
    signal: Dict[str, Any], 
    segment_a: str, 
    segment_b: str
):
    """
    Compara um sinal cultural entre dois setores/segmentos diferentes.
    Ideal para a visualização de 'Setores' no Next.js.
    """
    try:
        # A função original espera um objeto ou dict que tenha os campos necessários
        # O mock aqui simula o processamento da lógica migrada
        comparison = compare_signal_across_segments(signal, segment_a, segment_b)
        
        # Formatar para JSON serializável (extraindo dados das dataclasses)
        return {
            "status": "success",
            "data": {
                "segment_a": comparison['segment_a'].__dict__,
                "segment_b": comparison['segment_b'].__dict__,
                "delta": comparison['segment_a'].score - comparison['segment_b'].score
            }
        }
    except Exception as e:
        logger.error(f"Erro na comparação de segmentos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learning-status")
async def get_learning_status():
    """
    Retorna o status de aprendizado do sistema (Trend e Scores).
    Resgata a lógica do antigo dashboard/utils.py.
    """
    try:
        # Dados simulados baseados na evolução do aprendizado humano no backend
        historical_accuracy = [0.65, 0.70, 0.72, 0.78, 0.85]
        
        analytics = LearningAnalytics()
        trend = analytics.calculate_trend(historical_accuracy)
        normalized_scores = analytics.normalize_learning_scores({"overall_accuracy": historical_accuracy[-1]})
        color = analytics.get_status_color(historical_accuracy[-1])
        
        return {
            "status": "success",
            "data": {
                "trend": trend,
                "score": normalized_scores["overall_accuracy"],
                "color": color,
                "message": "Aprendizado contínuo ativo via feedbacks humanos."
            }
        }
    except Exception as e:
        logger.error(f"Erro no learning status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ml-architecture-info")
async def get_ml_architecture_info():
    """
    Retorna metadados da arquitetura de ML (V9.0) para exibição no Dashboard Next.js.
    Integra a visão dos arquivos .md resgatados.
    """
    return {
        "status": "success",
        "data": {
            "version": "9.1.0-NextGen",
            "engines": [
                {
                    "name": "Culture Intelligence Engine",
                    "status": "active",
                    "components": ["Weak Signals", "Temporal Intelligence", "Trend Analysis"]
                },
                {
                    "name": "ML Foundation",
                    "status": "integrated",
                    "models": ["BERTimbau", "GPT-4o mini", "spaCy PT-LG"]
                },
                {
                    "name": "Active Learning",
                    "status": "human-in-the-loop",
                    "features": ["Wilson Lower Bound", "Entropy Sampling"]
                }
            ],
            "roadmap_focus": "Automated Learning & Scalability"
        }
    }

@router.get("/segment-comparison")
async def get_segment_comparison(segment_a: str, segment_b: str):
    """
    Compara dois segmentos culturais.
    Resgatado de dashboard/utils.py:245
    """
    # Exemplo de lógica de comparação de similaridade entre nichos
    similarity = 0.75 # Placeholder
    return {
        "similarity_score": similarity,
        "common_circles": ["festa_celebracao", "hospitalidade"],
        "divergent_trends": ["tecnologia_acessivel" if segment_a == "tecnologia" else "tradicao"]
    }

# --- NEW: BUSINESS CONSULTANT ENDPOINTS (V9.1) ---

@router.post("/consultant/refine-briefing")
async def refine_briefing(
    goal_text: str,
    brand_name: Optional[str] = "Marca",
    segment: Optional[str] = "Geral",
    previous_answers: Optional[Dict[str, str]] = None
):
    """
    Interface de 'Consultoria Dinâmica' (V9.1).
    Transforma texto livre em parâmetros e sugere os próximos passos e dashboard ideal.
    """
    try:
        from core.intelligence.business_synthesizer import BusinessSynthesizer
        synthesizer = BusinessSynthesizer()
        
        # 1. Analisa o objetivo e integra respostas anteriores
        full_context_text = goal_text
        if previous_answers:
            for key, val in previous_answers.items():
                full_context_text += f" Informação extra ({key}): {val}."

        context = await synthesizer.analyze_business_context(full_context_text)
        
        # 2. Gera Sugestões de Palavras-Chave (Editáveis no Frontend)
        cultural_keywords = context.opportunities_sought
        
        # 3. MAPEAMENTO DE OUTPUTS & WIDGETS (Dicionário V9.1)
        # Busca a configuração ideal para o cenário detectado
        dashboard_config = get_widget_config(context.scenario_type)

        # 4. Perguntas Dinâmicas de "Aprofundamento"
        next_questions = []
        if not any(loc in goal_text.lower() for loc in ["rio", "são paulo", "nordeste", "sul", "bh"]):
            next_questions.append({
                "id": "location_detail",
                "question": "Em qual região do Brasil o foco é maior? Isso muda completamente o tom cultural.",
                "type": "selection",
                "options": ["Sudeste (SP/RJ)", "Nordeste", "Sul", "Nacional"]
            })
            
        if len(goal_text.split()) < 10:
            next_questions.append({
                "id": "lifestyle_detail",
                "question": "Qual o estilo de vida desse público? (Ex: Ativo e Urbano, Tradicional e Familiar, ou Jovem e Digital?)",
                "type": "text"
            })

        # Nova pergunta específica de Lançamento
        if context.scenario_type == "Lançamento de Produto" and "canal" not in full_context_text.lower():
            next_questions.append({
                "id": "channel_focus",
                "question": "Onde sua marca vive mais hoje? (Ex: Digital, PDV Físico, ou Comunidades)",
                "type": "selection",
                "options": ["TikTok/Instagram", "YouTube/Reviews", "Eventos/Físico", "WhatsApp/Direto"]
            })

        return {
            "status": "success",
            "detected_context": {
                "scenario": context.scenario_type,
                "audience": context.target_audience,
                "objective": context.business_objective
            },
            "suggestions": {
                "editable_keywords": list(set(cultural_keywords + [brand_name.lower()])),
                "strategic_advice": f"Configurando análise para um cenário de {context.scenario_type}."
            },
            "dashboard_setup": {
                "layout_strategy": dashboard_config["layout_strategy"],
                "recommended_widgets": dashboard_config["widgets"]
            },
            "next_steps": {
                "questions": next_questions,
                "can_proceed": len(next_questions) == 0 or (previous_answers and len(previous_answers) >= 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na consultoria dinâmica: {str(e)}")

@router.get("/consultant/onboarding-scenarios")
async def get_onboarding_scenarios():
    """
    Retorna os cenários padrão para o carrossel/onboarding do Next.js.
    """
    return {
        "scenarios": [
            {
                "id": "launch",
                "title": "Lançamento de Produto",
                "icon": "rocket",
                "description": "Foco em viralidade, aceitação de novos nichos e tendências de consumo.",
                "example_goal": "Quero lançar um novo energético para estudantes de TI em São Paulo."
            },
            {
                "id": "research",
                "title": "Pesquisa de Mercado",
                "icon": "search",
                "description": "Mapeamento profundo de hábitos, dores e círculos culturais dominantes.",
                "example_goal": "Entender o comportamento de compra de cosméticos em Salvador."
            },
            {
                "id": "reputation",
                "title": "Crise de Reputação",
                "icon": "shield",
                "description": "Monitoramento de tensões, sentimentos negativos e recuperação de imagem.",
                "example_goal": "Monitorar a reação do público após a mudança na embalagem da marca."
            }
        ]
    }
