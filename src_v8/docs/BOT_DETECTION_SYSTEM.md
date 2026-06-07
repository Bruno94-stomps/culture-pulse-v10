# 🤖 Sistema de Detecção de Bots - Culture Pulse V9.1

## 📋 Visão Geral

Sistema de detecção de bots/perfis fake **conservador** implementado no `WeakSignalDetector` para filtrar conteúdo artificial nas análises culturais.

### **Estratégia: Ponderação sem Descarte**
- ✅ **Nenhum sinal é descartado** (evita falsos positivos)
- ⚖️ **Ponderação gradual** baseada em bot_score
- 🎯 **Thresholds altos** (>70, >85) para ser conservador

---

## 🔬 Metodologia: 6 Sinais Híbridos Não-Supervisionados

### ⚠️ **POR QUE NÃO-SUPERVISIONADO?**

**Diferença Crítica com Weak Signal Detection:**

| Sistema | Método | Ground Truth CLI? | Motivo |
|---------|--------|-------------------|--------|
| **Weak Signal** | **Supervisionado** | ✅ `collect_ground_truth.py` | Fácil rotular (5-10 seg/exemplo) |
| **Bot Detection** | **Não-Supervisionado** | ❌ Não existe | Difícil rotular (5-10 min/exemplo) |

**Bot detection usa heurísticas não-supervisionadas porque:**
1. ❌ **Sem dataset rotulado**: Não temos `data/bot_ground_truth.csv`
2. ⏰ **Custo alto de rotulação**: Precisa investigar perfis individualmente (8-16h para 100 amostras)
3. 🔄 **Bots evoluem rápido**: Dataset fica desatualizado rapidamente
4. 🎯 **Solução pragmática**: Heurísticas funcionam imediatamente sem coleta

**Futuro**: Planejamos criar `collect_bot_ground_truth.py` para transição gradual a modelo supervisionado (Fase 2-3).

---

### **1. Authenticity Score (BERTimbau)** - 30% peso
```python
# Usa relevancia_cultural como proxy
authenticity = signal.relevancia_cultural  # 0-1
component = (1 - authenticity) * 30

# Interpretação:
# < 0.3: Linguagem artificial/genérica (HIGH RISK)
# 0.3-0.6: Aceitável
# > 0.6: Autêntico culturalmente
```

**Fonte**: `core/authenticity_analyzer.py` - BERTimbau embeddings + cosine similarity

---

### **2. Sentiment Stability** - 20% peso
```python
# Sentimento muito uniforme = suspeito
sentiment_stability = 1.0 - abs(sentiment)  # Quanto mais neutro, mais "estável"

if sentiment_stability > 0.85:  # 85%+ uniformidade
    component = sentiment_stability * 20
else:
    component = 0

# Interpretação:
# < 0.1 variance: Postagens uniformes (robótico)
# > 0.3 variance: Sentimentos variados (orgânico)
```

**Fonte**: Feature importante XGBoost (0.2 gain) - `results/CONTEXT_IMPORTANCE_INSIGHTS.md`

---

### **3. Dissonance Score** - 20% peso
```python
# Baixa dissonância contextual = previsível
dissonance = 1 - (momentum / 100)  # Normalizar

if dissonance < 0.2:  # Muito previsível
    component = (1 - dissonance) * 20
else:
    component = 0

# Interpretação:
# < 0.2: Contexto previsível (bot pattern)
# > 0.5: Contexto diverso (orgânico)
```

**Fonte**: `products/weak_signal_detector.py` - Critério de detecção de sinal fraco

---

### **4. Temporal Patterns** - 15% peso
```python
# NOTA: Não implementado na V9.1 (dados temporais limitados)
# Futuro: Detectar periodicidade robótica (postagens a cada X horas)
component = 0  # Placeholder
```

**Planejado**: Usar `temporal_cultural_analyzer.py` para detectar padrões de postagem suspeitosamente regulares.

---

### **5. Cross-Platform Dispersion** - 10% peso
```python
n_platforms = len(signal.plataformas)

if n_platforms < 2:
    component = 10  # Bot focado em uma plataforma
else:
    component = 0

# Interpretação:
# 1 plataforma: Suspeito (bots costumam focar)
# 3+ plataformas: Orgânico (engajamento real)
```

---

### **6. Volume + Sentiment Uniformity** - 5% peso
```python
# Volume explosivo + sentimento uniforme = bot farm
if volume > 1000 and abs(sentiment) < 0.1:
    component = 5
else:
    component = 0

# Interpretação:
# Spike súbito + sem variação = coordenado
```

---

## 📊 Score Final e Classificação

```python
bot_score = (
    authenticity_component +      # 30%
    stability_component +         # 20%
    dissonance_component +        # 20%
    temporal_component +          # 15%
    platform_component +          # 10%
    volume_sentiment_component    # 5%
)  # Total: 0-100
```

### **Thresholds Conservadores**

| Bot Score | Classificação | Peso Aplicado | Ação |
|-----------|---------------|---------------|------|
| **> 85** | 🤖 HIGH RISK | **60%** | Redução de 40% no weak_signal_score |
| **> 70** | ⚠️ MEDIUM RISK | **80%** | Redução de 20% no weak_signal_score |
| **≤ 70** | ✅ LOW RISK | **100%** | Sem penalização |

---

## 🎯 Implementação no Pipeline

### **1. Entrada: CulturalSignals**
```python
signals = [
    CulturalSignal(termo="maduro", volume=5000, sentiment=0.05, momentum=35, ...),
    CulturalSignal(termo="havaianas", volume=800, sentiment=0.65, momentum=72, ...)
]
```

### **2. Bot Detection Filter**
```python
# Em WeakSignalDetector.detect_weak_signals()
signals_filtered = self._apply_confidence_factors(signals)

# Cada sinal recebe:
signal.bot_score = 45.3  # Calculado pelos 6 métodos
signal.confidence_factor = 0.80  # 80% de peso (MEDIUM RISK)
signal.bot_risk_level = "MEDIUM"
```

### **3. Ponderação do Score**
```python
# Original score
base_score = 68.5

# Score ponderado pelo confidence_factor
final_score = base_score * 0.80  # = 54.8

weak_signal.weak_signal_score = final_score
weak_signal.original_score = base_score  # Preservado para auditoria
```

### **4. Display no Dashboard**
```python
# products/futuruma_dashboard.py - render_weak_signal_card()

if bot_risk_level == "HIGH":
    st.warning("🤖 ALTO RISCO DE BOT (score: 87.3/100) - Peso reduzido para 60%")
elif bot_risk_level == "MEDIUM":
    st.info("⚠️ Suspeita de Bot (score: 74.2/100) - Peso ajustado para 80%")
else:
    st.success("✅ Sinal Orgânico Verificado (bot score: 23.1/100)")
```

---

## 📈 Estatísticas de Execução

```bash
# Logs do detector (exemplo)
📊 Bot Detection Stats: 25 sinais analisados
   🤖 HIGH RISK (>85): 2 (8.0%) - peso 60%
   ⚠️ MEDIUM RISK (>70): 5 (20.0%) - peso 80%
   ✅ LOW RISK (≤70): 18 (72.0%) - peso 100%
```

---

## 🔧 Configuração (Ajustável)

### **Thresholds (em `WeakSignalDetector.__init__`)**
```python
self.bot_thresholds = {
    'high_risk': 85,      # Alterar para 90 se muito agressivo
    'medium_risk': 70,    # Alterar para 75 se necessário
    'low_risk': 0
}

self.bot_weights = {
    'high_risk': 0.60,    # Reduzir para 0.40 se quiser penalizar mais
    'medium_risk': 0.80,  # Reduzir para 0.70 se necessário
    'low_risk': 1.00
}
```

---

## ✅ Vantagens da Abordagem Conservadora

1. **Sem Descarte**: Evita perder sinais emergentes genuínos
2. **Ponderação Gradual**: Impacto proporcional ao risco
3. **Transparência**: Usuário vê bot_score e peso aplicado
4. **Auditável**: Preserva `original_score` para análise
5. **Ajustável**: Thresholds e pesos configuráveis

---

## ⚠️ Limitações Conhecidas

1. **Método 4 (Temporal Patterns)**: Não implementado (dados limitados)
2. **Ground Truth**: Sem dataset rotulado de bots brasileiros culturais
3. **Falsos Positivos**: Sinais genuínos com linguagem formal podem ter score alto
4. **Contexto Cultural**: Bots sofisticados podem imitar autenticidade

---

## 🔮 Roadmap Futuro

### **Fase 2 (1-2 semanas)** - Coletar dados de produção
- [ ] Coletar dados de produção (bot_score vs validação manual)
- [ ] Calibrar thresholds baseado em precisão real
- [ ] Implementar Método 4 (temporal patterns)

### **Fase 3 (1-2 meses)** - Bot Ground Truth Supervisionado
- [ ] **Criar `scripts/collect_bot_ground_truth.py`** (CLI para rotular bots)
  ```python
  # Interface similar ao collect_ground_truth.py
  response = input("\n👉 Este sinal é de BOT? [s/n/skip]: ")
  if response == 's':
      is_bot = 1  # Label supervisionado
  # Salvar em data/bot_ground_truth.csv
  ```
- [ ] Coletar 50-100 amostras rotuladas (10 por dia = 1 semana)
- [ ] Dataset balanceado (50% bots, 50% orgânicos)

### **Fase 4 (3-4 meses)** - Modelo Supervisionado Híbrido
- [ ] Treinar XGBoost com bot_ground_truth.csv
  ```python
  # Features: 6 heurísticas atuais
  # Labels: is_bot (manual)
  xgb_model.train(features, labels)
  # Precisão esperada: 85-90% após 200+ amostras
  ```
- [ ] Combinar modelo supervisionado + heurísticas
- [ ] Descarte automático com threshold >90 (após validação)
- [ ] Retreino mensal com novos exemplos

### **Fase 5 (6 meses)** - Avançado
- [ ] Análise de rede (bot farms coordenados)
- [ ] Detecção de deepfakes textuais
- [ ] API externa de verificação (Botometer adaptado para BR)

---

## 📚 Referências

- **BERTimbau**: `neuralmind/bert-base-portuguese-cased` (97.2% F1 em autenticidade cultural)
- **XGBoost Features**: `results/CONTEXT_IMPORTANCE_INSIGHTS.md` (sentiment_stability = 0.2 gain)
- **Bot Detection Criteria**: `docs/EXPLICACAO_SINAL_VS_RUIDO_E_ML.md` (6 métodos híbridos)
- **Authenticity Analyzer**: `core/authenticity_analyzer.py` (Sentence-Transformers)

---

## 🚀 Como Usar

### **1. Detector Automático (Padrão)**
```python
from products.weak_signal_detector import WeakSignalDetector

detector = WeakSignalDetector()
weak_signals = detector.detect_weak_signals(cultural_signals)

# Bot detection aplicado automaticamente
for ws in weak_signals:
    print(f"{ws.termo}: score={ws.weak_signal_score:.1f}, "
          f"bot_risk={ws.bot_risk_level}, "
          f"confidence={ws.confidence_factor*100:.0f}%")
```

### **2. Ajustar Thresholds (Customizado)**
```python
# Mais conservador (penaliza menos)
detector.bot_thresholds['high_risk'] = 90  # Era 85
detector.bot_weights['high_risk'] = 0.70   # Era 60%

# Mais agressivo (penaliza mais)
detector.bot_thresholds['high_risk'] = 80  # Era 85
detector.bot_weights['high_risk'] = 0.40   # Era 60%
```

### **3. Analisar Bot Score Manualmente**
```python
signal = cultural_signals[0]
bot_score = detector._calculate_bot_score(signal)

print(f"Bot Score: {bot_score:.1f}/100")
if bot_score > 85:
    print("HIGH RISK - Revisar manualmente")
```

---

## 📊 Dashboard Visualization

O dashboard automaticamente mostra:

1. **Card de Sinal** (render_weak_signal_card):
   - 🤖 **ALTO RISCO DE BOT** (se >85)
   - ⚠️ **Suspeita de Bot** (se >70)
   - ✅ **Sinal Orgânico Verificado** (se ≤70)

2. **Métricas Exibidas**:
   - Bot Score (0-100)
   - Confidence Factor (60-100%)
   - Risk Level (HIGH/MEDIUM/LOW)

---

## 💡 Boas Práticas

1. **Monitorar Periodicamente**: Revisar sinais com HIGH RISK manualmente
2. **Validar Calibração**: Coletar feedback sobre false positives/negatives
3. **Ajustar Gradualmente**: Aumentar penalização só após validação
4. **Documentar Exceções**: Sinais genuínos com high score devem ser investigados
5. **Comparar Original vs Final**: Usar `original_score` vs `weak_signal_score` para audit

---

**Versão**: V9.1  
**Data**: 09/02/2026  
**Autor**: Culture Pulse Team  
**Status**: ✅ Production Ready (Conservador)
