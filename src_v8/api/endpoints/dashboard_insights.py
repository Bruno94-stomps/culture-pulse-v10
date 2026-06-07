"""
api/endpoints/dashboard_insights.py — H-5678 FASE 2
=====================================================
REST endpoints that expose the 4 dashboard data-bridge datasets
(weak signals, emerging trends, emerging profiles, cultural relationships)
derived from real enriched pipeline data.

The Next.js frontend consumes these endpoints instead of legacy UI drivers.

Routes:
  GET /api/v8/dashboard/insights          — all 4 datasets in one call
  GET /api/v8/dashboard/weak-signals      — weak signals only
  GET /api/v8/dashboard/trends            — emerging trends only
  GET /api/v8/dashboard/profiles          — emerging profiles only
  GET /api/v8/dashboard/relationships     — cultural relationships only
"""
from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v8/dashboard", tags=["Dashboard Insights"])


# ── Response models ──────────────────────────────────────────────────────

class WeakSignalItem(BaseModel):
    title: str
    description: str
    strength: float
    source: str
    actionable: bool
    action: str


class TrendItem(BaseModel):
    name: str
    category: str
    description: str
    momentum: float
    growth: str


class ProfileItem(BaseModel):
    name: str
    description: str
    demographics: str
    behaviors: str
    relevance: int
    growth: str
    size: str
    opportunity: str
    warnings: str
    connected_circles: List[str]


class RelationshipItem(BaseModel):
    circle_1: str
    circle_2: str
    strength: float
    type: str
    description: str
    opportunity: str
    risk: Optional[str]


class DashboardInsightsResponse(BaseModel):
    status: str
    weak_signals: List[dict]
    emerging_trends: List[dict]
    emerging_profiles: List[dict]
    cultural_relationships: List[dict]
    metadata: dict


class DatasetResponse(BaseModel):
    status: str
    data: List[dict]
    count: int


# ── Helper: load enriched signals ───────────────────────────────────────

def _load_enriched(
    plan: str,
    count: int,
    use_realtime: bool = False,
    project_id: Optional[str] = None,
    context_text: Optional[str] = None,
) -> list:
    """Load enriched signals from the reader or trigger realtime collection."""
    try:
        context = {
            "project_id": project_id,
            "user_tier": plan,
        }
        if context_text and context_text.strip():
            context["keywords"] = [context_text.strip()]

        if use_realtime:
            # Trigger Real-time Analysis via CulturalEngine and project context
            from collectors.orchestrator import CulturalDataOrchestrator
            orch = CulturalDataOrchestrator()

            # Puxar dados das APIs sem rodar o engine completo (que re-inicializaria tudo)
            import asyncio
            try:
                def run_async(coro):
                    try:
                        return asyncio.run(coro)
                    except RuntimeError:
                        import nest_asyncio
                        nest_asyncio.apply()
                        return asyncio.get_event_loop().run_until_complete(coro)

                search_term = context_text.strip() if context_text and context_text.strip() else "cultura brasileira"
                raw_signals = run_async(
                    orch.collect_comprehensive_data(
                        termo=search_term,
                        context=context,
                    )
                )

                formatted = []
                if isinstance(raw_signals, dict):
                    for signal in raw_signals.values():
                        if hasattr(signal, "to_dict"):
                            formatted.append(signal.to_dict())
                elif isinstance(raw_signals, list):
                    for signal in raw_signals:
                        if hasattr(signal, "to_dict"):
                            formatted.append(signal.to_dict())
                        elif isinstance(signal, dict):
                            formatted.append(signal)
                return formatted
            except Exception as e:
                logger.error(f"Realtime collection diagnostic error: {e}")
                return []

        from core.intelligence.enriched_reader import get_enriched_signals
        return get_enriched_signals(plan=plan, count=count, context=context, use_realtime_api=False)
    except Exception as exc:
        logger.warning("Could not load enriched signals: %s", exc)
        return []


# ── Endpoints ────────────────────────────────────────────────────────────

@router.get("/insights", response_model=DashboardInsightsResponse)
async def dashboard_insights(
    plan: str = Query("free", description="Tier: free, pro, executive, enterprise"),
    count: int = Query(50, ge=1, le=500, description="Max enriched signals to process"),
    realtime: bool = Query(True, description="Se true (Padrão V9.7), faz busca direta nas APIs"),
    intent: str = Query("research", description="Contexto: research (Pesquisa) ou campaign (Lançamento)"),
    context_text: Optional[str] = Query(None, description="Manual context string from onboarding"),
    project_id: Optional[str] = Query(None, description="ID do projeto para filtrar sinais relacionados"),
):
    """
    Return all 4 dashboard insight datasets in a single call.
    MODO V9.7: Prioriza REALTIME (API Direta) para eliminar dados artificiais da Demo.
    """
    try:
        from core.intelligence.dashboard_data_bridge import get_dashboard_data
        from core.intelligence.business_synthesizer import get_business_synthesizer, BusinessContext

        # 1. Configurar Contexto de Negócio baseado no Intent e Context Text do Usuário
        synthesizer = get_business_synthesizer()
        
        if intent == "campaign":
            scenario = "Lançamento de Produto"
            objective = "validar autenticidade e fit de campanha"
        else:
            scenario = "Pesquisa de Mercado"
            objective = "mapear sinais fracos e oportunidades culturais"

        # V9.8: Contexto Manual (User Prompt) enriquece o objetivo de negócio
        if context_text and len(context_text.strip()) > 3:
            objective = f"{objective} | Contexto Usuário: {context_text}"

        context = BusinessContext(
            scenario_type=scenario,
            target_audience="público geral brasileiro",
            business_objective=objective,
            opportunities_sought=["conexão genuína", "autenticidade"]
        )

        # V9.7 FORÇA REALTIME se for Demo para garantir dados reais das APIs
        if realtime:
            from collectors.orchestrator import OrchestratorV9 as CulturalDataOrchestrator
            orch = CulturalDataOrchestrator()
            
            # V9.8: A busca agora prioriza o contexto manual do usuário ("Gold Insights")
            search_term = context_text if (context_text and len(context_text.strip()) > 2) else "cultura brasileira"
            raw_signals_result = await orch.orchestrator_classic.collect_comprehensive_data(
                termo=search_term,
                context={"project_id": project_id, "user_tier": plan},
            )
            
            signals_raw = []
            if isinstance(raw_signals_result, dict):
                signals_raw = list(raw_signals_result.values())
            elif isinstance(raw_signals_result, list):
                signals_raw = raw_signals_result
        else:
            from core.intelligence.enriched_reader import get_enriched_signals
            signals_raw = get_enriched_signals(plan=plan, count=count, context={"project_id": project_id, "user_tier": plan})

        # 2. Processamento Inteligente: Conversão e Enriquecimento
        signals_to_analyze = []
        for s in signals_raw:
            if hasattr(s, 'to_dict'):
                signals_to_analyze.append(s.to_dict())
            elif isinstance(s, dict):
                signals_to_analyze.append(s)

        # Aplicar análise de profundidade e rótulos visuais (WEAK SIGNAL, EXPLOSÃO, etc)
        enriched_analysis = synthesizer.analyze_cultural_signals(signals_to_analyze, context)

        # 3. Gerar datasets para o dashboard via Data Bridge
        data = get_dashboard_data(signals=enriched_analysis)

        return DashboardInsightsResponse(
            status="success",
            weak_signals=data["weak_signals"],
            emerging_trends=data["emerging_trends"],
            emerging_profiles=data["emerging_profiles"],
            cultural_relationships=data["cultural_relationships"],
            metadata={
                "project_id": project_id,
                "enriched_signals_count": len(signals_raw),
                "plan": plan,
                "intent_mode": intent,
                "has_real_data": len(signals_raw) > 0,
                "mode": "realtime" if realtime else "cached"
            },
        )

    except Exception as exc:
        logger.error("GET /dashboard/insights error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/weak-signals", response_model=DatasetResponse)
async def weak_signals(
    plan: str = Query("free"),
    count: int = Query(50, ge=1, le=500),
    project_id: Optional[str] = Query(None, description="ID do projeto para filtrar sinais relacionados"),
    top_n: int = Query(8, ge=1, le=50, description="Max results"),
):
    """Return weak signals derived from enriched pipeline data."""
    try:
        from core.intelligence.dashboard_data_bridge import derive_weak_signals

        signals = _load_enriched(plan, count, project_id=project_id)
        result = derive_weak_signals(signals, top_n=top_n)
        return DatasetResponse(status="success", data=result, count=len(result))

    except Exception as exc:
        logger.error("GET /dashboard/weak-signals error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/trends", response_model=DatasetResponse)
async def emerging_trends(
    plan: str = Query("free"),
    count: int = Query(50, ge=1, le=500),
    project_id: Optional[str] = Query(None, description="ID do projeto para filtrar sinais relacionados"),
    top_n: int = Query(10, ge=1, le=50),
):
    """Return emerging trends derived from enriched pipeline data."""
    try:
        from core.intelligence.dashboard_data_bridge import derive_emerging_trends

        signals = _load_enriched(plan, count, project_id=project_id)
        result = derive_emerging_trends(signals, top_n=top_n)
        return DatasetResponse(status="success", data=result, count=len(result))

    except Exception as exc:
        logger.error("GET /dashboard/trends error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/profiles", response_model=DatasetResponse)
async def emerging_profiles(
    plan: str = Query("free"),
    count: int = Query(50, ge=1, le=500),
    project_id: Optional[str] = Query(None, description="ID do projeto para filtrar sinais relacionados"),
    top_n: int = Query(6, ge=1, le=50),
):
    """Return emerging consumer profiles derived from enriched pipeline data."""
    try:
        from core.intelligence.dashboard_data_bridge import derive_emerging_profiles

        signals = _load_enriched(plan, count, project_id=project_id)
        result = derive_emerging_profiles(signals, top_n=top_n)
        return DatasetResponse(status="success", data=result, count=len(result))

    except Exception as exc:
        logger.error("GET /dashboard/profiles error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/relationships", response_model=DatasetResponse)
async def cultural_relationships(
    plan: str = Query("free"),
    count: int = Query(50, ge=1, le=500),
    project_id: Optional[str] = Query(None, description="ID do projeto para filtrar sinais relacionados"),
    top_n: int = Query(8, ge=1, le=50),
):
    """Return cultural circle relationships derived from enriched pipeline data."""
    try:
        from core.intelligence.dashboard_data_bridge import derive_cultural_relationships

        signals = _load_enriched(plan, count, project_id=project_id)
        result = derive_cultural_relationships(signals, top_n=top_n)
        return DatasetResponse(status="success", data=result, count=len(result))

    except Exception as exc:
        logger.error("GET /dashboard/relationships error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
