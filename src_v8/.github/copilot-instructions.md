# Culture Pulse V9.0 - AI Copilot Instructions

## 🎯 Project Overview

**Culture Pulse** is a Brazilian cultural intelligence system that analyzes real-time cultural signals across 16 cultural circles and 8+ data sources (YouTube, Reddit, Spotify, NewsAPI, Google Trends, Instagram, Meetup, Eventbrite) to help brands survive market transformation through **cultural imagination** - predicting cultural shifts 6-12 months ahead.

### Core Value Propositions
- **Real-time cultural analysis** via integrated async data collectors
- **Proprietary metrics**: Cultural Score, Alma Brasileira (cultural soul), IICB (Brazilian Cultural Intelligence Index)
- **Predictive capabilities**: Emerging profiles, cultural tensions, future scenarios
- **Multi-channel delivery**: Streamlit dashboard + FastAPI REST + automated insights

---

## 🏗️ Architecture Essentials

### Directory Structure (Key Components)
```
src_v8/
├── core/                    # Engines: cultural_engine.py, circles_processor.py, 
│                           # tfidf_analyzer.py, alma_brasileira.py, advanced_analytics_engine.py
├── collectors/             # Data collection: data_collectors.py orchestrator, 
│                           # SecureConfig for .env handling
├── dashboard/              # Streamlit UI: cultural_dashboard_integrated.py (7 tabs)
├── api/                    # FastAPI: main.py with endpoints in endpoints/ folder
├── config/                 # centralized_config.py (single source of truth for env/API keys)
├── autonomous_agent/       # ML Foundation + autonomous reasoning
├── monitoring/             # Health checks, performance tracking
├── diagnostic/             # System validation (orchestrator_diagnostics.py)
└── alerts/                 # Multi-channel notification system
```

### Critical Data Flows
```
┌─────────────────────────────────────────────────────────────────────┐
│              CULTURE PULSE DATA FLOW ARCHITECTURE                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  EXTERNAL APIs (8 sources)                                         │
│  ├── YouTube, Reddit, Spotify                                     │
│  ├── NewsAPI, Google Trends                                       │
│  └── Instagram, Meetup, Eventbrite                                │
│                 │                                                  │
│                 ▼                                                  │
│  COLLECTORS LAYER (async/concurrent)                              │
│  ├── data_collectors.py orchestrator                              │
│  └── Returns: List[CulturalSignal]                                │
│                 │                                                  │
│                 ▼                                                  │
│  CACHE LAYER (15-min TTL)                                         │
│  ├── Local: DataCollectorCache                                    │
│  └── Redis: cache_redis.py (fallback available)                   │
│                 │                                                  │
│                 ▼                                                  │
│  PROCESSORS (enrich data)                                         │
│  ├── circles_processor.py                                         │
│  ├── demographic_enricher.py                                      │
│  └── tension_analyzer.py                                          │
│                 │                                                  │
│                 ▼                                                  │
│  ANALYSIS ENGINES (core intelligence)                             │
│  ├── cultural_engine.py (main)                                    │
│  ├── tfidf_analyzer.py                                            │
│  ├── alma_brasileira.py                                           │
│  ├── authenticity_analyzer.py                                     │
│  └── advanced_analytics_engine.py                                 │
│                 │                                                  │
│        ┌────────┼────────┐                                         │
│        │        │        │                                         │
│        ▼        ▼        ▼                                         │
│    DASHBOARD  API REST  ALERTS                                    │
│   (Streamlit) (FastAPI) (Multi-ch)                                │
│                                                                    │
└─────────────────────────────────────────────────────────────────────┘
```

1. **Collection → Processing → Analysis**
   - Collectors async-fetch from APIs → normalize to `CulturalSignal` dataclass
   - Processors enrich with demographic/regional/tension data
   - Analyzers apply TF-IDF, sentiment, authenticity scoring

2. **Entry Points**
   - **Dashboard**: `dashboard/run_dashboard.py` → Streamlit app (7 tabs)
   - **API**: `api/run_api.py` → FastAPI server (FastAPI available check required)
   - **Batch**: `culture_pulse_master_v8.py` → Master orchestrator

---

## 🔌 Critical Integration Patterns

### Environment & Configuration
- **Load paths explicitly**: `config/secure_config.py` uses `load_dotenv(str(env_path))` with explicit Path
- **No relative paths**: Always use absolute paths from PROJECT_ROOT
- **Test APIs before use**: See `test_apis_final.py` - uses async collectors to verify real data

### Data Collection Pattern
```python
# From data_collectors.py - standard collector signature
collector = YouTubeCollector(config)
signals: List[CulturalSignal] = await collector.collect(search_terms, days=7)
# Returns CulturalSignal dataclass with: plataforma, termo, momentum, volume, 
# sentiment, relevancia_cultural, timestamp, demographic_data, tension_indicators
```

### API Access Pattern (from api/main.py)
- All endpoints require authentication header: `Authorization: Bearer {token}`
- Three tiers: `cp_demo_2025_free_tier`, `cp_pro_2025_advanced`, `cp_enterprise_2025_unlimited`
- Use middleware: `auth.py` for validation, rate limiting in production
- **Test auth tiers**: Use `api/middleware/auth.py` to verify token validation
  ```bash
  # Free tier test (limited to 100 requests/hour)
  curl -H "Authorization: Bearer cp_demo_2025_free_tier" http://localhost:8000/api/v8/analysis/brand
  # Pro tier test (1000 requests/hour)
  curl -H "Authorization: Bearer cp_pro_2025_advanced" http://localhost:8000/api/v8/circles/analyze
  # Enterprise tier (unlimited)
  curl -H "Authorization: Bearer cp_enterprise_2025_unlimited" http://localhost:8000/api/v8/tfidf/analyze
  ```

### Async/Concurrency
- Prefer `asyncio` + `aiohttp` for I/O bound operations (API calls)
- Use `core/async_processing.py`: `run_async_batch()`, `run_api_batch()` utilities
- Dashboard uses `@st.cache_resource` for expensive operations

---

## 📝 Project-Specific Conventions

### File Organization Rules
1. **No loose analytics**: All analysis goes in `core/` as dedicated *_engine or *_analyzer classes
2. **Config inheritance**: Import from `config.centralized_config` not individual modules
3. **API routes must register**: Add routers to `api/main.py` include_router() block
4. **Tests require conftest.py**: Path manipulation at root level, see [conftest.py](conftest.py)

### Naming Conventions
- Engines: `*_engine.py` (e.g., `cultural_engine.py`, `sentiment_analysis_engine.py`)
- Analyzers: `*_analyzer.py` (e.g., `authenticity_analyzer.py`, `brand_intelligence_analyzer.py`)
- Collectors: `*_collector.py` in `collectors/` folder
- Dataclasses: Use type hints; `CulturalSignal` is standard output type

### API Response Pattern
- All endpoints return JSON with structure: `{ "status": "success/error", "data": {...}, "metadata": {...} }`
- Status codes: 200 (OK), 400 (validation), 401 (auth), 429 (rate limit), 500 (server error)
- Use Pydantic models for request/response validation

---

## 🧪 Testing & Verification Workflows

### Critical Test Scenarios
**Before deploying any changes, validate these scenarios:**

1. **API Authentication (3 tiers)**
   ```bash
   # Test each tier returns correct rate limits
   pytest tests/test_api_auth.py -v
   ```

2. **Data Collection Failure Modes**
   ```bash
   # Test collector fallback when API unavailable
   pytest tests/test_collector_fallback.py -v
   ```

3. **Cache Consistency**
   ```bash
   # Ensure cache expiry + Redis fallback work
   pytest tests/test_cache_behavior.py -v
   ```

4. **Dashboard Component Loading**
   ```bash
   # All 7 tabs load without errors
   pytest tests/test_dashboard_components.py -v
   ```

5. **Async Concurrency**
   ```bash
   # 50+ concurrent collectors don't deadlock
   pytest tests/test_async_scaling.py -v
   ```

6. **Configuration Loading**
   ```bash
   # Load .env from any directory (critical fix from v8.0)
   python test_api_simple.py && echo "✅ Config loads correctly"
   ```

### Running Tests
```bash
# Quick connectivity check
python test_apis_final.py          # All 5 APIs async test
python test_api_simple.py          # Basic .env loading

# System diagnostics (comprehensive)
python diagnostic/run_diagnostics.py [full|quick|ui|monitor]
python diagnostic/orchestrator_diagnostics.py --mode full

# Pytest (standard)
pytest tests/ -v

# Full integration test (all systems)
pytest tests/ -v -m integration
```

### Diagnostic System (`diagnostic/diagnostic.py`)
Validates:
- Python version compatibility (3.8+)
- Dependencies installed (all requirements.txt)
- Project structure (24 key directories)
- Environment variables (8 API keys loaded correctly)
- API connectivity (async checks for all 8 APIs)
- Core components importable (13 engines)
- Performance baseline (< 5sec response time target)
- Auth tier validation

---

## ⚡ Performance & Optimization

### Caching Strategy
- **LocalCache**: `DataCollectorCache` in data_collectors.py (15-min TTL default)
- **Redis Fallback**: Check `core/cache_redis.py` - if Redis unavailable, use local
- **Streamlit Cache**: Use `@st.cache_data` for analytics, `@st.cache_resource` for objects

### Large Dataset Handling
- Collectors limit to **last 7 days** by default (configurable in `data_collectors.py`)
- Use **batch processing**: `run_api_batch()` from `core/async_processing.py`
- Dashboard limits displayed rows (configurable in `dashboard/utils.py`)

### Latency Monitoring
- Check `monitoring/latency_metrics.py` for real-time performance tracking
- API endpoints logged via `dashboard/source_indicators.py`

---

## 🔐 Security & Secrets

### Credential Handling
- **All keys in .env**: Never hardcode API keys, use `config.secure_config.SecureConfig`
- **Keys required**: YOUTUBE_API_KEY, REDDIT_CLIENT_ID/SECRET, SPOTIFY_CLIENT_ID/SECRET, NEWS_API_KEY
- **Missing keys**: Collectors gracefully fallback to simulated data (log as warning)

### Rate Limiting
- Each API has quota limits (YouTube: 10k/day, Reddit: 60/min for OAuth)
- Check `api/middleware/rate_limit.py` - implemented per-client, per-endpoint
- Implement exponential backoff in collectors for 429 responses

---

## 🚀 Quick Start for Contributors

1. **Understand the pipeline**: Read [arquitetura/MAPA_VISUAL_RECOMENDACOES_FINAIS.md](arquitetura/MAPA_VISUAL_RECOMENDACOES_FINAIS.md)
2. **Run diagnostics**: `python diagnostic/run_diagnostics.py full`
3. **Start development**:
   - Dashboard: `python dashboard/run_dashboard.py`
   - API: `python api/run_api.py --reload`
   - Combined: `python start_culture_pulse_v9.py`
4. **Test changes**: Run relevant test file, then `pytest tests/` for full suite

---

## 📚 Key Reference Files

| File | Purpose |
|------|---------|
| [culture_pulse_master_v8.py](culture_pulse_master_v8.py) | Master orchestrator, understand full flow |
| [core/cultural_engine.py](core/cultural_engine.py) | Core analysis engine, central logic |
| [collectors/data_collectors.py](collectors/data_collectors.py) | All 8 collectors unified, modular pattern |
| [api/main.py](api/main.py) | FastAPI app, middleware setup, router registration |
| [dashboard/cultural_dashboard_integrated.py](dashboard/cultural_dashboard_integrated.py) | Main UI (7 tabs) |
| [config/centralized_config.py](config/centralized_config.py) | Single source of truth for config |
| [diagnostic/diagnostic.py](diagnostic/diagnostic.py) | System validation, debugging aid |

---

## 🎓 Learning Patterns from Codebase

### Pattern 1: Adding a New Analyzer
1. Create `core/new_analyzer.py` with class inheriting base analyzer
2. Implement `analyze(signals: List[CulturalSignal]) → Dict` method
3. Register in `cultural_engine.py` pipeline
4. Add API endpoint in `api/endpoints/new_feature.py`
5. Add route in `api/main.py`: `app.include_router(new_router, prefix="/api/v8")`

### Pattern 2: Adding a New Data Source
1. Create `collectors/new_source_collector.py` with async `collect()` method
2. Return `List[CulturalSignal]` with populated fields
3. Register in `data_collectors.py` orchestrator
4. Add env var in `config/centralized_config.py`
5. Test with `test_apis_final.py`

### Pattern 3: Dashboard Visualization
1. Create component in `dashboard/` as separate module
2. Import in `cultural_dashboard_integrated.py`
3. Add to tab structure (7 tabs: Overview, Analysis, Circles, Trends, Alerts, ML, Settings)
4. Use `st.cache_resource` for data, `st.plotly_chart()` for viz

---

## ⚠️ Common Pitfalls & Solutions

| Issue | Solution |
|-------|----------|
| API keys not loading | Check `config/secure_config.py` explicit path; verify .env in project root |
| Collector returns empty | Check API quota; look for FALLBACK mode in logs; test with `test_apis_final.py` |
| Streamlit cache stale | Use `st.cache_data(ttl=300)` with explicit TTL; call `st.rerun()` for force refresh |
| Async deadlock | Ensure `asyncio.run()` called once per process; use `nest_asyncio` if nested loops |
| Import errors | Run from project root; verify `conftest.py` path setup; use `sys.path.insert(0, ...)` |

---

## 🔄 Versioning & Iterations

- **Current**: V8.0 (dashboard) + V9.0 (architecture improvements)
- **Next steps documented in**: ROADMAP_CONSOLIDADO_2025.txt, arquitetura/ folder
- **Breaking changes**: Update centralized_config.py first, then cascade to dependent modules

