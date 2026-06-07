import asyncio
import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ValidationScript")

# Carregar variáveis de ambiente do .env da src_v8
load_dotenv("src_v8/.env")

async def validate_active_learning():
    print("\n🧪 VALIDANDO: InsightLearner (H.I.T.L. + Signal Quality)")
    print("-" * 60)
    try:
        from src_v8.core.intelligence.learning.InsightLearner import get_insight_learner
        engine = get_insight_learner()
        
        # 1. Simular feedback para um termo novo
        query = "tech_wear_consolidated"
        print(f"Submetendo feedback para: {query}")
        res = engine.submit_query_feedback(
            query=query,
            relevant=True,
            confidence=0.95,
            notes="Teste pós-fusão de arquivos"
        )
        print(f"✅ Feedback gravado: {res['status']}")
        
    except Exception as e:
        print(f"❌ Erro no InsightLearner: {e}")

async def validate_automated_learning():
    print("\n🧪 VALIDANDO: StrategyLearner (Industry Weights + Performance)")
    print("-" * 60)
    try:
        from src_v8.core.intelligence.learning.StrategyLearner import get_strategy_learner
        engine = get_strategy_learner()
        
        # 1. Verificar pesos da indústria
        weights = engine._load_model_weights()
        print(f"✅ Pesos Estratégicos carregados: {weights}")
        
    except Exception as e:
        print(f"❌ Erro no StrategyLearner: {e}")

async def main():
    print("🚀 INICIANDO DIAGNÓSTICO DE CHAMADAS BACKEND V9.7")
    await validate_active_learning()
    await validate_automated_learning()
    print("\n🏁 DIAGNÓSTICO CONCLUÍDO")

if __name__ == "__main__":
    asyncio.run(main())
