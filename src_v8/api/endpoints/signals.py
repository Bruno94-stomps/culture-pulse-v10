"""
api/endpoints/signals.py — FASE 4: F-8 Drill-Down + F-12 Comparative
=====================================================================
REST endpoints for the Next.js frontend:

F-8 Drill-Down:
  POST /api/v8/signals/detail    — Full enrichment detail for one signal
                                    (all 16 engines in one response)

F-12 Comparative:
  POST /api/v8/signals/compare   — Side-by-side comparison of 2+ signals
                                    across all dimensions
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v8/signals", tags=["Signal Detail & Compare"])


# ── Response models ──────────────────────────────────────────────────────

class GenericResponse(BaseModel):
    status: str = "success"
    data: Any = None
    metadata: Dict[str, Any] = {}


class SignalDetailRequest(BaseModel):
    """A raw or partially enriched signal for full drill-down."""
    signal: Dict[str, Any] = Field(..., description="Signal dict (must include 'termo')")


class CompareRequest(BaseModel):
    """Two or more signals to compare side-by-side."""
    signals: List[Dict[str, Any]] = Field(
        ..., min_length=2, max_length=10,
        description="List of signal dicts to compare (2-10)",
    )
    dimensions: Optional[List[str]] = Field(
        default=None,
        description="Specific dimensions to compare (None = all). Options: circles, sentiment, tension, nature, authenticity, velocity, graph, feedback, topics, pest, vulnerability, alerts, actions, scenarios, opportunities, momentum, risk",
    )


# ── Helpers ──────────────────────────────────────────────────────────────

def _run_all_engines(signal: dict) -> dict:
    """Run all 16 engines synchronously on a signal and return enriched dict."""
    enriched = {**signal}

    # 1. Circles
    try:
        from core.intelligence.circles_processor import CulturalCirclesProcessor
        proc = CulturalCirclesProcessor()
        text = signal.get("termo", "") + " " + signal.get("descricao", "")
        result = proc.process_text(text)
        enriched["circles"] = result
    except Exception:
        enriched["circles"] = None

    # 2. Sentiment (via analysis — basic approach)
    try:
        sentiment_val = float(signal.get("sentiment", 0.5))
        enriched["sentiment_detail"] = {
            "score": sentiment_val,
            "label": "positive" if sentiment_val > 0.6 else "negative" if sentiment_val < 0.4 else "neutral",
        }
    except Exception:
        enriched["sentiment_detail"] = None

    # 3. Tension
    try:
        from core.engines.tension_engine import get_tension_engine
        te = get_tension_engine()
        text = signal.get("termo", "") + " " + signal.get("descricao", "")
        tres = te.analyze(text=text, sentiment=float(signal.get("sentiment", 0.5)),
                          circle=signal.get("circulo", ""), plataforma=signal.get("plataforma", ""))
        enriched["tension"] = {
            "score": tres.score, "level": str(tres.level.value) if hasattr(tres.level, "value") else str(tres.level),
            "types": [t.value if hasattr(t, "value") else str(t) for t in tres.types],
            "alerts": tres.alerts, "description": tres.description,
        }
    except Exception:
        enriched["tension"] = None

    # 4. Nature
    try:
        from core.classifiers.signal_nature_classifier import SignalNatureClassifier
        nc = SignalNatureClassifier()
        nres = nc.classify(
            termo=signal.get("termo", ""), mencoes=[signal.get("descricao", "")],
            contextos=[], plataformas=[signal.get("plataforma", "")],
            tensoes=[], demografico={},
            velocity=float(signal.get("velocity", 0)),
            volume=int(signal.get("volume", 0)),
            sentiment=float(signal.get("sentiment", 0.5)),
        )
        enriched["nature"] = {
            "nature": nres.nature, "confidence": nres.confidence,
            "bot_risk": nres.bot_risk, "authenticity_score": nres.authenticity_score,
        }
    except Exception:
        enriched["nature"] = None

    # 5. Authenticity (Refined V9.3 - Rareness/Depth)
    try:
        from core.intelligence.business_synthesizer import BusinessSynthesizer
        bs = BusinessSynthesizer()
        text = signal.get("termo", "") + " " + (signal.get("descricao", "") or "")
        circle = signal.get("circulo", "festa_celebracao")
        
        # Novo cálculo de profundidade e raridade (Weak Signals V9.4)
        depth_results = bs.calculate_signal_depth(text, circle)
        enriched["authenticity"] = depth_results
        
        # Injetar os novos campos de pesos (Entropy Weights)
        enriched["weak_signal_score"] = depth_results.get("depth_score", 0)
        enriched["discovery_factor"] = depth_results.get("discovery_factor", 1.0)
        enriched["is_outlier"] = depth_results.get("is_outlier", False)
        enriched["is_mainstream"] = depth_results.get("is_mainstream", True)
    except Exception as e:
        logger.warning(f"⚠️ Erro ao calcular depth/rareness: {e}")
        enriched["authenticity"] = None

    # 6. Momentum
    try:
        from core.engines.momentum import compute_collector_momentum
        m = compute_collector_momentum(
            platform=signal.get("plataforma", "generic"),
            volume=int(signal.get("volume", 0)),
            engagement=float(signal.get("engagement", 0)),
            cultural_score=float(signal.get("relevancia_cultural", 0)),
            termo=signal.get("termo", ""),
        )
        enriched["momentum_computed"] = round(m, 2)
    except Exception:
        enriched["momentum_computed"] = None

    # 🚀 7. Reliability & Veracity (V9.9 Bridge Integration)
    try:
        from core.engines.reliability_engine import get_reliability_engine
        rel_engine = get_reliability_engine()
        
        # O Bridge passa o sinal para o motor de confiabilidade
        # que calcula Autoridade + Visual Proof + Cross-Verification
        rel_data = rel_engine.calculate_reliability(
            signal=signal, 
            model_accuracy=0.5 # Default inicial
        )
        
        enriched["reliability"] = rel_data.get("reliability", "MEDIA")
        enriched["accuracy_score"] = rel_data.get("accuracy_score", 0.5)
        enriched["is_verified"] = rel_data.get("is_verified", False)
        enriched["visual_proof"] = rel_data.get("visual_proof", False)
        enriched["cross_verified"] = rel_data.get("cross_verified", False)
        
    except Exception as e:
        logger.warning(f"⚠️ Reliability Engine Bridge Error: {e}")
        enriched["reliability"] = "MEDIA"
        enriched["is_verified"] = False

    try:
        from core.engines.pest_engine import get_pest_engine
        pe = get_pest_engine()
        text = signal.get("termo", "") + " " + signal.get("descricao", "")
        pres = pe.classify(text)
        enriched["pest"] = {
            "category": pres.category.value if hasattr(pres.category, "value") else str(pres.category),
            "confidence": pres.confidence,
            "keywords_matched": pres.keywords_matched,
        }
    except Exception:
        enriched["pest"] = None

    # 8. Topics
    try:
        from core.intelligence.topic_engine import get_topic_engine
        top = get_topic_engine()
        text = signal.get("termo", "") + " " + signal.get("descricao", "")
        topres = top.classify(text)
        enriched["topics"] = topres
    except Exception:
        enriched["topics"] = None

    # 9. Vulnerability
    try:
        from core.engines.vulnerability_engine import get_vulnerability_engine
        ve = get_vulnerability_engine()
        vres = ve.assess(signal)
        enriched["vulnerability"] = {
            "score": vres.score, "level": vres.level,
            "top_risks": vres.top_risks, "recommendations": vres.recommendations,
        }
    except Exception:
        enriched["vulnerability"] = None

    # 10. Alerts
    try:
        from alerts.cultural_alerts_engine import get_alerts_engine
        ae = get_alerts_engine()
        ares = ae.evaluate(signal)
        enriched["cultural_alerts"] = [
            {"type": a.alert_type, "severity": a.severity, "message": a.message, "action": a.action}
            for a in ares
        ]
    except Exception:
        enriched["cultural_alerts"] = None

    # 11. Strategic Actions
    try:
        from core.intelligence.strategic_actions_engine import get_strategic_engine
        se = get_strategic_engine()
        sres = se.recommend(signal)
        enriched["strategic_action"] = {
            "action_type": sres.action_type, "urgency": sres.urgency,
            "title": sres.title, "channels": sres.channels, "kpis": sres.kpis,
        }
    except Exception:
        enriched["strategic_action"] = None

    # 12. Scenarios
    try:
        from core.engines.scenario_engine import get_scenario_engine
        sce = get_scenario_engine()
        scres = sce.generate_dict(signal)
        enriched["scenarios"] = scres
    except Exception:
        enriched["scenarios"] = None

    # 13. Opportunities
    try:
        from core.intelligence.opportunity_engine import get_opportunity_engine
        oe = get_opportunity_engine()
        ores = oe.detect(signal)
        enriched["opportunities"] = [
            {"type": o.opportunity_type, "confidence": o.confidence,
             "title": o.title, "window_weeks": o.window_weeks}
            for o in ores
        ]
    except Exception:
        enriched["opportunities"] = None

    # 14. Risk
    try:
        from core.engines.risk_engine import get_risk_engine
        re_ = get_risk_engine()
        rres = re_.assess_dict(signal)
        enriched["risk"] = rres
    except Exception:
        enriched["risk"] = None

    # 15. Cluster labels
    try:
        cluster_id = signal.get("cluster_id")
        if cluster_id is not None:
            from core.clustering import get_cluster_labeler
            cl = get_cluster_labeler()
            enriched["cluster_label"] = cl.label_clusters({
                cluster_id: [signal.get("termo", "")]
            })
    except Exception:
        pass

    return enriched


def _extract_dimensions(enriched: dict, dimensions: Optional[List[str]] = None) -> dict:
    """Extract specific dimensions from an enriched signal, or all if None."""
    ALL_DIMS = [
        "circles", "sentiment_detail", "tension", "nature", "authenticity",
        "momentum_computed", "velocity", "graph_analysis", "feedback",
        "topics", "pest", "vulnerability", "cultural_alerts",
        "strategic_action", "scenarios", "opportunities", "risk",
    ]
    dims = dimensions or ALL_DIMS
    return {d: enriched.get(d) for d in dims}


# ── F-8: Drill-Down ─────────────────────────────────────────────────────

@router.post("/detail", response_model=GenericResponse)
async def signal_detail(req: SignalDetailRequest):
    """
    F-8 Drill-Down: Get FULL enrichment detail for a single signal.

    Runs all 16 engines and returns a consolidated view with every
    dimension (circles, sentiment, tension, nature, PEST, vulnerability,
    risk, actions, scenarios, opportunities, etc.).

    The Next.js frontend renders this as a slide-out panel when the
    user clicks on any signal in a chart.
    """
    t0 = time.time()
    signal = req.signal
    if not signal.get("termo"):
        raise HTTPException(status_code=400, detail="Signal must include 'termo'.")

    try:
        enriched = _run_all_engines(signal)
        duration = time.time() - t0
        dimensions = _extract_dimensions(enriched)
        return GenericResponse(
            data={
                "signal": {
                    "termo": signal.get("termo"),
                    "plataforma": signal.get("plataforma"),
                    "circulo": signal.get("circulo"),
                    "timestamp": signal.get("timestamp"),
                },
                "enrichments": dimensions,
                "enrichment_count": sum(1 for v in dimensions.values() if v is not None),
                "total_dimensions": len(dimensions),
            },
            metadata={"duration_s": round(duration, 3), "endpoint": "F-8 drill-down"},
        )
    except Exception as exc:
        logger.error("signal_detail error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ── F-12: Comparative ───────────────────────────────────────────────────

@router.post("/compare", response_model=GenericResponse)
async def signal_compare(req: CompareRequest):
    """
    F-12 Comparative: Compare 2-10 signals side-by-side.

    Runs all engines on each signal and returns a structured comparison
    matrix. Optionally filter to specific dimensions.

    The Next.js frontend renders this as a side-by-side table or
    overlay chart.
    """
    t0 = time.time()
    results = []

    for sig in req.signals:
        if not sig.get("termo"):
            continue
        enriched = _run_all_engines(sig)
        dims = _extract_dimensions(enriched, req.dimensions)
        results.append({
            "signal": {
                "termo": sig.get("termo"),
                "plataforma": sig.get("plataforma"),
                "circulo": sig.get("circulo"),
            },
            "dimensions": dims,
        })

    if len(results) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 valid signals with 'termo'.")

    # Build comparison summary
    summary = _build_comparison_summary(results)
    duration = time.time() - t0

    return GenericResponse(
        data={
            "comparison": results,
            "signal_count": len(results),
            "summary": summary,
        },
        metadata={
            "duration_s": round(duration, 3),
            "dimensions_compared": req.dimensions or "all",
            "endpoint": "F-12 comparative",
        },
    )


def _build_comparison_summary(results: List[dict]) -> dict:
    """Build a high-level summary comparing signals across key numeric dimensions."""
    summary = {}

    # Momentum comparison
    momenta = []
    for r in results:
        m = r["dimensions"].get("momentum_computed")
        if m is not None:
            momenta.append({"termo": r["signal"]["termo"], "momentum": m})
    if momenta:
        momenta.sort(key=lambda x: x["momentum"], reverse=True)
        summary["momentum_ranking"] = momenta

    # Vulnerability comparison
    vulns = []
    for r in results:
        v = r["dimensions"].get("vulnerability")
        if v and isinstance(v, dict):
            vulns.append({"termo": r["signal"]["termo"], "score": v.get("score", 0), "level": v.get("level", "")})
    if vulns:
        vulns.sort(key=lambda x: x["score"], reverse=True)
        summary["vulnerability_ranking"] = vulns

    # Tension comparison
    tensions = []
    for r in results:
        t = r["dimensions"].get("tension")
        if t and isinstance(t, dict):
            tensions.append({"termo": r["signal"]["termo"], "score": t.get("score", 0), "level": t.get("level", "")})
    if tensions:
        tensions.sort(key=lambda x: x["score"], reverse=True)
        summary["tension_ranking"] = tensions

    # PEST distribution
    pest_dist = {}
    for r in results:
        p = r["dimensions"].get("pest")
        if p and isinstance(p, dict):
            cat = p.get("category", "unknown")
            pest_dist.setdefault(cat, []).append(r["signal"]["termo"])
    if pest_dist:
        summary["pest_distribution"] = pest_dist

    # Opportunity count comparison
    opp_counts = []
    for r in results:
        opps = r["dimensions"].get("opportunities")
        if opps and isinstance(opps, list):
            opp_counts.append({"termo": r["signal"]["termo"], "opportunity_count": len(opps)})
    if opp_counts:
        opp_counts.sort(key=lambda x: x["opportunity_count"], reverse=True)
        summary["opportunity_ranking"] = opp_counts

    return summary


# ── Live signals for frontend KeywordContext ─────────────────────────────────

@router.get("/live", response_model=GenericResponse)
async def signals_live(
    keywords: str = "",
    period_days: int = 30,
    limit: int = 50,
):
    """
    GET /api/v8/signals/live?keywords=funk,sertanejo&period_days=30&limit=50

    Returns real signals from Supabase filtered by keywords, formatted as
    ActiveSignal[] for the Next.js KeywordContext.

    Response shape per signal:
      { termo, momentum, sentiment, volume, plataforma, score, circulo, regiao }
    """
    kw_list = [k.strip() for k in keywords.split(",") if k.strip()] if keywords else []

    try:
        from config.centralized_config import get_supabase_client
        supabase = get_supabase_client()

        if supabase:
            query = supabase.table("cultural_signals").select(
                "id, termo, circulo, score, regiao, plataforma, raw_data, ts"
            ).order("ts", desc=True).limit(500)

            result = query.execute()
            rows = result.data or []

            if kw_list:
                kw_lower = [k.lower() for k in kw_list[:20]]
                matched = [
                    r for r in rows
                    if any(
                        kw in (r.get("termo") or "").lower() or
                        kw in (r.get("circulo") or "").lower()
                        for kw in kw_lower
                    )
                ]
                # Fallback: if no match, return recent signals
                rows = matched if matched else rows[:limit]
            else:
                rows = rows[:limit]

            signals_out = []
            for s in rows[:limit]:
                rd = s.get("raw_data") or {}
                if isinstance(rd, str):
                    import ast
                    try:
                        rd = ast.literal_eval(rd)
                    except Exception:
                        rd = {}
                raw_momentum = float(rd.get("momentum") or 50)
                # Normalize momentum: if stored 0-100 convert to 0-1
                momentum = raw_momentum / 100 if raw_momentum > 1 else raw_momentum
                signals_out.append({
                    "termo": s.get("termo") or "unknown",
                    "momentum": round(min(1.0, momentum), 3),
                    "sentiment": round(float(rd.get("sentiment") or 0.5), 3),
                    "volume": int(rd.get("volume") or rd.get("views") or 10),
                    "plataforma": s.get("plataforma") or "unknown",
                    "score": round(float(s.get("score") or 0), 3),
                    "circulo": s.get("circulo") or "",
                    "regiao": s.get("regiao") or "",
                })

            return GenericResponse(
                status="success",
                data=signals_out,
                metadata={
                    "total": len(signals_out),
                    "keywords": kw_list,
                    "data_source": "supabase_real",
                },
            )
    except Exception as e:
        logger.warning(f"signals/live Supabase error: {e}")

    # Fallback: generate synthetic signals based on keywords
    import random
    platforms = ["YouTube", "Spotify", "Reddit", "Instagram", "NewsAPI"]
    circles = ["música", "tecnologia", "gastronomia", "sustentabilidade", "esporte", "moda", "cultura digital"]
    fallback_kws = kw_list if kw_list else ["cultura", "brasil", "tendência"]
    signals_out = [
        {
            "termo": fallback_kws[i % len(fallback_kws)],
            "momentum": round(random.uniform(0.4, 0.95), 3),
            "sentiment": round(random.uniform(0.2, 0.85), 3),
            "volume": random.randint(10, 80),
            "plataforma": platforms[i % len(platforms)],
            "score": round(random.uniform(0.35, 0.9), 3),
            "circulo": circles[i % len(circles)],
            "regiao": "Brasil",
        }
        for i in range(min(limit, max(len(fallback_kws) * 3, 10)))
    ]
    return GenericResponse(
        status="success",
        data=signals_out,
        metadata={"total": len(signals_out), "keywords": kw_list, "data_source": "simulated"},
    )
