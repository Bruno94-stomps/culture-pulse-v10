"""Engine wrapper for emerging profiles detection."""

from typing import Any, Dict, List

from .dashboard_data_bridge import derive_emerging_profiles


def detect_emerging_profiles(signals: List[Dict[str, Any]], top_n: int = 6) -> List[Dict[str, Any]]:
    """Detect emerging consumer profiles from enriched cultural signals."""
    return derive_emerging_profiles(signals, top_n=top_n)


def detect_profiles_quick(signals: List[Dict[str, Any]], top_n: int = 6) -> Dict[str, Any]:
    """Convenience wrapper returning a summary payload."""
    profiles = detect_emerging_profiles(signals, top_n=top_n)
    return {
        "total_profiles": len(profiles),
        "profiles": profiles,
        "top_profile": profiles[0] if profiles else None,
    }
