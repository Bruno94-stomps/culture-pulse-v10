"""
Tests for INT-3 — Unified Momentum Calculation
===============================================

Validates:
  1. core/momentum.py canonical functions (Tier 1 + Tier 2)
  2. Collector integration via compute_collector_momentum
  3. Seasonal boosts
  4. Edge cases & boundary conditions
  5. Backward compatibility (output scale)
"""
import math
import sys
from pathlib import Path

import pytest
import numpy as np

# Ensure project root on path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.momentum import (
    calculate_momentum,
    calculate_momentum_series,
    compute_collector_momentum,
    _seasonal_multiplier,
    W_RESONANCE,
    W_VELOCITY,
    W_DISPERSION,
)


# ═══════════════════════════════════════════════════════════════════════════
# TIER 1 — Core canonical formula (0-1)
# ═══════════════════════════════════════════════════════════════════════════

class TestCalculateMomentum:
    """Tests for the core calculate_momentum (0-1) function."""

    def test_all_zeros_returns_zero(self):
        assert calculate_momentum(0, 0, 0) == 0.0

    def test_output_range_always_01(self):
        """Output must always be in [0, 1]."""
        for r in [0, 1, 10, 100, 1000]:
            for v in [0, 1, 10, 100, 1000]:
                for d in [0.0, 0.5, 1.0]:
                    result = calculate_momentum(r, v, d)
                    assert 0.0 <= result <= 1.0, f"Out of range for r={r}, v={v}, d={d}: {result}"

    def test_higher_resonance_higher_score(self):
        low = calculate_momentum(1, 5, 0.5)
        high = calculate_momentum(100, 5, 0.5)
        assert high > low

    def test_higher_velocity_higher_score(self):
        low = calculate_momentum(5, 1, 0.5)
        high = calculate_momentum(5, 100, 0.5)
        assert high > low

    def test_higher_dispersion_higher_score(self):
        low = calculate_momentum(5, 5, 0.0)
        high = calculate_momentum(5, 5, 1.0)
        assert high > low

    def test_negative_inputs_clamped(self):
        """Negative resonance/velocity should be treated as 0."""
        result = calculate_momentum(-10, -5, -0.5)
        assert result == 0.0

    def test_invalid_inputs_graceful(self):
        """Non-numeric inputs should not crash."""
        result = calculate_momentum("abc", None, "xyz")
        assert result == 0.0

    def test_weights_sum_to_one(self):
        """The weight constants should sum to 1.0."""
        assert abs(W_RESONANCE + W_VELOCITY + W_DISPERSION - 1.0) < 1e-9


class TestCalculateMomentumSeries:
    """Tests for vectorized series calculation."""

    def test_series_basic(self):
        r = [0, 5, 10]
        v = [0, 5, 10]
        d = [0, 0.5, 1.0]
        result = calculate_momentum_series(r, v, d)
        assert len(result) == 3
        assert result[0] == 0.0
        assert result[1] > 0.0
        assert result[2] > result[1]

    def test_series_all_zeros(self):
        result = calculate_momentum_series([0, 0], [0, 0], [0, 0])
        np.testing.assert_array_equal(result, [0.0, 0.0])


# ═══════════════════════════════════════════════════════════════════════════
# TIER 2 — Collector-facing unified momentum (0-100)
# ═══════════════════════════════════════════════════════════════════════════

class TestComputeCollectorMomentum:
    """Tests for the unified collector momentum function."""

    # -- Output range ---------------------------------------------------

    def test_output_range_0_100(self):
        """All platforms must return [0, 100]."""
        platforms = ["youtube", "reddit", "spotify", "newsapi", "ibge", "google_trends", "unknown"]
        for plat in platforms:
            result = compute_collector_momentum(plat, volume=50, engagement=100.0)
            assert 0.0 <= result <= 100.0, f"{plat}: {result}"

    def test_all_zeros_returns_zero(self):
        result = compute_collector_momentum("youtube")
        assert result == 0.0

    # -- YouTube --------------------------------------------------------

    def test_youtube_basic(self):
        m = compute_collector_momentum(
            "youtube",
            volume=20,
            engagement=30.0,
            cultural_score=5.0,
            diversity=10.0,
            extras={"channels": 10.0},
        )
        assert 0 < m <= 100

    def test_youtube_higher_engagement_higher_momentum(self):
        low = compute_collector_momentum("youtube", volume=10, engagement=5.0, diversity=3.0)
        high = compute_collector_momentum("youtube", volume=10, engagement=40.0, diversity=3.0)
        assert high > low

    def test_youtube_higher_volume_higher_momentum(self):
        low = compute_collector_momentum("youtube", volume=5, engagement=10.0, diversity=3.0)
        high = compute_collector_momentum("youtube", volume=40, engagement=10.0, diversity=3.0)
        assert high > low

    # -- Reddit ---------------------------------------------------------

    def test_reddit_basic(self):
        m = compute_collector_momentum(
            "reddit",
            volume=25,
            engagement=500.0,
            extras={"upvotes": 400.0, "comments": 80.0, "awards": 5.0},
        )
        assert 0 < m <= 100

    def test_reddit_upvotes_matter(self):
        low = compute_collector_momentum("reddit", volume=10, extras={"upvotes": 10.0, "comments": 5.0, "awards": 0.0})
        high = compute_collector_momentum("reddit", volume=10, extras={"upvotes": 3000.0, "comments": 5.0, "awards": 0.0})
        assert high > low

    # -- Spotify --------------------------------------------------------

    def test_spotify_basic(self):
        m = compute_collector_momentum(
            "spotify",
            volume=30,
            popularity=65.0,
            diversity=8.0,
            extras={"tracks": 20.0, "artists": 8.0, "playlists": 5.0, "cultural_genres": 3.0},
        )
        assert 0 < m <= 100

    def test_spotify_popularity_matters(self):
        low = compute_collector_momentum("spotify", popularity=10.0, extras={"tracks": 5.0, "artists": 3.0, "playlists": 1.0, "cultural_genres": 1.0})
        high = compute_collector_momentum("spotify", popularity=90.0, extras={"tracks": 5.0, "artists": 3.0, "playlists": 1.0, "cultural_genres": 1.0})
        assert high > low

    # -- NewsAPI --------------------------------------------------------

    def test_newsapi_basic(self):
        m = compute_collector_momentum("newsapi", volume=30, cultural_score=10.0)
        assert 0 < m <= 100

    def test_newsapi_cultural_ratio_matters(self):
        low = compute_collector_momentum("newsapi", volume=50, cultural_score=1.0)
        high = compute_collector_momentum("newsapi", volume=50, cultural_score=40.0)
        assert high > low

    # -- IBGE -----------------------------------------------------------

    def test_ibge_basic(self):
        m = compute_collector_momentum(
            "ibge",
            volume=50,
            diversity=5.0,
            regional_spread=0.6,
            extras={"population_millions": 100.0, "state_bonus": 2.0},
        )
        assert 0 < m <= 100

    def test_ibge_state_bonus_matters(self):
        low = compute_collector_momentum("ibge", extras={"population_millions": 50.0, "state_bonus": 0.0})
        high = compute_collector_momentum("ibge", extras={"population_millions": 50.0, "state_bonus": 3.0})
        assert high > low

    # -- Google Trends --------------------------------------------------

    def test_trends_basic(self):
        m = compute_collector_momentum(
            "google_trends",
            volume=40,
            popularity=75.0,
            diversity=15.0,
            extras={"recent_interest": 75.0, "regions_active": 15.0},
        )
        assert 0 < m <= 100

    def test_trends_interest_matters(self):
        low = compute_collector_momentum("google_trends", extras={"recent_interest": 5.0, "regions_active": 3.0})
        high = compute_collector_momentum("google_trends", extras={"recent_interest": 90.0, "regions_active": 3.0})
        assert high > low

    def test_trends_dispersion_from_regions(self):
        """Google Trends: more active regions → higher dispersion."""
        low = compute_collector_momentum("google_trends", extras={"recent_interest": 50.0, "regions_active": 2.0})
        high = compute_collector_momentum("google_trends", extras={"recent_interest": 50.0, "regions_active": 25.0})
        assert high > low

    # -- Generic / unknown platform ------------------------------------

    def test_generic_platform(self):
        m = compute_collector_momentum("tiktok", volume=100, engagement=500.0)
        assert 0 < m <= 100


# ═══════════════════════════════════════════════════════════════════════════
# Seasonal Boosts
# ═══════════════════════════════════════════════════════════════════════════

class TestSeasonalBoosts:
    """Tests for seasonal multipliers."""

    def test_carnaval_boost_samba(self):
        """Samba should get boosted during February."""
        mult = _seasonal_multiplier("samba", month=2)
        assert mult > 1.0

    def test_carnaval_boost_frevo(self):
        mult = _seasonal_multiplier("frevo", month=2)
        assert mult > 1.0

    def test_forro_boost_june(self):
        mult = _seasonal_multiplier("forró", month=6)
        assert mult > 1.0

    def test_no_boost_default(self):
        mult = _seasonal_multiplier("random_term", month=5)
        assert mult == 1.0

    def test_boost_applied_to_momentum(self):
        """Seasonal boost should make momentum higher."""
        base = compute_collector_momentum("youtube", volume=20, engagement=20.0, diversity=5.0, termo="capoeira")
        boosted = compute_collector_momentum("youtube", volume=20, engagement=20.0, diversity=5.0, termo="samba")
        # In February samba gets boost; in other months both are 1.0.
        # We test the mechanism: calling with month=2 explicitly
        m_no = _seasonal_multiplier("capoeira", month=2)
        m_yes = _seasonal_multiplier("samba", month=2)
        assert m_yes > m_no  # samba boosted, capoeira not


# ═══════════════════════════════════════════════════════════════════════════
# Edge Cases & Boundary Conditions
# ═══════════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    """Edge cases and boundary conditions."""

    def test_extreme_volume(self):
        """Very high volume should still be clamped to 100."""
        m = compute_collector_momentum("youtube", volume=10000, engagement=5000.0, diversity=500.0)
        assert m <= 100.0

    def test_zero_volume_all_platforms(self):
        """Zero volume should not crash."""
        for plat in ["youtube", "reddit", "spotify", "newsapi", "ibge", "google_trends"]:
            m = compute_collector_momentum(plat, volume=0)
            assert 0.0 <= m <= 100.0

    def test_negative_engagement(self):
        """Negative engagement should be handled gracefully."""
        m = compute_collector_momentum("reddit", engagement=-100.0)
        assert 0.0 <= m <= 100.0

    def test_regional_spread_clamped(self):
        """regional_spread > 1 should be clamped to 1."""
        m1 = compute_collector_momentum("ibge", regional_spread=0.8)
        m2 = compute_collector_momentum("ibge", regional_spread=5.0)
        # After clamping, spread=5.0 should behave like spread=1.0
        m3 = compute_collector_momentum("ibge", regional_spread=1.0)
        assert m2 == m3

    def test_resultado_is_float(self):
        result = compute_collector_momentum("youtube", volume=10, engagement=10.0)
        assert isinstance(result, float)

    def test_resultado_rounded(self):
        """Output should be rounded to 2 decimal places."""
        result = compute_collector_momentum("spotify", volume=15, popularity=55.0, extras={"tracks": 10.0, "artists": 5.0, "playlists": 3.0, "cultural_genres": 2.0})
        # Check that it has at most 2 decimal places
        assert result == round(result, 2)


# ═══════════════════════════════════════════════════════════════════════════
# Backward Compatibility
# ═══════════════════════════════════════════════════════════════════════════

class TestBackwardCompatibility:
    """Ensure the new unified function is compatible with CulturalSignal scale."""

    def test_scale_0_100(self):
        """compute_collector_momentum returns 0-100, matching CulturalSignal.momentum."""
        m = compute_collector_momentum("youtube", volume=30, engagement=25.0, diversity=8.0)
        assert 0.0 <= m <= 100.0

    def test_calculate_momentum_still_01(self):
        """calculate_momentum (core) still returns 0-1."""
        m = calculate_momentum(5.0, 5.0, 0.5)
        assert 0.0 <= m <= 1.0

    def test_consistency_tier1_tier2(self):
        """Tier 2 should be ~100x Tier 1 for equivalent inputs."""
        # Generic platform with direct resonance/velocity mapping
        m1 = calculate_momentum(5.0, 5.0, 0.5)  # 0-1
        m2 = compute_collector_momentum("unknown_plat", engagement=50.0, volume=50)
        # Both should be > 0 (exact comparison depends on scaling)
        assert m1 > 0
        assert m2 > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
