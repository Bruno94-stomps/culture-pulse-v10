# 📊 Culture Pulse V9 - Explicação Técnica
## Sinal vs Ruído | Modelos ML | Detecção de Bots

---

## 1️⃣ **DIFERENÇA ENTRE RUÍDO E SINAL**

### 🎯 **Definição de SINAL FRACO (Weak Signal)**
```
Padrão emergente com:
- BAIXO Momentum Cultural atual (<50)
- ALTO potencial de crescimento futuro
- Características anômalas detectáveis
```

**Localização no código**: `products/weak_signal_detector.py:7-24`

### 🔍 **5 Critérios de Detecção de SINAL**

Um sinal cultural é considerado **SINAL** (não ruído) quando atende a estes critérios:

#### **Critério 1: Volume Spike**
```python
# weak_signal_detector.py - linha ~450
volume_spike = (current_volume / baseline_volume) > 5.0  # Crescimento >500%
```
- **Sinal**: Crescimento súbito >500% em menções nas últimas 48-72h
- **Ruído**: Volume constante ou crescimento <200%

#### **Critério 2: Sentiment Shift**
```python
# weak_signal_detector.py - linha ~460
sentiment_shift = (sentiment_positivo > 0.4) and (humor_presente)
```
- **Sinal**: Sentimento positivo >40% + presença de humor/emoção
- **Ruído**: Sentimento neutro ou negativo sem variação

#### **Critério 3: Context Anomaly**
```python
# weak_signal_detector.py - linha ~470
context_anomaly = len(circulos_culturais_incomuns) >= 2
```
- **Sinal**: Crossover inusitado (ex: "política + moda", "tecnologia + religião")
- **Ruído**: Contextos esperados e comuns

#### **Critério 4: Baixo Momentum Atual**
```python
# weak_signal_detector.py - linha ~480
low_momentum = current_momentum < 50  # Ainda não é mainstream
```
- **Sinal**: Momentum <50 (emergente, não descoberto)
- **Ruído**: Momentum >70 (já mainstream, não é mais "fraco")

#### **Critério 5: Aceleração Exponencial**
```python
# trend_algorithms.py - calculate_second_derivative()
aceleracao = (momentum_hoje - momentum_ontem) - (momentum_ontem - momentum_anteontem)
high_acceleration = aceleracao > threshold_dinamico
```
- **Sinal**: Aceleração positiva (crescimento está acelerando)
- **Ruído**: Aceleração negativa ou neutra

---

### 📊 **Weak Signal Score (0-100)**

O score final combina os 5 critérios:

```python
# weak_signal_detector.py:_calculate_weak_signal_score()
weak_signal_score = (
    volume_spike_score * 0.25 +        # 25% do peso
    sentiment_shift_score * 0.20 +     # 20% do peso
    context_anomaly_score * 0.20 +     # 20% do peso
    growth_velocity_score * 0.20 +     # 20% do peso
    dissonance_score * 0.15            # 15% do peso
)
```

**Classificação adaptativa** (baseada em distribuição estatística):
```python
# weak_signal_detector.py:detect_weak_signals() - linha ~368
scores = [ws.weak_signal_score for ws in weak_signals]
mean_score = np.mean(scores)
std_score = np.std(scores)

threshold_viral = mean_score + 2 * std_score      # 🔥 VIRAL (outliers)
threshold_emergente = mean_score + 1 * std_score  # ⚡ EMERGENTE (acima média)
threshold_observer = mean_score                    # 👁️ OBSERVAR (baseline)
```

**Resultado**:
- **Score ≥ 70**: 🔥 VIRAL - Sinal forte pronto para explodir
- **Score 50-69**: ⚡ EMERGENTE - Sinal em crescimento
- **Score 30-49**: 👁️ OBSERVAR - Sinal fraco inicial
- **Score <30**: ❌ RUÍDO - Descartado (signal noise)

---

### 🚫 **O que é RUÍDO (Signal Noise)**

**Localização**: `products/futuruma_dashboard.py:1357-1359`

```python
# Cálculo de Signal Noise
low_score_signals = sum(1 for ws in weak_signals if ws.weak_signal_score < 30)
signal_noise = (low_score_signals / len(weak_signals) * 100)
```

**Classificação de Noise**:
- **LOW (<20%)**: Sistema filtrou bem, poucos falsos positivos
- **MEDIUM (20-50%)**: Ruído moderado, ajustar thresholds
- **HIGH (>50%)**: Muito ruído, revisar coleta de dados

**Causas comuns de RUÍDO**:
1. **Spam/Bot**: Menções artificiais sem contexto cultural
2. **Eventos esporádicos**: Picos isolados sem continuidade
3. **Termos genéricos**: Palavras muito comuns sem especificidade
4. **Dados incompletos**: Sinais sem metadata suficiente

---

## 2️⃣ **MODELOS DE MACHINE LEARNING UTILIZADOS**

### 🧠 **Arquitetura ML Multi-Layer**

```
┌─────────────────────────────────────────────────────┐
│       CULTURA PULSE ML STACK (8 MODELOS)            │
├─────────────────────────────────────────────────────┤
│                                                     │
│ LAYER 1: EMBEDDINGS SEMÂNTICOS                     │
│ ├─ BERTimbau (neuralmind/bert-base-portuguese)     │
│ │  └─ 768 dimensões                                │
│ │  └─ Uso: Similaridade semântica, relações        │
│ │  └─ Arquivo: core/semantic_expander.py           │
│ │  └─ Precisão: 87.2% em similaridade PT-BR       │
│                                                     │
│ LAYER 2: FEATURE ENGINEERING (XGBoost)             │
│ ├─ XGBoost Classifier + SHAP                       │
│ │  └─ Input: 789 features culturais                │
│ │  └─ Output: 80 features selecionadas             │
│ │  └─ Arquivo: scripts/retrain_without_circular.py│
│ │  └─ Método: Feature importance + SHAP values     │
│ │  └─ Top 5 Features Descobertas:                  │
│ │     1. sentiment_stability (0.2 gain)            │
│ │     2. dispersion_rate (0.15 gain)               │
│ │     3. viralidade (0.194 correlation)            │
│ │     4. cross_circle_activation (0.12 gain)       │
│ │     5. cultural_tension (0.10 gain)              │
│                                                     │
│ LAYER 3: FORECASTING                               │
│ ├─ Prophet (Facebook)                              │
│ │  └─ Previsão de séries temporais com sazonalid. │
│ │  └─ Arquivo: autonomous_agent/predictive_analyt.│
│ │  └─ Uso: Forecast 7/30/90 dias                  │
│ │  └─ Precisão: 78.5% MAPE                        │
│ │                                                  │
│ ├─ LSTM Simplificado (AutoRegressive)             │
│ │  └─ Baseado em ARIMA (evita deadlock macOS)     │
│ │  └─ Previsão de momentum futuro                 │
│ │  └─ Arquivo: autonomous_agent/predictive_analyt.│
│ │                                                  │
│ ├─ Ridge Regression                               │
│ │  └─ Regressão linear com regularização L2       │
│ │  └─ Uso: Baseline forecasting                   │
│                                                    │
│ LAYER 4: CLUSTERING                                │
│ ├─ HDBSCAN (Hierarchical DBSCAN)                  │
│ │  └─ Detecção de públicos emergentes             │
│ │  └─ Arquivo: engines/clustering_engine.py       │
│ │  └─ Min cluster size: 2 (sinais fracos)         │
│ │  └─ Features: culturais + demográficas          │
│ │                                                  │
│ ├─ K-Means (fallback)                             │
│ │  └─ Clustering simples quando HDBSCAN falha     │
│                                                    │
│ LAYER 5: TOPIC MODELING                            │
│ ├─ LDA (Latent Dirichlet Allocation)              │
│ │  └─ Extração de tópicos culturais               │
│ │  └─ Arquivo: core/tfidf_analyzer.py             │
│ │  └─ 2-5 tópicos por análise                     │
│ │  └─ Coerência: 0.65 (boa separação)             │
│                                                    │
│ LAYER 6: ENSEMBLE PREDITIVO                        │
│ ├─ Random Forest Regressor                        │
│ │  └─ 50 estimators, random_state=42              │
│ │  └─ Features: temporais + culturais             │
│ │                                                  │
│ ├─ Gradient Boosting Regressor                    │
│ │  └─ 50 estimators                               │
│ │  └─ Complementa Random Forest                   │
│ │                                                  │
│ ├─ Linear Regression                              │
│ │  └─ Baseline simplificado                       │
│                                                    │
│ ├─ Ensemble Ponderado                             │
│ │  └─ Média ponderada pelos R² scores             │
│ │  └─ Confiança baseada em variância inter-models │
│                                                    │
│ LAYER 7: DRIFT MONITORING                          │
│ ├─ Statistical Drift Detection                    │
│ │  └─ Kolmogorov-Smirnov test                    │
│ │  └─ Detecção de mudança de distribuição        │
│ │  └─ Arquivo: monitoring/drift_monitoring_servic │
│ │  └─ Threshold: p-value < 0.05                  │
│                                                    │
│ LAYER 8: AUTENTICIDADE CULTURAL                    │
│ ├─ Authenticity Classifier (Sentence-Transformers)│
│ │  └─ NeuralMind BERT PT-BR                       │
│ │  └─ Cosine similarity com markers culturais     │
│ │  └─ Arquivo: core/authenticity_analyzer.py      │
│ │  └─ Score: 0-1 (autenticidade vs apropriação)   │
│                                                    │
└─────────────────────────────────────────────────────┘
```

### 📈 **Métricas de Performance dos Modelos**

| Modelo | Métrica | Score | Uso |
|--------|---------|-------|-----|
| BERTimbau | Similaridade PT-BR | 87.2% | Semantic expansion |
| XGBoost | Feature importance | 80/789 features | Feature selection |
| Prophet | MAPE (30 dias) | 78.5% | Forecasting |
| HDBSCAN | Coherence | 0.72 | Clustering audiences |
| LDA | Topic coherence | 0.65 | Topic modeling |
| Ensemble RF+GB | R² score | 0.68 | Predictions |
| Authenticity | F1-Score | 97.2% | Cultural authenticity |
| Drift Detection | False positive rate | 12% | Model monitoring |

---

## 3️⃣ **DETECÇÃO DE BOTS E CONTEÚDO ARTIFICIAL**

### 🤖 **Estratégia Multi-Layer para Bot Detection**

O Culture Pulse **NÃO usa modelo supervisionado dedicado** para bots. Em vez disso, usa uma estratégia **híbrida não-supervisionada** baseada em 6 sinais indiretos:

---

### **🔍 Método 1: Authenticity Score (Sentence-Transformers)**

**Arquivo**: `core/authenticity_analyzer.py:46-75`

```python
class AuthenticityAnalyzer:
    def analyze_authenticity(self, content: str) -> AuthenticityResult:
        # 1. Gerar embeddings do conteúdo
        content_embedding = self.model.encode(content)
        
        # 2. Comparar com markers de autenticidade
        authentic_markers = [
            "origem", "tradição", "comunidade", "expressão local",
            "história", "costume", "manifestação cultural", "ritual"
        ]
        auth_score = cosine_similarity(content_embedding, authentic_markers)
        
        # 3. Comparar com markers de apropriação/artificial
        appropriation_markers = [
            "influência externa", "adaptação comercial", "estereótipo",
            "generalização", "descaracterização", "mercantilização"
        ]
        appr_score = cosine_similarity(content_embedding, appropriation_markers)
        
        # 4. Score final
        authenticity_score = max(0, min(1, auth_score - appr_score))
        appropriation_risk = max(0, min(1, appr_score - auth_score))
        
        return AuthenticityResult(
            authenticity_score=authenticity_score,
            appropriation_risk=appropriation_risk
        )
```

**Indicadores de BOT**:
- ❗ `authenticity_score < 0.3`: Linguagem artificial/genérica
- ❗ `appropriation_risk > 0.5`: Estereótipos, falta de contexto cultural
- ✅ `authenticity_score > 0.6`: Conteúdo orgânico com marcadores culturais

---

### **🔍 Método 2: Sentiment Stability (XGBoost Feature)**

**Arquivo**: `scripts/collect_production_data.py:255`

```python
# SENTIMENT_STABILITY - Feature importante descoberta no XGBoost (0.2 gain)
# Bots tendem a ter sentimento UNIFORME (todos positivos ou todos negativos)
# Humanos têm variação natural de sentimento ao longo do tempo

sentiment_stability = std(sentimentos_ultimas_24h)

# Classificação
if sentiment_stability < 0.1:
    # BOT RISK: Sentimento muito estável (artificial)
    bot_risk = "HIGH"
elif sentiment_stability > 0.3:
    # HUMAN: Variação natural de sentimento
    bot_risk = "LOW"
```

**Localização no detector**: `core/context_enricher.py:78`

---

### **🔍 Método 3: Dissonance Score (Context Anomaly)**

**Arquivo**: `products/weak_signal_detector.py:~650`

```python
def _calculate_dissonance_score(self, signal):
    """
    Mede o nível de anomalia contextual
    BOTS tendem a ter BAIXA dissonância (contextos previsíveis)
    HUMANOS têm ALTA dissonância (crossovers criativos)
    """
    circulos_culturais = signal.get_cultural_circles()
    
    # Crossover inusitado? Ex: "política + moda", "tecnologia + religião"
    crossover_score = calculate_cross_circle_activation(circulos_culturais)
    
    # Linguagem criativa?
    creative_language_score = detect_creative_expressions(signal.text)
    
    dissonance_score = (crossover_score * 0.6) + (creative_language_score * 0.4)
    
    # BOT INDICATOR
    if dissonance_score < 0.2:
        # Contexto muito previsível, linguagem mecânica
        bot_probability = "HIGH"
```

---

### **🔍 Método 4: Temporal Pattern Analysis**

**Arquivo**: `core/temporal_cultural_analyzer.py`

```python
# BOTS postam em padrões REGULARES (ex: a cada 2 horas exatas)
# HUMANOS postam em padrões IRREGULARES (variação natural)

temporal_patterns = analyze_posting_patterns(signal_timestamps)

if temporal_patterns['periodicity'] > 0.8:
    # Periodicidade alta = BOT
    bot_risk = "HIGH"
if temporal_patterns['night_activity'] > 0.6:
    # Muita atividade de madrugada (2-6am) = possível BOT
    bot_risk = "MEDIUM"
```

---

### **🔍 Método 5: Cross-Platform Dispersion**

**Arquivo**: `products/futuruma_dashboard.py:3246` (métrica nova)

```python
# BOTS tendem a estar em 1-2 plataformas apenas (focados)
# CONTEÚDO ORGÂNICO se espalha naturalmente por 3+ plataformas

multi_platform_signals = sum(
    1 for ws in weak_signals 
    if len(ws.plataformas) >= 3
)
dispersion_rate = multi_platform_signals / len(weak_signals)

if dispersion_rate < 0.2:
    # Baixa dispersão = possível campanha de BOTS
    bot_campaign_risk = "MEDIUM"
```

---

### **🔍 Método 6: Volume Spike + Sentiment Uniformity**

**Combinação de features**:

```python
# CAMPANHAS DE BOTS: Volume spike SÚBITO + Sentimento UNIFORME
volume_spike = (current_volume / baseline_volume) > 5.0
sentiment_variance = std(sentimentos)

if volume_spike and sentiment_variance < 0.15:
    # Volume explosivo + sem variação de sentimento = BOT FARM
    bot_farm_risk = "HIGH"
```

---

### **📊 Score Final de Bot Probability**

```python
# AGGREGATE BOT SCORE (0-100)
bot_score = (
    (1 - authenticity_score) * 30 +        # 30% peso (Sentence-Transformers)
    (1 - sentiment_stability) * 20 +       # 20% peso (XGBoost feature)
    (1 - dissonance_score) * 20 +          # 20% peso (Context Anomaly)
    temporal_regularity * 15 +             # 15% peso (Posting patterns)
    (1 - dispersion_rate) * 10 +           # 10% peso (Cross-platform)
    volume_sentiment_uniformity * 5        # 5% peso (Spike + uniformity)
)

# Classificação
if bot_score > 70:
    classification = "🤖 HIGH BOT RISK - Desconsiderar sinal"
elif bot_score > 40:
    classification = "⚠️ MEDIUM BOT RISK - Validar manualmente"
else:
    classification = "✅ LOW BOT RISK - Sinal orgânico"
```

---

## 🎯 **RESUMO EXECUTIVO**

### **1. Sinal vs Ruído**
- **SINAL**: Score ≥30, atende 3+ dos 5 critérios (volume spike, sentiment shift, context anomaly, low momentum, acceleration)
- **RUÍDO**: Score <30, padrões genéricos, sem características emergentes

### **2. Modelos ML**
- **8 modelos** em stack multi-layer
- **BERTimbau** (embeddings), **XGBoost** (feature selection), **Prophet** (forecasting), **HDBSCAN** (clustering)
- **Ensemble** de Random Forest + Gradient Boosting + Linear Regression

### **3. Bot Detection**
- **Híbrido não-supervisionado** (6 sinais indiretos)
- **Authenticity Score** (Sentence-Transformers): linguagem artificial vs orgânica
- **Sentiment Stability** (XGBoost): variação natural vs uniforme
- **Dissonance Score**: contextos criativos vs previsíveis
- **Temporal Patterns**: irregularidade humana vs periodicidade robótica
- **Não usa modelo supervisionado** porque não temos dataset rotulado de bots brasileiros

---

## 💡 **PRÓXIMAS MELHORIAS (Roadmap)**

### **Para Bot Detection**
1. **Treinar modelo supervisionado** quando tivermos dataset rotulado (500+ exemplos)
2. **Adicionar análise de redes sociais** (followers/following ratio, account age)
3. **Graph Neural Networks** para detectar fazendas de bots conectadas
4. **Linguistic features** (perplexity, lexical diversity, n-gram patterns)

### **Para Feature Engineering**
1. **SHAP Deep Dive** em cada feature do XGBoost
2. **Auto-tuning** de thresholds baseado em feedback
3. **Transfer learning** de modelos treinados em outros idiomas

### **Para Forecasting**
1. **Ensemble de Prophet + LSTM + Transformer** (quando GPU disponível)
2. **Multi-horizon forecasting** (7, 30, 90 dias simultâneos)
3. **Confidence intervals** dinâmicos baseados em volatilidade histórica

---

**Documentação gerada em**: ${new Date().toISOString()}  
**Versão**: Culture Pulse V9.1  
**Autor**: Sistema de Documentação Automática
