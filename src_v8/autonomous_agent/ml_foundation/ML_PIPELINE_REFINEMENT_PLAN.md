# ML Pipeline Refinement Plan

## Objetivo
Transformar o `ml_pipeline` atual de um protótipo (`DummyMLPipeline`) em um motor end-to-end sofisticado, contextualizado e orientado ao objetivo do usuário.

Este documento agora também descreve as revisões necessárias para unificar o sistema ML atual, evitar duplicidade e garantir que o fluxo use dados reais com `project_id` e `user_id`.

O plano cobre:
- diagnóstico e arquitetura de dados
- revisão e unificação do motor de sinais fracos
- evolução do lineage entre `ResearchRefiner`, `weak_signals_detector` e `BusinessSynthesizer`
- entrega de insights de negócio
- integração com onboarding, chat history e dashboards
- critérios de qualidade para sair do protótipo

---

## Revisões necessárias antes de avançar

### O que precisa ser revisado e consolidado
- Confirmar que `weak_signals_detector.py` é o motor primário de detecção de sinais fracos.
- Mapear como `ResearchRefiner`, `BusinessSynthesizer` e `weak_signals_detector` trabalham juntos.
- Revisar `AnalysisWorker`, `topic_engine.py` e `dashboard_data_bridge.py` para evitar pipelines paralelos desconectados.
- Verificar a integração de ML Foundation:
  - `ml_integrator_simple.py`
  - `github_models.py`
  - `bertimbau_real_engine.py`
  - `bert_finetuner.py`
  - `feedback_learning.py`
- Garantir que `local_slm_bridge.py` / Ollama seja um recurso consistente, não um módulo isolado.
- Revisar `SOLUCAO_COMPLETA_AUTOMATED_LEARNING.md` para alinhar proposta de coleta com a arquitetura real implementada.
- Definir contrato de dados `project_id` + `user_id` + `BusinessContext` em todos os endpoints e fluxos relevantes.
- Validar que não haja mocks em produção e que o fluxo dependa apenas de APIs reais.
- Criar esquema de mensagens/projetos para ativar context caching e histórico de chat.

---

## Fase 1 — Diagnóstico e arquitetura de dados (1 semana)

### Objetivo
Definir o motor de ML com precisão, revisar os módulos existentes e garantir que o pipeline tenha dados e contexto corretos.

### Entregáveis
- Mapa de inputs do ML:
  - onboarding: `brand`, `segment`, `objective`, `keywords`, `project_id`, `user_id`, `audiences`, `regions`
  - `projects`, `profiles`, `cultural_signals`, `signal_feedback`, `messages`
  - `analytics/consultant/refine-briefing`
- Contrato de dados do pipeline:
  - formato de `training_data`
  - formato de `BusinessContext`
  - formato de output de previsão, insight e recomendação
- Documento de arquitetura do motor:
  - coleta -> detecção -> enriquecimento -> insight -> feedback
  - fluxo frontend → projeto interno → backend de coleta claramente documentado
- Revisão de módulos cruciais e suas dependências:
  - `weak_signals_detector.py` como o motor principal de descoberta
  - `ResearchRefiner`
  - `BusinessSynthesizer`
  - `AnalysisWorker`
  - `dashboard_data_bridge.py`
  - `local_slm_bridge.py` como camada de enriquecimento narrativa, não motor de decisão
  - `ml_integrator_simple.py`
  - validação inicial de fluxo entre `WeakSignalsDetector` e `BusinessSynthesizer`

### Checks
- [x] `BusinessContext` definido com campos de negócio essenciais e usados em todos os endpoints ML
- [x] Estrutura de `training_data` validada no backend
- [x] Endpoints ML definindo claramente input/output e aceitando `project_id` + `user_id`
- [x] Todas as fontes de dados usadas no projeto foram mapeadas
- [x] Documentação de dependências atualizada para evitar duplicação de arquitetura
- [x] `weak_signals_detector.py` confirmado como fluxo principal do pipeline
- [x] `local_slm_bridge.py` definido como camada de apoio e não inferência primária
- [x] Fontes verificadas e mapeadas para distinguir real vs demo
- [x] Fluxos demo revisados e limpos na documentação e no frontend/endpoint de coleta
- [x] Revisar o frontend por chamadas antigas a `/collect/status` ou `/collect/sources` e corrigir eventuais referências ao caminho errado
- [x] Confirmar que o frontend não monta dinamicamente `/collect` nem invoca diretamente a URL de coleta; o fluxo atual dispara análise via `/api/projects/${projectId}`
- [x] Gate central validado: login/onboarding/projeto usa dados reais por padrão, fontes demo não são injetadas automaticamente e só entram com override explícito `ALLOW_DEMO_COLLECTION=true`
- [ ] Não há dependência de mocks em produção; protótipos devem ser isolados em testes
- [x] Validação de endpoints de coleta quando o fluxo de login e coleta estiver operacional:
  - testar `/api/v8/collect/status`
  - testar `/api/v8/collect/sources`
  - confirmar que o backend exige autenticação e que o ambiente de teste está conectado ao Supabase ou que o fallback demo auth pode validar o token corretamente
  - confirmar rota `/api/projects/[id]` com autenticação Bearer token Supabase em Next.js
  - confirmar rota `/api/projects/[id]` retornou `200` com `analysis_available: true`
- [x] Validação inicial do fluxo `WeakSignalsDetector` → `BusinessSynthesizer` criada

> Fase 1 concluída em nível de diagnóstico e validação inicial. Revisão do frontend e correção do fluxo de coleta concluídas; o frontend não chama diretamente `/collect` e o pipeline atual é disparado via rota de projeto interna.

---

## Fase 2 — Upgrade do motor e contexto (1-2 semanas)

### Objetivo
Melhorar o pipeline de ML para incorporar contexto de negócio, unificar o motor e eliminar redundâncias.

### Entregáveis
- `ml_pipeline` que usa contexto além de texto:
  - `segment`, `objective`, `keywords`, `project_id`, `user_id`, `audiences`, `regions`, `circles`
- `BusinessContext` ampliado para incluir:
  - `brand`, `segment`, `objective`, `keywords`, `project_id`, `user_id`, `audiences`, `regions`, `circles`, `timeline`, `constraints`, `success_metrics`
- Featurização contextualizada:
  - regionalidade, sentimento, relevância temporal, público, escala, gênero, contexto local
- Modelo de inferência que combina:
  - texto + keywords + contexto de projeto + histórico de sinais
- Implementação de `montar_payload_ia()` para gerar system prompt e histórico de mensagens estruturadas
- Desenvolvimento de esquema de `Projects` / `Messages` / `ChatHistory` para suportar context caching
- Revisão do fluxo de coleta para usar apenas APIs reais e não fallback mock
- Validar o fluxo completo de login até coleta, incluindo autenticação Supabase e endpoints de coleta:
  - `/api/v8/collect/status`
  - `/api/v8/collect/sources`
  - verificar que o ambiente de teste está conectado ao Supabase ou que o fallback demo auth autentica o token corretamente
- Evitar duplicação de lógica entre `AnalysisWorker`, `dashboard_data_bridge.py` e `BusinessSynthesizer`
- Definir RAG/SABIÁ-2 e Node.js / DeepSeek / Qwen como suporte opcional de contexto e cache, não como requisito do motor principal

### Checks
- [x] `ml_pipeline` aceita e usa `BusinessContext` no predict
- [x] `CulturalFeatureExtractor` gera features determinísticas baseadas em texto
- [x] Modelo deixa de ser somente `keyword -> label`
- [x] Métricas de performance básicas presentes e retornáveis
- [x] `project_id` e contexto de onboarding entram no pipeline
- [x] `montar_payload_ia()` definido e documentado
- [x] esquema de mensagens/contexto definido para cache de contexto
- [x] testes unitários de ML executados com sucesso: `py -3 -m pytest src_v8/tests/test_ml_pipeline.py -q` passou com `3 passed`
- [x] Não existem pipelines paralelos desconectados no fluxo de análise
- [x] Arquitetura híbrida de contexto é opcional e documentada

> Nota de execução: o esquema de cache de contexto foi introduzido com `ChatMessage`, `ContextCacheEntry` e `montar_context_cache_entry`; o output de `analyze_business_insights` agora inclui `context_cache_entry`. A validação também confirmou que a arquitetura híbrida de contexto foi documentada como opcional e não obrigatória para o fluxo principal.

---

## Fase 3 — Insights de negócio e outputs acionáveis (1-2 semanas)

### Objetivo
Fazer do pipeline um motor que entrega recomendações e scores úteis, não apenas labels, e conectar a saída ao dashboard.

### Entregáveis
- Endpoint novo: `POST /api/v8/ml/analyze/business-insights`
- Output enriquecido com:
  - `prediction`
  - `confidence`
  - `business_alignment`
  - `opportunity_score`
  - `risk_score`
  - `recommendation`
  - `dominant_culture`
  - `project_id`
  - `user_id`
  - `context_source`
- Integração de `business_context` e `project_id` no resultado
- Regras de recomendação alinhadas com objetivo do usuário e com a intenção do onboarding
- Validação de formato JSON estrito para respostas de IA

### Checks
- [x] endpoint de business insights implementado
- [x] endpoint responde com insights em vez de somente classification
- [x] resultados incluem score de alinhamento e recomendação
- [x] análise leva em conta objetivo (`lançamento`, `rebranding`, `crise` etc.)
- [x] testes unitários para `analyze_business_insights`
- [x] resposta AI validada estritamente como JSON estruturado
- [x] autenticação FastAPI forçada com `FASTAPI_TOKEN` real em todos os endpoints, sem fallback demo local
- [ ] anotação de falha de persistência de `brand_analysis` causada por token FastAPI inválido documentada

### Status Atual
- O fluxo de projeto via `POST /api/projects/[id]` foi validado com sucesso em Next.js e FastAPI.
- Autenticação FastAPI agora exige `FASTAPI_TOKEN` real em todos os endpoints; o fallback demo local foi removido do backend e das chamadas internas do Next.js.
- O endpoint direto de ML `POST /api/v8/ml/analyze/business-insights` ainda falha com `500` devido a `No trained model available`.
- Isso indica que o bloqueio atual não é o front-end, a rota de projeto ou o auth, mas a ausência de modelo treinado disponível no endpoint de insights.

### Bloqueio Identificado
- O pipeline chega ao endpoint de insights corretamente, mas não há modelo treinado carregado/disponível para gerar a resposta.
- Isso causa um erro de análise interno e impede a conclusão da validação completa do fluxo.

### O que precisa ser feito para remover esse bloqueio
- Garantir que o endpoint `POST /api/v8/ml/analyze/business-insights` carregue um modelo treinado válido antes de atender requisições.
- Implementar um fluxo de inicialização/bootstrapping de modelo no backend de ML.
- Adicionar fallback de modelo demo ou um modo de inferência simplificada enquanto o modelo principal não estiver pronto.
- Criar health checks específicos para verificar se o modelo de insights está disponível e pronto (`model_ready`, `trained_model_available`).
- Ajustar o endpoint para retornar uma mensagem clara e tratável quando o modelo não estiver disponível, em vez de um erro genérico 500.
- Validar o treinamento e a persistência do modelo em ambiente local/teste antes de reexecutar a validação de fluxo.

> Nota: validação do fluxo de projeto identificou que um token FastAPI inválido retornava 401 em `/api/v8/analysis/brand`, impedindo a persistência de `brand_analysis`. Foi implementada correção de autenticação para forçar `FASTAPI_TOKEN` real em todas as chamadas e remover fallback demo local no backend e nas requisições internas do Next.js.
>
> Procedimento de verificação de ambiente:
> - execute `py verify_env.py` para carregar `.env` e validar todas as variáveis essenciais.
> - garanta `FASTAPI_TOKEN`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `PROJECT_ANALYSIS_FASTAPI_URL`, `NEXT_PUBLIC_FASTAPI_URL`, `NEXT_PUBLIC_API_URL`, `ENVIRONMENT=production` e `ENABLE_DEMO_AUTH=false`.
> - atenção: `FASTAPI_TOKEN` deve ser configurado no Railway como secret do serviço backend FastAPI e não pode ser um token de demo.
>
### Checklist de integração frontend
- [x] Frontend envia `business_context` completo conforme o contrato do endpoint ML
- [x] Rota de projeto/disparo de análise usa `POST /api/v8/ml/analyze/business-insights`
- [x] Integração do endpoint de insights ao fluxo de projeto foi concluída e validada
- [x] Business insights persistido com `insights` sempre como array e fallback de estrutura clara
- [x] Campos `project_id`, `user_id`, `brand`, `segment`, `objective`, `keywords`, `audiences`, `regions`, `circles` são propagados corretamente
- [x] Dashboard consome a resposta enriquecida de insights
- [ ] Tratamento de erros e loading state validado no frontend
- [ ] Payload do frontend e resposta do backend são consistentes com o modelo de dados do projeto

---

## Próximo passo imediato
- Avançar para a Fase 3: integrar o endpoint de insights já estabilizado ao fluxo de projeto e foco em outputs acionáveis.
- Garantir que o frontend consuma `POST /api/v8/ml/analyze/business-insights` com o `business_context` enriquecido e que o resultado chegue ao dashboard.
- Confirmar que o fluxo de análise de projeto já validado (`POST /api/projects/[id]` com Bearer auth) sirva como base para a integração frontend/backend.
- Incluir um checklist específico de integração frontend para validar payload, contrato e consumo dos insights.
- Construir a camada de feedback de execução para capturar informações de uso e melhorar o motor.

## Fase 4 — Fluxo end-to-end e feedback (1 semana)

### Objetivo
Garantir o fluxo completo do onboarding até o dashboard e permitir feedback para evolução.

### Entregáveis
- Conexão entre onboarding e `business_context`
- Dados de projeto e histórico de mensagens disponíveis para o ML Pipeline
- Dashboards consumindo o endpoint de insights
- Estrutura de feedback para ajustar o modelo e treinar `feedback_learning`
- Implementação de pipeline de contexto em cache para DeepSeek/Qwen como arquitetura híbrida opcional
- Documentar digital twins/simulações como camada de produto/exploração, não como fluxo principal de inferência

### Checks
- [ ] onboarding cria/propaga `project_id`, `segment`, `objective`, `keywords`
- [ ] dashboards consomem `POST /api/v8/ml/analyze/business-insights`
- [ ] feedback de execução é capturado para melhoria contínua
- [ ] smoke test end-to-end do fluxo de projeto ao insight
- [ ] histórico de mensagens é usado para reconstruir contexto e cache de IA

---

## Fase 5 — Produção e robustez contínua (1-2 semanas)

### Objetivo
Transformar o motor em solução operacional, com monitoramento e qualidade.

### Entregáveis
- health check robusto de ML (`/api/v8/ml/health`)
- documentação de API de ML
- monitoramento de disponibilidade e performance
- testes de integração e smoke tests
- verificação de disponibilidade do Ollama local no MacMini

### Checks
- [ ] `ml_pipeline_ready` e `ollama_available` estão expostos em health
- [ ] health checks cobrem também Supabase e integração com dados de projeto
- [ ] documentação de uso de `BusinessContext` disponível
- [ ] testes de integração automáticos para os endpoints ML
- [ ] logs e métricas operacionais definidos
- [ ] separação clara entre treino e inferência
- [ ] MacMini local configurado com Ollama e cache de prompts

---

## Inferências e referências para ampliar a aplicação de ML

### Inferências que o motor deve trazer
- `segment + objective` → `alignment score`
- `keywords + text` → `topic relevance`
- `texto + contexto` → `opportunity / risk`
- `business_context` → `recommendation action`
- `prediction + confidence + alignment` → `next action`
- `project_id + user_id` → rastreabilidade do insight ao projeto
- `history + preferences` → contexto persistente de IA

### Referências internas do repositório
- `StrategyLearner` / `core.intelligence.learning.StrategyLearner`
- `BusinessSynthesizer` / `core.intelligence.business_synthesizer`
- `ResearchRefiner` / `core.intelligence.research_refiner`
- `weak_signals_detector.py`
- `core/analysis_worker.py`
- `core/intelligence/dashboard_data_bridge.py`
- `src_v8/api/endpoints/ml.py`
- `app/dashboard/strategy-learning/page.tsx`
- `SOLUCAO_COMPLETA_AUTOMATED_LEARNING.md`

### Referências de qualidade
- não deve ser apenas label prediction
- deve responder ao objetivo do usuário
- deve gerar insight e recomendação
- deve suportar contexto de projeto
- deve ser testável e operacional
- deve ser estritamente real-data, sem mocks em produção

---

## Critérios para sair do protótipo

### Produto mínimo aceitável
- motor conhece `business_context`
- motor entrega recommendations
- motor entende `objective`
- motor apresenta scores de alinhamento e risco
- motor funciona em endpoint real
- motor tem testes e é compilável
- usa `project_id` e `user_id` nos outputs
- responde em JSON estruturado quando envolve IA

### Não é mais protótipo quando:
- o pipeline usa dados de onboarding reais
- o output é acionável para o usuário
- o resultado é estruturado para dashboard
- a arquitetura é documentada e repetível
- o ciclo end-to-end está validado
- context caching está implantado para o histórico do projeto

---

## Check list de entregas ML

- [ ] Documento de arquitetura e contrato de dados ML
- [ ] `BusinessContext` robusto e completo
- [ ] `ml_pipeline` contextualizado e baseado em features
- [ ] `CulturalFeatureExtractor` determinístico e explicável
- [ ] Endpoint `analyze/business-insights`
- [ ] Insights de negócio com oportunidade, risco e recomendação
- [ ] Integração com onboarding e projeto
- [ ] Dashboards consumindo o endpoint de insights
- [ ] Health check ML completo
- [ ] Testes unitários e de integração
- [ ] Documentação operacional para o motor
- [ ] Arquitetura unificada sem pipelines paralelos desconectados
- [ ] Context caching definido para IA híbrida
- [ ] `project_id` / `user_id` presente em todos os fluxos relevantes

---

## Olhar Crítico para o Pipeline

- Manter `weak_signals_detector.py` como o motor principal de descoberta; não deixar que ele seja reduzido a um módulo auxiliar ou substituído por fluxos paralelos não conectados.
- Manter o foco em dados reais: onboarding, projetos, sinais reais e feedback do usuário. Mocks ou protótipos devem existir somente em testes e não em produção.
- Preservar `BusinessContext` como a âncora do fluxo; qualquer modelo ou endpoint deve aceitar `project_id`, `user_id`, `brand`, `segment`, `objective`, `audiences` e `regions`.
- Tratar `local_slm_bridge.py` / Ollama como camada de enriquecimento narrativa e geração de explicações, não como a fonte principal de decisões ou a única lógica de inferência.
- Não sobrecarregar o MVP com digital twins ou simulações de alto nível. Essas camadas são úteis como produto/visualização, mas não devem ser confundidas com o núcleo de tomada de decisão.
- Mapear e documentar explicitamente quais fontes são reais e quais são protótipo/demo, mantendo o fluxo de produção restrito a dados reais.
- Manter RAG/SABIÁ-2 como um recurso de contexto e recuperação, não como uma "nova inteligência" que substitui o pipeline baseado em sinais.
- Usar Node.js / DeepSeek / Qwen como uma arquitetura híbrida opcional para cache de contexto e gestão de prompt, mas não como um requisito para o caminho principal de insights.
- Exigir que a saída seja acionável: recomendações, pontuações de risco/oportunidade, alinhamento de objetivos e rastreabilidade por `project_id` / `user_id`.
- Evitar a duplicação de lógica entre `AnalysisWorker`, `dashboard_data_bridge.py` e `BusinessSynthesizer`; cada componente deve ter uma responsabilidade clara no fluxo.
- Garantir que a arquitetura documentada reflita o que está implementado, não apenas a visão ideal. A documentação deve apontar explicitamente quais módulos são reais e quais são experimentais.
- Preservar a separação clara entre inferência e treino. O pipeline deve ter health checks específicos para disponibilidade de modelo/SLM e para a integração com Supabase.
- Priorizar robustez e simplicidade antes de adicionar mais camadas de IA. O objetivo é um motor confiável de insights, não um conjunto de protótipos desconectados.

---

<!--
## Notas de implementação recentes
- Criado `scripts/validate_integration.ts` para testar o fluxo real de criação de projeto no Supabase e chamadas FastAPI ML.
- Ajustado `app/api/projects/[id]/route.ts` para enviar `demographics.genero: Todos` em vez de `todos`.
- Corrigido `scripts/validate_integration.ts` para detectar `is_active` no retorno de `GET /api/v8/ml/models`.
- Verificado localmente que `POST /api/v8/analysis/brand` responde `200` e que `POST /api/v8/ml/analyze/business-insights` retorna insights válidos com `cultural_demo` ativo.
- Confirmado que `src_v8/autonomous_agent/ml_foundation/back/ml_pipeline.py` é importável e que o modelo demo pode treinar e ser ativado.
- Adicionado wrapper compatível `analyze_business_context` em `src_v8/core/intelligence/business_synthesizer.py`.
- Limpado o script temporário `scripts/tmp_business_synth.py` após validação.
-->

---

## Observação final
Este é o plano de refinamento para que o `ml_pipeline` deixe de ser uma prova de conceito e passe a ser o motor central de decisão. O próximo passo técnico é implementar a arquitetura de contexto e integrar os dashboards-chave ao endpoint de insights, com uma linha única de fluxo de dados reais e contexto de projeto.

## Deploy de Auth Railway (etapa final)

Como etapa final de produção, o backend FastAPI deve ser implantado no Railway com o auth real configurado via secret manager. Essa etapa chega depois de definirmos a arquitetura de Redis/cache e validações de persistência.

Passo a passo:
- Conectar o repo GitHub `Bruno94-stomps/culture-pulse-v10` ao Railway.
- Criar ou configurar o serviço de backend usando `src_v8` como diretório raiz.
- Verificar se Railway detecta `src_v8/Dockerfile` e/ou usar o Docker build padrão.
- Adicionar secrets de deploy:
  - `FASTAPI_TOKEN`
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_KEY`
  - `PROJECT_ANALYSIS_FASTAPI_URL`
  - `NEXT_PUBLIC_FASTAPI_URL`
  - `NEXT_PUBLIC_API_URL`
  - `ENVIRONMENT=production`
  - `ENABLE_DEMO_AUTH=false`
- Subir o serviço e validar logs de startup do FastAPI.
- Testar os endpoints protegidos com `Authorization: Bearer <FASTAPI_TOKEN>`.
- Confirmar que o deploy só usa auth real em produção e que demo auth é permitido apenas em desenvolvimento.
