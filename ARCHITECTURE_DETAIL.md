# Architecture Detail

## Purpose

This document maps the current implementation files to the unified ML and intelligence flow described in `ARCHITECTURE.md`.
It is intended to clarify the concrete integration points and the responsibilities of each component.

---

## Unified Flow Overview

1. Frontend onboarding / project context
2. Backend stores / loads `project_id`, `user_id`, `BusinessContext`
3. `ResearchRefiner` and `BusinessSynthesizer` define search strategy and intent
4. Collectors call real APIs and return raw signal data
5. `WeakSignalsDetector` detects weak signals from raw data
6. `AnalysisWorker` enriches signals with topic, action and business metadata
7. `DashboardDataBridge` transforms enriched signal outputs into dashboard datasets
8. `LocalSLMBridge` / Ollama provides narrative generation for context-aware responses
9. Feedback loops into `feedback_learning` and future refinements

---

## File and Module Map

### Frontend / project context

- `culturepulse-web/` — Next.js frontend
- `app/dashboard/strategy-learning/page.tsx` — dashboard consumes ML strategy status and insights
- `src_v8/api/endpoints/ml.py` — ML endpoints used by frontend and internal services

### Backend / API / persistence

- `src_v8/api/endpoints/ml.py`
  - exposes ML endpoints such as `/api/v8/ml/models`, `/strategy-status`, `/models/{model_name}/train`
  - includes `BusinessContext` Pydantic model and backend ML health checks
- `culturepulse-web/supabase/schema.sql`
  - defines main tables `profiles`, `cultural_signals`, `signal_embeddings`
  - should be extended with `projects`, `messages`, `signal_feedback`, `model_weights`

### Research and collection strategy

- `src_v8/core/intelligence/research_refiner.py`
  - upstream strategic agent for refining research terms
  - uses `BusinessContext`, `MLIntegratorSimple`, and `GitHubModelsEngine`
  - outputs refined terms, recommended APIs, confidence and metrics
- `src_v8/core/intelligence/business_synthesizer.py`
  - central synthesizer for business-oriented cultural insights
  - uses `LocalSLMBridge` and `dynamic_scorer`
  - enriches insights with narrative and authenticity context
- `src_v8/scripts/run_real_collection.py`
  - orchestrates data collection from real APIs
  - invokes `WeakSignalsDetector` on collected raw signals
  - currently contains optional dry-run fallback logic that should be removed for production

### Weak signal detection

- `src_v8/autonomous_agent/weak_signals_detector.py`
  - primary weak signal detection engine
  - performs temporal analysis, semantic emergence, clustering and cultural shift analysis
  - integrates with `MLIntegratorSimple` and optionally `GitHubModelsEngine`
  - currently the core detection module in the unified flow

### ML Foundation components

- `src_v8/autonomous_agent/ml_foundation/ml_integrator_simple.py`
  - initialization wrapper for ML components
  - loads `FeedbackLearningEngine`, `GitHubModelsEngine`, `AdvancedNLPProcessor`, `CulturalEmbeddingsSimple`
- `src_v8/autonomous_agent/ml_foundation/github_models.py`
  - integration layer for GitHub Models / OpenAI-style API
  - used by `weak_signals_detector` and `ResearchRefiner`
- `src_v8/autonomous_agent/ml_foundation/bertimbau_real_engine.py`
  - BERTimbau embedding engine with PyTorch fallback
  - intended for semantic and cultural embedding generation
- `src_v8/autonomous_agent/ml_foundation/bert_finetuner.py`
  - fine-tuning pipeline for BERTimbau domain adaptation
- `src_v8/autonomous_agent/ml_foundation/feedback_learning.py`
  - feedback-driven training engine for quality/effectiveness prediction

### Enrichment and downstream intelligence

- `src_v8/core/analysis_worker.py`
  - async pipeline worker that applies registered enrichers to raw signals
  - intended to orchestrate `weak_signals_detector` output and other engine enrichers
- `src_v8/core/intelligence/topic_engine.py`
  - topic modeling engine for signal clustering and dashboard topic assignment
  - should be used as an enricher inside `AnalysisWorker`
- `src_v8/core/intelligence/dashboard_data_bridge.py`
  - derives dashboard-ready datasets from enriched signals
  - builds weak signals, emerging trends, profiles, and cultural relationships
- `src_v8/core/intelligence/strategic_actions_engine.py`
  - transforms enriched signal attributes into action recommendations
  - provides playbook steps, channels, KPIs, and impact estimates

### Local LLM / Ollama

- `src_v8/core/intelligence/local_slm_bridge.py`
  - local Ollama bridge for narrative generation using `llama3:8b`
  - includes caching of prompt results and availability detection
  - should be used by `BusinessSynthesizer` and other narrative layers

### Integration / validation

- `src_v8/api/integration_validator.py`
  - contains checks for core modules such as `research_refiner`, `weak_signals_detector`, `github_models_engine`, `ml_integrator_simple`
- `src_v8/core/classifiers/enhanced_ml_integration.py`
  - likely part of the advanced classifier path for ML + research refinement

---

## Recommended immediate consolidation tasks

1. Standardize `BusinessContext` across backend and ML modules.
2. Extend Supabase schema with `projects`, `messages`, `model_feedback`, `signal_feedback`.
3. Remove or disable mock/dry-run logic from `run_real_collection.py` for production.
4. Ensure `WeakSignalsDetector` is the canonical weak-signal engine, not a side branch.
5. Use `ResearchRefiner` output as the source of truth for collector queries.
6. Register `TopicEngine` and `StrategicActionsEngine` inside `AnalysisWorker`.
7. Make `local_slm_bridge.py` optional but available for narrative generation on MacMini.
8. Add `montar_payload_ia()` as a shared helper for building prompt + context payloads.
9. Document which components are upstream vs downstream in this file.

---

## Notes on hybrid architecture

- A Node.js context caching layer is not currently implemented.
- For a hybrid strategy, use Node.js for chat history / context caching and Python for heavy raw data extraction.
- The current Python backend is already the central ML intelligence layer.
- `ARCHITECTURE.md` now captures the high-level flow; this file explains the concrete file-level mapping.

---

## Next step

Use this document as the reference for the first refactoring sprint: align `weak_signals_detector.py`, `ResearchRefiner`, `BusinessSynthesizer`, `AnalysisWorker`, and `DashboardDataBridge` into one coherent, traceable pipeline.
