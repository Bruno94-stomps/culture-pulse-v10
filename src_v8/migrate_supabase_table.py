#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Migração e Validação: Criar tabela campaign_match_history no Supabase.
"""

import os
import logging
from supabase import create_client, Client
from dotenv import load_dotenv
from pathlib import Path

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("SUPABASE_MIGRATION")

def migrate_database():
    # 1. Carregar variáveis de ambiente
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        env_path = Path(__file__).parent.parent / ".env"
    
    load_dotenv(str(env_path))
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not key:
        key = os.getenv("SUPABASE_KEY")
        logger.warning("Usando SUPABASE_KEY normal. Operações de DDL podem falhar se não for service_role.")

    if not url or not key:
        logger.error("SUPABASE_URL ou SUPABASE_KEY não configurados no .env")
        return

    try:
        supabase: Client = create_client(url, key)
        
        # 2. SQL de criação da tabela
        # Nota: O cliente python do Supabase não possui um método direto .rpc() para rodar SQL puro sem uma função RPC definida.
        # Portanto, vamos tentar verificar se a tabela existe fazendo um select vazio.
        
        logger.info("Verificando existência da tabela 'campaign_match_history'...")
        try:
            supabase.table("campaign_match_history").select("id").limit(1).execute()
            logger.info("✅ Tabela 'campaign_match_history' já existe.")
        except Exception as e:
            if "PGRST204" in str(e) or "404" in str(e) or "not found" in str(e).lower():
                logger.info("❌ Tabela não encontrada. Por favor, execute o SQL no Dashboard do Supabase:")
                print("\n" + "="*50)
                print("-- COPIE E COLE NO SQL EDITOR DO SUPABASE --")
                print("""
CREATE TABLE IF NOT EXISTS public.campaign_match_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id TEXT NOT NULL,
    brand_name TEXT,
    segment TEXT,
    campaign_text TEXT,
    match_score FLOAT,
    insights JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Habilitar acesso para inserção
ALTER TABLE public.campaign_match_history FORCE ROW LEVEL SECURITY;
CREATE POLICY "Enable all for test" ON public.campaign_match_history FOR ALL USING (true) WITH CHECK (true);
                """)
                print("="*50 + "\n")
            else:
                logger.error(f"Erro inesperado ao verificar tabela: {e}")

    except Exception as e:
        logger.error(f"Erro na conexão com Supabase: {e}")

if __name__ == "__main__":
    migrate_database()
