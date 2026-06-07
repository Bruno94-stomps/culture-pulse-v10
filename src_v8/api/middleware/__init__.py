#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Middleware Module - Culture Pulse V9.0
Inicialização do módulo de middleware

🎯 MIDDLEWARE V9.0:
- Autenticação Bearer Token
- Rate Limiting inteligente  
- Cache Redis automático
- Logs estruturados
"""

from .auth import get_current_client, get_current_active_client, require_tier
from .rate_limit import rate_limit_middleware, get_rate_limit_status
from .cache import CacheMiddleware, add_cache_middleware, cache_router

__all__ = [
    "get_current_client",
    "get_current_active_client", 
    "require_tier",
    "rate_limit_middleware",
    "get_rate_limit_status",
    "CacheMiddleware",
    "add_cache_middleware", 
    "cache_router"
]
