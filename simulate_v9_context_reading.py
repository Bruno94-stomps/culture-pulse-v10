import asyncio
import json
import sys
import os

# Adicionar path para imports absolutos
# O script está na raiz, precisamos adicionar src_v8 ao path para imports de 'core' funcionarem
current_dir = os.path.dirname(os.path.abspath(__file__))
src_v8_path = os.path.join(current_dir, "src_v8")
if src_v8_path not in sys.path:
    sys.path.insert(0, src_v8_path)

from core.intelligence.business_synthesizer import BusinessSynthesizer, BusinessContext
from core.intelligence.local_slm_bridge import LocalSLMBridge

async def simulate_context_reading():
    print("🚀 INICIANDO SIMULAÇÃO DE LEITURA DE CONTEXTO V9.5")
    print("-" * 50)

    # 1. Definir o Input do Usuário (Simulando Onboarding)
    brand_name = "Natura"
    user_context_text = "Explorar como a Geração Z periférica ressignifica o luxo através do 'corre' diário e da sustentabilidade popular."
    strategic_goal = "Exploração" # Lente de Inovação/Dissonância
    
    print(f"📝 INPUT DO USUÁRIO:")
    print(f"   Marca: {brand_name}")
    print(f"   Contexto: '{user_context_text}'")
    print(f"   Objetivo: {strategic_goal}")
    print("-" * 50)

    # 2. Inicializar o Sintetizador
    # Nota: Em ambiente real, isso usaria o LocalSLMBridge (Llama-3 no Mac Mini)
    synthesizer = BusinessSynthesizer()
    
    # 3. Simular a "Leitura Semântica" do Contexto
    print("🧠 PASSO 1: MAPEAMENTO DE CÍRCULOS CULTURAIS (AFINIDADE)")
    
    # O motor busca palavras-chave e conceitos no texto para ativar os 16 círculos
    activated_circles = []
    text_lower = user_context_text.lower()
    
    for circle_name, metadata in synthesizer.cultural_circles.items():
        # Lógica simplificada de ativação baseada no motor real
        relevant_keywords = metadata.get('authenticity_markers', []) + metadata.get('opportunity_types', [])
        # Adicionando mapeamento manual para a simulação ficar clara
        keyword_map = {
            'sustentabilidade_consciente': ['sustentabilidade', 'popular'],
            'improviso_criatividade': ['corre', 'periférica', 'ressignifica'],
            'identidade_digital': ['geração z', 'gen z'],
            'natureza_meio_ambiente': ['sustentabilidade']
        }
        
        is_active = False
        # Verifica se o nome do círculo ou suas chaves estão no texto
        if circle_name in keyword_map:
            for kw in keyword_map[circle_name]:
                if kw in text_lower:
                    is_active = True
                    break
        
        if is_active:
            activated_circles.append(circle_name)
            print(f"   ✅ Círculo Ativado: [{circle_name.upper()}]")
            print(f"      -> Motivo: Termos de afinidade detectados no contexto.")

    print("-" * 50)

    # 4. Aplicação da Lente Estratégica
    print(f"🎯 PASSO 2: APLICAÇÃO DA LENTE [{strategic_goal}]")
    if strategic_goal == "Exploração":
        print("   🔍 Priorizando Sinais de Alta DISSONÂNCIA (Ruídos de Nicho).")
        print("   ⚠️ Ignorando dados de volume massivo (Mainstream).")
    elif strategic_goal == "Proteção":
        print("   🛡️ Foco em ESTABILIDADE (ARI) e FATORES DE RISCO PEST.")
    
    print("-" * 50)

    # 5. Geração do Insight de Materialização (Simulando RAG + SLM)
    print("📦 PASSO 3: MATERIALIZAÇÃO DO ASSET (O QUE O USUÁRIO VÊ)")
    
    # O sistema cruza o contexto Natura + Sustentabilidade + Corre
    proposed_asset = {
        "titulo": f"Manifesto {brand_name}: O Novo Luxo do Corre",
        "narrativa": "Sustentabilidade não como privilégio, mas como inteligência de sobrevivência e improviso.",
        "pioneirismo_score": "88% (Dissonância Narrativa Alta)",
        "proxima_acao": "Criar conteúdo com criadores do 'Grau' e 'Moda Circular Periférica' no Sudeste."
    }
    
    print(f"   💎 ASSET GERADO:")
    print(f"      Título: {proposed_asset['titulo']}")
    print(f"      Insight: {proposed_asset['narrativa']}")
    print(f"      {proposed_asset['pioneirismo_score']}")
    print(f"      🚀 Ação Recomenda: {proposed_asset['proxima_acao']}")
    print("-" * 50)
    print("✅ SIMULAÇÃO CONCLUÍDA COM SUCESSO")

if __name__ == "__main__":
    asyncio.run(simulate_context_reading())
