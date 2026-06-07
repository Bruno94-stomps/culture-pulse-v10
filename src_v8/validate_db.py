#!/usr/bin/env python3
import sys
import os
import logging
from datetime import datetime

# Setup paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from collectors.supabase_writer import _get_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DB_VALIDATOR")

def check_tables():
    client = _get_client()
    if not client:
        logger.error("❌ Supabase client não disponível. Verifique as variáveis de ambiente.")
        return

    tables = ["cultural_signals", "campaign_match_history"]
    
    for table in tables:
        try:
            # Tentar selecionar 1 linha
            result = client.table(table).select("count", count="exact").limit(1).execute()
            logger.info(f"✅ Tabela '{table}' existe e está operacional. Total rows: {result.count}")
        except Exception as e:
            logger.error(f"❌ Tabela '{table}' NÃO ENCONTRADA ou erro: {str(e)}")
            if "PGRST204" in str(e):
                logger.warning(f"💡 Sugestão: Crie a tabela '{table}' no console do Supabase.")

if __name__ == "__main__":
    check_tables()
