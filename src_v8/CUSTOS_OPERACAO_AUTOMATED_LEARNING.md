# 💰 CUSTOS DE OPERAÇÃO - AUTOMATED LEARNING ENGINE

## 📊 Resumo Executivo

| Componente | Custo Mensal | Observações |
|-----------|--------------|-------------|
| **APIs Externas** | R$ 200-800 | Variável por uso |
| **Infraestrutura** | R$ 50-150 | Cloud + Storage |
| **Total Estimado** | **R$ 250-950/mês** | Produção básica |

---

## 🔑 CUSTOS DE APIs (Principal)

### 1. YouTube Data API v3
**Status**: GRATUITA até limite

| Operação | Custo (quotas) | Limite Gratuito | Custo Adicional |
|----------|----------------|-----------------|-----------------|
| Search | 100 quotas/query | 10,000/dia | US$ 0 (gratuito) |
| Video details | 1 quota/vídeo | 10,000/dia | - |
| **Total coletas/dia** | ~100 queries | ✅ GRÁTIS | - |

**Estimativa**: **GRATUITO** (dentro do limite diário)

**⚠️ Se exceder**: US$ 0 (YouTube não cobra, mas bloqueia temporariamente)

---

### 2. Twitter/X API v2
**Status**: PAGO (API Free tier removida em 2023)

| Plano | Custo | Limits | Recomendação |
|-------|-------|--------|--------------|
| **Basic** | US$ 100/mês | 10K tweets/mês | ❌ Insuficiente |
| **Pro** | US$ 5,000/mês | 1M tweets/mês | ✅ Produção |
| **Enterprise** | Personalizado | Ilimitado | Para escala |

**Alternativa**: Usar **Reddit + YouTube** como principais, Twitter secundário.

**Estimativa**: 
- **Sem Twitter**: R$ 0
- **Com Twitter Pro**: R$ 25,000/mês (US$ 5,000)

**💡 Recomendação**: Começar SEM Twitter, adicionar depois se necessário.

---

### 3. Reddit API
**Status**: GRATUITA

| Operação | Limite Gratuito | Custo |
|----------|-----------------|-------|
| Posts | 60 requests/minuto | ✅ GRÁTIS |
| Comments | 60 requests/minuto | ✅ GRÁTIS |
| **Total** | ~86,400 requests/dia | ✅ GRÁTIS |

**Estimativa**: **GRATUITO**

---

### 4. Google Trends
**Status**: GRATUITA (sem API oficial)

| Método | Custo | Limitação |
|--------|-------|-----------|
| pytrends (não-oficial) | ✅ GRÁTIS | Rate limiting |
| Scraping | ✅ GRÁTIS | Não recomendado |

**Estimativa**: **GRATUITO**

---

### 5. NewsAPI
**Status**: FREEMIUM

| Plano | Custo | Limits |
|-------|-------|--------|
| **Developer** | Gratuito | 100 requests/dia |
| **Business** | US$ 449/mês | 250K requests/mês |

**Estimativa**: 
- **Gratuito**: Suficiente para testes
- **Produção**: R$ 2,245/mês (US$ 449)

**💡 Recomendação**: Usar tier gratuito inicialmente.

---

## 🖥️ CUSTOS DE INFRAESTRUTURA

### 1. Compute (Processamento)

#### Opção A: VPS Dedicado
| Provider | Especificações | Custo/mês |
|----------|----------------|-----------|
| **DigitalOcean** | 2 vCPU, 4GB RAM | US$ 24 (R$ 120) |
| **Linode** | 2 vCPU, 4GB RAM | US$ 20 (R$ 100) |
| **AWS EC2 t3.medium** | 2 vCPU, 4GB RAM | US$ 30 (R$ 150) |

**Recomendação**: DigitalOcean ou Linode para começar.

#### Opção B: Serverless (AWS Lambda + ECS)
| Componente | Custo |
|-----------|-------|
| Lambda (coletas periódicas) | ~US$ 5/mês |
| ECS Fargate (engine contínuo) | ~US$ 30/mês |
| **Total** | US$ 35/mês (R$ 175) |

---

### 2. Storage (Armazenamento)

#### DuckDB Local (Recomendado)
| Tipo | Capacidade | Custo |
|------|-----------|-------|
| Disco VPS | 100GB | Incluído no VPS |
| Backup S3 | 50GB | US$ 1.15/mês (R$ 5.75) |

#### Alternativa: PostgreSQL Gerenciado
| Provider | Especificações | Custo |
|----------|----------------|-------|
| **AWS RDS** | 20GB storage | US$ 15/mês (R$ 75) |
| **DigitalOcean DB** | 10GB storage | US$ 15/mês (R$ 75) |

**Recomendação**: DuckDB local + backup S3 (mais barato).

---

### 3. Monitoramento e Logs

| Serviço | Tier Gratuito | Custo Pago |
|---------|---------------|------------|
| **Datadog** | 5 hosts grátis | US$ 15/host |
| **NewRelic** | 100GB/mês grátis | US$ 0.30/GB |
| **CloudWatch** | 5GB logs grátis | US$ 0.50/GB |

**Estimativa**: **GRATUITO** (tier gratuito suficiente)

---

## 💻 CUSTOS DE DESENVOLVIMENTO (One-time)

| Item | Custo | Observação |
|------|-------|------------|
| Setup inicial | 8-16 horas | Incluído (código pronto) |
| Configuração APIs | 2-4 horas | Incluído (guias prontos) |
| Testes e ajustes | 4-8 horas | Primeira semana |
| **Total dev** | **14-28 horas** | Código já entregue |

**Se contratar dev**: R$ 100-200/hora = R$ 1,400-5,600 (one-time)

**✅ Você já tem**: Código completo pronto para usar!

---

## 📊 CENÁRIOS DE CUSTO

### 🟢 CENÁRIO 1: Teste/MVP (Mínimo)
```
APIs:
  ✅ YouTube: Gratuito
  ✅ Reddit: Gratuito
  ✅ Google Trends: Gratuito
  ✅ NewsAPI: Gratuito (tier básico)
  ❌ Twitter: Não usar

Infra:
  • DigitalOcean VPS: R$ 120/mês
  • S3 Backup: R$ 5/mês

TOTAL: R$ 125/mês
```

**Ideal para**: Provar conceito, primeiros clientes, MVP

---

### 🟡 CENÁRIO 2: Produção Básica (Recomendado)
```
APIs:
  ✅ YouTube: Gratuito
  ✅ Reddit: Gratuito
  ✅ Google Trends: Gratuito
  💰 NewsAPI Business: R$ 2,245/mês (opcional)
  ❌ Twitter: Não usar ainda

Infra:
  • AWS EC2 t3.medium: R$ 150/mês
  • DuckDB + S3 Backup: R$ 10/mês
  • CloudWatch: Gratuito

TOTAL: R$ 160/mês (sem NewsAPI)
TOTAL: R$ 2,405/mês (com NewsAPI)
```

**Ideal para**: Até 10 clientes, coleta 24/7

---

### 🔴 CENÁRIO 3: Produção Escala (Futuro)
```
APIs:
  ✅ YouTube: Gratuito
  ✅ Reddit: Gratuito
  💰 Twitter Pro: R$ 25,000/mês
  💰 NewsAPI Business: R$ 2,245/mês

Infra:
  • AWS ECS Fargate: R$ 500/mês
  • RDS PostgreSQL: R$ 200/mês
  • S3 + CloudFront: R$ 100/mês

TOTAL: R$ 28,045/mês
```

**Ideal para**: 50+ clientes, escala enterprise

---

## 🎯 RECOMENDAÇÃO PARA VOCÊ

### Fase 1: Setup (Semanas 1-2)
```bash
Custo: R$ 0/mês
Rodar localmente em seu computador
Usar apenas APIs gratuitas
```

**Ações**:
- Configurar em máquina local
- Testar com YouTube + Reddit + Google Trends
- Coletar primeiros 7-14 dias de dados

---

### Fase 2: MVP Cloud (Semanas 3-8)
```bash
Custo: R$ 120-150/mês
VPS básico + APIs gratuitas
Sem Twitter, sem NewsAPI pago
```

**Ações**:
- Migrar para DigitalOcean VPS (R$ 120/mês)
- Manter coleta 24/7
- Primeiros clientes beta

---

### Fase 3: Produção (Mês 3+)
```bash
Custo: R$ 150-300/mês
Baseado no volume de coletas
Adicionar NewsAPI se necessário
```

**Ações**:
- Escalar VPS se necessário
- Adicionar monitoramento
- Considerar Twitter Pro se validar valor

---

## 💡 OTIMIZAÇÕES DE CUSTO

### 1. Reduzir Frequência de Coleta
```python
# Ao invés de hourly:
collection_frequency="daily"  # Reduz 24x

# Economiza: Banda + Compute
```

### 2. Caching Inteligente
```python
# Cache por 6 horas
cache_ttl = 21600  # 6 horas

# Economiza: 75% de requests
```

### 3. Rate Limiting Agressivo
```python
# Esperar entre requests
time.sleep(2)  # 2 segundos

# Economiza: Evita banimento, reduz custos
```

### 4. Priorizar APIs Gratuitas
```python
apis = ["youtube", "reddit", "google_trends"]
# NÃO incluir: "twitter" (caro!)

# Economiza: R$ 25,000/mês
```

---

## 📈 ESCALABILIDADE DE CUSTOS

| Clientes | Coletas/dia | APIs | Infra | Total/mês |
|----------|-------------|------|-------|-----------|
| **1-5** | 50-100 | Grátis | R$ 120 | **R$ 120** |
| **5-10** | 100-300 | Grátis | R$ 150 | **R$ 150** |
| **10-20** | 300-500 | +NewsAPI | R$ 200 | **R$ 2,445** |
| **20-50** | 500-1000 | +Twitter | R$ 500 | **R$ 27,745** |
| **50+** | 1000+ | Enterprise | R$ 1000 | **R$ 50,000+** |

---

## 🎯 CONCLUSÃO

### ✅ PARA COMEÇAR (Hoje):
**Custo: R$ 0/mês**
- Rodar localmente
- APIs gratuitas (YouTube, Reddit, Trends)
- Coletar dados iniciais

### ✅ PARA PRODUÇÃO (Semana 3):
**Custo: R$ 120-150/mês**
- VPS básico
- Apenas APIs gratuitas
- Até 10 clientes

### ✅ PARA ESCALA (Mês 3+):
**Custo: R$ 150-300/mês**
- VPS otimizado
- NewsAPI se necessário
- 10-20 clientes

### ⚠️ EVITAR (Por enquanto):
**Twitter API Pro: R$ 25,000/mês**
- Muito caro para MVP
- Usar Reddit como alternativa
- Adicionar só se validar necessidade

---

## 📞 SUPORTE

Dúvidas sobre custos?
1. Comece com Fase 1 (R$ 0)
2. Escale conforme necessidade
3. Twitter só se realmente necessário

**Economia total vs usar todas APIs**: R$ 27,000/mês! 💰
