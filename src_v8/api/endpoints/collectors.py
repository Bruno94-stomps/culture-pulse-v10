"""
Legacy endpoint module for data collectors.
This file is no longer registered by the API router.
The active collection API is unified under src_v8/api/endpoints/collection.py.
"""

import sys
import os

# Adicionar path para imports absolutos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime

from api.middleware.auth import verify_api_key
from api.models import (
    CollectorResponse,
    CollectorTestResponse,
    CulturalSignalData,
    ErrorResponse
)
from collectors.data_collectors import create_unified_collectors

REAL_DATA_SOURCES = ['youtube', 'reddit', 'spotify', 'news', 'ibge']
SIMULATED_DATA_SOURCES = ['instagram', 'meetup']
ALLOW_DEMO_COLLECTION = os.getenv("ALLOW_DEMO_COLLECTION", "false").strip().lower() in ("1", "true", "yes", "y")
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").strip().lower() == "production"

router = APIRouter(prefix="/collectors", tags=["Data Collectors"])

@router.get("/test", response_model=CollectorTestResponse)
async def test_data_collectors(
    token_data: dict = Depends(verify_api_key)
):
    """
    Testa todos os coletores de dados consolidados com termo padrão
    """
    try:
        # Execute o teste dos coletores consolidados
        collectors = create_unified_collectors()
        
        if IS_PRODUCTION and not ALLOW_DEMO_COLLECTION:
            collectors = {
                name: impl for name, impl in collectors.items()
                if name in REAL_DATA_SOURCES
            }
        
        termo_teste = "samba"
        context = {"location": "Rio de Janeiro - Capital"}
        
        results = {}
        
        for name, collector in collectors.items():
            try:
                signal = await collector.collect_cultural_data(termo_teste, context)
                if signal:
                    results[name] = {
                        "status": "success",
                        "momentum": signal.momentum,
                        "volume": signal.volume,
                        "sentiment": signal.sentiment,
                        "timestamp": signal.timestamp,
                        "extras": signal.dados_extras
                    }
                else:
                    results[name] = {
                        "status": "failed",
                        "error": "No data returned"
                    }
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return CollectorTestResponse(
            test_term=termo_teste,
            context=context,
            results=results,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao testar coletores: {str(e)}")

@router.post("/collect", response_model=CollectorResponse)
async def collect_cultural_data(
    term: str = Query(..., description="Termo cultural para coletar"),
    collectors: Optional[List[str]] = Query(None, description="Lista de coletores específicos (youtube, reddit, spotify)"),
    location: Optional[str] = Query("Brasil", description="Localização para contextualização"),
    token_data: dict = Depends(verify_api_key)
):
    """
    Coleta dados culturais em tempo real para um termo específico
    """
    try:
        all_collectors = create_unified_collectors()
        
        # Filtrar coletores se especificado
        if collectors:
            invalid_sources = [s for s in collectors if s not in all_collectors]
            if invalid_sources:
                raise HTTPException(
                    status_code=400,
                    detail=f"Coletores inválidos: {invalid_sources}. Disponíveis: {list(all_collectors.keys())}"
                )
            selected_collectors = {name: collector for name, collector in all_collectors.items() 
                                 if name in collectors}
        else:
            selected_collectors = all_collectors

        if IS_PRODUCTION and not ALLOW_DEMO_COLLECTION:
            demo_requested = [name for name in selected_collectors if name in SIMULATED_DATA_SOURCES]
            if demo_requested:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Coletores demo não estão habilitados em produção: {demo_requested}. "
                        f"Use apenas coletores reais: {REAL_DATA_SOURCES} ou defina ALLOW_DEMO_COLLECTION=true."
                    )
                )
            selected_collectors = {
                name: collector for name, collector in selected_collectors.items() 
                if name in REAL_DATA_SOURCES
            }
        
        context = {"location": location}
        results = {}
        
        for name, collector in selected_collectors.items():
            try:
                signal = await collector.collect_cultural_data(term, context)
                if signal:
                    results[name] = CulturalSignalData(
                        momentum=signal.momentum,
                        volume=signal.volume,
                        sentiment=signal.sentiment,
                        timestamp=signal.timestamp,
                        source=signal.fonte,
                        is_verified=getattr(signal, 'is_verified', True),
                        accuracy_score=getattr(signal, 'accuracy_score', 1.0),
                        reliability=getattr(signal, 'reliability', 'MEDIA'),
                        source_url=getattr(signal, 'source_url', None),
                        source_category=getattr(signal, 'source_category', None),
                        image_url=getattr(signal, 'image_url', None),
                        extras=signal.dados_extras
                    )
                else:
                    results[name] = None
                    
            except Exception as e:
                # Log do erro mas continua com outros coletores
                print(f"Erro no coletor {name}: {e}")
                results[name] = None
        
        # Calcular is_verified_aggregate (True se a maioria das fontes for real/verificada)
        verified_count = len([r for r in results.values() if r and r.is_verified])
        is_verified_aggregate = verified_count > (len([r for r in results.values() if r]) / 2)
        
        return CollectorResponse(
            term=term,
            context=context,
            signals=results,
            is_verified_aggregate=is_verified_aggregate,
            timestamp=datetime.now().isoformat(),
            total_collectors=len(selected_collectors),
            successful_collectors=len([r for r in results.values() if r is not None])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na coleta de dados: {str(e)}")

@router.get("/available", response_model=Dict[str, Any])
async def get_available_collectors(
    token_data: dict = Depends(verify_api_key)
):
    """
    Lista coletores disponíveis e suas descrições
    """
    try:
        collectors_info = {
            "youtube": {
                "name": "YouTube Collector",
                "description": "Coleta dados de vídeos, comentários e tendências do YouTube",
                "data_types": ["videos", "comments", "trends"],
                "real_time": True,
                "enabled": True,
                "allowed_in_current_policy": True
            },
            "reddit": {
                "name": "Reddit Collector", 
                "description": "Coleta posts e comentários de subreddits brasileiros",
                "data_types": ["posts", "comments", "scores"],
                "real_time": True,
                "enabled": True,
                "allowed_in_current_policy": True
            },
            "spotify": {
                "name": "Spotify Collector",
                "description": "Coleta dados de popularidade musical e playlists",
                "data_types": ["tracks", "playlists", "popularity"],
                "real_time": True,
                "enabled": True,
                "allowed_in_current_policy": True
            },
            "news": {
                "name": "NewsAPI Collector",
                "description": "Coleta notícias e artigos culturais em tempo real",
                "data_types": ["articles", "headlines", "sources"],
                "real_time": True,
                "enabled": True,
                "allowed_in_current_policy": True
            },
            "ibge": {
                "name": "IBGE Collector",
                "description": "Dados demográficos e socioeconômicos do Brasil",
                "data_types": ["demographics", "economics", "regions"],
                "real_time": True,
                "enabled": True,
                "allowed_in_current_policy": True
            },
            "instagram": {
                "name": "Instagram/Threads Collector",
                "description": "Análise de tendências visuais e culturais do Instagram/Threads",
                "data_types": ["posts", "hashtags", "trends"],
                "real_time": False,
                "enabled": ALLOW_DEMO_COLLECTION,
                "allowed_in_current_policy": ALLOW_DEMO_COLLECTION
            },
            "meetup": {
                "name": "Meetup Collector",
                "description": "Eventos culturais e comunitários",
                "data_types": ["events", "communities", "trends"],
                "real_time": False,
                "enabled": ALLOW_DEMO_COLLECTION,
                "allowed_in_current_policy": ALLOW_DEMO_COLLECTION
            },
            "google_trends": {
                "name": "Google Trends Collector",
                "description": "Tendências de pesquisa e interesse cultural no Google",
                "data_types": ["trends", "searches", "popularity"],
                "real_time": True,
                "enabled": True,
                "allowed_in_current_policy": True
            },
            "rss_cultural": {
                "name": "RSS Cultural Collector",
                "description": "Coleta insights de portais culturais, blogs e veículos especializados via RSS",
                "data_types": ["articles", "cultural_insights", "headlines"],
                "real_time": True,
                "enabled": True,
                "allowed_in_current_policy": True
            }
        }

        source_policy = "real-only" if IS_PRODUCTION and not ALLOW_DEMO_COLLECTION else "real-plus-demo-allowed" if IS_PRODUCTION else "demo-allowed"

        return {
            "available_collectors": list(collectors_info.keys()),
            "collectors_info": collectors_info,
            "total_count": len(collectors_info),
            "source_policy": source_policy,
            "allow_demo_collection": ALLOW_DEMO_COLLECTION,
            "production_mode": IS_PRODUCTION
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar coletores: {str(e)}")

@router.get("/status", response_model=Dict[str, Any])
async def get_collectors_status(
    token_data: dict = Depends(verify_api_key)
):
    """
    Verifica o status de conectividade dos coletores
    """
    try:
        collectors = create_unified_collectors()
        status = {}
        
        for name, collector in collectors.items():
            try:
                connection_ok = hasattr(collector, 'client') and bool(getattr(collector, 'client', None))
                status[name] = {
                    "status": "online" if connection_ok else "unconfigured",
                    "client_configured": connection_ok,
                    "cache_size": len(collector.cache.cache) if hasattr(collector, 'cache') else 0,
                    "is_demo_source": name in SIMULATED_DATA_SOURCES,
                    "allowed_in_current_policy": not IS_PRODUCTION or ALLOW_DEMO_COLLECTION or name in REAL_DATA_SOURCES
                }
            except Exception as e:
                status[name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        source_policy = "real-only" if IS_PRODUCTION and not ALLOW_DEMO_COLLECTION else "real-plus-demo-allowed" if IS_PRODUCTION else "demo-allowed"

        return {
            "collectors_status": status,
            "production_mode": IS_PRODUCTION,
            "allow_demo_collection": ALLOW_DEMO_COLLECTION,
            "source_policy": source_policy,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao verificar status: {str(e)}")
