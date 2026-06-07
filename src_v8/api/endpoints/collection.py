#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Endpoints para Coleta de Dados - Culture Pulse V8.0
Endpoints REST para os coletores de dados reais

🎯 INTEGRAÇÃO COM COLETORES V7.0
📡 Endpoints:
- POST /api/v8/collect/full - Coleta completa de todas as fontes
- POST /api/v8/collect/quick - Coleta rápida (fontes prioritárias)
- GET /api/v8/collect/status - Status dos coletores
- GET /api/v8/collect/sources - Lista de fontes disponíveis
- POST /api/v8/collect/custom - Coleta customizada por fontes
"""

import sys
import os

# Adicionar path para imports absolutos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging

from api.middleware.rbac_manager import get_current_user
from collectors.orchestrator import (
    cultural_orchestrator,
    collect_cultural_data,
    quick_cultural_analysis,
    get_data_collection_status
)

logger = logging.getLogger(__name__)

REAL_DATA_SOURCES = ['youtube', 'reddit', 'spotify', 'news', 'ibge']
SIMULATED_DATA_SOURCES = ['instagram', 'meetup']
ALL_DATA_SOURCES = REAL_DATA_SOURCES + SIMULATED_DATA_SOURCES
ALLOW_DEMO_COLLECTION = os.getenv("ALLOW_DEMO_COLLECTION", "false").strip().lower() in ("1", "true", "yes", "y")
IS_PRODUCTION = os.getenv("ENVIRONMENT", "production").strip().lower() == "production"

# Gate de produção: em produção, somente fontes reais são usadas por padrão.
# Instagram/Threads e Meetup são tratadas como fontes demo/simuladas e só entram
# se ALLOW_DEMO_COLLECTION=true estiver explicitamente definido.

# Router para endpoints de coleta
collection_router = APIRouter(prefix="/collect", tags=["Data Collection"])


# Modelos Pydantic
class CollectionRequest(BaseModel):
    """Request para coleta de dados"""
    termo: str = Field(..., description="Termo cultural para buscar")
    context: Optional[Dict[str, Any]] = Field(
        None, 
        description="Contexto adicional (localização, período, etc.)"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "termo": "samba",
                "context": {
                    "location": "Rio de Janeiro",
                    "period": "ultimo_mes"
                }
            }
        }


class CustomCollectionRequest(CollectionRequest):
    """Request para coleta customizada"""
    sources: List[str] = Field(
        ..., 
        description="Lista de fontes específicas"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "termo": "forró",
                "sources": ["youtube", "spotify", "news"],
                "context": {
                    "location": "Nordeste"
                }
            }
        }


class CollectionResponse(BaseModel):
    """Response da coleta de dados"""
    status: str
    termo: str
    timestamp: str
    metricas_consolidadas: Dict[str, Any]
    ranking_plataformas: List[List[Any]]
    total_fontes: int
    sinais_detalhados: Dict[str, Any]
    weak_signals: Optional[Dict[str, Any]] = None
    cultural_metrics: Optional[Dict[str, Any]] = None

    class Config:
        extra = "ignore"


class CollectionAPIResponse(BaseModel):
    data: CollectionResponse
    metadata: Dict[str, Any] = Field(default_factory=dict)


def _build_pipeline_context(current_user: Any, request_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    context = dict(request_context or {})

    def _get_user_value(key: str, default=None):
        if current_user is None:
            return default
        if isinstance(current_user, dict):
            return current_user.get(key, default)
        return getattr(current_user, key, default)

    user_id = _get_user_value('user_id') or _get_user_value('id')
    project_id = _get_user_value('project_id')
    user_tier = _get_user_value('tier', 'free')
    onboarding = _get_user_value('onboarding')

    if user_id:
        context['user_id'] = user_id
    if project_id:
        context['project_id'] = project_id
    if user_tier:
        context['user_tier'] = user_tier
    if onboarding:
        context['onboarding'] = onboarding

    return context


# Endpoints
@collection_router.post(
    "/full",
    response_model=CollectionAPIResponse,
    summary="Coleta Completa de Dados",
    description="Coleta dados de todas as fontes disponíveis (YouTube, Reddit, Spotify, NewsAPI, IBGE, Instagram, Meetup). Em produção, por padrão, usa apenas fontes reais; fontes de demonstração só entram se ALLOW_DEMO_COLLECTION=true estiver habilitado."
)
async def collect_full_data(
    request: CollectionRequest,
    current_user = Depends(get_current_user)
):
    """
    Coleta completa de dados culturais de todas as fontes
    
    - **termo**: Termo cultural para buscar (ex: "samba", "capoeira")
    - **context**: Contexto opcional (localização, período)
    
    Retorna análise consolidada de todas as plataformas.
    """
    try:
        user_name = getattr(current_user, 'username', None) or (current_user.get('username') if isinstance(current_user, dict) else 'anonymous')
        logger.info(f"🚀 Usuário {user_name} solicitou coleta completa para '{request.termo}'")
        
        collection_sources = None
        if IS_PRODUCTION:
            collection_sources = REAL_DATA_SOURCES
            logger.info("🔒 Ambiente de produção: usando apenas fontes reais para coleta completa")

        pipeline_context = _build_pipeline_context(current_user, request.context)
        result = await collect_cultural_data(
            termo=request.termo,
            context=pipeline_context,
            sources=collection_sources
        )
        
        if result['status'] != 'success':
            raise HTTPException(
                status_code=400,
                detail=f"Falha na coleta: {result.get('message', 'Erro desconhecido')}"
            )
        
        logger.info(f"✅ Coleta completa concluída para '{request.termo}' - {result['total_fontes']} fontes")

        response = CollectionResponse(**result)
        metadata = {
            'engine_metadata': result.get('metrics_engine_output'),
            'collection_context': {
                'onboarding_context': result.get('onboarding_context'),
                'project_id': result.get('project_id'),
                'user_id': result.get('user_id')
            }
        }
        return CollectionAPIResponse(data=response, metadata=metadata)
        
    except Exception as e:
        logger.error(f"Erro na coleta completa: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno na coleta: {str(e)}"
        )


@collection_router.post(
    "/quick",
    response_model=CollectionAPIResponse,
    summary="Coleta Rápida de Dados",
    description="Coleta rápida com fontes prioritárias para demonstrações e testes. Em produção, este endpoint também opera somente com fontes reais por padrão."
)
async def collect_quick_data(
    request: CollectionRequest,
    current_user = Depends(get_current_user)
):
    """
    Coleta rápida de dados culturais (fontes prioritárias)
    
    Ideal para:
    - Demonstrações rápidas
    - Testes de API
    - Análises preliminares
    
    Usa fontes mais rápidas: Instagram, Meetup, NewsAPI, IBGE
    """
    try:
        user_name = getattr(current_user, 'username', None) or (current_user.get('username') if isinstance(current_user, dict) else 'anonymous')
        logger.info(f"⚡ Usuário {user_name} solicitou quick scan para '{request.termo}'")
        
        # Em produção, quick scan deve usar apenas fontes reais
        pipeline_context = _build_pipeline_context(current_user, request.context)

        if IS_PRODUCTION:
            logger.info("🔒 Ambiente de produção: quick scan usando fontes reais apenas")
            result = await collect_cultural_data(
                termo=request.termo,
                context=pipeline_context,
                sources=REAL_DATA_SOURCES
            )
        else:
            result = await cultural_orchestrator.quick_cultural_scan(
                termo=request.termo,
                context=pipeline_context
            )
        
        if result['status'] != 'success':
            raise HTTPException(
                status_code=400,
                detail=f"Falha no quick scan: {result.get('message', 'Erro desconhecido')}"
            )
        
        logger.info(f"⚡ Quick scan concluído para '{request.termo}' - {result['total_fontes']} fontes")

        response = CollectionResponse(**result)
        metadata = {
            'engine_metadata': result.get('metrics_engine_output'),
            'collection_context': {
                'onboarding_context': result.get('onboarding_context'),
                'project_id': result.get('project_id'),
                'user_id': result.get('user_id')
            }
        }
        return CollectionAPIResponse(data=response, metadata=metadata)
        
    except Exception as e:
        logger.error(f"Erro no quick scan: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno no quick scan: {str(e)}"
        )


@collection_router.post(
    "/custom",
    response_model=CollectionAPIResponse,
    summary="Coleta Customizada",
    description="Coleta de fontes específicas escolhidas pelo usuário"
)
async def collect_custom_data(
    request: CustomCollectionRequest,
    current_user = Depends(get_current_user)
):
    """
    Coleta customizada com fontes específicas
    
    Fontes disponíveis:
    - youtube: YouTube Data API
    - reddit: Reddit API
    - spotify: Spotify Web API
    - news: NewsAPI
    - ibge: IBGE APIs
    - instagram: Instagram/Threads (simulado)
    - meetup: Meetup Events (simulado)
    """
    try:
        # Validar fontes disponíveis
        available_sources = ['youtube', 'reddit', 'spotify', 'news', 'ibge', 'instagram', 'meetup']
        invalid_sources = [s for s in request.sources if s not in available_sources]
        if invalid_sources:
            raise HTTPException(
                status_code=400,
                detail=f"Fontes inválidas: {invalid_sources}. Disponíveis: {available_sources}"
            )

        # Em produção, as fontes demo são bloqueadas por padrão para evitar
        # que protótipos ou fallback simulado façam parte do fluxo de coleta.
        # Apenas quando o operador define ALLOW_DEMO_COLLECTION=true elas podem ser usadas.
        if IS_PRODUCTION and not ALLOW_DEMO_COLLECTION:
            demo_requested = [s for s in request.sources if s in SIMULATED_DATA_SOURCES]
            if demo_requested:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Fontes demo não estão habilitadas em produção: {demo_requested}. "
                        f"Use apenas fontes reais: {REAL_DATA_SOURCES} ou defina ALLOW_DEMO_COLLECTION=true para permitir demos."
                    )
                )
        
        user_name = getattr(current_user, 'username', None) or (current_user.get('username') if isinstance(current_user, dict) else 'anonymous')
        logger.info(f"🎯 Usuário {user_name} solicitou coleta customizada para '{request.termo}' - Fontes: {request.sources}")
        
        pipeline_context = _build_pipeline_context(current_user, request.context)
        result = await collect_cultural_data(
            termo=request.termo,
            context=pipeline_context,
            sources=request.sources
        )
        
        if result['status'] != 'success':
            raise HTTPException(
                status_code=400,
                detail=f"Falha na coleta customizada: {result.get('message', 'Erro desconhecido')}"
            )
        
        logger.info(f"🎯 Coleta customizada concluída para '{request.termo}' - {result['total_fontes']} fontes")

        response = CollectionResponse(**result)
        metadata = {
            'engine_metadata': result.get('metrics_engine_output'),
            'collection_context': {
                'onboarding_context': result.get('onboarding_context'),
                'project_id': result.get('project_id'),
                'user_id': result.get('user_id')
            }
        }
        return CollectionAPIResponse(data=response, metadata=metadata)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na coleta customizada: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno na coleta customizada: {str(e)}"
        )


@collection_router.get(
    "/status",
    summary="Status dos Coletores",
    description="Informações sobre o status de todos os coletores de dados"
)
async def get_collectors_status(
    current_user = Depends(get_current_user)
):
    """
    Status atual de todos os coletores de dados
    
    Retorna:
    - Total de coletores ativos
    - Status de cada coletor
    - Configuração de APIs
    - Dependências e requirements
    """
    try:
        user_name = getattr(current_user, 'username', None) or (current_user.get('username') if isinstance(current_user, dict) else 'anonymous')
        logger.info(f"📊 Usuário {user_name} consultou status dos coletores")
        
        status = get_data_collection_status()
        
        source_policy = "real-only" if IS_PRODUCTION and not ALLOW_DEMO_COLLECTION else "real-plus-demo-allowed" if IS_PRODUCTION else "demo-allowed"
        allowed_sources = REAL_DATA_SOURCES + SIMULATED_DATA_SOURCES if ALLOW_DEMO_COLLECTION else REAL_DATA_SOURCES
        
        # Adicionar informações extras sobre fontes e política de demo
        status['api_info'] = {
            'total_endpoints': 5,
            'available_sources': allowed_sources,
            'real_apis': REAL_DATA_SOURCES,
            'simulated_apis': SIMULATED_DATA_SOURCES,
            'version': 'V8.0',
            'allow_demo_collection': ALLOW_DEMO_COLLECTION,
            'production_mode': IS_PRODUCTION,
            'source_policy': source_policy,
            'demo_sources_enabled': ALLOW_DEMO_COLLECTION
        }
        
        quick_scan_sources = ['instagram', 'meetup', 'news', 'ibge'] if ALLOW_DEMO_COLLECTION else ['news', 'ibge']
        
        status['usage_recommendations'] = {
            'quick_scan_sources': quick_scan_sources,
            'comprehensive_sources': allowed_sources,
            'demo_friendly': SIMULATED_DATA_SOURCES if ALLOW_DEMO_COLLECTION else [],
            'production_ready': REAL_DATA_SOURCES
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Erro ao obter status dos coletores: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao obter status: {str(e)}"
        )


@collection_router.get(
    "/sources",
    summary="Fontes Disponíveis",
    description="Lista todas as fontes de dados disponíveis com detalhes"
)
async def get_available_sources(
    current_user = Depends(get_current_user)
):
    """Lista detalhada de todas as fontes de dados disponíveis"""
    
    allow_demo_collection = ALLOW_DEMO_COLLECTION
    source_policy = "real-only" if IS_PRODUCTION and not allow_demo_collection else "real-plus-demo-allowed" if IS_PRODUCTION else "demo-allowed"
    enabled_demo_sources = allow_demo_collection

    sources_info = {
        "youtube": {
            "name": "YouTube Data API",
            "type": "real_api",
            "description": "Vídeos, comentários e estatísticas do YouTube",
            "requires_api_key": True,
            "rate_limit": "Alto",
            "data_quality": "Alta",
            "cultural_relevance": "Muito Alta",
            "enabled": True,
            "allowed_in_current_policy": True
        },
        "reddit": {
            "name": "Reddit API",
            "type": "real_api", 
            "description": "Posts e comentários de subreddits brasileiros",
            "requires_api_key": True,
            "rate_limit": "Médio",
            "data_quality": "Alta",
            "cultural_relevance": "Alta",
            "enabled": True,
            "allowed_in_current_policy": True
        },
        "spotify": {
            "name": "Spotify Web API",
            "type": "real_api",
            "description": "Músicas, artistas e playlists culturais",
            "requires_api_key": True,
            "rate_limit": "Médio", 
            "data_quality": "Muito Alta",
            "cultural_relevance": "Muito Alta",
            "enabled": True,
            "allowed_in_current_policy": True
        },
        "news": {
            "name": "NewsAPI",
            "type": "real_api",
            "description": "Notícias sobre cultura brasileira",
            "requires_api_key": True,
            "rate_limit": "Baixo",
            "data_quality": "Alta",
            "cultural_relevance": "Alta",
            "enabled": True,
            "allowed_in_current_policy": True
        },
        "ibge": {
            "name": "IBGE APIs",
            "type": "real_api",
            "description": "Dados demográficos e pesquisas governamentais",
            "requires_api_key": False,
            "rate_limit": "Baixo",
            "data_quality": "Muito Alta",
            "cultural_relevance": "Alta",
            "enabled": True,
            "allowed_in_current_policy": True
        },
        "instagram": {
            "name": "Instagram/Threads",
            "type": "simulated",
            "description": "Simulação avançada de engajamento visual",
            "requires_api_key": False,
            "rate_limit": "Nenhum",
            "data_quality": "Média",
            "cultural_relevance": "Muito Alta",
            "enabled": enabled_demo_sources,
            "allowed_in_current_policy": enabled_demo_sources
        },
        "meetup": {
            "name": "Meetup Events",
            "type": "simulated",
            "description": "Simulação de eventos culturais comunitários",
            "requires_api_key": False,
            "rate_limit": "Nenhum", 
            "data_quality": "Média",
            "cultural_relevance": "Alta",
            "enabled": enabled_demo_sources,
            "allowed_in_current_policy": enabled_demo_sources
        }
    }
    
    return {
        "total_sources": len(sources_info),
        "real_apis": len([s for s in sources_info.values() if s["type"] == "real_api"]),
        "simulated": len([s for s in sources_info.values() if s["type"] == "simulated"]),
        "source_policy": source_policy,
        "allow_demo_collection": allow_demo_collection,
        "sources": sources_info,
        "recommended_combinations": {
            "quick_demo": ["instagram", "meetup"],
            "comprehensive_analysis": ["youtube", "reddit", "spotify", "news"],
            "government_data": ["ibge", "news"],
            "social_media": ["youtube", "reddit", "instagram"],
            "music_culture": ["spotify", "youtube"],
            "balanced_mix": ["youtube", "news", "ibge", "instagram"]
        }
    }


# Adicionar ao router principal da API
def include_collection_routes(app):
    """Incluir as rotas de coleta na aplicação principal"""
    app.include_router(collection_router)
