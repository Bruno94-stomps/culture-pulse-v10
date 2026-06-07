#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plan Configuration — Culture Pulse V9.9 (4 Tiers)
==================================================
Dicionário centralizado com TODAS as configurações diferenciadas por plano.
Importado por: auth.py, streaming.py, supabase_writer.py, dashboard, API.

Tiers:
  free        — Freemium (R$ 0)        → aquisição, demonstração de valor
  pro         — Profissional (R$ 6k)   → entry-point acessível
  executive   — Executivo (R$ 14k)     → sweet-spot de receita
  enterprise  — Enterprise (R$ 25k)    → máximo LTV

V9.9: Inclusão de Biographical Veracity (Reliability) e Data Lag (D+1).
"""

from __future__ import annotations
from typing import Dict, Any

# Conexão com Sistema de Cache V9.9
try:
    from core.cache.redis_config import TIER_POLICIES
except ImportError:
    # Fallback se o redis_config não estiver disponível
    TIER_POLICIES = {
        'free': {'ttl_multiplier': 24, 'label': 'Free'},
        'pro': {'ttl_multiplier': 1, 'label': 'Profissional'},
        'executive': {'ttl_multiplier': 1, 'label': 'Executivo'},
        'enterprise': {'ttl_multiplier': 0.25, 'label': 'Enterprise'}
    }

# ─────────────────────────────────────────────────────────────────────────────
#  Configuração por plano — SINGLE SOURCE OF TRUTH
# ─────────────────────────────────────────────────────────────────────────────
PLAN_CONFIG: Dict[str, Dict[str, Any]] = {
    "free": {
        # Identificação
        "label":             TIER_POLICIES['free']['label'],
        "price_brl":         "R$ 0",
        # Cotas
        "analyses_per_month": 10,
        "max_users":          1,
        "platforms_allowed":  3,       # usuário escolhe 3
        "circles_allowed":    3,       # usuário escolhe 3
        # API
        "rate_limit_per_hour": 50,
        # WebSocket
        "ws_enabled":         False,   # sem WebSocket — polling manual
        "ws_interval_s":      None,    # N/A
        "ws_buffer_replay":   0,
        "redis_channel":      None,    # sem canal Redis
        # Dados (Importado de redis_config)
        "retention_days":     30,
        "data_lag_hours":     TIER_POLICIES['free']['ttl_multiplier'], # Sincronizado com Redis
        "columns_visible":    ["tipo", "circulo", "termo", "score", "ts", "reliability"],
        "raw_data_access":    False,
        "evidence_urls":      False,   # Não vê o link original no Free
        "export_formats":     [],
        # Alertas
        "alerts_email":       None,
        "alerts_teams":       False,
        "alerts_whatsapp":    False,
        # Integração
        "api_integration":    False,
        "supabase_source":    "signals_public",
    },

    "pro": {
        "label":             TIER_POLICIES['pro']['label'],
        "price_brl":         "R$ 6.000/mês",
        "analyses_per_month": 30,
        "max_users":          2,
        "platforms_allowed":  8,       # todas
        "circles_allowed":    16,      # todos
        "rate_limit_per_hour": 500,
        "ws_enabled":         True,
        "ws_interval_s":      30,
        "ws_buffer_replay":   50,
        "redis_channel":      "signals:pro",
        "retention_days":     90,
        "columns_visible":    ["tipo", "circulo", "termo", "score", "regiao", "plataforma", "ts", "reliability", "source_url"],
        "raw_data_access":    False,
        "evidence_urls":      True,
        "export_formats":     ["pdf"],
        "alerts_email":       "monthly",
        "alerts_teams":       False,
        "alerts_whatsapp":    False,
        "api_integration":    False,
        "supabase_source":    "signals_pro",
    },

    "executive": {
        "label":             TIER_POLICIES['executive']['label'],
        "price_brl":         "R$ 14.000/mês",
        "analyses_per_month": 60,
        "max_users":          3,
        "platforms_allowed":  8,
        "circles_allowed":    16,
        "rate_limit_per_hour": 2000,
        "ws_enabled":         True,
        "ws_interval_s":      15,
        "ws_buffer_replay":   150,
        "redis_channel":      "signals:executive",
        "retention_days":     365,
        "columns_visible":    ["tipo", "circulo", "termo", "score", "regiao", "plataforma", "raw_data", "ts", "reliability", "source_url"],
        "raw_data_access":    "partial",
        "evidence_urls":      True,
        "export_formats":     ["pdf", "csv"],
        "alerts_email":       "biweekly",
        "alerts_teams":       True,
        "alerts_whatsapp":    False,
        "api_integration":    "basic",
        "supabase_source":    "signals_executive",
    },

    "enterprise": {
        "label":             TIER_POLICIES['enterprise']['label'],
        "price_brl":         "R$ 25.000/mês",
        "analyses_per_month": 100,
        "max_users":          5,
        "platforms_allowed":  8,
        "circles_allowed":    16,
        "rate_limit_per_hour": 10000,
        "ws_enabled":         True,
        "ws_interval_s":      5,
        "ws_buffer_replay":   500,
        "redis_channel":      "signals:enterprise",
        "retention_days":     730,
        "columns_visible":    ["*"],
        "raw_data_access":    True,
        "evidence_urls":      True,
        "export_formats":     ["pdf", "csv", "json"],
        "alerts_email":       "weekly",
        "alerts_teams":       True,
        "alerts_whatsapp":    True,
        "api_integration":    "advanced",
        "supabase_source":    "cultural_signals",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
#  Hierarquia de planos (para require_tier)
# ─────────────────────────────────────────────────────────────────────────────
TIER_HIERARCHY: Dict[str, int] = {
    "free":       0,
    "pro":        1,
    "executive":  2,
    "enterprise": 3,
}

# Lista ordenada de tiers válidos
VALID_TIERS = list(TIER_HIERARCHY.keys())

# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────

def get_plan(tier: str) -> Dict[str, Any]:
    """Retorna config do plano ou free como fallback."""
    return PLAN_CONFIG.get(tier, PLAN_CONFIG["free"])


def get_ws_interval(tier: str) -> int | None:
    """Retorna intervalo WebSocket em segundos (None = sem WS)."""
    return get_plan(tier).get("ws_interval_s")


def get_retention_days(tier: str) -> int:
    """Retorna dias de retenção de dados."""
    return get_plan(tier).get("retention_days", 30)


def get_rate_limit(tier: str) -> int:
    """Retorna rate limit por hora (-1 = ilimitado)."""
    return get_plan(tier).get("rate_limit_per_hour", 50)


def get_redis_channel(tier: str) -> str | None:
    """Retorna canal Redis (None = sem streaming)."""
    return get_plan(tier).get("redis_channel")


def get_buffer_replay_count(tier: str) -> int:
    """Retorna quantidade de sinais no buffer replay."""
    return get_plan(tier).get("ws_buffer_replay", 0)


def is_tier_valid(tier: str) -> bool:
    """Verifica se é um tier válido."""
    return tier in VALID_TIERS


def tier_meets_requirement(current: str, required: str) -> bool:
    """Verifica se current tier >= required tier."""
    return TIER_HIERARCHY.get(current, -1) >= TIER_HIERARCHY.get(required, 999)
