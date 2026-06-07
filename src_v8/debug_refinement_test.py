
import asyncio
import logging
import sys
import os
from datetime import datetime

# Adicionar path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from collectors.orchestrator import CulturalDataOrchestrator

# Configurar logging para ver os detalhes do refinamento
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DebugRefinement")

async def test_refinement_scenarios():
    orchestrator = CulturalDataOrchestrator()
    
    # CENÁRIO 1: Teste com contexto rico (Sucesso esperado no refinamento)
    print("\n--- CENÁRIO 1: CONTEXTO RICO (SUCESSO) ---")
    context_rich = {
        "location": "Rio de Janeiro",
        "demographics": {"faixa_etaria": "16-25"},
        "additional_terms": ["autenticidade", "periferia"]
    }
    # O YouTubeCollectorV8 usa esses campos para montar a query
    # Vamos simular apenas a chamada de montagem de query do YouTube para ver o log
    from collectors.data_collectors import YouTubeCollectorV8
    yt = YouTubeCollectorV8(api_key="MOCK_KEY")
    
    print("Executando refinamento para 'Samba' no Rio para Gen Z...")
    # O método correto é collect_cultural_data
    await yt.collect_cultural_data("Samba", context=context_rich)

    # CENÁRIO 2: Teste com contexto "errado" ou vazio (Debug de Fallback)
    print("\n--- CENÁRIO 2: CONTEXTO VAZIO/ERRADO (DEBUG FALLBACK) ---")
    # Aqui o sistema deve cair no fallback de 'Brasil' ou não adicionar termos extras
    context_empty = {}
    print("Executando refinamento para 'Keyword_Sem_Contexto'...")
    await yt.collect_cultural_data("Keyword_Sem_Contexto", context=context_empty)

    # CENÁRIO 3: Teste com erro de API simulado
    print("\n--- CENÁRIO 3: ERRO DE CONEXÃO/API ---")
    # Vamos forçar um erro de parâmetro na chamada para ver como o orquestrador loga o erro
    print("Simulando erro de quota/conexão na API...")
    # (O log do Orchestrator mostrará o traceback se a API falhar)
    try:
        await orchestrator.collect_comprehensive_data("teste_erro", selected_sources=["youtube"])
    except Exception as e:
        logger.error(f"Capturado erro no orquestrador: {e}")

    # CENÁRIO 4: Teste de Quota Excedida e Cache Fallback
    print("\n--- CENÁRIO 4: QUOTA EXCEDIDA E CACHE FALLBACK ---")
    # Simulamos o estouro de quota injetando uma chave inválida na instância
    yt_failed = YouTubeCollectorV8(api_key="EXPIRED_OR_INVALID_KEY")
    yt_failed.api_key = "INVALID_KEY_TO_FORCE_ERROR"
    
    # Criamos um cache fake para ver se ele recupera
    from collectors.data_collectors import data_cache
    fake_cache_key = f"youtube_Samba_{datetime.now().date()}"
    data_cache.set(fake_cache_key, {
        'count': 100,
        'videos': [{'snippet': {'title': 'Conteúdo Antigo em Cache'}}]
    })
    
    print("Tentando coletar 'Samba' com API bloqueada...")
    result = await yt_failed.collect_cultural_data("Samba", context=context_rich)
    
    if result and result.dados_extras.get('cache_hit'):
        print(f"✅ SUCESSO NO FALLBACK: Sistema usou cache (Momentum: {result.momentum})")
    else:
        print("❌ FALHA: Sistema não conseguiu recuperar do cache.")

    # CENÁRIO 5: FALHA TOTAL (SEM API E SEM CACHE)
    print("\n--- CENÁRIO 5: FALHA TOTAL (PESTILÊNCIA DIGITAL) ---")
    yt_catastrophe = YouTubeCollectorV8(api_key="BROKEN")
    yt_catastrophe.api_key = None # Forçamos erro de configuração
    
    # Limpamos o cache para este termo específico
    data_cache.set(f"youtube_CAOS_{datetime.now().date()}", None)
    
    print("Tentando coletar 'CAOS' sem API e sem Cache...")
    # O sistema deve retornar None ou cair num mock de segurança dependendo da implementação
    result_final = await yt_catastrophe.collect_cultural_data("CAOS", context={})
    
    if result_final is None:
        print("🛡️ COMPORTAMENTO ESPERADO: Sistema retornou None (Silêncio de Dados).")
        print("No dashboard, isso apareceria como 'Dados Indisponíveis' ou manteria o estado anterior.")
    else:
        print(f"⚠️ AVISO: Sistema retornou um objeto (Mock de segurança?): {result_final.plataforma}")

if __name__ == "__main__":
    asyncio.run(test_refinement_scenarios())
