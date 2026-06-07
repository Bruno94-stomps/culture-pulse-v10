import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any

# Mocking imports if needed for testing environment
try:
    from core.intelligence.business_synthesizer import BusinessSynthesizer, BusinessContext, get_business_synthesizer
    from core.intelligence.local_slm_bridge import LocalSLMBridge
except ImportError:
    import sys
    import os
    sys.path.append(os.path.join(os.getcwd(), 'src_v8'))
    from core.intelligence.business_synthesizer import BusinessSynthesizer, BusinessContext, get_business_synthesizer
    from core.intelligence.local_slm_bridge import LocalSLMBridge

async def run_e2e_veracity_test():
    """
    Teste de Veracidade V10.3: Validando a conexão entre Sinais Fracos e Alma do Brasileiro.
    Briefing: 'Lançamento de Marca de Cosméticos com foco em estética urbana periférica (RJ)'.
    Objetivo: Identificar inovação (Não-óbuio) e conectar com a Alma Cultural.
    """
    print("🚀 Iniciando Teste de Veracidade E2E (V10.3)...")
    
    # 1. Setup do Contexto (Briefing Real de Onboarding)
    briefing = """
    Contexto: Lançamento de nova linha de cosméticos autênticos.
    Público: Jovens da periferia do Rio de Janeiro.
    Objetivo: Inovação estética e conexão genuína com a 'estética do corre'.
    Metas: Identificar tendências emergentes que fogem do óbvio.
    """
    
    synthesizer = get_business_synthesizer()
    context = await synthesizer._analyze_business_context(briefing)
    
    # Forçar objetivo de 'inovação' para testar o filtro de Identidade Dinâmica
    context.success_metrics = ["inovação"] 
    
    print(f"\n📂 Contexto Estruturado:")
    print(f"   Cenário: {context.scenario_type}")
    print(f"   Público: {context.target_audience}")
    print(f"   Objetivo: {context.business_objective}")
    print(f"   Métricas: {context.success_metrics}")

    # 2. Sinais de Teste (Um Clichê e um Outlier)
    test_signals = [
        {
            "termo": "Samba", 
            "plataforma": "Instagram",
            "relevancia_cultural": 0.9,
            "momentum": 40,
            "texto_api": "Carnaval no Rio é sinônimo de samba e alegria.",
            "dados_extras": {"evidence": [{"url": "http://ig.com/p1", "views": 5000}]}
        },
        {
            "termo": "K-pop Periférico", 
            "plataforma": "TikTok",
            "relevancia_cultural": 0.75,
            "momentum": 85,
            "texto_api": "Grupos de dança em Madureira misturando K-pop com passinho.",
            "dados_extras": {"evidence": [{"url": "http://tk.com/v1", "views": 1500, "thumbnail": "kpop_madureira.jpg"}]}
        }
    ]

    # 3. Execução da Síntese Cultural
    print("\n🧠 Processando Sinais via BusinessSynthesizer (BERTimbau + Llama-3)...")
    results = synthesizer.analyze_cultural_signals(test_signals, context)

    # 4. Verificação de Resultados
    for res in results:
        print(f"\n--- Resultado para: {res['termo']} ---")
        print(f"📍 Quality Label: {res['quality_label']}")
        print(f"📊 Impacto de Negócio: {res['business_impact']:.2f}")
        print(f"🧬 Campaing Fit: {res['campaign_fit']:.2f}")
        print(f"📝 Alma Cultural (Narrativa): {res['narrative_context']}")
        print(f"💡 Conselho Estratégico: {res.get('recommendation', 'N/A')}")
        
        # Validação do Filtro Dinâmico
        if res['termo'] == "Samba":
            print(f"🔍 Verificação: Detectado como CLICHÊ? {'Sim' if res['business_impact'] < 0.6 else 'Não'}")
        if res['termo'] == "K-pop Periférico":
            print(f"🔍 Verificação: Detectado como WEAK SIGNAL / INOVAÇÃO? {'Sim' if res['business_impact'] > 0.7 else 'Não'}")
            
    print("\n✅ Teste de Veracidade concluído!")

if __name__ == "__main__":
    asyncio.run(run_e2e_veracity_test())
