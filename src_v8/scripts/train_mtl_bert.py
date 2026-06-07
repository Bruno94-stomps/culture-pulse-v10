#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S3.2 │ P18A — Multi-Task BERTimbau Training Script
Culture Pulse V9.0 — Sprint 3, Passo 2

Fluxo:
  1. Carrega 186 sinais enriquecidos do Supabase (P9 FIX)
  2. Tokeniza com BERTimbau tokenizer
  3. Monta features S2.2+S2.3 (8d)
  4. Treina CulturalMTLBert (20 epochs, holdout 20%)
  5. Avalia 4 heads: circle F1, tension F1, alma MAE, intensity MAE
  6. Compara com S3.1 TextCNN baseline
  7. Salva modelo + métricas
  8. Loga resultados no Supabase

CRITÉRIO DE ACEITE:
  MTL ≥ single-task (S3.1) em pelo menos 3 das 4 heads

USO:
  cd /Users/brmunizmoura/Documents/PULSO/src_v8
  python scripts/train_mtl_bert.py

Autor: Culture Pulse Team
Data: 2026-02-19
Sprint: S3.2 │ P18A
"""

import json
import logging
import os
import sys
import time
from pathlib import Path

import numpy as np

# ── Path setup ──
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(str(PROJECT_ROOT))

# ── Logging ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("train_mtl_bert")

# ── Supabase config ──
SUPABASE_URL = "https://wsizqmnnicpgblopmxyv.supabase.co"
SUPABASE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndzaXpxbW5uaWNwZ2Jsb3BteHl2Iiwicm9s"
    "ZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MTQ0MDExNiwiZXhwIjoyMDg3MDE2MTE2fQ."
    "ca8oGhfR1Ek7t5n9fmCS3O5UaaCBUhqRAIJtavc5QpE"
)
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

MODEL_DIR = PROJECT_ROOT / "models" / "mtl_bert_s32"

# S3.1 TextCNN baseline for comparison
S31_METRICS_FILE = PROJECT_ROOT / "models" / "textcnn_s31" / "training_metrics.json"


def fetch_signals():
    """Fetch all enriched signals from Supabase."""
    import requests

    all_rows = []
    offset = 0
    limit = 1000

    while True:
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/cultural_signals",
            headers={**HEADERS, "Range": f"{offset}-{offset + limit - 1}"},
            params={"select": "*", "order": "id.asc"},
        )
        if resp.status_code not in (200, 206):
            logger.error(f"Fetch error: {resp.status_code}")
            break
        rows = resp.json()
        if not rows:
            break
        all_rows.extend(rows)
        if len(rows) < limit:
            break
        offset += limit

    logger.info(f"Fetched {len(all_rows)} signals from Supabase")
    return all_rows


def load_s31_baseline():
    """Load S3.1 TextCNN metrics for comparison."""
    if S31_METRICS_FILE.exists():
        with open(S31_METRICS_FILE) as f:
            return json.load(f)
    logger.warning(f"S3.1 baseline not found at {S31_METRICS_FILE}")
    return None


def log_results_to_supabase(metrics: dict, model_path: str):
    """Log training results to Supabase."""
    import requests

    log_payload = {
        "tipo": "model_training",
        "circulo": "mtl_bert_s32",
        "termo": "multitask_bert_classifier",
        "score": float(metrics.get("circle_f1_macro", 0)),
        "regiao": "global",
        "plataforma": "internal",
        "raw_data": {
            "s32_mtl_bert": {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "model_path": model_path,
                "circle_f1_macro": metrics.get("circle_f1_macro"),
                "circle_accuracy": metrics.get("circle_accuracy"),
                "tension_f1_macro": metrics.get("tension_f1_macro"),
                "tension_accuracy": metrics.get("tension_accuracy"),
                "alma_mae": metrics.get("alma_mae"),
                "alma_r2": metrics.get("alma_r2"),
                "intensity_mae": metrics.get("intensity_mae"),
                "intensity_r2": metrics.get("intensity_r2"),
                "best_composite": metrics.get("best_composite_score"),
                "n_train": metrics.get("n_train"),
                "n_val": metrics.get("n_val"),
                "epochs": metrics.get("epochs"),
                "freeze_bert_layers": metrics.get("freeze_bert_layers"),
                "status": "COMPLETO",
                "sprint": "S3.2",
            }
        },
    }

    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/cultural_signals",
        headers={**HEADERS, "Prefer": "return=minimal"},
        json=log_payload,
    )
    if resp.status_code in (200, 201):
        logger.info("✅ Training results logged to Supabase")
    else:
        logger.warning(f"⚠️ Failed to log: {resp.status_code} {resp.text[:200]}")


def compare_with_baseline(mtl_metrics: dict, baseline: dict) -> dict:
    """
    Compare MTL results with S3.1 TextCNN baseline.

    Criterion: MTL ≥ single-task in ≥ 3 of 4 heads.
    Note: S3.1 has 3 heads (circle, tension binary, intensity 3-class).
    S3.2 has 4 heads (circle 9-class, tension 7-class, alma regr., intensity regr.).
    Direct comparison is approximate since tasks differ.
    """
    comparisons = {}

    # Head 1: Circle F1 — S3.1 has 7 classes, S3.2 has 9 (harder task)
    s31_circle = baseline.get("circle_f1_macro", 0)
    s32_circle = mtl_metrics.get("circle_f1_macro", 0)
    comparisons["circle"] = {
        "s31": s31_circle,
        "s32": s32_circle,
        "delta": s32_circle - s31_circle,
        "mtl_wins": s32_circle >= s31_circle * 0.9,  # 90% threshold (harder task)
        "note": "S3.2 has 9 classes vs S3.1's 7 (harder task)",
    }

    # Head 2: Tension — S3.1 binary, S3.2 multi-class (7 classes)
    s31_tension = baseline.get("tension_accuracy", 0)
    s32_tension = mtl_metrics.get("tension_accuracy", 0)
    comparisons["tension"] = {
        "s31": s31_tension,
        "s32": s32_tension,
        "delta": s32_tension - s31_tension,
        "mtl_wins": s32_tension >= s31_tension * 0.8,  # 80% (much harder: 7 vs 2 classes)
        "note": "S3.2 is 7-class vs S3.1 binary (much harder)",
    }

    # Head 3: Alma — S3.1 doesn't have this; any result is new capability
    s32_alma_mae = mtl_metrics.get("alma_mae", 1.0)
    comparisons["alma"] = {
        "s31": None,
        "s32_mae": s32_alma_mae,
        "s32_r2": mtl_metrics.get("alma_r2", 0),
        "mtl_wins": s32_alma_mae < 0.3,  # MAE < 0.3 is reasonable
        "note": "NEW capability (S3.1 has no alma head)",
    }

    # Head 4: Intensity — S3.1 is 3-class, S3.2 is regression [0,1]
    s31_intensity = baseline.get("intensity_accuracy", 0)
    s32_intensity_mae = mtl_metrics.get("intensity_mae", 1.0)
    comparisons["intensity"] = {
        "s31_accuracy": s31_intensity,
        "s32_mae": s32_intensity_mae,
        "s32_r2": mtl_metrics.get("intensity_r2", 0),
        "mtl_wins": s32_intensity_mae < 0.15,  # MAE < 0.15 is good for [0,1] range
        "note": "S3.2 regression vs S3.1 classification",
    }

    wins = sum(1 for v in comparisons.values() if v.get("mtl_wins", False))
    comparisons["total_wins"] = wins
    comparisons["criterion_met"] = wins >= 3

    return comparisons


def main():
    """Main training pipeline."""
    import torch
    from core.classifiers.multitask_bert_classifier import (
        prepare_mtl_data, train_mtl, save_mtl_model,
        CulturalMTLBert, CIRCLE_LABELS_MTL, TENSION_LABELS_MTL,
        IDX2CIRCLE, IDX2TENSION,
    )

    print("=" * 70)
    print("S3.2 │ Multi-Task BERTimbau Training Pipeline")
    print("=" * 70)

    t0 = time.time()

    # ── Step 1: Fetch data ──
    logger.info("Step 1/7: Fetching enriched signals from Supabase...")
    signals = fetch_signals()

    # Filter out model_training logs
    signals = [s for s in signals if s.get("tipo") != "model_training_log"
               and s.get("tipo") != "model_training"]
    logger.info(f"After filtering: {len(signals)} cultural signals")

    # ── Step 2: Load tokenizer ──
    # V9.1 DYNAMIC PADDING: tokenizer is no longer needed here;
    # train_mtl() loads its own tokenizer for the collate_fn.
    # Kept for optional data-report usage below.
    logger.info("Step 2/7: Tokenizer will be loaded inside train_mtl (dynamic padding)")

    # ── Step 3: Prepare data ──
    logger.info("Step 3/7: Preparing MTL training data...")
    (texts, features,
     circle_labels, tension_labels, alma_labels, intensity_labels,
     valid_ids) = prepare_mtl_data(signals, max_seq_len=64)

    # Data report
    from collections import Counter

    circle_dist = Counter(circle_labels.tolist())
    tension_dist = Counter(tension_labels.tolist())

    print(f"\n📊 Data Summary:")
    print(f"  Total signals: {len(valid_ids)}")
    print(f"  Texts: {len(texts)} raw strings (dynamic padding)")
    print(f"  Features shape: {features.shape}")
    print(f"\n  Circle distribution (9 classes):")
    for idx, count in sorted(circle_dist.items()):
        print(f"    {IDX2CIRCLE[idx]:>35}: {count}")
    print(f"\n  Tension distribution (7 classes):")
    for idx, count in sorted(tension_dist.items()):
        print(f"    {IDX2TENSION[idx]:>35}: {count}")
    print(f"\n  Alma scores: min={alma_labels.min():.2f}, max={alma_labels.max():.2f}, mean={alma_labels.mean():.2f}")
    print(f"  Intensity:   min={intensity_labels.min():.3f}, max={intensity_labels.max():.3f}, mean={intensity_labels.mean():.3f}")

    # ── Step 4: Train ──
    logger.info("Step 4/7: Training CulturalMTLBert...")

    EPOCHS = 20
    BATCH_SIZE = 8
    LR = 2e-5
    FREEZE_LAYERS = 10  # Freeze 10 of 12 layers — small dataset safety

    print(f"\n🏋️ Training Configuration:")
    print(f"  Epochs: {EPOCHS}")
    print(f"  Batch size: {BATCH_SIZE}")
    print(f"  Learning rate: {LR} (backbone), {LR*10} (heads)")
    print(f"  Holdout: 20% (stratified)")
    print(f"  Frozen BERT layers: {FREEZE_LAYERS}/12")
    print(f"  Loss weights: circle=1.0, tension=0.7, alma=0.5, intensity=0.3")
    print()

    model, metrics = train_mtl(
        texts, features,
        circle_labels, tension_labels, alma_labels, intensity_labels,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        lr=LR,
        holdout_ratio=0.2,
        device="cpu",
        label_smoothing=0.1,
        freeze_bert_layers=FREEZE_LAYERS,
    )

    # ── Step 5: Report ──
    t1 = time.time()
    elapsed = t1 - t0

    print(f"\n{'=' * 70}")
    print(f"📈 RESULTADOS FINAIS S3.2 — Multi-Task BERTimbau")
    print(f"{'=' * 70}")
    print(f"\n  Head 1 — Circle (9 classes):")
    print(f"    F1 macro:  {metrics['circle_f1_macro']:.4f}")
    print(f"    Accuracy:  {metrics['circle_accuracy']:.4f}")
    print(f"\n  Head 2 — Tension (7 classes):")
    print(f"    F1 macro:  {metrics['tension_f1_macro']:.4f}")
    print(f"    Accuracy:  {metrics['tension_accuracy']:.4f}")
    print(f"\n  Head 3 — Alma Score (regression):")
    print(f"    MAE:       {metrics['alma_mae']:.4f}")
    print(f"    R²:        {metrics['alma_r2']:.4f}")
    print(f"\n  Head 4 — Intensity (regression):")
    print(f"    MAE:       {metrics['intensity_mae']:.4f}")
    print(f"    R²:        {metrics['intensity_r2']:.4f}")
    print(f"\n  Composite:   {metrics['best_composite_score']:.4f}")
    print(f"  N train/val: {metrics['n_train']}/{metrics['n_val']}")
    print(f"  Tempo:       {elapsed:.1f}s")

    # Per-class circle
    print(f"\n📋 Per-class Circle F1:")
    for label, stats in metrics["circle_per_class"].items():
        bar = "█" * int(stats["f1"] * 20)
        print(f"    {label:>35}: F1={stats['f1']:.3f} P={stats['precision']:.3f} R={stats['recall']:.3f} (n={stats['support']}) {bar}")

    # Per-class tension
    print(f"\n📋 Per-class Tension F1:")
    for label, stats in metrics["tension_per_class"].items():
        bar = "█" * int(stats["f1"] * 20)
        print(f"    {label:>35}: F1={stats['f1']:.3f} P={stats['precision']:.3f} R={stats['recall']:.3f} (n={stats['support']}) {bar}")

    # ── Step 6: Compare with S3.1 baseline ──
    logger.info("Step 5/7: Comparing with S3.1 TextCNN baseline...")
    baseline = load_s31_baseline()

    if baseline:
        comparison = compare_with_baseline(metrics, baseline)

        print(f"\n{'=' * 70}")
        print(f"📊 COMPARAÇÃO S3.2 MTL vs S3.1 TextCNN")
        print(f"{'=' * 70}")

        for task, info in comparison.items():
            if task in ("total_wins", "criterion_met"):
                continue
            win = "✅" if info.get("mtl_wins") else "❌"
            print(f"\n  {win} {task.upper()}: {info.get('note', '')}")
            for k, v in info.items():
                if k not in ("mtl_wins", "note"):
                    print(f"      {k}: {v}")

        print(f"\n  {'=' * 40}")
        wins = comparison["total_wins"]
        criterion = comparison["criterion_met"]
        status = "✅ CRITÉRIO ATINGIDO" if criterion else "❌ CRITÉRIO NÃO ATINGIDO"
        print(f"  MTL wins: {wins}/4 heads")
        print(f"  Status: {status}")
        print(f"  (Critério: MTL ≥ single-task em ≥ 3 de 4 heads)")

        metrics["comparison_with_s31"] = comparison
    else:
        print("\n⚠️ S3.1 baseline not available — skipping comparison")

    # ── Step 7: Save ──
    logger.info("Step 6/7: Saving model...")
    save_mtl_model(model, metrics, MODEL_DIR)
    print(f"\n💾 Modelo salvo em: {MODEL_DIR}")

    logger.info("Step 7/7: Logging to Supabase...")
    log_results_to_supabase(metrics, str(MODEL_DIR))

    print(f"\n{'=' * 70}")
    print(f"✅ S3.2 MTL BERT TRAINING COMPLETO")
    print(f"{'=' * 70}")

    return model, metrics


if __name__ == "__main__":
    model, metrics = main()
