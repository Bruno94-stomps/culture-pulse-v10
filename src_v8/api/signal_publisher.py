#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Signal Publisher — Culture Pulse V9.1  (Sprint S4.1)
=====================================================
Publica CulturalSignal nos canais Redis em tempo real, fazendo a ponte entre:
  - Coleta (collectors/data_collectors.py, collection.py)
  - Persistência (supabase_writer.py)
  - Streaming WebSocket (api/endpoints/streaming.py)

Arquitetura:
  1. Após coleta + write no Supabase, chamar `publish_signals(signals)`
  2. Publisher converte cada sinal para dict serializado
  - Publica em TODOS os 4 canais Redis (free/pro/executive/enterprise)
     com filtragem de campos feita pelo WebSocket subscriber (já existente)
  4. Além de Pub/Sub, faz LPUSH no buffer Redis List por plano
     (para replay quando cliente reconecta — implementação S4.2)

Canal Redis:
  signals:free       — todos os sinais (filtro de campos no WS subscriber)
  signals:pro        — todos os sinais
  signals:executive  — sinais + raw_data parcial
  signals:enterprise — todos os sinais + raw_data completo

Buffer Lists (S4.2 — preparação):
  buffer:signals:free       — LPUSH + LTRIM 100
  buffer:signals:pro        — LPUSH + LTRIM 1000
  buffer:signals:executive  — LPUSH + LTRIM 2000
  buffer:signals:enterprise — LPUSH + LTRIM 10000

Env vars:
  REDIS_URL  = redis://localhost:6379/0  (default)
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from typing import TYPE_CHECKING, Dict, List, Optional

logger = logging.getLogger(__name__)

# ── Redis import ─────────────────────────────────────────────────────────────
try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    try:
        import aioredis  # type: ignore
        REDIS_AVAILABLE = True
    except ImportError:
        REDIS_AVAILABLE = False
        logger.warning("⚠️  Redis não disponível — publisher inativo")

if TYPE_CHECKING:
    from collectors.data_collectors import CulturalSignal

# ── Constantes ────────────────────────────────────────────────────────────────

# Canal para sinais crus — consumido pelo AnalysisWorker (DT-1 / Worker Async)
RAW_CHANNEL = "signals:raw"

PLAN_CHANNELS: Dict[str, str] = {
    "free":       "signals:free",
    "pro":        "signals:pro",
    "executive":  "signals:executive",
    "enterprise": "signals:enterprise",
}

PLAN_BUFFERS: Dict[str, str] = {
    "free":       "buffer:signals:free",
    "pro":        "buffer:signals:pro",
    "executive":  "buffer:signals:executive",
    "enterprise": "buffer:signals:enterprise",
}

PLAN_BUFFER_MAX: Dict[str, int] = {
    "free":       100,
    "pro":        1000,
    "executive":  2000,
    "enterprise": 10000,
}

PLAN_BUFFER_TTL: Dict[str, int] = {
    "free":       3600,        # 1 hora
    "pro":        86400,       # 24 horas
    "executive":  86400,       # 24 horas
    "enterprise": 0,           # sem TTL (ilimitado)
}


# ── Singleton Redis connection ────────────────────────────────────────────────

_redis_conn: Optional[object] = None


async def _get_redis() -> Optional[object]:
    """Retorna (ou cria) conexão Redis async singleton."""
    global _redis_conn
    if not REDIS_AVAILABLE:
        return None

    if _redis_conn is not None:
        try:
            await _redis_conn.ping()  # type: ignore
            return _redis_conn
        except Exception:
            _redis_conn = None

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    try:
        _redis_conn = await aioredis.from_url(redis_url, decode_responses=True)
        await _redis_conn.ping()  # type: ignore
        logger.info(f"✅ SignalPublisher conectado ao Redis: {redis_url}")
        return _redis_conn
    except Exception as exc:
        logger.warning(f"⚠️  Redis indisponível ({redis_url}): {exc}")
        _redis_conn = None
        return None


# ── Conversão de sinal ─────────────────────────────────────────────────────

def _signal_to_publish_dict(signal) -> dict:
    """
    Converte CulturalSignal (ou dict) para o formato de publicação.
    Inclui todos os campos para que a filtragem por plano aconteça no WS subscriber.
    """
    if isinstance(signal, dict):
        d = {**signal}
        d.setdefault("ts", time.time())
        return d

    # CulturalSignal dataclass
    dados_extras: dict = signal.dados_extras or {}
    regional: dict = signal.regional_data or {}

    raw_momentum = float(signal.momentum or 0)
    score = round(min(1.0, max(0.0, raw_momentum / 100.0)), 3)

    return {
        "tipo":       signal.relevancia_cultural or "desconhecido",
        "circulo":    dados_extras.get("circulo", dados_extras.get("circle", "geral")),
        "termo":      signal.termo,
        "score":      score,
        "regiao":     regional.get("regiao_principal", regional.get("target_location")),
        "plataforma": signal.plataforma,
        "ts":         time.time(),
        "entropy": {
            "score":          round(float(dados_extras.get("entropy_score", 0.0)), 2),
            "is_gold":         bool(dados_extras.get("is_non_obvious", False)),
            "user_intent":    dados_extras.get("user_intent_context", "Análise Geral"),
        },
        "raw_data": {
            "momentum":      raw_momentum,
            "volume":        signal.volume,
            "sentiment":     signal.sentiment,
            "dados_extras":  dados_extras,
            "regional_data": regional,
            "velocity":             getattr(signal, "velocity", None),
            "interaction_type":     getattr(signal, "interaction_type", None),
            "sequence_position":    getattr(signal, "sequence_position", None),
            "temporal_delta_hours": getattr(signal, "temporal_delta_hours", None),
            "momentum_velocity":    getattr(signal, "momentum_velocity", None),
        },
    }


# ── Publish API ───────────────────────────────────────────────────────────────

async def publish_signal(signal, redis_conn=None) -> int:
    """
    Publica UM sinal nos 3 canais Redis + buffer List + signals:raw (worker).

    Returns:
        Total de subscribers que receberam a mensagem (soma dos canais).
        0 se Redis indisponível.
    """
    r = redis_conn or await _get_redis()
    if r is None:
        return 0

    payload = _signal_to_publish_dict(signal)
    payload_json = json.dumps(payload, ensure_ascii=False, default=str)

    total_recipients = 0

    try:
        # Pub/Sub — publica em todos os 3 canais de plano
        for plan, channel in PLAN_CHANNELS.items():
            recipients = await r.publish(channel, payload_json)  # type: ignore
            total_recipients += recipients

        # Pub/Sub — canal raw para AnalysisWorker (DT-1 Worker Async)
        raw_recipients = await r.publish(RAW_CHANNEL, payload_json)  # type: ignore
        total_recipients += raw_recipients

        # Buffer List — LPUSH + LTRIM para cada plano
        for plan, buffer_key in PLAN_BUFFERS.items():
            await r.lpush(buffer_key, payload_json)  # type: ignore
            await r.ltrim(buffer_key, 0, PLAN_BUFFER_MAX[plan] - 1)  # type: ignore
            ttl = PLAN_BUFFER_TTL[plan]
            if ttl > 0:
                await r.expire(buffer_key, ttl)  # type: ignore

        return total_recipients
    except Exception as exc:
        logger.warning(f"⚠️  Erro ao publicar sinal no Redis: {exc}")
        return 0


async def publish_signals(signals: list) -> dict:
    """
    Publica uma lista de sinais. Retorna resumo.

    Returns:
        {"published": N, "total_recipients": N, "failed": N}
    """
    r = await _get_redis()
    if r is None:
        return {"published": 0, "total_recipients": 0, "failed": len(signals), "redis": False}

    published = 0
    total_recipients = 0
    failed = 0

    for signal in signals:
        if signal is None:
            continue
        try:
            recipients = await publish_signal(signal, redis_conn=r)
            total_recipients += recipients
            published += 1
        except Exception as exc:
            logger.warning(f"⚠️  Falha ao publicar sinal: {exc}")
            failed += 1

    logger.info(
        f"📡 SignalPublisher: {published} sinais publicados, "
        f"{total_recipients} recipients, {failed} falhas"
    )
    return {
        "published":        published,
        "total_recipients": total_recipients,
        "failed":           failed,
        "redis":            True,
    }


# ── Buffer replay (para S4.2 — reconexão WebSocket) ──────────────────────────

async def get_buffer(plan: str = "free", count: int = 50) -> List[dict]:
    """
    Lê os últimos N sinais do buffer do plano.
    Usado quando um cliente WebSocket reconecta para replay imediato.
    """
    r = await _get_redis()
    if r is None:
        return []

    buffer_key = PLAN_BUFFERS.get(plan, PLAN_BUFFERS["free"])
    max_allowed = PLAN_BUFFER_MAX.get(plan, 100)
    count = min(count, max_allowed)

    try:
        items = await r.lrange(buffer_key, 0, count - 1)  # type: ignore
        return [json.loads(item) for item in items]
    except Exception as exc:
        logger.warning(f"⚠️  Erro ao ler buffer Redis: {exc}")
        return []


# ── Sync wrapper (para uso em contexto síncrono) ─────────────────────────────

def publish_signals_sync(signals: list) -> dict:
    """
    Wrapper síncrono de publish_signals.
    Cria event loop se necessário (útil para chamada em supabase_writer.py).
    """
    try:
        loop = asyncio.get_running_loop()
        # Já dentro de um loop async — agendar como task
        future = asyncio.ensure_future(publish_signals(signals))
        return {"scheduled": True, "note": "publish enqueued in running loop"}
    except RuntimeError:
        # Nenhum loop ativo — podemos usar asyncio.run
        return asyncio.run(publish_signals(signals))


# ── Health check ─────────────────────────────────────────────────────────────

async def health_check() -> dict:
    """Verifica conectividade Redis para publicação."""
    r = await _get_redis()
    if r is None:
        return {"status": "unavailable", "redis": False}

    try:
        info = await r.info("server")  # type: ignore
        return {
            "status":        "ok",
            "redis":         True,
            "redis_version": info.get("redis_version", "?"),
            "channels":      list(PLAN_CHANNELS.values()),
            "buffers":       list(PLAN_BUFFERS.values()),
        }
    except Exception as exc:
        return {"status": "error", "redis": True, "error": str(exc)}
