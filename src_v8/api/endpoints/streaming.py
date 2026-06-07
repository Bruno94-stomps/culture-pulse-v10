#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSocket Streaming Endpoint - Culture Pulse V9.1 (4 Tiers)
Streaming de sinais culturais em tempo real via WebSocket + Redis Pub/Sub

Arquitetura híbrida (S4.1):
  - Coleta → supabase_writer.write_signals() → SignalPublisher → Redis Pub/Sub
  - WebSocket subscriber consome os canais Redis e forward ao cliente
  - Buffer Redis List por plano permite replay na reconexão (S4.2)
  - Sem Redis: modo offline explícito (sem DEMO_SIGNALS simulados)

Planos e canais Redis (V9.1 — 4 tiers):
  - free       → SEM WebSocket (polling manual via dashboard, refresh 60s)
  - pro        → channel: signals:pro         (16 círculos, sem raw_data, 30s)
  - executive  → channel: signals:executive   (16 círculos + raw parcial, 15s)
  - enterprise → channel: signals:enterprise  (tudo + raw completo + exports, 5s)

Config centralizada: config/plan_config.py (PLAN_CONFIG)
"""

import asyncio
import json
import logging
import time
from typing import Dict, Optional, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException
from fastapi.websockets import WebSocketState

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
#  Tentativa de importar Redis assíncrono (aioredis / redis.asyncio)          #
# --------------------------------------------------------------------------- #
try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    try:
        import aioredis  # type: ignore
        REDIS_AVAILABLE = True
    except ImportError:
        REDIS_AVAILABLE = False
        logger.warning("⚠️ Redis não disponível — WebSocket usará fallback de polling local")

# --------------------------------------------------------------------------- #
#  Mapeamento plano → canal Redis  (V9.1 — 4 tiers)                          #
# --------------------------------------------------------------------------- #
PLAN_CHANNELS: Dict[str, str] = {
    "free":       "",                    # sem WebSocket — polling manual
    "pro":        "signals:pro",
    "executive":  "signals:executive",
    "enterprise": "signals:enterprise",
}

# Sinais de demo para fallback local (sem Redis)
# S4.1: DEMO_SIGNALS mantido como opt-in explícito (demo_mode=true no query param)
# Em produção, sem Redis = modo offline sem dados simulados
DEMO_SIGNALS = [
    {"tipo": "tendencia", "circulo": "Música Popular", "termo": "funk carioca", "score": 0.87, "regiao": "RJ", "simulated": True},
    {"tipo": "emergente", "circulo": "Gastronomia", "termo": "açaí premium", "score": 0.74, "regiao": "SP", "simulated": True},
    {"tipo": "alerta",    "circulo": "Moda & Estilo", "termo": "streetwear nordestino", "score": 0.91, "regiao": "NE", "simulated": True},
    {"tipo": "tendencia", "circulo": "Esporte",       "termo": "beach tennis", "score": 0.82, "regiao": "SUL", "simulated": True},
    {"tipo": "emergente", "circulo": "Tecnologia",    "termo": "pix parcelado", "score": 0.69, "regiao": "BR", "simulated": True},
]

# S4.1: Importar SignalPublisher para publish endpoint e buffer replay
try:
    from api.signal_publisher import publish_signal as _publisher_publish
    from api.signal_publisher import get_buffer as _get_buffer
    _PUBLISHER_AVAILABLE = True
except ImportError:
    _PUBLISHER_AVAILABLE = False
    _publisher_publish = None
    _get_buffer = None

# Worker Async: Importar canais enriched e buffer para replay de enrichments
try:
    from core.analysis_worker import (
        ENRICHED_CHANNELS as _ENRICHED_CHANNELS,
        get_enriched_buffer as _get_enriched_buffer,
    )
    _WORKER_AVAILABLE = True
except ImportError:
    _WORKER_AVAILABLE = False
    _ENRICHED_CHANNELS = {}
    _get_enriched_buffer = None


# --------------------------------------------------------------------------- #
#  Gerenciador de conexões WebSocket                                           #
# --------------------------------------------------------------------------- #
class ConnectionManager:
    """Mantém mapa client_id → WebSocket ativo."""

    def __init__(self):
        self.active: Dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active[client_id] = websocket
        logger.info(f"🔌 WS conectado: {client_id} (total: {len(self.active)})")

    def disconnect(self, client_id: str):
        self.active.pop(client_id, None)
        logger.info(f"🔌 WS desconectado: {client_id} (total: {len(self.active)})")

    async def send(self, client_id: str, data: dict):
        ws = self.active.get(client_id)
        if ws and ws.client_state == WebSocketState.CONNECTED:
            try:
                await ws.send_json(data)
            except Exception as e:
                logger.warning(f"Erro ao enviar para {client_id}: {e}")
                self.disconnect(client_id)

    async def broadcast_to_plan(self, plan: str, data: dict):
        """Envia para todos os clientes de um plano (útil para admin)."""
        channel = PLAN_CHANNELS.get(plan, "signals:free")
        for cid, ws in list(self.active.items()):
            if ws.client_state == WebSocketState.CONNECTED:
                await self.send(cid, data)


manager = ConnectionManager()


# --------------------------------------------------------------------------- #
#  Funções de autenticação leve para WebSocket                                #
# --------------------------------------------------------------------------- #
def _resolve_plan(token: Optional[str]) -> str:
    """
    Resolve o plano a partir do token.
    Aceita tanto API keys estáticas quanto JWT emitidos pelo auth.py existente.
    S4.2: JWT agora inclui campo 'tier'; fallback busca CLIENTS_DB via 'sub'.
    V9.1: 4 tiers — free / pro / executive / enterprise.
    Fallback final: free.
    """
    VALID_TIERS = {"free", "pro", "executive", "enterprise"}

    if not token:
        return "free"

    # API keys estáticas (mantém compatibilidade com auth.py atual)
    static_map = {
        "cp_demo_2025_free_tier":         "free",
        "cp_pro_2025_advanced":           "pro",
        "cp_executive_2025_premium":      "executive",
        "cp_enterprise_2025_unlimited":   "enterprise",
    }
    if token in static_map:
        return static_map[token]

    # JWT — decodificar e extrair tier
    try:
        import jwt as _jwt
        SECRET_KEY = os.getenv("JWT_SECRET_KEY", "culture_pulse_integrated_secret_key_2025")
        payload = _jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        # S4.2: campo 'tier' adicionado ao JWT pelo auth.py
        tier = payload.get("tier")
        if tier and tier in VALID_TIERS:
            return tier

        # Fallback: buscar tier via client_id (sub) no CLIENTS_DB
        client_id = payload.get("sub")
        if client_id:
            try:
                from api.middleware.auth import CLIENTS_DB
                client_data = CLIENTS_DB.get(client_id, {})
                tier_from_db = client_data.get("tier")
                if tier_from_db and tier_from_db in VALID_TIERS:
                    return tier_from_db
            except ImportError:
                pass
    except Exception:
        pass

    return "free"


def _filter_signal_by_plan(signal: dict, plan: str) -> Optional[dict]:
    """
    Aplica filtro de features por plano antes de enviar ao cliente. (V9.1 — 4 tiers)

    free       → apenas campos básicos (tipo, circulo, termo, score, ts)
    pro        → + regiao, plataforma (sem raw_data)
    executive  → + raw_data parcial (sem demographics/tensions internas)
    enterprise → tudo incluindo raw_data completo
    """
    if plan == "free":
        return {
            "tipo":     signal.get("tipo"),
            "circulo":  signal.get("circulo"),
            "termo":    signal.get("termo"),
            "score":    signal.get("score"),
            "ts":       signal.get("ts"),
        }
    if plan == "pro":
        return {k: v for k, v in signal.items() if k != "raw_data"}
    if plan == "executive":
        # raw_data parcial — remover dados internos sensíveis
        result = dict(signal)
        raw = result.get("raw_data")
        if raw and isinstance(raw, dict):
            result["raw_data"] = {
                k: v for k, v in raw.items()
                if k not in ("demographic_data", "tension_indicators", "emerging_profile_signals")
            }
        return result
    # enterprise: tudo
    return signal


# --------------------------------------------------------------------------- #
#  Subscriber Redis assíncrono                                                #
# --------------------------------------------------------------------------- #
async def _redis_subscriber(client_id: str, channel: str, plan: str, redis_url: str):
    """
    Assina o canal Redis e encaminha mensagens para o WebSocket do cliente.
    Reconecta automaticamente em caso de falha.
    """
    retry_delay = 1.0
    while client_id in manager.active:
        try:
            r = await aioredis.from_url(redis_url, decode_responses=True)
            pubsub = r.pubsub()
            await pubsub.subscribe(channel)
            logger.info(f"📡 {client_id} subscribed → {channel}")
            retry_delay = 1.0  # reset on success

            async for message in pubsub.listen():
                if client_id not in manager.active:
                    break
                if message["type"] == "message":
                    try:
                        raw = json.loads(message["data"])
                        filtered = _filter_signal_by_plan(raw, plan)
                        if filtered:
                            await manager.send(client_id, {
                                "event": "signal",
                                "plan":  plan,
                                "data":  filtered,
                            })
                    except Exception as e:
                        logger.warning(f"Erro ao processar mensagem Redis: {e}")
            await pubsub.unsubscribe(channel)
            await r.aclose()

        except Exception as e:
            logger.warning(f"Redis subscriber erro ({client_id}): {e} — retry em {retry_delay}s")
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 30)


# --------------------------------------------------------------------------- #
#  Subscriber Redis: sinais ENRIQUECIDOS pelo AnalysisWorker                 #
# --------------------------------------------------------------------------- #
async def _enriched_subscriber(client_id: str, plan: str, redis_url: str):
    """
    Assina signals:enriched:{plan} e encaminha enrichments ao WebSocket.
    Evento: {"event": "enrichment", "plan": plan, "data": {...}}
    O cliente WS recebe dois eventos por sinal:
      1. "signal"     — instantâneo (<30ms), sinal cru
      2. "enrichment" — enriquecido (2-5s depois), com scores de engines
    """
    if not _WORKER_AVAILABLE or not _ENRICHED_CHANNELS:
        return  # Worker não disponível — sem enrichments

    enriched_channel = _ENRICHED_CHANNELS.get(plan, _ENRICHED_CHANNELS.get("free", ""))
    if not enriched_channel:
        return

    retry_delay = 1.0
    while client_id in manager.active:
        try:
            r = await aioredis.from_url(redis_url, decode_responses=True)
            pubsub = r.pubsub()
            await pubsub.subscribe(enriched_channel)
            logger.info(f"🔬 {client_id} subscribed → {enriched_channel}")
            retry_delay = 1.0

            async for message in pubsub.listen():
                if client_id not in manager.active:
                    break
                if message["type"] == "message":
                    try:
                        enriched = json.loads(message["data"])
                        filtered = _filter_signal_by_plan(enriched, plan)
                        if filtered:
                            # Remover metadados internos do worker antes de enviar
                            filtered.pop("_enrichment", None)
                            await manager.send(client_id, {
                                "event": "enrichment",
                                "plan":  plan,
                                "data":  filtered,
                            })
                    except Exception as e:
                        logger.warning(f"Erro ao processar enrichment: {e}")
            await pubsub.unsubscribe(enriched_channel)
            await r.aclose()

        except Exception as e:
            logger.warning(f"Enriched subscriber erro ({client_id}): {e} — retry em {retry_delay}s")
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 30)


# --------------------------------------------------------------------------- #
#  Fallback: modo offline (sem Redis) — S4.1 refatorado                      #
# --------------------------------------------------------------------------- #
async def _local_fallback(client_id: str, plan: str, demo_mode: bool = False):
    """
    Quando Redis não está disponível:
    - demo_mode=True: envia DEMO_SIGNALS a cada 30s (para demonstrações)
    - demo_mode=False: envia apenas status offline, sem dados simulados

    S4.1: DEMO_SIGNALS não são mais enviados por padrão.
    Cliente precisa passar ?demo_mode=true explicitamente.
    """
    if not demo_mode:
        # Modo offline real — informar e aguardar
        await manager.send(client_id, {
            "event": "info",
            "message": (
                "⚠️ Redis não disponível — streaming offline. "
                "Sinais reais não estão disponíveis em tempo real. "
                "Use a API REST para consultar dados. "
                "Adicione ?demo_mode=true para ver dados simulados."
            ),
            "offline": True,
        })
        # Keep-alive somente — sem dados falsos
        while client_id in manager.active:
            await manager.send(client_id, {"event": "ping", "ts": time.time(), "offline": True})
            await asyncio.sleep(30)
        return

    # demo_mode=True — DEMO_SIGNALS explícito
    intervals = {"free": 60, "pro": 30, "executive": 15, "enterprise": 5}
    interval = intervals.get(plan, 60)
    idx = 0

    await manager.send(client_id, {
        "event": "info",
        "message": "🎭 Modo DEMO ativo — dados simulados para demonstração.",
        "demo_mode": True,
    })

    while client_id in manager.active:
        signal = {**DEMO_SIGNALS[idx % len(DEMO_SIGNALS)], "ts": time.time()}
        filtered = _filter_signal_by_plan(signal, plan)
        if filtered:
            await manager.send(client_id, {"event": "signal", "plan": plan, "data": filtered})
        idx += 1
        await asyncio.sleep(interval)


# --------------------------------------------------------------------------- #
#  Router                                                                     #
# --------------------------------------------------------------------------- #
streaming_router = APIRouter(tags=["Streaming"])


@streaming_router.websocket("/ws/signals/{client_id}")
async def websocket_signals(
    websocket: WebSocket,
    client_id: str,
    token: Optional[str] = Query(default=None, description="API key ou JWT Bearer token"),
    redis_url: str = Query(default="redis://localhost:6379/0"),
    demo_mode: bool = Query(default=False, description="S4.1: opt-in para dados demo (sem Redis)"),
):
    """
    **WebSocket — Streaming de sinais culturais em tempo real**

    Conectar:
    ```
    ws://localhost:8000/ws/signals/{client_id}?token=cp_pro_2025_advanced
    ```

    S4.1 — Sinais crus em tempo real:
    - Sinais reais chegam via Redis Pub/Sub (publicados pelo SignalPublisher)
    - Buffer replay na reconexão (últimos N sinais do plano)
    - Sem Redis: modo offline (sem dados simulados)
    - Para demo: adicionar &demo_mode=true

    Worker Async — Sinais enriquecidos:
    - AnalysisWorker escuta signals:raw → executa engines → publica enriched
    - Cliente recebe evento "enrichment" com dados enriquecidos (2-5s depois)
    - Replay de enrichments na reconexão

    Eventos recebidos:
    - `{"event": "connected", "plan": "pro", ...}` — confirmação inicial
    - `{"event": "replay", "data": [...]}` — buffer replay sinais crus
    - `{"event": "replay_enriched", "data": [...]}` — buffer replay enriquecidos
    - `{"event": "signal", "plan": "pro", "data": {...}}` — novo sinal cultural
    - `{"event": "enrichment", "plan": "pro", "data": {...}}` — sinal enriquecido
    - `{"event": "ping"}` — keep-alive a cada 30s
    - `{"event": "info", "message": "..."}` — avisos do sistema
    """
    plan = _resolve_plan(token)
    channel = PLAN_CHANNELS.get(plan, "")

    # V9.1: Free não tem WebSocket — rejeitar com mensagem amigável
    if plan == "free":
        await websocket.accept()
        await websocket.send_json({
            "event": "upgrade_required",
            "plan":  "free",
            "message": (
                "⚠️ O plano Free não inclui streaming em tempo real. "
                "Use o dashboard para consultar sinais (refresh a cada 60s). "
                "Faça upgrade para Profissional (R$ 6.000/mês) para streaming WebSocket."
            ),
            "upgrade_url": "/dashboard/upgrade?required=pro",
        })
        await websocket.close(code=4003, reason="Upgrade required for WebSocket streaming")
        return

    await manager.connect(client_id, websocket)

    # Confirmação de conexão (V9.1 — 4 tiers)
    ws_intervals = {"pro": 30, "executive": 15, "enterprise": 5}
    circles_map = {"pro": 16, "executive": 16, "enterprise": 16}
    await manager.send(client_id, {
        "event":   "connected",
        "plan":    plan,
        "channel": channel,
        "client":  client_id,
        "redis":   REDIS_AVAILABLE,
        "demo_mode": demo_mode,
        "features": {
            "circles":    circles_map.get(plan, 3),
            "raw_data":   plan in ("executive", "enterprise"),
            "raw_data_full": plan == "enterprise",
            "exports":    plan in ("executive", "enterprise"),
            "export_formats": {"executive": ["pdf", "csv"], "enterprise": ["pdf", "csv", "json"]}.get(plan, []),
            "interval_s": ws_intervals.get(plan, 30),
            "api_integration": {"executive": "basic", "enterprise": "advanced"}.get(plan, False),
        },
        "ts": time.time(),
    })

    # S4.1: Buffer replay na reconexão (se Redis disponível)
    if REDIS_AVAILABLE and _PUBLISHER_AVAILABLE and _get_buffer:
        try:
            replay_count = {"pro": 50, "executive": 150, "enterprise": 500}.get(plan, 50)
            buffered = await _get_buffer(plan=plan, count=replay_count)
            if buffered:
                replay_signals = []
                for raw in buffered:
                    filtered = _filter_signal_by_plan(raw, plan)
                    if filtered:
                        replay_signals.append(filtered)
                if replay_signals:
                    await manager.send(client_id, {
                        "event": "replay",
                        "plan":  plan,
                        "count": len(replay_signals),
                        "data":  replay_signals,
                    })
                    logger.info(f"📦 Replay: {len(replay_signals)} sinais → {client_id}")
        except Exception as e:
            logger.warning(f"⚠️ Buffer replay falhou: {e}")

    # Worker Async: Replay de enrichments na reconexão
    if REDIS_AVAILABLE and _WORKER_AVAILABLE and _get_enriched_buffer:
        try:
            enriched_count = {"pro": 30, "executive": 80, "enterprise": 200}.get(plan, 30)
            enriched_buf = await _get_enriched_buffer(plan=plan, count=enriched_count)
            if enriched_buf:
                enriched_replay = []
                for raw in enriched_buf:
                    filtered = _filter_signal_by_plan(raw, plan)
                    if filtered:
                        filtered.pop("_enrichment", None)
                        enriched_replay.append(filtered)
                if enriched_replay:
                    await manager.send(client_id, {
                        "event": "replay_enriched",
                        "plan":  plan,
                        "count": len(enriched_replay),
                        "data":  enriched_replay,
                    })
                    logger.info(f"🔬 Replay enriched: {len(enriched_replay)} → {client_id}")
        except Exception as e:
            logger.warning(f"⚠️ Enriched replay falhou: {e}")

    # Iniciar subscribers em background
    redis_url_env = __import__("os").getenv("REDIS_URL", redis_url)
    tasks = []

    if REDIS_AVAILABLE:
        # Task 1: sinais crus
        tasks.append(asyncio.create_task(
            _redis_subscriber(client_id, channel, plan, redis_url_env)
        ))
        # Task 2: sinais enriquecidos (Worker Async)
        if _WORKER_AVAILABLE:
            tasks.append(asyncio.create_task(
                _enriched_subscriber(client_id, plan, redis_url_env)
            ))
    else:
        tasks.append(asyncio.create_task(
            _local_fallback(client_id, plan, demo_mode=demo_mode)
        ))

    # Keep-alive + detectar desconexão do cliente
    try:
        while True:
            try:
                # Aguarda mensagem do cliente (ping/pong ou close)
                msg = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                if msg == "ping":
                    await manager.send(client_id, {"event": "pong", "ts": time.time()})
            except asyncio.TimeoutError:
                # Envia ping próprio a cada 30s para manter conexão viva
                await manager.send(client_id, {"event": "ping", "ts": time.time()})
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.warning(f"WS loop erro ({client_id}): {e}")
    finally:
        for task in tasks:
            task.cancel()
        manager.disconnect(client_id)


# --------------------------------------------------------------------------- #
#  Endpoint auxiliar: publicar sinal manualmente (uso interno / testes)       #
# --------------------------------------------------------------------------- #
@streaming_router.post("/api/v9/streaming/publish")
async def publish_signal_endpoint(
    signal: dict,
    plan: str = "pro",
    redis_url: str = "redis://localhost:6379/0",
):
    """
    Publica um sinal no Redis via SignalPublisher centralizado (S4.1).

    O SignalPublisher distribui automaticamente para os 3 canais (free/pro/enterprise)
    e mantém o buffer List para replay.

    Exemplo de payload:
    ```json
    {
      "tipo": "emergente",
      "circulo": "Gastronomia",
      "termo": "ceviche brasileiro",
      "score": 0.88,
      "regiao": "SP",
      "raw_data": {"fonte": "youtube", "views": 120000}
    }
    ```
    """
    # S4.1: Usar SignalPublisher centralizado
    if _PUBLISHER_AVAILABLE and _publisher_publish:
        try:
            signal["ts"] = time.time()
            recipients = await _publisher_publish(signal)
            return {
                "status":     "ok",
                "publisher":  "signal_publisher",
                "recipients": recipients,
                "channels":   list(PLAN_CHANNELS.values()),
            }
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Publisher error: {e}")

    # Fallback direto ao Redis (compatibilidade)
    if not REDIS_AVAILABLE:
        return {"status": "warning", "message": "Redis não disponível — sinal não publicado"}

    channel = PLAN_CHANNELS.get(plan, "signals:free")
    signal["ts"] = time.time()

    try:
        r = await aioredis.from_url(
            __import__("os").getenv("REDIS_URL", redis_url),
            decode_responses=True
        )
        recipients = await r.publish(channel, json.dumps(signal))
        await r.aclose()
        return {"status": "ok", "channel": channel, "recipients": recipients, "publisher": "direct"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Erro Redis: {e}")


# --------------------------------------------------------------------------- #
#  Drift Detection Endpoint (S2.4)                                            #
# --------------------------------------------------------------------------- #

_drift_detector = None  # Lazy singleton


def _get_drift_detector():
    """Lazy init drift detector from Supabase reference signals."""
    global _drift_detector
    if _drift_detector is None:
        try:
            from core.classifiers.drift_detector import create_detector_from_supabase
            _drift_detector, n_ref = create_detector_from_supabase(p_val=0.05)
            logger.info(f"✅ Drift detector initialized with {n_ref} reference signals")
        except Exception as e:
            logger.warning(f"⚠️ Drift detector unavailable: {e}")
            return None
    return _drift_detector


@streaming_router.get("/api/v9/drift/status")
async def drift_status():
    """
    Get current drift detector status and last check result.

    Returns badge info for dashboard + detector summary.
    """
    detector = _get_drift_detector()
    if detector is None:
        return {
            "status": "unavailable",
            "message": "Drift detector not initialized",
            "badge": {"emoji": "❓", "color": "gray", "message": "Drift detector indisponível"},
        }

    return {
        "status": "ok",
        "badge": detector.get_dashboard_badge(),
        "summary": detector.get_summary(),
    }


@streaming_router.post("/api/v9/drift/check")
async def drift_check(signals: list):
    """
    Check a batch of signals for cultural drift.

    Send a list of signal objects (with raw_data containing s22_features + s23_scaled).
    Returns drift detection result.
    """
    detector = _get_drift_detector()
    if detector is None:
        raise HTTPException(
            status_code=503,
            detail="Drift detector not available. Ensure Supabase has reference signals."
        )

    try:
        alert = detector.check(signals=signals)
        result = alert.to_dict()

        # Log to Supabase if drift detected
        if alert.is_drift:
            try:
                from core.classifiers.drift_detector import log_drift_event
                log_drift_event(alert)
            except Exception as e:
                logger.warning(f"Failed to log drift event: {e}")

        return {"status": "ok", "drift": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drift check failed: {e}")

