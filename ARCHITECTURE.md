# Architecture Overview

## System Architecture

This repository now follows a clear separation between frontend, backend, data, and ML intelligence layers:

- Frontend: `culturepulse-web/` — Next.js App Router
- Backend: `src_v8/api/` — FastAPI service
- Data platform: Supabase — persistent storage for `projects`, `profiles`, `cultural_signals`, `messages`, `embeddings`, `model_feedback`
- ML and intelligence: local Python modules in `src_v8/` and optional local Ollama on MacMini
- Deployment:
  - Frontend deployed to Cloudflare Pages
  - Backend deployed to Railway as a Docker container

## Architecture Details

- See [`ARCHITECTURE_DETAIL.md`](ARCHITECTURE_DETAIL.md) for the concrete file-level mapping, integration points, and recommended consolidation tasks.

## Unified ML Flow

The consolidated architecture is one single flow from onboarding/project context to dashboard insight:

1. Frontend captures onboarding and user project context
2. Backend stores `project_id`, `user_id`, `BusinessContext` in Supabase
3. ResearchRefiner + BusinessSynthesizer refine search terms and define API collection strategy
4. Collectors request real API data and send raw signals to WeakSignalsDetector
4.5 The backend now builds a `pipeline_context` in `collection.py` and propagates `onboarding_context` through `orchestrator.py` into the metrics engine so weak signal detection is guided by business intent.
5. WeakSignalsDetector detects weak signals and produces candidate insights
6. AnalysisWorker enriches those signals with topics, actions, scores and business metadata
7. DashboardDataBridge derives dashboard datasets for the frontend
8. Local SLM Bridge (Ollama) provides narrative generation and context-aware responses
9. Feedback is captured and sent back to the ML pipeline for continuous learning

## Component Diagram

```mermaid
flowchart TD
    F[Frontend Next.js]
    B[FastAPI Backend]
    S[Supabase: projects / profiles / messages / signals / feedback]
    R[ResearchRefiner / BusinessSynthesizer]
    C[Collectors / Real APIs]
    W[WeakSignalsDetector]
    A[AnalysisWorker + Enrichers]
    D[Dashboard Data Bridge]
    L[Local SLM Bridge (Ollama)]
    N[Optional Node.js Context Cache / DeepSeek-Qwen]

    F -->|onboarding + project context| B
    B -->|store + load context| S
    B -->|build pipeline_context (onboarding/project)| R
    B -->|pass onboarding_context downstream| A
    R -->|refined terms + strategy| C
    C -->|raw signals + pipeline_context| W
    W -->|weak signals| A
    A -->|enriched signals + onboarding_context| D
    D -->|dashboard datasets| B
    B -->|insights API| F
    R -->|narrative requests| L
    L -->|local SLM responses| R
    F -->|chat history / messages| N
    N -->|context cache| B
    S -->|persistent state| B
```

## What changed in this architecture

- The ML flow is now explicit and single-path: onboarding → context → collection → weak signal detection → enrichment → dashboard.
- `weak_signals_detector.py` is the primary detection engine, not a side module.
- `ResearchRefiner` is upstream: it defines the search strategy and business intent before data collection.
- `collection.py` now builds and passes a `pipeline_context` containing onboarding/project context to `orchestrator.py`, which resolves user intent and feeds it into the cultural metrics and weak signal pipeline.
- `AnalysisWorker` and `DashboardDataBridge` are downstream enrichment and presentation layers.
- `context_enricher_v2.py` now explicitly accepts `onboarding_context` from the worker pipeline, closing the loop between onboarding and dashboard narrative enrichment.
- `pipeline/enrich` has an explicit `onboarding_context` payload path so API clients can provide business intent directly to the enrichment flow.
- `local_slm_bridge.py` is a local Ollama bridge for narrative generation, not a separate product flow.
- A hybrid Node.js / context caching service is acknowledged as optional for DeepSeek/Qwen.

## Critical architecture guardrails

- Preserve `weak_signals_detector.py` as the core discovery engine; it must remain the primary path for signal detection.
- Keep `BusinessContext` as the anchor for all ML flows, with `project_id`, `user_id`, `brand`, `segment`, `objective`, `audiences` and `regions` propagated end-to-end.
- Use `local_slm_bridge.py` / Ollama for narrative enrichment and explanation, not as the main decision-making engine.
- Treat digital twins and simulations as product/visualization layers, not as the core inference pipeline.
- Use RAG/SABIÁ-2 for contextual retrieval and support, not as a separate intelligence flow that bypasses the weak signal motor.
- Make the Node.js / DeepSeek / Qwen hybrid optional: only adopt it for prompt/context caching value, not to make the architecture dependent on it.
- Ensure the documentation separates the implemented main flow from experimental or optional components.
- Preserve a clear boundary between inference and training, and require health checks for both model availability and Supabase integration.
- Prioritize reliability and simplicity before adding more AI layers; the goal is a dependable business insights engine, not multiple disconnected prototypes.

## Deployment Flow

1. `test`
   - validate Python backend
   - run frontend lint and type-check
   - run tests and static analysis

2. `build-backend`
   - build the FastAPI Docker image
   - push the image to Docker registry or Railway container registry

3. `build-frontend`
   - install `culturepulse-web` dependencies
   - perform frontend lint and type-check
   - build the Next.js app

4. `deploy-cloudflare-pages`
   - publish the generated Next.js app to Cloudflare Pages

5. `deploy-railway`
   - deploy the backend Docker image to Railway

## Runtime

- Next.js frontend calls the backend via `FASTAPI_URL`
- Supabase is the primary persistent data layer
- Railway hosts the FastAPI container as a managed service
- Cloudflare Pages hosts the frontend static/site output
- Local Ollama can run on MacMini to provide `local_slm_bridge.py` capabilities

## Local Development

```bash
# Backend
cd src_v8
py -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend
cd culturepulse-web
npm install
npm run dev
```

## Environment

Required environment variables:

- `FASTAPI_URL` — target FastAPI base URL
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `OLLAMA_URL` or local `http://localhost:11434` for local SLM
- Railway and Cloudflare secrets in CI: `RAILWAY_TOKEN`, `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_PROJECT_NAME`
