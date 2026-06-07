# � Sistema de Alertas Unificado - Culture Pulse V9.0

## 🎯 **ARQUITETURA CONSOLIDADA V9.0**

### ✅ **Estrutura Unificada:**

```
alerts/
├── __init__.py                 # 📦 Exports principais
├── alert_manager.py           # 🧠 Core: Lógica principal de alertas  
├── alert_rules.py             # 📋 Regras: Tipos, níveis e validações
├── config.py                  # ⚙️ Config: Configurações centralizadas
├── notification_channels.py   # 📢 Canais: Email, Slack, Webhook
├── streamlit_interface.py     # 🎨 UI LEGADO: Interface Streamlit antigo (migrar para Next.js)
├── api_endpoints.py           # 🔌 API: Endpoints FastAPI
├── tests/                     # 🧪 Testes unitários
└── alerts.md                  # 📖 Esta documentação
```

> ⚠️ `alerts/streamlit_interface.py` é uma interface legada baseada em Streamlit. A implementação de alertas deve ser migrada para a interface Next.js atual, consumindo `alerts/api_endpoints.py` e o backend consolidado.

### 🔄 **Migração dos Arquivos Antigos:**

| Arquivo Antigo | Novo Local | Status |
|----------------|------------|---------|
| `core/alert_system.py` | `alerts/alert_manager.py` | ✅ Migrado |
| `alerts/alerts.py` | `alerts/streamlit_interface.py` | ✅ Migrado |
| `api/endpoints/alerts.py` | `alerts/api_endpoints.py` | ✅ Migrado |

---

## 🎯 **FUNCIONALIDADES CONSOLIDADAS**

### 🧠 **Core Alert Manager** (`alert_manager.py`)
- **Sistema de regras avançado** com thresholds configuráveis
- **Processamento assíncrono** de alertas em tempo real
- **Histórico completo** com persistência
- **Cache inteligente** para performance
- **Rate limiting** e cooldowns
- **Monitoramento de sistema** integrado

### 📋 **Sistema de Regras** (`alert_rules.py`)
- **12 tipos de alerta**:
  - 🔥 Alto/Baixo Momentum
  - 😊😞 Sentimento Positivo/Negativo  
  - 📈📉 Picos/Quedas de Volume
  - 🎯⚠️ Alto/Baixo Consenso
  - 📊 Tendências Emergentes
  - 🔧 Performance de Sistema
  - 💼 Métricas de Negócio

- **4 níveis de severidade**:
  - ℹ️ **INFO**: Informativo
  - ⚠️ **WARNING**: Atenção necessária
  - ❌ **ERROR**: Problema detectado
  - � **CRITICAL**: Ação imediata necessária

### ⚙️ **Configurações Centralizadas** (`config.py`)
- **Configurações por ambiente**: Development, Staging, Production
- **Thresholds personalizáveis** para cada tipo de alerta
- **Configurações de notificação** unificadas
- **Rate limiting** e cooldowns configuráveis
- **Variables de ambiente** suportadas

### 📢 **Canais de Notificação** (`notification_channels.py`)
- **Email**: SMTP configurável
- **Slack**: Webhook integration
- **Webhook**: Endpoints customizados
- **Dashboard**: Notificações em tempo real
- **API**: Integração REST/WebSocket

---

## � **COMO USAR O SISTEMA UNIFICADO**

### 1. **Import Único e Simples:**
```python
# ✅ NOVO: Import limpo e centralizado
from alerts import get_alert_manager, AlertType, AlertLevel

# Obter manager configurado
manager = get_alert_manager()
```

### 2. **Configuração de Alertas:**
```python
from alerts import configure_alerts, AlertConfig

# Configuração personalizada
config = AlertConfig()
config.thresholds.high_momentum = 85.0
config.notifications.email_enabled = True

# Aplicar configuração
configure_alerts(config)
```

### 3. **Criação de Alertas:**
```python
from alerts.alert_rules import AlertFactory

# Alerta cultural
alert = AlertFactory.create_cultural_alert(
    AlertType.HIGH_MOMENTUM,
    term="inovação",
    value=87.5,
    threshold=80.0,
    level=AlertLevel.WARNING
)

# Enviar alerta
manager.add_alert(alert)
```

### 4. **Interface Streamlit:**
```python
from alerts.streamlit_interface import show_alerts_dashboard

# Em sua aplicação Streamlit
def main():
    show_alerts_dashboard()
```

### 5. **API Endpoints:**
```python
from alerts.api_endpoints import alerts_router

# Em sua FastAPI app
app.include_router(alerts_router, prefix="/api/alerts")
```

---

## 🎨 **INTERFACE STREAMLIT OTIMIZADA**

### **� Tab Alertas:**
- **Alertas em tempo real** com cores e ícones
- **Configurações visuais** de thresholds
- **Histórico completo** com filtros
- **Estatísticas rápidas** (total, tipos, hoje)
- **Actions** (resolver, silenciar, escalar)

### **⚙️ Configurações Avançadas:**
```python
# Thresholds personalizáveis
🔥 Alto Momentum: 50-100 (padrão: 80)
😞 Sentimento Negativo: -1.0 a -0.5 (padrão: -0.5)  
📈 Pico de Volume: 50-200 (padrão: 100)
🎯 Alto Consenso: 60-95 (padrão: 75)
⚠️ Baixo Consenso: 10-50 (padrão: 30)
```

### **📊 Histórico e Análise:**
- **Últimos 50 alertas** armazenados
- **Filtros por tipo, nível, data**
- **Estatísticas por período**
- **Gráficos de tendências**
- **Export para CSV/JSON**

---

## 🔌 **API REST COMPLETA**

### **Endpoints Disponíveis:**

```bash
# Listar alertas
GET /api/alerts/

# Obter alerta específico  
GET /api/alerts/{alert_id}

# Criar alerta
POST /api/alerts/

# Resolver alerta
PUT /api/alerts/{alert_id}/resolve

# Configurações
GET /api/alerts/config
PUT /api/alerts/config

# Estatísticas
GET /api/alerts/stats

# WebSocket para tempo real
WS /api/alerts/ws
```

### **WebSocket para Tempo Real:**
```javascript
// Cliente JavaScript
const ws = new WebSocket('ws://localhost:8000/api/alerts/ws');
ws.onmessage = (event) => {
    const alert = JSON.parse(event.data);
    console.log('Novo alerta:', alert);
};
```

---

## 📈 **MÉTRICAS E MONITORAMENTO**

### **📊 Estatísticas Automáticas:**
- **Taxa de alertas** por minuto/hora/dia
- **Distribuição por tipo** e nível
- **Tempo médio de resolução**
- **Alertas falsos positivos**
- **Performance do sistema**

### **🔍 Debug e Logs:**
```python
# Logs estruturados
from alerts import get_alert_manager

manager = get_alert_manager()
stats = manager.get_stats()

print(f"Alertas ativos: {stats['active_alerts']}")
print(f"Taxa de alertas/hora: {stats['alerts_per_hour']}")
print(f"Tempo médio resolução: {stats['avg_resolution_time']}min")
```

---

## 🎯 **VANTAGENS DA CONSOLIDAÇÃO**

### ✅ **Organização e Manutenção:**
- **� Pasta única**: Tudo relacionado a alertas em `alerts/`
- **🔧 Manutenção simples**: Mudanças em um local apenas
- **📦 Imports limpos**: `from alerts import AlertManager`
- **🧪 Testes centralizados**: Suite unificada em `alerts/tests/`

### ✅ **Performance e Escalabilidade:**
- **⚡ Cache inteligente**: Redis/Local para alertas frequentes
- **🔄 Processamento assíncrono**: Múltiplos alertas simultâneos
- **📊 Rate limiting**: Evita spam de alertas
- **🎯 Cooldowns configuráveis**: Por tipo de alerta

### ✅ **Flexibilidade e Configuração:**
- **⚙️ Configurações por ambiente**: Dev/Staging/Prod
- **📋 Regras customizáveis**: Thresholds, operadores, cooldowns
- **📢 Múltiplos canais**: Email, Slack, Webhook, Dashboard
- **🎨 Interface rica**: Streamlit + API REST + WebSocket

---

## � **MIGRAÇÃO AUTOMÁTICA**

O sistema detecta automaticamente imports antigos e redireciona:

```python
# ❌ ANTIGO (ainda funciona)
from core.alert_system import get_alert_manager

# ✅ NOVO (recomendado)  
from alerts import get_alert_manager

# 🔄 REDIRECIONAMENTO AUTOMÁTICO
# Os imports antigos continuam funcionando durante a transição
```

---

## 🎉 **RESULTADO FINAL utilizando o arquivo 'python test_integration_simple.py'**

### **Sistema Unificado e Poderoso:**
- ✅ **12 tipos de alertas** com 4 níveis de severidade
- ✅ **Interface Streamlit** moderna e responsiva  
- ✅ **API REST completa** com WebSocket em tempo real
- ✅ **Configurações flexíveis** por ambiente
- ✅ **Múltiplos canais** de notificação
- ✅ **Cache e performance** otimizados
- ✅ **Testes e monitoramento** integrados

### **Imports Simples e Intuitivos:**
```python
from alerts import get_alert_manager, AlertType, AlertLevel
from alerts.streamlit_interface import show_alerts_dashboard  
from alerts.api_endpoints import alerts_router
```

**🎊 O Culture Pulse V9.0 agora possui um sistema de alertas moderno, unificado e altamente configurável!**

### 📊 **Sistema de Relatórios Simplificado**
- **Arquivo:** `dashboard/reports.py`
- **📋 4 tipos de relatórios:**
  - 📋 **Resumo Executivo** - Conciso para executivos
  - 📊 **Análise Detalhada** - Relatório técnico completo
  - 📈 **Relatório Comparativo** - Comparação entre termos/períodos
  - 🔍 **Análise de Tendências** - Foco em tendências temporais

- **📄 Formato de exportação em PDF:**
  - PDF em formato texto estruturado
  - Formatação rica com emojis e seções
  - Download imediato via botão
  - Nome do arquivo automático com timestamp

- **💡 Geração automática de insights e recomendações:**
  - Insights baseados em momentum, volume e sentimento
  - Recomendações automáticas baseadas em dados
  - Análise por plataforma detalhada
  - Distribuições de momentum e sentimento

### 🎛️ **Sistema de tabs navegável**
- **Arquivo:** `dashboard/culture_pulse_dashboard.py`
- **Tabs principais:**
  - 📊 **Análise** - Visualização principal dos dados
  - 🚨 **Alertas** - Sistema de alertas em tempo real
  - 📋 **Relatórios** - Geração e download de relatórios
  - 📈 **Histórico** - Histórico completo de análises

## 🎯 **OTIMIZAÇÕES REALIZADAS**

### ⚡ **Performance:**
- ❌ Removido sistema de autenticação complexo
- ❌ Removido múltiplos formatos de exportação
- ❌ Removido configurações avançadas desnecessárias
- ✅ Mantido apenas funcionalidades essenciais
- ✅ Interface mais rápida e responsiva

### 🎨 **Interface:**
- ✅ **Cores e ícones** para alertas
- ✅ **Navegação por tabs** simples
- ✅ **Configurações visuais** de thresholds
- ✅ **Histórico visual** com métricas
- ✅ **Download direto** de relatórios

### 🔧 **Funcionalidades Mantidas:**
- ✅ **5 tipos de alertas** configuráveis
- ✅ **Histórico completo** de alertas
- ✅ **Thresholds personalizáveis**
- ✅ **4 tipos de relatórios**
- ✅ **Exportação PDF**
- ✅ **Insights automáticos**
- ✅ **Sistema de tabs**

## 🚀 **COMO USAR**

### 1. **Acesso:**
```
http://localhost:8501
```

### 2. **Análise Cultural:**
- Configure termo na sidebar
- Clique "Iniciar Análise Cultural"
- Navegue pelas tabs

### 3. **Tab Alertas (🚨):**
- Visualize alertas coloridos com ícones
- Configure thresholds no expander "Configurações"
- Veja histórico completo no expander "Histórico"

### 4. **Tab Relatórios (📋):**
- Escolha tipo de relatório (4 opções)
- Clique "Gerar Relatório"
- Faça download do PDF formatado

### 5. **Tab Histórico (📈):**
- Veja estatísticas de todas as análises
- Limpe histórico se necessário

## 🎉 **RESULTADO FINAL**

### ✅ **Sistema Simplificado e Rápido:**
- Interface visual com cores e ícones ✅
- Histórico completo de alertas ✅
- Configurações personalizáveis por threshold ✅
- 4 tipos de relatórios ✅
- Formato de exportação em PDF ✅
- Geração automática de insights e recomendações ✅
- Sistema de tabs navegável ✅

### 🚀 **Performance Otimizada:**
- Carregamento muito mais rápido
- Interface mais responsiva
- Apenas funcionalidades essenciais
- Navegação fluida entre tabs

### 💡 **Foco nas Funcionalidades Solicitadas:**
- Removido complexidade desnecessária
- Mantido todas as funcionalidades principais
- Interface moderna e intuitiva
- Sistema completamente funcional

## 📋 **COMO USAR O SISTEMA**

```python
# Sistema unificado e limpo
from alerts import get_alert_manager, AlertType

# Obter e configurar alertas
manager = get_alert_manager()
manager.add_rule(AlertType.HIGH_MOMENTUM, threshold=80)

# Criar alerta
manager.create_system_alert(
    AlertType.SYSTEM_PERFORMANCE,
    "api_response_time",
    "API lenta detectada",
    AlertLevel.WARNING
)

# Interface Streamlit
from alerts.streamlit_interface import show_alerts_dashboard
show_alerts_dashboard()

# API endpoints
from alerts.api_endpoints import alerts_router
app.include_router(alerts_router, prefix="/api/alerts")
```

---


**💡 Conclusão**: Consolidação em `alerts/` com arquitetura modular, imports limpos e responsabilidades bem definidas.