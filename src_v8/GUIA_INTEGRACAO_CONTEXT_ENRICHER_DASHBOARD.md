"""
GUIA DE INTEGRAÇÃO: Context Enricher no Dashboard

📋 RESUMO:
O Context Enricher foi integrado ao dashboard através do módulo 
dashboard/context_enricher_integration.py que funciona como wrapper.

✅ VERIFICAÇÕES REALIZADAS:
1. ✅ Encoding UTF-8 compatível (sem emojis problemáticos nas strings)
2. ✅ Import sem dependências do core/__init__.py (evita erro torch)
3. ✅ Integração testada com sucesso
4. ✅ Wrapper DashboardContextEnricher criado

🎯 ONDE INTEGRAR NO DASHBOARD:

================================================================================
OPÇÃO 1: Integração Simples (Recomendada)
================================================================================

No arquivo: dashboard/cultural_dashboard_integrated_v11.py

LOCALIZAÇÃO: Dentro do método que gera sinais fracos
LINHA APROXIMADA: ~5480 (método _generate_weak_signals)

CÓDIGO A ADICIONAR:

```python
# No topo do arquivo, adicionar import:
from dashboard.context_enricher_integration import DashboardContextEnricher

# No __init__ da classe (linha ~545):
def __init__(self):
    """Inicialização otimizada do dashboard"""
    self._initialize_session_state()
    self._setup_performance_optimization()
    self._initialize_cultural_metrics_engine()
    
    # NOVO: Inicializar Context Enricher
    try:
        self.context_enricher = DashboardContextEnricher(use_llm=False)
    except Exception as e:
        print(f"⚠️ Context Enricher não disponível: {e}")
        self.context_enricher = None

# Modificar _generate_weak_signals (linha ~5480):
def _generate_weak_signals(self):
    """Gera sinais fracos detectados COM CONTEXTO NARRATIVO"""
    weak_signals = [
        {
            "title": "Micro-Influenciadores Rurais Emergindo",
            "description": "Influenciadores rurais brasileiros...",
            "strength": 0.76,
            "source": "Instagram Analytics + TikTok Trends",
            "actionable": True,
            "action": "Mapear influenciadores rurais..."
        },
        # ... outros sinais ...
    ]
    
    # NOVO: Enriquecer sinais com contexto narrativo
    if hasattr(self, 'context_enricher') and self.context_enricher:
        # Permitir seleção de segmento/desafio pelo usuário (ou usar default)
        segmento = st.session_state.get('user_segment', None)
        desafio = st.session_state.get('user_challenge', None)
        
        weak_signals = self.context_enricher.enrich_weak_signals_batch(
            weak_signals,
            segmento=segmento,
            desafio=desafio
        )
    
    return weak_signals

# Exibir contexto enriquecido (linha ~4457 onde exibe sinais):
for signal in weak_signals:
    strength_indicator = "🔥" if signal["strength"] > 0.7 else "⚡"
    
    st.markdown(f"{strength_indicator} **{signal['title']}**")
    st.markdown(f"*Força do sinal: {signal['strength']:.1%}*")
    st.markdown(f"{signal['description']}")
    
    # NOVO: Exibir contexto cultural enriquecido
    if signal.get('contexto_cultural'):
        with st.expander("🇧🇷 Ver Contexto Cultural Detalhado"):
            st.markdown("**Contexto Cultural:**")
            st.write(signal['contexto_cultural'])
            
            if signal.get('circulos_culturais'):
                st.markdown("**Círculos Culturais:**")
                st.info(signal['circulos_culturais'])
            
            if signal.get('relevancia_negocio'):
                st.markdown("**Relevância de Negócio:**")
                st.success(signal['relevancia_negocio'])
    
    # Usar recomendação enriquecida (se disponível)
    if signal['actionable']:
        action_text = signal.get('recomendacao_acao', signal.get('action', ''))
        st.info(f"💡 **Ação Recomendada:** {action_text}")
    
    st.markdown("---")
```

================================================================================
OPÇÃO 2: Adicionar Filtros de Segmento/Desafio na Sidebar
================================================================================

No sidebar do dashboard (permite usuário escolher segmento):

```python
# Na sidebar (método _render_sidebar ou similar):
st.sidebar.markdown("### 🎯 Contexto de Negócio")

# Segmento
if hasattr(self, 'context_enricher') and self.context_enricher:
    segments = self.context_enricher.get_available_segments()
    user_segment = st.sidebar.selectbox(
        "Segmento de Negócio",
        ["Nenhum"] + segments,
        help="Adapta contexto cultural ao seu segmento"
    )
    st.session_state['user_segment'] = None if user_segment == "Nenhum" else user_segment
    
    # Desafio
    challenges_map = {
        "Nenhum": None,
        "Lançamento de Produto": "lancamento_produto",
        "Reposicionamento": "reposicionamento",
        "Expansão de Mercado": "expansao_mercado",
        "Crise de Reputação": "crise_reputacao",
        "Construção de Marca": "construcao_marca",
        "Pesquisa de Mercado": "pesquisa_mercado"
    }
    
    user_challenge_display = st.sidebar.selectbox(
        "Desafio de Negócio",
        list(challenges_map.keys()),
        help="Prioriza círculos culturais relevantes ao desafio"
    )
    st.session_state['user_challenge'] = challenges_map[user_challenge_display]
```

================================================================================
OPÇÃO 3: Nova Aba "Contexto Cultural" no Dashboard
================================================================================

Criar uma nova aba dedicada ao enriquecimento de sinais:

```python
# Em render() ou main(), adicionar nova aba:
tabs = st.tabs([
    "📊 Overview",
    "📡 Sinais Fracos",
    "🇧🇷 Contexto Cultural",  # NOVO
    "📈 Tendências",
    "🎯 Futuros"
])

with tabs[2]:  # Nova aba
    st.markdown("### 🇧🇷 **Análise de Contexto Cultural**")
    st.markdown("*Enriquecimento narrativo com base em segmento e desafio*")
    
    col1, col2 = st.columns(2)
    
    with col1:
        segments = ["Tecnologia", "E-commerce", "Saúde", "Alimentação"]
        segmento = st.selectbox("Segmento", segments)
    
    with col2:
        challenges = {
            "Lançamento de Produto": "lancamento_produto",
            "Pesquisa de Mercado": "pesquisa_mercado",
            "Expansão de Mercado": "expansao_mercado"
        }
        desafio_display = st.selectbox("Desafio", list(challenges.keys()))
        desafio = challenges[desafio_display]
    
    st.markdown("---")
    
    # Gerar e enriquecer sinais
    weak_signals = self._generate_weak_signals()
    
    if hasattr(self, 'context_enricher') and self.context_enricher:
        enriched = self.context_enricher.enrich_weak_signals_batch(
            weak_signals[:3],  # Top 3 sinais
            segmento=segmento,
            desafio=desafio
        )
        
        for signal in enriched:
            with st.expander(f"🔍 {signal['title']} (Força: {signal['strength']:.1%})"):
                col_left, col_right = st.columns([2, 1])
                
                with col_left:
                    st.markdown("**Descrição:**")
                    st.write(signal['description'])
                    
                    st.markdown("**Contexto Cultural:**")
                    st.write(signal.get('contexto_cultural', 'N/A'))
                    
                    st.markdown("**Recomendação:**")
                    st.info(signal.get('recomendacao_acao', 'N/A'))
                
                with col_right:
                    st.markdown("**Círculos Culturais:**")
                    st.success(signal.get('circulos_culturais', 'N/A')[:150])
                    
                    if signal.get('relevancia_negocio'):
                        st.markdown("**Relevância:**")
                        st.metric("Score", signal['relevancia_negocio'][:50])
```

================================================================================
📊 VERIFICAÇÃO DE OUTRAS INTEGRAÇÕES NECESSÁRIAS
================================================================================

O context_enricher.py já integra:

✅ core/business_segments.py
   - Usado para adaptação por segmento
   - SEGMENT_CULTURAL_PROFILES importado
   - get_segment_characteristics() usado

✅ core/business_synthesizer.py  
   - Usado para mapeamento desafio → círculos culturais
   - Importado mas BusinessSynthesizer não instanciado diretamente
   - Usa apenas o mapeamento challenge_circle_mapping

✅ collectors/data_collectors.py
   - CulturalSignal dataclass NÃO é usada diretamente
   - context_enricher retorna Dict genérico, não CulturalSignal
   - COMPATÍVEL com qualquer fonte de dados

❌ NÃO precisa integrar com:
   - core/cultural_engine.py (independente)
   - core/tfidf_analyzer.py (independente)
   - api/main.py (pode ser usado, mas não obrigatório)

================================================================================
🧪 TESTE COMPLETO DA INTEGRAÇÃO
================================================================================

Para testar no dashboard real:

1. Adicionar import no cultural_dashboard_integrated_v11.py
2. Inicializar DashboardContextEnricher no __init__
3. Modificar _generate_weak_signals para enriquecer
4. Adicionar expander com contexto cultural na exibição
5. Executar dashboard: python dashboard/run_dashboard.py

COMANDO DE TESTE:
```bash
# Verificar se import funciona
python -c "from dashboard.context_enricher_integration import DashboardContextEnricher; print('✅ OK')"

# Testar integração standalone
python dashboard/context_enricher_integration.py

# Executar dashboard (aplicar mudanças antes)
python dashboard/run_dashboard.py
```

================================================================================
📝 RESUMO FINAL
================================================================================

✅ MÓDULO CRIADO: dashboard/context_enricher_integration.py
✅ ENCODING CORRIGIDO: Sem emojis problemáticos nas strings retornadas
✅ TESTE REALIZADO: Integration funcional
✅ WRAPPER PRONTO: DashboardContextEnricher pode ser usado diretamente

🎯 PRÓXIMO PASSO:
Escolher OPÇÃO 1, 2 ou 3 acima e aplicar no dashboard real.

Recomendação: OPÇÃO 1 (mais simples, menor impacto no código existente)

================================================================================
"""
