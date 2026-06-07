import asyncio
import logging
from src_v8.core.intelligence.business_synthesizer import BusinessSynthesizer, BusinessContext
from src_v8.core.intelligence.local_slm_bridge import LocalSLMBridge
from dataclasses import dataclass

@dataclass
class MockAuth:
    term: str = "Tênis Customizado de Favela"
    authenticity_score: float = 0.92

async def test_business_slm():
    print("🚀 TESTE: Business Synthesizer + Local SLM (Llama-3)")
    print("="*60)
    
    # 1. Setup
    bridge = LocalSLMBridge()
    if not bridge.is_available:
        print("❌ Ollama não detectado. Abortando teste.")
        return
        
    synthesizer = BusinessSynthesizer(slm_bridge=bridge)
    
    context = BusinessContext(
        scenario_type="Lançamento de Produto",
        target_audience="Jovens de periferia apaixonados por moda urbana",
        business_objective="Lançar uma collab de tênis autêntica",
        opportunities_sought=["Conexão genuína", "Relevância cultural"]
    )
    
    # 2. Mock dos dados necessários para o conselho estratégico
    auth = MockAuth()
    threshold = {"is_breakout": True}
    semantic = {"tags": ["Moda", "Periferia"]}
    narrative = {
        "context": "O uso de tênis customizados em comunidades reflete o orgulho territorial e a estética da superação.",
        "relevance": "Sinal ideal para colabs que valorizam o artista local."
    }
    
    print(f"📡 Sinal: {auth.term}")
    print(f"🤖 Gerando Conselho Estratégico via Llama-3 Local...")
    
    advice = synthesizer._generate_strategic_advice(auth, threshold, semantic, narrative)
    
    print("\n" + "-"*60)
    print("📊 RESULTADO DO BUSINESS SLM:")
    print(advice)
    print("-"*60)
    
    if len(advice) > 50:
        print("✅ SUCESSO: Estratégia gerada pela IA!")
    else:
        print("⚠️ AVISO: A estratégia parece muito curta ou um fallback.")

if __name__ == "__main__":
    asyncio.run(test_business_slm())
