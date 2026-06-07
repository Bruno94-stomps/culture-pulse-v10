#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Circles Endpoints - Culture Pulse V8.0
Endpoints específicos para análise de círculos culturais

🎯 FUNCIONALIDADES:
- Análise isolada dos 16 círculos culturais
- Análise por círculos específicos
- Comparação entre círculos
- Insights regionais
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List, Optional
import logging
import sys
import os

# Adicionar path para imports absolutos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from api.models import CirclesAnalysisRequest, CirclesAnalysisResponse, ErrorResponse
from api.middleware.auth import get_current_client, ClientInfo
from core.Abas.Camada1_Fundamentos.circulos_culturais.circles_processor import CulturalCirclesProcessor

logger = logging.getLogger(__name__)

# Criar router
circles_router = APIRouter()


@circles_router.post(
    "/analyze",
    response_model=CirclesAnalysisResponse,
    summary="Análise dos Círculos Culturais",
    description="""
    **Executa análise específica dos 16 Círculos Culturais Brasileiros**
    
    Analisa os círculos culturais de forma isolada, permitindo compreender
    quais aspectos culturais são mais relevantes para um segmento/localização.
    
    ### Os 16 Círculos Culturais Brasileiros:
    
    **Centrais (4):**
    - Adaptação e Flexibilidade
    - Conexão com a Natureza e o Coletivo
    - Resiliência e Fé
    - Economia Informal e Empreendedorismo
    
    **Intermediários (8):**
    - Musicalidade e Expressão
    - Vida Urbana e Vida Rural
    - Alegria e Celebração
    - Festa e Luta Cotidianas
    - Criatividade e Improvisação
    - Diversidade Geográfica e Cultural
    - Afeto e Hospitalidade
    - Desejo de Ascensão e Oportunidades
    
    **Externos (4):**
    - Sincretismo Cultural
    - Relação com o Caos
    - Astúcia e Sagacidade
    - Desigualdade x Solidariedade Contradições
    """,
    responses={
        200: {"description": "Análise executada com sucesso"},
        400: {"description": "Dados inválidos"},
        500: {"description": "Erro interno"}
    }
)
async def analyze_circles(
    request: CirclesAnalysisRequest,
    current_client: ClientInfo = Depends(get_current_client)
):
    """Executar análise dos círculos culturais"""
    
    try:
        logger.info(f"Análise círculos - Segmento: {request.segment} - Cliente: {current_client.id}")
        
        # Criar processador de círculos
        processor = CulturalCirclesProcessor()
        
        # Executar análise
        result = processor.analyze_cultural_circles(
            content_data=request.content_data,
            segment=request.segment.value,
            location=request.location.value,
            focus_circles=request.focus_circles
        )
        
        # Converter para formato da API
        response = _convert_circles_result(result)
        
        logger.info(f"Círculos analisados - Score: {response['overall_score']:.2f}")
        
        return response
        
    except Exception as e:
        logger.error(f"Erro na análise de círculos: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "circles_analysis_error",
                "message": str(e)
            }
        )


@circles_router.get(
    "/list",
    summary="Lista dos Círculos Culturais",
    description="Retorna lista completa dos 16 círculos culturais com descrições"
)
async def list_circles(
    category: Optional[str] = Query(None, description="Filtrar por categoria (central, intermediario, externo)"),
    current_client: ClientInfo = Depends(get_current_client)
):
    """Listar todos os círculos culturais disponíveis"""
    
    circles_info = {
        "central": {
            "adaptacao_flexibilidade": {
                "name": "Adaptação e Flexibilidade",
                "description": "Capacidade de se ajustar a novas situações e desafios com resiliência.",
                "weight": 1.3,
                "examples": ["mudança", "resiliência", "versatilidade"]
            },
            "conexao_natureza_coletivo": {
                "name": "Conexão com a Natureza e o Coletivo",
                "description": "Forte ligação com o ambiente natural e um senso de comunidade e pertencimento.",
                "weight": 1.2,
                "examples": ["comunidade", "natureza", "sustentabilidade"]
            },
            "resiliencia_fe": {
                "name": "Resiliência e Fé",
                "description": "Capacidade de superar dificuldades com otimismo e uma forte base de esperança ou crença.",
                "weight": 1.3,
                "examples": ["superação", "esperança", "persistência"]
            },
            "economia_informal_empreendedorismo": {
                "name": "Economia Informal e Empreendedorismo",
                "description": "Habilidade de criar oportunidades econômicas fora das estruturas formais.",
                "weight": 1.1,
                "examples": ["autônomo", "vendedor", "pequeno negócio"]
            }
        },
        "intermediario": {
            "musicalidade_expressao": {
                "name": "Musicalidade e Expressão",
                "description": "Conexão profunda com música e diversas formas de expressão artística.",
                "weight": 1.0,
                "examples": ["samba", "MPB", "dança", "arte de rua"]
            },
            "vida_urbana_rural": {
                "name": "Vida Urbana e Vida Rural",
                "description": "A dualidade e a interação entre os costumes e desafios da cidade e do campo.",
                "weight": 0.9,
                "examples": ["metrópole", "interior", "tradição rural", "modernidade urbana"]
            },
            "alegria_celebracao": {
                "name": "Alegria e Celebração",
                "description": "Uma forte inclinação para a celebração, festividades e a busca pela alegria.",
                "weight": 1.0,
                "examples": ["carnaval", "festas juninas", "comemorações"]
            },
            "festa_luta_cotidianas": {
                "name": "Festa e Luta Cotidianas",
                "description": "O equilíbrio entre celebrar a vida e enfrentar as batalhas do dia a dia.",
                "weight": 1.0,
                "examples": ["trabalho", "lazer", "superação diária"]
            },
            "criatividade_improvisacao": {
                "name": "Criatividade e Improvisação",
                "description": "A habilidade de encontrar soluções criativas e improvisar diante de imprevistos ('jeitinho brasileiro').",
                "weight": 1.1,
                "examples": ["jeitinho", "inovação", "solução criativa"]
            },
            "diversidade_geografica_cultural": {
                "name": "Diversidade Geográfica e Cultural",
                "description": "A vasta gama de paisagens, climas e tradições culturais que coexistem no país.",
                "weight": 1.1,
                "examples": ["regionalismo", "sotaques", "culinária local"]
            },
            "afeto_hospitalidade": {
                "name": "Afeto e Hospitalidade",
                "description": "O calor humano, a receptividade e a importância dos laços afetivos.",
                "weight": 1.0,
                "examples": ["acolhimento", "amizade", "carinho"]
            },
            "desejo_ascensao_oportunidades": {
                "name": "Desejo de Ascensão e Oportunidades",
                "description": "A busca contínua por crescimento pessoal, profissional e melhores condições de vida.",
                "weight": 0.9,
                "examples": ["sonho", "progresso", "educação", "trabalho"]
            }
        },
        "externo": {
            "sincretismo_cultural": {
                "name": "Sincretismo Cultural",
                "description": "A fusão e reinterpretação de diferentes crenças, tradições e costumes.",
                "weight": 1.2,
                "examples": ["religião", "música", "culinária"]
            },
            "relacao_com_caos": {
                "name": "Relação com o Caos",
                "description": "Habilidade de navegar e prosperar em ambientes caóticos e desorganizados.",
                "weight": 0.8,
                "examples": ["burocracia", "trânsito", "informalidade"]
            },
            "astucia_sagacidade": {
                "name": "Astúcia e Sagacidade",
                "description": "A 'malandragem' vista como uma forma de inteligência para navegar em situações complexas.",
                "weight": 0.7,
                "examples": ["esperteza", "negociação", "jogo de cintura"]
            },
            "desigualdade_solidariedade": {
                "name": "Desigualdade x Solidariedade Contradições",
                "description": "A convivência paradoxal entre profundas desigualdades sociais e fortes redes de solidariedade.",
                "weight": 0.9,
                "examples": ["justiça social", "ajuda mútua", "contraste social"]
            }
        }
    }
    
    if category:
        if category not in circles_info:
            raise HTTPException(
                status_code=400,
                detail=f"Categoria inválida. Use: central, intermediario, externo"
            )
        return {
            "category": category,
            "circles": circles_info[category],
            "total": len(circles_info[category])
        }
    
    return {
        "total_circles": 16,
        "categories": {
            "central": {"count": 4, "circles": circles_info["central"]},
            "intermediario": {"count": 8, "circles": circles_info["intermediario"]}, 
            "externo": {"count": 4, "circles": circles_info["externo"]}
        }
    }


@circles_router.get(
    "/compare",
    summary="Comparar Círculos por Região",
    description="Compara relevância dos círculos entre diferentes regiões"
)
async def compare_circles_by_region(
    regions: List[str] = Query(..., description="Lista de regiões para comparar"),
    segment: str = Query("geral", description="Segmento para análise"),
    current_client: ClientInfo = Depends(get_current_client)
):
    """Comparar círculos culturais entre regiões"""
    
    if len(regions) < 2:
        raise HTTPException(
            status_code=400,
            detail="Forneça pelo menos 2 regiões para comparação"
        )
    
    try:
        processor = CulturalCirclesProcessor()
        comparison_results = {}
        
        # Dados simulados para demonstração
        mock_data = {"texts": ["exemplo"], "metrics": {}}
        
        for region in regions:
            result = processor.analyze_cultural_circles(
                content_data=mock_data,
                segment=segment,
                location=region
            )
            
            comparison_results[region] = {
                "overall_score": result.get("overall_score", 0.0),
                "top_circles": sorted(
                    result.get("circles_scores", {}).items(),
                    key=lambda x: x[1].get("score", 0),
                    reverse=True
                )[:5]
            }
        
        return {
            "comparison_type": "regional",
            "segment": segment,
            "regions": comparison_results,
            "insights": _generate_regional_insights(comparison_results)
        }
        
    except Exception as e:
        logger.error(f"Erro na comparação regional: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro na comparação: {str(e)}"
        )


@circles_router.get(
    "/{circle_name}/details",
    summary="Detalhes de Círculo Específico",
    description="Informações detalhadas sobre um círculo cultural específico"
)
async def get_circle_details(
    circle_name: str,
    current_client: ClientInfo = Depends(get_current_client)
):
    """Obter detalhes de um círculo cultural específico"""
    
    # Mapeamento de informações detalhadas dos círculos
    circles_details = {
        "sincretismo_cultural": {
            "category": "central",
            "weight": 1.2,
            "regional_variations": {
                "nordeste": {"modifier": 1.3, "characteristics": ["religiosidade", "folclore"]},
                "sudeste": {"modifier": 1.1, "characteristics": ["diversidade", "cosmopolitismo"]},
                "sul": {"modifier": 0.9, "characteristics": ["imigração", "tradições europeias"]},
                "norte": {"modifier": 1.2, "characteristics": ["indígena", "ribeirinho"]},
                "centro_oeste": {"modifier": 1.0, "characteristics": ["agronegócio", "migração"]}
            },
            "segment_relevance": {
                "religioso": 1.5,
                "cultural": 1.4,
                "educacional": 1.2,
                "alimentacao": 1.1,
                "moda": 1.0
            }
        }
        # Adicionar outros círculos conforme necessário
    }
    
    if circle_name not in circles_details:
        # Se não tiver detalhes específicos, retornar informação básica
        return {
            "name": circle_name,
            "message": "Detalhes específicos não disponíveis",
            "suggestion": "Use /circles/list para ver círculos disponíveis"
        }
    
    return {
        "circle_name": circle_name,
        "details": circles_details[circle_name],
        "analysis_tips": [
            "Considere o contexto regional",
            "Analise relevância por segmento",
            "Observe modificadores culturais"
        ]
    }


# Funções auxiliares
def _convert_circles_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Converte resultado do processador para formato da API"""
    
    circles_scores = {}
    for circle_name, circle_data in result.get("circles_scores", {}).items():
        circles_scores[circle_name] = {
            "name": circle_name,
            "score": circle_data.get("score", 0.0),
            "level": _get_level_from_score(circle_data.get("score", 0.0)),
            "weight": circle_data.get("weight", 1.0),
            "regional_modifier": circle_data.get("regional_modifier", 1.0),
            "segment_modifier": circle_data.get("segment_modifier", 1.0)
        }
    
    return {
        "overall_score": result.get("overall_score", 0.0),
        "cultural_level": result.get("cultural_level", "indefinido"),
        "circles_scores": circles_scores,
        "dominant_circles": result.get("dominant_circles", []),
        "processing_time": result.get("processing_time", 0.0)
    }

    def get_circle_insights(self, circle_id: str, score: float) -> Dict[str, str]:
        """Gera insights automáticos para um círculo"""
        
        if circle_id not in self.circles:
            return {}
        
        circle = self.circles[circle_id]
        
        # Categorizar score
        if score >= 0.8:
            level = "Excelente"
            insight = f"Forte alinhamento com {circle.name}"
        elif score >= 0.6:
            level = "Bom"
            insight = f"Boa conexão com {circle.name}"
        elif score >= 0.4:
            level = "Moderado"
            insight = f"Conexão moderada com {circle.name}"
        else:
            level = "Fraco"
            insight = f"Baixa conexão com {circle.name}"
        
        return {
            'level': level,
            'insight': insight,
            'description': circle.description,
            'recommendations': self._get_recommendations(circle_id, score)
        }

def _generate_regional_insights(comparison_data: Dict[str, Any]) -> List[str]:
    """Gera insights baseados na comparação regional"""
    
    insights = []
    
    # Análise básica dos resultados
    scores = [(region, data["overall_score"]) for region, data in comparison_data.items()]
    scores.sort(key=lambda x: x[1], reverse=True)
    
    if len(scores) >= 2:
        highest = scores[0]
        lowest = scores[-1]
        
        insights.append(f"{highest[0]} apresenta maior score cultural ({highest[1]:.2f})")
        insights.append(f"{lowest[0]} apresenta menor score cultural ({lowest[1]:.2f})")
        
        if highest[1] - lowest[1] > 0.3:
            insights.append("Diferença significativa entre regiões analisadas")
        else:
            insights.append("Perfis culturais similares entre as regiões")
    
    return insights


# ══════════════════════════════════════════════════════════════════════════════
# S4.3 — Unknown Circle Endpoints
# ══════════════════════════════════════════════════════════════════════════════

@circles_router.get(
    "/unknown",
    summary="Sinais Desconhecidos",
    description=(
        "Lista sinais classificados como `emergente_desconhecido` — "
        "sinais que não atingiram o threshold de nenhum dos 16 círculos culturais."
    ),
)
async def list_unknown_signals(
    count: int = Query(50, ge=1, le=500, description="Quantidade de sinais a retornar"),
    current_client: ClientInfo = Depends(get_current_client),
):
    """Lista sinais desconhecidos acumulados."""
    try:
        from core.classifiers.unknown_circle_detector import get_unknown_circle_detector
        detector = get_unknown_circle_detector()
        signals = await detector.get_unknown_signals(count=count)
        queue_size = await detector.get_queue_size()
        return {
            "status": "success",
            "data": {
                "signals": signals,
                "total_in_queue": queue_size,
                "returned": len(signals),
            },
        }
    except Exception as e:
        logger.error(f"Erro ao listar sinais desconhecidos: {e}")
        raise HTTPException(status_code=500, detail={"error": "unknown_signals_error", "message": str(e)})


@circles_router.get(
    "/candidates",
    summary="Candidatos a Novos Círculos",
    description=(
        "Retorna clusters candidatos a novos círculos culturais, "
        "detectados via Ward clustering sobre sinais desconhecidos."
    ),
)
async def list_candidates(
    current_client: ClientInfo = Depends(get_current_client),
):
    """Lista candidatos a novos círculos."""
    try:
        from core.classifiers.unknown_circle_detector import get_unknown_circle_detector
        detector = get_unknown_circle_detector()
        candidates = await detector.get_candidates()
        return {
            "status": "success",
            "data": {
                "candidates": candidates,
                "count": len(candidates),
            },
        }
    except Exception as e:
        logger.error(f"Erro ao listar candidatos: {e}")
        raise HTTPException(status_code=500, detail={"error": "candidates_error", "message": str(e)})


@circles_router.post(
    "/detect",
    summary="Executar Detecção de Novos Círculos",
    description=(
        "Executa Ward clustering sobre sinais desconhecidos acumulados "
        "e retorna candidatos a novos círculos culturais."
    ),
)
async def detect_new_circles(
    current_client: ClientInfo = Depends(get_current_client),
):
    """Executa clustering para detectar candidatos."""
    try:
        from core.classifiers.unknown_circle_detector import get_unknown_circle_detector
        detector = get_unknown_circle_detector()
        candidates = await detector.detect_candidates()
        return {
            "status": "success",
            "data": {
                "candidates": [c.to_dict() for c in candidates],
                "count": len(candidates),
            },
        }
    except Exception as e:
        logger.error(f"Erro na detecção de novos círculos: {e}")
        raise HTTPException(status_code=500, detail={"error": "detection_error", "message": str(e)})


@circles_router.post(
    "/promote",
    summary="Promover Candidato a Novo Círculo",
    description=(
        "Propõe a promoção de um cluster candidato a novo círculo cultural. "
        "Retorna os dados necessários para registro manual pelo admin."
    ),
)
async def promote_candidate(
    cluster_id: int = Query(..., description="ID do cluster a promover"),
    circle_name: str = Query(..., description="Nome para o novo círculo"),
    current_client: ClientInfo = Depends(get_current_client),
):
    """Promove cluster candidato a proposta de novo círculo."""
    try:
        from core.classifiers.unknown_circle_detector import get_unknown_circle_detector
        detector = get_unknown_circle_detector()
        result = await detector.promote_candidate(
            cluster_id=cluster_id,
            circle_name=circle_name,
        )
        if result.get("status") == "error":
            raise HTTPException(status_code=404, detail=result)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao promover candidato: {e}")
        raise HTTPException(status_code=500, detail={"error": "promote_error", "message": str(e)})


@circles_router.get(
    "/unknown/stats",
    summary="Estatísticas do Detector de Círculos Desconhecidos",
)
async def unknown_stats(
    current_client: ClientInfo = Depends(get_current_client),
):
    """Retorna estatísticas do detector."""
    try:
        from core.classifiers.unknown_circle_detector import get_unknown_circle_detector
        detector = get_unknown_circle_detector()
        stats = await detector.get_stats()
        return {"status": "success", "data": stats}
    except Exception as e:
        logger.error(f"Erro nas stats do detector: {e}")
        raise HTTPException(status_code=500, detail={"error": "stats_error", "message": str(e)})

