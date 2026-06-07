"""
Enriched Data Reader — H-234
==============================
Bridge between the AnalysisWorker enriched buffer (Redis) and the
dashboard / API consumers.

The dashboard should use ``EnrichedDataReader.get_signals()`` instead of
calling collectors directly. This returns data that has already passed
through the 7-engine pipeline (circles, unknown_detector, sentiment,
nature, authenticity, velocity, graph).

Fallback strategy:
  1. Try Redis enriched buffer
  2. If Redis unavailable, run pipeline in-process (sync shim)
  3. If pipeline unavailable, return raw collector data as-is

Usage in Streamlit:
    from core.intelligence.enriched_reader import EnrichedDataReader

    reader = EnrichedDataReader()
    signals = reader.get_signals(plan="free", count=20)
    # signals is List[dict] with enrichment metadata
"""
from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ── Redis availability ───────────────────────────────────────────────────────
try:
    import redis as _sync_redis
    SYNC_REDIS_AVAILABLE = True
except ImportError:
    SYNC_REDIS_AVAILABLE = False

try:
    import redis.asyncio as aioredis
    ASYNC_REDIS_AVAILABLE = True
except ImportError:
    ASYNC_REDIS_AVAILABLE = False

# ── Buffer keys (mirror analysis_worker.py) ──────────────────────────────────
ENRICHED_BUFFERS = {
    "free":       "buffer:enriched:free",
    "pro":        "buffer:enriched:pro",
    "executive":  "buffer:enriched:executive",
    "enterprise": "buffer:enriched:enterprise",
}

ENRICHED_BUFFER_MAX = {
    "free":       50,
    "pro":        500,
    "executive":  2000,
    "enterprise": 5000,
}


class EnrichedDataReader:
    """
    Reads signals with V9.7 Real-time Priority logic.
    Eliminates legacy Streamlit/Mock fallbacks.
    """

    def __init__(self, redis_url: Optional[str] = None):
        self._redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._sync_client = None
        self._cache_ttl = 300  # 5 minutos para cache de API por Tier

    # ── Sync Redis client ────────────────────────────────────────────────

    def _get_sync_redis(self):
        """Get or create sync Redis client."""
        if self._sync_client is not None:
            try:
                self._sync_client.ping()
                return self._sync_client
            except Exception:
                self._sync_client = None

        if not SYNC_REDIS_AVAILABLE:
            return None

        try:
            self._sync_client = _sync_redis.from_url(
                self._redis_url,
                decode_responses=True,
                socket_connect_timeout=3,
                socket_timeout=3,
            )
            self._sync_client.ping()
            return self._sync_client
        except Exception:
            return None

    def _flatten_collected_signals(self, raw_result: Any, context: Optional[Dict[str, Any]] = None) -> List[dict]:
        """Flatten raw collector results into a list of signal dicts."""
        signals: List[dict] = []

        def enrich_signal(signal_dict: dict) -> dict:
            if not context:
                return signal_dict
            enriched = signal_dict.copy()
            enriched["onboarding_context"] = context.get("onboarding")
            enriched["project_id"] = context.get("project_id")
            enriched["user_tier"] = context.get("user_tier")
            enriched["requested_keywords"] = context.get("keywords")
            return enriched

        if isinstance(raw_result, dict):
            for item in raw_result.values():
                if isinstance(item, list):
                    for signal in item:
                        signal_dict = signal.to_dict() if hasattr(signal, 'to_dict') else signal
                        signals.append(enrich_signal(signal_dict))
                elif hasattr(item, 'to_dict'):
                    signals.append(enrich_signal(item.to_dict()))
                elif isinstance(item, dict):
                    signals.append(enrich_signal(item))
                elif item is not None:
                    signals.append(enrich_signal({'value': item}))
        elif isinstance(raw_result, list):
            for item in raw_result:
                if hasattr(item, 'to_dict'):
                    signals.append(enrich_signal(item.to_dict()))
                elif isinstance(item, dict):
                    signals.append(enrich_signal(item))
                else:
                    signals.append(enrich_signal({'value': item}))
        elif hasattr(raw_result, 'to_dict'):
            signals.append(enrich_signal(raw_result.to_dict()))
        elif raw_result is not None:
            signals.append(enrich_signal({'value': raw_result}))

        return signals

    # ── Public API V9.7 (Real-time First) ────────────────────────────────

    def get_signals(
        self,
        plan: str = "free",
        count: int = 20,
        context: Optional[Dict[str, Any]] = None,
        force_refresh: bool = False,
        use_realtime_api: bool = True,
    ) -> List[dict]:
        """
        Main entry point for Dashboard V9.7: Real-time API priority.
        
        S4.1-REALTIME logic:
          1. If use_realtime_api: Call Orchestrator directly with onboarding/project context
          2. Tier Isolation: Cache result in Redis per plan
          3. Smart Fallback: Supabase historical signals when real-time unavailable
        """
        plan = plan.lower()
        if plan not in ENRICHED_BUFFERS:
            plan = "free"

        user_id = None
        if context:
            user_id = context.get("user_id")

        termo = "cultura"
        if context:
            keywords = context.get("keywords") or (context.get("onboarding") or {}).get("keywords")
            if keywords:
                if isinstance(keywords, list) and keywords:
                    termo = keywords[0]
                elif isinstance(keywords, str) and keywords.strip():
                    termo = keywords.strip()

        # ── 1. REAL-TIME API (Prioridade V9.7) ─────────────────────────
        if use_realtime_api:
            try:
                # Import dinâmico para evitar loop circular
                from collectors.orchestrator import OrchestratorV9
                import asyncio
                
                orch = OrchestratorV9()
                
                # Execução Síncrona para compatibilidade com o Reader
                # Se estiver em loop uvicorn, utiliza nest_asyncio
                def run_sync(coro):
                    try:
                        import nest_asyncio
                        nest_asyncio.apply()
                    except ImportError:
                        pass
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            return loop.run_until_complete(coro)
                        else:
                            return asyncio.run(coro)
                    except Exception:
                        return asyncio.run(coro)

                # Busca real nas APIs usando onboarding/project context
                raw_result = run_sync(
                    orch.collect_with_monitoring(
                        topics=[termo],
                        context={
                            "user_tier": plan,
                            "user_id": user_id,
                            "project_id": context.get("project_id") if context else None,
                            "onboarding": context.get("onboarding") if context else None,
                            "keywords": context.get("keywords") if context else None,
                        }
                    )
                )
                signals = self._flatten_collected_signals(raw_result, context=context)

                if not signals and hasattr(orch.orchestrator_classic, "collect_comprehensive_data_v9"):
                    raw_result = run_sync(orch.orchestrator_classic.collect_comprehensive_data_v9())
                    signals = self._flatten_collected_signals(raw_result, context=context)

                if signals:
                    # ── 2. REDIS TIER STORAGE (Cache de Performance) ──────────
                    self._write_to_redis_buffer(plan, signals[:count])
                    return signals[:count]
            except Exception as e:
                logger.warning(f"⚠️ Real-time API failed, falling back to Supabase: {e}")

        # ── 3. FALLBACK: SUPABASE (Individualized Context) ─────────────
        return self._get_signals_from_supabase(count, context=context)

    def _write_to_redis_buffer(self, plan: str, signals: List[dict]):
        """Isolamento de Cache por Tier via Redis."""
        r = self._get_sync_redis()
        if r is None: return

        try:
            buffer_key = ENRICHED_BUFFERS.get(plan, "buffer:enriched:free")
            max_cap = ENRICHED_BUFFER_MAX.get(plan, 50)
            
            # Atomic update
            pipe = r.pipeline()
            pipe.delete(buffer_key)
            for sig in signals[:max_cap]:
                pipe.rpush(buffer_key, json.dumps(sig))
            pipe.execute()
        except Exception as e:
            logger.debug(f"Redis write error: {e}")

    def _get_signals_from_supabase(self, count: int, context: Optional[Dict[str, Any]] = None) -> List[dict]:
        """
        Busca o que foi salvo no Supabase hoje.
        Prioriza os sinais gerados por este usuário ou contexto de projeto.
        """
        try:
            from collectors import supabase_writer
            from datetime import datetime
            client = supabase_writer._get_client()
            if not client:
                return []

            user_id = context.get("user_id") if context else None
            project_id = context.get("project_id") if context else None
            onboarding = context.get("onboarding") if context else None
            keywords = context.get("keywords") if context else None
            today = datetime.now().strftime('%Y-%m-%d')

            # 1. TENTA BUSCAR DADOS DO USUÁRIO ESPECÍFICO (HOJE)
            if user_id:
                user_res = client.table("cultural_signals")\
                    .select("*")\
                    .filter("ts", "gte", today)\
                    .filter("user_id", "eq", user_id)\
                    .order("ts", desc=True)\
                    .limit(count)\
                    .execute()
                
                if user_res.data:
                    logger.info(f"Fallback: Loaded {len(user_res.data)} user-specific signals.")
                    return [self._attach_context(s, context) for s in user_res.data]

            # 2. SE HOUVER CONTEXTO DE PROJETO/ONBOARDING, BUSCA SINAIS RELACIONADOS
            if project_id or onboarding or keywords:
                query = client.table("cultural_signals").select("*")
                if project_id:
                    query = query.filter("project_id", "eq", project_id)
                elif keywords:
                    first_keyword = keywords[0] if isinstance(keywords, list) and keywords else keywords
                    if isinstance(first_keyword, str) and first_keyword.strip():
                        query = query.filter("termo", "ilike", f"%{first_keyword}%")
                elif onboarding and isinstance(onboarding, dict):
                    brand = onboarding.get("brand") or onboarding.get("segment")
                    if brand:
                        query = query.filter("circulo", "ilike", f"%{brand}%")

                query = query.order("ts", desc=True).limit(count)
                result = query.execute()
                if result.data:
                    logger.info(f"Fallback: Loaded {len(result.data)} project-specific historical signals.")
                    return [self._attach_context(s, context) for s in result.data]

            # 3. BUSCA GERAL DO DIA PARA TENDÊNCIAS
            result = client.table("cultural_signals")\
                .select("*")\
                .filter("ts", "gte", today)\
                .order("ts", desc=True)\
                .limit(count)\
                .execute()
            
            if result.data:
                return [self._attach_context(s, context) for s in result.data]

            # 4. HISTÓRICO MAIS AMPLIO
            logger.warning("Fallback Supabase: sem sinais de hoje, buscando dados históricos")
            result = client.table("cultural_signals")\
                .select("*")\
                .order("ts", desc=True)\
                .limit(count)\
                .execute()
            return [self._attach_context(s, context) for s in result.data] if result.data else []
        except Exception as e:
            logger.error(f"Critical fallback failure (Supabase/Context): {e}")
            return []

    def _attach_context(self, signal: dict, context: Optional[Dict[str, Any]] = None) -> dict:
        if not context:
            return signal
        enriched = signal.copy()
        enriched["onboarding_context"] = context.get("onboarding")
        enriched["project_id"] = context.get("project_id")
        enriched["user_tier"] = context.get("user_tier")
        enriched["requested_keywords"] = context.get("keywords")
        enriched["fallback_source"] = "supabase_historical"
        return enriched


def get_enriched_signals(
    plan: str = "free",
    count: int = 50,
    context: Optional[Dict[str, Any]] = None,
    force_refresh: bool = False,
    use_realtime_api: bool = False,
) -> List[dict]:
    reader = EnrichedDataReader()
    return reader.get_signals(
        plan=plan,
        count=count,
        context=context,
        force_refresh=force_refresh,
        use_realtime_api=use_realtime_api,
    )
