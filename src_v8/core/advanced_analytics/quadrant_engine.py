#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Signal Quadrant — Culture Pulse V9.0  (Sprint S3.6 / P18B)
============================================================
Dashboard component: Relevância × Novidade scatter quadrant.

Quadrants:
  ┌────────────┬────────────┐
  │ Top-Left   │ Top-Right  │
  │ Established│ STRONG     │  ← push notification zone
  │ Signals    │ SIGNALS    │
  ├────────────┼────────────┤
  │ Bottom-Left│ Bottom-Rt  │
  │ Noise      │ Emerging   │
  │            │ (watch)    │
  └────────────┴────────────┘
  X = novelty_score (0..1)
  Y = relevancia_score (0..1)
  Colour = cultural circle
  Size   = signal_strength

Usage in dashboard:
  from dashboard.components.signal_quadrant import render_signal_quadrant
  render_signal_quadrant(signals_data)
"""

from __future__ import annotations

import hashlib
import logging
import math
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ── Lazy imports ────────────────────────────────────────────────────────────
try:
    import plotly.express as px
    import plotly.graph_objects as go
    _PLOTLY = True
except ImportError:
    _PLOTLY = False

try:
    import pandas as pd
    _PD = True
except ImportError:
    _PD = False


# ── Project root ────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ═══════════════════════════════════════════════════════════════════════════════
#  CIRCLE COLOR MAP (16 circles)
# ═══════════════════════════════════════════════════════════════════════════════

CIRCLE_COLORS: Dict[str, str] = {
    "MUSICA": "#E91E63",
    "GASTRONOMIA": "#FF9800",
    "MODA": "#9C27B0",
    "TECNOLOGIA": "#2196F3",
    "ARTE": "#F44336",
    "ESPORTE": "#4CAF50",
    "POLITICA": "#607D8B",
    "SAUDE": "#00BCD4",
    "EDUCACAO": "#3F51B5",
    "COMPORTAMENTO": "#FF5722",
    "SUSTENTABILIDADE": "#8BC34A",
    "RELIGIAO": "#795548",
    "ECONOMIA": "#FFC107",
    "TURISMO": "#009688",
    "JUVENTUDE": "#E040FB",
    "FAMILIA": "#FFAB91",
}


# ═══════════════════════════════════════════════════════════════════════════════
#  SIGNAL METRICS CALCULATOR
# ═══════════════════════════════════════════════════════════════════════════════

def compute_novelty_score(signal: Dict) -> float:
    """
    Novelty score (0..1) based on:
      - How recently the signal appeared (recency)
      - Low frequency in historical data (uniqueness)
      - Source diversity (multiple platforms → higher novelty)
    """
    raw_data = signal.get("raw_data", {}) or {}

    # Factor 1: Recency (0..1)
    ts_str = signal.get("ts", "")
    recency = 0.5
    if ts_str:
        try:
            if isinstance(ts_str, str):
                ts_dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            else:
                ts_dt = ts_str
            if ts_dt.tzinfo is None:
                ts_dt = ts_dt.replace(tzinfo=timezone.utc)
            hours_ago = (datetime.now(timezone.utc) - ts_dt).total_seconds() / 3600
            recency = math.exp(-hours_ago / 48)  # half-life ~33h
        except (ValueError, TypeError):
            pass

    # Factor 2: Momentum anomaly (high momentum relative to baseline = novel)
    score = signal.get("score", 0) or 0
    momentum = raw_data.get("momentum", score * 100)
    if isinstance(momentum, (int, float)):
        momentum_novelty = min(1.0, abs(momentum) / 100.0)
    else:
        momentum_novelty = 0.5

    # Factor 3: Velocity-based novelty (high acceleration = novel)
    velocity = raw_data.get("velocity", 0) or 0
    accel = raw_data.get("momentum_velocity", 0) or 0
    vel_novelty = min(1.0, (abs(velocity) + abs(accel)) / 200.0) if velocity else 0.3

    # Weighted combination
    novelty = 0.35 * recency + 0.35 * momentum_novelty + 0.30 * vel_novelty
    return round(max(0.0, min(1.0, novelty)), 4)


def compute_relevance_score(signal: Dict) -> float:
    """
    Relevance score (0..1) based on:
      - Score field (already 0..1)
      - Source reliability
      - Volume/interaction indicators
    """
    raw_data = signal.get("raw_data", {}) or {}

    # Factor 1: Direct score
    base_score = signal.get("score", 0.5) or 0.5
    if isinstance(base_score, (int, float)):
        base_score = max(0.0, min(1.0, float(base_score)))
    else:
        base_score = 0.5

    # Factor 2: Source reliability
    reliability = raw_data.get("fonte_confiabilidade", "MEDIA")
    rel_map = {"ALTA": 0.9, "MEDIA": 0.6, "BAIXA": 0.3}
    rel_score = rel_map.get(reliability, 0.6)

    # Factor 3: Volume as proxy for cultural impact
    volume = raw_data.get("volume", 1) or 1
    if isinstance(volume, (int, float)):
        vol_score = min(1.0, math.log1p(volume) / 10.0)
    else:
        vol_score = 0.3

    relevance = 0.50 * base_score + 0.30 * rel_score + 0.20 * vol_score
    return round(max(0.0, min(1.0, relevance)), 4)


def compute_signal_strength(novelty: float, relevance: float) -> float:
    """Combined signal strength = geometric mean of novelty and relevance."""
    return round(math.sqrt(novelty * relevance), 4)


def classify_quadrant(novelty: float, relevance: float) -> str:
    """Assign quadrant label."""
    if novelty >= 0.5 and relevance >= 0.5:
        return "🔴 Sinal Forte"
    elif novelty >= 0.5 and relevance < 0.5:
        return "🟡 Emergente"
    elif novelty < 0.5 and relevance >= 0.5:
        return "🔵 Estabelecido"
    else:
        return "⚪ Ruído"


# ═══════════════════════════════════════════════════════════════════════════════
#  DATA PREPARATION
# ═══════════════════════════════════════════════════════════════════════════════

def prepare_quadrant_data(
    signals: List[Dict],
) -> "pd.DataFrame":
    """
    Convert list of signal dicts (from Supabase rows) into a DataFrame
    with novelty_score, relevance_score, signal_strength, quadrant.
    """
    if not _PD:
        raise ImportError("pandas is required for quadrant data")

    rows = []
    for sig in signals:
        raw = sig.get("raw_data", {}) or {}
        novelty = compute_novelty_score(sig)
        relevance = compute_relevance_score(sig)
        strength = compute_signal_strength(novelty, relevance)
        quadrant = classify_quadrant(novelty, relevance)
        circulo = sig.get("circulo", raw.get("circulo", "COMPORTAMENTO"))

        rows.append({
            "id": sig.get("id", 0),
            "termo": sig.get("termo", "?"),
            "plataforma": sig.get("plataforma", "?"),
            "circulo": circulo.upper() if isinstance(circulo, str) else "COMPORTAMENTO",
            "novelty_score": novelty,
            "relevance_score": relevance,
            "signal_strength": strength,
            "quadrant": quadrant,
            "title": raw.get("title", sig.get("termo", "")),
            "momentum": raw.get("momentum", sig.get("score", 0) * 100),
            "velocity": raw.get("velocity", 0),
            "source": raw.get("source", sig.get("plataforma", "")),
        })

    df = pd.DataFrame(rows)
    return df


# ═══════════════════════════════════════════════════════════════════════════════
#  STREAMLIT COMPONENT
# ═══════════════════════════════════════════════════════════════════════════════

def build_signal_quadrant_figure(
    signals: List[Dict],
    title: str = "📡 Quadrante de Sinais Culturais — Relevância × Novidade",
    height: int = 600,
    selected_circles: Optional[List[str]] = None,
) -> Optional[go.Figure]:
    """
    Build a Plotly scatter quadrant figure from a list of cultural signals.

    Parameters
    ----------
    signals : list of dict
        Rows from Supabase `cultural_signals` table (or CulturalSignal-like dicts).
    title : str
        Chart title.
    height : int
        Chart height in pixels.
    selected_circles : Optional[List[str]]
        List of cultural circles to filter on. If None, all circles are included.

    Returns
    -------
    plotly.graph_objects.Figure | None
        Plotly figure ready for rendering in any frontend, or None if no signals.
    """
    if not _PLOTLY:
        raise ImportError("Plotly is required for building the signal quadrant figure.")
    if not _PD:
        raise ImportError("Pandas is required for building the signal quadrant figure.")

    if not signals:
        logger.info("No signals available for quadrant figure generation.")
        return None

    df = prepare_quadrant_data(signals)
    if df.empty:
        logger.info("Prepared quadrant data is empty.")
        return None

    if selected_circles:
        df = df[df["circulo"].isin(selected_circles)]

    df = df.copy()
    df["color"] = df["circulo"].map(lambda c: CIRCLE_COLORS.get(c, "#999999"))
    df["bubble_size"] = df["signal_strength"].clip(0.05, 1.0) * 30

    fig = px.scatter(
        df,
        x="novelty_score",
        y="relevance_score",
        color="circulo",
        color_discrete_map=CIRCLE_COLORS,
        size="bubble_size",
        hover_name="termo",
        hover_data={
            "quadrant": True,
            "plataforma": True,
            "momentum": ":.1f",
            "velocity": ":.1f",
            "novelty_score": ":.3f",
            "relevance_score": ":.3f",
            "signal_strength": ":.3f",
            "bubble_size": False,
            "color": False,
        },
        title=title,
        height=height,
        labels={
            "novelty_score": "Novidade (0→1)",
            "relevance_score": "Relevância Cultural (0→1)",
            "circulo": "Círculo Cultural",
        },
    )

    fig.add_hline(y=0.5, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=0.5, line_dash="dash", line_color="gray", opacity=0.5)

    annotations = [
        dict(x=0.75, y=0.92, text="🔴 SINAIS FORTES", showarrow=False,
             font=dict(size=13, color="#D32F2F"), bgcolor="rgba(255,255,255,0.7)"),
        dict(x=0.75, y=0.08, text="🟡 EMERGENTES", showarrow=False,
             font=dict(size=12, color="#F57C00"), bgcolor="rgba(255,255,255,0.7)"),
        dict(x=0.25, y=0.92, text="🔵 ESTABELECIDOS", showarrow=False,
             font=dict(size=12, color="#1565C0"), bgcolor="rgba(255,255,255,0.7)"),
        dict(x=0.25, y=0.08, text="⚪ RUÍDO", showarrow=False,
             font=dict(size=12, color="#757575"), bgcolor="rgba(255,255,255,0.7)"),
    ]
    fig.update_layout(
        annotations=annotations,
        xaxis=dict(range=[-0.02, 1.02], dtick=0.25),
        yaxis=dict(range=[-0.02, 1.02], dtick=0.25),
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5
        ),
        plot_bgcolor="rgba(248,249,250,1)",
    )

    return fig


# ═══════════════════════════════════════════════════════════════════════════════
#  STANDALONE TEST (Plotly only, no Streamlit)
# ═══════════════════════════════════════════════════════════════════════════════

def _standalone_test():
    """Test quadrant computation without Streamlit."""
    import json, random

    print("=" * 65)
    print("  S3.6 — Signal Quadrant: module check")
    print("=" * 65)

    # Generate synthetic signals
    circles = list(CIRCLE_COLORS.keys())
    plats = ["YouTube", "Reddit", "Spotify", "NewsAPI", "rss_cultural"]
    signals = []
    for i in range(40):
        signals.append({
            "id": i + 1,
            "termo": f"termo_{i % 10}",
            "plataforma": random.choice(plats),
            "circulo": random.choice(circles),
            "score": round(random.uniform(0.1, 0.95), 3),
            "ts": (datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 72))).isoformat(),
            "raw_data": {
                "momentum": round(random.uniform(10, 95), 1),
                "volume": random.randint(1, 5000),
                "velocity": round(random.uniform(-50, 100), 2),
                "momentum_velocity": round(random.uniform(-20, 50), 2),
                "fonte_confiabilidade": random.choice(["ALTA", "MEDIA", "BAIXA"]),
                "circulo": random.choice(circles),
            },
        })

    df = prepare_quadrant_data(signals)

    print(f"\n  Signals:  {len(df)}")
    print(f"\n  Quadrant distribution:")
    for q, count in df["quadrant"].value_counts().items():
        print(f"    {q:20s}: {count}")

    print(f"\n  Novelty  — mean={df['novelty_score'].mean():.3f}, "
          f"std={df['novelty_score'].std():.3f}")
    print(f"  Relevance— mean={df['relevance_score'].mean():.3f}, "
          f"std={df['relevance_score'].std():.3f}")
    print(f"  Strength — mean={df['signal_strength'].mean():.3f}")

    print(f"\n  Sample (top 5 by strength):")
    top = df.nlargest(5, "signal_strength")
    for _, row in top.iterrows():
        print(
            f"    {row['termo']:15s} [{row['circulo']:12s}] "
            f"nov={row['novelty_score']:.3f} rel={row['relevance_score']:.3f} "
            f"str={row['signal_strength']:.3f} {row['quadrant']}"
        )

    ok = len(df) == 40 and not df["novelty_score"].isna().any()
    print(f"\n  {'✅' if ok else '❌'} Module loads OK — {len(df)} signals scored")
    return df


if __name__ == "__main__":
    _standalone_test()
