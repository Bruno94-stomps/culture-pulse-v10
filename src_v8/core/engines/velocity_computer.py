#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S3.5 │ P8 + P15 — Velocity & Positional Features for CulturalSignal
Culture Pulse V9.0 — Sprint 3, Passo 5

PROBLEMA:
  P8  — Campos ausentes: CulturalSignal não tem campos de velocidade/aceleração
  P15 — Sem consciência temporal: sinais não sabem quanto tempo passou desde o
        último sinal do mesmo termo, nem se estão acelerando ou desacelerando.

SOLUÇÃO:
  Computar 5 novos campos para cada CulturalSignal:
    1. velocity:             delta_momentum / delta_t entre ciclos
    2. interaction_type:     share, comment, reaction, view (da plataforma)
    3. sequence_position:    rank ordinal no batch atual
    4. temporal_delta_hours: horas desde sinal anterior do mesmo termo
    5. momentum_velocity:    aceleração: d²momentum/dt² (2nd derivative)

ARQUITETURA:
  ┌──────────────────────────────────────────────────────────────────────┐
  │ Input: List[signal_dict] or List[CulturalSignal] (from batch/DB)    │
  │                                                                     │
  │ Step 1 — Sort by (termo, timestamp)                                 │
  │ Step 2 — For each signal:                                           │
  │   • temporal_delta = ts[i] - ts[i-1] for same termo                 │
  │   • velocity = (momentum[i] - momentum[i-1]) / delta_hours          │
  │   • momentum_velocity = (velocity[i] - velocity[i-1]) / delta_hours │
  │   • sequence_position = ordinal rank in current batch                │
  │   • interaction_type = infer from platform/volume patterns           │
  │                                                                     │
  │ Output: enriched signals with all 5 fields populated                 │
  └──────────────────────────────────────────────────────────────────────┘

CRITÉRIO DE ACEITE:
  CulturalSignal.velocity disponível e não-nulo em ≥80% dos sinais

USO:
  from core.velocity_computer import (
      VelocityComputer, compute_velocity_features,
      compute_velocity_from_supabase, backfill_velocity_supabase,
  )

Autor: Culture Pulse Team
Data: 2026-02-20
Sprint: S3.5 │ P8 + P15
"""

import json
import logging
import os
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ═══════════════════════════════════════════════════════════════════════
# INTERACTION TYPE INFERENCE
# ═══════════════════════════════════════════════════════════════════════

# Platform → dominant interaction type mapping
PLATFORM_INTERACTION_MAP = {
    "YouTube": "view",
    "Reddit": "comment",
    "Spotify": "view",           # streams ≈ views
    "NewsAPI": "view",           # article reads
    "Instagram/Threads": "reaction",  # likes/reactions
    "Meetup": "share",           # event RSVPs ≈ sharing
    "IBGE": "view",              # data access
    "internal": "view",
}

# Volume thresholds to refine interaction type
def infer_interaction_type(
    platform: str,
    volume: int = 0,
    momentum: float = 0.0,
) -> str:
    """
    Infer dominant interaction type from platform and engagement patterns.
    
    Returns one of: share, comment, reaction, view
    """
    base_type = PLATFORM_INTERACTION_MAP.get(platform, "view")
    
    # High volume + high momentum suggests sharing/viral behavior
    if volume > 100 and momentum > 70:
        return "share"
    
    # Medium engagement with moderate volume → reactions
    if volume > 50 and momentum > 40:
        if base_type == "view":
            return "reaction"
    
    return base_type


# ═══════════════════════════════════════════════════════════════════════
# VELOCITY COMPUTATION
# ═══════════════════════════════════════════════════════════════════════

class VelocityComputer:
    """
    Computes velocity and positional features for cultural signals.
    
    Designed to work with:
      1. In-memory lists of signal dicts (from collectors or Supabase)
      2. CulturalSignal dataclass instances (post-collection)
    """
    
    def __init__(self, min_delta_hours: float = 0.001):
        """
        Args:
            min_delta_hours: minimum time delta to avoid division by zero (≈3.6s)
        """
        self.min_delta_hours = min_delta_hours
    
    def compute(self, signals: List[Dict]) -> List[Dict]:
        """
        Compute all 5 velocity/positional features for a batch of signals.
        
        Signals must have: id, termo, plataforma, raw_data (with momentum, volume),
        and either ts or timestamp field.
        
        Returns:
            Same signals list with velocity fields added to raw_data.
        """
        if not signals:
            return signals
        
        # Group by termo for temporal computations
        by_termo = defaultdict(list)
        for i, s in enumerate(signals):
            by_termo[s.get("termo", "")].append((i, s))
        
        # Sort each group by timestamp
        for termo, group in by_termo.items():
            group.sort(key=lambda x: self._get_timestamp(x[1]))
        
        # Compute per-signal features
        prev_velocities = {}  # termo → last velocity (for acceleration)
        prev_momenta = {}     # termo → last momentum
        prev_timestamps = {}  # termo → last timestamp
        
        batch_position = 0
        
        for termo, group in sorted(by_termo.items()):
            for seq_in_termo, (idx, signal) in enumerate(group):
                raw = signal.get("raw_data", {})
                if isinstance(raw, str):
                    try:
                        raw = json.loads(raw)
                    except (json.JSONDecodeError, TypeError):
                        raw = {}
                
                current_ts = self._get_timestamp(signal)
                current_momentum = float(raw.get("momentum", 0.0) or 0.0)
                current_volume = int(raw.get("volume", 0) or 0)
                platform = signal.get("plataforma", "")
                
                # 1. sequence_position (ordinal rank in batch)
                batch_position += 1
                seq_pos = batch_position
                
                # 2. interaction_type
                int_type = infer_interaction_type(platform, current_volume, current_momentum)
                
                # 3. temporal_delta_hours
                if termo in prev_timestamps:
                    delta = (current_ts - prev_timestamps[termo]).total_seconds() / 3600.0
                    temporal_delta = max(delta, self.min_delta_hours)
                else:
                    temporal_delta = 0.0  # first signal of this termo
                
                # 4. velocity = delta_momentum / delta_t
                if termo in prev_momenta and temporal_delta > 0:
                    delta_momentum = current_momentum - prev_momenta[termo]
                    velocity = delta_momentum / temporal_delta
                else:
                    velocity = 0.0  # first signal — no previous to compare
                
                # 5. momentum_velocity (acceleration = d²momentum/dt²)
                if termo in prev_velocities and temporal_delta > 0:
                    delta_velocity = velocity - prev_velocities[termo]
                    accel = delta_velocity / temporal_delta
                else:
                    accel = 0.0
                
                # Store velocity fields in raw_data
                velocity_data = {
                    "velocity": round(velocity, 4),
                    "interaction_type": int_type,
                    "sequence_position": seq_pos,
                    "temporal_delta_hours": round(temporal_delta, 4),
                    "momentum_velocity": round(accel, 6),
                    "s35_version": "S3.5_v1",
                }
                
                # Merge into raw_data
                if isinstance(signal.get("raw_data"), dict):
                    signal["raw_data"].update(velocity_data)
                else:
                    signal["raw_data"] = velocity_data
                
                # Update tracking for next signal in this termo
                prev_timestamps[termo] = current_ts
                prev_momenta[termo] = current_momentum
                prev_velocities[termo] = velocity
                
                signals[idx] = signal
        
        return signals
    
    def _get_timestamp(self, signal: Dict) -> datetime:
        """Extract and parse timestamp from signal dict."""
        ts_str = signal.get("ts") or signal.get("timestamp") or ""
        
        if not ts_str:
            return datetime.now(timezone.utc)
        
        try:
            # Handle various ISO formats
            ts_str = str(ts_str).strip()
            if ts_str.endswith("Z"):
                ts_str = ts_str[:-1] + "+00:00"
            
            # Try parsing
            if "+" in ts_str or "-" in ts_str.split("T")[-1]:
                return datetime.fromisoformat(ts_str)
            else:
                return datetime.fromisoformat(ts_str).replace(tzinfo=timezone.utc)
        except (ValueError, AttributeError):
            return datetime.now(timezone.utc)
    
    def coverage_report(self, signals: List[Dict]) -> Dict[str, Any]:
        """
        Compute coverage statistics for velocity fields.
        
        Returns dict with field-level coverage percentages.
        """
        n = len(signals)
        if n == 0:
            return {"total": 0, "coverage": {}}
        
        fields = ["velocity", "interaction_type", "sequence_position",
                   "temporal_delta_hours", "momentum_velocity"]
        coverage = {}
        
        for f in fields:
            count = 0
            for s in signals:
                raw = s.get("raw_data", {})
                if isinstance(raw, str):
                    try:
                        raw = json.loads(raw)
                    except (json.JSONDecodeError, TypeError):
                        raw = {}
                val = raw.get(f)
                if val is not None:
                    count += 1
            coverage[f] = round(count / n * 100, 1)
        
        return {
            "total": n,
            "coverage": coverage,
            "min_coverage": min(coverage.values()) if coverage else 0.0,
            "all_above_80": all(v >= 80.0 for v in coverage.values()),
        }


# ═══════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def compute_velocity_features(signals: List[Dict]) -> List[Dict]:
    """Convenience wrapper: compute velocity for a list of signal dicts."""
    vc = VelocityComputer()
    return vc.compute(signals)


def compute_velocity_from_supabase(
    limit: int = 500,
    exclude_internal: bool = True,
) -> Tuple[List[Dict], Dict]:
    """
    Fetch signals from Supabase, compute velocity, return enriched signals + coverage.
    """
    import requests
    
    sb_url = os.environ.get("SUPABASE_URL", "https://wsizqmnnicpgblopmxyv.supabase.co")
    sb_key = os.environ.get("SUPABASE_SERVICE_KEY", os.environ.get("SUPABASE_KEY", ""))
    
    if not sb_key:
        raise ValueError("SUPABASE_SERVICE_KEY not set")
    
    headers = {"apikey": sb_key, "Authorization": f"Bearer {sb_key}"}
    params = {
        "select": "id,termo,plataforma,circulo,score,regiao,raw_data,ts",
        "limit": str(limit),
        "order": "id.asc",
    }
    if exclude_internal:
        params["plataforma"] = "neq.internal"
    
    resp = requests.get(f"{sb_url}/rest/v1/cultural_signals", headers=headers, params=params)
    resp.raise_for_status()
    signals = resp.json()
    
    logger.info(f"📥 Fetched {len(signals)} signals from Supabase")
    
    vc = VelocityComputer()
    enriched = vc.compute(signals)
    report = vc.coverage_report(enriched)
    
    return enriched, report


def backfill_velocity_supabase(
    dry_run: bool = True,
    limit: int = 500,
) -> Dict[str, Any]:
    """
    Backfill velocity features onto existing Supabase signals.
    
    Steps:
      1. Fetch all signals
      2. Compute velocity
      3. PATCH raw_data for each signal with velocity fields
    
    Returns:
        Dict with backfill statistics
    """
    import requests
    
    sb_url = os.environ.get("SUPABASE_URL", "https://wsizqmnnicpgblopmxyv.supabase.co")
    sb_key = os.environ.get("SUPABASE_SERVICE_KEY", os.environ.get("SUPABASE_KEY", ""))
    
    if not sb_key:
        raise ValueError("SUPABASE_SERVICE_KEY not set")
    
    headers = {
        "apikey": sb_key,
        "Authorization": f"Bearer {sb_key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }
    
    # Fetch
    enriched, report = compute_velocity_from_supabase(limit=limit)
    
    if dry_run:
        logger.info(f"🔍 DRY RUN: {len(enriched)} signals would be updated")
        logger.info(f"   Coverage: {report['coverage']}")
        return {
            "mode": "dry_run",
            "signals": len(enriched),
            "coverage": report["coverage"],
            "would_update": len(enriched),
        }
    
    # Patch each signal's raw_data
    updated = 0
    errors = 0
    
    for s in enriched:
        sig_id = s.get("id")
        if not sig_id:
            continue
        
        try:
            url = f"{sb_url}/rest/v1/cultural_signals?id=eq.{sig_id}"
            payload = {"raw_data": s["raw_data"]}
            resp = requests.patch(url, headers=headers, json=payload)
            
            if resp.status_code in (200, 204):
                updated += 1
            else:
                errors += 1
                if errors <= 3:
                    logger.warning(f"  ⚠️ ID {sig_id}: HTTP {resp.status_code}")
        except Exception as e:
            errors += 1
            if errors <= 3:
                logger.warning(f"  ⚠️ ID {sig_id}: {e}")
    
    logger.info(f"✅ Backfill complete: {updated} updated, {errors} errors")
    
    return {
        "mode": "live",
        "signals": len(enriched),
        "updated": updated,
        "errors": errors,
        "coverage": report["coverage"],
        "criterion_met": report["all_above_80"],
    }


# ═══════════════════════════════════════════════════════════════════════
# STANDALONE TEST
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    print("=" * 65)
    print("  S3.5 — Velocity Computer: module check")
    print("=" * 65)
    
    # Synthetic test
    from datetime import timedelta
    
    base_ts = datetime(2026, 2, 20, 10, 0, 0, tzinfo=timezone.utc)
    
    fake_signals = []
    termos = ["funk carioca", "deepfake"]
    plats = ["YouTube", "Reddit", "NewsAPI", "Spotify"]
    
    for i in range(20):
        termo = termos[i % len(termos)]
        ts = (base_ts + timedelta(hours=i * 2)).isoformat()
        fake_signals.append({
            "id": i + 1,
            "termo": termo,
            "plataforma": plats[i % len(plats)],
            "circulo": "teste",
            "score": 0.5,
            "ts": ts,
            "raw_data": {
                "momentum": float(30 + i * 3 + np.random.uniform(-5, 5)),
                "volume": int(10 + i * 2),
                "sentiment": 0.6,
            },
        })
    
    vc = VelocityComputer()
    enriched = vc.compute(fake_signals)
    report = vc.coverage_report(enriched)
    
    print(f"\n  Signals:    {len(enriched)}")
    print(f"  Coverage:   {report['coverage']}")
    print(f"  All ≥80%:   {report['all_above_80']}")
    
    # Show a few samples
    for s in enriched[:4]:
        raw = s["raw_data"]
        print(
            f"\n  ID={s['id']:2d} termo={s['termo']:<15s} plat={s['plataforma']:<12s}"
            f"\n    velocity={raw.get('velocity', '?'):>8} "
            f"int_type={raw.get('interaction_type', '?'):<10s} "
            f"seq={raw.get('sequence_position', '?'):>3} "
            f"delta_h={raw.get('temporal_delta_hours', '?'):>8} "
            f"accel={raw.get('momentum_velocity', '?'):>10}"
        )
    
    print(f"\n  ✅ Module loads OK — {len(enriched)} signals enriched")
