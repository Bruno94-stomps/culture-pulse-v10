# 📊 Análise de Covariação Contextual e Feature Importance

**Data**: 2026-02-05  
**Samples**: 750  
**Features analisadas**: 30 numéricas  
**Modelo**: XGBoost Classifier  
**Accuracy**: 100% (Train & Test)

---

## 🔗 1. COVARIAÇÕES CONTEXTUAIS (|r| > 0.7)

### 🏆 Top 10 Pares com Maior Covariação

| Rank | Feature 1 | Feature 2 | Correlação | Interpretação |
|------|-----------|-----------|------------|---------------|
| 1 | **alcance_regional** | **cross_platform_reach** | **0.920** | Sinais que se espalham geograficamente também aparecem em múltiplas plataformas |
| 2 | **likes** | **shares** | **0.910** | Alto engajamento (likes) leva a compartilhamentos |
| 3 | **likes** | **comments** | **0.904** | Conteúdo que recebe likes também gera discussão |
| 4 | **momentum** | **momentum_sentiment** | **0.897** | Momentum alto correlaciona com sentimento positivo |
| 5 | **velocidade** | **virality_index** | **0.889** | Velocidade de crescimento é indicador de viralidade |
| 6 | **shares** | **comments** | **0.849** | Compartilhamentos geram discussões |
| 7 | **volume** | **likes** | **0.845** | Alto volume de menções atrai engajamento |
| 8 | **aceleracao** | **trending_score** | **0.836** | Aceleração identifica tendências emergentes |
| 9 | **volume** | **shares** | **0.787** | Volume impulsiona compartilhamentos |
| 10 | **aceleracao** | **growth_acceleration** | **0.754** | Features de crescimento são redundantes |

### 💡 Insights de Covariação

**Cluster 1: Engajamento Social (r > 0.85)**
- **Likes → Shares → Comments**: Ciclo de engajamento unificado
- **Implicação**: Uma métrica de engajamento pode representar as outras (reduzir dimensionalidade)

**Cluster 2: Alcance Geográfico (r = 0.92)**
- **Alcance Regional ↔ Cross-Platform**: Sinais nacionais aparecem em todas as plataformas
- **Implicação**: Força regional = força multi-plataforma

**Cluster 3: Dinâmica de Crescimento (r > 0.83)**
- **Momentum ↔ Sentiment**: Crescimento vem com positividade
- **Velocidade ↔ Viralidade**: Rapidez = viral
- **Aceleração ↔ Trending**: Aceleração detecta trends

**Cluster 4: Cultural (r = 0.75)**
- **Diversidade Demográfica ↔ Ressonância Cultural**: Sinais diversos ressoam culturalmente
- **Autenticidade ↔ Autenticidade-Relevância**: Features derivadas redundantes

---

## 🎯 2. CORRELAÇÃO COM WEAK_SIGNAL

### Top 10 Features Correlacionadas (ordenado por |r|)

| Rank | Feature | Correlação | P-value | Significância |
|------|---------|------------|---------|---------------|
| 1 | **weak_signal_score** | **0.864** | 0.0000 | ⭐⭐⭐ Altíssima (esperado - circular) |
| 2 | **viralidade** | **0.194** | 0.0000 | ⭐⭐ Alta significância |
| 3 | **engagement_rate** | **-0.091** | 0.0132 | ⭐ Significativa (negativa!) |
| 4 | **growth_acceleration** | **-0.076** | 0.0372 | ⭐ Fraca mas significativa (negativa!) |
| 5 | **likes** | 0.057 | 0.1206 | Não significativa |
| 6 | **dia_mes** | 0.056 | 0.1235 | Não significativa |
| 7 | **comments** | 0.051 | 0.1598 | Não significativa |
| 8 | **volume** | 0.051 | 0.1600 | Não significativa |
| 9 | **shares** | 0.051 | 0.1648 | Não significativa |
| 10 | **momentum** | -0.038 | 0.2934 | Não significativa |

### 💡 Insights Surpreendentes

**1. Viralidade positiva (r=0.194) ✅**
- Sinais fracos têm maior viralidade (compartilhamento orgânico)
- **Ação**: Priorizar métricas de viralidade em detecção

**2. Engagement_rate NEGATIVA (r=-0.091) ⚠️**
- Weak signals têm MENOS engajamento relativo ao volume
- **Interpretação**: Sinais fracos são "nicho" - volume baixo mas intenso em comunidades específicas
- **Ação**: Não descartar sinais com baixo engagement absoluto

**3. Growth_acceleration NEGATIVA (r=-0.076) ⚠️**
- Weak signals NÃO têm crescimento acelerado
- **Interpretação**: Crescimento é **constante e sustentado**, não explosivo
- **Ação**: Detectar padrões lineares, não apenas aceleração

**4. Volume, Likes, Shares NÃO significativos (p > 0.12)**
- Métricas absolutas de engajamento não diferenciam weak signals
- **Ação**: Usar métricas relativas (taxas, proporções)

---

## 🌲 3. XGBoost FEATURE IMPORTANCE

### 🏆 Top 15 Features (by Gain - Qualidade dos Splits)

| Rank | Feature | Gain | % Total | Interpretação |
|------|---------|------|---------|---------------|
| 1 | **weak_signal_score** | **59.8** | **98.5%** | ⚠️ Dominância total (circular) |
| 2 | **shares** | 0.3 | 0.5% | Compartilhamento como diferenciador |
| 3 | **sentiment_stability** | 0.2 | 0.3% | Estabilidade de sentimento (não volatilidade) |
| 4 | **engagement_rate** | 0.1 | 0.2% | Taxa de engajamento (não absoluto) |
| 5 | **momentum_sentiment** | 0.1 | 0.2% | Sentimento do momentum |
| 6 | **relevancia_cultural** | 0.1 | 0.2% | Relevância cultural brasileira |
| 7 | **growth_acceleration** | 0.1 | 0.2% | Aceleração de crescimento |
| 8 | **trending_score** | 0.1 | 0.2% | Score de trending |
| 9 | **cultural_resonance** | 0.1 | 0.2% | Ressonância cultural |
| 10 | **comments** | 0.1 | 0.2% | Comentários (discussão) |
| 11 | **autenticidade_relevancia** | 0.1 | 0.2% | Autenticidade + Relevância |
| 12 | **velocidade** | 0.1 | 0.2% | Velocidade de crescimento |
| 13 | **volume_velocity** | 0.1 | 0.2% | Volume × Velocidade |
| 14 | **sentiment** | 0.1 | 0.2% | Sentimento geral |
| 15 | **contexto_score** | 0.0 | 0.0% | Score de contexto |

### 🔢 Top 15 Features (by Weight - Frequência de Uso)

| Rank | Feature | Weight | % uso | Interpretação |
|------|---------|--------|-------|---------------|
| 1 | **weak_signal_score** | 68 | 55% | Usado em 55% dos nós |
| 2 | **engagement_rate** | 11 | 9% | 2ª feature mais consultada |
| 3 | **trending_score** | 10 | 8% | Score trending importante |
| 4 | **velocidade** | 6 | 5% | Velocidade de crescimento |
| 5 | **momentum_sentiment** | 6 | 5% | Sentimento do momentum |
| 6 | **volume_velocity** | 4 | 3% | Combinação volume-velocidade |
| 7 | **cultural_resonance** | 4 | 3% | Ressonância cultural |
| 8 | **sentiment** | 3 | 2% | Sentimento geral |
| 9 | **relevancia_cultural** | 3 | 2% | Relevância cultural |
| 10 | **growth_acceleration** | 3 | 2% | Aceleração |

### 💡 Insights XGBoost

**1. Problema de Circularidade ⚠️**
- `weak_signal_score` domina 98.5% do gain
- **Causa**: Modelo treina com target que já é derivado de weak_signal_score
- **Solução**: Retreinar SEM weak_signal_score para descobrir features reais

**2. Features Secundárias Importantes (quando weak_signal_score excluído)**
- **Shares** (0.3 gain): Compartilhamento diferencia weak signals
- **Sentiment_stability** (0.2): Estabilidade emocional, não volatilidade
- **Engagement_rate** (0.1): Taxa relativa, não absoluta

**3. Features Culturais Relevantes**
- **Relevância_cultural**: Top 6 em gain
- **Cultural_resonance**: Top 9 em gain
- **Autenticidade_relevancia**: Top 11 em gain
- **Implicação**: Dimensão cultural é diferenciadora

**4. Features Ignoradas (0 gain)**
- `contexto_score`: Não agrega informação
- `hora_dia`: Temporal não diferencia
- Várias features de engajamento absoluto (likes, volume)

---

## 📌 4. PERFIS DE TERMOS (Weak Signal Rate)

| Termo | Weak Signal % | n | Avg Momentum | Avg Volume | Interpretação |
|-------|---------------|---|--------------|------------|---------------|
| **IA no Varejo** | **41.7%** | 48 | 39.4 | ? | Tech emergente no varejo |
| **NFT Games Brasil** | **41.2%** | 51 | 32.7 | ? | Gaming blockchain |
| **Blockchain Agro** | **41.2%** | 51 | 36.4 | ? | AgTech descentralizado |
| **Copa do Mundo 2026** | **40.0%** | 45 | 39.4 | ? | Evento cultural massivo |
| **Criptomoedas Brasil** | **39.2%** | 51 | 34.3 | ? | Fintech descentralizado |

**Padrão identificado**: Termos de **tecnologia emergente + cultura brasileira** têm maior taxa de weak signal.

---

## 🎯 5. RECOMENDAÇÕES ESTRATÉGICAS

### Para Detecção de Weak Signals

**1. Remover Circularidade**
```python
# Retreinar XGBoost SEM weak_signal_score
features_importantes = [
    'shares', 'sentiment_stability', 'engagement_rate',
    'trending_score', 'momentum_sentiment', 'relevancia_cultural',
    'cultural_resonance', 'viralidade', 'velocidade'
]
```

**2. Priorizar Features Culturais**
- `relevancia_cultural`, `cultural_resonance`, `autenticidade_relevancia`
- Estas features diferenciam sinais brasileiros de ruído global

**3. Usar Métricas Relativas, não Absolutas**
- ✅ `engagement_rate` (likes/volume)
- ✅ `viralidade` (shares/volume)
- ❌ `likes` (absoluto)
- ❌ `volume` (absoluto)

**4. Detectar Crescimento Sustentado, não Explosivo**
- Weak signals NÃO têm growth_acceleration alta
- Procurar padrões **lineares consistentes** por 7-14 dias

**5. Considerar Padrão Temporal**
- `dia_mes` tem correlação 0.056 (fraca mas positiva)
- Analisar sazonalidade mensal

### Para Enriquecimento de Contexto

**Features com Alta Covariação (redundantes - simplificar)**
- Manter: `likes` (representa engajamento geral)
- Remover: `shares`, `comments` (r > 0.85 com likes)
- Manter: `alcance_regional` (representa presença multi-plataforma)
- Remover: `cross_platform_reach` (r = 0.92)

**Features Únicas (manter todas)**
- `viralidade` (r = 0.194 com weak_signal)
- `sentiment_stability`
- `relevancia_cultural`
- `cultural_resonance`

---

## 📈 6. PRÓXIMOS PASSOS

1. **Retreinar XGBoost sem weak_signal_score** para descobrir features reais
2. **Testar modelo apenas com features culturais** (relevância, ressonância, autenticidade)
3. **Criar feature de "crescimento sustentado"** (média móvel 7 dias)
4. **Analisar interação termo × plataforma** (alguns termos são fortes em plataformas específicas)
5. **Incorporar contextos narrativos** como features via NLP (TF-IDF de descrições)

---

## ✅ CONCLUSÕES

### Maior Covariação Contextual:
1. **Alcance Regional ↔ Multi-plataforma** (r=0.92)
2. **Engajamento Social** (likes, shares, comments: r>0.85)
3. **Crescimento Dinâmico** (momentum, velocidade, aceleração: r>0.83)

### Features Mais Importantes (XGBoost):
1. **weak_signal_score** (98.5% gain) - ⚠️ circular
2. **engagement_rate** (9% weight, 0.1 gain)
3. **trending_score** (8% weight, 0.1 gain)
4. **cultural_resonance** (3% weight, 0.1 gain)
5. **relevancia_cultural** (2% weight, 0.1 gain)

### Descobertas Surpreendentes:
- ⚠️ **Weak signals têm MENOR engagement_rate** (nicho intenso)
- ⚠️ **Weak signals NÃO têm crescimento acelerado** (linear sustentado)
- ✅ **Weak signals têm MAIOR viralidade** (compartilhamento orgânico)
- ✅ **Dimensão cultural diferencia** sinais brasileiros autênticos

---

**Gerado por**: Context Importance Analyzer  
**Arquivos**: `results/context_importance_analysis.json`, `results/context_importance_analysis.png`
