# 🎯 PLANO DE ATIVAÇÃO CONTINUOUS LEARNING V9.7

Este documento detalha os próximos passos para colocar a inteligência adaptativa do Pulse em produção (24/7).

## 🔋 Estado das Engines (Migração concluída)
- [x] **ActiveLearning (Queries)**: Unificado no Supabase + Diálogo Conversacional.
- [x] **AutomatedLearning (Pesos Indústria)**: Unificado no Supabase + SGDRegressor Online.
- [x] **FeedbackEngine (Qualidade Sinais)**: Unificado no Supabase via tabela `signal_feedback`.
- [x] **RealTimeLearning (Performance)**: Unificado no Supabase via tabela `analysis_performance` (Bridge).

## 🛠️ Próximas Ações Imediatas (Prioridade 1)

(. ) valide se a tabela de brand_profiles já existe no Supabase
### 1. 🕐 Ativação do Scheduler de Coleta (CONCLUÍDO ✅)
Ativado o motor que constrói a "biografia" da marca automaticamente.
- [x] Integrado `StrategyLearner.start_scheduler()` no `src_v8/api/main.py` via `lifespan`.
- [x] Validado via scripts de diagnóstico (Cold Start fallback ativo).
- [ ] Monitorar o loop de coleta 24/7 para Nikon, Streetwear, Tech, etc.

### 2. 💬 Injeção Conversacional (Frontend Next.js)
Fazer com que o sistema "fale" com o analista através do novo endpoint `/uncertain`.
- [x] Criar componente `ConversationalPrompt.tsx` no Next.js.
- [x] Conectar ao endpoint `GET /api/v8/active-learning/uncertain`.
- [x] Implementar o envio de feedback `POST /api/v8/active-learning/feedback`.
- [x] Injetar componente no `DashboardShell` para ativação global.

### 3. 🏁 Validação de Malha Fechada (CONCLUÍDO ✅)
Testado o fluxo completo:
- [x] Coleta Automática (Simulada via Ingestão de Termo Incerto).
- [x] Identificação de Termo Incerto (GET /uncertain validado com `top_k`).
- [x] Pergunta ao Usuário -> Resposta do Usuário (Simulada via `submit_query_feedback`).
- [x] Re-Rank dos pesos: Retorno `recorded` e recálculo do Wilson Score confirmados.

### 4. 🛡️ Refinamento da Confiabilidade (Reliability V9.9) (CONCLUÍDO PARCIAL ✅)
Evoluir a "Veracidade Biográfica" dos sinais coletados.
- [x] **Remover Mocks de Narrativa**: Substituído `visual_evidence_score = 0.8` fixo por lógica dinâmica de extração de metadados (`image`, `thumbnail`, `media_url`).
- [x] **Scraping de Imagens**: Implementada extração real de thumbnails/OG-images para sinais RSS/News via `VisualEvidenceExtractor`.
- [x] **Calculadora de Reliability Dinâmica**: Criado `src_v8/core/reliability_engine.py` que ajusta o `reliability` (ALTA/MEDIA/BAIXA) baseado em Fonte + Prova Visual + Histórico.
- [x] **Integração no Fluxo**: O `ContextEnricherV2` agora utiliza o motor dinâmico para decidir a veracidade de cada sinal narrado.
- [ ] **Cross-Verification**: Implementar lógica que marca um sinal como "VERIFICADO" apenas se ele aparecer em mais de 2 fontes diferentes simultaneamente.

---

## ☁️ Persistência Supabase (Checklist de Verificação)
- [x] **FeedbackEngine (Sinais)**: Gravando features em `FLOAT8[]` para treinamento futuro da RandomForest.
- [x] **RealTimeLearning (Pesos Globais)**: Persistindo histórico de acurácia Predicted vs Actual em `analysis_performance`.
- [x] **Sync Cross-Node**: Garantir que múltiplos Workers leiam os mesmos pesos do Supabase.

## 🚀 Como Iniciar Agora
Para iniciar o sistema de aprendizado, execute:
```bash
# Integrar no seu processo de boot
export PYTHONPATH=$PYTHONPATH:./src_v8
python3 -c "from src_v8.core.learning.automated_learning_engine import AutomatedLearningEngine; engine = AutomatedLearningEngine(); engine.start_scheduler()"
```
