#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI Main Application - Culture Pulse V9.0
Aplicação principal da API REST

🎯 FUNCIONALIDADES V9.0:
- Endpoints para análise cultural completa
- Sistema de autenticação e rate limiting
- Cache Redis distribuído com fallback local
- Machine Learning Pipeline cultural brasileiro
- Sistema de alertas multi-canal
- Dashboard Next.js (App Router) integration
- Documentação automática (Swagger/OpenAPI)
- Validação de dados com Pydantic
- Logs estruturados e monitoramento
"""

import sys
import os

# Adicionar path para imports absolutos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.trustedhost import TrustedHostMiddleware
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from contextlib import asynccontextmanager
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ FastAPI não disponível: {e}")
    FASTAPI_AVAILABLE = False

import logging
import time
from typing import Dict, Any

try:
    # WhatsApp router (Removed/Moved in V9.0 cleanup? Keeping try/except)
    whatsapp_router = None
except Exception as e:
    whatsapp_router = None
    logging.getLogger(__name__).warning(f"⚠️ WhatsApp router não carregado: {e}")

# Streaming WebSocket (V9.0)
try:
    from .endpoints.streaming import streaming_router
except Exception as e:
    streaming_router = None
    logging.getLogger(__name__).warning(f"⚠️ Streaming router não carregado: {e}")

# Importações opcionais (podem falhar se dependências não estão instaladas)
try:
    from .endpoints.analysis import analysis_router
except Exception as e:
    logger_temp = logging.getLogger(__name__)
    logger_temp.warning(f"⚠️ Could not import analysis router: {e}")
    analysis_router = None

try:
    from .endpoints.circles import circles_router
except Exception as e:
    circles_router = None

try:
    from .endpoints.tfidf import tfidf_router
except Exception as e:
    tfidf_router = None

try:
    from .endpoints.alma import alma_router
except Exception as e:
    alma_router = None

try:
    from .endpoints.health import health_router
except Exception as e:
    health_router = None

try:
    from .endpoints.collection import collection_router
except Exception as e:
    collection_router = None

# Legacy collectors.py router has been unified into the collection endpoint module.
collectors_router = None

try:
    from .endpoints.ml import ml_router
except Exception as e:
    logging.getLogger(__name__).warning(f"⚠️ ML router não carregado: {e}")
    ml_router = None

try:
    from .endpoints.cache import router as cache_router
except Exception as e:
    cache_router = None
    logging.getLogger(__name__).warning(f"⚠️ Cache router não carregado: {e}")

# Advanced Analytics (V9.1 rescue)
try:
    from .endpoints.advanced_analytics.endpoints import router as advanced_router
except Exception as e:
    advanced_router = None
    logging.getLogger(__name__).warning(f"⚠️ Advanced analytics router não carregado: {e}")

try:
    from .endpoints.config_plans import router as config_plans_router
except Exception as e:
    config_plans_router = None
    logging.getLogger(__name__).warning(f"⚠️ Config plans router não carregado: {e}")

try:
    from config.plan_config import PLAN_CONFIG
except Exception:
    try:
        from src_v8.config.plan_config import PLAN_CONFIG
    except Exception:
        PLAN_CONFIG = None

try:
    from alerts.api_endpoints import alerts_router
except Exception as e:
    alerts_router = None

try:
    from .endpoints.feedback import router as feedback_router
except Exception as e:
    feedback_router = None

try:
    from .endpoints.topics import router as topics_router
except Exception as e:
    topics_router = None

try:
    from .endpoints.pest import router as pest_router
except Exception as e:
    pest_router = None

try:
    from .endpoints.dashboard_insights import router as dashboard_insights_router
except Exception as e:
    dashboard_insights_router = None

try:
    from .endpoints.emerging_profiles import router as emerging_profiles_router
except Exception as e:
    emerging_profiles_router = None

try:
    from .endpoints.intelligence import router as intelligence_router
except Exception as e:
    intelligence_router = None

try:
    from .endpoints.cluster_labels import router as cluster_labels_router
except Exception as e:
    cluster_labels_router = None

try:
    from .endpoints.risk import router as risk_router
except Exception as e:
    risk_router = None

try:
    from .endpoints.pipeline import router as pipeline_router
except Exception as e:
    pipeline_router = None

try:
    from .endpoints.signals import router as signals_router
except Exception as e:
    signals_router = None

try:
    from .endpoints.graph_network import router as graph_network_router
except Exception as e:
    graph_network_router = None

try:
    from .endpoints.active_learning import router as active_learning_router
except Exception as e:
    active_learning_router = None

try:
    from .endpoints.recall import router as recall_router
except Exception as e:
    recall_router = None

try:
    from .endpoints.industry import router as industry_router
except Exception as e:
    industry_router = None

try:
    from .endpoints.cross_impact import router as cross_impact_router
except Exception as e:
    cross_impact_router = None

try:
    from .endpoints.stability_risk import router as stability_risk_router
except Exception as e:
    stability_risk_router = None

try:
    from .endpoints.explore import router as explore_router
except Exception as e:
    explore_router = None

try:
    from .middleware.auth import get_current_client
except Exception as e:
    get_current_client = None

try:
    from .middleware.rate_limit import rate_limit_middleware
except Exception as e:
    rate_limit_middleware = None

try:
    from .middleware.cache import add_cache_middleware, cache_router
except Exception as e:
    add_cache_middleware = None
    cache_router = None

try:
    from core.engines.cultural_engine import create_cultural_engine
except Exception as e:
    create_cultural_engine = None

try:
    from core.cache.cache_redis import get_cache
except Exception as e:
    get_cache = None

# Configurar logging
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s:%(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)
logger = logging.getLogger(__name__)

# Instância global do engine cultural
cultural_engine = None
business_synthesizer = None
api_orchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação"""
    global cultural_engine
    
    # Startup
    logger.info("🚀 Inicializando Culture Pulse V9.0 API")
    
    # 1. Inicializar StrategyLearner e Ativar Scheduler (24/7 Service)
    try:
        from core.intelligence.learning.StrategyLearner import get_strategy_learner
        strategy = get_strategy_learner()
        # Inicia o agendador em background (Coleta baseada no ONBOARDING)
        import asyncio
        asyncio.create_task(strategy.start_scheduler())
        logger.info("✅ StrategyLearner: Scheduler ativado (Weak Signals via Onboarding)")
    except Exception as e:
        logger.warning(f"⚠️ StrategyLearner falhou ao iniciar: {e}")

    # 3. Inicializar BusinessSynthesizer (IA Generativa de Contexto)
    global business_synthesizer
    try:
        from core.intelligence.business_synthesizer import BusinessSynthesizer
        business_synthesizer = BusinessSynthesizer()
        logger.info("✅ BusinessSynthesizer: IA de Contexto carregada")
    except Exception as e:
        logger.warning(f"⚠️ BusinessSynthesizer não disponível: {e}")

    # 4. Inicializar OrchestratorV9 (Coordenação de Coletores)
    global api_orchestrator
    try:
        from collectors.orchestrator import OrchestratorV9
        api_orchestrator = OrchestratorV9()
        logger.info("✅ OrchestratorV9: Sistema de coleta unificado pronto")
    except Exception as e:
        logger.warning(f"⚠️ OrchestratorV9 não disponível: {e}")

    # Inicializar cache Redis (opcional)
    if get_cache:
        try:
            cache = get_cache()
            cache_stats = cache.get_stats()
            logger.info(f"✅ Cache inicializado: {cache_stats['cache_type']}")
        except Exception as e:
            logger.warning(f"⚠️ Cache não disponível: {e}")
    
    # Inicializar Cultural Engine (opcional)
    if create_cultural_engine:
        try:
            cultural_engine = create_cultural_engine()
            logger.info("✅ Cultural Engine carregado")
        except Exception as e:
            logger.warning(f"⚠️ Cultural Engine não disponível: {e}")
    
    # Cache warming para dados críticos
    logger.info("✅ API iniciada com sucesso")
    
    yield
    
    # Shutdown
    logger.info("⏹️ Finalizando Culture Pulse V9.0 API")

# Criar aplicação FastAPI
app = FastAPI(
    title="Culture Pulse V9.0 API",
    description="""
    🧠 **API de Análise Cultural Brasileira V9.0**
    
    Sistema avançado de inteligência cultural para marcas e empresas que desejam
    compreender e se conectar com diferentes públicos brasileiros.
    
    ## 🎯 Principais Funcionalidades V9.0
    
    * **Cache Redis Distribuído**: Performance otimizada com fallback local
    * **Machine Learning Pipeline**: Modelos culturais brasileiros especializados
    * **Sistema de Alertas**: Notificações multi-canal (email/Slack/webhook)
    * **Next.js Integration**: Dashboard de alta performance (App Router)
    * **Análise Completa**: Score cultural baseado em 16 círculos culturais brasileiros
    * **Alma Brasileira**: Medição de autenticidade e valores culturais
    * **TF-IDF Cultural**: Relevância de termos culturais em conteúdos
    * **Segmentação**: Análise por localização, demografia e segmento de mercado
    
    ## 🔐 Autenticação
    
    Utilize Bearer Token para autenticação em todos os endpoints protegidos.
    
    ## 📊 Rate Limiting & Planos (Migrado para Supabase Tiering)
    
    * ✅ **Free Tier**: 100 requisições/hora (Acesso a 4 Círculos)
    * 🚀 **Pro Tier**: 1.000 requisições/hora (Filtros Avançados + Sinais Fracos)
    * 💎 **Enterprise**: Ilimitado (Custom Training + White Label)
    
    ## 🗄️ Infraestrutura V9.0
    * **Cloud-Native**: Migrado de DuckDB (Local) para **Supabase DB** (Global)
    * **Hybrid Intelligence**: Dados persistidos em tempo real para aprendizado contínuo.
    """,
    version="9.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",          # Next.js dev
        "http://localhost:3001",          # Next.js dev (Porta Ativa)
        "https://culturepulse.com.br",    # Produção
        "https://*.culturepulse.com.br",  # Subdomínios
        "https://*.vercel.app",           # Preview deploys Vercel
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Middleware de segurança
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "culturepulse.com.br", "*.culturepulse.com.br"]
)

# Middleware de rate limiting
if rate_limit_middleware:
    app.middleware("http")(rate_limit_middleware)

# Middleware de cache Redis
if add_cache_middleware:
    cache_middleware_instance = add_cache_middleware(app)

# Registrar routers (apenas os que foram carregados com sucesso)
if analysis_router:
    app.include_router(
        analysis_router,
        prefix="/api/v8/analysis",
        tags=["Análise Cultural"],
        dependencies=[Depends(get_current_client)] if get_current_client else []
    )

if circles_router:
    app.include_router(
        circles_router,
        prefix="/api/v8/circles",
        tags=["Círculos Culturais"],
        dependencies=[Depends(get_current_client)] if get_current_client else []
    )

if tfidf_router:
    app.include_router(
        tfidf_router,
        prefix="/api/v8/tfidf",
        tags=["TF-IDF Cultural"],
        dependencies=[Depends(get_current_client)] if get_current_client else []
    )

if alma_router:
    app.include_router(
        alma_router,
        prefix="/api/v8/alma",
        tags=["Alma Brasileira"],
        dependencies=[Depends(get_current_client)] if get_current_client else []
    )

if collection_router:
    app.include_router(
        collection_router,
        prefix="/api/v8",
        tags=["Coleta de Dados"],
        dependencies=[Depends(get_current_client)] if get_current_client else []
    )

if health_router:
    app.include_router(
        health_router,
        prefix="/api/v8/health",
        tags=["Health Check"]
    )

# Router de gerenciamento de cache
if cache_router:
    app.include_router(
        cache_router,
        dependencies=[Depends(get_current_client)] if get_current_client else []
    )

# Router de Machine Learning
if ml_router:
    app.include_router(
        ml_router,
        dependencies=[Depends(get_current_client)] if get_current_client else []
    )

# Router de Configuration Plans (V9.9)
if config_plans_router:
    app.include_router(
        config_plans_router,
        dependencies=[Depends(get_current_client)] if get_current_client else []
    )
elif get_current_client:
    @app.get("/plans/my-plan", tags=["Configuration"])
    async def fallback_get_user_plan_details(current_client = Depends(get_current_client)):
        plan_details = PLAN_CONFIG.get(current_client.tier, PLAN_CONFIG.get("free", {})) if PLAN_CONFIG else {}
        return {
            "tier": current_client.tier,
            "details": plan_details,
            "user": {
                "id": current_client.id,
                "name": current_client.name,
                "email": current_client.email,
                "onboarding": current_client.onboarding,
            }
        }

# Router de Advanced Analytics (V9.1 rescue)
if advanced_router:
    app.include_router(
        advanced_router,
        dependencies=[Depends(get_current_client)] if get_current_client else []
    )

# Router de Sistema de Alertas
if alerts_router:
    app.include_router(
        alerts_router,
        dependencies=[Depends(get_current_client)] if get_current_client else []
    )

# Router de Feedback Learning (INT-1 — FASE 2)
if feedback_router:
    app.include_router(
        feedback_router,
        dependencies=[Depends(get_current_client)] if get_current_client else []
    )

# Router de Topic Modelling (INT-2 — FASE 2)
if topics_router:
    app.include_router(
        topics_router,
        dependencies=[Depends(get_current_client)] if get_current_client else []
    )

# Router de PEST Classification (F-5 — FASE 2)
if pest_router:
    app.include_router(
        pest_router,
        dependencies=[Depends(get_current_client)] if get_current_client else []
    )

# Router de Dashboard Insights (H-5678 — FASE 2)
if dashboard_insights_router:
    app.include_router(
        dashboard_insights_router,
        dependencies=[Depends(get_current_client)] if get_current_client else []
    )

# Router de Emerging Profiles (MVP de perfis emergentes)
if emerging_profiles_router:
    app.include_router(
        emerging_profiles_router,
        dependencies=[Depends(get_current_client)] if get_current_client else []
    )

@app.get('/__debug__/runtime')
async def __debug_runtime():
    import os, sys
    import api
    return {
        'main_file': api.main.__file__,
        'cwd': os.getcwd(),
        'sys_path': sys.path[:10],
        'ml_router_defined': ml_router is not None,
        'ml_router_prefix': getattr(ml_router, 'prefix', None)
    }

# Router de Cultural Intelligence (H-9 — FASE 3)
if intelligence_router:
    app.include_router(
        intelligence_router,
        dependencies=[Depends(get_current_client)] if get_current_client else []
    )

# Router de Cluster Labels (F-4 — FASE 3)
if cluster_labels_router:
    app.include_router(
        cluster_labels_router,
        dependencies=[Depends(get_current_client)] if get_current_client else []
    )

# Router de Risk Assessment & Retrain (F-6/F-7 — FASE 3)
if risk_router:
    app.include_router(
        risk_router,
        dependencies=[Depends(get_current_client)] if get_current_client else []
    )

# Router de Pipeline Management + Engine Gaps (FASE 4 prep)
if pipeline_router:
    app.include_router(
        pipeline_router,
        dependencies=[Depends(get_current_client)] if get_current_client else []
    )

# Router de Signal Detail + Compare (F-8/F-12 — FASE 4)
if signals_router:
    app.include_router(
        signals_router,
        dependencies=[Depends(get_current_client)] if get_current_client else []
    )

# Router de Network Graph (F-9 — FASE 4)
if graph_network_router:
    app.include_router(
        graph_network_router,
        dependencies=[Depends(get_current_client)] if get_current_client else []
    )

# Router de Active Learning (F-10 — FASE 5)
if active_learning_router:
    app.include_router(
        active_learning_router,
        dependencies=[Depends(get_current_client)] if get_current_client else []
    )

# Router de Recall Histórico (F-11 — FASE 5)
if recall_router:
    app.include_router(
        recall_router,
        dependencies=[Depends(get_current_client)] if get_current_client else []
    )

# Router de Industry Weights (F-13 — FASE 5)
if industry_router:
    app.include_router(
        industry_router,
        dependencies=[Depends(get_current_client)] if get_current_client else []
    )

# Router de Cross-Impact Matrix (F-14 — FASE 5)
if cross_impact_router:
    app.include_router(
        cross_impact_router,
        dependencies=[Depends(get_current_client)] if get_current_client else []
    )

# Router de Stability × Risk Integration (Caminhos 1+2+3)
if stability_risk_router:
    app.include_router(
        stability_risk_router,
        dependencies=[Depends(get_current_client)] if get_current_client else []
    )

# Router de Business Exploration (4 Pillars — V9.1)
if explore_router:
    app.include_router(
        explore_router,
        dependencies=[Depends(get_current_client)] if get_current_client else []
    )

# Router de WhatsApp (SEM autenticação - webhook público)
if whatsapp_router:
    app.include_router(
        whatsapp_router,
        tags=["WhatsApp"]
    )

# Router de Streaming WebSocket (V9.0 — sem auth no Depends, auth via query param token)
if streaming_router:
    app.include_router(streaming_router)

# Endpoint raiz
@app.get("/", tags=["Root"])
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "🧠 Culture Pulse V9.0 API",
        "version": "9.0.0",
        "status": "operational",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/v8/health"
    }

# Endpoint de informações da API
@app.get("/api/v8/info", tags=["Informações"])
async def api_info():
    """Informações detalhadas da API"""
    global cultural_engine
    
    if not cultural_engine:
        raise HTTPException(status_code=503, detail="Cultural Engine não inicializado")
    
    metrics = cultural_engine.get_performance_metrics()
    
    return {
        "api": {
            "name": "Culture Pulse V9.0",
            "version": "9.0.0",
            "description": "API de Análise Cultural Brasileira V9.0",
            "uptime": time.time()
        },
        "engine": {
            "status": metrics.get("engine_status", "unknown"),
            "total_analyses": metrics.get("total_analyses", 0),
            "cache_size": metrics.get("cache_size", 0),
            "avg_processing_time": f"{metrics.get('avg_processing_time', 0):.3f}s"
        },
        "endpoints": {
            "analysis": "/api/v8/analysis/brand",
            "circles": "/api/v8/circles/analyze",
            "tfidf": "/api/v8/tfidf/analyze",
            "alma": "/api/v8/alma/analyze",
            "health": "/api/v8/health"
        }
    }

# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request, call_next):
    """Log de todas as requisições"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Função para obter instância do engine
def get_cultural_engine():
    """Dependency injection para o cultural engine"""
    global cultural_engine
    if not cultural_engine:
        raise HTTPException(status_code=503, detail="Cultural Engine não disponível")
    return cultural_engine

# Para execução direta
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
