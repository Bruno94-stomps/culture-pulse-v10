#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify essential environment variables for Culture Pulse production run."""

from pathlib import Path
import os

try:
    from dotenv import load_dotenv
except ImportError:
    print("ERROR: python-dotenv não está instalado. Instale com: pip install python-dotenv")
    raise

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

required_vars = [
    "FASTAPI_TOKEN",
    "SUPABASE_URL",
    "SUPABASE_SERVICE_KEY",
    "PROJECT_ANALYSIS_FASTAPI_URL",
    "NEXT_PUBLIC_FASTAPI_URL",
    "NEXT_PUBLIC_API_URL",
    "ENVIRONMENT",
    "ENABLE_DEMO_AUTH",
]

missing = []

print("🔎 Verificando variáveis de ambiente essenciais...")
for key in required_vars:
    value = os.getenv(key)
    if value is None or value == "":
        missing.append(key)
        print(f"[MISSING] {key}")
    else:
        if key == "FASTAPI_TOKEN":
            print(f"[OK] {key} is set (hidden)")
        else:
            print(f"[OK] {key}={value}")

print("")
print("ATENÇÃO:")
print("  - O token real FASTAPI_TOKEN deve vir do ambiente de produção ou do secret manager do seu deploy.")
print("  - Não coloque um token de demo.")
print("")

if missing:
    print(f"ERRO: Variáveis de ambiente faltantes: {', '.join(missing)}")
    raise SystemExit(1)

if os.getenv("ENVIRONMENT", "development").strip().lower() != "production":
    print("AVISO: ENVIRONMENT não está definido como production.")

if os.getenv("ENABLE_DEMO_AUTH", "false").strip().lower() != "false":
    print("AVISO: ENABLE_DEMO_AUTH não está definido como false. Isso pode permitir demo auth.")

print("\n✅ Verificação concluída. Todas as variáveis essenciais estão definidas.")
