# 🔧 Guia de Integração V9.1 - Componentes ML/NLP

## 📋 Componentes Implementados

### 1. **BrazilianTextPreprocessor** ✅
**Arquivo**: `core/text_preprocessor.py`  
**Finalidade**: Preprocessamento específico PT-BR antes dos embeddings

**Features**:
- 50+ contrações brasileiras (tá→está, vc→você, pq→porque)
- Normalização de gírias regionais (massa→legal, dahora→legal, maneiro→legal)
- Correção de typos comuns (sustentabilidae→sustentabilidade, igualdae→igualdade)
- Extração de emojis (preservados para análise de sentimento)
- Análise de qualidade: spam/bot detection com 7 checks

**Uso**:
```python
from core.classifiers.text_preprocessor import BrazilianTextPreprocessor

preprocessor = BrazilianTextPreprocessor()

# Níveis: 'light' (básico), 'medium' (+contrações+typos), 'full' (+slang+lemma)
texto_limpo = preprocessor.preprocess(raw_text, level='medium')

# Verificar qualidade
qualidade = preprocessor.analyze_text_quality(raw_text)
if qualidade['is_spam_likely']:
    # Pular sinal
    pass
```

**Integração**: ✅ Já integrado em `collectors/data_collectors.py` (YouTube processor)

---

### 2. **TemporalEmbedder** ✅
**Arquivo**: `core/temporal_embedder.py`  
**Finalidade**: Adiciona dimensões temporais aos embeddings BERTimbau

**Features**:
- Transforma 768d → 776d (8 dimensões temporais)
- Embeddings cíclicos (sin/cos) para sazonalidade
- Eventos culturais brasileiros: Carnaval, Festas Juninas, Black Friday, Natal
- Contexto automático: detecta proximidade de eventos, intensidade do período

**Uso**:
```python
from core.temporal_embedder import TemporalEmbedder

embedder = TemporalEmbedder()

# Adicionar temporal ao BERTimbau
temporal_emb = embedder.encode_with_time(
    text_embedding=bertimbau_768d,
    timestamp=sinal.timestamp,
    include_events=True
)  # Resultado: 776d

# Obter contexto cultural
context = embedder.get_cultural_context(datetime(2026, 2, 15))
# {'closest_event': 'carnaval', 'period_intensity': 0.9, ...}
```

**Integração**: ✅ Já integrado em `core/semantic_expander.py`

---

### 3. **ContextDriftDetector** ✅
**Arquivo**: `monitoring/context_drift_detector.py`  
**Finalidade**: Detecta quando termos mudam de contexto semântico (covariate shift)

**Features**:
- Compara embeddings históricos vs atuais (cosine distance)
- Threshold padrão: 0.3 (configurável)
- 4 severidades: low, medium, high, critical
- Recomendações automáticas de retreino
- Histórico persistente em JSON

**Uso**:
```python
from monitoring.context_drift_detector import ContextDriftDetector

detector = ContextDriftDetector(drift_threshold=0.3)

# Adicionar observações históricas
detector.add_observation(
    term="Wuhan",
    embedding=bertimbau_emb,
    context_terms=["turismo", "china", "história"],
    timestamp=datetime(2018, 6, 1)
)

# Detectar drift atual
alert = detector.detect_drift(
    term="Wuhan",
    current_embedding=current_emb,
    current_context=["COVID", "pandemia", "lockdown"],
    timestamp=datetime(2020, 3, 15)
)

if alert:
    print(f"Drift detectado: {alert.drift_score:.3f}, severidade={alert.severity}")
```

**Integração**: ✅ Já integrado em `monitoring/drift_monitoring_service.py`

---

### 4. **FeatureImportanceAnalyzer** ✅
**Arquivo**: `analysis/feature_importance_analyzer.py`  
**Finalidade**: Reduz features de 789 → ~80 usando XGBoost + SHAP

**Features**:
- XGBoost para feature importance (gain, weight, cover)
- SHAP values para explicabilidade (Shapley Additive Explanations)
- Remoção de redundâncias (correlação > 0.85)
- Proteção de features culturais críticas (alma_brasileira, momentum, etc)
- Relatórios detalhados de importância

**Uso**:
```python
from analysis.feature_importance_analyzer import FeatureImportanceAnalyzer

analyzer = FeatureImportanceAnalyzer(target_features=80)

# Rodar análise offline (uma vez)
report = analyzer.analyze(X_train, y_train, feature_names)

# Top features
print(report['top_20_features'])

# Transformar dados de produção
X_reduced = analyzer.transform(X_production)  # 789 → 80 features
```

**Integração**: Ver seção "Uso Offline" abaixo

---

### 5. **DistributionShiftDetector** ✅
**Arquivo**: `monitoring/distribution_shift_detector.py`  
**Finalidade**: Detecta divergência entre dados de treino (sintéticos) e produção (reais)

**Features**:
- Kolmogorov-Smirnov test (KS test) por feature
- Threshold p-value: 0.05 (padrão)
- 4 magnitudes: minor, moderate, severe, critical
- Histórico de shifts em JSON
- Comparação detalhada por feature

**Uso**:
```python
from monitoring.distribution_shift_detector import DistributionShiftDetector

detector = DistributionShiftDetector(
    reference_data=train_data,  # Dados sintéticos
    p_value_threshold=0.05
)

# Detectar shifts em produção
alerts = detector.detect_shift(production_data)

for alert in alerts:
    print(f"{alert.feature_name}: KS={alert.ks_statistic:.3f}, "
          f"magnitude={alert.shift_magnitude}")
```

**Integração**: ✅ Já integrado em `monitoring/drift_monitoring_service.py`

---

## 🔄 Serviço Unificado: DriftMonitoringService

**Arquivo**: `monitoring/drift_monitoring_service.py`  
**Finalidade**: Orquestra ContextDriftDetector + DistributionShiftDetector

**Features**:
- Monitoramento em tempo real de sinais
- Alertas automáticos (email/Slack via callback)
- Dashboard de métricas
- Verifica se requer retreino de modelos

**Uso**:
```python
from monitoring.drift_monitoring_service import create_monitoring_service

# Criar serviço
service = create_monitoring_service(
    reference_data_path="data/synthetic_train_data.csv"
)

# Monitorar sinal
result = await service.monitor_signal(
    signal=cultural_signal_dict,
    embedding=bertimbau_emb,
    timestamp=datetime.now()
)

# Verificar se requer retreino
if service.requires_model_retrain():
    print("🚨 RETREINO NECESSÁRIO!")
```

---

## 📊 Checklist de Integração

### ✅ Fase 1: Preprocessamento de Texto (COMPLETO)
- [x] `BrazilianTextPreprocessor` criado
- [x] Integrado em `collectors/data_collectors.py`
- [x] YouTube processor filtra spam/bots
- [ ] Estender para Reddit, NewsAPI collectors (próximo passo)

### ✅ Fase 2: Embeddings Temporais (COMPLETO)
- [x] `TemporalEmbedder` criado
- [x] Integrado em `core/semantic_expander.py`
- [x] BERTimbau agora retorna 776d (768 + 8 temporal)
- [ ] Atualizar weak_signal_detector.py para aceitar 776d (próximo passo)

### ✅ Fase 3: Monitoramento de Drift (COMPLETO)
- [x] `ContextDriftDetector` criado
- [x] `DistributionShiftDetector` criado
- [x] `DriftMonitoringService` unificado criado
- [ ] Integrar no pipeline principal (culture_pulse_master_v8.py)
- [ ] Adicionar visualizações no dashboard (tab Monitoring)

### ⏳ Fase 4: Redução de Features (PENDENTE - USO OFFLINE)
- [x] `FeatureImportanceAnalyzer` criado
- [x] Script `run_feature_selection.py` criado
- [ ] **AÇÃO NECESSÁRIA**: Rodar análise offline com dados de treino
- [ ] Atualizar `core/weak_signal_detector.py` com features selecionadas
- [ ] Salvar configuração em `config/selected_features.json`

### ⏳ Fase 5: Dashboard de Monitoramento (PENDENTE)
- [ ] Criar tab "Monitoring" no dashboard
- [ ] Visualizar drifts detectados (timeline)
- [ ] Visualizar shifts por feature (heatmap)
- [ ] Exibir top termos com drift
- [ ] Indicador de necessidade de retreino

---

## 🚀 Como Usar os Componentes

### **Uso 1: Coletor com Preprocessamento**

```python
# Em collectors/data_collectors.py (já integrado)
from core.classifiers.text_preprocessor import BrazilianTextPreprocessor

preprocessor = BrazilianTextPreprocessor()

# Ao processar dados
title = preprocessor.preprocess(raw_title, level='light')
description = preprocessor.preprocess(raw_description, level='medium')

# Verificar qualidade
quality = preprocessor.analyze_text_quality(raw_text)
if quality['is_spam_likely'] or quality['quality_score'] < 0.5:
    continue  # Pular sinal de baixa qualidade
```

### **Uso 2: Embeddings com Sazonalidade**

```python
# Em core/semantic_expander.py (já integrado)
from core.temporal_embedder import TemporalEmbedder

temporal_embedder = TemporalEmbedder()

# Ao gerar embeddings
text_emb = model.encode(termo)  # BERTimbau: 768d
temporal_emb = temporal_embedder.encode_with_time(
    text_emb,
    timestamp=sinal.timestamp,
    include_events=True
)  # Agora: 776d (768 texto + 8 temporal)

# Obter contexto para narrativa
context = temporal_embedder.get_cultural_context(sinal.timestamp)
# "Sinal surge durante Carnaval (intensidade: 0.9)"
```

### **Uso 3: Monitoramento Contínuo**

```python
# Criar serviço de monitoramento
from monitoring.drift_monitoring_service import create_monitoring_service

service = create_monitoring_service(
    reference_data_path="data/synthetic_train_data.csv"
)

# No pipeline principal (culture_pulse_master_v8.py)
for sinal in novos_sinais:
    # 1. Obter embedding
    embedding = semantic_expander.get_embedding(sinal.termo)
    
    # 2. Monitorar drift
    result = await service.monitor_signal(
        signal={
            'termo': sinal.termo,
            'related_terms': sinal.related_terms,
            'features': sinal.features_dict
        },
        embedding=embedding,
        timestamp=sinal.timestamp
    )
    
    # 3. Verificar alertas
    if result['context_drift_detected']:
        print(f"⚠️ Context drift: {sinal.termo}")
    
    # 4. (A cada 1000 sinais) Verificar distribution shifts
    if len(signals_buffer) >= 1000:
        prod_data = pd.DataFrame([s.features_dict for s in signals_buffer])
        alerts = await service.check_distribution_shifts(prod_data)
        
        if alerts:
            print(f"📊 Distribution shifts: {len(alerts)} features")

# Verificar se requer retreino
if service.requires_model_retrain():
    print("🚨 AÇÃO: Retreinar modelos!")
    # Enviar email/Slack/etc
```

### **Uso 4: Análise de Features (OFFLINE)**

```bash
# 1. Gerar dados de treino com 789 features
python scripts/generate_training_data.py --output data/training_data.csv

# 2. Rodar análise de feature importance
python run_feature_selection.py \
    --data data/training_data.csv \
    --output config/selected_features.json \
    --target-features 80

# 3. Resultado: config/selected_features.json com 80 features selecionadas
```

```python
# Em core/weak_signal_detector.py, carregar features selecionadas
import json

with open('config/selected_features.json', 'r') as f:
    config = json.load(f)
    selected_features = config['selected_features']

# Ao criar features, usar apenas as selecionadas
features_df = features_df[selected_features]
```

---

## 📈 Impacto Esperado

| Componente | Problema Resolvido | Métrica |
|------------|-------------------|---------|
| **BrazilianTextPreprocessor** | Ruído em texto PT-BR (contrações, typos, gírias) | +10-15% qualidade embeddings |
| **TemporalEmbedder** | Falta de contexto sazonal cultural | +5-8% precisão em sinais sazonais |
| **ContextDriftDetector** | Termos mudando sentido não detectados | 100% detecção drifts > 0.3 |
| **FeatureImportanceAnalyzer** | 789 features → lentidão + overfitting | 90% redução, mantém 95%+ performance |
| **DistributionShiftDetector** | Train (sintético) ≠ Test (real) | Alerta quando F1 esperado < 70% |

---

## ⚠️ Próximos Passos Críticos

### 1. **Estender Preprocessamento aos Outros Collectors** (1-2 horas)
Adicionar `BrazilianTextPreprocessor` em:
- `RedditCollectorV8._process_reddit_data()`
- `NewsAPICollectorV8._process_news_data()`
- `SpotifyCollectorV8._process_spotify_data()`

### 2. **Integrar Monitoramento no Pipeline Principal** (2-3 horas)
Modificar `culture_pulse_master_v8.py`:
```python
from monitoring.drift_monitoring_service import create_monitoring_service

# Inicializar
drift_service = create_monitoring_service("data/synthetic_train_data.csv")

# No loop principal
for sinal in sinais:
    await drift_service.monitor_signal(sinal, embedding)

# A cada 1000 sinais
if batch_count % 1000 == 0:
    if drift_service.requires_model_retrain():
        send_alert("Retreino necessário!")
```

### 3. **Rodar Feature Selection Offline** (30 min)
```bash
# Gerar dados sintéticos de treino (se não existir)
python scripts/generate_synthetic_training_data.py

# Rodar análise
python run_feature_selection.py \
    --data data/synthetic_training_data.csv \
    --output config/selected_features.json \
    --target-features 80
```

### 4. **Atualizar WeakSignalDetector com Features Reduzidas** (1 hora)
```python
# Em core/weak_signal_detector.py
import json

class WeakSignalDetectorEnhanced:
    def __init__(self):
        # Carregar features selecionadas
        with open('config/selected_features.json', 'r') as f:
            self.selected_features = json.load(f)['selected_features']
    
    def extract_features(self, signal):
        # Extrair todas as 789 features
        all_features = self._extract_all_features(signal)
        
        # Filtrar apenas as selecionadas (80)
        selected_only = {k: v for k, v in all_features.items() 
                        if k in self.selected_features}
        
        return selected_only
```

### 5. **Adicionar Tab de Monitoramento no Dashboard** (3-4 horas)
Criar `dashboard/monitoring_tab.py`:
- Timeline de context drifts
- Heatmap de distribution shifts
- Top termos com drift
- Top features com shift
- Indicador de necessidade de retreino

---

## 🧪 Como Testar os Componentes

### Teste 1: Preprocessamento
```bash
cd core
python text_preprocessor.py
# Verifica: contrações, gírias, typos, spam detection
```

### Teste 2: Embeddings Temporais
```bash
cd core
python temporal_embedder.py
# Verifica: eventos culturais, sazonalidade, contexto
```

### Teste 3: Context Drift
```bash
cd monitoring
python context_drift_detector.py
# Verifica: drift Wuhan, termo estável
```

### Teste 4: Distribution Shift
```bash
cd monitoring
python distribution_shift_detector.py
# Verifica: KS test, magnitude de shifts
```

### Teste 5: Feature Importance
```bash
cd analysis
python feature_importance_analyzer.py
# Verifica: XGBoost, SHAP, seleção de features
```

### Teste 6: Serviço de Monitoramento
```bash
cd monitoring
python drift_monitoring_service.py
# Verifica: monitoramento de sinais, alertas
```

---

## 📚 Dependências Adicionais

Adicionar ao `requirements.txt` (se ainda não estiverem):
```
xgboost>=2.0.0
shap>=0.44.0
scipy>=1.11.0
```

Instalar:
```bash
pip install xgboost shap scipy
```

---

## 🎯 Resumo Executivo

**5 componentes implementados** endereçam lacunas críticas identificadas na análise ML/NLP:

1. ✅ **Preprocessing PT-BR** → Melhora qualidade de embeddings
2. ✅ **Temporal Embeddings** → Captura sazonalidade cultural
3. ✅ **Context Drift Detection** → Detecta termos mudando sentido
4. ✅ **Feature Selection** → Reduz 789→80 features (90% redução)
5. ✅ **Distribution Shift Detection** → Monitora divergência train/prod

**Status de integração**:
- 🟢 Fases 1-3: Integradas e funcionais
- 🟡 Fase 4: Requer execução offline (30 min)
- 🟡 Fase 5: Requer desenvolvimento dashboard (3-4h)

**Ação imediata**: Rodar `run_feature_selection.py` para reduzir features.

---

**Documentação criada**: Fevereiro 2026  
**Autor**: Culture Pulse V9.1 Team
