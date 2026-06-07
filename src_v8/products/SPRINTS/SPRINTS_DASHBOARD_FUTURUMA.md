# 📊 INVENTÁRIO COMPLETO - Dashboard Futurumã V9.1

**Data:** 5 de fevereiro de 2026  
**Objetivo:** Mapear TODAS as dimensões, features, painéis e análises antes de implementar onboarding

---

## 🎯 RESUMO EXECUTIVO

**Status:** Dashboard com **ALTA COMPLEXIDADE** - 3,236 linhas, 15 painéis, 4 tabs, 30+ métricas

### Problemas Identificados:
1. ⚠️ **Sobrecarga cognitiva**: Muitos painéis sem hierarquia clara
2. ⚠️ **Falta de progressividade**: Tudo exposto ao mesmo tempo
3. ⚠️ **Personalização invisível**: Context Enricher não tem UI dedicada
4. ⚠️ **Redundâncias**: 2 sistemas de tensões (system + real)

### Oportunidades:
1. ✅ Sistema tecnicamente completo (100.4% conformidade)
2. ✅ 6 dimensões contextuais implementadas
3. ✅ Forecasting + Scenario Planning integrados
4. ⏭️ Precisa apenas de **simplificação + UI progressiva**

---

## 📐 DIMENSÕES DO SISTEMA

### 1. **Dimensões de Análise Cultural** (6 implementadas)

| Dimensão | Descrição | Implementado? | Visível no Dashboard? |
|----------|-----------|---------------|----------------------|
| **Semantic Context** | Termos relacionados (BERTimbau 768d) | ✅ SIM | ⚠️ Parcial (tab 4) |
| **Territorial Context** | 16 círculos + 5 regiões + 8 plataformas | ✅ SIM | ⚠️ Parcial (tab 4) |
| **Tension Context** | 12 tipos de tensões culturais | ✅ SIM | ✅ SIM (painel dedicado) |
| **Temporal Context** | Week-over-week, velocidade, crescimento | ✅ SIM | ⚠️ Parcial (tab 4) |
| **Behavioral Context** | Padrões emergentes, journey mapping | ✅ SIM | ❌ NÃO (invisível) |
| **Narrative Context** | Narrativas automáticas (WHERE/WHAT/WHICH) | ✅ SIM | ⚠️ Parcial (tab 4) |

**PROBLEMA:** 6 dimensões implementadas, mas 50% invisíveis ou difíceis de acessar.

---

### 2. **Dimensões de Personalização** (Context Enricher - 7 camadas)

| Camada | Função | Implementado? | Visível no UI? |
|--------|--------|---------------|----------------|
| **Layer 1: Text Analysis** | TF-IDF + sentiment | ✅ SIM | ❌ NÃO |
| **Layer 2: Knowledge Base** | 15 termos culturais BR | ✅ SIM | ❌ NÃO |
| **Layer 3: LLM Framework** | OpenAI/Anthropic (opcional) | ✅ SIM | ❌ NÃO |
| **Layer 4: Cache System** | Composite keys (termo+segmento+desafio) | ✅ SIM | ❌ NÃO |
| **Layer 5: Segment Adaptation** | cultural_weight (1.2-1.5) | ✅ SIM | ❌ NÃO |
| **Layer 6: Challenge Adaptation** | circle prioritization | ✅ SIM | ❌ NÃO |
| **Layer 7: XGBoost Features** | 789 features prontas | ✅ SIM | ❌ NÃO |

**PROBLEMA CRÍTICO:** Context Enricher 100% implementado, mas **0% visível** no dashboard.  
**IMPACTO:** Usuários não sabem que personalização existe.

---

## 🎨 PAINÉIS DO DASHBOARD (15 painéis)

### **SIDEBAR** (Configuração)

| Componente | Linhas | Função | Complexidade |
|------------|--------|--------|--------------|
| Problema de Negócio | 26 | Dropdown 10 opções | Média |
| Keywords | 42 | Text input + exemplos | Baixa |
| Período | 45 | Date range picker | Baixa |
| Opções de Exibição | 5 | Slider (max signals) | Baixa |
| **TOTAL SIDEBAR** | **118** | **4 seções** | **Média** |

---

### **CONTEÚDO PRINCIPAL** (11 painéis + 4 tabs)

#### **PAINÉIS SEMPRE VISÍVEIS** (acima das tabs)

| # | Painel | Função | Linhas | Métricas | Prioridade |
|---|--------|--------|--------|----------|-----------|
| 1 | **Signal Velocity** | Classificação velocidade (rápido/médio/lento) | 132 | 3 classes + distribuição | ALTA |
| 2 | **System Tensions** | Tensões culturais detectadas | 112 | 12 tipos de tensões | ALTA |
| 3 | **Forecasting** | Projeções Prophet + Ridge (7/30/90 dias) | 130 | 3 horizontes temporais | ALTA |
| 4 | **Topics** | Topic Modeling (LDA) | 60 | N topics configurável | MÉDIA |
| 5 | **Real Tensions** | Tensões reais (fallback para system) | 83 | Por tipo (digital/geracional/regional) | MÉDIA |
| 6 | **Emerging Audiences** | Clustering HDBSCAN de públicos | 146 | Clusters + features | MÉDIA |
| 7 | **Autonomous Decisions** | Decisões IA (estratégica/tática/reativa) | 122 | 3 níveis de decisão | BAIXA |
| 8 | **ML Predictions** | 4 modelos ML (trend/engagement/virality/opportunity) | 126 | 4 predictions + confidence | MÉDIA |
| 9 | **Temporal Validation** | Validação temporal (baseline + trends) | 143 | 4 métricas de estabilidade | BAIXA |
| 10 | **Scenario Planning** | 3 cenários (otimista/base/pessimista) | 292 | 3 tabs × 3 cenários | ALTA |
| 11 | **Contextual Intelligence** | 6 dimensões contextuais | 87 | 4 tabs (narratives/territory/temporal/semantic) | **CRÍTICO** |

**TOTAL PAINÉIS PRINCIPAIS:** 1,433 linhas (44% do código)

---

#### **TABS INFERIORES** (4 tabs fixas)

| Tab | Nome | Função | Linhas | Complexidade |
|-----|------|--------|--------|--------------|
| Tab 1 | **Sinais Detectados** | Lista de cards com todos os sinais | 8 (loop render_weak_signal_card) | Alta (cada card: 62 linhas) |
| Tab 2 | **Análise Temporal** | Timeline chart (plotly) | 66 | Média |
| Tab 3 | **Mapa de Tensões** | Network graph (círculos culturais) | 52 | Alta |
| Tab 4 | **Monitoramento ML/NLP** | Drift detection (V9.1) | 15 | Média |

---

## 📊 FEATURES E MÉTRICAS (30+ métricas)

### **Métricas por Weak Signal** (17 métricas)

| Categoria | Métricas | Fonte |
|-----------|----------|-------|
| **Score & Volume** | weak_signal_score, volume_atual, volume_7d_ago | WeakSignalDetector |
| **Momentum** | current_momentum, momentum_7d_ago, momentum_aceleracao | momentum.py |
| **Sentiment** | sentiment_positivo, sentiment_humor, sentiment_stability | TF-IDF Analyzer |
| **Temporal** | first_mention, latest_mention, timespan_days | CulturalSignal |
| **Engagement** | engagement_rate (likes/comments/shares) | Calculado |
| **Plataformas** | plataformas (list), volume_por_plataforma (dict) | CulturalSignal |
| **Cultural** | contextos_culturais, circulos_priorizados | Context Enricher |
| **Tensões** | tensoes_detectadas (list) | TensionDetectionEngine |

---

### **Métricas Agregadas do Dashboard** (13 métricas)

| Métrica | Função | Painel |
|---------|--------|--------|
| **Qualidade Geral** | Avg score → Excelente/Boa/Inicial/Fraca | Header |
| **Distribuição de Velocidade** | Rápido/Médio/Lento (%) | Signal Velocity |
| **Tensões Ativas** | Count por tipo (digital/geracional/regional) | System Tensions |
| **Forecast Confidence** | Prophet confidence intervals | Forecasting |
| **Topic Coherence** | LDA coherence score | Topics |
| **Cluster Quality** | Silhouette score (HDBSCAN) | Emerging Audiences |
| **Decision Confidence** | Autonomous agent confidence | Autonomous Decisions |
| **Model Accuracy** | F1-score dos 4 modelos ML | ML Predictions |
| **Temporal Stability** | Change rate over baseline | Temporal Validation |
| **Scenario Probability** | Otimista/Base/Pessimista (%) | Scenario Planning |
| **Semantic Similarity** | Cosine similarity (BERTimbau) | Contextual Intel (tab 4) |
| **Growth Rate** | Week-over-week % change | Contextual Intel (tab 3) |
| **Territorial Coverage** | Regiões + Círculos ativas | Contextual Intel (tab 2) |

---

## 🔍 ANÁLISES DISPONÍVEIS (8 sistemas)

| Sistema | Arquivo | Função | Usado no Dashboard? |
|---------|---------|--------|---------------------|
| **Weak Signal Detector** | products/weak_signal_detector.py | Detecta sinais fracos (30 métricas) | ✅ SIM (core) |
| **Momentum Calculator** | core/momentum.py | Calcula momentum cultural real | ✅ SIM (todos sinais) |
| **Tension Analyzer** | core/tension_detection_engine.py | 12 tipos de tensões | ✅ SIM (painel dedicado) |
| **TF-IDF Analyzer** | core/tfidf_analyzer.py | Topic Modeling (LDA) | ✅ SIM (painel topics) |
| **Clustering Engine** | core/clustering_engine.py | HDBSCAN para públicos | ✅ SIM (emerging audiences) |
| **Predictive Analytics** | autonomous_agent/predictive_analytics.py | Prophet + Ridge forecasting | ✅ SIM (forecasting panel) |
| **Scenario Planning** | core/scenario_planning_engine.py | 3 cenários × 3 horizontes | ✅ SIM (scenario panel) |
| **Contextual Intelligence** | core/contextual_intelligence_engine.py | 6 dimensões + Context Enricher | ⚠️ PARCIAL (tab 4 only) |

**TAXA DE USO:** 100% dos sistemas implementados estão no dashboard  
**PROBLEMA:** Contextual Intelligence mal exposta (tab 4, não integrada aos sinais)

---

## 🎨 COMPONENTES VISUAIS (12 tipos)

| Tipo | Quantidade | Biblioteca | Uso |
|------|------------|------------|-----|
| **Cards** | 1 tipo (weak signal card) | Next.js/React + CSS | Tab 1 |
| **Line Charts** | 3 (timeline, temporal, growth) | Plotly | Tabs 2, 4 |
| **Bar Charts** | 5 (velocity, tensions, topics, etc) | Plotly | Painéis |
| **Pie Charts** | 2 (círculos, regiões) | Plotly | Tab 4 |
| **Network Graphs** | 2 (tension map, semantic network) | Plotly | Tab 3, Tab 4 |
| **Heatmaps** | 1 (context dissemination) | Plotly | Tab 3 |
| **Scatter Plots** | 2 (clusters, predictions) | Plotly | Painéis |
| **Gauges** | 1 (confidence score) | Plotly | Autonomous |
| **Tables** | 4 (signals list, topics, tensions, etc) | Next.js/React | Diversos |
| **Metrics** | 20+ (st.metric equiv.) | Next.js/React | Headers |
| **Expanders** | 10+ (detalhes) | Next.js/React | Cards |
| **Tabs** | 2 conjuntos (4 + 3) | Next.js/React | Principal + Scenarios |

---

## 📋 ESTRUTURA HIERÁRQUICA DO DASHBOARD

```
🔮 FUTURUMÃ DASHBOARD
│
├── 📊 SIDEBAR (Configuração)
│   ├── Problema de Negócio (dropdown)
│   ├── Keywords (text input)
│   ├── Período (date range)
│   └── Opções (slider)
│
├── 🎯 MAIN CONTENT
│   │
│   ├── ⚡ FILTROS AVANÇADOS (render_advanced_filters)
│   │   └── [não implementado visualmente - retorna dict vazio]
│   │
│   ├── 📊 KPIs HEADER
│   │   ├── Qualidade Geral (score médio)
│   │   ├── Total de Sinais
│   │   └── Range de Scores
│   │
│   ├── 🚀 PAINÉIS PRINCIPAIS (11 painéis sempre visíveis)
│   │   ├── 1️⃣ Signal Velocity Panel ⭐
│   │   ├── 2️⃣ System Tensions Panel ⭐
│   │   ├── 3️⃣ Forecasting Panel ⭐
│   │   ├── 4️⃣ Topics Panel
│   │   ├── 5️⃣ Real Tensions Panel
│   │   ├── 6️⃣ Emerging Audiences Panel
│   │   ├── 7️⃣ Autonomous Decisions Panel
│   │   ├── 8️⃣ ML Predictions Panel
│   │   ├── 9️⃣ Temporal Validation Panel
│   │   ├── 🔟 Scenario Planning Panel ⭐⭐
│   │   └── 1️⃣1️⃣ Contextual Intelligence Panel ⭐⭐⭐ CRÍTICO
│   │
│   └── 📑 TABS INFERIORES (4 tabs fixas)
│       ├── Tab 1: 📋 Sinais Detectados (lista completa)
│       ├── Tab 2: 📊 Análise Temporal (timeline)
│       ├── Tab 3: 🌐 Mapa de Tensões (network graph)
│       └── Tab 4: 🔄 Monitoramento ML/NLP (drift detection)
│
└── 💡 TELA INICIAL (quando não há dados)
    ├── Explicação do sistema (3 colunas)
    └── Case Study: Nike x Maduro
```

---

## ⚠️ PROBLEMAS IDENTIFICADOS (5 críticos)

### 1. **SOBRECARGA VISUAL** 🔴 CRÍTICO

**Problema:**  
- 11 painéis sempre visíveis (1,433 linhas)
- Usuário precisa scrollar >3 telas para ver tudo
- Sem hierarquia clara entre painéis essenciais vs avançados

**Impacto:**
- Time-to-first-insight: >30min
- Bounce rate: ~40% (estimado)
- Usuários confusos sobre "onde começar"

**Solução Proposta:**
- Tabs progressivas: "Básico" → "Avançado" → "Especialista"
- Colapsar painéis menos usados
- Dashboard adaptativo (mostrar apenas o que é relevante)

---

### 2. **CONTEXTUAL INTELLIGENCE INVISÍVEL** 🔴 CRÍTICO

**Problema:**
- Context Enricher: 1,273 linhas de código (7 camadas)
- Personalização por segmento/desafio: **0% visível no UI**
- Tab 4 "Contextual Intelligence" isolada, não integrada aos sinais
- Usuários não sabem que podem ter análises personalizadas

**Impacto:**
- **INOVAÇÃO ÚNICA perdida** (único sistema com personalização cultural)
- Diferencial competitivo invisível
- ROI do Context Enricher: 0% (tecnicamente pronto, comercialmente invisível)

**Solução Proposta:**
- Welcome screen com seleção de perfil (segmento + desafio)
- Sidebar persistente mostrando perfil ativo
- Context comparison modal ("Ver como outro segmento vê isso")
- Badge em cada sinal: "Personalizado para Alimentos"

---

### 3. **REDUNDÂNCIA DE TENSÕES** 🟡 MÉDIO

**Problema:**
- 2 painéis de tensões: `system_tensions_panel` + `real_tensions_panel`
- Lógica duplicada (283 linhas vs 195 linhas)
- Usuário não entende a diferença

**Solução Proposta:**
- Unificar em 1 painel: "Tensões Culturais"
- Usar `real_tensions` como primário, `system` como fallback
- Economizar ~200 linhas de código

---

### 4. **FALTA DE PROGRESSIVIDADE** 🟡 MÉDIO

**Problema:**
- Tudo exposto ao mesmo tempo
- Usuário novato vs expert veem a mesma interface
- Sem indicação de "fluxo recomendado"

**Solução Proposta:**
- Onboarding com 5 passos:
  1. Selecionar perfil
  2. Buscar 1 termo
  3. Ver top 3 sinais
  4. Explorar contexto cultural
  5. Exportar insights
- Progress indicator (% explorado)
- Tooltip contextual em cada métrica

---

### 5. **TABS MAL ESTRUTURADAS** 🟠 BAIXO

**Problema:**
- 4 tabs fixas no rodapé (depois de 11 painéis)
- Tab 1 "Sinais Detectados" duplica informação (painéis já mostram sinais)
- Tab 4 "Monitoramento ML/NLP" relevante só para time técnico

**Solução Proposta:**
- Reorganizar em tabs temáticas:
  - **Tab 1: Overview** (KPIs + top 5 sinais + forecasting)
  - **Tab 2: Análise Profunda** (todos os 11 painéis em accordion)
  - **Tab 3: Contexto Cultural** (contextual intelligence dedicada)
  - **Tab 4: Configurações** (filtros avançados + monitoramento)

---

## 💡 RECOMENDAÇÕES DE SIMPLIFICAÇÃO

### **FASE 6A: Simplificação Imediata** (1-2 dias)

#### 1. **Unificar Tensões** ✂️ CORTAR
- Remover `system_tensions_panel` (112 linhas)
- Manter apenas `real_tensions_panel` (83 linhas)
- **Economia:** -112 linhas, -1 painel

#### 2. **Colapsar Painéis Avançados** 📦 ORGANIZAR
- Mover para expanders (collapsed por padrão):
  - Autonomous Decisions (122 linhas)
  - Temporal Validation (143 linhas)
  - ML Predictions (126 linhas)
- **Economia:** -391 linhas visíveis inicialmente

#### 3. **Reorganizar Tabs** 🗂️ REESTRUTURAR
- **Nova Tab 1: Overview** (300 linhas)
  - KPIs header
  - Top 5 sinais (cards)
  - Forecasting quick view
- **Nova Tab 2: Análise Cultural** (900 linhas)
  - Signal Velocity
  - Contextual Intelligence (destacado)
  - Scenario Planning
- **Nova Tab 3: Avançado** (500 linhas)
  - Topics, Clustering, ML Predictions
  - Temporal Validation
  - Monitoramento

#### 4. **Remover Tab "Sinais Detectados"** ❌ ELIMINAR
- Redundante (painéis já mostram sinais)
- Migrar funcionalidade para Tab 1 (Overview)
- **Economia:** -1 tab, -8 linhas

**TOTAL ECONOMIA FASE 6A:** -503 linhas visíveis, -2 redundâncias, +3 tabs reorganizadas

---

### **FASE 6B: Onboarding & Personalização** (3-4 dias)

#### 1. **Welcome Screen** 🎯 NOVO
```python
# dashboard/onboarding_manager.py (200 linhas)
if 'user_profile' not in st.session_state:
    render_welcome_screen()  # Selecionar segmento + desafio
    return  # Não mostrar dashboard antes de configurar
```

#### 2. **Sidebar com Avatar** 👤 NOVO
```python
# dashboard/components/profile_selector.py (150 linhas)
st.sidebar.markdown(f"### 👤 {segment_avatar} {segmento}")
st.sidebar.caption(f"🎯 Desafio: {desafio}")
st.sidebar.caption(f"🔵 Círculos: {', '.join(circulos_prioritarios[:3])}")
```

#### 3. **Context Comparison Modal** 🔀 NOVO
```python
# dashboard/components/context_comparison.py (250 linhas)
if st.button("🔀 Ver como outro segmento vê isso"):
    show_comparison_modal(signal, current_segment, compare_segment)
    # Mostra lado a lado: Alimentos vs Entretenimento
```

#### 4. **Tutorial Interativo** 📚 NOVO
```python
# dashboard/components/interactive_tour.py (180 linhas)
if st.session_state.first_time_user:
    run_joyride_tour()  # 5 passos essenciais
```

**TOTAL ADIÇÕES FASE 6B:** +780 linhas, +4 componentes novos

---

### **FASE 6C: Visualizações Aprimoradas** (2-3 dias)

#### 1. **Context Cards** 💳 MELHORAR
- Antes/depois da personalização
- Highlight de círculos priorizados
- Badge "Personalizado para {segmento}"

#### 2. **Mapa Interativo do Brasil** 🗺️ NOVO
- folium integration (regiões clicáveis)
- Popup com volume por região
- Heatmap de intensidade cultural

#### 3. **Network 3D** 🌐 MELHORAR
- plotly 3D para semantic network
- Tooltip interativo com similarity
- Zoom/pan fluido

**TOTAL ADIÇÕES FASE 6C:** +300 linhas visuais

---

## 📊 RESUMO FINAL: ANTES vs DEPOIS

| Métrica | ANTES (V9.1 atual) | DEPOIS (V9.2 com FASE 6) | Delta |
|---------|-------------------|--------------------------|-------|
| **Linhas Visíveis** | 1,433 (11 painéis) | 930 (6 painéis + tabs) | **-35%** |
| **Tabs Fixas** | 4 tabs confusas | 3 tabs temáticas | **-25%** |
| **Redundâncias** | 2 (tensões duplicadas) | 0 | **-100%** |
| **Personalização Visível** | 0% | 100% (sidebar + comparison) | **+100%** |
| **Time-to-First-Insight** | >30min | <3min (com onboarding) | **-90%** |
| **Componentes Novos** | 0 | 4 (welcome/avatar/comparison/tour) | **+4** |
| **Total Linhas Código** | 3,236 | 4,016 (+780 onboarding) | **+24%** |
| **Usabilidade (NPS)** | ~5/10 (estimado) | >8/10 (target) | **+60%** |

---

## 🎯 PRÓXIMOS PASSOS RECOMENDADOS

### **Prioridade CRÍTICA** (começar AGORA):

1. ✅ **Inventário completo** (este documento) - CONCLUÍDO
2. ⏭️ **FASE 6A: Simplificação** (1-2 dias)
   - Unificar tensões
   - Colapsar painéis avançados
   - Reorganizar tabs
3. ⏭️ **FASE 6B: Onboarding** (3-4 dias)
   - Welcome screen
   - Sidebar com avatar
   - Context comparison modal
   - Tutorial interativo
4. ⏭️ **FASE 6C: Visualizações** (2-3 dias)
   - Context cards
   - Mapa do Brasil
   - Network 3D

**TIMELINE TOTAL:** 6-9 dias para dashboard production-ready

---

## 📌 OBSERVAÇÕES FINAIS

### **Pontos Fortes a Manter:**
- ✅ Sistema tecnicamente completo (100.4% conformidade acadêmica)
- ✅ 6 dimensões contextuais funcionando
- ✅ Context Enricher (1,273 linhas, 7 camadas)
- ✅ Forecasting + Scenario Planning integrados

### **Gaps Críticos a Resolver:**
- 🔴 Context Enricher invisível no UI
- 🔴 Sobrecarga visual (11 painéis sempre visíveis)
- 🟡 Redundâncias (2 painéis de tensões)
- 🟡 Falta de progressividade (novato vs expert)

### **Diferencial Competitivo a Explorar:**
- ⭐ **ÚNICO sistema com personalização cultural**
- ⭐ Alimentos vs Entretenimento (Copa 2026) = prova de conceito
- ⭐ Context Enricher pronto para uso comercial

**Decisão:** Implementar FASE 6 COMPLETA para desbloquear adoção em escala.

---

---

## 🎯 PLANO DE SIMPLIFICAÇÃO EXECUTIVA (Estilo SIGNAL_LAB)

### 📋 **REFERÊNCIA DE DESIGN**: SIGNAL_LAB Dashboard
- **Público-alvo**: CMO, C-level (sem tempo para profundidade técnica)
- **Princípios**: Limpo, direto, acionável
- **Estrutura**: 4 abas superiores + KPIs visuais + tabela de sinais

---

## 🚀 FASE 6A: SIMPLIFICAÇÃO IMEDIATA (1-2 dias)

### **1. UNIFICAR TENSÕES** ✂️

**ANTES:** 2 painéis redundantes
- `render_system_tensions_panel()` - 112 linhas
- `render_real_tensions_panel()` - 83 linhas
- **Total:** 195 linhas duplicadas

**DEPOIS:** 1 painel unificado
```python
def render_tensions_panel(weak_signals, tensions_result=None):
    """Unified tension panel with fallback"""
    if tensions_result:
        # Usar real tensions (TensionDetectionEngine)
        display_real_tensions(tensions_result)
    else:
        # Fallback para system tensions (heurístico)
        display_system_tensions(weak_signals)
```

**Economia:** -112 linhas, -1 painel redundante

---

### **2. COLAPSAR PAINÉIS AVANÇADOS** 📦

**Painéis para EXPANDER (collapsed por padrão):**

| Painel | Motivo | Público | Linhas |
|--------|--------|---------|--------|
| **Autonomous Decisions** | Muito técnico para CMO | Data Scientists | 122 |
| **Temporal Validation** | Métrica de confiabilidade interna | DevOps/QA | 143 |
| **ML Predictions** | 4 modelos confusos sem contexto | Analistas | 126 |
| **Monitoramento ML/NLP (Tab 4)** | Drift detection técnico | ML Engineers | 15 |

**Total colapsado:** 406 linhas invisíveis por padrão

---

### **3. ELIMINAR REDUNDÂNCIAS** ❌

| Elemento | Redundância | Ação |
|----------|-------------|------|
| **Tab 1: Sinais Detectados** | Já mostrado em painéis | ❌ REMOVER |
| **Filtros Avançados** | Retorna dict vazio | ❌ REMOVER (não implementado) |

**Economia:** -8 linhas visíveis

---

## 🎨 FASE 6B: NOVA ESTRUTURA (4 ABAS SUPERIORES)

### 📐 **WIREFRAME DA NOVA ARQUITETURA**

```
┌─────────────────────────────────────────────────────────────────────┐
│  🔮 FUTURUMÃ    [Dashboard] [Projetos] [Sinais] [Analytics]  [+New] │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Welcome back, Jordan                                          [JD] │
│  Your weak signals intelligence platform is detecting              │
│  27 active behavioral patterns across 5 regions                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

### **ABA 1: 📊 DASHBOARD** (Visão Executiva Simplificada)

**OBJETIVO:** Responder em 10 segundos:
1. **O que está acontecendo?** (KPIs)
2. **Quão forte?** (Signal Strength)
3. **Quão rápido?** (Trend Velocity)

#### **LAYOUT (inspirado em SIGNAL_LAB):**

```
┌────────────────────────────────────────────────────────────────┐
│ Welcome back, [Nome do Usuário]                                │
│ [Mensagem contextual baseada em último scan]                   │
│                                                                │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│ │ 847      │ │ 2.4M     │ │ 34.2%    │ │ 94.7     │          │
│ │ ACTIVE   │ │ AUDIENCE │ │ CONVERS. │ │ GROWTH   │          │
│ │ SIGNALS  │ │ REACH    │ │ RATE     │ │ INDEX    │          │
│ │ +12.3%   │ │ +8.7%    │ │ +5.1%    │ │ +15.8%   │          │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│                                                                │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │ 📈 SIGNAL ACTIVITY (Last 6 weeks)                       │   │
│ │ [Line chart verde suave - estilo SIGNAL_LAB]            │   │
│ └─────────────────────────────────────────────────────────┘   │
│                                                                │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│ │ 47       │ │ 87.3%    │ │ 1,247    │ │ +42.8%   │          │
│ │ GLOBAL   │ │ SIGNAL   │ │ PATTERN  │ │ TREND    │          │
│ │ COVERAGE │ │ STRENGTH │ │ DETECT.  │ │ VELOCITY │          │
│ │ regions  │ │ avg conf │ │ patterns │ │ growth   │          │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
└────────────────────────────────────────────────────────────────┘
```

#### **COMPONENTES MAPEADOS:**

| # | Componente Origem | Métrica Destino | Posição |
|---|-------------------|-----------------|---------|
| 1 | KPIs Header → | **ACTIVE SIGNALS** (847) | Card top-left |
| 2 | Signal Velocity → | **TREND VELOCITY** (+42.8%) | Card top-right |
| 3 | Forecasting → | **GROWTH INDEX** (94.7) | Card top-center-right |
| 4 | Temporal Context → | **SIGNAL ACTIVITY** (6 weeks chart) | Chart middle |
| 5 | Territorial Context → | **GLOBAL COVERAGE** (47 regions) | Card bottom-left |
| 6 | Real Tensions → | **SIGNAL STRENGTH** (87.3% avg) | Card bottom-center |
| 7 | Emerging Audiences → | **PATTERN DETECTION** (1,247) | Card bottom-center-right |

**Painéis REMOVIDOS desta aba:**
- Topics (muito técnico)
- ML Predictions (confuso sem contexto)
- Autonomous Decisions (muito técnico)
- Temporal Validation (métrica interna)

**Total de componentes:** **8 cards + 1 chart = 9 elementos**  
**Tempo de leitura:** <10 segundos

---

### **ABA 2: 📁 PROJETOS** (Gestão de Pesquisas)

**OBJETIVO:** Criar e gerenciar múltiplas pesquisas (marca, tema, assunto)

#### **LAYOUT:**

```
┌────────────────────────────────────────────────────────────────┐
│ 🔍 Search...                                        [+ New Project] │
│                                                                │
│ PROJECT ENTRIES                                     [View All] │
│ Active behavioral patterns and weak signals                    │
│                                                                │
│ ┌──────────────────────────────────────────────────────┐      │
│ │ ID       SIGNAL              AUDIENCE    REGION    ⋮ │      │
│ ├──────────────────────────────────────────────────────┤      │
│ │ SIG-2847 AI Content Resist   Gen Z      N.America  ⋮ │      │
│ │          Updated 2h ago                              │      │
│ │ SIG-2846 Micro-Community     Millennials Europe    ⋮ │      │
│ │ SIG-2845 Nostalgia-Driven    Gen X      APAC       ⋮ │      │
│ │ SIG-2844 Privacy-Conscious   Early Adp  Global     ⋮ │      │
│ └──────────────────────────────────────────────────────┘      │
└────────────────────────────────────────────────────────────────┘
```

#### **COMPONENTES MAPEADOS:**

| # | Componente Origem | Função Destino | Descrição |
|---|-------------------|----------------|-----------|
| 1 | **Sidebar → Keywords** | **[+ New Project] Button** | Criar nova pesquisa |
| 2 | **Tab 1: Sinais Detectados** | **PROJECT ENTRIES Table** | Lista de projetos ativos |
| 3 | **Context Enricher → Segmento** | **Filtro: Industry** | Filtrar por segmento |
| 4 | **Context Enricher → Desafio** | **Filtro: Goal** | Filtrar por objetivo |

#### **MODAL: New Project (Welcome Screen Integrado)**

```
┌────────────────────────────────────────────────────────┐
│ ✨ Create New Project                                  │
│                                                        │
│ User Profile                                           │
│ ┌────────────────────────────────────────────────┐    │
│ │ Name: [Jordan Silva_____________________]      │    │
│ └────────────────────────────────────────────────┘    │
│                                                        │
│ Brand/Topic to Research                                │
│ ┌────────────────────────────────────────────────┐    │
│ │ [Copa do Mundo 2026__________________]         │    │
│ └────────────────────────────────────────────────┘    │
│                                                        │
│ Industry Segment                                       │
│ ┌────────────────────────────────────────────────┐    │
│ │ [v] Alimentação e Bebidas                      │    │
│ │ [ ] Entretenimento                             │    │
│ │ [ ] Tecnologia                                 │    │
│ │ [ ] E-commerce                                 │    │
│ └────────────────────────────────────────────────┘    │
│                                                        │
│ Business Goal                                          │
│ ┌────────────────────────────────────────────────┐    │
│ │ [v] Pesquisa de Mercado                        │    │
│ │ [ ] Lançamento de Produto                      │    │
│ │ [ ] Construção de Marca                        │    │
│ └────────────────────────────────────────────────┘    │
│                                                        │
│ Target Audience                                        │
│ ┌────────────────────────────────────────────────┐    │
│ │ [v] Famílias 25-44                             │    │
│ │ [v] Classe B/C                                 │    │
│ │ [v] Sul/Sudeste                                │    │
│ └────────────────────────────────────────────────┘    │
│                                                        │
│ Data Sources                                           │
│ ┌────────────────────────────────────────────────┐    │
│ │ [v] YouTube  [v] Reddit  [v] News  [v] Trends │    │
│ └────────────────────────────────────────────────┘    │
│                                                        │
│ Keywords (Optional - or use AI templates)              │
│ ┌────────────────────────────────────────────────┐    │
│ │ [futebol, copa, seleção, mundial______]       │    │
│ │                                                │    │
│ │ 💡 Templates: [Evento Esportivo] [Produto]    │    │
│ └────────────────────────────────────────────────┘    │
│                                                        │
│ [Cancel]                      [Create & Analyze] │    │
└────────────────────────────────────────────────────────┘
```

**AFTER CREATE:** Redireciona para **Aba 3: Sinais** com análise do projeto criado.

---

### **ABA 3: 📊 SINAIS** (Análise Macro por Projeto)

**OBJETIVO:** Ver análise macro de cada projeto/pesquisa

#### **LAYOUT:**

```
┌────────────────────────────────────────────────────────────────┐
│ 🔍 [Dropdown: Selecionar Projeto]  Copa do Mundo 2026    [⋮]  │
│                                                                │
│ 👤 Perfil: Alimentação e Bebidas | Pesquisa de Mercado        │
│ 🎯 Círculos prioritários: Família, Diversidade Regional        │
│                                                                │
│ ════════════════════════════════════════════════════════       │
│                                                                │
│ 🚀 SIGNAL VELOCITY                                             │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐                        │
│ │ 🔥 45%   │ │ ⚡ 32%   │ │ 🐌 23%   │                        │
│ │ RÁPIDO   │ │ MÉDIO    │ │ LENTO    │                        │
│ └──────────┘ └──────────┘ └──────────┘                        │
│ [Bar chart: distribuição velocidade]                          │
│                                                                │
│ ════════════════════════════════════════════════════════       │
│                                                                │
│ ⚠️ TENSÕES CULTURAIS ATIVAS                                    │
│ ┌────────────────────────────────────────────────────┐        │
│ │ 🔴 DIGITAL: Tradição vs Inovação (0.78)            │        │
│ │ 🟡 GERACIONAL: Millennials vs Gen Z (0.52)         │        │
│ │ 🟢 REGIONAL: Sudeste vs Nordeste (0.34)            │        │
│ └────────────────────────────────────────────────────┘        │
│                                                                │
│ ════════════════════════════════════════════════════════       │
│                                                                │
│ 📈 FORECASTING (Next 90 days)                                  │
│ ┌────────────────────────────────────────────────────┐        │
│ │ [Line chart: 7/30/90 dias Prophet + confidence]   │        │
│ │ Breakthrough estimado: 12 de março (68% confiança) │        │
│ └────────────────────────────────────────────────────┘        │
│                                                                │
│ ════════════════════════════════════════════════════════       │
│                                                                │
│ 👥 PÚBLICOS EMERGENTES                                         │
│ ┌────────────────────────────────────────────────────┐        │
│ │ Cluster 1: "Pais planejando viagem" (287 perfis)  │        │
│ │ Cluster 2: "Torcedores engajados" (534 perfis)    │        │
│ │ Cluster 3: "Empresas patrocínio" (129 perfis)     │        │
│ └────────────────────────────────────────────────────┘        │
│                                                                │
│ ════════════════════════════════════════════════════════       │
│                                                                │
│ 🎯 TOP 5 SINAIS FRACOS                                         │
│ ┌────────────────────────────────────────────────────┐        │
│ │ 1. "Kit família Copa" (Score: 87.3) 🔥             │        │
│ │    Volume: 12.4k | Momentum: +142% | Plataformas: │        │
│ │    YouTube (48%), Reddit (32%), News (20%)         │        │
│ │    [Ver Contexto Cultural] [Comparar Segmentos]    │        │
│ │                                                    │        │
│ │ 2. "Churrasco torcida" (Score: 82.1) ⚡            │        │
│ │ 3. "Produtos regionais Copa" (Score: 78.5) ⚡       │        │
│ │ 4. "Festa junina mundial" (Score: 71.2) 🐌         │        │
│ │ 5. "Delivery Copa" (Score: 68.9) 🐌                │        │
│ └────────────────────────────────────────────────────┘        │
└────────────────────────────────────────────────────────────────┘
```

#### **COMPONENTES MAPEADOS:**

| # | Painel Origem | Seção Destino | Posição |
|---|---------------|---------------|---------|
| 1 | **Context Enricher** | **Perfil Header** (top) | Persistente |
| 2 | **Signal Velocity Panel** | **🚀 SIGNAL VELOCITY** | Seção 1 |
| 3 | **Real Tensions Panel** | **⚠️ TENSÕES CULTURAIS** | Seção 2 |
| 4 | **Forecasting Panel** | **📈 FORECASTING** | Seção 3 |
| 5 | **Emerging Audiences Panel** | **👥 PÚBLICOS EMERGENTES** | Seção 4 |
| 6 | **Tab 1: Sinais Detectados** | **🎯 TOP 5 SINAIS FRACOS** | Seção 5 |
| 7 | **Contextual Intelligence (parcial)** | **[Ver Contexto Cultural] Button** | Dentro de cada sinal |

**Painéis INTEGRADOS (não mais separados):**
- Signal Velocity
- Tensions
- Forecasting
- Emerging Audiences
- Top Signals

**Total de seções:** **5 seções bem definidas**  
**Scroll:** ~2 telas (vs 3+ antes)

---

### **ABA 4: 📊 ANALYTICS** (Análise Detalhada + Previsões)

**OBJETIVO:** Análise profunda + cenários futuros + monitoramento

#### **SUB-TABS:**
- **Análise Temporal**
- **Cenários Futuros**
- **Contexto Cultural**
- **Monitoramento ML**

#### **COMPONENTES MAPEADOS (por sub-tab):**

| Sub-Tab | Painéis Origem | Descrição |
|---------|----------------|-----------|
| **Análise Temporal** | Tab 2 (Timeline) + Tab 3 (Mapa Tensões) | Timeline chart + Network graph |
| **Cenários Futuros** | Scenario Planning Panel | 3 cenários × 3 horizontes + Business Impact |
| **Contexto Cultural** | Contextual Intelligence Panel (4 tabs) | Narrativas + Território + Temporal + Semântico |
| **Monitoramento ML** | ML Predictions + Topics + Tab 4 (Drift) | Status modelos + Topics LDA + Drift detection |

---

## 📊 MAPEAMENTO COMPLETO: 11 PAINÉIS → 4 ABAS

### **TABELA DETALHADA:**

| # | Painel/Tab Origem | Destino Final | Prioridade CMO | Justificativa |
|---|-------------------|---------------|----------------|---------------|
| 1 | **Signal Velocity** | [Dashboard] KPI Cards | ⭐⭐⭐ CRÍTICO | Responde: "Quão rápido?" |
| 2 | **System Tensions** | **UNIFICADO** com Real | ⭐⭐ ALTA | Redundância eliminada |
| 3 | **Real Tensions** | [Sinais] Seção 2 | ⭐⭐⭐ CRÍTICO | Responde: "Que conflitos?" |
| 4 | **Forecasting** | [Sinais] Seção 3 | ⭐⭐⭐ CRÍTICO | Responde: "O que vem?" |
| 5 | **Topics** | [Analytics/Monitor ML] | ⭐ BAIXA | Muito técnico para CMO |
| 6 | **Emerging Audiences** | [Sinais] Seção 4 | ⭐⭐ ALTA | Responde: "Quem são?" |
| 7 | **Autonomous Decisions** | [Analytics/Expander] | ⭐ BAIXA | Técnico - collapsed |
| 8 | **ML Predictions** | [Analytics/Monitor ML] | ⭐⭐ MÉDIA | Contextualizado com status |
| 9 | **Temporal Validation** | [Analytics/Expander] | ⭐ BAIXA | Métrica interna - collapsed |
| 10 | **Scenario Planning** | [Analytics/Cenários] | ⭐⭐⭐ CRÍTICO | Responde: "E se?" |
| 11 | **Contextual Intel.** | [Analytics/Contexto] | ⭐⭐⭐ CRÍTICO | Responde: "Por quê?" |
| 12 | **Tab 1: Sinais Det.** | [Projetos] + [Sinais] | ⭐⭐⭐ CRÍTICO | Lista + Top 5 integrados |
| 13 | **Tab 2: Análise Temp.** | [Analytics/Temporal] | ⭐⭐ MÉDIA | Timeline visual |
| 14 | **Tab 3: Mapa Tensões** | [Analytics/Temporal] | ⭐⭐ MÉDIA | Network graph |
| 15 | **Tab 4: Monitor ML** | [Analytics/Monitor ML] | ⭐ BAIXA | Para time técnico |

---

## 🎓 TUTORIAL EM 3 PASSOS (Simplificado)

### **PASSO 1: O QUE PESQUISAR** (30 segundos)
```
┌────────────────────────────────────────────────┐
│ 🎯 Defina sua pesquisa                         │
│                                                │
│ ✅ Nome do usuário: Jordan Silva               │
│ ✅ Marca/Tema: Copa do Mundo 2026              │
│ ✅ Segmento: Alimentação e Bebidas             │
│ ✅ Objetivo: Pesquisa de Mercado               │
│                                                │
│ 💡 DICA: Use templates prontos para começar!   │
│                                                │
│ [Próximo: Ver Contexto →]                      │
└────────────────────────────────────────────────┘
```

### **PASSO 2: VER CONTEXTO & MONITORAR** (60 segundos)
```
┌────────────────────────────────────────────────┐
│ 📊 Análise pronta!                             │
│                                                │
│ Veja os 3 painéis principais:                  │
│ 1️⃣ SINAIS: Top 5 oportunidades detectadas      │
│ 2️⃣ VELOCIDADE: 45% crescendo rápido 🔥         │
│ 3️⃣ TENSÕES: 3 conflitos culturais ativos ⚠️    │
│                                                │
│ 💡 DICA: Clique em cada sinal para ver mais    │
│    detalhes e contexto cultural!               │
│                                                │
│ [Próximo: Análise Profunda →]                  │
└────────────────────────────────────────────────┘
```

### **PASSO 3: ANÁLISE** (90 segundos)
```
┌────────────────────────────────────────────────┐
│ 🔮 Análise Profunda disponível                 │
│                                                │
│ Explore 4 visões:                              │
│ 1️⃣ TEMPORAL: Como evoluiu? (timeline)          │
│ 2️⃣ CENÁRIOS: O que pode acontecer? (3 futuros) │
│ 3️⃣ CONTEXTO: Por quê está acontecendo?         │
│ 4️⃣ MONITOR: Como está a precisão? (ML status)  │
│                                                │
│ 💡 DICA: Compare com outro segmento para ver    │
│    como Entretenimento vs Alimentos reagem!    │
│                                                │
│ [Concluir Tutorial ✓]                          │
└────────────────────────────────────────────────┘
```

**TOTAL TEMPO:** 3 minutos (vs 30min antes)

---

## 🎨 SIDEBAR SIMPLIFICADA (Nova Estrutura)

### **ANTES (V9.1):**
```
├── Problema de Negócio (dropdown)
├── Keywords (text input)
├── Período (date range)
└── Opções de Exibição (slider)
```
**Total:** 4 seções, 118 linhas

### **DEPOIS (V9.2):**
```
┌─────────────────────────────┐
│ 👤 Jordan Silva             │
│ 🍔 Alimentação & Bebidas    │
│ 🎯 Pesquisa de Mercado      │
│ [Editar Perfil]             │
├─────────────────────────────┤
│ 📁 Projetos Ativos (3)      │
│ • Copa do Mundo 2026  ●     │
│ • Black Friday 2026         │
│ • Festas Juninas 2026       │
├─────────────────────────────┤
│ 📅 Período: Últimos 30 dias │
│ [Ajustar]                   │
├─────────────────────────────┤
│ ⚙️ Configurações            │
│ 🆘 Ajuda                    │
│ 🚪 Sair                     │
└─────────────────────────────┘
```
**Total:** 3 seções compactas (~40 linhas estimadas)

**ECONOMIA:** -78 linhas, -1 seção redundante

---

## 📊 COMPARATIVO FINAL: ANTES vs DEPOIS

| Métrica | ANTES (V9.1) | DEPOIS (V9.2) | Delta | Impacto CMO |
|---------|--------------|---------------|-------|-------------|
| **Estrutura** | 11 painéis + 4 tabs | 4 abas superiores | -7 elementos | ✅ Mais claro |
| **Linhas Visíveis** | 1,433 (11 painéis) | ~600 (cards + 5 seções) | **-58%** | ✅ Menos scroll |
| **Redundâncias** | 2 (tensões duplicadas) | 0 | **-100%** | ✅ Sem confusão |
| **Time-to-Insight** | >30min | <3min | **-90%** | ✅ Decisão rápida |
| **Personalização Visível** | 0% (invisível) | 100% (header + perfil) | **+100%** | ✅ Diferencial claro |
| **Tutorial** | Nenhum | 3 passos (3min) | **+3min** | ✅ Onboarding |
| **Hierarquia** | Plana (tudo igual) | 3 níveis (crítico/alta/baixa) | **+3 níveis** | ✅ Priorização |
| **Sidebar** | 118 linhas, 4 seções | ~40 linhas, 3 seções | **-66%** | ✅ Mais limpo |
| **Context Enricher** | Tab 4 isolada | Perfil persistente + botão | **+UI** | ✅ Sempre visível |
| **Scroll Necessário** | >3 telas | ~1.5 telas | **-50%** | ✅ Visão completa |

---

## 🚀 PRÓXIMOS PASSOS (Ordem de Execução)

### **SPRINT 1: Unificação & Limpeza** (1-2 dias)
1. ✂️ Unificar tensões (remover `system_tensions_panel`)
2. 📦 Colapsar 3 painéis avançados (Autonomous, Temporal Validation, ML Predictions)
3. ❌ Remover Tab 1 "Sinais Detectados" redundante
4. ❌ Remover `render_advanced_filters` (não implementado)

**Resultado:** -503 linhas visíveis, dashboard mais limpo

### **SPRINT 2: Nova Estrutura** (2-3 dias)
1. 🎨 Criar 4 abas superiores (Dashboard, Projetos, Sinais, Analytics)
2. 🏗️ Migrar painéis para novas abas (seguir tabela de mapeamento)
3. 👤 Criar welcome screen modal (New Project)
4. 📊 Redesenhar sidebar (perfil compacto)

**Resultado:** Estrutura SIGNAL_LAB implementada

### **SPRINT 3: Onboarding** (1-2 dias)
1. 📚 Criar tutorial 3 passos (Pesquisar → Contexto → Análise)
2. 💡 Adicionar tooltips contextuais
3. 🎯 Progress indicator (% dashboard explorado)
4. 🎬 Videos tutoriais curtos (<2min cada)

**Resultado:** Time-to-insight <3min

### **SPRINT 4: Context Enricher UI** (2 dias)
1. 👤 Perfil persistente no header (sempre visível)
2. 🔀 Context comparison modal ("Ver outro segmento")
3. 💳 Context cards aprimorados (antes/depois)
4. 🏷️ Badge "Personalizado para Alimentos" em cada sinal

**Resultado:** Context Enricher 100% visível

**TIMELINE TOTAL:** 6-9 dias para dashboard production-ready

---

**Última atualização:** 6 de fevereiro de 2026, 00:15 UTC-3
