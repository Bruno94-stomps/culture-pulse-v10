# 🤖 ML Training Pipeline - Classificador de Autenticidade Cultural

Sistema completo de coleta, anotação e treino de classificador de autenticidade cultural brasileiro usando **BERTimbau + XGBoost**.

---

## 📊 **Arquitetura**

```
┌──────────────────────────────────────────────────────────────────┐
│                   ML TRAINING PIPELINE                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1️⃣  COLETA AUTOMÁTICA                                           │
│      ├─ WeakSignalDetector detecta sinais                       │
│      ├─ AutoCollector salva automaticamente                     │
│      └─ dataset/raw_signals.jsonl                               │
│                                                                  │
│  2️⃣  ANOTAÇÃO MANUAL                                             │
│      ├─ annotation_tool.py (CLI interativa)                     │
│      ├─ Labels: autêntico/comercial/apropriação/misto          │
│      └─ dataset/annotated_signals.csv                           │
│                                                                  │
│  3️⃣  FEATURE ENGINEERING                                         │
│      ├─ BERTimbau embeddings (768 dims)                         │
│      ├─ Features heurísticas (11 features)                      │
│      └─ Total: 779 features                                     │
│                                                                  │
│  4️⃣  TREINO                                                       │
│      ├─ XGBoost Classifier                                       │
│      ├─ 80% treino / 20% teste                                  │
│      ├─ Cross-validation 5-fold                                 │
│      └─ models/authenticity_classifier.pkl                      │
│                                                                  │
│  5️⃣  PREDIÇÃO                                                     │
│      ├─ Carrega modelo treinado                                 │
│      ├─ Classifica novos sinais                                 │
│      └─ Retorna: label + confidence + probabilities             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🚀 **Quick Start**

### **Instalação**

```bash
# Já instalado no projeto:
pip install sentence-transformers xgboost scikit-learn pandas numpy
```

### **1. Coletar Sinais Automaticamente**

```python
from products.ml_training.auto_collector import AutoCollector
from products.weak_signal_detector import WeakSignalDetector

# Configurar coletor automático
auto_collector = AutoCollector(enabled=True, min_score=30.0)

# Executar detecção normal
detector = WeakSignalDetector()
signals = detector.detect_weak_signals(
    termo="Copa 2026",
    youtube_data=youtube_data,
    reddit_data=reddit_data
)

# Coletar automaticamente
collected = auto_collector.collect_from_signals(signals)
print(f"📦 Coletados {collected} sinais")
```

### **2. Anotar Sinais Manualmente**

```bash
# Iniciar sessão de anotação
python products/ml_training/annotation_tool.py --annotator "seu_nome" --batch 50

# Ver estatísticas
python products/ml_training/annotation_tool.py --stats

# Revisar últimas anotações
python products/ml_training/annotation_tool.py --review

# Exportar dataset
python products/ml_training/annotation_tool.py --export
```

**Interface CLI:**
```
📊 SINAL 1/50 - ID: a3f2c8d9e1b4
================================================================

📝 TEXTO:
   Funk carioca das favelas do Rio

🏷️  CONTEXTO DETECTADO: EMERGENTE

📈 MÉTRICAS HEURÍSTICAS:
   Volume:     150 menções
   Momentum:   45.20
   Sentiment:   0.65
   Velocity:    2.30

🌍 REGIÕES: Sudeste, Nacional
📱 FONTES:  youtube:85, reddit:59

🏷️  CLASSIFICAÇÃO:
   [A] Autêntico      - Movimento cultural genuíno, orgânico
   [C] Comercial      - Campanha comercial, marketing
   [P] Apropriação    - Apropriação cultural, descontextualização
   [M] Misto          - Elementos autênticos + comerciais
   [I] Ignorar        - Não é relevante / Skip
   [Q] Quit           - Sair e salvar progresso

👉 Sua classificação: A
   Confiança (0-100, Enter=50): 85
   Notas (opcional, Enter=skip): Movimento genuíno das comunidades

✅ Anotado como 'autêntico' (confiança: 85%)
```

### **3. Treinar Classificador**

```bash
# Treino básico (requer mínimo 100 exemplos anotados)
python products/ml_training/train_classifier.py

# Com tuning de hiperparâmetros (lento, ~30 min)
python products/ml_training/train_classifier.py --tune

# Customizado
python products/ml_training/train_classifier.py \
    --min-samples 200 \
    --test-size 0.25 \
    --output models/my_classifier.pkl
```

**Output esperado:**
```
📊 Dataset:
   Exemplos: 500
   Classes: ['apropriação', 'autêntico', 'comercial', 'misto']
   Distribuição:
      apropriação    :   85 ( 17.0%)
      autêntico      :  250 ( 50.0%)
      comercial      :  120 ( 24.0%)
      misto          :   45 (  9.0%)

📊 AVALIAÇÃO
================================================================
📈 Classification Report:
                precision    recall  f1-score   support

   apropriação      0.780     0.720     0.749        18
     autêntico      0.920     0.940     0.930        50
     comercial      0.850     0.810     0.829        24
         misto      0.710     0.770     0.739         8

      accuracy                          0.860       100
     macro avg      0.815     0.810     0.812       100
  weighted avg      0.861     0.860     0.860       100

🔝 Top 15 Features Mais Importantes:
    1. emb_234                        : 0.0342
    2. momentum_x_sentiment           : 0.0298
    3. emb_567                        : 0.0287
    4. volume_log                     : 0.0245
    5. sentiment_norm                 : 0.0234
   ...

✅ Modelo salvo: products/ml_training/models/authenticity_classifier.pkl
```

### **4. Usar Classificador em Produção**

```python
from products.ml_training.train_classifier import AuthenticityClassifier

# Carregar modelo treinado
classifier = AuthenticityClassifier.load(
    'products/ml_training/models/authenticity_classifier.pkl'
)

# Classificar novo sinal
result = classifier.predict(
    text="Nike lança linha inspirada em cultura brasileira",
    momentum=65,
    sentiment=0.3,
    volume=500,
    velocity=1.5,
    num_sources=3,
    has_youtube=1,
    has_reddit=1
)

print(result)
# {
#     'label': 'comercial',
#     'confidence': 87.3,
#     'probabilities': {
#         'autêntico': 5.2,
#         'comercial': 87.3,
#         'apropriação': 4.1,
#         'misto': 3.4
#     }
# }
```

---

## 📂 **Estrutura de Arquivos**

```
products/ml_training/
├── dataset_collector.py       # Sistema de coleta automática
├── annotation_tool.py         # Interface CLI de anotação
├── auto_collector.py          # Hook para WeakSignalDetector
├── train_classifier.py        # Treino do classificador XGBoost
├── README.md                  # Este arquivo
│
├── dataset/                   # Dados coletados
│   ├── raw_signals.jsonl      # Sinais coletados (1 por linha)
│   ├── annotated_signals.csv  # Sinais anotados (para treino)
│   ├── dataset_stats.json     # Estatísticas do dataset
│   └── training_data_YYYYMMDD.csv  # Exports para treino
│
└── models/                    # Modelos treinados
    └── authenticity_classifier.pkl  # Classificador treinado
```

---

## 🎯 **Métricas de Sucesso**

### **Target: 1.000 Exemplos Anotados**

| Fase | Exemplos | Acurácia Esperada | Status |
|------|----------|-------------------|--------|
| **Piloto** | 100-200 | ~60-70% | Baseline |
| **Beta** | 200-500 | ~70-80% | Validação |
| **Produção** | 500-1.000 | **>80%** | ✅ Deploy |
| **Refinamento** | 1.000+ | >85% | Melhoria contínua |

### **Distribuição Ideal de Labels**

- **Autêntico**: 40-50% (movimento cultural genuíno)
- **Comercial**: 25-30% (campanhas de marketing)
- **Apropriação**: 15-20% (descontextualização cultural)
- **Misto**: 5-10% (híbrido)

---

## 🔬 **Features Utilizadas**

### **1. Embeddings BERTimbau (768 dims)**
- Modelo: `neuralmind/bert-base-portuguese-cased`
- Captura semântica e contexto cultural brasileiro
- Pré-treinado em corpus português BR

### **2. Features Heurísticas (11 features)**

| Feature | Descrição | Range |
|---------|-----------|-------|
| `momentum_norm` | Score de momentum normalizado | 0-1 |
| `sentiment_norm` | Sentimento médio normalizado | 0-1 |
| `volume_log` | Volume em escala logarítmica | 0-∞ |
| `velocity_norm` | Velocidade de crescimento | 0-1 |
| `source_diversity` | Diversidade de fontes | 0-1 |
| `region_coverage` | Cobertura regional | 0-1 |
| `has_youtube` | Presença no YouTube | 0/1 |
| `has_reddit` | Presença no Reddit | 0/1 |
| `has_trends` | Aparece no Google Trends | 0/1 |
| `momentum_x_sentiment` | Interação momentum × sentiment | 0-∞ |
| `volume_x_velocity` | Interação volume × velocity | 0-∞ |

**Total: 779 features** (768 embeddings + 11 heurísticas)

---

## 📊 **Workflow Completo**

### **Mês 1-2: Coleta e Anotação (Fevereiro-Março 2026)**

```bash
# Semana 1: Coletar primeiros 100 sinais
# - Executar WeakSignalDetector em diversos contextos
# - AutoCollector salva automaticamente

# Semana 2-4: Anotar 100 sinais
python products/ml_training/annotation_tool.py --batch 25
# (4 sessões de 25 sinais cada)

# Semana 5-8: Coletar + anotar mais 400 sinais
# Target: 500 sinais anotados até fim de março
```

### **Mês 3: Treino e Validação (Abril 2026)**

```bash
# Treinar modelo com 500 exemplos
python products/ml_training/train_classifier.py --tune

# Validar performance (target: F1 > 0.75)
# Se F1 < 0.75: anotar mais 200 exemplos
```

### **Mês 4-6: Produção (Maio-Julho 2026)**

```python
# Integrar no WeakSignalDetector
from products.ml_training.train_classifier import AuthenticityClassifier

detector = WeakSignalDetector()
classifier = AuthenticityClassifier.load('models/authenticity_classifier.pkl')

# Em _analyze_term_signals(), adicionar:
for signal in signals:
    result = classifier.predict(
        signal.termo,
        momentum=signal.current_momentum,
        sentiment=signal.sentiment_positivo,
        ...
    )
    signal.authenticity_score = result['confidence']
    signal.authenticity_label = result['label']
```

---

## 🔧 **Troubleshooting**

### **Erro: "Nenhum dado anotado encontrado"**
```bash
# Verificar estatísticas
python products/ml_training/annotation_tool.py --stats

# Se total_annotated = 0, anotar primeiro:
python products/ml_training/annotation_tool.py --batch 50
```

### **Erro: "Dataset muito pequeno"**
```bash
# Mínimo recomendado: 100 exemplos
# Ideal para produção: 500+ exemplos

# Verificar progresso:
python products/ml_training/annotation_tool.py --stats
# Output: "Progresso: 15.0% de 1.000"
```

### **Modelo com baixa acurácia (<70%)**
1. **Anotar mais exemplos** (target: 500+)
2. **Balancear dataset** (evitar 90% de uma classe)
3. **Tunar hiperparâmetros**: `--tune`
4. **Revisar qualidade das anotações**: `--review`

---

## 🎓 **Boas Práticas de Anotação**

### ✅ **DO:**
- Ler todo o contexto antes de classificar
- Usar campo "Notas" para casos ambíguos
- Anotar em sessões de 25-50 sinais (evitar fadiga)
- Revisar anotações periodicamente: `--review`
- Manter consistência de critérios

### ❌ **DON'T:**
- Anotar mais de 100 sinais de uma vez (fadiga)
- Usar apenas informação do texto (ignorar métricas)
- Classificar sinais ambíguos sem notas
- Desbalancear classes (>70% de uma label)

---

## 🚀 **Próximos Passos**

- [ ] Coletar 1.000 sinais anotados (Q1-Q2 2026)
- [ ] Atingir F1 > 0.80 no teste
- [ ] Integrar classificador no WeakSignalDetector
- [ ] Dashboard: exibir `authenticity_score` e badges
- [ ] API endpoint: `/api/classify-authenticity`
- [ ] Retreino mensal com novos dados

---

## 📞 **Suporte**

**Documentação**: `products/ml_training/README.md` (este arquivo)

**Scripts**:
- Coleta: `dataset_collector.py`, `auto_collector.py`
- Anotação: `annotation_tool.py`
- Treino: `train_classifier.py`

**Última Atualização**: 01/02/2026  
**Versão**: 1.0 - Sistema Completo de ML Training
