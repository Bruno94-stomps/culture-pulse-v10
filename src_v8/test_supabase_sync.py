#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import json
import asyncio
from datetime import datetime, timezone

# Ajustar paths para encontrar o pacote src_v8
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src_v8.collectors.supabase_writer import write_signals, _get_client

class MockSignal:
    def __init__(self, termo, plataforma):
        self.termo = termo
        self.plataforma = plataforma
        self.relevancia_cultural = "sinal_fraco"
        self.momentum = 85.0
        self.volume = 1500
        self.sentiment = 0.8
        self.score_qualidade = 0.9
        self.fonte_confiabilidade = "V9.9_Test"
        self.timestamp = datetime.now(timezone.utc).isoformat()
        
        # Atributos novos da V9.9
        self.narrativa_cultural = "Narrativa de teste gerada pelo Llama-3 Local (Simulação)"
        self.recomendacao_acao = "Passo 1: Validar | Passo 2: Escalar"
        self.using_local_slm = True
        
        # Placeholders para conformidade com a assinatura do writer
        self.dados_extras = {"circulo": "tecnologia"}
        self.regional_data = {"regiao_principal": "Brasil"}
        self.demographic_data = {}
        self.tension_indicators = {}
        self.emerging_profile_signals = {}
        self.velocity = 0.8
        self.interaction_type = "viral"
        self.sequence_position = 1
        self.temporal_delta_hours = 0.1
        self.momentum_velocity = 0.5

def test_supabase_sync():
    print("🧪 TESTE DE SINCRONIZAÇÃO SUPABASE (V9.9)")
    print("="*60)
    
    # 1. Verificar conexão
    client = _get_client()
    if not client:
        print("❌ Falha crítica: Supabase não configurado.")
        return

    # 2. Criar sinal mock com dados da IA
    termo_teste = f"IA_LOCAL_TEST_{datetime.now().strftime('%H%M%S')}"
    mock = MockSignal(termo_teste, "YouTube")
    
    print(f"📡 Enviando sinal '{termo_teste}' para o Supabase...")
    count = write_signals([mock])
    
    if count > 0:
        print(f"✅ Sucesso: {count} sinal persistido.")
        
        # 3. Verificar se os campos da IA estão no raw_data do banco
        print("🔍 Validando persistência no banco...")
        try:
            res = client.table("cultural_signals").select("raw_data").eq("termo", termo_teste).execute()
            if res.data:
                raw = res.data[0]['raw_data']
                print(f"   - Narrativa salva: {raw.get('narrativa_cultural')[:50]}...")
                print(f"   - Estratégia salva: {raw.get('recomendacao_acao')[:50]}...")
                print(f"   - Tag SLM: {raw.get('using_local_slm')}")
                
                if raw.get('narrativa_cultural') and raw.get('using_local_slm'):
                    print("\n💎 SINCRONIZAÇÃO COMPLETA: Frontend lerá estes dados via JSONB.")
                else:
                    print("\n⚠️ AVISO: Alguns campos parecem ausentes no raw_data.")
            else:
                print("❌ Erro: Sinal não encontrado no banco após gravação.")
        except Exception as e:
            print(f"❌ Erro na validação: {e}")
    else:
        print("❌ Falha na gravação do sinal.")

if __name__ == "__main__":
    test_supabase_sync()
