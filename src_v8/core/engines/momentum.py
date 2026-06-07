"""
Momentum utilities for Futurumã — INT-3 Unified Momentum
=========================================================

Provides the **single source of truth** for the project-wide `MOMENTUM`
metric used across pipelines and collectors.

Two tiers:
  1. ``calculate_momentum``  — core formula (0-1), downstream analysis
  2. ``compute_collector_momentum`` — collector-facing adapter (0-100)

All ad-hoc heuristics that previously lived inside each collector are
now routed through ``compute_collector_momentum``.

Outputs a 0-1 float (tier 1) or 0-100 float (tier 2).
"""
from __future__ import annotations

import logging
import math
from datetime import datetime
from typing import Any, Dict, Iterable, Optional

import numpy as np

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# TIER 1 — Core canonical formula (0-1)
# ═══════════════════════════════════════════════════════════════════════════

# Weights — single place to tune
W_RESONANCE = 0.40
W_VELOCITY = 0.40
W_DISPERSION = 0.20


def calculate_momentum(ressonancia: float, velocity: float, dispersion: float) -> float:
    """Calculate normalized MOMENTUM score from components.

    Args:
        ressonancia: engagement / reach (expected 0..inf, will be clipped)
        velocity: growth rate (e.g., relative change, can be >1)
        dispersion: geographic dispersion (0..1 where 1 is fully dispersed)

    Returns:
        momentum: float in [0, 1]

    Formula:
        momentum = clamp( W_R*norm(ressonancia) + W_V*norm(velocity) + W_D*dispersion )
    """
    try:
        r = float(ressonancia)
    except Exception:
        r = 0.0
    try:
        v = float(velocity)
    except Exception:
        v = 0.0
    try:
        d = float(dispersion)
    except Exception:
        d = 0.0

    r_norm = np.log1p(max(r, 0.0)) / 10.0
    v_norm = np.log1p(max(v, 0.0)) / 5.0
    d_clip = min(max(d, 0.0), 1.0)

    raw = W_RESONANCE * r_norm + W_VELOCITY * v_norm + W_DISPERSION * d_clip
    return float(min(max(raw, 0.0), 1.0))


def calculate_momentum_series(
    series_ressonancia: Iterable[float],
    series_velocity: Iterable[float],
    series_dispersion: Iterable[float],
):
    """Vectorized helper: compute momentum per-element for iterables.

    Returns a numpy array of momentum values.
    """
    r = np.array(list(series_ressonancia), dtype=float)
    v = np.array(list(series_velocity), dtype=float)
    d = np.array(list(series_dispersion), dtype=float)
    vec = np.vectorize(calculate_momentum)
    return vec(r, v, d)


# ═══════════════════════════════════════════════════════════════════════════
# TIER 2 — Collector-facing unified momentum (0-100)
# ═══════════════════════════════════════════════════════════════════════════
#
# Every collector passes its raw metrics through this single function.
# The mapping from platform-specific counters to the canonical
# (resonance, velocity_proxy, dispersion) triple is done here.
#
# This replaces the ad-hoc formulas that existed in data_collectors.py
# for YouTube, Reddit, Spotify, NewsAPI, IBGE, and Google Trends.
# ═══════════════════════════════════════════════════════════════════════════

# --- Platform normalization constants ──────────────────────────────────
# These ceilings prevent division by zero and keep the ratios sane.

_PLATFORM_CEILINGS: Dict[str, Dict[str, float]] = {
    "youtube": {
        "engagement_max": 50.0,     # max engagement points expected
        "volume_max": 50.0,         # max videos in a single query
        "channels_max": 20.0,       # max unique channels
    },
    "reddit": {
        "upvotes_max": 5000.0,
        "comments_max": 2000.0,
        "awards_max": 50.0,
        "posts_max": 100.0,
    },
    "spotify": {
        "tracks_max": 50.0,
        "artists_max": 20.0,
        "playlists_max": 20.0,
        "popularity_max": 100.0,
        "genres_max": 10.0,
    },
    "newsapi": {
        "articles_max": 100.0,
        "cultural_ratio_max": 1.0,
    },
    "ibge": {
        "population_millions_max": 220.0,  # Brazil total
    },
    "google_trends": {
        "interest_max": 100.0,
    },
}

# Seasonal boosts (month → { termos → multiplier })
_SEASONAL_BOOSTS: Dict[int, Dict[str, float]] = {
    1: {"samba": 1.15, "frevo": 1.15},
    2: {"samba": 1.20, "frevo": 1.20, "carnaval": 1.25},
    3: {"samba": 1.10, "frevo": 1.10},
    6: {"forró": 1.15, "festa junina": 1.15, "são joão": 1.15},
    7: {"forró": 1.10},
}


def _seasonal_multiplier(termo: str, month: Optional[int] = None) -> float:
    """Return seasonal boost multiplier for a given term and month."""
    if month is None:
        month = datetime.now().month
    boosts = _SEASONAL_BOOSTS.get(month, {})
    return boosts.get(termo.lower(), 1.0)


def compute_collector_momentum(
    platform: str,
    *,
    volume: int = 0,
    engagement: float = 0.0,
    cultural_score: float = 0.0,
    popularity: float = 0.0,
    diversity: float = 0.0,
    regional_spread: float = 0.0,
    termo: str = "",
    extras: Optional[Dict[str, Any]] = None,
) -> float:
    """Compute unified momentum for a CulturalSignal from any collector.

    This is the **single canonical function** that every collector must
    call. It maps platform-specific raw counters into the core
    (resonance, velocity_proxy, dispersion) triple, applies the
    canonical ``calculate_momentum`` formula, scales to 0-100,
    and applies seasonal boosts.

    Args:
        platform: 'youtube', 'reddit', 'spotify', 'newsapi', 'ibge',
                  'google_trends', or any string (falls back to generic).
        volume: number of items (videos, posts, tracks, articles, etc.)
        engagement: platform-specific engagement aggregate
                    (YouTube: title_quality+desc+cultural points;
                     Reddit: upvotes + comments + awards weighted;
                     Spotify: avg popularity;
                     NewsAPI: cultural_score;
                     Google Trends: recent interest 0-100)
        cultural_score: number of culturally relevant items found
        popularity: average popularity metric (Spotify, Trends)
        diversity: diversity count (unique channels, artists, genres,
                   regions, etc.)
        regional_spread: 0-1 geographic dispersion estimate
        termo: search term (used for seasonal boost)
        extras: dict with platform-specific fields (optional overrides)

    Returns:
        float: momentum score in [0, 100]
    """
    extras = extras or {}
    plat = platform.lower().replace(" ", "_")

    # ── Map to canonical triple ─────────────────────────────────
    resonance = 0.0
    velocity_proxy = 0.0
    dispersion = max(0.0, min(regional_spread, 1.0))

    if plat == "youtube":
        ceil = _PLATFORM_CEILINGS["youtube"]
        channels = float(extras.get("channels", diversity))
        # Resonance: engagement quality per video
        resonance = engagement / ceil["engagement_max"] * 10.0
        # Velocity proxy: volume + channel diversity
        velocity_proxy = (
            (volume / ceil["volume_max"]) * 5.0
            + (channels / ceil["channels_max"]) * 3.0
            + (cultural_score / max(volume, 1)) * 2.0
        )

    elif plat == "reddit":
        ceil = _PLATFORM_CEILINGS["reddit"]
        upvotes = float(extras.get("upvotes", engagement * 0.5))
        comments = float(extras.get("comments", engagement * 0.3))
        awards = float(extras.get("awards", engagement * 0.01))
        resonance = (upvotes / ceil["upvotes_max"]) * 8.0 + (awards / ceil["awards_max"]) * 2.0
        velocity_proxy = (
            (comments / ceil["comments_max"]) * 4.0
            + (volume / ceil["posts_max"]) * 4.0
        )

    elif plat == "spotify":
        ceil = _PLATFORM_CEILINGS["spotify"]
        tracks = float(extras.get("tracks", volume * 0.5))
        artists = float(extras.get("artists", diversity))
        playlists = float(extras.get("playlists", 0))
        genres_count = float(extras.get("cultural_genres", diversity))
        resonance = (
            (popularity / ceil["popularity_max"]) * 6.0
            + (genres_count / ceil["genres_max"]) * 2.0
        )
        velocity_proxy = (
            (tracks / ceil["tracks_max"]) * 3.0
            + (artists / ceil["artists_max"]) * 3.0
            + (playlists / ceil["playlists_max"]) * 2.0
        )

    elif plat == "newsapi":
        ceil = _PLATFORM_CEILINGS["newsapi"]
        articles = max(volume, 1)
        cultural_ratio = cultural_score / articles
        resonance = cultural_ratio * 8.0
        velocity_proxy = (articles / ceil["articles_max"]) * 8.0

    elif plat == "ibge":
        ceil = _PLATFORM_CEILINGS["ibge"]
        pop_millions = float(extras.get("population_millions", volume))
        state_bonus = float(extras.get("state_bonus", 0.0))
        resonance = (pop_millions / ceil["population_millions_max"]) * 6.0 + state_bonus
        velocity_proxy = diversity * 2.0  # number of states with data

    elif plat in ("google_trends", "trends"):
        ceil = _PLATFORM_CEILINGS["google_trends"]
        recent_interest = float(extras.get("recent_interest", popularity))
        regions_active = float(extras.get("regions_active", diversity))
        resonance = (recent_interest / ceil["interest_max"]) * 8.0
        velocity_proxy = regions_active * 0.5
        dispersion = min(regions_active / 27.0, 1.0)  # 27 Brazilian states

    else:
        # Generic fallback
        resonance = engagement / 10.0
        velocity_proxy = volume / 10.0

    # ── Apply core formula (returns 0-1) ────────────────────────
    momentum_01 = calculate_momentum(resonance, velocity_proxy, dispersion)

    # ── Scale to 0-100 ──────────────────────────────────────────
    momentum_100 = momentum_01 * 100.0

    # ── Seasonal boost ──────────────────────────────────────────
    if termo:
        momentum_100 *= _seasonal_multiplier(termo)

    # ── Clamp final ─────────────────────────────────────────────
    return round(min(100.0, max(0.0, momentum_100)), 2)
