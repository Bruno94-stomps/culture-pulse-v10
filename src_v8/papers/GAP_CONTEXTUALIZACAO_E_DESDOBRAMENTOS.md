"""
🎯 GAP CRÍTICO IDENTIFICADO: Contextualização & Desdobramentos
Análise detalhada + proposta de implementação
Data: 03 de Fevereiro de 2026
"""

================================================================================
🔴 PROBLEMA IDENTIFICADO
================================================================================

**SITUAÇÃO ATUAL:**
O dashboard Futurumã retorna métricas isoladas para queries:

```
Input:  "sustentabilidade afetiva"
Output: Score: 68.5 | Volume: 1,250 | Sentiment: 0.72
```

**POR QUE ISSO É UM PROBLEMA:**

1. **Sem Contexto Cultural**
   - Não sabemos ONDE o sinal está presente (territórios)
   - Não sabemos COM QUÊ ele está conectado (palavras relacionadas)
   - Não sabemos QUAIS tensões ele está provocando

2. **Sem Desdobramentos Temporais**
   - Não vemos COMO o sinal evoluiu (semana a semana)
   - Não identificamos sub-temas emergentes
   - Não prevemos próximos desdobramentos

3. **Sem Comportamentos Observados**
   - Não extraímos AÇÕES que as pessoas estão tomando
   - Não mapeamos rituais/práticas emergentes
   - Não identificamos jornadas de adoção

4. **Decisões Comprometidas**
   - CMO vê "68.5" mas não sabe O QUE FAZER
   - Sem narrativa clara para apresentar ao board
   - Sem contexto para escolher estratégia

================================================================================
📊 COMPARATIVO: Estado Atual vs Proposta
================================================================================

┌─────────────────────────────────────────────────────────────────────────┐
│ DIMENSÃO              │ HOJE                 │ PROPOSTA                │
├─────────────────────────────────────────────────────────────────────────┤
│ Query Response        │ Score + Volume       │ Enriched Intelligence   │
│ Contexto              │ ❌ Ausente           │ ✅ 6 dimensões          │
│ Palavras relacionadas │ ❌ Não mostra        │ ✅ Top 10 + distância   │
│ Territórios           │ ❌ Não identifica    │ ✅ Círculos + regiões   │
│ Tensões               │ ⚠️ Isoladas          │ ✅ Contextualizadas     │
│ Evolução temporal     │ ❌ Snapshot only     │ ✅ 4 semanas tracking   │
│ Comportamentos        │ ❌ Não extrai        │ ✅ Padrões + rituais    │
│ Journey stage         │ ❌ Não identifica    │ ✅ 4 estágios mapeados  │
│ Acionabilidade        │ ⚠️ Baixa             │ ✅ Alta (recomendações) │
└─────────────────────────────────────────────────────────────────────────┘

================================================================================
🎯 PROPOSTA: Contextual Intelligence Engine
================================================================================

## ARQUITETURA

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CONTEXTUAL INTELLIGENCE ENGINE                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  INPUT: Query + WeakSignal data                                    │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 1. SEMANTIC EXPANSION                                        │   │
│  │    - BERTimbau embeddings                                    │   │
│  │    - Cosine similarity top-k                                 │   │
│  │    - Semantic network graph                                  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                           ↓                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 2. CULTURAL TERRITORY MAPPING                                │   │
│  │    - Círculos culturais (16 categorias)                      │   │
│  │    - Regiões geográficas (5 BR)                              │   │
│  │    - Plataformas (8 fontes)                                  │   │
│  │    - Penetração quantificada                                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                           ↓                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 3. CONTEXTUALIZED TENSIONS                                   │   │
│  │    - Tensões detectadas + query                              │   │
│  │    - Intensidade no contexto                                 │   │
│  │    - Tensões emergentes (não mapeadas)                       │   │
│  │    - Impacto no momentum                                     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                           ↓                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 4. TEMPORAL UNFOLDING                                        │   │
│  │    - Week-over-week tracking                                 │   │
│  │    - Sub-temas emergentes                                    │   │
│  │    - Narrative shifts                                        │   │
│  │    - Próximos desdobramentos (predição)                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                           ↓                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 5. BEHAVIORAL PATTERNS                                       │   │
│  │    - Ações mencionadas (verbos)                              │   │
│  │    - Rituais/práticas                                        │   │
│  │    - Mudanças de comportamento                               │   │
│  │    - Frequência + contexto                                   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                           ↓                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 6. JOURNEY MAPPING                                           │   │
│  │    - Awareness → Interest → Adoption → Advocacy              │   │
│  │    - Estágio atual identificado                              │   │
│  │    - Próximos estágios previstos                             │   │
│  │    - Recomendações por estágio                               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  OUTPUT: EnrichedSignal (contexto completo)                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

================================================================================
🔧 IMPLEMENTAÇÃO DETALHADA
================================================================================

## 1. SEMANTIC EXPANSION (Palavras Relacionadas)

**Objetivo:** Encontrar conceitos semanticamente próximos à query

**Técnica:**
- Usar BERTimbau embeddings (768 dims)
- Calcular cosine similarity com corpus de termos culturais
- Ranquear por distância semântica

**Implementação:**
```python
# core/contextual_intelligence_engine.py

class SemanticExpander:
    def __init__(self, bertimbau_model):
        self.model = bertimbau_model
        self.cultural_corpus = self._load_cultural_terms()
    
    def find_related_concepts(
        self, 
        query: str, 
        top_k: int = 10,
        min_similarity: float = 0.7
    ) -> List[RelatedConcept]:
        """
        Encontra conceitos relacionados semanticamente
        
        Returns:
            [
                RelatedConcept(
                    term='co-living',
                    similarity=0.82,
                    cultural_circle='Comunidade',
                    frequency=450
                ),
                ...
            ]
        """
        query_embedding = self.model.encode(query)
        
        similarities = []
        for term, term_embedding in self.cultural_corpus.items():
            sim = cosine_similarity(query_embedding, term_embedding)
            if sim >= min_similarity:
                similarities.append({
                    'term': term,
                    'similarity': sim,
                    'cultural_circle': self._get_circle(term),
                    'frequency': self._get_frequency(term)
                })
        
        # Ranquear por similaridade
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        return [RelatedConcept(**s) for s in similarities[:top_k]]
```

**Output Esperado:**
```
Query: "sustentabilidade afetiva"

🔗 Conceitos Relacionados:
1. co-living (0.82) - Comunidade - 450 menções
2. economia do cuidado (0.78) - Bem-estar - 320 menções
3. redes de apoio (0.75) - Comunidade - 580 menções
4. burnout emocional (0.72) - Saúde - 410 menções
5. espaços seguros (0.71) - Pertencimento - 390 menções
```

---

## 2. CULTURAL TERRITORY MAPPING

**Objetivo:** Identificar onde o sinal está presente

**Dimensões:**
- **Círculos Culturais:** 16 categorias (Bem-estar, Comunidade, etc)
- **Regiões Geográficas:** 5 BR (Norte, Nordeste, Centro-Oeste, Sudeste, Sul)
- **Plataformas:** 8 fontes (YouTube, Reddit, Instagram, etc)
- **Penetração:** % de presença em cada território

**Implementação:**
```python
class CulturalTerritoryMapper:
    def map_territories(self, signal_data: Dict) -> TerritoryMap:
        """
        Mapeia territórios onde o sinal está presente
        
        Returns:
            TerritoryMap(
                cultural_circles={
                    'Bem-estar': 45%,
                    'Comunidade': 30%,
                    'Saúde Mental': 25%
                },
                regions={
                    'Sudeste': 50%,
                    'Sul': 30%,
                    'outros': 20%
                },
                platforms={
                    'Instagram': 60%,
                    'Reddit': 25%,
                    'YouTube': 15%
                }
            )
        """
        # Agregar contextos culturais
        circles = self._aggregate_cultural_circles(signal_data)
        
        # Analisar metadados geográficos
        regions = self._extract_regional_presence(signal_data)
        
        # Distribuição por plataforma
        platforms = self._calculate_platform_distribution(signal_data)
        
        return TerritoryMap(
            cultural_circles=circles,
            regions=regions,
            platforms=platforms,
            penetration_score=self._calculate_penetration(circles, regions)
        )
```

**Output Esperado:**
```
📍 Territórios Culturais

Círculos Dominantes:
├─ Bem-estar (45%)         ████████████████████
├─ Comunidade (30%)        ████████████
└─ Saúde Mental (25%)      ██████████

Regiões:
├─ Sudeste (50%)           ██████████████████████
├─ Sul (30%)               ████████████
└─ Outros (20%)            ████████

Plataformas:
├─ Instagram (60%)         ████████████████████████
├─ Reddit (25%)            ██████████
└─ YouTube (15%)           ██████
```

---

## 3. CONTEXTUALIZED TENSIONS

**Objetivo:** Mostrar tensões conectadas à query específica

**Técnica:**
- Usar TensionDetectionEngine existente
- Filtrar tensões relevantes para a query
- Calcular intensidade no contexto
- Identificar tensões emergentes

**Implementação:**
```python
class ContextualizedTensionAnalyzer:
    def analyze_tensions_in_context(
        self, 
        query: str, 
        signal_data: Dict
    ) -> List[ContextualTension]:
        """
        Analisa tensões no contexto da query
        
        Returns:
            [
                ContextualTension(
                    tension='Individualismo vs Coletivismo',
                    intensity=7.5,
                    relevance_to_query=0.89,
                    evidence=['mencao1', 'mencao2'],
                    impact_on_momentum=+12%
                ),
                ...
            ]
        """
        # Detectar todas as tensões
        all_tensions = self.tension_engine.detect(signal_data)
        
        # Filtrar por relevância à query
        query_embedding = self.model.encode(query)
        relevant_tensions = []
        
        for tension in all_tensions:
            tension_embedding = self.model.encode(tension.description)
            relevance = cosine_similarity(query_embedding, tension_embedding)
            
            if relevance > 0.6:  # Threshold de relevância
                relevant_tensions.append(
                    ContextualTension(
                        tension=tension.name,
                        intensity=tension.intensity,
                        relevance_to_query=relevance,
                        evidence=self._extract_evidence(tension, signal_data),
                        impact_on_momentum=self._calculate_impact(tension)
                    )
                )
        
        return sorted(relevant_tensions, key=lambda t: t.relevance_to_query, reverse=True)
```

**Output Esperado:**
```
⚡ Tensões no Contexto

1. Individualismo vs Coletivismo
   Intensidade: 7.5/10
   Relevância: 89%
   Impacto no momentum: +12%
   
   Evidências:
   - "cansei de cuidar sozinha da minha saúde mental"
   - "a gente precisa voltar a ser comunidade"
   - "solidão coletiva é real"

2. Performance vs Autenticidade
   Intensidade: 6.8/10
   Relevância: 82%
   Impacto no momentum: +8%
   
   Evidências:
   - "parar de fingir que está tudo bem"
   - "vulnerabilidade como força"
```

---

## 4. TEMPORAL UNFOLDING (Desdobramentos)

**Objetivo:** Tracking da evolução temporal do sinal

**Técnica:**
- Coletar dados históricos (4-8 semanas)
- Identificar sub-temas emergentes por semana
- Detectar narrative shifts
- Prever próximos desdobramentos

**Implementação:**
```python
class TemporalUnfoldingTracker:
    def track_evolution(
        self, 
        query: str, 
        weeks: int = 4
    ) -> TemporalEvolution:
        """
        Tracking de evolução temporal
        
        Returns:
            TemporalEvolution(
                weeks=[
                    WeekSnapshot(
                        week_number=1,
                        volume=850,
                        momentum_delta=+45%,
                        emerging_themes=['espaços seguros', 'check-in emocional'],
                        narrative_shift='Individual → Coletivo'
                    ),
                    ...
                ],
                predicted_next_steps=['comunidades intencionais', 'rituais compartilhados']
            )
        """
        historical_data = self._fetch_historical_data(query, weeks)
        
        week_snapshots = []
        for week_data in historical_data:
            # Extrair temas emergentes (TF-IDF)
            emerging_themes = self._extract_emerging_themes(week_data)
            
            # Detectar mudanças de narrativa
            narrative_shift = self._detect_narrative_shift(
                week_data, 
                previous_week=week_snapshots[-1] if week_snapshots else None
            )
            
            week_snapshots.append(
                WeekSnapshot(
                    week_number=len(week_snapshots) + 1,
                    volume=week_data['volume'],
                    momentum_delta=self._calculate_delta(week_data),
                    emerging_themes=emerging_themes,
                    narrative_shift=narrative_shift
                )
            )
        
        # Prever próximos desdobramentos
        predicted_next = self._predict_next_steps(week_snapshots)
        
        return TemporalEvolution(
            weeks=week_snapshots,
            predicted_next_steps=predicted_next
        )
```

**Output Esperado:**
```
📈 Desdobramentos Temporais (4 semanas)

Semana 1:
  Volume: 850 (+45% vs baseline)
  Temas emergentes: espaços seguros, check-in emocional
  Shift narrativo: Individual → Coletivo

Semana 2:
  Volume: 1,050 (+23% vs S1)
  Temas emergentes: limites saudáveis, micro-comunidades
  Shift narrativo: Reativo → Proativo

Semana 3:
  Volume: 1,180 (+12% vs S2)
  Temas emergentes: rituais de cuidado, vulnerabilidade
  Shift narrativo: Teórico → Prático

Semana 4:
  Volume: 1,250 (+6% vs S3)
  Temas emergentes: ação coletiva, espaços físicos
  Shift narrativo: Digital → Híbrido

🔮 Próximos desdobramentos previstos:
  - Comunidades intencionais (prob: 78%)
  - Rituais compartilhados (prob: 65%)
  - Co-housing afetivo (prob: 52%)
```

---

## 5. BEHAVIORAL PATTERNS

**Objetivo:** Extrair ações e práticas mencionadas

**Técnica:**
- NLP para extrair verbos de ação
- Identificar rituais/práticas
- Quantificar frequência
- Mapear mudanças comportamentais

**Implementação:**
```python
class BehavioralPatternExtractor:
    def extract_behaviors(self, signal_data: Dict) -> List[BehaviorPattern]:
        """
        Extrai padrões comportamentais
        
        Returns:
            [
                BehaviorPattern(
                    action='criar grupos de apoio',
                    frequency=45,
                    context='15-30 pessoas, WhatsApp',
                    change_type='novo hábito',
                    adoption_stage='early adopters'
                ),
                ...
            ]
        """
        texts = self._get_all_mentions(signal_data)
        
        behaviors = []
        for text in texts:
            # Extrair verbos de ação (spaCy)
            actions = self._extract_action_verbs(text)
            
            for action in actions:
                # Identificar contexto
                context = self._extract_context(text, action)
                
                # Classificar tipo de mudança
                change_type = self._classify_change_type(action, context)
                
                # Identificar estágio de adoção
                adoption_stage = self._identify_adoption_stage(action)
                
                behaviors.append(
                    BehaviorPattern(
                        action=action,
                        frequency=self._count_frequency(action, texts),
                        context=context,
                        change_type=change_type,
                        adoption_stage=adoption_stage
                    )
                )
        
        return self._deduplicate_and_rank(behaviors)
```

**Output Esperado:**
```
🎯 Comportamentos Observados

1. Criar grupos de apoio micro (45 menções)
   Contexto: 15-30 pessoas, WhatsApp/Telegram
   Tipo: Novo hábito
   Estágio: Early adopters

2. Rituais de check-in emocional (38 menções)
   Contexto: Manhã/noite, 5-10 min
   Tipo: Rotina diária
   Estágio: Early majority

3. Compartilhar vulnerabilidades (32 menções)
   Contexto: Círculos de confiança, presencial
   Tipo: Mudança de mindset
   Estágio: Innovators

4. Rejeitar "cultura da correria" (28 menções)
   Contexto: Trabalho/carreira
   Tipo: Abandono de prática
   Estágio: Early adopters
```

---

## 6. JOURNEY MAPPING

**Objetivo:** Identificar estágio de adoção do sinal

**Etapas:**
1. **Awareness** (Consciência)
2. **Interest** (Interesse)
3. **Adoption** (Adoção)
4. **Advocacy** (Defesa/Evangelização)

**Implementação:**
```python
class JourneyMapper:
    def identify_stage(self, signal_data: Dict) -> JourneyStage:
        """
        Identifica estágio da jornada de adoção
        
        Returns:
            JourneyStage(
                current='Interest',
                confidence=0.78,
                indicators=[
                    'Volume crescendo (+45%)',
                    'Discussões sobre "como fazer"',
                    'Primeiras experimentações'
                ],
                next_stage='Adoption',
                time_to_next='4-6 semanas',
                recommended_actions=[...]
            )
        """
        # Analisar indicadores por estágio
        awareness_score = self._calculate_awareness(signal_data)
        interest_score = self._calculate_interest(signal_data)
        adoption_score = self._calculate_adoption(signal_data)
        advocacy_score = self._calculate_advocacy(signal_data)
        
        # Identificar estágio atual (maior score)
        scores = {
            'Awareness': awareness_score,
            'Interest': interest_score,
            'Adoption': adoption_score,
            'Advocacy': advocacy_score
        }
        
        current_stage = max(scores, key=scores.get)
        confidence = scores[current_stage]
        
        # Identificar indicadores
        indicators = self._extract_stage_indicators(current_stage, signal_data)
        
        # Prever próximo estágio
        next_stage = self._predict_next_stage(current_stage, signal_data)
        time_to_next = self._estimate_transition_time(current_stage, next_stage)
        
        # Gerar recomendações
        recommendations = self._generate_stage_recommendations(current_stage)
        
        return JourneyStage(
            current=current_stage,
            confidence=confidence,
            indicators=indicators,
            next_stage=next_stage,
            time_to_next=time_to_next,
            recommended_actions=recommendations
        )
```

**Output Esperado:**
```
🗺️ Journey Mapping

Estágio Atual: INTEREST (78% confiança)

Indicadores:
✅ Volume crescendo consistentemente (+45% em 4 semanas)
✅ Discussões sobre "como fazer" aumentaram 3x
✅ Primeiras experimentações relatadas (grupos de apoio)
✅ Busca por frameworks/metodologias

Próximo Estágio: ADOPTION (previsto em 4-6 semanas)

Recomendações para acelerar transição:
1. Criar guias práticos de implementação
2. Facilitar conexões entre interessados
3. Destacar casos de sucesso (early adopters)
4. Oferecer suporte/ferramentas para experimentação
5. Reduzir barreiras de entrada
```

================================================================================
📊 DASHBOARD PROPOSTO: Painel de Contextualização
================================================================================

**Novo Componente Visual:**

```python
def render_contextual_intelligence_panel(query: str, weak_signals: List[WeakSignal]):
    """
    Painel completo de contextualização e desdobramentos
    """
    st.markdown("### 🧠 Contextual Intelligence")
    st.caption(f"Análise profunda para: **{query}**")
    
    # Inicializar engine
    engine = ContextualIntelligenceEngine()
    enriched = engine.enrich_signal(query, weak_signals)
    
    # === TABS ===
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔗 Relacionados",
        "📍 Territórios", 
        "⚡ Tensões",
        "📈 Evolução",
        "🎯 Comportamentos",
        "🗺️ Jornada"
    ])
    
    # TAB 1: Semantic Expansion
    with tab1:
        st.markdown("#### Conceitos Relacionados")
        for concept in enriched.related_concepts:
            st.markdown(f"**{concept.term}** (similaridade: {concept.similarity:.2f})")
            st.caption(f"📊 {concept.frequency} menções | 🎨 {concept.cultural_circle}")
    
    # TAB 2: Territory Mapping
    with tab2:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("##### Círculos Culturais")
            # Gráfico de barras horizontais
            
        with col2:
            st.markdown("##### Regiões")
            # Mapa do Brasil
            
        with col3:
            st.markdown("##### Plataformas")
            # Gráfico de pizza
    
    # TAB 3: Contextualized Tensions
    with tab3:
        for tension in enriched.tensions:
            with st.expander(f"{tension.tension} (intensidade: {tension.intensity}/10)"):
                st.progress(tension.intensity / 10)
                st.markdown(f"**Relevância:** {tension.relevance_to_query:.0%}")
                st.markdown(f"**Impacto no momentum:** {tension.impact_on_momentum:+.1%}")
                st.markdown("**Evidências:**")
                for evidence in tension.evidence[:3]:
                    st.caption(f"💬 {evidence}")
    
    # TAB 4: Temporal Unfolding
    with tab4:
        # Timeline visual com Plotly
        fig = go.Figure()
        for week in enriched.evolution.weeks:
            # Adicionar pontos e linhas
            pass
        st.plotly_chart(fig)
        
        # Próximos desdobramentos
        st.markdown("#### 🔮 Próximos Desdobramentos Previstos")
        for step in enriched.evolution.predicted_next_steps:
            st.info(f"• {step}")
    
    # TAB 5: Behavioral Patterns
    with tab5:
        for behavior in enriched.behaviors:
            st.markdown(f"**{behavior.action}** ({behavior.frequency} menções)")
            st.caption(f"Contexto: {behavior.context}")
            st.caption(f"Tipo: {behavior.change_type} | Estágio: {behavior.adoption_stage}")
    
    # TAB 6: Journey Mapping
    with tab6:
        journey = enriched.journey_stage
        
        # Progress bar dos estágios
        stages = ['Awareness', 'Interest', 'Adoption', 'Advocacy']
        current_idx = stages.index(journey.current)
        
        cols = st.columns(4)
        for idx, stage in enumerate(stages):
            with cols[idx]:
                if idx < current_idx:
                    st.success(f"✅ {stage}")
                elif idx == current_idx:
                    st.info(f"🔵 {stage}")
                else:
                    st.text(f"⚪ {stage}")
        
        # Indicadores e recomendações
        st.markdown("##### Indicadores")
        for indicator in journey.indicators:
            st.markdown(f"✅ {indicator}")
        
        st.markdown("##### Recomendações")
        for action in journey.recommended_actions:
            st.markdown(f"🎯 {action}")
```

================================================================================
🎯 PRIORIZAÇÃO & ROADMAP
================================================================================

**FASE 1 (Semana 1-2): Fundação**
   1. ✅ Criar `ContextualIntelligenceEngine` base
   2. ✅ Implementar `SemanticExpander` (BERTimbau)
   3. ✅ Implementar `CulturalTerritoryMapper`
   4. ✅ Testes unitários das 2 features

**FASE 2 (Semana 3-4): Tensões & Evolução**
   5. ✅ Implementar `ContextualizedTensionAnalyzer`
   6. ✅ Implementar `TemporalUnfoldingTracker`
   7. ✅ Armazenar histórico (4-8 semanas)
   8. ✅ Testes de integração

**FASE 3 (Semana 5-6): Comportamentos & Jornada**
   9. ✅ Implementar `BehavioralPatternExtractor` (spaCy)
   10. ✅ Implementar `JourneyMapper`
   11. ✅ Dashboard: render_contextual_intelligence_panel()
   12. ✅ Testes end-to-end

**FASE 4 (Semana 7-8): Validação & Refinamento**
   13. ✅ Coletar feedback de 5-10 usuários
   14. ✅ Ajustar thresholds e algoritmos
   15. ✅ Otimizar performance
   16. ✅ Documentação completa

================================================================================
📊 IMPACTO ESPERADO
================================================================================

**SCORE ACADÊMICO:**
   - Antes: 98.4%
   - Depois: 100.4% (+2.0%)
   - Justificativa: Feature além dos papers (inovação)

**VALOR DE NEGÓCIO:**
   ✅ Decisões mais informadas (contexto completo)
   ✅ Narrativas ricas para stakeholders
   ✅ Acionabilidade aumentada (recomendações específicas)
   ✅ Diferencial competitivo único no mercado
   ✅ Redução de tempo de análise (automatizado)

**CONFORMIDADE ACADÊMICA:**
   ✅ Atende "visão holística" (Mühlroth & Grottke, 2018)
   ✅ Supera "snapshot data" criticado por Gutsche (2018)
   ✅ Integra temporal tracking (todos os papers)

================================================================================
🚀 PRÓXIMOS PASSOS IMEDIATOS
================================================================================

1. **Aprovar proposta** ✅
2. **Criar issue no GitHub** (trackear implementação)
3. **Implementar FASE 1** (Semantic Expansion + Territory Mapping)
4. **Testar com 10 queries reais**
5. **Iterar baseado em feedback**

================================================================================
