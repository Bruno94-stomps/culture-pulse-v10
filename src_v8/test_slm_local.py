#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V9.9 — Teste de Validação SLM Local (Mac Mini M4)
==============================================
Verifica se a ponte com o Ollama (Llama-3-8B) está funcionando
e gerando narrativas culturais reais para o dashboard.
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório do projeto ao path para localizar os módulos
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SLM_TEST")

from core.intelligence.local_slm_bridge import get_slm_bridge
from core.intelligence.context_enricher_v2 import DashboardContextEnricher, BusinessContext

def run_validation():
    print("\n🚀 INICIANDO VALIDAÇÃO DE INTELIGÊNCIA LOCAL (LLAMA-3-8B)")
    print("============================================================")

    # 1. Testar conexão direta com a Ponte
    bridge = get_slm_bridge()
    if not bridge.is_available:
        print("❌ ERRO: Ollama não detectado. Certifique-se que o Ollama está aberto e o Llama-3-8B baixado.")
        return

    print("✅ Conexão com Llama-3-8B estabelecida!")

    # 2. Simular um cenário de negócio (Onboarding)
    contexto = BusinessContext(
        scenario_type="Estratégia de Marca",
        target_audience="Jovens de periferia apaixonados por tecnologia",
        business_objective="Lançar um novo smartphone com foco em criação de conteúdo"
    )

    # 3. Simular um sinal cultural detectado pelos motores
    signal_bruto = {
        "termo": "Dancinhas de IA no TikTok",
        "texto": "Mistura de passos de funk com filtros gerados por inteligência artificial.",
        "circulo": "Tecnologia & Digital",
        "stability_context": {"status": "emergindo"}
    }

    print("\n📡 SINAL DETECTADO: 'Dancinhas de IA no TikTok'")
    print(f"🎯 OBJETIVO: {contexto.business_objective}")
    print("\n🤖 Gerando Narrativa Cultural Real...")

    # 4. Executar o enriquecimento
    enricher = DashboardContextEnricher(use_llm=True)
    signal_enriquecido = enricher.enrich_weak_signal(
        signal=signal_bruto,
        contexto_onboarding=contexto
    )

    print("\n============================================================")
    print("📊 RESULTADO DO SLM LOCAL:")
    print("------------------------------------------------------------")
    narrativa = signal_enriquecido.get('narrativa_cultural', 'Falha ao gerar narrativa.')
    print(f"NARRATIVA: {narrativa}")
    print("------------------------------------------------------------")
    
    if signal_enriquecido.get('using_local_slm'):
        print("💎 SUCESSO: A narrativa foi gerada pelo Llama-3 local!")
    else:
        print("⚠️ AVISO: O sistema usou o fallback heurístico (templates).")
    print("============================================================\n")

if __name__ == "__main__":
    run_validation()
