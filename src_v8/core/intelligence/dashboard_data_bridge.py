#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Data Bridge — Culture Pulse V9.7 (H-5678)
=====================================================
Derives real weak signals, emerging trends, emerging profiles,
and cultural relationships from the enriched pipeline data.

V9.7 REAL-TIME PRIORITY:
  - Integration with BusinessSynthesizer Depth Context
  - Intent-aware logic (Research vs Campaign)
  - Zero Mock Data policy (Supabase/Redis history only)
"""

from __future__ import annotations

import logging
import re
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ── 16 Cultural Circles (canonical names) ────────────────────────────────────

CIRCLES = [
    "Família & Tradições",
    "Gastronomia & Sabores",
    "Música & Festivais",
    "Futebol & Esportes",
    "Religião & Espiritualidade",
    "Tecnologia & Digital",
    "Trabalho & Prosperidade",
    "Educação & Conhecimento",
    "Saúde & Bem-Estar",
    "Sustentabilidade & Consumo",
    "Diversidade & Inclusão",
    "Comunidade & Vizinhança",
    "Status & Reconhecimento",
    "Relacionamentos & Afeto",
    "Humor & Entretenimento",
    "Moda & Estilo",
]

# Map common platform names → readable source labels
_SOURCE_LABELS = {
    "youtube": "YouTube Analytics",
    "reddit": "Reddit Trends",
    "spotify": "Spotify Cultural Insights",
    "newsapi": "NewsAPI Intelligence",
    "google_trends": "Google Trends",
    "instagram": "Instagram Analytics",
    "meetup": "Meetup Events",
    "eventbrite": "Eventbrite Pulse",
}

# ── PEST category emoji map ─────────────────────────────────────────────────
_PEST_EMOJI = {
    "Political": "🏛️",
    "Economic": "💰",
    "Social": "👥",
    "Technological": "💻",
}

# ── Trend category labels ───────────────────────────────────────────────────
_TREND_CATEGORIES = [
    "💻 **Comportamento Digital**",
    "🌱 **Consumo Consciente**",
    "🎭 **Identidade Cultural**",
    "🏢 **Trabalho & Economia**",
]


# ═══════════════════════════════════════════════════════════════════════════════
#  1. WEAK SIGNALS (Now Real-Time Driven)
# ═══════════════════════════════════════════════════════════════════════════════

def derive_weak_signals(
    signals: List[dict],
    intent: str = "research",
    top_n: int = 8,
) -> List[dict]:
    """
    Derive weak signals from real API data.
    Priority: Higher validation scores from BusinessSynthesizer.
    """
    if not signals:
        return []

    scored: List[Tuple[float, dict]] = []

    for sig in signals:
        termo = sig.get("termo", "")
        if not termo: continue

        # 1. Coleta de Métricas Enriquecidas (Sintetizador V9.7)
        depth = sig.get("quality_score", 0.5) 
        is_verified = sig.get("is_verified", False)
        
        # 2. Lógica: Baixo Volume + Alta Autenticidade + V9 Validation
        momentum = sig.get("momentum", 0)
        volume = sig.get("volume", 0)
        
        vol_score = max(0, 1.0 - min(volume / 5000, 1.0)) 
        
        # Ponderação pela Intenção:
        if intent == "research":
            strength = (vol_score * 0.4) + (depth * 0.4) + (0.2 if is_verified else 0)
        else: # Campaign
            strength = (vol_score * 0.2) + (depth * 0.5) + (sig.get("relevancia_cultural", 0.5) * 0.3)

        if strength < 0.2: continue

        plataforma = sig.get("plataforma", "unknown")
        # Usa o Insight do Sintetizador se disponível, mantendo tom sério
        description = sig.get("insight_summary", sig.get("descricao", f"Sinal emergente sobre '{termo}'."))

        scored.append((strength, {
            "title": termo,
            "description": description,
            "strength": round(strength * 10, 1),
            "source": _SOURCE_LABELS.get(plataforma.lower(), plataforma.title()),
            "actionable": is_verified,
            "action": "Aprofundar Análise" if intent == "research" else "Ativar Campanha",
            "metadata": {
                "momentum": momentum,
                "is_verified": is_verified,
                "intent_alignment": intent
            }
        }))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [s[1] for s in scored[:top_n]]

# ═══════════════════════════════════════════════════════════════════════════════
#  2. EMERGING TRENDS (Now Real-Time Driven)
# ═══════════════════════════════════════════════════════════════════════════════

def derive_emerging_trends(
    signals: List[dict],
    intent: str = "research",
    top_n: int = 5,
) -> List[dict]:
    """
    Groups real signals into actionable trends with high cognitive accuracy.
    Focus on S4.1-REALTIME: High correlation and verified signals.
    """
    if not signals: return []

    trends = []
    # Agrupamento por Círculo E Plataforma para evitar homogeneização forçada
    by_cluster = defaultdict(list)
    for s in signals:
        # Cluster base: Círculo Cultural + Plataforma (indicador de ecossistema)
        cluster_key = (s.get("circulo", "Geral"), s.get("plataforma", "unknown"))
        by_cluster[cluster_key].append(s)

    for (circle, platform), sigs in by_cluster.items():
        if not sigs: continue
        
        # 1. ACCURACY CALCULATION (V9.7 Logic)
        # Sinais verificados valem 3x mais na densidade da tendência
        accuracy_density = sum(1.5 if s.get("is_verified") else 1.0 for s in sigs)
        avg_momentum = sum(s.get("momentum", 0) for s in sigs) / len(sigs)
        
        # 2. DEFINITION OF THE "WHY"
        # Prioriza o insight do sintetizador que explica a causa da tendência
        best_insight = next((s.get("insight_summary") for s in sigs if s.get("insight_summary")), None)
        main_term = max(sigs, key=lambda x: x.get("momentum", 0)).get("termo", circle)
        
        description = best_insight if best_insight else f"Concentração de {len(sigs)} sinais em {circle} via {platform} com momentum crescente."

        trends.append({
            "category": circle,
            "title": main_term,
            "description": description,
            "momentum": round(min(100, avg_momentum + (accuracy_density * 3)), 1),
            "direction": "up" if avg_momentum > 35 or accuracy_density > 3 else "stable",
            "is_strategic": any(s.get("is_verified", False) for s in sigs),
            "platform_source": platform
        })

    trends.sort(key=lambda x: x["momentum"], reverse=True)
    return trends[:top_n]


# ═══════════════════════════════════════════════════════════════════════════════
#  3. EMERGING PROFILES  (replaces _generate_emerging_profiles)
# ═══════════════════════════════════════════════════════════════════════════════

def derive_emerging_profiles(
    signals: List[dict],
    intent: str = "research",
    top_n: int = 6,
) -> List[dict]:
    """
    Derive specific, high-accuracy consumer profiles (Personas Reais).
    Replaces "General" descriptions with behavior-driven traits.
    """
    if not signals: return []

    circle_groups: Dict[str, List[dict]] = defaultdict(list)
    for sig in signals:
        circle = sig.get("circulo", "Geral")
        circle_groups[circle].append(sig)

    profiles = []

    for circle, sigs in circle_groups.items():
        # 1. DATA RICHNESS FILTER
        if len(sigs) < 2 and not any(s.get("is_verified") for s in sigs):
            continue

        # 2. IDENTITY INFERENCE (V9.7)
        # Verifica se o Sintetizador já rotulou a audiência
        custom_name = next((s.get("audience_label") for s in sigs if s.get("audience_label")), None)
        
        # Se não houver rótulo de IA, usamos lógica comportamental dura
        avg_auth = sum(s.get("authenticity_analysis", {}).get("authenticity_score", 0.5) for s in sigs) / len(sigs)
        avg_tension = sum(s.get("tension_analysis", {}).get("tension_score", 0) for s in sigs) / len(sigs)
        
        # Denominação baseada em Comportamento Real vs Círculo
        if not custom_name:
            if avg_auth > 0.8: prefix = "Curadores de"
            elif avg_tension > 0.6: prefix = "Questionadores de"
            elif len(sigs) > 5: prefix = "Massa Crítica em"
            else: prefix = "Entusiastas de"
            name = f"{prefix} {circle}"
        else:
            name = custom_name

        # 3. RELEVANCE & ACCURACY
        # Perfis com sinais de múltiplas plataformas são considerados "Omnichannel" (mais reais/robustos)
        unique_platforms = len(set(s.get("plataforma") for s in sigs))
        accuracy_score = (avg_auth * 60) + (unique_platforms * 15) + (len(sigs) * 5)
        
        profiles.append({
            "name": name,
            "description": next((s.get("insight_summary") for s in sigs if s.get("insight_summary")), 
                              f"Grupo ativamente engajado com {circle} apresentando alta taxa de autenticidade."),
            "relevance": round(min(100, accuracy_score), 1),
            "growth": f"+{round(sum(s.get('velocity_analysis', {}).get('velocity', 0) for s in sigs) * 10, 1) if sigs else 0}%",
            "behaviors": list(set(b for s in sigs for b in s.get("behaviors", ["Consumo Direto"])))[:3],
            "is_omnidata": unique_platforms > 1,
            "connected_circles": list(set(str(s.get("graph_analysis", {}).get("neighbors", [])[0:1]) for s in sigs if s.get("graph_analysis")))[:2]
        })

    profiles.sort(key=lambda x: x["relevance"], reverse=True)
    return profiles[:top_n]


# ═══════════════════════════════════════════════════════════════════════════════
#  4. CULTURAL RELATIONSHIPS  (replaces _generate_cultural_relationships)
# ═══════════════════════════════════════════════════════════════════════════════

def derive_cultural_relationships(
    signals: List[dict],
    top_n: int = 8,
) -> List[dict]:
    """
    Derive relationships between cultural circles from enriched data.

    Uses graph_analysis neighbors + tension co-occurrence to find
    circle-pair connections.

    Returns list of dicts matching the legacy shape:
      {circle_1, circle_2, strength, type, description, opportunity, risk}
    """
    if not signals:
        return []

    # Count co-occurrences between circles
    pair_counts: Dict[Tuple[str, str], int] = Counter()
    pair_tensions: Dict[Tuple[str, str], List[float]] = defaultdict(list)
    pair_sentiments: Dict[Tuple[str, str], List[float]] = defaultdict(list)

    for sig in signals:
        circle = sig.get("circulo", "")
        if not circle:
            continue

        # Get graph neighbors
        gd = sig.get("graph_analysis", {})
        neighbors = gd.get("neighbors", []) if isinstance(gd, dict) else []

        td = sig.get("tension_analysis", {})
        t_score = td.get("tension_score", 0) if isinstance(td, dict) else 0

        sd = sig.get("sentiment_detail", {})
        s_score = sd.get("alma_score", 50) / 100.0 if isinstance(sd, dict) else 0.5

        for neighbor in neighbors:
            if neighbor == circle:
                continue
            pair = tuple(sorted([circle, neighbor]))
            pair_counts[pair] += 1
            pair_tensions[pair].append(t_score)
            pair_sentiments[pair].append(s_score)

    # Also infer from circles that share signals (signals assigned to multiple circles)
    # Use circle co-assignment from different signals with same termo
    termo_circles: Dict[str, set] = defaultdict(set)
    for sig in signals:
        c = sig.get("circulo", "")
        t = sig.get("termo", "")
        if c and t:
            termo_circles[t].add(c)

    for termo, circles_set in termo_circles.items():
        if len(circles_set) >= 2:
            circle_list = sorted(circles_set)
            for i in range(len(circle_list)):
                for j in range(i + 1, len(circle_list)):
                    pair = (circle_list[i], circle_list[j])
                    pair_counts[pair] = pair_counts.get(pair, 0) + 1

    if not pair_counts:
        return []

    # Score and rank pairs
    max_count = max(pair_counts.values()) if pair_counts else 1
    relationships: List[Tuple[float, dict]] = []

    for pair, count in pair_counts.items():
        strength = round(min(count / max(max_count, 1), 0.99), 2)
        if strength < 0.1:
            continue

        avg_tension = (
            sum(pair_tensions[pair]) / len(pair_tensions[pair])
            if pair_tensions[pair] else 0
        )
        avg_sentiment = (
            sum(pair_sentiments[pair]) / len(pair_sentiments[pair])
            if pair_sentiments[pair] else 0.5
        )

        rel_type = _classify_relationship(strength, avg_tension, avg_sentiment)
        desc = _relationship_description(pair[0], pair[1], rel_type, strength)
        opp = _relationship_opportunity(pair[0], pair[1], rel_type)
        risk = _relationship_risk(pair[0], pair[1], rel_type, avg_tension)

        relationships.append((strength, {
            "circle_1": pair[0],
            "circle_2": pair[1],
            "strength": strength,
            "type": rel_type,
            "description": desc,
            "opportunity": opp,
            "risk": risk,
        }))

    relationships.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in relationships[:top_n]]


# ═══════════════════════════════════════════════════════════════════════════════
#  Helper functions
# ═══════════════════════════════════════════════════════════════════════════════

def _title_from_termo(termo: str) -> str:
    """Create a human-readable title from a signal term."""
    if not termo:
        return "Sinal Emergente"
    words = termo.strip().split()
    title = " ".join(w.capitalize() for w in words[:6])
    return title if len(title) > 3 else f"Tendência: {title}"


def _suggest_action(termo: str, pest: str, vel_trend: str) -> str:
    """Suggest an actionable next step based on signal characteristics."""
    actions = {
        "Political": f"Monitorar implicações regulatórias de '{termo}' e preparar posicionamento.",
        "Economic": f"Avaliar oportunidade de mercado em '{termo}' e impacto financeiro.",
        "Social": f"Mapear comunidades engajadas com '{termo}' para parcerias autênticas.",
        "Technological": f"Avaliar adoção tecnológica em '{termo}' e potencial de inovação.",
    }
    base = actions.get(pest, f"Acompanhar evolução de '{termo}' nos próximos 30 dias.")
    if vel_trend in ("rising", "accelerating"):
        base += " Prioridade alta — velocidade crescente."
    return base


def _pest_to_trend_category(pest: str) -> str:
    """Map PEST primary to a trend category label."""
    mapping = {
        "Political": "🏛️ **Política & Regulação**",
        "Economic": "🏢 **Trabalho & Economia**",
        "Social": "🎭 **Identidade Cultural**",
        "Technological": "💻 **Comportamento Digital**",
    }
    return mapping.get(pest, "🌱 **Consumo Consciente**")


def _circulo_to_category(circulo: str) -> str:
    """Map a cultural circle name to a trend category label."""
    c = (circulo or "").lower()
    if any(x in c for x in ("music", "música", "funk", "sertanejo", "pagode", "samba", "forró")):
        return "🎵 **Música & Entretenimento**"
    if any(x in c for x in ("sustentabilidade", "meio ambiente", "clima", "verde")):
        return "🌱 **Consumo Consciente**"
    if any(x in c for x in ("tecnologia", "tech", "digital", "ia", "inteligência")):
        return "💻 **Comportamento Digital**"
    if any(x in c for x in ("gastronomia", "comida", "alimentação", "culinária")):
        return "🍽️ **Gastronomia & Lifestyle**"
    if any(x in c for x in ("moda", "beleza", "fashion", "estética")):
        return "👗 **Moda & Beleza**"
    if any(x in c for x in ("esporte", "fitness", "saúde", "bem-estar")):
        return "💪 **Saúde & Bem-estar**"
    if any(x in c for x in ("politica", "política", "governo", "social")):
        return "🏛️ **Política & Identidade**"
    return "🎭 **Identidade Cultural**"


def _clean_trend_name(raw: str) -> str:
    """Clean up a topic/group name for display."""
    if not raw:
        return "Tendência Emergente"
    # Remove leading numbers / underscores
    cleaned = re.sub(r"^[\d_]+", "", raw).strip()
    if not cleaned:
        return raw
    return cleaned[:80]


def _infer_related_circles(circle: str) -> set:
    """Infer related circles when graph data is unavailable."""
    relations = {
        "Família & Tradições": {"Gastronomia & Sabores", "Religião & Espiritualidade"},
        "Gastronomia & Sabores": {"Família & Tradições", "Saúde & Bem-Estar"},
        "Música & Festivais": {"Comunidade & Vizinhança", "Humor & Entretenimento"},
        "Futebol & Esportes": {"Comunidade & Vizinhança", "Status & Reconhecimento"},
        "Religião & Espiritualidade": {"Família & Tradições", "Comunidade & Vizinhança"},
        "Tecnologia & Digital": {"Trabalho & Prosperidade", "Educação & Conhecimento"},
        "Trabalho & Prosperidade": {"Tecnologia & Digital", "Educação & Conhecimento"},
        "Educação & Conhecimento": {"Trabalho & Prosperidade", "Tecnologia & Digital"},
        "Saúde & Bem-Estar": {"Gastronomia & Sabores", "Sustentabilidade & Consumo"},
        "Sustentabilidade & Consumo": {"Saúde & Bem-Estar", "Diversidade & Inclusão"},
        "Diversidade & Inclusão": {"Sustentabilidade & Consumo", "Comunidade & Vizinhança"},
        "Comunidade & Vizinhança": {"Música & Festivais", "Religião & Espiritualidade"},
        "Status & Reconhecimento": {"Moda & Estilo", "Futebol & Esportes"},
        "Relacionamentos & Afeto": {"Família & Tradições", "Tecnologia & Digital"},
        "Humor & Entretenimento": {"Música & Festivais", "Tecnologia & Digital"},
        "Moda & Estilo": {"Status & Reconhecimento", "Sustentabilidade & Consumo"},
    }
    return relations.get(circle, {"Tecnologia & Digital", "Comunidade & Vizinhança"})


def _infer_behaviors(platforms: List[str], auth: float, tension: float) -> str:
    """Generate a behavior description string."""
    parts = []
    if "youtube" in platforms or "tiktok" in platforms:
        parts.append("Consumo intenso de vídeo")
    if "reddit" in platforms:
        parts.append("Discussão em comunidades online")
    if "spotify" in platforms:
        parts.append("Cultura musical ativa")
    if "instagram" in platforms:
        parts.append("Engajamento visual")
    if auth > 0.7:
        parts.append("valorização de autenticidade")
    if tension > 0.5:
        parts.append("sensibilidade a tensões culturais")
    return ", ".join(parts) if parts else "Perfil digital ativo com múltiplas interações"


def _infer_demographics(circle: str, platforms: List[str]) -> str:
    """Infer approximate demographics from circle + platforms."""
    age_hints = {
        "Tecnologia & Digital": "18-35 anos",
        "Família & Tradições": "30-55 anos",
        "Música & Festivais": "16-30 anos",
        "Futebol & Esportes": "18-45 anos",
        "Educação & Conhecimento": "20-40 anos",
        "Saúde & Bem-Estar": "25-45 anos",
        "Sustentabilidade & Consumo": "22-38 anos",
        "Trabalho & Prosperidade": "25-50 anos",
    }
    age = age_hints.get(circle, "20-45 anos")
    classes = "classes B/C" if circle not in ("Status & Reconhecimento",) else "classes A/B"
    return f"{age}, {classes}, digitalmente ativos"


def _estimate_size(signal_count: int) -> str:
    """Estimate audience size from signal count (very rough)."""
    base = signal_count * 150_000
    if base >= 1_000_000:
        return f"{base / 1_000_000:.1f}M pessoas"
    return f"{base / 1_000:.0f}K pessoas"


def _profile_name(circle: str, pest: str, sentiment: float) -> str:
    """Generate a creative profile name."""
    prefixes = {
        "Tecnologia & Digital": "Conectados Digitais",
        "Família & Tradições": "Guardiões de Tradição",
        "Música & Festivais": "Vibrantes Culturais",
        "Futebol & Esportes": "Torcedores Engajados",
        "Sustentabilidade & Consumo": "Eco-Conscientes",
        "Diversidade & Inclusão": "Ativistas Culturais",
        "Trabalho & Prosperidade": "Empreendedores Emergentes",
        "Educação & Conhecimento": "Buscadores de Saber",
        "Saúde & Bem-Estar": "Wellness Seekers",
        "Comunidade & Vizinhança": "Construtores Comunitários",
        "Gastronomia & Sabores": "Foodies Brasileiros",
        "Religião & Espiritualidade": "Espiritualizados Modernos",
        "Status & Reconhecimento": "Aspirantes de Status",
        "Relacionamentos & Afeto": "Buscadores de Conexão",
        "Humor & Entretenimento": "Creators de Conteúdo",
        "Moda & Estilo": "Trendsetters Locais",
    }
    return prefixes.get(circle, f"Perfil {circle.split(' &')[0]}")


def _profile_description(circle: str, name: str, count: int, auth: float) -> str:
    """Generate profile description."""
    auth_label = "alta autenticidade" if auth > 0.7 else "autenticidade moderada"
    return (
        f"Perfil emergente no círculo '{circle}' com {count} sinais "
        f"captados. Grupo demonstra {auth_label} e engajamento crescente "
        f"com conteúdos relacionados."
    )


def _profile_opportunity(circle: str, pest: str, auth: float) -> str:
    """Generate opportunity text."""
    if auth > 0.7:
        return f"Alta autenticidade permite parcerias genuínas em {circle}."
    return f"Oportunidade de posicionamento no círculo {circle} via conteúdo relevante."


def _profile_warnings(tension: float, auth: float) -> str:
    """Generate warning text."""
    if tension > 0.6:
        return "Alto nível de tensão cultural — abordagem cuidadosa necessária."
    if auth < 0.4:
        return "Baixa autenticidade percebida — investir em credibilidade primeiro."
    return "Manter monitoramento contínuo para detectar mudanças de percepção."


def _classify_relationship(strength: float, tension: float, sentiment: float) -> str:
    """Classify the type of relationship between two circles."""
    if tension > 0.6:
        return "Conflito Ativo" if tension > 0.8 else "Tensão Criativa"
    if strength > 0.75 and sentiment > 0.6:
        return "Sinergia Natural"
    if strength > 0.5:
        return "Amplificação Mútua"
    return "Evolução Necessária"


def _relationship_description(c1: str, c2: str, rel_type: str, strength: float) -> str:
    """Generate relationship description."""
    return (
        f"{'Forte' if strength > 0.7 else 'Moderada'} conexão entre "
        f"{c1} e {c2} ({rel_type}). "
        f"Força: {strength:.0%}."
    )


def _relationship_opportunity(c1: str, c2: str, rel_type: str) -> str:
    """Generate relationship opportunity text."""
    if rel_type == "Sinergia Natural":
        return f"Campanhas que conectam {c1} com {c2} têm alto potencial emocional."
    if rel_type == "Tensão Criativa":
        return f"Resolver a tensão entre {c1} e {c2} pode gerar posicionamento diferenciado."
    return f"Explorar interseção entre {c1} e {c2} para conteúdo original."


def _relationship_risk(c1: str, c2: str, rel_type: str, tension: float) -> Optional[str]:
    """Generate relationship risk text (None if no risk)."""
    if tension > 0.5:
        return f"Tensão elevada entre {c1} e {c2} pode gerar reação negativa se mal abordada."
    if rel_type == "Evolução Necessária":
        return f"Relação incipiente — investimento prematuro pode não gerar retorno."
    return None


# ═══════════════════════════════════════════════════════════════════════════════
#  Convenience: get enriched signals and derive all 4 datasets
# ═══════════════════════════════════════════════════════════════════════════════

def get_dashboard_data(
    signals: Optional[List[dict]] = None,
    plan: str = "free",
    count: int = 50,
) -> Dict[str, List[dict]]:
    """
    One-shot: derive all 4 datasets from enriched signals.

    If ``signals`` is None, attempts to load from EnrichedDataReader.

    Returns:
        {
          "weak_signals": [...],
          "emerging_trends": [...],
          "emerging_profiles": [...],
          "cultural_relationships": [...],
        }
    """
    if signals is None:
        try:
            from core.intelligence.enriched_reader import get_enriched_signals
            signals = get_enriched_signals(plan=plan, count=count)
        except Exception as exc:
            logger.warning("dashboard_data_bridge: could not load enriched signals: %s", exc)
            signals = []

    return {
        "weak_signals": derive_weak_signals(signals),
        "emerging_trends": derive_emerging_trends(signals),
        "emerging_profiles": derive_emerging_profiles(signals),
        "cultural_relationships": derive_cultural_relationships(signals),
    }
