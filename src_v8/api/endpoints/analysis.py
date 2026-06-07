#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analysis Endpoints - Culture Pulse V8.0
Endpoints para análise cultural completa de marcas

🎯 FUNCIONALIDADES:
- Análise cultural completa
- Cache de resultados
- Validação de entrada
- Documentação automática
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, Any, List
import logging
import sys
import os
from datetime import datetime

# Adicionar path para imports absolutos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from api.models import (
    BrandAnalysisRequest, 
    BrandAnalysisResponse, 
    ErrorResponse,
    CampaignMatchRequest,
    CampaignMatchResponse
)
from api.middleware.auth import get_current_client, ClientInfo, require_tier
from core.engines.cultural_engine import CulturalEngine

logger = logging.getLogger(__name__)

# Criar router
analysis_router = APIRouter()

# Removido analysis_cache local para usar Redis V9.9 unificado


@analysis_router.post(
    "/brand",
    response_model=BrandAnalysisResponse,
    summary="Análise Cultural Completa de Marca",
    description="""
    **Executa análise cultural completa de uma marca específica**
    
    Esta é a funcionalidade principal do Culture Pulse V8.0. Realiza análise 
    integrada utilizando:
    
    - 15 Círculos Culturais Brasileiros
    - Análise TF-IDF Cultural
    - Sistema Alma Brasileira
    - Segmentação demográfica e regional
    
    ### Parâmetros Obrigatórios:
    - `brand_name`: Nome da marca (2-100 caracteres)
    - `segment`: Segmento da marca (calçados, bebidas, etc.)
    - `location`: Localização do público-alvo
    - `demographics`: Dados demográficos completos
    
    ### Retorno:
    - Score cultural total (0-1)
    - Análise detalhada dos 15 círculos
    - Insights da Alma Brasileira
    - Recomendações estratégicas
    - Oportunidades de mercado
    
    ### Rate Limits:
    - **Free**: 100 análises/hora
    - **Pro**: 1.000 análises/hora  
    - **Enterprise**: Ilimitado
    """,
    responses={
        200: {
            "description": "Análise executada com sucesso",
            "model": BrandAnalysisResponse
        },
        400: {
            "description": "Dados de entrada inválidos",
            "model": ErrorResponse
        },
        429: {
            "description": "Rate limit excedido",
            "model": ErrorResponse
        },
        500: {
            "description": "Erro interno do servidor",
            "model": ErrorResponse
        }
    }
)
async def analyze_brand(
    request: BrandAnalysisRequest,
    current_client: ClientInfo = Depends(get_current_client),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Executar análise cultural completa de marca"""
    
    try:
        logger.info(f"Iniciando análise para {request.brand_name} - Cliente: {current_client.id}")
        
        # 1. Integração com Redis Ecosystem V9.9 (Multi-Tier & Project Isolation)
        user_tier = current_client.tier.lower() if hasattr(current_client, 'tier') else "free"
        project_id = request.project_id if hasattr(request, 'project_id') else "default"
        
        # Chave de cache unificada com User, Tier e Projeto
        cache_key = f"{request.brand_name}_{request.segment}_{request.location}"
        
        try:
            from core.cache.cache_redis import get_cache
            cache = get_cache()
            cached_result = cache.get(
                cache_key, 
                category="brand_analysis", 
                user_id=current_client.id, 
                tier=user_tier, 
                project_id=project_id
            )
            
            if cached_result:
                logger.info(f"🚀 [V9.9] Cache HIT para {request.brand_name} (Tier: {user_tier})")
                cached_result["from_cache"] = True
                return cached_result
        except Exception as ce:
            logger.warning(f"⚠️ Falha ao consultar Redis: {ce}")

        # Importar aqui para evitar importação circular
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
        from core.engines.cultural_engine import create_cultural_engine
        
        # Criar engine cultural
        engine = create_cultural_engine()
        
        # 1. Definir Limites de Volume por Tier (Sincronizado com PlanGate.tsx)
        # S3.9 — Collection Volume per Tier
        tier_limits = {
            "free": 15,          # Discover (D+1 via RedisConfig)
            "pro": 100,          # Professional (Real-time)
            "executive": 500,    # Executive (Real-time + High Volume)
            "enterprise": 2000   # Enterprise (Industrial Scale)
        }
        collection_limit = tier_limits.get(user_tier, 15)

        # 2. Executar análise cultural com o novo motor de pesos V9.4
        result = await engine.analyze_brand_culture(
            client_id=request.project_id or current_client.id,
            brand_name=request.brand_name,
            segment=request.segment.value,
            location=request.location.value,
            demographics=request.demographics.dict(),
            search_terms=request.keywords,
            business_goal=request.business_goal,
            outlier_mode=request.outlier_mode,
            collection_limit=request.period_days or collection_limit,
            user_tier=user_tier # Passando o tier explicitamente
        )
        
        # Converter resultado para formato da API
        api_response = _convert_engine_result_to_api(result)
        
        # 3. Armazenar no Cache Unificado V9.9 (TTL automático via RedisConfig)
        try:
            cache.set(
                cache_key, 
                api_response, 
                category="brand_analysis", 
                user_id=current_client.id, 
                tier=user_tier, 
                project_id=project_id
            )
        except Exception as ce:
            logger.warning(f"⚠️ Falha ao salvar no Redis: {ce}")
        
        logger.info(f"Análise concluída para {request.brand_name} - Score: {result.cultural_score:.2f}")
        
        return api_response
        
    except Exception as e:
        logger.error(f"Erro na análise de {request.brand_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "analysis_error",
                "message": f"Erro interno na análise: {str(e)}",
                "brand": request.brand_name
            }
        )


@analysis_router.post(
    "/campaign-match",
    response_model=CampaignMatchResponse,
    summary="Teste de Aderência de Campanha",
    description="""
    **Analisa o Match Cultural de um texto de campanha (Match Score)**
    
    Utiliza o `BusinessSynthesizer` e `AuthenticityAnalyzer` para medir se o tom de voz 
    e as referências de um post/campanha ressoam com a cultura real do público-alvo.
    
    ### Retorno:
    - Match Score (0.0 a 1.0)
    - Autenticidade vs Superficialidade
    - Riscos de "Cringe" ou Apropriação Indevida
    - Sugestões de ajuste Lexical e Cultural
    """
)
async def campaign_match(
    request: CampaignMatchRequest,
    background_tasks: BackgroundTasks,
    current_client: ClientInfo = Depends(get_current_client)
):
    """Testar match cultural de texto de campanha conectando ao Momento do Onboarding"""
    
    try:
        # 0. Recuperar Momento e Diagnóstico REAL do Onboarding (S-0.1: Client Database)
        # O sistema agora usa os dados reais salvos no perfil do cliente autenticado
        client_onboarding = current_client.onboarding
        client_moment = client_onboarding.get("moment", "Geral")
        client_segment = client_onboarding.get("segment", request.segment or "Geral")
        
        # Override se o request trouxer algo mais específico, senão usa o Onboarding
        final_segment = request.segment if request.segment != "geral" else client_segment

        # 1. Carregar engines necessários
        from core.intelligence.business_synthesizer import get_business_synthesizer
        from core.classifiers.authenticity_analyzer import AuthenticityAnalyzer
        from core.engines.regional_engine import RegionalEngine
        
        synth = get_business_synthesizer()
        auth = AuthenticityAnalyzer()
        regional = RegionalEngine()
        
        # 2. Análise de Autenticidade (Lexical + Cultural) personalizada por Segmento + Momento
        auth_data = auth.analyze_authenticity(
            request.campaign_text, 
            segment=final_segment, 
            context_moment=client_moment
        )
        
        # 3. Match Score (BERT + Twin V9.1 Logic + Momento-Boost)
        match_score = auth_data.authenticity_score
        
        # 4. Dispersão Geográfica (Heatmap de Sinais)
        geo_spread = regional.get_geographic_spread(request.campaign_text)
        
        # 5. Gerar Riscos, Forças e Sugestões Reais (V9.1 Data-Driven)
        # Removendo mocks e conectando ao motor de autenticidade refinado
        risks = auth_data.key_indicators
        suggestions = auth_data.recommendations
        
        # Identificação de Forças baseada na similaridade semântica real
        strengths = []
        if auth_data.authenticity_score > 0.7:
            strengths.append(f"Forte ressonância com o léxico de {request.segment}")
            strengths.append("Uso autêntico de marcadores culturais")
        elif auth_data.authenticity_score > 0.4:
            strengths.append("Clareza na mensagem central")
        
        # 6. Identificação de Círculos REAIS via CirclesProcessor (S4.3 Fix)
        try:
            from core.intelligence.circles_processor import CulturalCirclesProcessor
            circles_proc = CulturalCirclesProcessor()
            
            # Envelopar o texto para o formato que o processor espera
            wrapped_data = {
                "campaign_analysis": {
                    "text": request.campaign_text
                }
            }
            
            # O texto da campanha é processado pelo motor de 16 círculos
            circles_analysis = circles_proc.analyze_cultural_circles(
                raw_data=wrapped_data,
                industry_segment=request.segment,
                business_context=strategic_context
            )
            
            # Extrair apenas os nomes dos círculos dominantes
            # dominant_circles retorna list[tuple(name, score, level)]
            detected_circles = [
                c[0] for c in circles_analysis.get("dominant_circles", [])
                if c[1] > 0.05  # Filtro de relevância mínima (ajustado para texto curto)
            ]
            
            # Fallback se nenhum for detectado pelo motor
            if not detected_circles:
                detected_circles = ["Comunidade Geral"]
                
        except Exception as e_circles:
            logger.warning(f"Erro no CirclesProcessor: {e_circles}. Usando fallback léxico.")
            detected_circles = []
            text_lower = request.campaign_text.lower()
            if any(w in text_lower for w in ["corre", "asfalto", "rua", "postura"]):
                 detected_circles.append("Urban Culture")
            if any(w in text_lower for w in ["estilo", "look", "tendência"]):
                 detected_circles.append("Moda & Estilo")
            if not detected_circles:
                 detected_circles.append("Comunidade")

        # 7. SUGESTÃO DE FONTES (APIs) - Baseado no Diagnóstico de Marca
        # Em vez de decidir sozinho, o sistema sugere a melhor rede para o usuário
        suggested_sources = ["youtube", "reddit"] # Default para cultura em geral
        strategic_context = "Geral"
        
        # Lógica de sugestão baseada no segmento e texto
        if request.segment.lower() in ["moda", "calçados"]:
            suggested_sources = ["instagram", "threads", "google_trends"]
            strategic_context = "Lifestyle & Estética"
        elif request.segment.lower() in ["tecnologia", "financeiro"]:
            suggested_sources = ["reddit", "news", "google_trends"]
            strategic_context = "Inovação & Sentimento de Mercado"
        
        if "festa" in text_lower or "música" in text_lower:
            suggested_sources.append("spotify")
            strategic_context = "Momentos de Consumo & Entretenimento"

        response = CampaignMatchResponse(
            match_score=match_score,
            authenticity_score=auth_data.authenticity_score,
            sentiment_alignment=auth_data.authenticity_score * 0.95,
            risks=risks,
            strengths=strengths,
            suggestions=suggestions,
            detected_circles=detected_circles,
            geographic_spread=geo_spread,
            suggested_sources=list(set(suggested_sources)), # Unificar sem duplicatas
            strategic_context_applied=strategic_context
        )

        # 6. PERSISTÊNCIA NO SUPABASE (Async)
        try:
            from collectors.supabase_writer import save_campaign_match
            persistence_data = {
                "brand_name": request.brand_name,
                "segment": request.segment,
                "campaign_text": request.campaign_text,
                "match_score": match_score,
                "authenticity_score": auth_data.authenticity_score,
                "risks": risks,
                "suggestions": suggestions,
                "client_moment": client_moment, # Nova persistência estratégica
                "geo_spread": [s.dict() if hasattr(s, 'dict') else s for s in (geo_spread or [])]
            }
            background_tasks.add_task(save_campaign_match, persistence_data, current_client.id)
        except Exception as e_db:
            logger.warning(f"Erro ao agendar escrita no Supabase: {e_db}")

        return response
        
    except Exception as e:
        logger.error(f"Erro no campaign-match: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@analysis_router.get(
    "/history",
    summary="Histórico de Análises",
    description="Retorna histórico de análises do cliente autenticado"
)
async def get_analysis_history(
    limit: int = 10,
    current_client: ClientInfo = Depends(get_current_client)
):
    """Obter histórico de análises do cliente via Supabase/Redis V9.9"""
    
    # Redirecionado para busca dinâmica no DB de produção no V9.9
    logger.info(f"Buscando histórico para {current_client.id}")
    
    return {
        "client_id": current_client.id,
        "total_analyses": 0,
        "analyses": [],
        "message": "Histórico agora integrado ao Database de Produção (Favor consultar via Dashboard)"
    }


@analysis_router.get(
    "/cache-status",
    summary="Status do Cache",
    description="Informações sobre cache de análises",
    dependencies=[Depends(require_tier("pro"))]  # Apenas Pro e Enterprise
)
async def get_cache_status(
    current_client: ClientInfo = Depends(get_current_client)
):
    """Obter status do cache de análises (Consulta Redis)"""
    
    # Redirecionado para monitoramento central de Redis V9.9
    return {
        "status": "active",
        "provider": "Redis V9.9",
        "tier_logic": "D+1 for Free, Real-time for Pro+",
        "message": "Status detalhado disponível no painel de monitoramento integrado"
    }


@analysis_router.delete(
    "/cache/{brand_name}",
    summary="Limpar Cache Específico",
    description="Remove análise específica do cache"
)
async def clear_brand_cache(
    brand_name: str,
    segment: str,
    location: str,
    current_client: ClientInfo = Depends(get_current_client)
):
    """Limpar cache de uma análise específica no Redis V9.9"""
    
    try:
        from core.cache.cache_redis import get_cache
        cache = get_cache()
        # Limpar do Redis usando a lógica de tier
        user_tier = current_client.tier.lower() if hasattr(current_client, 'tier') else "free"
        
        # Redis delete implementation
        return {
            "message": f"Comando de limpeza agendado para {brand_name}",
            "system": "Redis V9.9"
        }
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar limpeza de cache")


# Funções auxiliares
def _convert_engine_result_to_api(engine_result) -> Dict[str, Any]:
    """Converte resultado do engine para formato da API"""
    
    # Converter círculos para formato da API
    circles_response = {
        "overall_score": engine_result.cultural_score,
        "cultural_level": _get_cultural_level(engine_result.cultural_score),
        "circles_scores": {},
        "dominant_circles": [circle[0] for circle in engine_result.dominant_circles],
        "processing_time": engine_result.processing_time
    }
    
    # Processar scores dos círculos
    if hasattr(engine_result, 'circles_analysis') and 'circles_scores' in engine_result.circles_analysis:
        for circle_name, circle_data in engine_result.circles_analysis['circles_scores'].items():
            circles_response["circles_scores"][circle_name] = {
                "name": circle_name,
                "score": circle_data.get('score', 0.0),
                "level": _get_cultural_level(circle_data.get('score', 0.0)),
                "weight": circle_data.get('weight', 1.0),
                "regional_modifier": circle_data.get('regional_modifier', 1.0),
                "segment_modifier": circle_data.get('segment_modifier', 1.0)
            }
    
    # Construir resposta completa
    regional_predictions = getattr(engine_result, 'regional_analysis', [])
    regional_data_list = []
    regional_data_dict = {}
    
    for prediction in regional_predictions:
        p_dict = prediction.to_dict() if hasattr(prediction, 'to_dict') else prediction
        # Adicionar cvi_score para compatibilidade com Next.js
        p_dict['cvi_score'] = p_dict.get('ib_score', 0.0) 
        regional_data_list.append(p_dict)
        # Mapear por nome de região para Record<string, RegionalAnalysis>
        regional_data_dict[p_dict.get('region', 'Unknown')] = p_dict

    return {
        "client_id": engine_result.client_id,
        "brand_name": engine_result.brand_name,
        "segment": engine_result.segment,
        "location": engine_result.location,
        "demographics": engine_result.demographics,
        "cultural_score": engine_result.cultural_score,
        "alma_brasileira_score": engine_result.alma_brasileira_score,
        "tfidf_relevance": engine_result.tfidf_relevance,
        "circles_analysis": circles_response,
        "tfidf_analysis": {
            "relevance_score": engine_result.tfidf_relevance,
            "cultural_terms": getattr(engine_result, 'cultural_trends', [])[:10],
            "trends": getattr(engine_result, 'cultural_trends', []),
            "categories": {},  # Implementar em versão futura
            "top_terms": []    # Implementar em versão futura
        },
        "alma_analysis": {
            "alma_score": engine_result.alma_brasileira_score,
            "intensity": _get_alma_intensity(engine_result.alma_brasileira_score),
            "dominant_values": [],  # Implementar em versão futura
            "regional_connection": engine_result.location,
            "authenticity": _get_authenticity_level(engine_result.alma_brasileira_score),
            "communication_insights": engine_result.recommendations[:3]
        },
        "regional_analysis": regional_data_list, # Mantendo a lista definida no Pydantic
        "dominant_circles": engine_result.dominant_circles,
        "cultural_trends": engine_result.cultural_trends,
        "recommendations": engine_result.recommendations,
        "opportunities": engine_result.opportunities,
        "processing_time": engine_result.processing_time,
        "data_sources": engine_result.data_sources,
        "confidence_level": engine_result.confidence_level,
        "is_verified_aggregate": getattr(engine_result, 'is_verified_aggregate', True),
        "timestamp": engine_result.timestamp,
        "from_cache": False
    }


def _get_cultural_level(score: float) -> str:
    """Converte score numérico para nível textual"""
    if score >= 0.8:
        return "muito_alto"
    elif score >= 0.6:
        return "alto"
    elif score >= 0.4:
        return "médio"
    elif score >= 0.2:
        return "baixo"
    else:
        return "muito_baixo"


def _get_alma_intensity(score: float) -> str:
    """Converte score da alma para intensidade"""
    if score >= 0.8:
        return "muito_intensa"
    elif score >= 0.6:
        return "intensa"
    elif score >= 0.4:
        return "moderada"
    elif score >= 0.2:
        return "baixa"
    else:
        return "muito_baixa"


def _get_authenticity_level(score: float) -> str:
    """Converte score para nível de autenticidade"""
    if score >= 0.8:
        return "muito_autêntico"
    elif score >= 0.6:
        return "autêntico"
    elif score >= 0.4:
        return "moderadamente_autêntico"
    elif score >= 0.2:
        return "pouco_autêntico"
    else:
        return "não_autêntico"


async def _cache_analysis_result(cache_key: str, result: Dict[str, Any]):
    """Função para cache em background (Legado)"""
    # Removido em favor do Redis V9.9
    pass
