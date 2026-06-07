#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase Writer — Culture Pulse V9.1  (Sprint S1.1 + SBFIX + 4-Tier)
====================================================
Persiste CulturalSignal no Supabase após cada ciclo de coleta.

Tabela alvo: `cultural_signals`
  id BIGSERIAL PK
  user_id UUID (FK auth.users — pode ser NULL para writes de serviço)
  tipo    TEXT   ← relevancia_cultural
  circulo TEXT   ← dados_extras.circulo  (fallback: 'geral')
  termo   TEXT
  score   NUMERIC(4,3)  ← momentum / 100, clampado 0‥1
  regiao  TEXT   ← regional_data.regiao_principal
  plataforma TEXT
  raw_data JSONB  ← demais campos do sinal
  ts TIMESTAMPTZ  ← timestamp

Env vars necessárias (em src_v8/.env):
  SUPABASE_URL          = https://<project>.supabase.co
  SUPABASE_SERVICE_KEY  = <service_role JWT>  (ignora RLS)

Conflito de upsert (V9.1 — constraint diária):
  UNIQUE INDEX em (termo, plataforma, (ts::date))
  → Cada combinação termo+plataforma gera no máximo 1 row por DIA.
  → Coletas subsequentes no mesmo dia fazem UPDATE (upsert sobrescreve).
  → Implementação: CREATE UNIQUE INDEX cultural_signals_unique_day
      ON cultural_signals (termo, plataforma, (ts::date));
"""

from __future__ import annotations

import logging
import os
from dataclasses import asdict
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

logger = logging.getLogger(__name__)

# ── S4.1: Signal Publisher (Redis Pub/Sub + buffer) ─────────────────────────
try:
    from api.signal_publisher import publish_signals_sync as _publish_to_redis
    _PUBLISHER_AVAILABLE = True
except ImportError:
    _PUBLISHER_AVAILABLE = False
    logger.debug("SignalPublisher não disponível — Redis streaming desativado")

# ── Importação lazy do supabase-py ──────────────────────────────────────────
try:
    from supabase import Client, create_client  # type: ignore
    _SUPABASE_AVAILABLE = True
except ImportError:
    _SUPABASE_AVAILABLE = False
    logger.warning(
        "⚠️  supabase-py não instalado — Supabase writer inativo. "
        "Execute: pip install supabase"
    )

if TYPE_CHECKING:
    from collectors.data_collectors import CulturalSignal  # pragma: no cover

# ── Singleton do client ──────────────────────────────────────────────────────
_client: Optional["Client"] = None


def _get_client() -> Optional["Client"]:
    """Retorna (ou cria) o client Supabase singleton."""
    global _client
    if _client is not None:
        return _client

    if not _SUPABASE_AVAILABLE:
        return None

    url = os.getenv("SUPABASE_URL", "").strip()
    key = (
        os.getenv("SUPABASE_SERVICE_KEY", "").strip()
        or os.getenv("SUPABASE_KEY", "").strip()
    )

    if not url or not key:
        logger.warning(
            "⚠️  SUPABASE_URL e/ou SUPABASE_SERVICE_KEY não definidos — "
            "Supabase writer inativo."
        )
        return None

    try:
        _client = create_client(url, key)
        logger.info("✅ Supabase client inicializado")
        return _client
    except Exception as exc:
        logger.error(f"❌ Falha ao criar Supabase client: {exc}")
        return None


# ── Mapeamento de campo ───────────────────────────────────────────────────────

def _signal_to_row(signal: "CulturalSignal", project_id: Optional[str] = None, user_id: Optional[str] = None) -> dict:
    """
    Converte um CulturalSignal para uma linha da tabela `cultural_signals`.

    Campos que vão direto para colunas dedicadas:
        termo, plataforma, relevancia_cultural → tipo,
        momentum → score (normalizado 0‧1),
        regional_data.regiao_principal → regiao,
        dados_extras.circulo → circulo,
        timestamp → ts (ISO 8601 com offset UTC).

    Todo o restante vai em `raw_data` (JSONB) para não perder informação.
    """
    # ── Normalização do timestamp ────────────────────────────────────────────
    ts = signal.timestamp
    if ts and "T" in ts:
        # já é ISO — garantir sufixo UTC se não tiver
        if ts.endswith("Z") or "+" in ts.split("T")[-1]:
            ts_iso = ts
        else:
            ts_iso = ts + "Z"
    else:
        ts_iso = datetime.now(timezone.utc).isoformat()

    # ── Campos derivados ─────────────────────────────────────────────────────
    dados_extras: dict = signal.dados_extras or {}
    regional: dict = signal.regional_data or {}

    circulo: str = (
        dados_extras.get("circulo")
        or dados_extras.get("circle")
        or "geral"
    )
    regiao: Optional[str] = (
        regional.get("regiao_principal")
        or regional.get("target_location")
    )

    # score: momentum 0-100 → 0.000-1.000
    raw_momentum = float(signal.momentum or 0)
    score = round(min(1.0, max(0.0, raw_momentum / 100.0)), 3)

    # ── Payload raw_data ────────────────────────────────────────────────────
    raw_data = {
        "momentum": raw_momentum,
        "volume": signal.volume,
        "sentiment": signal.sentiment,
        "score_qualidade": signal.score_qualidade,
        "is_verified": getattr(signal, "is_verified", False),
        "accuracy_score": getattr(signal, "accuracy_score", 0.0),
        "fonte_confiabilidade": signal.fonte_confiabilidade,
        "dados_extras": dados_extras,
        "demographic_data": signal.demographic_data or {},
        "regional_data": regional,
        "tension_indicators": signal.tension_indicators or {},
        "emerging_profile_signals": signal.emerging_profile_signals or {},
        # S3.5 — Velocity & positional features
        "velocity": getattr(signal, "velocity", None),
        "interaction_type": getattr(signal, "interaction_type", None),
        "sequence_position": getattr(signal, "sequence_position", None),
        "temporal_delta_hours": getattr(signal, "temporal_delta_hours", None),
        "momentum_velocity": getattr(signal, "momentum_velocity", None),
        # V9.9 — Local SLM Bridge (Llama-3-8B)
        "narrativa_cultural": getattr(signal, "narrativa_cultural", None),
        "recomendacao_acao": getattr(signal, "recomendacao_acao", None),
        "using_local_slm": getattr(signal, "using_local_slm", False),
    }

    project_id = (
        project_id
        or getattr(signal, "project_id", None)
        or dados_extras.get("project_id")
    )
    user_id = (
        user_id
        or getattr(signal, "user_id", None)
        or dados_extras.get("user_id")
    )

    return {
        # colunas diretas
        "tipo": signal.relevancia_cultural,
        "circulo": circulo,
        "termo": signal.termo,
        "score": score,
        "regiao": regiao,
        "plataforma": signal.plataforma,
        "raw_data": raw_data,
        "ts": ts_iso,
        "user_id": user_id,
        "project_id": project_id,
    }


# ── API pública ───────────────────────────────────────────────────────────────

def write_signals(signals: List["CulturalSignal"], project_id: Optional[str] = None, user_id: Optional[str] = None) -> int:
    """
    Persiste uma lista de CulturalSignal no Supabase de forma síncrona.

    Tenta upsert (requer UNIQUE constraint em termo,plataforma,ts).
    Se falhar com 42P10 (constraint inexistente), faz fallback para INSERT.

    Publica no Redis SEMPRE que há sinais válidos, independente do resultado
    Supabase — para não bloquear o pipeline WS/Worker quando DB falha.

    Returns:
        Número de linhas gravadas com sucesso (0 se nenhuma ou em caso de erro).
    """
    client = _get_client()

    # Filtrar Nones e converter para dicts
    rows = []
    valid_signals = []
    for sig in signals:
        if sig is None:
            continue
        try:
            rows.append(_signal_to_row(sig, project_id=project_id, user_id=user_id))
            valid_signals.append(sig)
        except Exception as exc:
            logger.warning(f"⚠️  Erro ao converter sinal para linha DB: {exc}")

    if not rows:
        logger.debug("Nenhum sinal válido para persistir.")
        return 0

    # ── S4.1-FIX: Publicar no Redis SEMPRE (não depender do Supabase) ────
    if _PUBLISHER_AVAILABLE and valid_signals:
        try:
            pub_result = _publish_to_redis(valid_signals)
            logger.info(f"📡 Redis publish: {pub_result}")
        except Exception as pub_exc:
            logger.warning(f"⚠️  Redis publish falhou (não-crítico): {pub_exc}")

    # ── Persistir no Supabase ────────────────────────────────────────────
    # V9.1: Constraint diária UNIQUE INDEX (termo, plataforma, (ts::date))
    # PostgREST não suporta on_conflict com expressões, então:
    #   1) Tentar upsert com on_conflict=termo,plataforma,ts (constraint exata)
    #   2) Se falhar (23505 duplicate de daily constraint), tentar UPDATE manual
    #   3) Fallback final: INSERT simples
    if client is None:
        logger.debug("Supabase writer inativo — sinais não persistidos (Redis OK).")
        return 0

    try:
        result = (
            client.table("cultural_signals")
            .upsert(rows, on_conflict="termo,plataforma,ts")
            .execute()
        )
        count = len(result.data) if result.data else 0
        logger.info(f"✅ Supabase: {count}/{len(rows)} sinais persistidos (upsert)")
        return count
    except Exception as exc:
        err_str = str(exc)
        if "42P10" in err_str or "ON CONFLICT" in err_str:
            # Constraint por timestamp exato não existe — fallback INSERT
            logger.warning("⚠️  UNIQUE constraint inexistente — usando INSERT (fallback)")
            try:
                result = (
                    client.table("cultural_signals")
                    .insert(rows)
                    .execute()
                )
                count = len(result.data) if result.data else 0
                logger.info(f"✅ Supabase: {count}/{len(rows)} sinais persistidos (insert fallback)")
                return count
            except Exception as insert_exc:
                ins_err = str(insert_exc)
                if "23505" in ins_err or "duplicate" in ins_err.lower():
                    # Constraint diária bloqueou → dado já existe para hoje, ok
                    logger.info("ℹ️  Sinais já existem para hoje (constraint diária) — skip OK")
                    return 0
                logger.error(f"❌ INSERT fallback também falhou: {insert_exc}")
                return 0
        elif "23505" in err_str or "duplicate" in err_str.lower():
            # Constraint diária bloqueou upsert → dado já existe para hoje
            logger.info("ℹ️  Sinais já existem para hoje (constraint diária) — skip OK")
            return 0
        else:
            logger.error(f"❌ Erro ao gravar sinais no Supabase: {exc}")
            return 0


def write_signal(signal: "CulturalSignal") -> bool:
    """Persiste um único CulturalSignal. Retorna True se bem-sucedido."""
    return write_signals([signal]) > 0


def write_signals_dict(signals_dict: dict, project_id: Optional[str] = None, user_id: Optional[str] = None) -> int:
    """
    Conveniência para o padrão do orchestrator que retorna
    Dict[str, CulturalSignal]  (chave = nome da fonte).

    Returns:
        Número de linhas gravadas.
    """
    return write_signals(list(signals_dict.values()), project_id=project_id, user_id=user_id)


def save_campaign_match(response_data: dict, client_id: str) -> bool:
    """
    Persiste o resultado de um Campaign Match no Supabase.
    """
    client = _get_client()
    if not client:
        return False
        
    try:
        # Preparar dados para inserção na tabela campaign_match_history
        payload = {
            "client_id": client_id,
            "brand_name": response_data.get("brand_name", "N/A"),
            "segment": response_data.get("segment", "N/A"),
            "campaign_text": response_data.get("campaign_text", ""),
            "match_score": response_data.get("match_score", 0),
            "authenticity_score": response_data.get("authenticity_score", 0),
            "sentiment_alignment": response_data.get("sentiment_alignment", 0),
            "risks": response_data.get("risks", []),
            "strengths": response_data.get("strengths", []),
            "suggestions": response_data.get("suggestions", []),
            "detected_circles": response_data.get("detected_circles", []),
            "geographic_spread": response_data.get("geographic_spread", [])
        }
        
        # Tentar persistência (V9.1: campaign_match_history)
        client.table("campaign_match_history").insert(payload).execute()
        logger.info(f"✅ Match de campanha salvo para o cliente {client_id}")
        return True
    except Exception as e:
        logger.error(f"⚠️ Erro ao persistir match no Supabase: {str(e)}")
        return False


# ── Health check ─────────────────────────────────────────────────────────────

def is_available() -> bool:
    """Retorna True se o Supabase writer está configurado e operacional."""
    return _get_client() is not None


def health_check() -> dict:
    """
    Verifica conectividade básica com Supabase.

    Returns:
        Dict com 'status' ('ok' | 'unavailable' | 'error') e 'details'.
    """
    if not _SUPABASE_AVAILABLE:
        return {"status": "unavailable", "details": "supabase-py não instalado"}

    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_SERVICE_KEY", "") or os.getenv("SUPABASE_KEY", "")
    if not url or not key:
        return {"status": "unavailable", "details": "Credenciais não definidas"}

    client = _get_client()
    if client is None:
        return {"status": "error", "details": "Falha ao criar client"}

    try:
        # Consulta mínima para checar conectividade
        client.table("cultural_signals").select("id").limit(1).execute()
        return {
            "status": "ok",
            "details": f"Conectado a {url[:40]}...",
            "table": "cultural_signals",
        }
    except Exception as exc:
        return {"status": "error", "details": str(exc)}
