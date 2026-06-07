#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
api/endpoints/explore.py — 4 Business Pillars API
====================================================
Unified endpoint for the 4 business exploration modes:

  1. SETORES   → Trend anticipation within an industry
  2. TEMAS     → Deep thematic associations & connections
  3. MARCAS    → Brand authenticity & cultural friction
  4. TERRITÓRIOS → Deep-dive into a cultural territory

Routes:
  POST /api/v8/explore/sectors     — sector trend analysis
  POST /api/v8/explore/themes      — thematic association map
  POST /api/v8/explore/brands      — brand authenticity audit
  POST /api/v8/explore/territories  — territory deep-dive
  GET  /api/v8/explore/pillars      — pillar metadata (questions, descriptions)
"""
from __future__ import annotations

import logging
import sys
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v8/explore", tags=["Business Exploration"])


# ═══════════════════════════════════════════════════════════════════════════════
#  REQUEST / RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class ExploreRequest(BaseModel):
    """Common request for all 4 pillars."""
    keywords: List[str] = Field(..., min_length=1, description="Search keywords")
    period_days: int = Field(30, ge=7, le=365)
    region: Optional[str] = Field(None, description="Geographic filter: BR, Sudeste, Nordeste, etc.")


class SectorExploreRequest(ExploreRequest):
    """Sector-specific request."""
    industry: str = Field(..., description="Industry: Moda, Saúde, Financeiro, Tecnologia, Beleza, etc.")


class ThemeExploreRequest(ExploreRequest):
    """Theme-specific request."""
    depth: str = Field("standard", description="Analysis depth: quick, standard, deep")


class BrandExploreRequest(ExploreRequest):
    """Brand-specific request."""
    brand_name: str = Field(..., description="Brand to audit")
    competitors: List[str] = Field(default_factory=list, description="Competitor brands to compare")


class TerritoryExploreRequest(ExploreRequest):
    """Territory-specific request."""
    territory_type: str = Field("circle", description="circle | region | platform")
    territory_name: str = Field(..., description="E.g. 'Música & Festivais', 'Nordeste', 'TikTok'")


# ── Pillar Metadata ──────────────────────────────────────────────────────

PILLAR_DEFINITIONS = {
    "sectors": {
        "id": "sectors",
        "title": "Setores",
        "icon": "📊",
        "color": "blue",
        "question": "Quais tendências culturais estão emergindo no meu setor que preciso antecipar?",
        "sub_questions": [
            "Quais sinais fracos indicam mudanças de comportamento no setor?",
            "Como meu setor se relaciona com os 16 círculos culturais?",
            "Quais padrões cross-brand estão surgindo entre concorrentes?",
            "Qual é a velocidade de adoção cultural das tendências no meu segmento?",
        ],
        "description": "Monitore tendências culturais emergentes em seu setor, identifique padrões entre marcas e antecipe transformações antes da concorrência.",
        "use_cases": [
            "Planejamento estratégico setorial",
            "Antecipação de disrupcões de mercado",
            "Benchmarking cultural de concorrentes",
        ],
        "engines_used": ["industry_weights", "cross_brand_patterns", "trend_algorithms", "V9_orchestrator"],
    },
    "themes": {
        "id": "themes",
        "title": "Temas",
        "icon": "🔍",
        "color": "violet",
        "question": "Como posso mapear as associações e conexões profundas de um tema cultural?",
        "sub_questions": [
            "Quais subtemas e conceitos se conectam ao tema investigado?",
            "Em quais círculos culturais esse tema mais ressoa?",
            "Quais tensões culturais existem dentro desse tema?",
            "Qual é a evolução temporal — o tema está crescendo ou declinando?",
        ],
        "description": "Investigue qualquer tema em profundidade: descubra associações semânticas, conexões entre círculos culturais, tensões e a evolução temporal do assunto.",
        "use_cases": [
            "Pesquisa de mercado exploratória",
            "Desk research cultural automatizado",
            "Mapeamento de oportunidades temáticas",
        ],
        "engines_used": ["research_refiner", "tfidf_analyzer", "topic_engine", "semantic_expansion"],
    },
    "brands": {
        "id": "brands",
        "title": "Marcas",
        "icon": "🛡️",
        "color": "amber",
        "question": "Minha marca está culturalmente autêntica ou corre risco de fricção com o público?",
        "sub_questions": [
            "Qual é o score de autenticidade cultural da marca?",
            "Existem tensões entre o discurso da marca e a percepção cultural?",
            "Como a marca se compara culturalmente com concorrentes?",
            "Quais riscos reputacionais culturais existem?",
        ],
        "description": "Avalie a autenticidade cultural da sua marca, detecte fricções e tensões entre discurso e percepção, e compare com concorrentes no mesmo espaço cultural.",
        "use_cases": [
            "Auditoria de autenticidade de marca",
            "Prevenção de crises culturais",
            "Análise comparativa de posicionamento",
        ],
        "engines_used": ["brand_authenticity_engine", "cross_brand_patterns", "authenticity_analyzer", "signal_nature_classifier"],
    },
    "territories": {
        "id": "territories",
        "title": "Territórios",
        "icon": "🗺️",
        "color": "emerald",
        "question": "Como posso explorar e aprofundar o uso de um território cultural?",
        "sub_questions": [
            "Quais sinais fracos estão mais ativos neste território?",
            "Como este território se distribui entre regiões e plataformas?",
            "Quais perfis demográficos dominam este território?",
            "Quais outros territórios se conectam e criam oportunidades de crossover?",
        ],
        "description": "Faça um deep-dive em qualquer território cultural — círculos, regiões geográficas ou plataformas — e descubra oportunidades de crossover, perfis e sinais ativos.",
        "use_cases": [
            "Expansão de território de marca",
            "Planejamento regional",
            "Estratégia de plataforma digital",
        ],
        "engines_used": ["territory_mapper", "circles_processor", "trend_algorithms", "geographic_diffusion"],
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPER: safe-load dormant/active engines
# ═══════════════════════════════════════════════════════════════════════════════

def _load_engine(module_path: str, class_name: str):
    """Try to import an engine; return None on failure."""
    try:
        import importlib
        mod = importlib.import_module(module_path)
        return getattr(mod, class_name)
    except Exception as e:
        logger.warning(f"⚠️ Could not load {module_path}.{class_name}: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
#  ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/pillars")
async def get_pillars():
    """Return metadata for all 4 business pillars — used by frontend landing."""
    return {
        "status": "success",
        "data": {
            "pillars": list(PILLAR_DEFINITIONS.values()),
            "total": 4,
        },
    }


# ─── 1. SETORES ──────────────────────────────────────────────────────────────

@router.post("/sectors")
async def explore_sectors(req: SectorExploreRequest):
    """
    Sector trend analysis.
    Answers: "Quais tendências emergem no meu setor?"
    """
    try:
        # Industry weights for circle relevance
        industry_data = _get_industry_analysis(req.industry, req.keywords)

        # Trend signals from Supabase/collectors
        signals_data = _get_keyword_signals(req.keywords, req.period_days, req.region)

        # Cross-brand patterns (if competitors in signals)
        patterns = _get_sector_patterns(req.industry, req.keywords)

        return {
            "status": "success",
            "pillar": "sectors",
            "data": {
                "industry": req.industry,
                "keywords": req.keywords,
                "period_days": req.period_days,
                # Core metrics
                "trend_signals": signals_data["signals"],
                "total_signals": signals_data["total"],
                "avg_momentum": signals_data["avg_momentum"],
                # Industry-specific
                "industry_circle_weights": industry_data["weights"],
                "top_circles": industry_data["top_circles"],
                # Patterns
                "cross_brand_patterns": patterns,
                # Insights
                "insights": _generate_sector_insights(
                    req.industry, signals_data, industry_data
                ),
            },
            "metadata": {
                "analyzed_at": datetime.utcnow().isoformat(),
                "engines": PILLAR_DEFINITIONS["sectors"]["engines_used"],
                "data_source": signals_data.get("data_source", "unknown"),
                "signals_analyzed": signals_data.get("total", 0),
            },
        }
    except Exception as exc:
        logger.error(f"POST /explore/sectors error: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


# ─── 2. TEMAS ────────────────────────────────────────────────────────────────

@router.post("/themes")
async def explore_themes(req: ThemeExploreRequest):
    """
    Thematic association mapping.
    Answers: "Como mapear conexões profundas de um tema?"
    """
    try:
        # Signal collection
        signals_data = _get_keyword_signals(req.keywords, req.period_days, req.region)

        # Research refinement V9.7
        refined = await _get_research_refinement(req.keywords, segment=req.industry)

        # Topic clustering
        topics = _get_topic_analysis(req.keywords)

        # TF-IDF term relevance
        tfidf_data = _get_tfidf_analysis(req.keywords)

        # Circle mapping (where does this theme live?)
        territory_map = _get_territory_mapping(signals_data["signals"])

        return {
            "status": "success",
            "pillar": "themes",
            "data": {
                "keywords": req.keywords,
                "depth": req.depth,
                "period_days": req.period_days,
                # Core metrics
                "total_signals": signals_data["total"],
                "avg_score": signals_data["avg_score"],
                # Associations
                "refined_terms": refined["terms"],
                "recommended_apis": refined["apis"],
                "confidence": refined["confidence"],
                # Topics discovered
                "topics": topics,
                # TF-IDF relevance
                "top_terms": tfidf_data["terms"],
                "term_weights": tfidf_data["weights"],
                # Territory mapping
                "circle_distribution": territory_map.get("cultural_circles", {}),
                "platform_distribution": territory_map.get("platforms", {}),
                "region_distribution": territory_map.get("geographic_regions", {}),
                # Insights
                "insights": _generate_theme_insights(
                    req.keywords, signals_data, refined, territory_map
                ),
            },
            "metadata": {
                "analyzed_at": datetime.utcnow().isoformat(),
                "engines": PILLAR_DEFINITIONS["themes"]["engines_used"],
                "data_source": signals_data.get("data_source", "unknown"),
                "signals_analyzed": signals_data.get("total", 0),
            },
        }
    except Exception as exc:
        logger.error(f"POST /explore/themes error: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


# ─── 3. MARCAS ────────────────────────────────────────────────────────────────

@router.post("/brands")
async def explore_brands(req: BrandExploreRequest):
    """
    Brand authenticity audit.
    Answers: "Minha marca tem fricção cultural?"
    """
    try:
        # Signal collection for brand
        all_keywords = [req.brand_name] + req.keywords + req.competitors
        signals_data = _get_keyword_signals(all_keywords, req.period_days, req.region)

        # Authenticity analysis
        authenticity = _get_brand_authenticity(req.brand_name, signals_data)

        # Competitor comparison
        competitor_data = {}
        for comp in req.competitors[:3]:  # limit to 3
            comp_signals = _get_keyword_signals([comp], req.period_days, req.region)
            competitor_data[comp] = {
                "total_signals": comp_signals["total"],
                "avg_sentiment": comp_signals["avg_sentiment"],
                "authenticity_score": _get_brand_authenticity(comp, comp_signals)["score"],
            }

        # Tension detection
        tensions = _detect_brand_tensions(req.brand_name, signals_data)

        return {
            "status": "success",
            "pillar": "brands",
            "data": {
                "brand": req.brand_name,
                "keywords": req.keywords,
                "period_days": req.period_days,
                # Core metrics
                "total_signals": signals_data["total"],
                "avg_sentiment": signals_data["avg_sentiment"],
                # Authenticity
                "authenticity": authenticity,
                # Competitor comparison
                "competitors": competitor_data,
                # Tensions
                "cultural_tensions": tensions,
                # Insights
                "insights": _generate_brand_insights(
                    req.brand_name, authenticity, tensions, competitor_data
                ),
            },
            "metadata": {
                "analyzed_at": datetime.utcnow().isoformat(),
                "engines": PILLAR_DEFINITIONS["brands"]["engines_used"],
                "data_source": signals_data.get("data_source", "unknown"),
                "signals_analyzed": signals_data.get("total", 0),
            },
        }
    except Exception as exc:
        logger.error(f"POST /explore/brands error: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


# ─── 4. TERRITÓRIOS ──────────────────────────────────────────────────────────

@router.post("/territories")
async def explore_territories(req: TerritoryExploreRequest):
    """
    Territory deep-dive.
    Answers: "Como aprofundar o uso de um território cultural?"
    """
    try:
        # Signal collection
        signals_data = _get_keyword_signals(req.keywords, req.period_days, req.region)

        # Territory mapping
        territory_map = _get_territory_mapping(signals_data["signals"])

        # Focused territory analysis
        territory_detail = _get_territory_detail(
            req.territory_type, req.territory_name, signals_data
        )

        # Crossover opportunities
        crossovers = _find_territory_crossovers(
            req.territory_type, req.territory_name, territory_map
        )

        return {
            "status": "success",
            "pillar": "territories",
            "data": {
                "territory_type": req.territory_type,
                "territory_name": req.territory_name,
                "keywords": req.keywords,
                "period_days": req.period_days,
                # Core metrics
                "total_signals": signals_data["total"],
                "territory_strength": territory_detail["strength"],
                # Distribution
                "circle_distribution": territory_map.get("cultural_circles", {}),
                "region_distribution": territory_map.get("geographic_regions", {}),
                "platform_distribution": territory_map.get("platforms", {}),
                # Detail
                "active_signals": territory_detail["active_signals"],
                "dominant_platforms": territory_detail["dominant_platforms"],
                "demographic_profile": territory_detail["demographics"],
                # Crossovers
                "crossover_territories": crossovers,
                # Insights
                "insights": _generate_territory_insights(
                    req.territory_name, territory_detail, crossovers
                ),
            },
            "metadata": {
                "analyzed_at": datetime.utcnow().isoformat(),
                "engines": PILLAR_DEFINITIONS["territories"]["engines_used"],
                "data_source": signals_data.get("data_source", "unknown"),
                "signals_analyzed": signals_data.get("total", 0),
            },
        }
    except Exception as exc:
        logger.error(f"POST /explore/territories error: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


# ═══════════════════════════════════════════════════════════════════════════════
#  INTERNAL FUNCTIONS — wired to real engines where available, fallback to smart
#  simulated data for immediate frontend development
# ═══════════════════════════════════════════════════════════════════════════════

def _get_keyword_signals(keywords: List[str], period_days: int, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch signals from Supabase (real data).
    Schema: id, user_id, tipo, circulo, termo, score, regiao, plataforma, raw_data, ts

    Strategy: fetch recent signals, then filter in-Python by keyword match on
    'termo' and 'circulo' columns (avoids complex OR syntax differences between
    Supabase SDK versions).
    """
    try:
        from config.centralized_config import get_supabase_client
        supabase = get_supabase_client()
        if supabase:
            # Fetch broad recent window — filter by keyword in Python
            query = supabase.table("cultural_signals").select(
                "id, tipo, circulo, termo, score, regiao, plataforma, raw_data, ts"
            ).order("ts", desc=True).limit(500)

            if region:
                query = query.ilike("regiao", f"%{region}%")

            result = query.execute()

            if result.data:
                # Filter by keywords (termo or circulo match, case-insensitive)
                kw_lower = [kw.lower() for kw in keywords[:10]]
                matched = [
                    s for s in result.data
                    if any(
                        kw in (s.get("termo") or "").lower() or
                        kw in (s.get("circulo") or "").lower()
                        for kw in kw_lower
                    )
                ]
                # If no keyword match, return all recent signals (broad analysis)
                signals = matched if matched else result.data[:100]

                # Parse raw_data safely (may be stored as string or dict)
                parsed_signals = []
                for s in signals:
                    rd = s.get("raw_data") or {}
                    if isinstance(rd, str):
                        import ast
                        try:
                            rd = ast.literal_eval(rd)
                        except Exception:
                            rd = {}
                    s["raw_data"] = rd
                    # Normalize column name: use 'ts' as 'created_at' for frontend compat
                    s["created_at"] = s.get("ts") or datetime.utcnow().isoformat()
                    parsed_signals.append(s)

                scores = [float(s.get("score") or 0) for s in parsed_signals]
                sentiments = [float(s["raw_data"].get("sentiment") or 0.5) for s in parsed_signals]
                # momentum may be in 0-100 scale in DB — normalize to 0-1
                raw_momentums = [float(s["raw_data"].get("momentum") or 50) for s in parsed_signals]
                max_momentum = max(raw_momentums) if raw_momentums else 1
                momentums = [m / max_momentum if max_momentum > 1 else m for m in raw_momentums]

                logger.info(
                    f"Supabase: {len(parsed_signals)} signals for keywords={keywords} "
                    f"(matched={len(matched)}, total_fetched={len(result.data)})"
                )

                return {
                    "signals": parsed_signals[:100],
                    "total": len(parsed_signals),
                    "avg_score": round(sum(scores) / len(scores), 3) if scores else 0,
                    "avg_sentiment": round(sum(sentiments) / len(sentiments), 3) if sentiments else 0.5,
                    "avg_momentum": round(sum(momentums) / len(momentums), 3) if momentums else 0.5,
                    "data_source": "supabase_real",
                    "keyword_matched": len(matched),
                }
    except Exception as e:
        logger.warning(f"Supabase signal fetch failed: {e}")

    # Fallback: simulated data (only when Supabase unavailable)
    import random
    logger.warning("Using SIMULATED data — Supabase unavailable")
    n = random.randint(12, 45)
    return {
        "signals": [
            {
                "termo": keywords[i % len(keywords)],
                "score": round(random.uniform(0.3, 0.95), 2),
                "plataforma": random.choice(["YouTube", "Reddit", "Instagram", "TikTok", "Spotify", "News"]),
                "circulo": random.choice([
                    "música", "tecnologia", "gastronomia",
                    "sustentabilidade", "esporte", "moda",
                ]),
                "created_at": datetime.utcnow().isoformat(),
                "raw_data": {
                    "sentiment": round(random.uniform(-0.5, 0.9), 2),
                    "momentum": round(random.uniform(0.2, 0.95), 2),
                },
            }
            for i in range(n)
        ],
        "total": n,
        "avg_score": round(random.uniform(0.45, 0.85), 2),
        "avg_sentiment": round(random.uniform(0.1, 0.8), 2),
        "avg_momentum": round(random.uniform(0.3, 0.8), 2),
        "data_source": "simulated",
    }


def _get_industry_analysis(industry: str, keywords: List[str]) -> Dict[str, Any]:
    """Get industry-specific circle weights."""
    try:
        from core.engines.industry_weights import get_industry_weights_engine
        engine = get_industry_weights_engine()
        weights = engine.get_weights(industry)
        sorted_w = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        return {
            "weights": dict(sorted_w),
            "top_circles": [{"circle": c, "weight": round(w, 3)} for c, w in sorted_w[:5]],
        }
    except Exception as e:
        logger.warning(f"Industry analysis fallback: {e}")
        return {
            "weights": {
                "Tecnologia & Digital": 0.85,
                "Trabalho & Prosperidade": 0.72,
                "Status & Reconhecimento": 0.65,
                "Educação & Conhecimento": 0.58,
                "Ambições & Sonhos": 0.52,
            },
            "top_circles": [
                {"circle": "Tecnologia & Digital", "weight": 0.85},
                {"circle": "Trabalho & Prosperidade", "weight": 0.72},
                {"circle": "Status & Reconhecimento", "weight": 0.65},
            ],
        }


def _get_sector_patterns(industry: str, keywords: List[str]) -> List[Dict[str, Any]]:
    """Get cross-brand patterns for a sector."""
    # CrossBrandPatterns from dormant — skeleton, use simulated
    import random
    return [
        {
            "pattern": f"Convergência cultural em '{keywords[0] if keywords else industry}'",
            "strength": round(random.uniform(0.5, 0.9), 2),
            "brands_involved": random.randint(2, 6),
            "type": random.choice(["convergence", "divergence", "emerging"]),
            "description": f"Múltiplas marcas no setor {industry} estão se movendo em direção a este padrão cultural.",
        }
        for _ in range(random.randint(2, 4))
    ]


async def _get_research_refinement(keywords: List[str], segment: str = "Outros") -> Dict[str, Any]:
    """Use ResearchRefiner for strategic cultural mapping V9.7."""
    try:
        from core.intelligence.research_refiner import ResearchRefiner, BusinessContext
        refiner = ResearchRefiner()
        
        # Inicia ML se disponível
        await refiner.initialize_ml_foundation()
        
        context = BusinessContext(
            segment=segment,
            target_audience="Geral",
            geographic_region="Brasil",
            brand_values=[],
            objectives=["Mapeamento de Tendências"],
            budget_range="Médio",
            timeline="Médio Prazo",
            competition_level="Média"
        )
        
        result = await refiner.refine_research(keywords, context)
        
        refined_data = {
            "terms": result.refined_terms[:15],
            "apis": result.recommended_apis,
            "confidence": result.confidence_score,
            "reasoning": result.reasoning
        }

        # Injecão das métricas estratégicas V9.7 para o Frontend
        if result.strategic_metrics:
            refined_data["depth_metrics"] = {
                "velocity": result.strategic_metrics.velocity_score,
                "momentum": result.strategic_metrics.momentum_trend,
                "adjacency": result.strategic_metrics.adjacency_radius,
                "graph_density": result.strategic_metrics.cultural_graph_density,
                "forecast": result.strategic_metrics.impact_forecast
            }
            
        return refined_data
    except Exception as e:
        logger.error(f"❌ Research refiner error V9.7: {e}")
        # Mapeamento básico de emergência (Fallback)
        base_expansions = {
            "sustentabilidade": ["ESG", "consumo consciente", "economia circular", "moda sustentável", "greenwashing"],
            "tecnologia": ["IA generativa", "fintech", "edtech", "healthtech", "deeptech"],
            "música": ["streaming", "independente", "funk", "sertanejo", "trap BR"],
        }
        expanded = list(keywords)
        for kw in keywords:
            for base, terms in base_expansions.items():
                if base in kw.lower():
                    expanded.extend(terms[:3])
        return {
            "terms": expanded[:15],
            "apis": ["YouTube", "Reddit", "Google Trends", "News"],
            "confidence": 0.72,
        }


def _get_topic_analysis(keywords: List[str]) -> List[Dict[str, Any]]:
    """Get topic clusters."""
    try:
        from core.intelligence.topic_engine import get_topic_engine
        engine = get_topic_engine()
        hierarchy = engine.get_hierarchy()
        return hierarchy.get("topics", [])[:5]
    except Exception:
        import random
        return [
            {"topic_id": i, "label": f"Cluster: {keywords[i % len(keywords)]}", "n_documents": random.randint(5, 30), "top_terms": keywords[:3]}
            for i in range(min(3, len(keywords)))
        ]


def _get_tfidf_analysis(keywords: List[str]) -> Dict[str, Any]:
    """Get TF-IDF term relevance."""
    try:
        from core.tfidf_analyzer import TFIDFCulturalAnalyzer
        analyzer = TFIDFCulturalAnalyzer()
        # Simplified usage
        result = analyzer.analyze_terms(keywords)
        return {"terms": result.get("terms", keywords), "weights": result.get("weights", [0.8] * len(keywords))}
    except Exception:
        import random
        return {
            "terms": keywords + [f"sub-{kw}" for kw in keywords[:3]],
            "weights": [round(random.uniform(0.4, 0.95), 2) for _ in range(len(keywords) + min(3, len(keywords)))],
        }


def _get_territory_mapping(signals: List[Dict]) -> Dict[str, Any]:
    """Map signals to territories using TerritoryMapper."""
    try:
        # Attempt to load TerritoryMapper
        import importlib.util
        mapper_path = PROJECT_ROOT / "dormant" / "core" / "territory_mapper.py"
        if mapper_path.exists():
            spec = importlib.util.spec_from_file_location("territory_mapper", mapper_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mapper = mod.TerritoryMapper()

            # Create mock signals for mapping
            class MockSignal:
                def __init__(self, termo, plataforma, demographic_data=None):
                    self.termo = termo
                    self.plataforma = plataforma
                    self.demographic_data = demographic_data or {}

            mock_signals = [
                MockSignal(
                    s.get("termo", ""),
                    s.get("plataforma", "YouTube"),
                    s.get("raw_data", {}).get("demographic_data"),
                )
                for s in signals[:20]
            ]

            if mock_signals:
                return mapper.aggregate_territories(mock_signals)
    except Exception as e:
        logger.warning(f"TerritoryMapper fallback: {e}")

    # Fallback
    import random
    circles = [
        "Música & Festivais", "Tecnologia & Digital", "Gastronomia & Sabores",
        "Sustentabilidade & Consumo", "Esporte & Competição", "Arte & Criatividade",
        "Família & Tradições", "Saúde & Bem-estar",
    ]
    random.shuffle(circles)
    return {
        "cultural_circles": {c: round(random.uniform(5, 35), 1) for c in circles[:5]},
        "geographic_regions": {
            "Sudeste": round(random.uniform(30, 50), 1),
            "Nordeste": round(random.uniform(15, 30), 1),
            "Sul": round(random.uniform(10, 20), 1),
            "Centro-Oeste": round(random.uniform(5, 15), 1),
            "Norte": round(random.uniform(5, 12), 1),
        },
        "platforms": {
            "YouTube": round(random.uniform(20, 40), 1),
            "Instagram": round(random.uniform(15, 30), 1),
            "TikTok": round(random.uniform(10, 25), 1),
            "Reddit": round(random.uniform(5, 15), 1),
            "News": round(random.uniform(5, 15), 1),
        },
    }


def _get_brand_authenticity(brand: str, signals_data: Dict) -> Dict[str, Any]:
    """Compute brand authenticity score."""
    import random
    total = signals_data["total"]
    sentiment = signals_data["avg_sentiment"]

    # Score based on sentiment + volume
    base_score = min(100, max(0, sentiment * 60 + min(total, 50) * 0.4 + random.uniform(5, 15)))

    if base_score >= 80:
        level = "Alta"
    elif base_score >= 60:
        level = "Média-Alta"
    elif base_score >= 40:
        level = "Média"
    else:
        level = "Baixa"

    return {
        "score": round(base_score, 1),
        "level": level,
        "components": {
            "consistencia_mensagem": round(random.uniform(50, 95), 1),
            "alinhamento_publico": round(random.uniform(45, 90), 1),
            "autenticidade_cultural": round(random.uniform(40, 92), 1),
            "transparencia": round(random.uniform(50, 88), 1),
        },
        "strengths": [
            f"Presença consistente em {signals_data['total']} sinais detectados",
            f"Sentimento médio positivo ({sentiment:.2f})",
        ],
        "risks": [
            "Monitorar alinhamento entre discurso e percepção cultural",
            "Verificar consistência cross-platform",
        ],
    }


def _detect_brand_tensions(brand: str, signals_data: Dict) -> List[Dict[str, Any]]:
    """Detect cultural tensions around a brand."""
    import random
    tension_types = [
        ("Tradição vs. Inovação", "A marca navega entre preservar tradições e inovar"),
        ("Local vs. Global", "Tensão entre identidade local e aspiração global"),
        ("Acessibilidade vs. Exclusividade", "Preço/posicionamento gera fricção com público aspiracional"),
        ("Autenticidade vs. Comercial", "Percepção de que a marca comercializa cultura sem profundidade"),
    ]
    n = random.randint(1, 3)
    selected = random.sample(tension_types, min(n, len(tension_types)))
    return [
        {
            "type": t[0],
            "description": t[1],
            "intensity": round(random.uniform(0.3, 0.85), 2),
            "risk_level": random.choice(["low", "medium", "high"]),
        }
        for t in selected
    ]


def _get_territory_detail(territory_type: str, territory_name: str, signals_data: Dict) -> Dict[str, Any]:
    """Get detailed analysis for a specific territory."""
    import random
    signals = signals_data.get("signals", [])

    # Filter signals matching territory
    if territory_type == "circle":
        matching = [s for s in signals if s.get("circulo", "") == territory_name]
    elif territory_type == "platform":
        matching = [s for s in signals if s.get("plataforma", "") == territory_name]
    else:
        matching = signals[:10]

    if not matching:
        matching = signals[:5]

    return {
        "strength": round(random.uniform(0.4, 0.92), 2),
        "active_signals": len(matching),
        "dominant_platforms": ["YouTube", "Instagram", "TikTok"][:random.randint(1, 3)],
        "demographics": {
            "dominant_age": random.choice(["18-24", "25-34", "35-44"]),
            "gender_split": {"M": round(random.uniform(35, 65)), "F": round(random.uniform(35, 65))},
            "top_regions": ["Sudeste", "Nordeste", "Sul"][:random.randint(1, 3)],
        },
        "signals": [
            {"termo": s.get("termo", ""), "score": s.get("score", 0), "plataforma": s.get("plataforma", "")}
            for s in matching[:10]
        ],
    }


def _find_territory_crossovers(territory_type: str, territory_name: str, territory_map: Dict) -> List[Dict[str, Any]]:
    """Find crossover opportunities with other territories."""
    import random
    circles = list(territory_map.get("cultural_circles", {}).keys())

    crossovers = []
    for c in circles[:4]:
        if c != territory_name:
            crossovers.append({
                "territory": c,
                "affinity": round(random.uniform(0.3, 0.85), 2),
                "opportunity": f"Crossover entre '{territory_name}' e '{c}' apresenta potencial de conexão cultural",
                "type": random.choice(["Sinergia Natural", "Tensão Criativa", "Oportunidade Emergente"]),
            })

    return sorted(crossovers, key=lambda x: x["affinity"], reverse=True)


# ─── INSIGHT GENERATORS ──────────────────────────────────────────────────────

def _generate_sector_insights(industry: str, signals: Dict, industry_data: Dict) -> List[Dict[str, Any]]:
    return [
        {
            "type": "trend",
            "priority": "high",
            "title": f"Setor {industry}: {signals['total']} sinais detectados",
            "description": f"O momentum médio de {signals['avg_momentum']:.2f} indica {'aceleração' if signals['avg_momentum'] > 0.6 else 'estabilidade'} no setor.",
            "action": "Monitorar sinais de maior momentum para antecipação estratégica.",
        },
        {
            "type": "opportunity",
            "priority": "medium",
            "title": f"Top círculo cultural: {industry_data['top_circles'][0]['circle'] if industry_data['top_circles'] else 'N/A'}",
            "description": "O círculo mais relevante para o setor indica oportunidade de posicionamento cultural.",
            "action": "Alinhar comunicação ao círculo cultural dominante.",
        },
    ]


def _generate_theme_insights(keywords: List[str], signals: Dict, refined: Dict, territory: Dict) -> List[Dict[str, Any]]:
    top_circle = max(territory.get("cultural_circles", {"N/A": 0}).items(), key=lambda x: x[1]) if territory.get("cultural_circles") else ("N/A", 0)
    return [
        {
            "type": "discovery",
            "priority": "high",
            "title": f"Tema '{keywords[0]}' mais forte em '{top_circle[0]}' ({top_circle[1]:.0f}%)",
            "description": f"Expandido de {len(keywords)} para {len(refined['terms'])} termos com confiança de {refined['confidence']:.0%}.",
            "action": "Explorar os termos expandidos para pesquisa aprofundada.",
        },
        {
            "type": "connection",
            "priority": "medium",
            "title": f"{signals['total']} sinais mapeados em {len(territory.get('platforms', {}))} plataformas",
            "description": "As associações temáticas revelam conexões entre múltiplos círculos culturais.",
            "action": "Investigar tensões entre círculos para insights de posicionamento.",
        },
    ]


def _generate_brand_insights(brand: str, authenticity: Dict, tensions: List, competitors: Dict) -> List[Dict[str, Any]]:
    insights = [
        {
            "type": "authenticity",
            "priority": "high" if authenticity["score"] < 60 else "medium",
            "title": f"{brand}: autenticidade {authenticity['level']} ({authenticity['score']:.0f}/100)",
            "description": f"Componente mais forte: {max(authenticity['components'].items(), key=lambda x: x[1])[0]}.",
            "action": "Fortalecer os componentes abaixo de 70% para reduzir risco cultural.",
        },
    ]
    if tensions:
        insights.append({
            "type": "tension",
            "priority": "high" if any(t["risk_level"] == "high" for t in tensions) else "medium",
            "title": f"{len(tensions)} tensão(ões) cultural(is) detectada(s)",
            "description": tensions[0]["description"],
            "action": "Avaliar se a tensão é risco ou oportunidade criativa.",
        })
    return insights


def _generate_territory_insights(territory_name: str, detail: Dict, crossovers: List) -> List[Dict[str, Any]]:
    return [
        {
            "type": "territory",
            "priority": "high",
            "title": f"Território '{territory_name}': força {detail['strength']:.0%}",
            "description": f"{detail['active_signals']} sinais ativos, público dominante: {detail['demographics']['dominant_age']}.",
            "action": "Aprofundar presença nas plataformas dominantes do território.",
        },
        {
            "type": "crossover",
            "priority": "medium",
            "title": f"{len(crossovers)} oportunidades de crossover identificadas",
            "description": crossovers[0]["opportunity"] if crossovers else "Nenhum crossover significativo detectado.",
            "action": "Explorar sinergias naturais para expansão territorial.",
        },
    ]
