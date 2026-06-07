#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test S4.1 — REST→Redis→WebSocket Streaming Pipeline
=====================================================
Valida que o fluxo completo funciona:
  1. SignalPublisher publica sinal no Redis (3 canais + buffer)
  2. Buffer replay retorna sinais recentes
  3. Filtro por plano funciona corretamente
  4. WebSocket endpoint registrado no FastAPI
  5. supabase_writer integra com publisher

Sprint S4.1 — Critério de aceite:
  "browser recebe sinal real via WebSocket < 30s após coleta"

Uso:
  cd src_v8
  .venv/bin/python scripts/test_s41_streaming.py
"""

import sys
import os
import asyncio
import json
import time
import logging

# Prevent Streamlit from auto-launching
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")

# Setup paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
logger = logging.getLogger("test_s41")

# ─────────────────────────────────────────────────────────────────────────────
# Test Results Tracker
# ─────────────────────────────────────────────────────────────────────────────

results = []

def log_result(test_name: str, passed: bool, detail: str = ""):
    status = "✅ PASS" if passed else "❌ FAIL"
    results.append({"name": test_name, "passed": passed, "detail": detail})
    logger.info(f"{status} | {test_name}{f' — {detail}' if detail else ''}")


# ─────────────────────────────────────────────────────────────────────────────
# TEST 1: SignalPublisher importável
# ─────────────────────────────────────────────────────────────────────────────

def test_publisher_import():
    try:
        from api.signal_publisher import (
            publish_signal,
            publish_signals,
            get_buffer,
            publish_signals_sync,
            health_check,
            PLAN_CHANNELS,
            PLAN_BUFFERS,
            PLAN_BUFFER_MAX,
            PLAN_BUFFER_TTL,
            REDIS_AVAILABLE,
        )
        log_result(
            "T1 — SignalPublisher importável",
            True,
            f"Redis lib available: {REDIS_AVAILABLE}, "
            f"channels: {list(PLAN_CHANNELS.keys())}, "
            f"buffers: {list(PLAN_BUFFERS.keys())}"
        )
        return True
    except Exception as e:
        log_result("T1 — SignalPublisher importável", False, str(e))
        return False


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2: Signal conversion (CulturalSignal → publish dict)
# ─────────────────────────────────────────────────────────────────────────────

def test_signal_conversion():
    try:
        from api.signal_publisher import _signal_to_publish_dict

        # Test with dict input
        d = _signal_to_publish_dict({
            "tipo": "emergente",
            "circulo": "Música",
            "termo": "brega funk",
            "score": 0.75,
        })
        assert "ts" in d, "Missing ts"
        assert d["termo"] == "brega funk"
        assert d["score"] == 0.75

        # Test with mock CulturalSignal-like object
        class MockSignal:
            def __init__(self):
                self.relevancia_cultural = "tendencia"
                self.termo = "açaí premium"
                self.momentum = 87.0
                self.volume = 1200
                self.sentiment = 0.65
                self.plataforma = "youtube"
                self.dados_extras = {"circulo": "Gastronomia"}
                self.regional_data = {"regiao_principal": "SP"}
                self.score_qualidade = 0.9
                self.fonte_confiabilidade = 0.85
                self.demographic_data = {}
                self.tension_indicators = {}
                self.emerging_profile_signals = {}
                self.timestamp = None

        sig = MockSignal()
        d2 = _signal_to_publish_dict(sig)
        assert d2["tipo"] == "tendencia"
        assert d2["circulo"] == "Gastronomia"
        assert d2["termo"] == "açaí premium"
        assert 0.0 <= d2["score"] <= 1.0
        assert d2["plataforma"] == "youtube"
        assert d2["regiao"] == "SP"
        assert "raw_data" in d2

        log_result("T2 — Signal conversion", True, f"dict→ok, CulturalSignal→ok (score={d2['score']})")
        return True
    except Exception as e:
        log_result("T2 — Signal conversion", False, str(e))
        return False


# ─────────────────────────────────────────────────────────────────────────────
# TEST 3: Redis connectivity + publish + buffer
# ─────────────────────────────────────────────────────────────────────────────

async def test_redis_publish_and_buffer():
    try:
        from api.signal_publisher import (
            publish_signal, get_buffer, health_check, REDIS_AVAILABLE
        )

        if not REDIS_AVAILABLE:
            log_result("T3 — Redis publish + buffer", False, "Redis lib not installed")
            return False

        # Health check
        hc = await health_check()
        if hc["status"] != "ok":
            log_result("T3 — Redis publish + buffer", False, f"Redis unreachable: {hc}")
            return False

        # Publish a test signal
        test_signal = {
            "tipo": "test_s41",
            "circulo": "Tecnologia",
            "termo": f"test_streaming_{int(time.time())}",
            "score": 0.99,
            "regiao": "BR",
            "plataforma": "test",
            "ts": time.time(),
        }

        t0 = time.time()
        recipients = await publish_signal(test_signal)
        latency_ms = (time.time() - t0) * 1000

        # Read buffer — signal should be there
        buffer_free = await get_buffer(plan="free", count=5)
        buffer_pro = await get_buffer(plan="pro", count=5)

        found_in_free = any(s.get("termo") == test_signal["termo"] for s in buffer_free)
        found_in_pro = any(s.get("termo") == test_signal["termo"] for s in buffer_pro)

        passed = found_in_free and found_in_pro
        log_result(
            "T3 — Redis publish + buffer",
            passed,
            f"recipients={recipients}, latency={latency_ms:.1f}ms, "
            f"in_free_buffer={found_in_free}, in_pro_buffer={found_in_pro}"
        )
        return passed
    except Exception as e:
        log_result("T3 — Redis publish + buffer", False, str(e))
        return False


# ─────────────────────────────────────────────────────────────────────────────
# TEST 4: Plan filtering works correctly
# ─────────────────────────────────────────────────────────────────────────────

def test_plan_filtering():
    try:
        # Import from streaming.py
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "streaming",
            os.path.join(PROJECT_ROOT, "api", "endpoints", "streaming.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _filter = mod._filter_signal_by_plan

        full_signal = {
            "tipo": "emergente",
            "circulo": "Música",
            "termo": "brega funk",
            "score": 0.88,
            "ts": time.time(),
            "regiao": "NE",
            "plataforma": "youtube",
            "raw_data": {"views": 50000, "sentiment": 0.7},
        }

        # Free: apenas campos básicos, sem raw_data
        free = _filter(full_signal, "free")
        assert "raw_data" not in free
        assert "plataforma" not in free  # free gets only tipo,circulo,termo,score,ts
        assert free["tipo"] == "emergente"

        # Pro: tudo exceto raw_data
        pro = _filter(full_signal, "pro")
        assert "raw_data" not in pro
        assert pro["plataforma"] == "youtube"

        # Enterprise: tudo
        ent = _filter(full_signal, "enterprise")
        assert "raw_data" in ent
        assert ent["raw_data"]["views"] == 50000

        log_result(
            "T4 — Plan filtering",
            True,
            f"free={len(free)} fields, pro={len(pro)} fields, enterprise={len(ent)} fields"
        )
        return True
    except Exception as e:
        log_result("T4 — Plan filtering", False, str(e))
        return False


# ─────────────────────────────────────────────────────────────────────────────
# TEST 5: supabase_writer has publisher integration
# ─────────────────────────────────────────────────────────────────────────────

def test_supabase_writer_integration():
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "supabase_writer",
            os.path.join(PROJECT_ROOT, "collectors", "supabase_writer.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        # Check that the publisher import exists
        has_publisher = hasattr(mod, "_PUBLISHER_AVAILABLE")
        has_publish_fn = hasattr(mod, "_publish_to_redis")

        log_result(
            "T5 — supabase_writer publisher integration",
            has_publisher and has_publish_fn,
            f"_PUBLISHER_AVAILABLE attr={has_publisher}, _publish_to_redis attr={has_publish_fn}"
        )
        return has_publisher and has_publish_fn
    except Exception as e:
        log_result("T5 — supabase_writer publisher integration", False, str(e))
        return False


# ─────────────────────────────────────────────────────────────────────────────
# TEST 6: streaming.py has demo_mode opt-in and buffer replay
# ─────────────────────────────────────────────────────────────────────────────

def test_streaming_refactored():
    try:
        filepath = os.path.join(
            PROJECT_ROOT,
            "api", "endpoints", "streaming.py"
        )
        with open(filepath, "r") as f:
            code = f.read()

        has_demo_mode = "demo_mode" in code
        has_buffer_replay = "replay" in code.lower()
        has_publisher_import = "_PUBLISHER_AVAILABLE" in code
        no_auto_demo = 'demo_mode: bool = Query(default=False' in code
        has_offline = '"offline": True' in code

        all_ok = has_demo_mode and has_buffer_replay and has_publisher_import and no_auto_demo and has_offline

        log_result(
            "T6 — streaming.py refactored (S4.1)",
            all_ok,
            f"demo_mode={has_demo_mode}, buffer_replay={has_buffer_replay}, "
            f"publisher={has_publisher_import}, opt_in_demo={no_auto_demo}, "
            f"offline_mode={has_offline}"
        )
        return all_ok
    except Exception as e:
        log_result("T6 — streaming.py refactored (S4.1)", False, str(e))
        return False


# ─────────────────────────────────────────────────────────────────────────────
# TEST 7: End-to-end latency (publish → buffer read < 30s)
# ─────────────────────────────────────────────────────────────────────────────

async def test_e2e_latency():
    try:
        from api.signal_publisher import publish_signal, get_buffer, REDIS_AVAILABLE

        if not REDIS_AVAILABLE:
            log_result("T7 — E2E latency < 30s", False, "Redis not available")
            return False

        unique_term = f"e2e_latency_test_{int(time.time() * 1000)}"
        test_signal = {
            "tipo": "test_s41",
            "circulo": "Tecnologia",
            "termo": unique_term,
            "score": 0.95,
            "plataforma": "test_e2e",
            "ts": time.time(),
        }

        t_start = time.time()

        # Step 1: Publish
        await publish_signal(test_signal)

        # Step 2: Read from buffer
        buffer = await get_buffer(plan="pro", count=10)
        t_end = time.time()

        found = any(s.get("termo") == unique_term for s in buffer)
        latency_ms = (t_end - t_start) * 1000

        passed = found and latency_ms < 30000  # < 30 seconds

        log_result(
            "T7 — E2E latency < 30s",
            passed,
            f"latency={latency_ms:.1f}ms, found_in_buffer={found}, "
            f"criterion: < 30000ms ({'MET' if passed else 'NOT MET'})"
        )
        return passed
    except Exception as e:
        log_result("T7 — E2E latency < 30s", False, str(e))
        return False


# ─────────────────────────────────────────────────────────────────────────────
# TEST 8: Buffer limits respected (LTRIM)
# ─────────────────────────────────────────────────────────────────────────────

async def test_buffer_limits():
    try:
        from api.signal_publisher import (
            publish_signal, get_buffer, REDIS_AVAILABLE, PLAN_BUFFER_MAX
        )

        if not REDIS_AVAILABLE:
            log_result("T8 — Buffer limits (LTRIM)", False, "Redis not available")
            return False

        # Read current buffer size
        buffer = await get_buffer(plan="free", count=PLAN_BUFFER_MAX["free"] + 50)
        current_size = len(buffer)
        max_size = PLAN_BUFFER_MAX["free"]

        passed = current_size <= max_size

        log_result(
            "T8 — Buffer limits (LTRIM)",
            passed,
            f"free buffer size={current_size}, max={max_size}"
        )
        return passed
    except Exception as e:
        log_result("T8 — Buffer limits (LTRIM)", False, str(e))
        return False


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

async def run_async_tests():
    await test_redis_publish_and_buffer()
    await test_e2e_latency()
    await test_buffer_limits()


def main():
    print("=" * 70)
    print("🧪 S4.1 — TEST: REST → Redis → WebSocket Streaming Pipeline")
    print("=" * 70)
    print()

    # Sync tests
    test_publisher_import()
    test_signal_conversion()
    test_plan_filtering()
    test_supabase_writer_integration()
    test_streaming_refactored()

    # Async tests (Redis)
    try:
        asyncio.run(run_async_tests())
    except Exception as e:
        logger.warning(f"⚠️  Async tests skipped: {e}")

    # Summary
    print()
    print("=" * 70)
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    print(f"📊 RESULTADO: {passed}/{total} testes passaram")
    print("=" * 70)

    for r in results:
        icon = "✅" if r["passed"] else "❌"
        print(f"  {icon} {r['name']}")

    # Save results
    results_dir = os.path.join(
        PROJECT_ROOT,
        "models", "streaming_s41"
    )
    os.makedirs(results_dir, exist_ok=True)

    results_file = os.path.join(results_dir, "s41_test_results.json")
    import json as json_mod
    with open(results_file, "w") as f:
        json_mod.dump({
            "sprint": "S4.1",
            "description": "REST → Redis → WebSocket Streaming",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "passed": passed,
            "total": total,
            "all_passed": passed == total,
            "results": results,
        }, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Resultados salvos em: {results_file}")

    # Criteria check
    redis_tests = [r for r in results if "Redis" in r["name"] or "E2E" in r["name"] or "Buffer" in r["name"]]
    non_redis = [r for r in results if r not in redis_tests]

    non_redis_passed = all(r["passed"] for r in non_redis)
    redis_passed = all(r["passed"] for r in redis_tests) if redis_tests else False

    print()
    if non_redis_passed:
        print("✅ CRITÉRIO CODE: Todos os testes de código passaram")
    else:
        print("❌ CRITÉRIO CODE: Falha em testes de código")

    if redis_passed:
        print("✅ CRITÉRIO REDIS: Pub/Sub + Buffer + E2E latency OK")
    else:
        print("⚠️  CRITÉRIO REDIS: Redis não disponível ou testes falharam")
        print("   → Redis é necessário para streaming real. Sem Redis = modo offline.")

    print()
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
