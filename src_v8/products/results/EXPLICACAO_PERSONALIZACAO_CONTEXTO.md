# 🎯 Como Pesquisas são Personalizadas por Contexto (Segmento + Desafio)

## Pergunta Respondida
**"Como 2 usuários pesquisando 'Copa do Mundo 2026' podem ter outputs diferentes?"**
- Usuário A: Alimentos + Pesquisa de Mercado
- Usuário B: Entretenimento + Construção de Marca

---

## 📊 Fluxo de Personalização

```
┌─────────────────────────────────────────────────────────────────────┐
│ FASE 1: COLETA DE DADOS (IGUAIS PARA AMBOS OS USUÁRIOS)           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  APIs Culturais → Termo: "Copa do Mundo 2026"                      │
│                                                                     │
│  ✅ YouTube: 45.000 vídeos                                         │
│     - "Brasileiros já planejam viagens"                            │
│     - "Expectativa alta para seleção"                              │
│                                                                     │
│  ✅ Reddit: 12.000 posts                                           │
│     - Discussões sobre times, viagens, festas                      │
│                                                                     │
│  ✅ Instagram: 230.000 posts                                       │
│     - Fotos, memes, preparativos                                   │
│                                                                     │
│  📊 MÉTRICAS BRUTAS (idênticas):                                   │
│     - Sentiment Stability: 0.82 (alto)                             │
│     - Viralidade: 0.91 (altíssimo)                                 │
│     - Volume: 287.000 menções                                      │
│     - Engagement Rate: 0.12 (mainstream)                           │
│     - Momentum: 78 (crescimento forte)                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
                    Dados brutos IDÊNTICOS
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ FASE 2: CONTEXTUALIZAÇÃO (DIFERENTE PARA CADA USUÁRIO)            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Context Enricher recebe:                                           │
│  1. Dados brutos (iguais)                                          │
│  2. CONTEXTO DO USUÁRIO (diferente)                                │
│                                                                     │
│  ┌──────────────────────┐      ┌──────────────────────┐           │
│  │ 👤 USUÁRIO A         │      │ 👤 USUÁRIO B         │           │
│  ├──────────────────────┤      ├──────────────────────┤           │
│  │ Segmento:            │      │ Segmento:            │           │
│  │ Alimentação/Bebidas  │      │ Entretenimento       │           │
│  │                      │      │                      │           │
│  │ Desafio:             │      │ Desafio:             │           │
│  │ Pesquisa de Mercado  │      │ Construção de Marca  │           │
│  └──────────────────────┘      └──────────────────────┘           │
│           ↓                              ↓                         │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
            Context Enricher aplica adaptações
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ FASE 3: ADAPTAÇÃO POR SEGMENTO (business_segments.py)             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 🍔 ALIMENTOS E BEBIDAS                                      │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │ Cultural Weight: 1.4 (ALTO - tradição forte)               │   │
│  │ Social Importance: 1.5 (MUITO ALTO - convivência)          │   │
│  │ Key Circles: gastronomia_convivencia,                      │   │
│  │              tradicoes_familiares, celebracao_festa         │   │
│  │ Demographic Appeal:                                         │   │
│  │   - 18-24: 1.2x                                            │   │
│  │   - 25-34: 1.4x ⭐ (MAIOR PESO)                            │   │
│  │   - 35-44: 1.3x                                            │   │
│  │   - 45+: 1.1x                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 🎬 ENTRETENIMENTO                                           │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │ Cultural Weight: 1.5 (MUITO ALTO - emoção forte)           │   │
│  │ Social Importance: 1.5 (conexão emocional)                 │   │
│  │ Key Circles: musicalidade_expressao,                       │   │
│  │              alegria_celebracao, criatividade               │   │
│  │ Demographic Appeal:                                         │   │
│  │   - 18-24: 1.5x ⭐ (MAIOR PESO)                            │   │
│  │   - 25-34: 1.4x                                            │   │
│  │   - 35-44: 1.2x                                            │   │
│  │   - 45+: 1.1x                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ FASE 4: ADAPTAÇÃO POR DESAFIO (business_synthesizer.py)           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 🔍 PESQUISA DE MERCADO                                      │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │ Círculos Prioritários:                                      │   │
│  │   1. diversidade_regional (nuances locais)                 │   │
│  │   2. familia_comunidade (valores profundos)                │   │
│  │   3. trabalho_conquista (aspirações)                       │   │
│  │                                                             │   │
│  │ Approach:                                                   │   │
│  │   "Mapear nuances regionais e valores familiares           │   │
│  │    profundos para entender o território"                   │   │
│  │                                                             │   │
│  │ Risk Mitigation:                                            │   │
│  │   "Não generalizar diferentes realidades regionais"        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 🏗️ CONSTRUÇÃO DE MARCA                                      │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │ Círculos Prioritários:                                      │   │
│  │   1. musicalidade_expressao (criatividade)                 │   │
│  │   2. humor_leveza (descontração)                           │   │
│  │   3. festa_celebracao (alegria coletiva)                   │   │
│  │                                                             │   │
│  │ Approach:                                                   │   │
│  │   "Criar identidade baseada na expressividade e            │   │
│  │    alegria genuína brasileira"                             │   │
│  │                                                             │   │
│  │ Risk Mitigation:                                            │   │
│  │   "Evitar estereótipos reducionistas"                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ FASE 5: OUTPUTS PERSONALIZADOS                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ 🍔 ALIMENTOS - Output Personalizado                          │ │
│  ├───────────────────────────────────────────────────────────────┤ │
│  │                                                               │ │
│  │ 📖 CONTEXTO CULTURAL:                                         │ │
│  │    "Copa 2026 como MOMENTO DE CONVIVÊNCIA FAMILIAR.          │ │
│  │     Brasileiros preparam CHURRASCADAS, FESTAS EM CASA,       │ │
│  │     PRODUTOS REGIONAIS. Tradição gastronômica se fortalece   │ │
│  │     em grandes eventos esportivos."                           │ │
│  │                                                               │ │
│  │ 🔄 CÍRCULOS CULTURAIS:                                        │ │
│  │    - diversidade_regional (85%) ⭐                           │ │
│  │    - familia_comunidade (90%) ⭐⭐                           │ │
│  │    - trabalho_conquista (75%)                                │ │
│  │    - gastronomia_convivencia (95%) ⭐⭐⭐                    │ │
│  │                                                               │ │
│  │ 👥 PÚBLICO-ALVO:                                              │ │
│  │    - Famílias 25-44 anos (peso 1.4x)                         │ │
│  │    - Classes B e C                                           │ │
│  │    - Todas as regiões (foco nuances locais)                  │ │
│  │    - Consumidores de produtos regionais                      │ │
│  │                                                               │ │
│  │ 💡 RECOMENDAÇÕES:                                             │ │
│  │    1. Mapear PRATOS TÍPICOS por região                       │ │
│  │    2. Criar KITS FAMILIARES para festas em casa             │ │
│  │    3. Destacar TRADIÇÕES GASTRONÔMICAS regionais             │ │
│  │    4. Parcerias com RESTAURANTES LOCAIS                      │ │
│  │    5. Produtos FÁCEIS DE COMPARTILHAR                        │ │
│  │                                                               │ │
│  │ ⚠️ RISCOS:                                                    │ │
│  │    - Generalizar culinária (Brasil tem 5 regiões distintas)  │ │
│  │    - Ignorar restrições alimentares regionais                │ │
│  │                                                               │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ 🎬 ENTRETENIMENTO - Output Personalizado                     │ │
│  ├───────────────────────────────────────────────────────────────┤ │
│  │                                                               │ │
│  │ 📖 CONTEXTO CULTURAL:                                         │ │
│  │    "Copa 2026 como CELEBRAÇÃO COLETIVA MASSIVA.              │ │
│  │     Brasileiros buscam EXPERIÊNCIAS EMOCIONANTES, MÚSICA,    │ │
│  │     FESTAS, EXPRESSÃO CRIATIVA. Evento que une emoção,       │ │
│  │     arte e identidade nacional."                              │ │
│  │                                                               │ │
│  │ 🔄 CÍRCULOS CULTURAIS:                                        │ │
│  │    - musicalidade_expressao (95%) ⭐⭐⭐                     │ │
│  │    - humor_leveza (90%) ⭐⭐                                 │ │
│  │    - festa_celebracao (100%) ⭐⭐⭐⭐                        │ │
│  │    - paixao_coletiva (85%) ⭐                                │ │
│  │                                                               │ │
│  │ 👥 PÚBLICO-ALVO:                                              │ │
│  │    - Jovens 18-34 anos (peso 1.5x)                           │ │
│  │    - Alta conexão emocional com futebol                      │ │
│  │    - Consumidores de experiências (não produtos)             │ │
│  │    - Ativos em redes sociais                                 │ │
│  │                                                               │ │
│  │ 💡 RECOMENDAÇÕES:                                             │ │
│  │    1. Criar EXPERIÊNCIAS IMERSIVAS (telões, festas)          │ │
│  │    2. Usar MÚSICA BRASILEIRA como identidade                 │ │
│  │    3. Campanhas com HUMOR LEVE e criativo                    │ │
│  │    4. Conteúdo VIRAL e compartilhável                        │ │
│  │    5. Parcerias com ARTISTAS e influencers                   │ │
│  │                                                               │ │
│  │ ⚠️ RISCOS:                                                    │ │
│  │    - Estereotipar cultura brasileira                         │ │
│  │    - Comercializar excessivamente a paixão                   │ │
│  │                                                               │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔑 Elementos que Mudam por Contexto

### 1. Círculos Culturais Priorizados

| Alimentos (Pesquisa) | Entretenimento (Marca) |
|----------------------|------------------------|
| diversidade_regional (85%) | musicalidade_expressao (95%) |
| familia_comunidade (90%) | humor_leveza (90%) |
| trabalho_conquista (75%) | festa_celebracao (100%) |
| gastronomia_convivencia (95%) | paixao_coletiva (85%) |

**Por quê?**
- Alimentos: Foco em **tradição, convivência, valores familiares**
- Entretenimento: Foco em **emoção, expressão, celebração coletiva**

### 2. Público-Alvo Adaptado

| Alimentos | Entretenimento |
|-----------|----------------|
| Famílias 25-44 anos (1.4x peso) | Jovens 18-34 anos (1.5x peso) |
| Classes B e C | Alta conexão emocional |
| Todas as regiões | Consumidores de experiências |
| Produtos regionais | Ativos em redes sociais |

### 3. Recomendações de Ação

| Alimentos | Entretenimento |
|-----------|----------------|
| ✅ Mapear pratos típicos por região | ✅ Criar experiências imersivas |
| ✅ Kits familiares para festas | ✅ Usar música brasileira |
| ✅ Tradições gastronômicas | ✅ Campanhas com humor |
| ✅ Parcerias restaurantes locais | ✅ Conteúdo viral |
| ✅ Produtos compartilháveis | ✅ Parcerias com artistas |

### 4. Focos Estratégicos

**Alimentos (Pesquisa de Mercado):**
- Entender nuances regionais profundamente
- Mapear valores familiares e aspirações
- Identificar tradições gastronômicas específicas

**Entretenimento (Construção de Marca):**
- Valorizar expressividade e criatividade
- Celebrar alegria e espontaneidade
- Criar identidade emocional forte

---

## 💡 Como Isso Funciona na Prática

### Input Único (Dados das APIs):
```json
{
  "termo": "Copa do Mundo 2026",
  "metricas": {
    "sentiment_stability": 0.82,
    "viralidade": 0.91,
    "volume": 287000,
    "engagement_rate": 0.12,
    "momentum": 78
  },
  "texto_api": "Brasileiros já planejam viagens, festas, eventos..."
}
```

### Processo de Adaptação:
```python
# Context Enricher recebe contexto do usuário
context_alimentos = enricher.enrich_signal(
    termo="Copa do Mundo 2026",
    metricas=metricas,
    segmento="Alimentação e Bebidas",    # ← PERSONALIZA
    desafio="pesquisa_mercado"            # ← PERSONALIZA
)

context_entretenimento = enricher.enrich_signal(
    termo="Copa do Mundo 2026",
    metricas=metricas,
    segmento="Entretenimento",            # ← PERSONALIZA
    desafio="construcao_marca"            # ← PERSONALIZA
)
```

### Outputs Personalizados:

**Alimentos:**
- Círculos: familia_comunidade, gastronomia, diversidade_regional
- Público: Famílias 25-44
- Ação: Criar kits regionais, destacar tradições

**Entretenimento:**
- Círculos: musicalidade, festa_celebracao, humor_leveza
- Público: Jovens 18-34
- Ação: Experiências imersivas, música, conteúdo viral

---

## 🎯 Conclusão

### O que é IGUAL:
✅ Dados brutos das APIs (volume, viralidade, sentiment)  
✅ Texto coletado (posts, vídeos, comentários)  
✅ Métricas calculadas (sentiment_stability, momentum)

### O que é DIFERENTE:
🔄 **Círculos culturais priorizados** (família vs emoção)  
🔄 **Público-alvo** (25-44 vs 18-34)  
🔄 **Recomendações de ação** (kits regionais vs experiências)  
🔄 **Narrativa cultural** (convivência vs celebração)  
🔄 **Riscos identificados** (generalização regional vs estereótipos)

---

## 📚 Conceito: Contextual Intelligence

**"Mesmos dados culturais, insights personalizados por contexto de negócio"**

O sistema não cria dados diferentes, mas **interpreta e prioriza** os mesmos dados de formas diferentes baseado em:
1. **Segmento** (Alimentos tem cultural_weight 1.4, Entretenimento 1.5)
2. **Desafio** (Pesquisa ≠ Construção de Marca)
3. **Círculos Culturais** (Mapeamento diferente)
4. **Features XGBoost** (Peso das métricas varia por contexto)

Isso torna a pesquisa **útil e acionável** para cada usuário específico.
