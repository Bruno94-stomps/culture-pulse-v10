#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Middleware de Cache Redis para FastAPI - Culture Pulse V9.0
Middleware automático de cache para endpoints da API

🎯 FUNCIONALIDADES:
- Cache automático de responses
- TTL configurável por endpoint
- Headers de cache informativos
- Invalidação inteligente
- Bypass para endpoints críticos
"""

import json
import time
import hashlib
from typing import Dict, Optional, Set, Callable, Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import logging

try:
    from core.cache.cache_redis import get_cache
except ImportError:
    try:
        from core.cache_redis import get_cache
    except ImportError:
        # Fallback: cache desabilitado se módulo não encontrado
        def get_cache():
            return None

logger = logging.getLogger(__name__)

class CacheMiddleware:
    """
    Middleware de cache automático para FastAPI
    
    Funcionalidades:
    - Cache baseado em método + URL + query params
    - TTL configurável por padrão de rota
    - Headers informativos
    - Exclusão de rotas sensíveis
    """
    
    def __init__(
        self,
        default_ttl: int = 300,  # 5 minutos
        cache_category: str = "api_responses"
    ):
        self.default_ttl = default_ttl
        self.cache_category = cache_category
        self.cache = get_cache()
        
        # Configurações por rota
        self.route_configs: Dict[str, Dict[str, Any]] = {
            # Análises culturais - cache longo
            "/api/v8/analysis": {"ttl": 1800, "enabled": True},  # 30min
            "/api/v8/circles": {"ttl": 1800, "enabled": True},   # 30min
            "/api/v8/tfidf": {"ttl": 900, "enabled": True},      # 15min
            "/api/v8/alma": {"ttl": 1800, "enabled": True},      # 30min
            
            # Coleta - cache curto
            "/api/v8/collect": {"ttl": 60, "enabled": True},     # 1min
            
            # Health - sem cache
            "/api/v8/health": {"ttl": 0, "enabled": False},
            
            # Info - cache médio
            "/api/v8/info": {"ttl": 300, "enabled": True},       # 5min
        }
        
        # Métodos que não devem ser cacheados
        self.no_cache_methods: Set[str] = {"POST", "PUT", "DELETE", "PATCH"}
        
        # Patterns de query params sensíveis
        self.sensitive_params: Set[str] = {"token", "key", "password", "auth"}
    
    def _should_cache(self, request: Request) -> bool:
        """Determina se a requisição deve ser cacheada"""
        # Métodos não cacheáveis
        if request.method in self.no_cache_methods:
            return False
        
        # Verificar configuração da rota
        for pattern, config in self.route_configs.items():
            if request.url.path.startswith(pattern):
                return config.get("enabled", True) and config.get("ttl", 0) > 0
        
        # Por padrão, cachear GET requests
        return request.method == "GET"
    
    def _get_ttl(self, request: Request) -> int:
        """Obtém TTL para a requisição"""
        for pattern, config in self.route_configs.items():
            if request.url.path.startswith(pattern):
                return config.get("ttl", self.default_ttl)
        
        return self.default_ttl
    
    def _make_cache_key(self, request: Request) -> str:
        """Cria chave de cache para a requisição"""
        # Componentes da chave
        method = request.method
        path = request.url.path
        
        # Query params (filtrar sensíveis)
        query_params = dict(request.query_params)
        filtered_params = {
            k: v for k, v in query_params.items()
            if k.lower() not in self.sensitive_params
        }
        
        # Ordenar params para consistência
        params_str = "&".join(f"{k}={v}" for k, v in sorted(filtered_params.items()))
        
        # Gerar hash
        cache_input = f"{method}:{path}:{params_str}"
        cache_hash = hashlib.md5(cache_input.encode()).hexdigest()
        
        return f"api_request:{cache_hash}"
    
    def _extract_response_data(self, response: Response) -> Optional[Dict[str, Any]]:
        """Extrai dados da resposta para cache"""
        try:
            if hasattr(response, 'body'):
                body = response.body
                if isinstance(body, bytes):
                    body = body.decode('utf-8')
                
                return {
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'body': body,
                    'cached_at': time.time()
                }
        except Exception as e:
            logger.warning(f"Falha ao extrair dados da resposta: {e}")
        
        return None
    
    def _create_cached_response(self, cached_data: Dict[str, Any]) -> Response:
        """Cria resposta a partir dos dados do cache"""
        try:
            # Headers do cache
            headers = cached_data.get('headers', {})
            headers['X-Cache'] = 'HIT'
            headers['X-Cache-Timestamp'] = str(cached_data.get('cached_at', 0))
            
            # Criar resposta
            if cached_data['status_code'] == 200:
                try:
                    # Tentar JSON
                    json_body = json.loads(cached_data['body'])
                    return JSONResponse(
                        content=json_body,
                        status_code=cached_data['status_code'],
                        headers=headers
                    )
                except json.JSONDecodeError:
                    # Resposta texto
                    return Response(
                        content=cached_data['body'],
                        status_code=cached_data['status_code'],
                        headers=headers
                    )
            else:
                return Response(
                    content=cached_data['body'],
                    status_code=cached_data['status_code'],
                    headers=headers
                )
                
        except Exception as e:
            logger.warning(f"Falha ao criar resposta do cache: {e}")
            return None
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """Middleware principal"""
        # Verificar se deve cachear
        if not self._should_cache(request):
            response = await call_next(request)
            response.headers["X-Cache"] = "BYPASS"
            return response
        
        # Gerar chave de cache
        cache_key = self._make_cache_key(request)
        
        # Se o cache não está disponível, bypass direto
        if self.cache is None:
            response = await call_next(request)
            response.headers["X-Cache"] = "BYPASS"
            return response

        # Tentar cache
        cached_data = await self.cache.aget(cache_key, self.cache_category)
        if cached_data:
            cached_response = self._create_cached_response(cached_data)
            if cached_response:
                logger.debug(f"Cache HIT para {request.url.path}")
                return cached_response
        
        # Cache miss - executar request
        start_time = time.time()
        response = await call_next(request)
        processing_time = time.time() - start_time
        
        # Headers informativos
        response.headers["X-Cache"] = "MISS"
        response.headers["X-Processing-Time"] = f"{processing_time:.3f}s"
        
        # Cachear resposta se sucesso
        if response.status_code == 200:
            ttl = self._get_ttl(request)
            response_data = self._extract_response_data(response)
            
            if response_data and ttl > 0:
                await self.cache.aset(
                    cache_key,
                    response_data,
                    ttl,
                    self.cache_category
                )
                logger.debug(f"Cached response para {request.url.path} (TTL: {ttl}s)")
        
        return response
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalida cache baseado em padrão
        
        Args:
            pattern: Padrão de rota para invalidar (ex: "/api/v8/analysis")
        
        Returns:
            Número de chaves invalidadas
        """
        try:
            return self.cache.clear_category(f"{self.cache_category}:{pattern}")
        except Exception as e:
            logger.warning(f"Falha ao invalidar pattern '{pattern}': {e}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do cache"""
        stats = self.cache.get_stats()
        stats['middleware_config'] = {
            'default_ttl': self.default_ttl,
            'route_configs': self.route_configs,
            'no_cache_methods': list(self.no_cache_methods)
        }
        return stats

# Middleware global para aplicação
cache_middleware = CacheMiddleware()

def add_cache_middleware(app):
    """Adiciona middleware de cache à aplicação FastAPI"""
    app.middleware("http")(cache_middleware)
    return cache_middleware

# Endpoint para gestão de cache
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

cache_router = APIRouter(prefix="/api/v8/cache", tags=["Cache Management"])

@cache_router.get("/stats")
async def get_cache_stats():
    """Obtém estatísticas do cache"""
    return cache_middleware.get_cache_stats()

@cache_router.post("/invalidate/{pattern:path}")
async def invalidate_cache(pattern: str):
    """
    Invalida cache por padrão de rota
    
    Args:
        pattern: Padrão da rota (ex: analysis, circles)
    """
    try:
        count = cache_middleware.invalidate_pattern(pattern)
        return {
            "message": f"Cache invalidado para pattern '{pattern}'",
            "invalidated_keys": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao invalidar cache: {e}")

@cache_router.post("/clear")
async def clear_all_cache():
    """Limpa todo o cache da API"""
    try:
        cache = get_cache()
        count = cache.clear_category(cache_middleware.cache_category)
        return {
            "message": "Cache da API limpo",
            "cleared_keys": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao limpar cache: {e}")

if __name__ == "__main__":
    # Teste do middleware
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    
    app = FastAPI()
    add_cache_middleware(app)
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "test", "timestamp": time.time()}
    
    client = TestClient(app)
    
    # Primeira requisição
    response1 = client.get("/test")
    print(f"Response 1: {response1.headers.get('X-Cache')}")
    
    # Segunda requisição (deve ser cache)
    response2 = client.get("/test")
    print(f"Response 2: {response2.headers.get('X-Cache')}")
    
    # Stats
    stats = cache_middleware.get_cache_stats()
    print(f"Cache stats: {json.dumps(stats, indent=2)}")
