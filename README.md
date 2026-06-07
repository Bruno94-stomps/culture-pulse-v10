# 🧠 Culture Pulse V8.0 - Inteligência Cultural Brasileira

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Deploy](https://img.shields.io/badge/Deploy-Auto-brightgreen.svg)](https://github.com/your-repo/actions)

## 🔧 Resumo das Alterações de Arquitetura e ML

- Autenticação FastAPI reforçada: `FASTAPI_TOKEN` obrigatório e o fallback de demo auth foi removido em produção.
- Backend FastAPI configurado para deployment Docker no Railway; `FASTAPI_TOKEN` deve ser definido como secret do Railway no serviço backend.
- Frontend Next.js alinhado com backend via variáveis de ambiente `NEXT_PUBLIC_FASTAPI_URL` e `PROJECT_ANALYSIS_FASTAPI_URL`.
- Plano de ML atualizado para foco em `BusinessContext`, validação de fluxo de projeto e health checks de ML, com documentação central em `src_v8/autonomous_agent/ml_foundation/ML_PIPELINE_REFINEMENT_PLAN.md`.
- Documentação consolidada para garantir que o deploy use os secrets corretos e evite tokens de demo.

> **Sistema avançado de análise cultural brasileira com 8 APIs integradas, 15 círculos culturais e dashboard interativo.**

## 🚀 **Deploy Rápido**

### Cloudflare Pages (Frontend)
Deploy do frontend Next.js está alinhado com Cloudflare Pages para alta disponibilidade e performance.

### Railway (Backend)
Deploy do backend FastAPI em imagem Docker pelo Railway, que suporta contêineres e serviço gerenciado.
No Railway, o backend FastAPI deve receber o segredo `FASTAPI_TOKEN` como variável de ambiente no painel de Environment / Secrets do serviço.
Esse token é lido pelo app em runtime e deve ser um token real de produção, não um valor de demo.

### Supabase (Banco de Dados)
O banco de dados é hospedado no Supabase, com autenticação e persistência de `projects`, `profiles` e `cultural_signals`.

---

## 📋 **Visão Geral**

Culture Pulse V8.0 é uma plataforma de **inteligência cultural brasileira** que analisa dados de múltiplas fontes para gerar insights sobre comportamentos, tendências e valores culturais do Brasil.

### 🎯 **Principais Funcionalidades**

- **📊 8 APIs Integradas**: YouTube, Reddit, Spotify, NewsAPI, IBGE, Instagram, Meetup, Google Trends
- **🔵 15 Círculos Culturais**: Framework proprietário de análise cultural brasileira
- **🧠 Scores Culturais**: Cultural, Alma Brasileira, TF-IDF, IICB (Índice Integrado)
- **🎨 Dashboard Interativo**: Frontend Next.js com visualizações avançadas
- **🕸️ Grafos Culturais**: Análise de relacionamentos entre termos culturais
- **📄 Relatórios Executivos**: Insights automáticos e recomendações estratégicas

---

## 🏗️ **Arquitetura do Sistema**

```mermaid
graph TB
    A[Frontend Next.js] --> B[Cloudflare Pages]
    A --> C[FastAPI Backend]
    C --> D[Railway (Docker Container)]
    C --> E[Supabase Database]
    E --> F[projects / profiles / cultural_signals]
    C --> G[8 APIs Externas]
    G --> H[Processamento Cultural]
    H --> I[Scores & Métricas]
```

### 📦 **Componentes Principais**

- **`culturepulse-web/`** - Frontend Next.js
- **`src_v8/api/`** - Backend FastAPI
- **`src_v8/core/`** - Processamento cultural e scores
- **`src_v8/data/`** - Pipeline de dados e cache
- **`src_v8/config/`** - Configurações do sistema

---

## 🧠 **Machine Learning e Insights**

Este projeto já inclui uma base de ML local e um plano de evolução para um motor de insights de negócio.

### O que já está disponível
- `src_v8/api/endpoints/ml.py` expõe o router `/api/v8/ml`
- endpoint de saúde: `GET /api/v8/ml/health`
- status do engine: `GET /api/v8/ml/strategy-status`
- análise avançada de perfil: `POST /api/v8/ml/analyze/cultural-profile`
- insights de negócio: `POST /api/v8/ml/analyze/business-insights`

### O que o motor deve entregar
- inferência orientada ao objetivo do usuário
- alinhamento de segmento e palavras-chave
- scores de oportunidade, risco e confiança
- recomendação acionável em texto
- contexto de projeto via `BusinessContext`

### Onde está integrado hoje
- o dashboard `app/dashboard/strategy-learning/page.tsx` consome o endpoint de status ML
- o backend local usa `src_v8/autonomous_agent/ml_foundation/back/ml_pipeline.py`
- a documentação de refinamento está em `src_v8/autonomous_agent/ml_foundation/ML_PIPELINE_REFINEMENT_PLAN.md`

### Nota
O motor local ainda é um estágio de transição para um pipeline end-to-end. A meta é sair do protótipo e entregar insights reais de negócio, não apenas classificações de texto.

---

## 🚀 **Instalação e Execução**

### **Método 1: Docker (Recomendado)**

```bash
# Clone o repositório
git clone https://github.com/your-repo/culture-pulse-v8.git
cd culture-pulse-v8

# Execute com Docker Compose
docker-compose up -d

# Acesse:
# Frontend: http://localhost:3000
# API: http://localhost:8000
```

### **Método 2: Instalação Local**

```bash
# Clone o repositório
git clone https://github.com/your-repo/culture-pulse-v8.git
cd culture-pulse-v8

# Instale dependências
pip install -r src_v8/requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas chaves de API
# O frontend Next.js também precisa de FASTAPI_URL para chamar o backend FastAPI
```

Adicione ao arquivo `.env` ou `.env.local` do frontend:

```env
FASTAPI_URL=http://localhost:8000
NEXT_PUBLIC_FASTAPI_WS_URL=ws://localhost:8000
```

Para o ambiente de ML local, verifique o health endpoint do backend:

```bash
GET http://localhost:8000/api/v8/ml/health
```

Esse endpoint expõe os indicadores:
- `ml_pipeline_ready`
- `ollama_available`

### ✅ Verificação de variáveis de ambiente

Antes de iniciar, use o script `verify_env.py` para garantir que o shell carregue todas as variáveis essenciais do `.env`.

```bash
py verify_env.py
```

Esse check valida:
- `FASTAPI_TOKEN`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_KEY`
- `PROJECT_ANALYSIS_FASTAPI_URL`
- `NEXT_PUBLIC_FASTAPI_URL`
- `NEXT_PUBLIC_API_URL`
- `ENVIRONMENT=production`
- `ENABLE_DEMO_AUTH=false`

> Atenção: o token real `FASTAPI_TOKEN` deve vir do secret manager do deploy Railway no serviço backend FastAPI. Não use um token de demo; em local use `.env` apenas para desenvolvimento.


Observações importantes:
- O `ml_pipeline` local exige o pacote `autonomous_agent.ml_foundation.back.ml_pipeline` disponível em `src_v8/autonomous_agent/ml_foundation/back`.
- A rota de insights business está disponível em `POST /api/v8/ml/analyze/business-insights`.
- O dashboard `app/dashboard/strategy-learning/page.tsx` consome `GET /api/v8/ml/strategy-status`.
- Ollama só é necessária para integrações de LLM avançadas; o pipeline local pode funcionar sem ela.
- O endpoint `/api/v8/ml/health` é protegido e requer autenticação.

Para referência de arquitetura e roadmap de ML:
- `src_v8/autonomous_agent/ml_foundation/ML_PIPELINE_REFINEMENT_PLAN.md`

```bash
# Execute o backend
cd src_v8
py -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Execute o frontend (novo terminal)
cd culturepulse-web
npm run dev
```

### **Método 3: Dev Container**

```bash
# Abra no VS Code com Dev Containers
code --folder-uri vscode-remote://dev-container+.../culture-pulse-v8
```

---

## 🔑 **Configuração das APIs**

Crie um arquivo `.env` na raiz do projeto:

```env
# APIs Externas
YOUTUBE_API_KEY=your_youtube_key
REDDIT_CLIENT_ID=your_reddit_id
REDDIT_CLIENT_SECRET=your_reddit_secret
SPOTIFY_CLIENT_ID=your_spotify_id
SPOTIFY_CLIENT_SECRET=your_spotify_secret
NEWS_API_KEY=your_news_key
MEETUP_API_KEY=your_meetup_key

# Sistema
REDIS_URL=redis://localhost:6379
DATABASE_URL=duckdb:///data/culture_pulse.db
SECRET_KEY=your_secret_key_here

# Supabase real
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
# ou use SUPABASE_SERVICE_ROLE_KEY para deploy/produção

# Auth / smoke test
ENVIRONMENT=production
ENABLE_DEMO_AUTH=false
SMOKE_TEST_AUTH_TOKEN=your_real_smoke_test_token

# Deploy
API_SERVER_PORT=8000
```

> Nota: o backend agora exige autenticação Supabase real para smoke tests. O fallback de demo auth só funciona quando `ENVIRONMENT` está em `development` ou `ENABLE_DEMO_AUTH=true`.

---

## 🎯 **15 Círculos Culturais**

### 📍 **Centrais (4)**
- **Adaptação e Flexibilidade** - Jeitinho brasileiro, adaptação a crises
- **Conexão com Natureza e Coletivo** - Preservação, comunidades, mutirões
- **Resiliência e Fé** - Superação, religiosidade, otimismo
- **Economia Informal e Empreendedorismo** - Comércio de rua, economia criativa

### 🔄 **Intermediários (8)**
- **Musicalidade e Expressão** - Samba, MPB, forró, funk
- **Vida Urbana e Rural** - Migração, tradições
- **Alegria e Celebração** - Carnaval, festas
- **Festa e Luta Cotidianas** - Trabalho e celebração
- **Criatividade e Improvisação** - Gambiarra, soluções criativas
- **Diversidade Geográfica** - Riqueza regional
- **Afeto e Hospitalidade** - Calor humano
- **Desejo de Ascensão** - Educação, meritocracia

### 🌐 **Externos (4)**
- **Sincretismo Cultural** - Fusão religiosa e cultural
- **Relação com o Caos** - Navegação na complexidade
- **Astúcia e Sagacidade** - Malandragem, esperteza
- **Desigualdade x Solidariedade** - Paradoxos sociais

---

## 📊 **APIs e Dados**

### **APIs Ativas (5)**
- 📺 **YouTube API** - Vídeos, comentários, trends
- 💬 **Reddit API** - Discussões, comunidades brasileiras
- 🎵 **Spotify API** - Tendências musicais, playlists
- 📰 **NewsAPI** - Notícias, sentiment analysis
- 📊 **IBGE API** - Dados demográficos oficiais

### **APIs Simuladas (3)**
- 📷 **Instagram/Threads** - Posts, stories, engagement
- 🤝 **Meetup API** - Eventos, comunidades locais
- 📈 **Google Trends** - Tendências de busca

### **Métricas Geradas**
- **Score Cultural** (0-100) - Relevância cultural geral
- **Alma Brasileira** (0-100) - Conexão com valores brasileiros
- **TF-IDF Score** (0-100) - Relevância terminológica
- **IICB** - Índice Integrado de Cultura Brasileira

---

## 🎨 **Dashboard e Visualizações**

### **Funcionalidades da Interface**
- 📋 **Formulário Contextualizado** (2 partes: negócio + análise)
- 📊 **Cards de Scores** com interpretação automática
- 🔵 **Círculos Interativos** com hover e seleção
- 🕸️ **Grafos de Relacionamento** cultural
- 📈 **Gráficos de Qualidade** por API
- 📄 **Resumo Executivo** com insights e recomendações

### **Contextos de Negócio**
- Lançamento de Produto
- Crise de Reputação
- Pesquisa de Mercado
- Monitoramento de Concorrência
- Expansão Regional
- Inovação Cultural

---

## 🔧 **Desenvolvimento**

### **Estrutura do Projeto**
```
culture-pulse-v8/
├── src_v8/
│   ├── api/                 # Backend FastAPI
│   ├── core/               # Processamento cultural
│   ├── data/               # Pipeline de dados
│   ├── config/             # Configurações
│   └── requirements.txt    # Dependências
├── culturepulse-web/       # Frontend Next.js
├── .github/workflows/      # CI/CD GitHub Actions
├── docker-compose.yml      # Containers Docker
├── Dockerfile             # Imagem principal
└── README.md              # Este arquivo
```

### **Scripts Úteis**
```bash
# Executar testes
pytest src_v8/tests/

# Diagnóstico do sistema
python src_v8/scripts/diagnostic.py

# Limpar cache
python src_v8/scripts/clear_cache.py

# Backup de dados
python src_v8/scripts/backup_data.py
```

---

## 🚀 **Deploy Automático**

### **GitHub Actions**
- ✅ **CI/CD Pipeline** automatizado
- ✅ **Testes automáticos** em PR
- ✅ **Deploy do frontend em Cloudflare Pages**
- ✅ **Deploy do backend Docker no Railway**
- ✅ **Build Docker** automático

### **Ambientes**
- **Development**: `dev` branch → Deploy automático
- **Staging**: `staging` branch → Testes E2E
- **Production**: `main` branch → Deploy manual aprovado

---

## 📚 **Documentação**

- 📖 **[Guia de Uso](docs/USER_GUIDE.md)** - Como usar o sistema
- 🔧 **[API Reference](docs/API_REFERENCE.md)** - Documentação das APIs
- 🏗️ **[Arquitetura](docs/ARCHITECTURE.md)** - Detalhes técnicos
- 🎯 **[Círculos Culturais](docs/CULTURAL_CIRCLES.md)** - Framework cultural
- 🚀 **[Deploy Guide](docs/DEPLOY_GUIDE.md)** - Guia de deploy

---

## 🤝 **Contribuição**

1. **Fork** o repositório
2. **Crie** uma branch feature (`git checkout -b feature/nova-funcionalidade`)
3. **Commit** suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. **Push** para a branch (`git push origin feature/nova-funcionalidade`)
5. **Abra** um Pull Request

### **Guidelines**
- Mantenha o padrão de código existente
- Adicione testes para novas funcionalidades
- Atualize a documentação quando necessário
- Use commits semânticos (feat, fix, docs, etc.)

---

## 📊 **Roadmap**

### **V8.1 - Próximas Features**
- [ ] Autenticação multi-tenant
- [ ] Export PDF avançado
- [ ] Alertas e notificações
- [ ] API pública para desenvolvedores

### **V8.2 - Inteligência Avançada**
- [ ] Machine Learning para predições
- [ ] Análise de sentimento avançada
- [ ] Comparação temporal
- [ ] Benchmarking setorial

### **V8.3 - Expansão**
- [ ] Dashboard mobile
- [ ] Integração com BI tools
- [ ] Webhooks e automações
- [ ] Multi-idioma (ES, EN)

---

## 📄 **Licença**

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 🙏 **Agradecimentos**

- **FastAPI** - Framework web moderno
- **Next.js** - Interface interativa do frontend
- **Plotly** - Visualizações avançadas
- **NetworkX** - Análise de grafos
- **DuckDB** - Banco analítico rápido

---

## 📞 **Suporte**

- 📧 **Email**: support@culturepulse.ai
- 💬 **Discord**: [Culture Pulse Community](https://discord.gg/culturepulse)
- 📖 **Wiki**: [Documentação Completa](https://github.com/your-repo/culture-pulse-v8/wiki)
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-repo/culture-pulse-v8/issues)

---

**Culture Pulse V8.0 - Inteligência Cultural Brasileira** 🧠🇧🇷

*Desenvolvido com ❤️ para entender e valorizar a cultura brasileira*
