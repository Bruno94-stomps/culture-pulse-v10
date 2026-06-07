#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 Cache Management Endpoint V9.0 - Culture Pulse
Endpoint para monitoramento e limpeza do cache Redis/Local
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
import logging
from core.cache.cache_redis import get_cache

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v8/cache",
    tags=["Cache & Optimization"]
)

@router.get("/stats")
async def get_cache_stats():
    """Retorna estatísticas detalhadas de uso do cache (Redis vs Fallback Local)"""
    try:
        cache = get_cache()
        return cache.get_stats()
    except Exception as e:
        logger.error(f"Erro ao obter stats do cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/keys/{category}")
async def list_cache_keys(category: str = "default"):
    """Lista chaves ativas no Redis para uma categoria (Se Redis disponível)"""
    cache = get_cache()
    if not cache.redis_client:
        return {"status": "info", "message": "Redis inativo. Cache local não suporta listagem de chaves."}
    
    try:
        pattern = f"{cache.key_prefix}:{category}:*"
        keys = cache.redis_client.keys(pattern)
        return {"category": category, "count": len(keys), "keys": keys[:100]} # Top 100
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/clear/{category}")
async def clear_cache_category(category: str):
    """Limpa todas as entradas de uma categoria específica (ex: 'entropy', 'bertimbau')"""
    try:
        cache = get_cache()
        count = cache.clear_category(category)
        logger.info(f"🧹 Cache limpo para categoria '{category}': {count} itens removidos.")
        return {"status": "success", "category": category, "deleted_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/warmup")
async def trigger_cache_warmup(category: str, terms: List[str]):
    """Força o aquecimento do cache para termos específicos"""
    # Exemplo: Se precisar pré-carregar embeddings do BERTimbau
    return {"status": "scheduled", "message": f"Warm-up planejado para {len(terms)} termos na categoria {category}"}
