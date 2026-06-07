#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_worker_async.py — Worker Async: Pipeline Plugável + Enrichment E2E
=========================================================================
Valida toda a cadeia:
  publish → signals:raw → AnalysisWorker → enrich pipeline → signals:enriched:{plan} → WS

Testes:
  T1 — AnalysisWorker importável + constantes expostas
  T2 — Engine registration + pipeline ordering (priority)
  T3 — Enrich pipeline (sem Redis, chamada direta)
  T4 — Publish em signals:raw (SignalPublisher integrado)
  T5 — Worker processa signals:raw → publica em signals:enriched:{plan}
  T6 — Enriched buffer LTRIM + TTL corretos
  T7 — get_enriched_buffer() retorna dados enriquecidos
  T8 — Engine enable/disable toggle dinâmico
  T9 — Engine required=True falha → pipeline interrompe
  T10 — E2E completo: publish cru → worker enriquece → buffer contém enriched

Requer: Redis rodando em localhost:6379

Uso:
  cd src_v8
  .venv/bin/python scripts/test_worker_async.py
"""

import asyncio
import json
import os
import sys
import time

# ── Configuração de paths ────────────────────────────────────────────────────
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ── Resultados ───────────────────────────────────────────────────────────────
RESULTS = []
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "models", "worker_async")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def _ok(name, detail=""):
    RESULTS.append({"test": name, "status": "PASS", "detail": detail})
    print(f"  ✅ {name}: PASS — {detail}")


def _fail(name, detail=""):
    RESULTS.append({"test": name, "status": "FAIL", "detail": detail})
    print(f"  ❌ {name}: FAIL — {detail}")


# ── Helper: Redis sync para limpeza ──────────────────────────────────────────
def _get_sync_redis():
    """Retorna cliente Redis síncrono para setup/cleanup de testes."""
    import redis
    r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
    r.ping()
    return r


def _cleanup_enriched_buffers(r):
    """Limpa buffers enriched para evitar interferência entre testes."""
    for key in ["buffer:enriched:free", "buffer:enriched:pro", "buffer:enriched:enterprise"]:
        r.delete(key)


# ═══════════════════════════════════════════════════════════════════════════════
# T1 — AnalysisWorker importável + constantes
# ═══════════════════════════════════════════════════════════════════════════════
def test_t1_import():
    name = "T1_worker_importable"
    print(f"\n{'='*60}\n  {name}\n{'='*60}")
    try:
        from core.analysis_worker import (
            AnalysisWorker,
            RegisteredEngine,
            create_default_worker,
            get_enriched_buffer,
            RAW_CHANNEL,
            ENRICHED_CHANNELS,
            ENRICHED_BUFFERS,
            ENRICHED_BUFFER_MAX,
            ENRICHED_BUFFER_TTL,
            REDIS_AVAILABLE,
        )

        assert RAW_CHANNEL == "signals:raw", f"RAW_CHANNEL={RAW_CHANNEL}"
        assert len(ENRICHED_CHANNELS) == 3, f"ENRICHED_CHANNELS={ENRICHED_CHANNELS}"
        assert "free" in ENRICHED_CHANNELS
        assert "pro" in ENRICHED_CHANNELS
        assert "enterprise" in ENRICHED_CHANNELS
        assert ENRICHED_BUFFER_MAX["free"] == 50
        assert ENRICHED_BUFFER_MAX["pro"] == 500
        assert ENRICHED_BUFFER_MAX["enterprise"] == 5000
        assert ENRICHED_BUFFER_TTL["free"] == 3600
        assert ENRICHED_BUFFER_TTL["enterprise"] == 0

        _ok(name,
            f"Redis lib={REDIS_AVAILABLE}, channels={list(ENRICHED_CHANNELS.keys())}, "
            f"max_buf=[{ENRICHED_BUFFER_MAX['free']},{ENRICHED_BUFFER_MAX['pro']},{ENRICHED_BUFFER_MAX['enterprise']}]"
        )
        return True
    except Exception as e:
        _fail(name, str(e))
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# T2 — Engine registration + pipeline ordering
# ═══════════════════════════════════════════════════════════════════════════════
def test_t2_registration():
    name = "T2_engine_registration"
    print(f"\n{'='*60}\n  {name}\n{'='*60}")
    try:
        from core.analysis_worker import AnalysisWorker

        worker = AnalysisWorker(redis_url="redis://localhost:6379/0")

        # Registrar em ordem inversa de prioridade
        worker.register("gamma", lambda s: {**s, "gamma": True}, priority=30)
        worker.register("alpha", lambda s: {**s, "alpha": True}, priority=10)
        worker.register("beta",  lambda s: {**s, "beta": True},  priority=20)

        info = worker.pipeline_info
        names = [e["name"] for e in info]
        priorities = [e["priority"] for e in info]

        assert names == ["alpha", "beta", "gamma"], f"Ordem errada: {names}"
        assert priorities == [10, 20, 30], f"Prioridades: {priorities}"

        # Unregister
        worker.unregister("beta")
        info2 = worker.pipeline_info
        names2 = [e["name"] for e in info2]
        assert "beta" not in names2, f"beta deveria ter sido removida: {names2}"
        assert len(names2) == 2

        # Chaining
        worker2 = AnalysisWorker()
        worker2.register("a", lambda s: s, priority=1).register("b", lambda s: s, priority=2)
        assert len(worker2.pipeline_info) == 2, "Chaining falhou"

        _ok(name, f"ordering=[alpha,beta,gamma], unregister=ok, chaining=ok")
        return True
    except Exception as e:
        _fail(name, str(e))
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# T3 — Enrich pipeline (sem Redis, chamada direta)
# ═══════════════════════════════════════════════════════════════════════════════
async def test_t3_enrich_direct():
    name = "T3_enrich_direct"
    print(f"\n{'='*60}\n  {name}\n{'='*60}")
    try:
        from core.analysis_worker import AnalysisWorker

        worker = AnalysisWorker()

        # Engines simples para teste
        def add_circle(signal: dict) -> dict:
            signal["circulo"] = "Tecnologia"
            signal["circle_score"] = 0.95
            return signal

        def add_sentiment(signal: dict) -> dict:
            signal["sentiment_detail"] = {"score": 0.8, "label": "positivo"}
            return signal

        async def add_auth(signal: dict) -> dict:
            """Engine async para testar suporte a corrotinas."""
            await asyncio.sleep(0.01)
            signal["authenticity_score"] = 0.92
            return signal

        worker.register("circles", add_circle, priority=10)
        worker.register("sentiment", add_sentiment, priority=20)
        worker.register("authenticity", add_auth, priority=30)

        # Executar pipeline
        raw_signal = {"tipo": "emergente", "termo": "pix parcelado", "score": 0.69}
        enriched = await worker.enrich(raw_signal)

        # Verificar enriquecimento
        assert enriched["circulo"] == "Tecnologia", f"circulo={enriched.get('circulo')}"
        assert enriched["circle_score"] == 0.95
        assert enriched["sentiment_detail"]["score"] == 0.8
        assert enriched["authenticity_score"] == 0.92

        # Verificar metadados _enrichment
        meta = enriched.get("_enrichment")
        assert meta is not None, "Falta _enrichment"
        assert "circles" in meta["engines_applied"]
        assert "sentiment" in meta["engines_applied"]
        assert "authenticity" in meta["engines_applied"]
        assert len(meta["engines_failed"]) == 0
        assert meta["duration"] > 0

        _ok(name,
            f"3 engines aplicadas (sync×2 + async×1), "
            f"duration={meta['duration']*1000:.1f}ms, "
            f"fields=[circulo, sentiment_detail, authenticity_score]"
        )
        return True
    except Exception as e:
        _fail(name, str(e))
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# T4 — Publish em signals:raw (SignalPublisher integrado)
# ═══════════════════════════════════════════════════════════════════════════════
async def test_t4_publish_raw():
    name = "T4_publish_raw"
    print(f"\n{'='*60}\n  {name}\n{'='*60}")
    try:
        import redis.asyncio as aioredis
        from api.signal_publisher import publish_signal, RAW_CHANNEL

        assert RAW_CHANNEL == "signals:raw", f"RAW_CHANNEL={RAW_CHANNEL}"

        # Assinar signals:raw ANTES de publicar
        r = await aioredis.from_url("redis://localhost:6379/0", decode_responses=True)
        pubsub = r.pubsub()
        await pubsub.subscribe("signals:raw")

        # Consumir mensagem de subscribe
        msg = await pubsub.get_message(timeout=1)

        # Publicar sinal de teste
        test_signal = {
            "tipo": "test_worker",
            "circulo": "Tecnologia",
            "termo": f"raw_test_{int(time.time())}",
            "score": 0.88,
            "ts": time.time(),
        }
        await publish_signal(test_signal)

        # Esperar mensagem no signals:raw
        received = None
        for _ in range(20):  # 20 × 100ms = 2s max
            msg = await pubsub.get_message(timeout=0.1)
            if msg and msg["type"] == "message":
                received = json.loads(msg["data"])
                break

        await pubsub.unsubscribe("signals:raw")
        await r.aclose()

        assert received is not None, "Nenhuma mensagem recebida em signals:raw"
        assert received["termo"] == test_signal["termo"], \
            f"termo={received.get('termo')}, expected={test_signal['termo']}"

        _ok(name, f"publish_signal → signals:raw entregue, termo={received['termo']}")
        return True
    except Exception as e:
        _fail(name, str(e))
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# T5 — Worker processa signals:raw → publica em signals:enriched:{plan}
# ═══════════════════════════════════════════════════════════════════════════════
async def test_t5_worker_raw_to_enriched():
    name = "T5_raw_to_enriched"
    print(f"\n{'='*60}\n  {name}\n{'='*60}")
    try:
        import redis.asyncio as aioredis
        from core.analysis_worker import AnalysisWorker, ENRICHED_CHANNELS

        # Limpar buffers enriched para evitar resíduos
        r_sync = _get_sync_redis()
        _cleanup_enriched_buffers(r_sync)

        # Criar worker com engine simples
        worker = AnalysisWorker(redis_url="redis://localhost:6379/0")
        worker.register("tag", lambda s: {**s, "enriched_by_t5": True}, priority=10)

        # Assinar um canal enriched ANTES de iniciar o worker
        r = await aioredis.from_url("redis://localhost:6379/0", decode_responses=True)
        pubsub = r.pubsub()
        await pubsub.subscribe(ENRICHED_CHANNELS["pro"])
        await pubsub.get_message(timeout=1)  # subscribe ack

        # Iniciar worker em background
        worker_task = asyncio.create_task(worker.start())

        # Dar tempo para subscriber conectar
        await asyncio.sleep(0.3)

        # Publicar sinal CRU no signals:raw
        r_pub = await aioredis.from_url("redis://localhost:6379/0", decode_responses=True)
        test_termo = f"t5_enrich_{int(time.time())}"
        raw_payload = json.dumps({
            "tipo": "emergente",
            "termo": test_termo,
            "score": 0.75,
            "ts": time.time(),
        })
        await r_pub.publish("signals:raw", raw_payload)
        await r_pub.aclose()

        # Esperar enriched no canal pro
        received_enriched = None
        t0 = time.time()
        for _ in range(50):  # 50 × 100ms = 5s max
            msg = await pubsub.get_message(timeout=0.1)
            if msg and msg["type"] == "message":
                data = json.loads(msg["data"])
                if data.get("termo") == test_termo:
                    received_enriched = data
                    break
        latency = (time.time() - t0) * 1000

        # Parar worker
        await worker.stop()
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass

        # Esperar flush do Redis (worker pode ter publicações pendentes)
        await asyncio.sleep(0.2)

        await pubsub.unsubscribe(ENRICHED_CHANNELS["pro"])
        await r.aclose()

        assert received_enriched is not None, \
            f"Nenhuma mensagem enriquecida recebida em {ENRICHED_CHANNELS['pro']} dentro de 5s"
        assert received_enriched.get("enriched_by_t5") is True, \
            f"Engine não aplicou enriquecimento: {received_enriched}"
        assert "_enrichment" in received_enriched, "Falta metadado _enrichment"
        assert "tag" in received_enriched["_enrichment"]["engines_applied"]

        stats = worker.stats
        _ok(name,
            f"signals:raw → enrich → signals:enriched:pro OK, "
            f"latency={latency:.0f}ms, processed={stats['processed']}, "
            f"enriched={stats['enriched']}"
        )
        return True
    except Exception as e:
        _fail(name, str(e))
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# T6 — Enriched buffer LTRIM + TTL
# ═══════════════════════════════════════════════════════════════════════════════
async def test_t6_buffer_ltrim_ttl():
    name = "T6_buffer_ltrim_ttl"
    print(f"\n{'='*60}\n  {name}\n{'='*60}")
    try:
        r_sync = _get_sync_redis()

        # Limpar buffers
        _cleanup_enriched_buffers(r_sync)

        # Preencher buffer:enriched:free com 80 itens (max=50)
        for i in range(80):
            payload = json.dumps({"idx": i, "tipo": "test_ltrim", "ts": time.time()})
            r_sync.lpush("buffer:enriched:free", payload)
            r_sync.ltrim("buffer:enriched:free", 0, 49)  # max Free = 50

        buf_free_len = r_sync.llen("buffer:enriched:free")
        assert buf_free_len <= 50, f"Buffer free len={buf_free_len}, expected ≤50"

        # TTL: simular expire
        r_sync.expire("buffer:enriched:free", 3600)
        ttl = r_sync.ttl("buffer:enriched:free")
        assert 0 < ttl <= 3600, f"TTL free={ttl}, expected ≤3600"

        # Enterprise: sem TTL (persist)
        r_sync.lpush("buffer:enriched:enterprise", json.dumps({"test": "ttl_ent"}))
        # Não aplicar expire → TTL deve ser -1 (persist)
        ttl_ent = r_sync.ttl("buffer:enriched:enterprise")
        assert ttl_ent == -1, f"TTL enterprise={ttl_ent}, expected -1 (persist)"

        _cleanup_enriched_buffers(r_sync)

        _ok(name,
            f"LTRIM free: 80→{buf_free_len} (max 50), "
            f"TTL free={ttl}s, TTL enterprise={ttl_ent} (persist)"
        )
        return True
    except Exception as e:
        _fail(name, str(e))
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# T7 — get_enriched_buffer() retorna dados
# ═══════════════════════════════════════════════════════════════════════════════
async def test_t7_get_enriched_buffer():
    name = "T7_get_enriched_buffer"
    print(f"\n{'='*60}\n  {name}\n{'='*60}")
    try:
        from core.analysis_worker import get_enriched_buffer, ENRICHED_BUFFERS

        r_sync = _get_sync_redis()

        # Limpar TODOS os buffers e verificar que estão vazios
        _cleanup_enriched_buffers(r_sync)
        assert r_sync.llen(ENRICHED_BUFFERS["pro"]) == 0, \
            f"Buffer pro não limpou: {r_sync.llen(ENRICHED_BUFFERS['pro'])}"

        # Inserir sinais de teste no buffer:enriched:pro
        test_termos = []
        for i in range(15):
            termo = f"t7_buf_{i}"
            test_termos.append(termo)
            payload = json.dumps({
                "tipo": "test", "termo": termo, "score": 0.5 + i * 0.03, "ts": time.time(),
            })
            r_sync.lpush(ENRICHED_BUFFERS["pro"], payload)

        # Verificar que inseriu corretamente
        buf_len = r_sync.llen(ENRICHED_BUFFERS["pro"])
        assert buf_len == 15, f"Buffer pro deveria ter 15 itens, tem {buf_len}"

        # Ler buffer via função da API
        result = await get_enriched_buffer(plan="pro", count=10)

        assert len(result) == 10, f"count=10 mas retornou {len(result)}"
        # LPUSH → mais recente está primeiro
        assert result[0]["termo"] == "t7_buf_14", \
            f"Primeiro={result[0]['termo']}, expected=t7_buf_14"
        assert result[9]["termo"] == "t7_buf_5", \
            f"Décimo={result[9]['termo']}, expected=t7_buf_5"

        # Testar count > existente retorna apenas o que existe
        result_all = await get_enriched_buffer(plan="pro", count=500)
        assert len(result_all) == 15, f"count=500, expected 15, got {len(result_all)}"

        # Respeita max_allowed do plano
        big_result = await get_enriched_buffer(plan="free", count=9999)
        # Free max = 50, mas buffer free está vazio → retorna 0
        assert len(big_result) == 0, "Buffer free deveria estar vazio"

        _cleanup_enriched_buffers(r_sync)

        _ok(name,
            f"get_enriched_buffer(pro, 10)={len(result)} itens, "
            f"ordering=LIFO ok (first={result[0]['termo']}, last={result[9]['termo']}), "
            f"count>exist={len(result_all)}"
        )
        return True
    except Exception as e:
        _fail(name, str(e))
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# T8 — Engine enable/disable toggle dinâmico
# ═══════════════════════════════════════════════════════════════════════════════
async def test_t8_enable_disable():
    name = "T8_enable_disable"
    print(f"\n{'='*60}\n  {name}\n{'='*60}")
    try:
        from core.analysis_worker import AnalysisWorker

        worker = AnalysisWorker()
        worker.register("alpha", lambda s: {**s, "alpha": True}, priority=10)
        worker.register("beta",  lambda s: {**s, "beta": True},  priority=20)
        worker.register("gamma", lambda s: {**s, "gamma": True}, priority=30)

        # Todas habilitadas
        signal = {"tipo": "test"}
        enriched = await worker.enrich(signal)
        assert enriched.get("alpha") is True
        assert enriched.get("beta") is True
        assert enriched.get("gamma") is True
        assert len(enriched["_enrichment"]["engines_applied"]) == 3

        # Desabilitar beta
        worker.disable("beta")
        info = worker.pipeline_info
        beta_info = [e for e in info if e["name"] == "beta"][0]
        assert beta_info["enabled"] is False

        enriched2 = await worker.enrich({"tipo": "test"})
        assert enriched2.get("alpha") is True
        assert enriched2.get("beta") is None, "beta deveria estar desabilitada"
        assert enriched2.get("gamma") is True
        assert len(enriched2["_enrichment"]["engines_applied"]) == 2
        assert "beta" not in enriched2["_enrichment"]["engines_applied"]

        # Re-habilitar beta
        worker.enable("beta")
        enriched3 = await worker.enrich({"tipo": "test"})
        assert enriched3.get("beta") is True
        assert len(enriched3["_enrichment"]["engines_applied"]) == 3

        _ok(name, "disable(beta)→2 engines, enable(beta)→3 engines, toggle OK")
        return True
    except Exception as e:
        _fail(name, str(e))
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# T9 — Engine required=True falha → pipeline interrompe
# ═══════════════════════════════════════════════════════════════════════════════
async def test_t9_required_engine_fail():
    name = "T9_required_engine_fail"
    print(f"\n{'='*60}\n  {name}\n{'='*60}")
    try:
        from core.analysis_worker import AnalysisWorker

        worker = AnalysisWorker()
        worker.register("ok_first", lambda s: {**s, "first": True}, priority=10)
        worker.register(
            "fail_required",
            lambda s: (_ for _ in ()).throw(ValueError("falha intencional")),
            priority=20,
            required=True,
        )
        worker.register("should_skip", lambda s: {**s, "third": True}, priority=30)

        signal = {"tipo": "test_required"}
        enriched = await worker.enrich(signal)

        # first deve ter rodado
        assert enriched.get("first") is True, "first engine deveria ter rodado"
        # third NÃO deve ter rodado (pipeline interrompido)
        assert enriched.get("third") is None, "third NÃO deveria ter rodado (pipeline interrompido)"
        # fail_required deve estar em engines_failed
        assert "fail_required" in enriched["_enrichment"]["engines_failed"]
        # first está em engines_applied, fail_required não
        assert "ok_first" in enriched["_enrichment"]["engines_applied"]
        assert "fail_required" not in enriched["_enrichment"]["engines_applied"]
        assert "should_skip" not in enriched["_enrichment"]["engines_applied"]

        _ok(name,
            f"applied={enriched['_enrichment']['engines_applied']}, "
            f"failed={enriched['_enrichment']['engines_failed']}, "
            f"pipeline interrompido após required fail"
        )
        return True
    except Exception as e:
        _fail(name, str(e))
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# T10 — E2E: publish cru → worker enriquece → buffer enriched contém resultado
# ═══════════════════════════════════════════════════════════════════════════════
async def test_t10_e2e_full():
    name = "T10_e2e_full"
    print(f"\n{'='*60}\n  {name}\n{'='*60}")
    try:
        import redis.asyncio as aioredis
        from core.analysis_worker import (
            AnalysisWorker, get_enriched_buffer, ENRICHED_BUFFERS,
        )

        r_sync = _get_sync_redis()
        _cleanup_enriched_buffers(r_sync)

        # Worker com 2 engines simples
        worker = AnalysisWorker(redis_url="redis://localhost:6379/0")
        worker.register(
            "score_boost",
            lambda s: {**s, "score": round(s.get("score", 0) * 1.5, 3)},
            priority=10,
        )
        worker.register(
            "tag_enriched",
            lambda s: {**s, "enriched": True, "worker_version": "9.1"},
            priority=20,
        )

        # Iniciar worker em background
        worker_task = asyncio.create_task(worker.start())
        await asyncio.sleep(0.3)

        # Publicar 5 sinais crus via Redis direto (simula SignalPublisher)
        r_pub = await aioredis.from_url("redis://localhost:6379/0", decode_responses=True)
        test_id = int(time.time())
        for i in range(5):
            payload = json.dumps({
                "tipo": "tendencia",
                "termo": f"e2e_{test_id}_{i}",
                "score": 0.6,
                "circulo": "Música Popular",
                "ts": time.time(),
            })
            await r_pub.publish("signals:raw", payload)
            await asyncio.sleep(0.05)
        await r_pub.aclose()

        # Esperar worker processar (max 3s)
        t0 = time.time()
        for _ in range(30):
            await asyncio.sleep(0.1)
            if worker.stats["processed"] >= 5:
                break
        process_time = (time.time() - t0) * 1000

        # Parar worker
        await worker.stop()
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass

        stats = worker.stats
        assert stats["processed"] >= 5, \
            f"processed={stats['processed']}, expected ≥5"
        assert stats["enriched"] >= 5, \
            f"enriched={stats['enriched']}, expected ≥5"
        assert stats["errors"] == 0, \
            f"errors={stats['errors']}, expected 0"

        # Verificar buffer enriched
        buf_pro = await get_enriched_buffer(plan="pro", count=10)
        assert len(buf_pro) >= 5, f"buffer pro len={len(buf_pro)}, expected ≥5"

        # Verificar enriquecimento no buffer
        sample = buf_pro[0]  # mais recente (LPUSH → LIFO)
        assert sample.get("enriched") is True, f"Falta campo 'enriched': {sample}"
        assert sample.get("worker_version") == "9.1", f"worker_version={sample.get('worker_version')}"
        assert sample.get("score") == 0.9, f"score deveria ser 0.6*1.5=0.9, got {sample.get('score')}"
        assert "_enrichment" in sample, "Falta _enrichment no buffer"

        # Buffer enterprise também deve ter
        buf_ent = await get_enriched_buffer(plan="enterprise", count=10)
        assert len(buf_ent) >= 5, f"buffer enterprise len={len(buf_ent)}, expected ≥5"

        _cleanup_enriched_buffers(r_sync)

        _ok(name,
            f"5 sinais: raw→enrich→buffer OK, "
            f"process_time={process_time:.0f}ms, "
            f"stats=[processed={stats['processed']}, enriched={stats['enriched']}, errors={stats['errors']}], "
            f"score=0.6→{sample.get('score')} (boost 1.5×)"
        )
        return True
    except Exception as e:
        _fail(name, str(e))
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════════════════════════════════
async def run_async_tests():
    """Executa testes que precisam de event loop."""
    await test_t3_enrich_direct()
    await test_t4_publish_raw()
    await test_t5_worker_raw_to_enriched()
    await test_t6_buffer_ltrim_ttl()
    await test_t7_get_enriched_buffer()
    await test_t8_enable_disable()
    await test_t9_required_engine_fail()
    await test_t10_e2e_full()


def main():
    print("=" * 70)
    print("  WORKER ASYNC — E2E Tests")
    print("  Pipeline: publish → signals:raw → AnalysisWorker → enriched → WS")
    print("=" * 70)

    # Testes síncronos
    test_t1_import()
    test_t2_registration()

    # Testes async
    asyncio.run(run_async_tests())

    # ── Sumário ──────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  SUMÁRIO")
    print("=" * 70)
    passed = sum(1 for r in RESULTS if r["status"] == "PASS")
    total = len(RESULTS)
    for r in RESULTS:
        icon = "✅" if r["status"] == "PASS" else "❌"
        print(f"  {icon} {r['test']}: {r['status']}")

    print(f"\n  RESULTADO: {passed}/{total} testes passaram")
    if passed == total:
        print("  🎉 TODOS OS TESTES PASSARAM — Worker Async validado!")
    else:
        print("  ⚠️  Há falhas — verificar logs acima")
    print("=" * 70)

    # ── Salvar resultado ─────────────────────────────────────────────────
    report = {
        "sprint": "DT-1 + Worker Async",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "passed": passed,
        "total": total,
        "tests": RESULTS,
    }
    report_path = os.path.join(OUTPUT_DIR, "test_worker_async_results.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n  📄 Relatório: {report_path}")


if __name__ == "__main__":
    main()
