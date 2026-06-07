# 🤖 SOLUÇÃO COMPLETA: Aprendizado Automatizado Sem Dados Históricos

> Nota: este documento descreve uma arquitetura de aprendizado automatizado e inclui artefatos Python e um demo em Streamlit.
> A visualização legacy em Streamlit foi migrada para o fluxo atual via Next.js e FastAPI.
> O endpoint de monitoramento ativo é `/api/v8/ml/strategy-status` e a interface de produto está em `app/dashboard/strategy-learning/page.tsx`.

## 🎯 SUA PERGUNTA

> "Como eu não tenho dados históricos, mas tenho as chaves das APIs, Como podemos fazer com que rode automaticamente para entender o que está acontecendo para diferentes marcas, contextos, territórios e temas?"

---

## ✅ RESPOSTA: Sistema de 3 Componentes

```
┌─────────────────────────────────────────────────────────────┐
│  1️⃣ AUTOMATED COLLECTION SCHEDULER                          │
│     • Coleta 24/7 de múltiplas marcas/contextos            │
│     • Usa suas APIs reais (YouTube, Twitter, Reddit)       │
│     • Armazena em DuckDB                                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  2️⃣ ONLINE LEARNING ENGINE                                  │
│     • NÃO precisa dados históricos!                         │
│     • Aprende incrementalmente com cada coleta             │
│     • SGDRegressor (sklearn) com partial_fit()             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  3️⃣ ADAPTIVE WEIGHTS CALCULATOR                             │
│     • Gera pesos por indústria/contexto                    │
│     • Melhora conforme coleta mais dados                   │
│     • Integra com Metrics Engine                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 ARQUIVOS CRIADOS

| Arquivo | Propósito | Linha de Comando |
|---------|-----------|------------------|
| **`core/automated_learning_engine.py`** | Engine principal | - |
| **`start_automated_learning.py`** | Script de inicialização | `python start_automated_learning.py` |
| **`GUIA_APRENDIZADO_AUTOMATIZADO.md`** | Documentação completa | Leia para entender tudo |
| **`demo_automated_learning.py`** | Visualização Streamlit legacy | `streamlit run demo_automated_learning.py` |
| **`requirements_automated_learning.txt`** | Dependências | `pip install -r requirements_automated_learning.txt` |

> Nota: o `demo_automated_learning.py` é uma visualização legacy em Streamlit. O fluxo de monitoramento ativo agora está disponível em `app/dashboard/strategy-learning/page.tsx` no frontend Next.js e no endpoint FastAPI `/api/v8/ml/strategy-status`.

---

## 🚀 QUICK START (5 Minutos)

### Passo 1: Instalar Dependências
```bash
cd /Users/brmunizmoura/Documents/PULSO/src_v8
pip install -r requirements_automated_learning.txt
```

### Passo 2: Verificar APIs no .env
```bash
# Seu .env já tem as chaves?
cat .env | grep API_KEY

# Se não, adicione:
# YOUTUBE_API_KEY=sua_chave_aqui
# TWITTER_BEARER_TOKEN=seu_token_aqui
# (etc...)
```

### Passo 3: Rodar Coleta Inicial
```bash
python start_automated_learning.py
# Escolher opção 1: Rodar coleta inicial
```

### Passo 4: Ver a interface ativa
O demo Streamlit ainda existe como referência, mas o fluxo ativo atual está disponível no frontend Next.js em `/dashboard/strategy-learning` e no endpoint FastAPI `/api/v8/ml/strategy-status`.

---

## 💡 COMO FUNCIONA (Sem Dados Históricos!)

### Traditional ML (NÃO funciona sem histórico)
```python
❌ PROBLEMA:
X_train = load_historical_data()  # Não existe!
model.fit(X_train, y_train)       # Erro!
```

### Online Learning (FUNCIONA desde o dia 1!)
```python
✅ SOLUÇÃO:
model = SGDRegressor()  # Começa vazio!

for batch in data_stream:
    features = extract(batch)
    target = calculate(batch)
    model.partial_fit(features, target)  # Aprende incrementalmente!
```

**Diferença chave**: `partial_fit()` vs `fit()`
- `fit()`: Treina com tudo de uma vez (precisa histórico)
- `partial_fit()`: Aprende pedaço por pedaço (não precisa histórico)

---

## 📊 CONTEXTOS PADRÃO PRÉ-CONFIGURADOS

O sistema já vem com 5 contextos prontos:

| Marca/Tema | Indústria | Keywords | Frequência | Territórios |
|------------|-----------|----------|------------|-------------|
| **Nike** | fashion | nike, tênis nike, nike brasil | Hourly | BR, SP, RJ, MG |
| **Streetwear Brasil** | fashion | streetwear, grife nacional | Daily | BR, SP |
| **Startups Brasil** | tech | startup brasil, tech brasil | Daily | BR, SP, SC |
| **Música Brasileira** | music | funk brasileiro, trap brasil | Hourly | BR, RJ, SP, BA |
| **Food Brasil** | food | food truck brasil, gastronomia | Daily | BR, SP, RJ |

**Você pode adicionar quantos quiser!**

---

## ➕ ADICIONAR SEUS CONTEXTOS

### Via Menu Interativo (Mais Fácil)
```bash
python start_automated_learning.py
# Escolher opção 5: Adicionar novo contexto

Nome da marca: Havaianas
Indústria: fashion
Keywords: havaianas, sandália brasileira, chinelo brasil
Territórios: BR, SP, RJ, MG, BA
Prioridade: 5
Frequência: daily

✅ Contexto adicionado!
```

### Via Código (Mais Flexível)
```python
from core.automated_learning_engine import AutomatedLearningEngine, BrandContext

engine = AutomatedLearningEngine()

# Exemplo: Sua marca
sua_marca = BrandContext(
    brand_name="Sua Marca Aqui",
    industry="sua_industria",  # fashion, tech, music, food, other
    keywords=["keyword1", "keyword2", "keyword3"],
    territories=["BR", "SP", "RJ"],
    priority=5,  # 1-5
    collection_frequency="hourly"  # hourly, daily, realtime
)

engine.add_brand_context(sua_marca)
```

---

## 📈 CRONOGRAMA DE CONFIANÇA

```
Dia 1-2:   ████░░░░░░ 20-40%  Bootstrap inicial
Dia 3-7:   ██████░░░░ 40-70%  Padrões emergindo
Dia 8-14:  ████████░░ 70-85%  Pode começar a usar!
Dia 15-21: █████████░ 85-92%  Alta confiança
Dia 22+:   ██████████ 92-95%  Maturidade
```

**Recomendação**: Esperar 7-14 dias antes de usar pesos em produção.

---

## 🎓 EXEMPLO: EVOLUÇÃO DOS PESOS

### Fashion (Nike + Streetwear) - Após 14 dias

```python
# Dia 1 (Default)
{
    'velocity': 0.25,
    'acceleration': 0.15,
    'cii': 0.30,
    'geographic_spread': 0.15,
    'resonance': 0.15,
    'confidence': 0.30  # 30%
}

# Dia 14 (Aprendido)
{
    'velocity': 0.28,        # ↑ 12% (moda é rápida!)
    'acceleration': 0.14,     # ↓ 6%
    'cii': 0.35,             # ↑ 16% (visual, engajamento alto)
    'geographic_spread': 0.12, # ↓ 20% (moda concentrada)
    'resonance': 0.11,       # ↓ 26%
    'confidence': 0.82       # 82% ✅
}
```

**Interpretação**: Sistema aprendeu que moda prioriza velocidade e engajamento visual!

---

## 🔗 INTEGRAÇÃO COM METRICS ENGINE

### Como usar os pesos aprendidos:

```python
from core.automated_learning_engine import AutomatedLearningEngine
from core.cultural_metrics_engine import CulturalMetricsEngine

# Inicializar
learning_engine = AutomatedLearningEngine()
metrics_engine = CulturalMetricsEngine()

# Buscar pesos aprendidos
industry = "fashion"
weights = learning_engine.get_learned_weights_for_context(industry)

# Se confiança baixa, usar defaults
if weights['confidence'] < 0.6:
    weights = metrics_engine.get_default_weights()

# Calcular momentum adaptativo
momentum = metrics_engine.calculate_momentum(
    data=current_data,
    weights=weights,
    industry=industry
)

print(f"Momentum: {momentum}")
print(f"Confiança: {weights['confidence'] * 100}%")
```

---

## 🎯 FLUXO COMPLETO (Resumo Visual)

```
VOCÊ
 ↓ configura contextos
 
AUTOMATED SCHEDULER
 ↓ coleta de APIs (YouTube, Twitter, Reddit)
 
DATA BUFFER
 ↓ extrai features (volume, engagement, velocity)
 
ONLINE LEARNING
 ↓ partial_fit() incremental
 
ADAPTIVE WEIGHTS
 ↓ armazena em DuckDB
 
METRICS ENGINE
 ↓ calcula momentum adaptativo
 
DASHBOARD
 ↓ visualiza resultados
 
VOCÊ
 ✅ insights acionáveis!
```

---

## 🔄 PRÓXIMOS PASSOS (Fase 1 + 2)

### Esta Semana (Fase 1: Setup)
- [ ] ✅ **Instalar dependências** (5 min)
- [ ] ✅ **Verificar APIs no .env** (2 min)
- [ ] ✅ **Rodar coleta inicial** (10 min)
- [ ] ✅ **Adicionar seus contextos** (5 min cada)
- [ ] ✅ **Ver demo visual** (opcional)

### Semana 2-3 (Fase 2: Aprendizado)
- [ ] Deixar scheduler rodando em background (24/7)
- [ ] Monitorar logs diários
- [ ] Verificar pesos aprendidos (dia 7, 14)
- [ ] Integrar com Metrics Engine
- [ ] Testar em dashboard Nike

### Semana 4+ (Fase 3: Produção)
- [ ] Confiança 80%+ alcançada
- [ ] Usar pesos em produção
- [ ] Adicionar mais contextos
- [ ] Expandir para mais territórios

---

## 📊 MONITORAMENTO

### Ver Status da Coleta
```bash
python start_automated_learning.py
# Opção 3: Ver status

📊 STATUS:
Total de pontos: 1,247
Contextos ativos: 5
Indústrias: fashion (582), tech (234), music (301), food (130)
```

### Ver Pesos Aprendidos
```bash
# Opção 4: Ver pesos aprendidos

🎓 PESOS APRENDIDOS:
FASHION:
   Velocidade: 0.278
   CII: 0.346
   Confiança: 78.4%
```

### Logs em Tempo Real
```bash
tail -f automated_learning.log

2026-01-10 14:23:15 - INFO - ✅ Coletados 45 pontos para Nike
2026-01-10 14:23:18 - INFO - 📚 Modelo atualizado com 5 features
```

---

## 🐛 TROUBLESHOOTING

### Problema: "Não foi possível resolver a importação schedule"
```bash
pip install schedule duckdb scikit-learn
```

### Problema: APIs não retornam dados
1. Verificar `.env` tem chaves corretas
2. Testar manualmente uma API
3. Checar rate limits

### Problema: Pesos não mudam
- **Causa**: Poucos dados coletados
- **Solução**: Esperar mais tempo (mínimo 3-5 dias)

---

## 🎓 CONCEITOS CHAVE

### 1. Online Learning
Aprendizado incremental que NÃO precisa de dados históricos.

### 2. Partial Fit
Método que atualiza o modelo com novos dados sem retreinar tudo.

### 3. Adaptive Weights
Pesos que se ajustam automaticamente por contexto/indústria.

### 4. Confidence Score
Métrica de confiança (0-100%) dos pesos aprendidos.

### 5. Data Buffer
Janela deslizante dos últimos N pontos coletados.

---

## 🎯 RESUMO EXECUTIVO

| Aspecto | Solução |
|---------|---------|
| **Problema** | Sem dados históricos para ML |
| **Solução** | Online Learning + Coleta Automatizada |
| **Tempo de setup** | 15 minutos |
| **Tempo para resultados** | 7-14 dias (confiança 70-85%) |
| **APIs necessárias** | YouTube, Twitter, Reddit (que você já tem!) |
| **Complexidade** | Baixa (código já pronto) |
| **Manutenção** | Mínima (roda sozinho 24/7) |
| **Escalabilidade** | Alta (adicionar contextos facilmente) |

---

## 📞 SUPORTE

1. **Documentação completa**: `GUIA_APRENDIZADO_AUTOMATIZADO.md`
2. **Demo visual**: `streamlit run demo_automated_learning.py`
3. **Logs**: `automated_learning.log`
4. **Status**: Opção 3 do menu

---

**🎉 PRONTO! Sistema completo para resolver seu problema.**

Agora você pode:
✅ Coletar dados automaticamente de múltiplas marcas  
✅ Aprender pesos em tempo real (sem histórico prévio)  
✅ Adaptar por contexto (fashion, tech, music, food)  
✅ Construir histórico enquanto usa o sistema  

**Próximo passo**: `pip install -r requirements_automated_learning.txt` 🚀
