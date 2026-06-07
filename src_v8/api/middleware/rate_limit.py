#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Middleware de Rate Limiting - Culture Pulse V8.0
Sistema de controle de taxa de requisições

🎯 RESPONSABILIDADES:
- Controle de requisições por cliente
- Diferentes limites por tier
- Headers informativos
- Cache distribuído (simulado)
"""

from fastapi import Request, Response, HTTPException, status
from typing import Dict, Any
import time
import logging
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

# Cache em memória para rate limiting
# Em produção, usar Redis ou similar
rate_limit_cache = defaultdict(lambda: {
    "requests": deque(),
    "blocked_until": 0
})


class RateLimiter:
    """Sistema de rate limiting baseado em sliding window"""
    
    def __init__(self):
        self.window_size = 3600  # 1 hora em segundos
        self.cleanup_interval = 300  # Limpeza a cada 5 minutos
        self.last_cleanup = time.time()
    
    def check_rate_limit(self, client_id: str, tier: str, limit: int) -> Dict[str, Any]:
        """
        Verifica se cliente está dentro do rate limit
        
        Args:
            client_id: ID do cliente
            tier: Tier do cliente (free, pro, enterprise)
            limit: Limite de requests por hora (-1 = ilimitado)
            
        Returns:
            Dict com informações do rate limit
        """
        current_time = time.time()
        
        # Enterprise tem limite ilimitado
        if limit == -1:
            return {
                "allowed": True,
                "requests_remaining": "unlimited",
                "reset_time": None,
                "current_usage": 0
            }
        
        # Cleanup periódico
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_requests()
            self.last_cleanup = current_time
        
        client_data = rate_limit_cache[client_id]
        
        # Verificar se está bloqueado
        if current_time < client_data["blocked_until"]:
            return {
                "allowed": False,
                "requests_remaining": 0,
                "reset_time": client_data["blocked_until"],
                "current_usage": len(client_data["requests"])
            }
        
        # Remover requests antigas (fora da janela)
        window_start = current_time - self.window_size
        while client_data["requests"] and client_data["requests"][0] < window_start:
            client_data["requests"].popleft()
        
        current_usage = len(client_data["requests"])
        
        # Verificar limite
        if current_usage >= limit:
            # Bloquear por 1 hora
            client_data["blocked_until"] = current_time + self.window_size
            
            return {
                "allowed": False,
                "requests_remaining": 0,
                "reset_time": client_data["blocked_until"],
                "current_usage": current_usage
            }
        
        # Adicionar request atual
        client_data["requests"].append(current_time)
        
        return {
            "allowed": True,
            "requests_remaining": limit - current_usage - 1,
            "reset_time": current_time + self.window_size,
            "current_usage": current_usage + 1
        }
    
    def _cleanup_old_requests(self):
        """Remove dados antigos do cache"""
        current_time = time.time()
        cleanup_before = current_time - (self.window_size * 2)  # 2 horas atrás
        
        clients_to_remove = []
        
        for client_id, client_data in rate_limit_cache.items():
            # Remover requests muito antigas
            while client_data["requests"] and client_data["requests"][0] < cleanup_before:
                client_data["requests"].popleft()
            
            # Remover clientes inativos
            if (not client_data["requests"] and 
                current_time > client_data["blocked_until"]):
                clients_to_remove.append(client_id)
        
        for client_id in clients_to_remove:
            del rate_limit_cache[client_id]
        
        logger.info(f"Rate limit cleanup: removidos {len(clients_to_remove)} clientes inativos")


# Instância global do rate limiter
rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware de rate limiting para todas as requisições
    """
    # Ignorar endpoints que não precisam de rate limiting
    exempt_paths = [
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/v8/health",
        "/"
    ]
    
    if request.url.path in exempt_paths:
        return await call_next(request)
    
    # Obter informações do cliente do header Authorization
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        # Se não tem auth, deixar para o middleware de auth tratar
        return await call_next(request)
    
    try:
        # Importar aqui para evitar importação circular
        from .auth import verify_token, verify_api_key, CLIENTS_DB
        
        token = auth_header[7:]  # Remove "Bearer "
        client_id = verify_token(token) or verify_api_key(token)
        
        if not client_id or client_id not in CLIENTS_DB:
            # Cliente inválido, deixar para auth middleware tratar
            return await call_next(request)
        
        client_data = CLIENTS_DB[client_id]
        
        # Verificar rate limit
        rate_limit_result = rate_limiter.check_rate_limit(
            client_id=client_id,
            tier=client_data["tier"],
            limit=client_data["rate_limit"]
        )
        
        # Criar response
        if rate_limit_result["allowed"]:
            response = await call_next(request)
        else:
            # Rate limit excedido
            logger.warning(f"Rate limit excedido para cliente {client_id}")
            
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Limite de {client_data['rate_limit']} requisições por hora excedido",
                    "reset_time": rate_limit_result["reset_time"],
                    "tier": client_data["tier"]
                }
            )
        
        # Adicionar headers informativos
        if rate_limit_result["requests_remaining"] != "unlimited":
            response.headers["X-RateLimit-Limit"] = str(client_data["rate_limit"])
            response.headers["X-RateLimit-Remaining"] = str(rate_limit_result["requests_remaining"])
            response.headers["X-RateLimit-Reset"] = str(int(rate_limit_result["reset_time"]))
        else:
            response.headers["X-RateLimit-Limit"] = "unlimited"
            response.headers["X-RateLimit-Remaining"] = "unlimited"
        
        response.headers["X-RateLimit-Used"] = str(rate_limit_result["current_usage"])
        response.headers["X-Client-Tier"] = client_data["tier"]
        
        return response
        
    except Exception as e:
        logger.error(f"Erro no rate limiting: {e}")
        # Em caso de erro, continuar sem rate limiting
        return await call_next(request)


def get_rate_limit_status(client_id: str) -> Dict[str, Any]:
    """Obter status atual do rate limit para um cliente"""
    from .auth import CLIENTS_DB
    
    if client_id not in CLIENTS_DB:
        return {"error": "Cliente não encontrado"}
    
    client_data = CLIENTS_DB[client_id]
    
    if client_data["rate_limit"] == -1:
        return {
            "tier": client_data["tier"],
            "limit": "unlimited",
            "current_usage": 0,
            "remaining": "unlimited",
            "reset_time": None
        }
    
    rate_limit_result = rate_limiter.check_rate_limit(
        client_id=client_id,
        tier=client_data["tier"],
        limit=client_data["rate_limit"]
    )
    
    return {
        "tier": client_data["tier"],
        "limit": client_data["rate_limit"],
        "current_usage": rate_limit_result["current_usage"],
        "remaining": rate_limit_result["requests_remaining"],
        "reset_time": rate_limit_result["reset_time"]
    }


# Para testes
if __name__ == "__main__":
    # Teste do rate limiter
    limiter = RateLimiter()
    
    print("🚦 TESTE RATE LIMITER - Culture Pulse V8.0")
    print("=" * 50)
    
    # Simular cliente free (100 req/hora)
    client_id = "test_client"
    limit = 100
    
    print(f"\n📊 Testando cliente com limite de {limit} req/hora")
    
    # Simular 105 requests
    for i in range(105):
        result = limiter.check_rate_limit(client_id, "free", limit)
        
        if i % 20 == 0:  # Mostrar status a cada 20 requests
            print(f"Request {i+1}: Permitido={result['allowed']}, Restante={result['requests_remaining']}")
        
        if not result["allowed"]:
            print(f"❌ Rate limit atingido na request {i+1}")
            break
    
    print("\n✅ Teste concluído!")
