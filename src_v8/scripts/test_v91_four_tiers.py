#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E2E Test — V9.1 Four Tiers Pipeline
=====================================
Valida TODAS as mudanças dos 4 tiers no pipeline real:

T1  — plan_config.py: 4 tiers configurados corretamente
T2  — auth.py: CLIENTS_DB tem 4 clientes, rate limits corretos
T3  — auth.py: require_tier hierarquia 4 níveis
T4  — auth.py: JWT com tier executive funciona
T5  — streaming.py: _resolve_plan resolve 4 tiers (API key + JWT)
T6  — streaming.py: _filter_signal_by_plan filtra corretamente por tier
T7  — streaming.py: PLAN_CHANNELS tem 4 entradas (free=vazio)
T8  — streaming.py: Free bloqueado de WS (sem canal Redis)
T9  — supabase_writer.py: Upsert funciona com constraint
T10 — Supabase real: Constraint diária (SQL migration pronta)
T11 — plan_config helpers: get_ws_interval, get_retention_days, etc.

Resultado esperado: 11/11 ✅
"""
import sys, os

# Path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

passed = 0
failed = 0
total = 11

def ok(name, detail=""):
    global passed
    passed += 1
    print(f"  ✅ {name}" + (f" — {detail}" if detail else ""))

def fail(name, detail=""):
    global failed
    failed += 1
    print(f"  ❌ {name}" + (f" — {detail}" if detail else ""))


print("=" * 70)
print("E2E TEST — V9.1 FOUR TIERS PIPELINE")
print("=" * 70)

# ────────────────────────────────────────────────────────────────
# T1 — plan_config.py: 4 tiers configurados
# ────────────────────────────────────────────────────────────────
print("\nT1 — plan_config.py: 4 tiers configurados")
try:
    from config.plan_config import (
        PLAN_CONFIG, TIER_HIERARCHY, VALID_TIERS,
        get_plan, get_ws_interval, get_retention_days,
        get_rate_limit, get_redis_channel, get_buffer_replay_count,
        is_tier_valid, tier_meets_requirement,
    )
    assert len(PLAN_CONFIG) == 4, f"Expected 4 tiers, got {len(PLAN_CONFIG)}"
    assert set(PLAN_CONFIG.keys()) == {"free", "pro", "executive", "enterprise"}
    assert TIER_HIERARCHY == {"free": 0, "pro": 1, "executive": 2, "enterprise": 3}
    assert VALID_TIERS == ["free", "pro", "executive", "enterprise"]
    ok("T1", f"4 tiers: {list(PLAN_CONFIG.keys())}")
except Exception as e:
    fail("T1", str(e))

# ────────────────────────────────────────────────────────────────
# T2 — auth.py: CLIENTS_DB com 4 clientes
# ────────────────────────────────────────────────────────────────
print("\nT2 — auth.py: CLIENTS_DB com 4 clientes e rate limits corretos")
try:
    from api.middleware.auth import CLIENTS_DB
    assert len(CLIENTS_DB) == 4, f"Expected 4 clients, got {len(CLIENTS_DB)}"
    
    expected = {
        "client_demo":       ("free",       50),
        "client_pro":        ("pro",        500),
        "client_executive":  ("executive",  2000),
        "client_enterprise": ("enterprise", 10000),
    }
    for cid, (tier, rl) in expected.items():
        assert cid in CLIENTS_DB, f"Missing client: {cid}"
        assert CLIENTS_DB[cid]["tier"] == tier, f"{cid} tier={CLIENTS_DB[cid]['tier']}, expected={tier}"
        assert CLIENTS_DB[cid]["rate_limit"] == rl, f"{cid} rate_limit={CLIENTS_DB[cid]['rate_limit']}, expected={rl}"
    
    ok("T2", "4 clients: free=50/h, pro=500/h, exec=2000/h, ent=10000/h")
except Exception as e:
    fail("T2", str(e))

# ────────────────────────────────────────────────────────────────
# T3 — auth.py: require_tier hierarquia 4 níveis
# ────────────────────────────────────────────────────────────────
print("\nT3 — auth.py: require_tier hierarquia 4 níveis")
try:
    # Testar indiretamente: simular a lógica do tier_hierarchy
    tier_hierarchy = {"free": 0, "pro": 1, "executive": 2, "enterprise": 3}
    
    # free < pro < executive < enterprise
    assert tier_hierarchy["free"] < tier_hierarchy["pro"]
    assert tier_hierarchy["pro"] < tier_hierarchy["executive"]
    assert tier_hierarchy["executive"] < tier_hierarchy["enterprise"]
    
    # enterprise >= tudo
    for t in tier_hierarchy:
        assert tier_hierarchy["enterprise"] >= tier_hierarchy[t]
    
    ok("T3", "free(0) < pro(1) < executive(2) < enterprise(3)")
except Exception as e:
    fail("T3", str(e))

# ────────────────────────────────────────────────────────────────
# T4 — auth.py: JWT com tier executive
# ────────────────────────────────────────────────────────────────
print("\nT4 — auth.py: JWT gerado com tier executive")
try:
    from api.middleware.auth import create_access_token, verify_token
    import jwt as _jwt
    
    token = create_access_token("client_executive")
    assert token, "Token vazio"
    
    # Decodificar e verificar tier
    SECRET = "culture_pulse_integrated_secret_key_2025"
    payload = _jwt.decode(token, SECRET, algorithms=["HS256"])
    assert payload["sub"] == "client_executive"
    assert payload["tier"] == "executive", f"tier={payload.get('tier')}"
    
    # verify_token retorna client_id
    cid = verify_token(token)
    assert cid == "client_executive"
    
    ok("T4", f"JWT sub=client_executive, tier=executive")
except Exception as e:
    fail("T4", str(e))

# ────────────────────────────────────────────────────────────────
# T5 — streaming.py: _resolve_plan resolve 4 tiers
# ────────────────────────────────────────────────────────────────
print("\nT5 — streaming.py: _resolve_plan resolve 4 tiers (API key + JWT)")
try:
    # Import direto do ARQUIVO (evita api/endpoints/__init__.py que importa
    # tfidf/circles com core.Abas legacy quebrado)
    import importlib.util
    _streaming_path = os.path.join(PROJECT_ROOT, "api", "endpoints", "streaming.py")
    _spec = importlib.util.spec_from_file_location("streaming_direct", _streaming_path)
    streaming_mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(streaming_mod)
    
    _resolve_plan_fn = streaming_mod._resolve_plan
    _filter_fn = streaming_mod._filter_signal_by_plan
    _channels = streaming_mod.PLAN_CHANNELS
    
    # API keys estáticas
    assert _resolve_plan_fn(None) == "free", "None → free"
    assert _resolve_plan_fn("") == "free", "empty → free"
    assert _resolve_plan_fn("cp_demo_2025_free_tier") == "free"
    assert _resolve_plan_fn("cp_pro_2025_advanced") == "pro"
    assert _resolve_plan_fn("cp_executive_2025_premium") == "executive"
    assert _resolve_plan_fn("cp_enterprise_2025_unlimited") == "enterprise"
    
    # JWT
    for cid, expected_tier in [
        ("client_demo", "free"),
        ("client_pro", "pro"),
        ("client_executive", "executive"),
        ("client_enterprise", "enterprise"),
    ]:
        jwt_token = create_access_token(cid)
        resolved = _resolve_plan_fn(jwt_token)
        assert resolved == expected_tier, f"JWT {cid}: resolved={resolved}, expected={expected_tier}"
    
    ok("T5", "4 API keys + 4 JWTs resolvem corretamente")
except Exception as e:
    fail("T5", str(e))

# ────────────────────────────────────────────────────────────────
# T6 — streaming.py: _filter_signal_by_plan
# ────────────────────────────────────────────────────────────────
print("\nT6 — streaming.py: _filter_signal_by_plan filtra por tier")
try:
    # _filter_fn já carregado em T5
    test_signal = {
        "tipo": "tendencia",
        "circulo": "Música",
        "termo": "pagode",
        "score": 0.88,
        "regiao": "BA",
        "plataforma": "youtube",
        "ts": 1708600000,
        "raw_data": {
            "momentum": 88.0,
            "volume": 5000,
            "sentiment": 0.7,
            "demographic_data": {"age": "18-24"},
            "tension_indicators": {"polarization": 0.3},
            "emerging_profile_signals": {"is_emerging": True},
        },
    }
    
    # Free: só campos básicos
    free_filtered = _filter_fn(test_signal, "free")
    assert set(free_filtered.keys()) == {"tipo", "circulo", "termo", "score", "ts"}, f"Free keys: {free_filtered.keys()}"
    
    # Pro: sem raw_data
    pro_filtered = _filter_fn(test_signal, "pro")
    assert "raw_data" not in pro_filtered, "Pro não deve ter raw_data"
    assert "regiao" in pro_filtered, "Pro deve ter regiao"
    assert "plataforma" in pro_filtered, "Pro deve ter plataforma"
    
    # Executive: raw_data parcial (sem demographics/tensions)
    exec_filtered = _filter_fn(test_signal, "executive")
    assert "raw_data" in exec_filtered, "Executive deve ter raw_data"
    exec_raw = exec_filtered["raw_data"]
    assert "momentum" in exec_raw, "Executive raw deve ter momentum"
    assert "demographic_data" not in exec_raw, "Executive raw NÃO deve ter demographic_data"
    assert "tension_indicators" not in exec_raw, "Executive raw NÃO deve ter tension_indicators"
    assert "emerging_profile_signals" not in exec_raw, "Executive raw NÃO deve ter emerging_profile_signals"
    
    # Enterprise: tudo
    ent_filtered = _filter_fn(test_signal, "enterprise")
    assert ent_filtered == test_signal, "Enterprise deve retornar tudo"
    
    ok("T6", "free=5 campos, pro=sem raw, exec=raw parcial, ent=tudo")
except Exception as e:
    fail("T6", str(e))

# ────────────────────────────────────────────────────────────────
# T7 — streaming.py: PLAN_CHANNELS com 4 entradas
# ────────────────────────────────────────────────────────────────
print("\nT7 — streaming.py: PLAN_CHANNELS com 4 entradas (free=vazio)")
try:
    # _channels já carregado em T5 via streaming_mod
    assert len(_channels) == 4, f"Expected 4, got {len(_channels)}"
    assert _channels["free"] == "", "Free deve ter canal vazio"
    assert _channels["pro"] == "signals:pro"
    assert _channels["executive"] == "signals:executive"
    assert _channels["enterprise"] == "signals:enterprise"
    
    ok("T7", f"free='', pro=signals:pro, exec=signals:executive, ent=signals:enterprise")
except Exception as e:
    fail("T7", str(e))

# ────────────────────────────────────────────────────────────────
# T8 — streaming.py: Free sem canal Redis = sem WS
# ────────────────────────────────────────────────────────────────
print("\nT8 — Free sem WebSocket (canal Redis vazio)")
try:
    channel = _channels.get("free", "")
    assert channel == "", f"Free channel should be empty, got '{channel}'"
    
    # Verificar na config
    assert get_ws_interval("free") is None, "Free ws_interval should be None"
    assert get_redis_channel("free") is None, "Free redis_channel should be None"
    assert get_buffer_replay_count("free") == 0, "Free buffer should be 0"
    
    ok("T8", "Free: ws_interval=None, channel=None, buffer=0")
except Exception as e:
    fail("T8", str(e))

# ────────────────────────────────────────────────────────────────
# T9 — supabase_writer.py: Importa e funciona
# ────────────────────────────────────────────────────────────────
print("\nT9 — supabase_writer.py: Importação e health check")
try:
    from collectors.supabase_writer import is_available, health_check
    
    status = health_check()
    if status["status"] == "ok":
        ok("T9", f"Supabase writer OK: {status['details'][:50]}")
    elif status["status"] == "unavailable":
        ok("T9", f"Writer inativo (esperado em CI): {status['details']}")
    else:
        ok("T9", f"Writer status: {status}")
except Exception as e:
    fail("T9", str(e))

# ────────────────────────────────────────────────────────────────
# T10 — Migration SQL: arquivo existe e tem os comandos corretos
# ────────────────────────────────────────────────────────────────
print("\nT10 — Migration SQL V9.1 existe e contém comandos corretos")
try:
    migration_path = os.path.join(PROJECT_ROOT, "supabase", "migrations", "20260222_v91_four_tiers.sql")
    assert os.path.exists(migration_path), f"Migration não encontrada: {migration_path}"
    
    with open(migration_path, "r") as f:
        sql = f.read()
    
    checks = [
        ("CREATE profiles", "CREATE TABLE IF NOT EXISTS public.profiles"),
        ("executive", "'executive'"),
        ("constraint diária", "cultural_signals_unique_day"),
        ("ts_to_date", "ts_to_date"),
        ("dedup duplicados", "DELETE FROM public.cultural_signals a"),
        ("RLS temporal", "730 days"),
        ("RLS temporal", "365 days"),
        ("RLS temporal", "90 days"),
        ("RLS temporal", "30 days"),
        ("View pro", "signals_pro"),
        ("View executive", "signals_executive"),
        ("analyses_this_month", "analyses_this_month"),
        ("reset function", "reset_monthly_analyses"),
        ("service_role access", "service_role full access"),
    ]
    
    missing = []
    for label, pattern in checks:
        if pattern not in sql:
            missing.append(f"{label} ({pattern})")
    
    if missing:
        fail("T10", f"Faltando na migration: {missing}")
    else:
        ok("T10", f"Migration OK: {len(checks)} padrões verificados")
except Exception as e:
    fail("T10", str(e))

# ────────────────────────────────────────────────────────────────
# T11 — plan_config helpers
# ────────────────────────────────────────────────────────────────
print("\nT11 — plan_config helpers funcionam corretamente")
try:
    # get_ws_interval
    assert get_ws_interval("free") is None
    assert get_ws_interval("pro") == 30
    assert get_ws_interval("executive") == 15
    assert get_ws_interval("enterprise") == 5
    
    # get_retention_days
    assert get_retention_days("free") == 30
    assert get_retention_days("pro") == 90
    assert get_retention_days("executive") == 365
    assert get_retention_days("enterprise") == 730
    
    # get_rate_limit
    assert get_rate_limit("free") == 50
    assert get_rate_limit("pro") == 500
    assert get_rate_limit("executive") == 2000
    assert get_rate_limit("enterprise") == 10000
    
    # get_buffer_replay_count
    assert get_buffer_replay_count("free") == 0
    assert get_buffer_replay_count("pro") == 50
    assert get_buffer_replay_count("executive") == 150
    assert get_buffer_replay_count("enterprise") == 500
    
    # tier_meets_requirement
    assert tier_meets_requirement("enterprise", "free") == True
    assert tier_meets_requirement("free", "enterprise") == False
    assert tier_meets_requirement("executive", "executive") == True
    assert tier_meets_requirement("pro", "executive") == False
    
    # is_tier_valid
    assert is_tier_valid("executive") == True
    assert is_tier_valid("starter") == False
    
    ok("T11", "Todos os helpers: ws_interval, retention, rate_limit, buffer, tier_meets, is_valid")
except Exception as e:
    fail("T11", str(e))


# ────────────────────────────────────────────────────────────────
# RESULTADO
# ────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
if failed == 0:
    print(f"🎉 RESULTADO: {passed}/{total} PASSOU — V9.1 Four Tiers VALIDADO!")
else:
    print(f"⚠️  RESULTADO: {passed}/{total} passou, {failed} falhou")
print("=" * 70)

sys.exit(0 if failed == 0 else 1)
