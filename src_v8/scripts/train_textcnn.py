#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S3.1 │ P17 — TextCNN Training Script
Culture Pulse V9.0 — Sprint 3, Passo 1

Fluxo:
  1. Carrega 186 sinais + labels do Supabase
  2. Gera embeddings BERTimbau (768d)
  3. Monta features S2.2+S2.3 (8d)
  4. Treina CulturalTextCNN (50 epochs, holdout 20%)
  5. Avalia F1 macro (meta ≥ 0.65)
  6. Salva modelo + métricas
  7. Loga resultados no Supabase

USO:
  cd /Users/brmunizmoura/Documents/PULSO/src_v8
  python scripts/train_textcnn.py

Autor: Culture Pulse Team
Data: 2026-02-19
Sprint: S3.1 │ P17
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
logger = logging.getLogger("train_textcnn")

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

MODEL_DIR = PROJECT_ROOT / "models" / "textcnn_s31"


def fetch_signals():
    """Fetch all 186 signals from Supabase."""
    import requests
    url = f"{SUPABASE_URL}/rest/v1/cultural_signals?select=*&order=id.asc"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    signals = resp.json()
    logger.info(f"Fetched {len(signals)} signals from Supabase")
    return signals


def fetch_labels():
    """Fetch all Snorkel labels from Supabase."""
    import requests
    url = f"{SUPABASE_URL}/rest/v1/signal_labels?select=*&order=signal_id.asc"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    labels = resp.json()
    logger.info(f"Fetched {len(labels)} labels from Supabase")
    return labels


def load_bertimbau():
    """Load BERTimbau model + tokenizer."""
    from transformers import AutoTokenizer, AutoModel
    import torch

    logger.info("Loading BERTimbau (neuralmind/bert-base-portuguese-cased)...")
    tokenizer = AutoTokenizer.from_pretrained("neuralmind/bert-base-portuguese-cased")
    model = AutoModel.from_pretrained("neuralmind/bert-base-portuguese-cased")
    model.eval()
    logger.info(f"BERTimbau loaded. Device: cpu, Params: {sum(p.numel() for p in model.parameters()):,}")
    return model, tokenizer


def log_results_to_supabase(metrics: dict, model_path: str):
    """Log training results to Supabase drift_events-style table."""
    import requests
    from datetime import datetime

    payload = {
        "raw_data": {
            "s31_textcnn": {
                "timestamp": datetime.utcnow().isoformat(),
                "model_path": model_path,
                "circle_f1_macro": metrics.get("circle_f1_macro"),
                "circle_accuracy": metrics.get("circle_accuracy"),
                "intensity_accuracy": metrics.get("intensity_accuracy"),
                "tension_accuracy": metrics.get("tension_accuracy"),
                "best_epoch_f1": metrics.get("best_epoch_f1"),
                "n_train": metrics.get("n_train"),
                "n_val": metrics.get("n_val"),
                "per_class": metrics.get("circle_per_class"),
                "status": "COMPLETO",
                "sprint": "S3.1",
            }
        }
    }

    # Log as a special signal for auditing
    log_payload = {
        "tipo": "model_training",
        "circulo": "textcnn_s31",
        "termo": "neural_signal_classifier",
        "score": float(metrics.get("circle_f1_macro", 0)),
        "regiao": "global",
        "plataforma": "internal",
        "raw_data": payload["raw_data"],
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


def main():
    """Main training pipeline."""
    import torch
    from core.classifiers.neural_signal_classifier import (
        prepare_training_data,
        train_classifier,
        save_model,
        CulturalTextCNN,
        LABEL2IDX,
        IDX2LABEL,
    )

    print("=" * 70)
    print("S3.1 │ TextCNN Training Pipeline")
    print("=" * 70)

    t0 = time.time()

    # ── Step 1: Fetch data ──
    logger.info("Step 1/6: Fetching data from Supabase...")
    signals = fetch_signals()
    labels = fetch_labels()

    # ── Step 2: Load BERTimbau ──
    logger.info("Step 2/6: Loading BERTimbau...")
    bert_model, bert_tokenizer = load_bertimbau()

    # ── Step 3: Prepare training data ──
    logger.info("Step 3/6: Preparing training data...")
    embeddings, features, circle_labels, tension_labels, intensity_labels, valid_ids = (
        prepare_training_data(signals, labels, bert_model, bert_tokenizer)
    )

    # Data report
    from collections import Counter
    circle_dist = Counter(circle_labels.tolist())
    intensity_dist = Counter(intensity_labels.tolist())
    tension_dist = Counter(tension_labels.astype(int).tolist())

    print(f"\n📊 Data Summary:")
    print(f"  Signals: {len(valid_ids)}")
    print(f"  Embeddings shape: {embeddings.shape}")
    print(f"  Features shape: {features.shape}")
    print(f"  Circle distribution: {dict(sorted(circle_dist.items()))}")
    print(f"  Intensity distribution: {dict(sorted(intensity_dist.items()))}")
    print(f"  Tension distribution: {dict(sorted(tension_dist.items()))}")

    # Map circle indices to labels for readability
    circle_named = {IDX2LABEL[k]: v for k, v in circle_dist.items()}
    print(f"  Circle labels: {circle_named}")

    # ── Step 4: Train ──
    logger.info("Step 4/6: Training CulturalTextCNN v2 (token-level)...")
    print(f"\n🏋️ Training Configuration (v2 — Kim 2014 TextCNN):")
    print(f"  Epochs: 80")
    print(f"  Batch size: 16")
    print(f"  Learning rate: 5e-4")
    print(f"  Holdout: 20% (stratified)")
    print(f"  Dropout: 0.4")
    print(f"  Num filters: 128 per kernel")
    print(f"  Kernel sizes: [2, 3, 4]")
    print(f"  Label smoothing: 0.1")
    print(f"  Loss weights: circle=1.0, tension=0.3, intensity=0.5")
    print()

    model, metrics = train_classifier(
        embeddings, features,
        circle_labels, tension_labels, intensity_labels,
        epochs=80,
        batch_size=16,
        lr=5e-4,
        holdout_ratio=0.2,
        device="cpu",
        label_smoothing=0.1,
    )

    # ── Step 5: Report ──
    t1 = time.time()
    elapsed = t1 - t0

    print(f"\n{'=' * 70}")
    print(f"📈 RESULTADOS FINAIS S3.1 — TextCNN")
    print(f"{'=' * 70}")
    print(f"  Circle F1 macro:   {metrics['circle_f1_macro']:.4f}  (meta ≥ 0.65)")
    print(f"  Circle accuracy:   {metrics['circle_accuracy']:.4f}")
    print(f"  Intensity accuracy: {metrics['intensity_accuracy']:.4f}")
    print(f"  Tension accuracy:  {metrics['tension_accuracy']:.4f}")
    print(f"  Best epoch F1:     {metrics['best_epoch_f1']:.4f}")
    print(f"  N train / val:     {metrics['n_train']} / {metrics['n_val']}")
    print(f"  Tempo total:       {elapsed:.1f}s")

    f1 = metrics["circle_f1_macro"]
    if f1 >= 0.65:
        status = "✅ META ATINGIDA"
    elif f1 >= 0.50:
        status = "⚠️ ACEITÁVEL (abaixo da meta)"
    else:
        status = "❌ ABAIXO DO ESPERADO"
    print(f"\n  Status: {status}")

    print(f"\n📋 Per-class F1:")
    for label, stats in metrics["circle_per_class"].items():
        bar = "█" * int(stats["f1"] * 20)
        print(f"    {label:>15}: F1={stats['f1']:.3f} P={stats['precision']:.3f} R={stats['recall']:.3f} (n={stats['support']}) {bar}")

    # ── Step 6: Save ──
    logger.info("Step 5/6: Saving model...")
    save_model(model, metrics, MODEL_DIR)
    print(f"\n💾 Modelo salvo em: {MODEL_DIR}")

    logger.info("Step 6/6: Logging to Supabase...")
    log_results_to_supabase(metrics, str(MODEL_DIR))

    print(f"\n{'=' * 70}")
    print(f"✅ S3.1 TextCNN TRAINING COMPLETO")
    print(f"{'=' * 70}")

    return model, metrics


if __name__ == "__main__":
    model, metrics = main()
