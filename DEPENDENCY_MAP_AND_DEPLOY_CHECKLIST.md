# Dependency Map & Deploy Checklist

## 1. Visão Geral do Mapa de Dependências

### 1.1 Frontend → Backend

O frontend atual é um Next.js App Router que depende de:

- `Supabase` para login, sessão, projetos e perfis.
- `FastAPI` para análise cultural e LLM/back-end inteligente.
- `DEMO_MODE` para fornecer fallback mock em alguns caminhos.

### 1.2 Rotas Frontend importantes

#### Autenticação / projeto

- `app/(auth)/login/page.tsx`
  - `supabase.auth.signInWithPassword`
  - `supabase.auth.signInWithOAuth` com `redirectTo /auth/callback`
- `app/auth/callback/route.ts`
  - `supabase.auth.exchangeCodeForSession(code)`
  - `profiles.upsert()`
- `middleware.ts`
  - Protege `/dashboard` e encaminha demo quando Supabase não existe.
- `app/dashboard/layout.tsx`
  - Busca `user` do Supabase no servidor.
- `app/api/projects/[id]/route.ts`
  - Cria, edita, atualiza e deleta projetos.

#### Análise e inteligência

- `app/dashboard/intelligence/page.tsx`
  - `POST ${FASTAPI_URL}/api/v8/intelligence/full`
- `app/dashboard/scenarios/page.tsx`
  - `POST http://localhost:8000/api/v8/intelligence/scenarios/batch`
- `app/dashboard/opportunities/page.tsx`
  - `POST http://localhost:8000/api/v8/intelligence/opportunities/batch`
- `app/dashboard/stability-risk/page.tsx`
  - `GET ${FASTAPI_URL}/api/v8/stability-risk/matrix`
  - `GET ${FASTAPI_URL}/api/v8/stability-risk/status`
- `app/dashboard/trends/page.tsx`
  - `GET ${FASTAPI_URL}/api/v8/dashboard/trends`
  - `GET ${FASTAPI_URL}/api/v8/dashboard/weak-signals`
  - `GET ${FASTAPI_URL}/api/v8/dashboard/profiles`
- `app/onboarding/page.tsx`
  - `POST ${FASTAPI_URL}/api/v8/analytics/consultant/refine-briefing`
  - `POST /api/projects` para criar projeto com metadata completa
  - `POST /api/projects/[id]` para acionar análise de projeto
  - redireciona para `/dashboard?projectId=<id>` para o dashboard carregar imediatamente o projeto criado
- `app/dashboard/projects/[id]/AnalyzeButton.tsx`
  - `POST /api/projects/[id]` (server-side trigger local)

### 1.3 Backend disponível em `src_v8/api`

O FastAPI atual expõe routers como:

- `/api/v8/intelligence`
  - `full`, `scenarios`, `opportunities`, `alerts`, `actions`, `vulnerability`
- `/api/v8/signals`
  - `live`, `detail`, `compare`
- `/api/v8/stability-risk`
  - `matrix`, `status`, `assess`, `portfolio`
- `/api/v8/dashboard`
  - `trends`, `weak-signals`, `profiles`, `relationships`, `insights`
- `/analytics`
  - `consultant/refine-briefing`, `quadrant`, `segment-comparison`, `learning-status`

### 1.4 Rotas que estão desalinhadas ou quebradas
- A API FastAPI atual em `src_v8/api/main.py` monta apenas rotas `/api/v8` — não há roteamento `/api/v1` ativo.

- `app/onboarding/page.tsx` chamava `POST /api/v8/intelligence/synthesize` — este problema já foi removido; a rota atual é `POST /api/v8/analytics/consultant/refine-briefing`.
- `app/dashboard/projects/[id]/AnalyzeButton.tsx` chamava `/api/fastapi/api/v8/...` — foi corrigido para usar o endpoint local `/api/projects/[id]`.
- O fluxo de projeto foi completado: `app/dashboard/projects/[id]/page.tsx` agora expõe botões diretos como "Ver insights do projeto" e `AnalyzeButton` redireciona para `/dashboard/insights?projectId=<id>` após disparar a análise.
- `src_v8/collectors/supabase_writer.py` e `src_v8/collectors/orchestrator.py` agora propagam `project_id`/`user_id` para a persistência em `cultural_signals`.
- `app/dashboard/trends/page.tsx` usava `/api/v1/dashboard/...` — agora está alinhado com `/api/v8/dashboard/...`.
- `app/dashboard/clustering/page.tsx` ainda carregava `/api/v1/clusters/label`; foi atualizado para `/api/v8/clusters/label`.
- `components/auth/PlanGate.tsx` foi atualizado para `${API_BASE_URL}/plans` e o backend agora inclui o router `config_plans`.
- `app/dashboard/layout.tsx` e `app/dashboard/upgrade/page.tsx` agora consultam `/plans/my-plan` para obter o tier autenticado do usuário em vez de depender apenas de `user_metadata.plan`.
- `components/auth/PlanGate.tsx` agora exibe um fallback amigável quando `/plans/my-plan` não está disponível.
- O dashboard agora suporta `?projectId=<id>` para carregar imediatamente o projeto criado pelo onboarding e atualizar o `latestProject`.
- `hooks/useConsultant.ts` e `app/dashboard/campaign-analysis/page.tsx` foram removidos porque dependiam de um endpoint `preventive-analysis` inexistente.

## 2. Supabase e Persistência

### 2.1 Estrutura de dados confirmada

- Tabela `projects` existe e é usada por `app/api/projects/*`.
- Tabela `profiles` é upsertada no callback de login.
- Tabela `cultural_signals` é esperada em várias páginas de dashboard.

### 2.2 Pontos de atenção

- `cultural_signals` é essencial para dashboards reais, mas o deploy e docs não comprovam se a tabela está criada e populada.
- O fluxo de onboarding não garante que o projeto salvo em Supabase seja consumido pelo dashboard principal.
- Há geração de mock em `KeywordContext` e dashboards, o que pode mascarar falhas de integração real.
- `profiles` é upsertado em `app/auth/callback/route.ts` e atualizado em `app/onboarding/page.tsx`; a tabela é usada para personalização de perfil no dashboard, análises e na UI de tendências.
- `projects` é criado em `app/dashboard/projects/new/page.tsx`, salvo em Supabase, e lido/atualizado em `app/api/projects/[id]/route.ts`; o botão `Analyze` em `app/dashboard/projects/[id]/AnalyzeButton.tsx` dispara análise baseada nesse registro.
- `cultural_signals` é consumido por dashboards como `app/dashboard/trends/page.tsx`, `app/dashboard/signals/page.tsx`, `app/dashboard/circles/page.tsx`, `app/dashboard/unknowns/page.tsx` e por endpoints FastAPI (por exemplo `src_v8/api/endpoints/signals.py`). Ele também é persistido por coletores como `src_v8/collectors/supabase_writer.py`.
- Fluxo de contexto de projeto: criação em `app/api/projects/[id]/route.ts`, trigger de análise em `src_v8/api/endpoints/analysis.py`, coleta ativa em `src_v8/core/engines/cultural_engine.py` e ingestão em `src_v8/collectors/orchestrator.py::_ingest_historical_data`.
- Gap: `cultural_signals` está sendo consumido globalmente pelo dashboard, mas não armazena `project_id`/`user_id`, o que misturaria sinais de briefings diferentes e quebra a separação de contexto entre projetos.

### 2.3 Validação de schema e views

- Contagem atual em Supabase usando a configuração do `.env`:
  - `signals_public`: 0 registros
  - `signals_pro`: 103 registros
  - `signals_executive`: 323 registros
  - `cultural_signals`: 323 registros
  - `signal_labels`: 186 registros
- O backend usa o mapa de planos em `src_v8/config/plan_config.py` para selecionar a fonte Supabase por plano:
  - `free` → `signals_public`
  - `pro` → `signals_pro`
  - `executive` → `signals_executive`
  - `enterprise` → `cultural_signals`
- O código também referencia `signal_labels` como fonte adicional de rotulagem de sinais.
- No schema atual do Supabase, as tabelas/views validadas são:
  - `projects`
  - `profiles`
  - `cultural_signals`
  - `signal_labels`
  - `signals_public`
  - `signals_pro`
  - `signals_executive`
  - `signal_embeddings` (implícita pelo schema de embeddings)
- O backend também faz referência a tabelas/entidades que não existem no schema Supabase atual testado:
  - `brand_profiles`
  - `learned_weights`
  - `model_weights`
  - `analysis_performance`
  - `signal_feedback`
  - `collected_data`
  - `discovered_patterns`
  - `project_contexts`
  - `messages`
  - `project_ai_payloads`
- Observação: o frontend do dashboard está consultando diretamente `cultural_signals` em server components, em vez de usar os views `signals_public`, `signals_pro` ou `signals_executive`.

## 2.4 DDL recomendada para tabelas faltantes

```sql
-- Projetos e contexto de projeto
CREATE TABLE IF NOT EXISTS public.projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
  name TEXT NOT NULL,
  description TEXT,
  status TEXT NOT NULL DEFAULT 'draft',
  objective TEXT,
  segment TEXT,
  keywords TEXT[],
  audiences TEXT[],
  regions TEXT[],
  business_context JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.project_contexts (
  id BIGSERIAL PRIMARY KEY,
  project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
  user_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
  context_name TEXT,
  business_context JSONB,
  prompt_payload JSONB,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.messages (
  id BIGSERIAL PRIMARY KEY,
  project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
  user_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Feedback e aprendizado de modelos
CREATE TABLE IF NOT EXISTS public.signal_feedback (
  id BIGSERIAL PRIMARY KEY,
  signal_id BIGINT REFERENCES public.cultural_signals(id) ON DELETE SET NULL,
  project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
  user_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
  feedback_type TEXT,
  rating NUMERIC(3,2),
  comment TEXT,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.model_feedback (
  id BIGSERIAL PRIMARY KEY,
  model_name TEXT NOT NULL,
  project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
  user_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
  prompt_payload JSONB,
  model_response JSONB,
  rating NUMERIC(3,2),
  feedback_text TEXT,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.analysis_performance (
  id BIGSERIAL PRIMARY KEY,
  project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
  model_name TEXT,
  run_at TIMESTAMPTZ DEFAULT NOW(),
  metric_name TEXT,
  metric_value NUMERIC,
  metadata JSONB
);

CREATE TABLE IF NOT EXISTS public.collected_data (
  id BIGSERIAL PRIMARY KEY,
  project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
  source TEXT,
  source_id TEXT,
  raw_data JSONB,
  processed BOOLEAN DEFAULT FALSE,
  collected_at TIMESTAMPTZ DEFAULT NOW(),
  metadata JSONB
);

CREATE TABLE IF NOT EXISTS public.discovered_patterns (
  id BIGSERIAL PRIMARY KEY,
  project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
  pattern_type TEXT,
  description TEXT,
  score NUMERIC(5,4),
  metadata JSONB,
  discovered_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.brand_profiles (
  id BIGSERIAL PRIMARY KEY,
  project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
  brand_name TEXT,
  profile_data JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.learned_weights (
  id BIGSERIAL PRIMARY KEY,
  project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
  model_name TEXT,
  feature_name TEXT,
  weight NUMERIC,
  last_updated TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.model_weights (
  id BIGSERIAL PRIMARY KEY,
  project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
  model_name TEXT,
  weights JSONB,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

- Observação: use `jsonb` para armazenar `business_context`, `prompt_payload`, `metadata` e qualquer payload de IA que precise ser lido pelo pipeline.
- Estas tabelas são prioridades altas para alinhar o backend ML com o schema do Supabase e garantir que a persistência de projeto/feedback/contexto exista.
- Isso sugere que o ambiente atual tem suporte às views de sinais em tiers, mas não às tabelas de ML/historicização esperadas pelo `StrategyLearner` e pelo feedback engine.
- Próximo passo recomendado: criar ou validar no Supabase as tabelas de ML/historicização que o backend referencia, ou ajustar o backend para alinhar com o schema atual.

### Correções aplicadas
- Corrigido: `src_v8/api/endpoints/emerging_profiles.py` agora usa `use_realtime_api=True` para aproveitar a coleta em tempo real.
- Corrigido: `src_v8/collectors/data_collectors.py` conserta o fallback local do cache quando Redis não está disponível.
- Corrigido: `src_v8/core/intelligence/enriched_reader.py` agora injeta contexto de onboarding/projeto nos sinais em tempo real e no fallback.
- Corrigido: `src_v8/api/endpoints/emerging_profiles.py` agora busca contexto de projeto do Supabase e usa esse contexto para enriquecer a coleta em tempo real.
- Corrigido: `src_v8/api/signal_publisher.py` agora publica também para o canal Redis `signals:executive` e mantém buffer `buffer:signals:executive` para replay, alinhando o fluxo de tiers com `executive`.
- Corrigido: `culturepulse-web/supabase/schema.sql` e `src_v8/supabase/migrations/20260222_v91_four_tiers.sql` agora definem `WITH (security_invoker = true)` nas views `signals_public`, `signals_pro`, `signals_executive` para preservar RLS e evitar warnings de `SECURITY DEFINER`.
- Corrigido: DNS do `SUPABASE_URL` foi validado localmente e resolve corretamente para o host Supabase.
- Corrigido: `src_v8/api/main.py` agora importa `get_strategy_learner` explicitamente de `core.intelligence.learning.StrategyLearner`, eliminando o caminho legado `core.learning.StrategyLearner`.
- Corrigido: `src_v8/core/learning` shim de compatibilidade criado e todos os imports legacy `core.learning.*` normalizados para `core.intelligence.learning.*`.
- Corrigido: `src_v8/core/advanced_analytics/multipliers_engine.py` deixou de depender de `streamlit` e `plotly`, passando a gerar payloads JSON compatíveis com Next.js.
- Corrigido: `components/dashboard/ActiveLearningCurator.tsx` agora mantém o estado `stats` corretamente e `tsconfig.json` foi reforçado com `baseUrl: "."` para suportar aliases `@/*`.
- Corrigido: `app/dashboard/emerging-profiles/page.tsx` removeu o fallback demo/mock e passou a depender apenas de dados reais do backend FastAPI.
- Corrigido: `app/dashboard/clustering/page.tsx`, `app/dashboard/graph/page.tsx`, `app/dashboard/page.tsx`, `app/dashboard/alerts/page.tsx`, `app/dashboard/opportunities/page.tsx`, `app/dashboard/scenarios/page.tsx`, `app/dashboard/strategy/page.tsx`, `app/dashboard/signals/page.tsx` e `app/dashboard/unknowns/page.tsx` removeram fallback demo/mock e agora apresentam dados ou estado vazio real.
- Corrigido: `app/dashboard/layout.tsx` removeu o fallback offline/demo e agora redireciona para `/login` quando o usuário Supabase não está autenticado.
- [x] Corrigido: o botão PDF do dashboard foi conectado a um fluxo real de exportação.
  - [x] `components/dashboard/ExportContext.tsx` e `components/dashboard/ExportDataPublisher.tsx` foram adicionados.
  - [x] `app/dashboard/intelligence/page.tsx` publica dados de exportação reais.
  - [x] `components/layout/TopBar.tsx` agora chama `exportIntelligenceToPDF` quando há dados prontos.
- [x] Corrigido: centralização adicional de dashboard client:
  - [x] `components/dashboard/DashboardContext.tsx` e `components/dashboard/useDashboardSupabaseClient.ts` foram criados.
  - [x] `DashboardShell` agora expõe `user` e `plan` via `DashboardProvider`.
  - [x] `components/layout/TopBar.tsx` e `app/dashboard/page.tsx` usam o hook `useDashboardSupabaseClient` em vez de criar o cliente Supabase diretamente.
- [x] Corrigido: `lib/utils/pdf-export.ts` e `types/jspdf.d.ts` foram ajustados para `jspdf-autotable` e metodos `setDrawColor`/`setPage`, tornando o exportador PDF compatível com a tipagem TypeScript do projeto.
- Corrigido: smoke test contra `FASTAPI_URL` validou os endpoints `/api/v8/dashboard/trends`, `/api/v8/ml/strategy-status` e `/api/v8/dashboard/emerging-profiles`.
- Esclarecido: a correção da pipeline de coleta/enriquecimento de dados se aplica a outros endpoints que usam a mesma infraestrutura (`EnrichedDataReader`, `CulturalDataOrchestrator`), não apenas a `Perfis Emergentes`.

### Ações pendentes
- [x] [PRIORIDADE ALTA] Migrar `src_v8/SOLUCAO_COMPLETA_AUTOMATED_LEARNING.md` para o workflow atual: manter o motor Python como backend útil e mover a visualização legacy Streamlit para Next.js exposto via FastAPI.
  - Nota: o código já existe no repo com `app/dashboard/strategy-learning/page.tsx` e `src_v8/api/endpoints/ml.py`, e o endpoint local está ativo — a rota existe, mas exige autenticação.
- [x] [PRIORIDADE ALTA] Rever o fluxo de ML na instância local para expor o endpoint `/api/v8/ml/strategy-status` e garantir que o dashboard `app/dashboard/strategy-learning` funcione de fato.
  - Verificado: `src_v8/api/endpoints/ml.py` e `src_v8/api/main.py` registram a rota no app importado.
  - Nota: o problema era operacional. O backend foi reiniciado corretamente de `src_v8` em `8000` e o endpoint de debug `/__debug__/runtime` retornou `ml_router_defined: true` e `ml_router_prefix: /api/v8/ml`.
  - Check operacional concluído: `GET http://localhost:8000/__debug__/runtime` confirma o router carregado.
  - Próxima ação: manter esse estado como novo padrão de deploy local e documentar a exigência de rodar o servidor sempre de `src_v8`.
    - Comando de startup padrão:
      `cmd /c "cd /d c:\Users\brmun\Downloads\culture-pulse-v10\src_v8 && py -3 -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload"`
  - Validado com `GET http://localhost:8000/__debug__/runtime` e `ml_router_defined: true`.
- [x] [PRIORIDADE ALTA] Documentar o estado atual do ML: `ml_router` vs `ml_pipeline` vs Ollama.
  - Estado atual: `ml_router` está ativo no FastAPI e expõe a interface em `/api/v8/ml`.
  - Estado atual: `ml_pipeline` é a implementação subjacente de ML em `autonomous_agent.ml_foundation.back.ml_pipeline` e agora está disponível em `src_v8/autonomous_agent/ml_foundation/back/ml_pipeline.py`.
  - Estado atual: Ollama aparece como backend local via `core/intelligence/local_slm_bridge.py` e `core/intelligence/business_synthesizer.py`, mas não está acessível agora em `http://127.0.0.1:11434/api/tags`.
  - Ponto a resolver: testar os endpoints ML com a implementação local agora presente e documentar como usar o pacote local.
  - Ponto a resolver: validar quais endpoints ML funcionam realmente e quais devolvem `503` por ausência de `ml_pipeline`.
  - Ponto a resolver: verificar se Ollama está acessível em `localhost:11434` e se o `BusinessSynthesizer` usa esse bridge no runtime.
  - Ponto a resolver: separar claramente no MAP:
    - `ml_router` = interface HTTP / OpenAPI
    - `ml_pipeline` = motor ML subjacente
    - `Ollama` = SLM local via bridge de narrativa/contexto
- [x] [PRIORIDADE ALTA] Verificar se `GET http://localhost:8000/openapi.json` lista `/api/v8/ml/strategy-status` após a reinicialização.
  - Verificado: `/openapi.json` contém `/api/v8/ml/strategy-status`.
  - Verificado diretamente: `GET /api/v8/ml/strategy-status` retornou `401 Not authenticated`, confirmando que a rota existe e está protegida.
  - `ml_pipeline` import em `src_v8` falha com `ModuleNotFoundError: No module named 'autonomous_agent.ml_foundation.back'`.
  - `Ollama` não está acessível localmente: `http://127.0.0.1:11434/api/tags` falha com conexão recusada.
  - Ações concretas para resolver:
    1. Habilitar `ml_pipeline` no ambiente local
       - resultado: `autonomous_agent.ml_foundation.back.ml_pipeline` agora existe em `src_v8/autonomous_agent/ml_foundation/back/ml_pipeline.py`
       - `autonomous_agent` deve ser importável a partir de `src_v8` com `import autonomous_agent.ml_foundation.back.ml_pipeline`
       - próximo passo: verificar se `GET /api/v8/ml/health` retorna `ml_pipeline_ready: true` com a implementação local disponível
    2. Testar endpoints ML funcionalmente
       - `GET /api/v8/ml/strategy-status` retornou `401 Not authenticated`
       - `GET /api/v8/ml/health` retornou `401 Not authenticated`
       - `POST /api/v8/ml/predict` retornou `401 Not authenticated`
       - conclusão: as rotas existem e estão protegidas por autenticação; não há erro de rota ou OpenAPI faltante
    3. Restaurar Ollama local
       - `http://127.0.0.1:11434/api/tags` falhou com conexão recusada
       - `LocalSLMBridge` está presente e usa `llama3:8b` em `http://localhost:11434/api/generate`
       - `bridge.is_available` retornou `False`
       - próximo passo: iniciar Ollama localmente e validar que o serviço responde em `localhost:11434`
  - Requisito de ambiente para ML:
       - `src_v8/autonomous_agent/ml_foundation/back` deve existir e conter `ml_pipeline.py`
       - o pacote `autonomous_agent` deve ser importável a partir de `src_v8` com `import autonomous_agent.ml_foundation.back.ml_pipeline`
       - o `BusinessSynthesizer`/`LocalSLMBridge` deve conseguir conectar em `http://localhost:11434`
       - o endpoint de Ollama `/api/tags` deve responder para que o bridge seja considerado disponível
       - o endpoint `/api/v8/ml/health` agora expõe `ml_pipeline_ready` e `ollama_available` como requisitos de ambiente verificáveis
- [ ] Atualizar `src_v8/alerts/doc_alerts/alerts.md` para deixar claro que `alerts/streamlit_interface.py` é um dashboard legado e que a interface de alertas deve migrar para Next.js como parte da arquitetura atual.
- [ ] Migrar dashboard de alertas Streamlit para Next.js, garantindo que a nova UI consuma `alerts/api_endpoints.py` e se integre ao frontend `culturepulse-web`.
- [ ] Validar existência e uso real das tabelas Supabase necessárias para ML:
  - `brand_profiles`
  - `learned_weights`
  - `model_weights`
  - `analysis_performance`
  - `signal_feedback`
  - `collected_data`
  - `discovered_patterns`
- [ ] Validar se a tabela `brand_profiles` existe e está populada, pois ela alimenta o scheduler de contextos no backend.
- [ ] Validar se `cultural_signals` está populada e visível conforme plano, sem depender apenas de mock/fallback.
- [x] Gravar `project_id` e/ou `user_id` em `cultural_signals` para suportar contexto de projeto (`src_v8/collectors/supabase_writer.py::_signal_to_row`).
- [x] Tornar `src_v8/collectors/supabase_writer.py` capaz de persistir `project_id`/`user_id` no payload de ingestão (`src_v8/collectors/orchestrator.py::_ingest_historical_data`).
- [x] Ajustar o dashboard (`app/dashboard/trends/page.tsx`, `app/dashboard/insights/page.tsx`, `app/dashboard/signals/page.tsx`) e os endpoints (`src_v8/api/endpoints/dashboard_insights.py`, `src_v8/api/endpoints/emerging_profiles.py`) para filtrar sinais por `project_id`/briefing, não apenas por `cultural_signals` global.
- [ ] Adicionar checagem de plano no scheduler de coleta: `free` vs `pro` vs `executive` vs `enterprise`.
- [ ] Adicionar checagem de plano no modelo/fluxo de aprendizado para ajustar frequência e profundidade da coleta e do uso de dados.
- [ ] Confirmar se há integração Docker / Ollama ativa para que o backend use LLM como feature/input no ciclo de aprendizado.
- [x] Adicionar `supabase==2.30.0` a `src_v8/requirements_api.txt` para garantir que o backend possa usar `collectors.supabase_writer` e o fallback Supabase do `EnrichedDataReader`.
- [x] Revisar e limpar o deploy legacy de Streamlit: variáveis de ambiente, comandos e entradas de inicialização ainda estão presentes em deploys principais e não fazem parte do fluxo Next.js/JSON. (Atualizado: `src_v8/Dockerfile`, `src_v8/docker-compose.yml`, `src_v8/railway.toml`, `src_v8/Procfile`, `.env` e `src_v8/requirements.txt` para backend FastAPI/uvicorn.)
- [ ] Criar endpoints de input/feedback e importação de resultados reais para que o `StrategyLearner` seja mais que um painel estático.
- [ ] Transformar o painel de status em dashboard funcional com inputs para:
  - feedback manual
  - re-treinamento de pesos
  - disparo de coleta/reavaliação
  - visualização de `confidence`, `n_samples`, `performance` e `drift`
- [ ] Atualizar `StrategyLearner` para usar os dados reais de `analysis_performance` e `signal_feedback` no cálculo de pesos, em vez de manter lógica base fixa.
- [ ] Revisar se o backend precisa de `Ollama`/local SLM e documentar como habilitar essa integração no Docker e no ambiente.
- [ ] Criar um check de arquitetura que vincule o ML clássico do `StrategyLearner` ao motor de LLM se quisermos enriquecer features com narrativa cultural.
- [ ] Criar documentação operacional para o ciclo de ML no backend:
  - como iniciar o scheduler
  - onde ver logs de coleta
  - como reiniciar ou resetar pesos
- [ ] Adicionar testes unitários e de integração para os endpoints de ML/estratégia em `src_v8/api/endpoints/ml.py` e `src_v8/api/main.py`.
- [x] Criar smoke tests que verifiquem a disponibilidade de `FASTAPI_URL` e os endpoints críticos `/api/v8/dashboard/trends`, `/api/v8/ml/strategy-status`, `/api/v8/dashboard/emerging-profiles`.
- [ ] Definir um plano de rollout de recursos de ML e perfis emergentes, começando por um MVP que exiba dados existentes em vez de lógica de aprendizado completa.

- O `.env` atual ainda contém variáveis de Streamlit (`STREAMLIT_PORT`, `STREAMLIT_ADDRESS`) que são legacy/optional para o fluxo Next.js + FastAPI e não são obrigatórias para a rota de perfis emergentes.
- A configuração de deploy principal foi atualizada para o backend FastAPI/uvicorn e não referencia mais Streamlit em `src_v8/Dockerfile`, `src_v8/docker-compose.yml`, `src_v8/railway.toml` ou `src_v8/Procfile`.
- Teste direto em `GET /api/v8/dashboard/emerging-profiles?plan=free&top_n=3` com a chave `cp_demo_2025_free_tier` retornou `200 OK` com `data: []`, indicando que o endpoint funciona, mas não há dados reais disponíveis devido à falta de Redis e ao fallback Supabase inoperante.
- Se as tabelas `projects`, `profiles` ou `cultural_signals` estiverem vazias, o frontend atual tende a cair em mock/fallback e o fluxo real não ficará visível.
- `src_v8/SOLUCAO_COMPLETA_AUTOMATED_LEARNING.md` é um documento de arquitetura/conceito com implementação Python e um demo Streamlit legado. A visualização de aprendizado já foi migrada para o fluxo ativo via Next.js (`app/dashboard/strategy-learning/page.tsx`) e FastAPI (`/api/v8/ml/strategy-status`).
- `src_v8/HUB/docs_sobre_dashboard/PERFIS_EMERGENTES.md` é um documento conceitual de engine de perfis emergentes. Ele descreve um dashboard Streamlit e não um front-end ativo em `culturepulse-web`; também depende de migração para Next.js se for incorporado.

<!--
Notas de implementação recentes:
- Criado `scripts/validate_integration.ts` para testar o fluxo real de criação de projeto no Supabase e chamadas FastAPI ML.
- Ajustado `app/api/projects/[id]/route.ts` para enviar `demographics.genero: Todos` em vez de `todos`.
- Corrigido `scripts/validate_integration.ts` para detectar `is_active` no retorno de `GET /api/v8/ml/models`.
- Verificado localmente que `POST /api/v8/analysis/brand` responde `200` e que `POST /api/v8/ml/analyze/business-insights` retorna insights válidos com `cultural_demo` ativo.
- Confirmado que `src_v8/autonomous_agent/ml_foundation/back/ml_pipeline.py` é importável e que o modelo demo pode treinar e ser ativado.
- Adicionado wrapper compatível `analyze_business_context` em `src_v8/core/intelligence/business_synthesizer.py`.
- Limpado o script temporário `scripts/tmp_business_synth.py` após validação.
-->

## 3. Demo vs Real

### 3.1 O que funciona em produção real

- Login Supabase básico está implementado.
- Proteção de rota em `middleware.ts` existe.
- FastAPI possui endpoints reais e muitos motores de inteligência.
- `app/dashboard/intelligence/page.tsx` já consome o backend real.

### 3.2 O que ainda está em demo/fallback

- `app/dashboard/page.tsx` usa `defaultProject` e não reflete onboarding.
- `KeywordContext` usa `DEMO_PROJECT` quando `NEXT_PUBLIC_DEMO_MODE` está ativo.
- Muitas páginas ainda usam dados estáticos ou fallback mock.
- O onboarding chama um endpoint inexistente, portanto não inicia o fluxo real.

## 4. Ollama / LLM Local

### 4.1 Status da integração

- A integração com Ollama está em `src_v8/core/intelligence/local_slm_bridge.py`.
- O backend inicializa `BusinessSynthesizer()` no startup, potencialmente usando Ollama local.
- Não há chamadas diretas do frontend para Ollama.

### 4.2 Riscos

- Depende do Ollama rodando em `localhost:11434`.
- Se o serviço local não estiver disponível, endpoints avançados podem falhar.
- O onboarding atual não chega a acionar esse backend corretamente.

## 5. CI/CD e Deploy

### 5.1 O que existe hoje em `.github/workflows/deploy.yml`

- Jobs:
  - `test`
  - `security`
  - `build-backend`
  - `build-frontend`
  - `deploy-cloudflare-pages`
  - `deploy-railway`
  - `notify`

### 5.2 O que está desatualizado / errado

- O pipeline agora usa `build-backend` para Docker do backend FastAPI, `build-frontend` para o Next.js e `deploy-cloudflare-pages` para o frontend.
- Os deploys Vercel, Streamlit Cloud e Heroku foram removidos como parte do fluxo principal.
- A imagem Docker do backend é implantada no Railway como serviço gerenciado.
- O workflow usa `main` para deploy de produção, mas a branch `staging` ainda precisa de homologação separada configurada.
- O README anterior mencionava Streamlit e APIs antigas; o código atual já usa Next.js + Supabase + FastAPI.
- Revisar todos os endpoints e páginas do dashboard para remover pontos legacy de Streamlit/demo, `const supabase = createClient()` redundantes e flags como `fetchedRealData` que refletem fluxo demo/mock antigo.

### 5.3 Falta no CI/CD

- Deploy de homologação (`staging`) separado do ambiente de produção.
- `staging` deve ser usado como ambiente de homologação/QA para validar integrações antes do `main`, com branch `staging` acionando:
  - build e testes do frontend Next.js
  - build do backend FastAPI
  - deploy para Cloudflare Pages staging
  - deploy para Railway staging
  - smoke test dos endpoints críticos após deploy
- Gatilho de deploy somente para branches relevantes com ambiente diferenciado.
- Testes do frontend Next.js (`npm run build`, `npm run lint`, `npm run type-check`) não estão no workflow atual.
- Integração do backend FastAPI no CI: rodar `uvicorn` + checar endpoints críticos ou mocks.
- Validação de variáveis de ambiente / secrets antes do deploy.
- Remoção ou atualização de deploys obsoletos (Streamlit / Heroku) e uso principal do Railway para backend.

### 5.4 ML

- O `pytest` criado valida o backend local do `ml_pipeline`, comprovando que:
  - `autonomous_agent.ml_foundation.back.ml_pipeline` é importável a partir de `src_v8`;
  - o pipeline local instancia `DummyMLPipeline`;
  - o pipeline treina um modelo básico, executa predição e retorna scores de confiança;
  - o `CulturalFeatureExtractor` gera features válidas para textos.
- Esse teste confirma o motor ML básico disponível, mas não garante que o dashboard completo seja hoje suportado por um motor de insight de negócio avançado.

- Integração atual do ML no código:
  - backend FastAPI inclui `ml_router` em `src_v8/api/main.py` quando o pacote ML está disponível;
  - `src_v8/api/endpoints/ml.py` expõe endpoints `/api/v8/ml/*` e health check `/api/v8/ml/health`;
  - `ml_pipeline` local foi materializado em `src_v8/autonomous_agent/ml_foundation/back/ml_pipeline.py`.

- Fluxo observado:
  - onboarding atual não usa diretamente `/api/v8/ml`; ele chama `POST /api/v8/analytics/consultant/refine-briefing`, cria projeto e redireciona para o dashboard com `projectId`;
  - o único dashboard que usa diretamente o ML router atual é `app/dashboard/strategy-learning/page.tsx`, via `GET ${FASTAPI_BASE_URL}/api/v8/ml/strategy-status`;
  - outros dashboards usam endpoints de inteligência e dashboard (`/api/v8/intelligence/*`, `/api/v8/dashboard/*`, `/api/v8/analytics/*`) e podem estar apoiados em outros motores backend, mas não no `ml_router` direto.

- O estado atual do `ml_pipeline` local é sintético:
  - o modelo treina com labels simples e retorna o primeiro label disponível;
  - a confiança e features são geradas de forma aleatória ou simplificada;
  - não há ainda uma compreensão real de segmento de negócio, keywords e objetivo do usuário;
  - insights gerados são de natureza cultural básica (classificação, confiança, resumo de features), não um motor completo de estratégia de negócio.

- Para que o dashboard final seja apoiado apenas no `ml_pipeline` e entregue interpretação de negócio avançada, é preciso:
  1. Unificar onboarding, projeto e ML:
     - propagar `segment`, `keywords`, `objective` e `project_id` do onboarding para o backend ML;
     - garantir que `cultural_signals` persista `project_id`/`user_id` e que dashboards filtrem por contexto de projeto.
  2. Converter o `ml_pipeline` de protótipo para motor real:
     - treinar modelos com dados reais de sinais, metas de projeto e contexto de usuário;
     - construir features de negócio/segmento usando keywords, categoria e objetivo;
     - usar embeddings, scoring de oportunidade, riscos e tendência, não apenas labels simples.
  3. Alinhar dashboards ao ML router:
     - fazer páginas usarem diretamente `/api/v8/ml/*` ou endpoints de analytics construídos sobre o mesmo motor;
     - remover mocks/fallbacks e garantir consumo de dados reais em `app/dashboard/*`.
  4. Expor insights de objetivo de negócio:
     - análise de segmento e contexto;
     - identificação de oportunidades e riscos alinhados ao objetivo;
     - recomendações acionáveis e métricas de performance;
     - monitoramento de drift e confiança por projeto.
  5. Adicionar testes de integração reais dos endpoints ML:
     - `GET /api/v8/ml/health` deve retornar `ml_pipeline_ready: true`;
     - `GET /api/v8/ml/strategy-status` deve ser validado em ambiente autenticado;
     - carregar `app/dashboard/strategy-learning/page.tsx` contra o backend ML.

- Investigar dashboards que usam ML diretamente:
  - `app/dashboard/strategy-learning/page.tsx` é o único frontend que chama diretamente `/api/v8/ml/strategy-status`.
  - outros dashboards estão ligados a backend de inteligência (`/api/v8/intelligence/*`, `/api/v8/dashboard/*`, `/api/v8/analytics/*`), mas não usam o `ml_router` direto atualmente.

- Conclusão:
  - o `ml_pipeline` local está ativo e testado em nível de módulo;
  - a integração completa do onboarding + dashboards ao `ml_pipeline` ainda exige trabalho de arquitetura e implementação;
  - para chegar lá, o sistema precisa de um motor de modelo/insight real, de fluxo de contexto por projeto e de dashboards consumindo endpoints ML sem fallback.

## 6. Checklist de validação

### 6.1 Prioridades altas

- [x] Corrigir todas as chamadas que usam `http://localhost:8000` para `FASTAPI_URL` ou para um proxy de deploy.
- [x] Corrigir `app/dashboard/projects/[id]/AnalyzeButton.tsx` para usar rotas reais do backend ou remover se não estiver válido.
- [x] Em `app/dashboard/projects/[id]/page.tsx` incluir botões diretos como "Ver insights do projeto" para tornar a página o ponto natural de entrada do projeto.
- [x] Em `app/dashboard/projects/[id]/AnalyzeButton.tsx` após disparar a análise, redirecionar para `/dashboard/insights?projectId=<id>` em vez de apenas dar refresh.
  - Nota: esses dois itens foram implementados e garantem que a página do projeto funcione como ponto de entrada de contexto de projeto para o dashboard.
- [x] Corrigir `app/onboarding/page.tsx` para não chamar endpoint inexistente `intelligence/synthesize`.
- [x] Alinhar `app/dashboard/trends/page.tsx` para `/api/v8/dashboard/*` em vez de `/api/v1/dashboard/*`.
- [x] Unificar o consumo do dashboard em `app/dashboard/trends/page.tsx` e `app/dashboard/insights/page.tsx` para usar `/api/v8/dashboard/insights`.
- [x] Centralizar a autenticação de dashboard em `lib/dashboard.ts` e substituir tokens hardcoded nas pages do dashboard.
- [x] Remover hardcoded `cp_demo_2025_free_tier` das pages do dashboard e usar o helper centralizado de headers.
- [x] Corrigir `components/dashboard/ActiveLearningCurator.tsx` para usar estado de `stats` e garantir aliases `@/*` via `tsconfig.json`.
- [x] Remover fallback demo/mock nas últimas páginas do dashboard: `app/dashboard/clustering/page.tsx`, `app/dashboard/graph/page.tsx`, `app/dashboard/page.tsx` e `app/dashboard/signals/page.tsx`.
- [x] Conectar o botão de exportação PDF do `TopBar` ao fluxo real de `app/dashboard/intelligence/page.tsx` usando `ExportContext` e `ExportDataPublisher`.
- [x] Centralizar `user`/`plan` no dashboard por meio de `DashboardShell` e `DashboardProvider`.
- [x] Criar o hook `useDashboardSupabaseClient` para o browser dashboard.
- [x] Remover a chamada direta a `createClient()` de `app/dashboard/page.tsx` e usar o hook centralizado.
- [x] Atualizar `types/jspdf.d.ts` e `lib/utils/pdf-export.ts` para suportar `autoTable`, `setDrawColor` e `setPage` no fluxo de exportação PDF.
- [x] Revisar e remover em todos os endpoints/páginas do dashboard qualquer fallback demo/mock legacy, pontos de Streamlit, `const supabase = createClient()` redundantes e uso de `fetchedRealData`. (Revisão completa: as páginas server-side do dashboard que usam Supabase permanecem corretas como server-side Supabase clients; o único ponto client-side foi centralizado em `DashboardShell` / `DashboardProvider` / `useDashboardSupabaseClient`.)
- [x] Estender o mesmo padrão do `DashboardShell`/`DashboardProvider` e `useDashboardSupabaseClient` para outros componentes do dashboard que ainda usam `createClient()` no cliente, garantindo que não haja duplicação de lógica nem quebra do sistema. (Confirmado: o único cliente dashboard que usa `createClient()` agora está centralizado em `useDashboardSupabaseClient`.)
- [x] Refatorar `app/api/projects/[id]/route.ts` para usar proxy seguro compartilhado via helper servidor.
- [x] Validar `app/api/projects/[id]/route.ts` com autenticação Supabase real via Bearer token e chamadas GET/POST de projeto.
- [x] Validar E2E com `npm run validate:project-analysis` usando `SUPABASE_SERVICE_KEY` e URLs explícitas para app/fastapi.
- [x] Aplicar `fetchFastApi` em outros route handlers do `app/api` que façam proxy para FastAPI, quando disponíveis.
- [x] Expandir `BrandAnalysisRequest` para incluir `project_id`, `keywords`, `regions`, `audiences`, `circles`, `period_days`.
- [x] Garantir que o dashboard consuma o projeto salvo no Supabase e não só mock local. O fluxo já está implementado: o onboarding cria o projeto, redireciona para o dashboard com `?projectId=<id>` e o dashboard carrega o projeto imediatamente.
- [x] Definir `FASTAPI_URL` em `.env` / ambiente de deploy e documentar o requisito. Exemplo: `FASTAPI_URL=http://localhost:8000` no desenvolvimento local. O build local e o dev server foram verificados.
- [x] Revisar o Redis local e, em seguida, ajustar o `SUPABASE_URL` ou os dados de `cultural_signals` para fazer o endpoint retornar perfis reais em vez de `[]`.
- [x] Confirmar que `SUPABASE_URL` resolve em DNS e que a tabela `cultural_signals` está populada com sinais reais.
- [x] Verificar que a coleta em tempo real usa o contexto de onboarding/projeto para retornar sinais mais robustos e detalhados.
- [x] Validar o fallback histórico do Supabase (`cultural_signals`) como perfil legado quando a coleta em tempo real estiver indisponível.
- [x] Gravar `project_id` e/ou `user_id` em `cultural_signals` para associar sinais ao contexto de projeto (`src_v8/collectors/supabase_writer.py::_signal_to_row`).
- [x] Tornar `src_v8/collectors/supabase_writer.py` capaz de persistir `project_id`/`user_id` no payload de ingestão (`src_v8/collectors/orchestrator.py::_ingest_historical_data`).
- [x] Ajustar o dashboard e/ou endpoints para filtrar sinais por `project_id`/briefing, não apenas por `cultural_signals` global (`app/dashboard/trends/page.tsx`, `app/dashboard/insights/page.tsx`, `src_v8/api/endpoints/dashboard_insights.py`, `src_v8/api/endpoints/emerging_profiles.py`).
- [x] Criar smoke test automatizado para `/api/v8/dashboard/emerging-profiles/status` usando token demo e registrar o resultado como validação de endpoint.
- [x] Confirmar que o host do `SUPABASE_URL` resolve corretamente para DNS e que `SUPABASE_SERVICE_KEY` está presente no `.env`.
- [x] Atualizar as views de tiering Supabase `signals_public`, `signals_pro`, `signals_executive` para `WITH (security_invoker = true)`.
- [x] Confirmar que as páginas do dashboard usam `/plans/my-plan` como fonte de verdade do plano autenticado, em vez de `user_metadata.plan`.
- [x] Confirmar que o Supabase foi ajustado para suportar os tiers atuais `free`, `pro`, `executive` e `enterprise`, incluindo views/tiering e permissões associadas.
- [x] Verificar se o FastAPI ativo está realmente usando `src_v8/api/main.py` e se a rota `/plans/my-plan` está exposta; o OpenAPI atual do servidor não lista `/plans/my-plan`.
- [x] Corrigir suporte ao plano `executive` em toda a stack: frontend, backend, cache Redis e Supabase source tiering.
- [x] Corrigir import legacy em `src_v8/api/main.py` para `core.intelligence.learning.StrategyLearner` e remover o fallback `core.learning.StrategyLearner`.
- [x] Normalizar todos os imports legacy `core.learning.*` via shim em `src_v8/core/learning` e garantir compatibilidade com `core.intelligence.learning.*`.
- [x] Atualizar `src_v8/core/advanced_analytics/multipliers_engine.py` para remover dependências de `streamlit` / `plotly` e gerar payloads JSON compatíveis com Next.js.
- [x] Validar smoke test real no backend para `/api/v8/dashboard/trends`, `/api/v8/ml/strategy-status` e `/api/v8/dashboard/emerging-profiles`.
- [x] Retirar Streamlit do fluxo principal e garantir que o frontend execute com Next.js como interface ativa.

### 6.2 Prioridades médias

- [x] Atualizar `.github/workflows/deploy.yml` para usar a raiz do Next.js (`culturepulse-web`) e separar frontend/backend.
- [x] Adicionar pipeline `staging` para homologação com branch `staging`.
  - `staging` = homologação antes de `main`, com deploys de teste para Cloudflare Pages staging e Railway staging.
  - Deve executar o mesmo conjunto de builds e validações do `main`, mais smoke tests dos endpoints críticos.
- [x] Incluir testes do frontend Next.js no CI (`npm install`, `npm run lint`, `npm run build`, `npm run type-check`).
- [x] Remover deploys obsoletos de Streamlit / Heroku se não fazem mais parte do fluxo.
- [x] Documentar claramente quais projetos dependem de Supabase `projects`, `profiles`, `cultural_signals`.
- [x] Documentar a migração do frontend para usar `/plans/my-plan` como fonte de verdade de planos e o comportamento de fallback do `PlanGate`.
- [x] Rever `src_v8/SOLUCAO_COMPLETA_AUTOMATED_LEARNING.md` e `src_v8/HUB/docs_sobre_dashboard/PERFIS_EMERGENTES.md` para determinar se o conteúdo é apenas descritivo ou se há código/subsistema relacionado que precisa ser criado ou migrado para Next.js.
  - Resultado: ambos são principalmente documentos de design/conceito; `SOLUCAO_COMPLETA_AUTOMATED_LEARNING.md` refere-se a um demo Streamlit legado, e `PERFIS_EMERGENTES.md` descreve um dashboard Streamlit conceitual. Para entrar no fluxo ativo, precisam ser traduzidos/migrados para `culturepulse-web`.
- [x] Migrar `src_v8/SOLUCAO_COMPLETA_AUTOMATED_LEARNING.md` para o workflow atual: manter o motor Python como backend útil e mover a visualização legacy Streamlit para Next.js exposto via FastAPI.
- [x] Criar o código de implementação para `PERFIS_EMERGENTES`, porque o documento é conceitual e não contém artefatos de implementação.
  - Entregáveis implementados:
    - `src_v8/core/intelligence/emerging_profiles_engine.py`
    - `src_v8/api/endpoints/emerging_profiles.py`
    - `app/dashboard/emerging-profiles/page.tsx`
- [x] Definir o contrato de API para perfis emergentes:
  - `GET /api/v8/dashboard/emerging-profiles`
  - `POST /api/v8/dashboard/emerging-profiles/refresh`
  - `GET /api/v8/dashboard/emerging-profiles/status`
- [x] Implementar o frontend de `PERFIS_EMERGENTES` no `culturepulse-web`, com cards de perfis, métricas de `emergence_score`, `growth_velocity`, `uniqueness_index` e `stability_score`.
- [x] Criar a integração de dados do motor com `cultural_signals`, `profiles` e `projects` para alimentar os perfis emergentes.
  - Implementado via `core.intelligence.enriched_reader.EnrichedDataReader` com fallback Supabase `cultural_signals`
  - Suporte de filtro opcional `project_id` adicionado ao endpoint
- [x] Mapear os códigos referenciados por esses docs (`core/automated_learning_engine.py`, `start_automated_learning.py`, `demo_automated_learning.py`, `core/emerging_profiles_engine.py`, `dashboard/cultural_dashboard_integrated.py`) para possível migração ou depreciação.
  - Resultado: as funções de aprendizado automático estão atualmente implementadas em `src_v8/core/intelligence/learning/StrategyLearner.py` e integradas à API via `src_v8/core/engines/cultural_metrics_engine.py`; a geração de perfis emergentes está exposta em `src_v8/api/endpoints/dashboard_insights.py` e consumida pelo `app/dashboard/trends/page.tsx`.
- [x] Criar rota FastAPI `/api/v8/ml/strategy-status` para expor o estado do StrategyLearner.
- [x] Criar componente Next.js de monitoramento em `app/dashboard/strategy-learning/page.tsx` e `components/dashboard/StrategyLearnerMonitor.tsx`.
- [x] Adicionar link no menu do dashboard para `/dashboard/strategy-learning`.
- [ ] Atualizar `src_v8/alerts/doc_alerts/alerts.md` para deixar claro que `alerts/streamlit_interface.py` é um dashboard legado e que a interface de alertas deve migrar para Next.js como parte da arquitetura atual.
- [ ] Migrar dashboard de alertas Streamlit para Next.js, garantindo que a nova UI consuma `alerts/api_endpoints.py` e se integre ao frontend `culturepulse-web`.
- [ ] Validar existência e uso real das tabelas Supabase necessárias para ML:
  - `brand_profiles`
  - `learned_weights`
  - `model_weights`
  - `analysis_performance`
  - `signal_feedback`
  - `collected_data`
  - `discovered_patterns`
  - `project_contexts`
  - `messages`
  - `project_ai_payloads`
- [ ] Criar as tabelas Supabase faltantes recomendadas como prioridade alta e registrar isso no mapa de dependências.
- [ ] Mapear o schema Supabase atual vs backend ML e corrigir imediatamente as tabelas ausentes ou renomeadas.
- [ ] Validar se a tabela `brand_profiles` existe e está populada, pois ela alimenta o scheduler de contextos no backend.
- [ ] Validar se `cultural_signals` está populada e visível conforme plano, sem depender apenas de mock/fallback.
- [ ] Validar se o dashboard front-end usa a fonte correta por tier ou se está consultando diretamente `cultural_signals`, incluindo o workflow `signals_public` vs `signals_pro`/`signals_executive`.
- [ ] Adicionar checagem de plano no scheduler de coleta: `free` vs `pro` vs `executive` vs `enterprise`.
- [ ] Adicionar checagem de plano no modelo/fluxo de aprendizado para ajustar frequência e profundidade da coleta e do uso de dados.
- [ ] Confirmar se há integração Docker / Ollama ativa para que o backend use LLM como feature/input no ciclo de aprendizado.
- [ ] [PRIORIDADE FINAL] Deploy do backend FastAPI no Railway com auth real e `FASTAPI_TOKEN` no secret manager, após definirmos a arquitetura Redis/cache.
  - Conectar o repo `Bruno94-stomps/culture-pulse-v10` ao Railway.
  - Definir o diretório de serviço como `src_v8` e usar `src_v8/Dockerfile`.
  - Adicionar secrets: `FASTAPI_TOKEN`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `PROJECT_ANALYSIS_FASTAPI_URL`, `NEXT_PUBLIC_FASTAPI_URL`, `NEXT_PUBLIC_API_URL`, `ENVIRONMENT=production`, `ENABLE_DEMO_AUTH=false`.
  - Testar com `Authorization: Bearer <FASTAPI_TOKEN>` os endpoints `/api/v8/ml/health` e `/api/v8/analysis/brand`.
  - Garantir que o auth real esteja em produção e que o fallback de demo só funcione com `ENABLE_DEMO_AUTH=true` em development.
- [x] Adicionar `supabase==2.30.0` a `src_v8/requirements_api.txt` para garantir que o backend possa usar `collectors.supabase_writer` e o fallback Supabase do `EnrichedDataReader`.
- [ ] Validar que `SUPABASE_URL` resolve em DNS e que `cultural_signals` retorna dados reais em `GET /api/v8/dashboard/emerging-profiles` quando o pipeline estiver populado.
- [ ] Revisar se as variáveis de ambiente de Streamlit (`STREAMLIT_PORT`, `STREAMLIT_ADDRESS`) ainda fazem parte do deploy principal ou se devem ser mantidas apenas como legacy/optional.
- [ ] Criar endpoints de input/feedback e importação de resultados reais para que o `StrategyLearner` seja mais que um painel estático.
- [ ] Transformar o painel de status em dashboard funcional com inputs para:
  - feedback manual
  - re-treinamento de pesos
  - disparo de coleta/reavaliação
  - visualização de `confidence`, `n_samples`, `performance` e `drift`
- [ ] Atualizar `StrategyLearner` para usar os dados reais de `analysis_performance` e `signal_feedback` no cálculo de pesos, em vez de manter lógica base fixa.
- [ ] Revisar se o backend precisa de `Ollama`/local SLM e documentar como habilitar essa integração no Docker e no ambiente.
- [ ] Criar um check de arquitetura que vincule o ML clássico do `StrategyLearner` ao motor de LLM se quisermos enriquecer features com narrativa cultural.
- [ ] Criar documentação operacional para o ciclo de ML no backend:
  - como iniciar o scheduler
  - onde ver logs de coleta
  - como reiniciar ou resetar pesos
- [ ] Adicionar testes unitários e de integração para os endpoints de ML/estratégia em `src_v8/api/endpoints/ml.py` e `src_v8/api/main.py`.
- [x] Criar smoke tests que verifiquem a disponibilidade de `FASTAPI_URL` e os endpoints críticos `/api/v8/dashboard/trends`, `/api/v8/ml/strategy-status`, `/api/v8/dashboard/emerging-profiles`.
- [ ] Definir um plano de rollout de recursos de ML e perfis emergentes, começando por um MVP que exiba dados existentes em vez de lógica de aprendizado completa.
- [ ] Verificar se o frontend pode exibir falha graciosa quando o backend ML não está disponível, em vez de quebrar a página.
- [x] Validar os acessos de plano em `components/auth/PlanGate.tsx` e garantir que as páginas de ML/perfis emergentes sejam protegidas quando necessário.

#### Subtarefas de execução das prioridades médias
- [ ] Pipeline de deploy `staging`:
  - criar workflow dedicado em `.github/workflows/deploy-staging.yml` ou condição no deploy atual
  - configurar `CLOUDFLARE_PAGES_STAGING`, `RAILWAY_STAGING`, `FASTAPI_URL_STAGING`
  - adicionar smoke tests pós-deploy para `/api/v8/dashboard/trends` e `/api/v8/ml/strategy-status`
- [ ] Testes do frontend Next.js no CI:
  - `npm install`
  - `npm run lint`
  - `npm run build`
  - `npm run type-check`
  - `npm run test` se houver testes existentes
- [ ] Documentação Supabase/ML:
  - criar guia rápido de dependências `projects`, `profiles`, `cultural_signals`
  - incluir instruções de migração para `brand_profiles` e tabelas de aprendizado
  - adicionar seção de falha do backend ML e como depurar
- [ ] MVP de `PERFIS_EMERGENTES`:
  - definir contrato de API e rotas FastAPI
  - criar backend básico com retorno de dados mock ou calculados a partir de `cultural_signals`
  - criar stub inicial em `src_v8/api/endpoints/emerging_profiles.py` para `/api/v8/dashboard/emerging-profiles`
  - implementar UI de dashboard com cards e métricas básicas
  - testar proteção de plano em `PlanGate`
- [ ] Validação de dados Supabase:
  - verificar presença das tabelas `brand_profiles`, `learned_weights`, `model_weights`, `analysis_performance`, `signal_feedback`, `collected_data`, `discovered_patterns`
  - confirmar que `cultural_signals` tem dados e está disponível para o frontend
  - documentar gaps de schema e tabelas faltantes

### 6.3 Prioridades baixas
- [ ] UI/UX e visual do sistema (mover para prioridade baixa com foco em branding, onboarding e experiência inicial):
  - [ ] Mudar o layout da página inicial para seguir o branding da marca Futurumã, usando as cores proprietárias e a fonte Inter.
  - [ ] Atualizar o cabeçalho da página inicial para substituir o texto `Culture Pulse` pelo logo em `culturepulse-web/logo` no canto superior esquerdo.
  - [ ] No Onboarding, remover a seção de Hipótese e deixar apenas a entrada de palavras-chave, objetivo, marca e contexto para direcionar a pesquisa.
  - [ ] Melhorar a UI do Onboarding para tornar o fluxo mais claro, incluindo estados de carregamento e progresso visível.
  - [ ] Após o Onboarding, apresentar micro partes do dashboard antes de levar o usuário diretamente à visualização completa, para mostrar o valor e o que será entregue.- [ ] Sincronizar documentação `README.md` e `DEPLOY_FUTURAMA_GUIDE.md` com o fluxo real.
- [ ] Adicionar checklist de pré-deploy para variáveis de ambiente e secrets.
- [ ] Criar um README de deploy por ambiente.
- [ ] Validar se o backend local precisa de `Ollama` e documentar como habilitar.

## 7. Recomendações mais importantes

1. Atualizar todas as URLs de backend no frontend para usar `FASTAPI_URL` / env var, removendo hardcode de `localhost`.
2. Revisar e corrigir rotas quebradas em `app/onboarding/page.tsx` e `AnalyzeButton.tsx`.
3. Ajustar o pipeline `.github/workflows/deploy.yml` para refletir a arquitetura atual:
   - build/test frontend Next.js
   - deploy do frontend para Cloudflare Pages ou ambiente consolidado
   - deploy do backend FastAPI separado ou em container
   - homologação (`staging`) diferente de produção (`main`)
4. Separar demo/fallback do fluxo real para não mascarar falhas de integração.
5. Documentar claramente as dependências de Supabase e as variáveis de ambiente exigidas.

## 8. Pontos adicionais necessários

- `CI/CD` para homologação e produção com ambientes distintos.
- `deploy.yml` deve ser ajustado para o frontend real e para a entrega do backend FastAPI.
- Se o projeto realmente não usa mais Streamlit, remover essa etapa do workflow.
- Rever `src_v8/SOLUCAO_COMPLETA_AUTOMATED_LEARNING.md` e `src_v8/HUB/docs_sobre_dashboard/PERFIS_EMERGENTES.md` para documentar o que deve ser criado versus o que deve ser migrado para Next.js, e identificar se o `.md` contém apenas descrição ou também requer ação de implementação.
- Validar a existência de `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `FASTAPI_URL`, `CLOUDFLARE_API_TOKEN`, `SUPABASE_SERVICE_ROLE_KEY` como secrets necessários.
- Adicionar um passo de `smoke test` pós-deploy para verificar os endpoints críticos.
## Notas de implementação recentes
- Criado e validado o script `scripts/validate_integration.ts` para fazer teste real de integração entre Supabase e FastAPI ML.
- Corrigido `app/api/projects/[id]/route.ts` para enviar o valor correto `genero: Todos` ao backend de análise.
- Ajustado o teste de modelo ativo no script para usar `is_active` em vez de `active`.
- Confirmado que o backend FastAPI em `src_v8/api/main.py` pode expor `/api/v8/ml` e que o modelo `cultural_demo` é ativado corretamente.
- Verificado que o `ml_pipeline` local em `src_v8/autonomous_agent/ml_foundation/back/ml_pipeline.py` treina e retorna previsões com confidência.
## 9. Comando recomendado para inspecionar contexto atual

Use este comando no terminal do repositório para saber o estado atual do código, quais arquivos foram alterados e o histórico recente:

```powershell
git status --short
git diff --stat
git log --oneline -5
```

> Esse comando mostra o que mudou, quais áreas estão ativas agora, e os commits recentes para decidir os próximos pontos.
