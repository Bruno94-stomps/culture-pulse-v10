#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S3.3 │ P6 — Training Pipeline: BERTimbau Fine-Tuning
Culture Pulse V9.0

PIPELINE:
  1. Fetch cultural_signals + signal_labels from Supabase
  2. Join → (text, Snorkel label, confidence)
  3. Zero-shot baseline (cosine vs prototypes)
  4. Fine-tune BERTimbau (5 epochs, all layers trainable)
  5. Compare fine-tuned vs zero-shot
  6. Extract domain embeddings & compute cosine quality improvement
  7. Save model to models/bertimbau_cultural_v1/
  8. Log results to Supabase

CRITÉRIO DE ACEITE:
  F1 macro fine-tuned > F1 macro zero-shot

USO:
  python scripts/train_finetune_bert.py
  python scripts/train_finetune_bert.py --epochs 10 --batch 8 --min-conf 0.7
"""

import argparse
import json
import logging
import os
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np
import requests

# ── Project root ──────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

# Direct import to avoid core/__init__.py (imports torch_geometric)
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "core.bert_finetuner", PROJECT_ROOT / "core" / "bert_finetuner.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

BERTimbauFinetuner = _mod.BERTimbauFinetuner
FinetuneDataset = _mod.FinetuneDataset
SNORKEL_LABELS = _mod.SNORKEL_LABELS
SNORKEL2IDX = _mod.SNORKEL2IDX
IDX2SNORKEL = _mod.IDX2SNORKEL
NUM_SNORKEL_CLASSES = _mod.NUM_SNORKEL_CLASSES
prepare_finetune_data = _mod.prepare_finetune_data
finetune_bertimbau = _mod.finetune_bertimbau
save_finetuned_model = _mod.save_finetuned_model
zero_shot_classify = _mod.zero_shot_classify
extract_domain_embeddings = _mod.extract_domain_embeddings

# ── Logging ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Supabase ─────────────────────────────────────────────────────────
SUPABASE_URL = "https://wsizqmnnicpgblopmxyv.supabase.co"
SUPABASE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndzaXpxbW5uaWNwZ2Jsb3BteHl2Iiwi"
    "cm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MTQ0MDExNiwiZXhwIjoyMDg3"
    "MDE2MTE2fQ.ca8oGhfR1Ek7t5n9fmCS3O5UaaCBUhqRAIJtavc5QpE"
)
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}


# ═══════════════════════════════════════════════════════════════════════
# FETCH DATA
# ═══════════════════════════════════════════════════════════════════════

def fetch_signals():
    """Fetch all cultural_signals from Supabase."""
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/cultural_signals?select=id,termo,circulo,plataforma,raw_data",
        headers=HEADERS,
    )
    r.raise_for_status()
    data = r.json()
    logger.info(f"📥 Fetched {len(data)} signals from Supabase")
    return data


def fetch_labels():
    """Fetch all signal_labels from Supabase."""
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/signal_labels?select=signal_id,label,confidence",
        headers=HEADERS,
    )
    r.raise_for_status()
    data = r.json()
    logger.info(f"📥 Fetched {len(data)} Snorkel labels from Supabase")
    return data


# ═══════════════════════════════════════════════════════════════════════
# BUILD TEXTS FOR ZERO-SHOT
# ═══════════════════════════════════════════════════════════════════════

def build_text_label_pairs(signals, labels, min_confidence=0.5):
    """
    Join signals + labels → list of (text, label_idx) for evaluation.
    """
    sig_map = {s["id"]: s for s in signals}
    pairs = []
    for lb in labels:
        if lb["label"] not in SNORKEL2IDX:
            continue
        if lb["confidence"] < min_confidence:
            continue
        sig = sig_map.get(lb["signal_id"])
        if not sig:
            continue
        raw = sig.get("raw_data") or {}
        narrative = raw.get("narrativa", raw.get("narrative", ""))
        text = f"{sig.get('termo', '')}. {narrative}".strip()
        if len(text) < 10:
            continue
        pairs.append((text, SNORKEL2IDX[lb["label"]]))
    return pairs


# ═══════════════════════════════════════════════════════════════════════
# LOG TO SUPABASE
# ═══════════════════════════════════════════════════════════════════════

def log_to_supabase(results: dict):
    """Log training results to signals_public table."""
    row = {
        "tipo": "model_training",
        "circulo": "bertimbau_finetune_s33",
        "termo": "bert_finetuner",
        "score": results.get("finetuned_f1", 0.0),
        "regiao": "global",
    }
    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/signals_public",
            headers=HEADERS,
            json=row,
        )
        if r.status_code in (200, 201):
            logger.info("📊 Results logged to Supabase ✅")
        else:
            logger.warning(f"⚠️  Supabase log HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        logger.warning(f"⚠️  Supabase log failed: {e}")


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="S3.3 — BERTimbau Fine-tuning")
    parser.add_argument("--epochs", type=int, default=5, help="Training epochs")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--lr", type=float, default=2e-5, help="Learning rate")
    parser.add_argument("--min-conf", type=float, default=0.5, help="Min Snorkel confidence")
    parser.add_argument("--patience", type=int, default=3, help="Early stopping patience")
    parser.add_argument("--label-smoothing", type=float, default=0.1, help="Label smoothing")
    parser.add_argument("--output-dir", type=str, default="models/bertimbau_cultural_v1")
    args = parser.parse_args()

    t_global = time.time()
    print("=" * 70)
    print("  S3.3 │ P6 — BERTimbau Fine-Tuning para Domínio Cultural")
    print("=" * 70)
    print(f"  Epochs: {args.epochs} │ Batch: {args.batch} │ LR: {args.lr}")
    print(f"  Min confidence: {args.min_conf} │ Patience: {args.patience}")
    print(f"  Label smoothing: {args.label_smoothing}")
    print(f"  Output: {args.output_dir}")
    print()

    # ── 1. Fetch data ────────────────────────────────────────────────
    print("─── STEP 1: Fetch data from Supabase ───")
    signals = fetch_signals()
    labels = fetch_labels()

    # ── 2. Build text/label pairs ────────────────────────────────────
    print("\n─── STEP 2: Build text-label pairs ───")
    pairs = build_text_label_pairs(signals, labels, min_confidence=args.min_conf)
    texts = [p[0] for p in pairs]
    label_idxs = [p[1] for p in pairs]
    dist = Counter(IDX2SNORKEL[l] for l in label_idxs)
    print(f"  Samples after filtering (conf≥{args.min_conf}): {len(pairs)}")
    for lb, ct in dist.most_common():
        print(f"    {lb:20s}  {ct}")

    # ── 3. Zero-shot baseline ────────────────────────────────────────
    print("\n─── STEP 3: Zero-shot baseline (generic BERTimbau + cosine) ───")
    zs_results = zero_shot_classify(texts, label_idxs)
    print(f"  Zero-shot Accuracy: {zs_results['accuracy']:.4f}")
    print(f"  Zero-shot F1 macro: {zs_results['f1_macro']:.4f}")
    print(f"\n  Classification Report (zero-shot):")
    for line in zs_results["report"].split("\n"):
        print(f"    {line}")

    # ── 4. Prepare datasets ──────────────────────────────────────────
    print("\n─── STEP 4: Prepare fine-tuning datasets ───")
    train_ds, val_ds, data_info = prepare_finetune_data(
        signals, labels,
        min_confidence=args.min_conf,
        val_ratio=0.15,
        max_len=128,
    )
    print(f"  Train: {data_info['n_train']} │ Val: {data_info['n_val']}")
    print(f"  Train dist: {data_info['train_distribution']}")
    print(f"  Val dist:   {data_info['val_distribution']}")

    # ── 5. Fine-tune ─────────────────────────────────────────────────
    print(f"\n─── STEP 5: Fine-tune BERTimbau ({args.epochs} epochs) ───")
    model, history = finetune_bertimbau(
        train_ds, val_ds,
        num_epochs=args.epochs,
        batch_size=args.batch,
        lr=args.lr,
        warmup_ratio=0.1,
        label_smoothing=args.label_smoothing,
        use_sample_weights=True,
        patience=args.patience,
    )

    # ── 6. Final evaluation on val set ───────────────────────────────
    print(f"\n─── STEP 6: Final evaluation ───")
    print(f"  Best val F1 macro: {history['best_val_f1']:.4f}")
    print(f"  Stopped at epoch:  {history['stopped_epoch']}")
    print(f"  Training time:     {history['training_time_s']:.1f}s")

    # Full evaluation on ALL data to compare fairly with zero-shot
    import torch
    from torch.utils.data import DataLoader
    import torch.nn as nn

    # Reprocess all data as val (no shuffle) for final comparison
    # FinetuneDataset already imported at top level
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained("neuralmind/bert-base-portuguese-cased")
    enc = tokenizer(texts, padding="max_length", truncation=True, max_length=128, return_tensors="pt")
    all_ds = FinetuneDataset(enc["input_ids"], enc["attention_mask"],
                             torch.tensor(label_idxs, dtype=torch.long))
    all_loader = DataLoader(all_ds, batch_size=args.batch, shuffle=False)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    all_preds = []
    with torch.no_grad():
        for batch in all_loader:
            logits, _ = model.forward(
                batch["input_ids"].to(device),
                batch["attention_mask"].to(device),
            )
            all_preds.extend(logits.argmax(dim=-1).cpu().tolist())

    from sklearn.metrics import f1_score, classification_report
    ft_f1 = f1_score(label_idxs, all_preds, average="macro", zero_division=0)
    ft_acc = sum(1 for p, l in zip(all_preds, label_idxs) if p == l) / len(all_preds)

    present = sorted(set(label_idxs) | set(all_preds))
    target_names = [IDX2SNORKEL.get(i, f"cls_{i}") for i in present]
    ft_report = classification_report(
        label_idxs, all_preds, labels=present,
        target_names=target_names, zero_division=0,
    )

    print(f"\n  Fine-tuned (full dataset) Accuracy: {ft_acc:.4f}")
    print(f"  Fine-tuned (full dataset) F1 macro: {ft_f1:.4f}")
    print(f"\n  Classification Report (fine-tuned):")
    for line in ft_report.split("\n"):
        print(f"    {line}")

    # ── 7. Comparison ────────────────────────────────────────────────
    print(f"\n─── STEP 7: COMPARISON ───")
    print(f"  ┌─────────────────┬───────────┬───────────┬──────────┐")
    print(f"  │ Metric          │ Zero-shot │ Fine-tuned│ Winner   │")
    print(f"  ├─────────────────┼───────────┼───────────┼──────────┤")

    zs_f1 = zs_results["f1_macro"]
    zs_acc = zs_results["accuracy"]

    def winner(a, b, a_name="ZS", b_name="FT"):
        if b > a + 0.001:
            return f"{b_name} ✅"
        elif a > b + 0.001:
            return f"{a_name}"
        return "TIE"

    f1_win = winner(zs_f1, ft_f1)
    acc_win = winner(zs_acc, ft_acc)

    print(f"  │ F1 macro        │  {zs_f1:.4f}  │  {ft_f1:.4f}  │ {f1_win:8s} │")
    print(f"  │ Accuracy        │  {zs_acc:.4f}  │  {ft_acc:.4f}  │ {acc_win:8s} │")
    print(f"  └─────────────────┴───────────┴───────────┴──────────┘")

    criterion_met = ft_f1 > zs_f1
    print()
    if criterion_met:
        print(f"  ✅ CRITÉRIO ATINGIDO: F1 fine-tuned ({ft_f1:.4f}) > zero-shot ({zs_f1:.4f})")
    else:
        print(f"  ❌ CRITÉRIO NÃO ATINGIDO: F1 fine-tuned ({ft_f1:.4f}) <= zero-shot ({zs_f1:.4f})")

    # ── 8. Domain embedding quality ──────────────────────────────────
    print(f"\n─── STEP 8: Domain embedding quality ───")
    domain_embs = extract_domain_embeddings(model, texts[:50])  # sample
    print(f"  Domain embeddings shape: {domain_embs.shape}")
    print(f"  Embedding norm mean: {np.linalg.norm(domain_embs, axis=1).mean():.4f}")

    # Intra-class vs inter-class cosine separation
    from numpy.linalg import norm as np_norm
    emb_norm = domain_embs / (np_norm(domain_embs, axis=1, keepdims=True) + 1e-9)
    sim_matrix = emb_norm @ emb_norm.T
    n_sample = min(50, len(label_idxs))
    sample_labels = label_idxs[:n_sample]

    intra_sims = []
    inter_sims = []
    for i in range(n_sample):
        for j in range(i + 1, n_sample):
            s = sim_matrix[i, j]
            if sample_labels[i] == sample_labels[j]:
                intra_sims.append(s)
            else:
                inter_sims.append(s)

    if intra_sims and inter_sims:
        intra_mean = np.mean(intra_sims)
        inter_mean = np.mean(inter_sims)
        separation = intra_mean - inter_mean
        print(f"  Intra-class cosine (same circle): {intra_mean:.4f}")
        print(f"  Inter-class cosine (diff circle): {inter_mean:.4f}")
        print(f"  Separation (intra - inter):       {separation:.4f}")
        if separation > 0:
            print(f"  ✅ Domain embeddings show class separation")
        else:
            print(f"  ⚠️  Domain embeddings have weak class separation")

    # ── 9. Save model ────────────────────────────────────────────────
    print(f"\n─── STEP 9: Save model ───")
    history["zero_shot_f1"] = zs_f1
    history["zero_shot_acc"] = zs_acc
    history["finetuned_f1_full"] = ft_f1
    history["finetuned_acc_full"] = ft_acc
    history["criterion_met"] = criterion_met

    saved_path = save_finetuned_model(model, history, output_dir=args.output_dir)
    print(f"  Saved to: {saved_path}")

    # ── 10. Log to Supabase ──────────────────────────────────────────
    print(f"\n─── STEP 10: Log to Supabase ───")
    log_to_supabase({
        "finetuned_f1": ft_f1,
        "zero_shot_f1": zs_f1,
        "criterion_met": criterion_met,
    })

    # ── Summary ──────────────────────────────────────────────────────
    elapsed = time.time() - t_global
    print(f"\n{'='*70}")
    print(f"  S3.3 COMPLETE — Total time: {elapsed:.1f}s")
    print(f"  Zero-shot F1: {zs_f1:.4f} → Fine-tuned F1: {ft_f1:.4f}")
    if criterion_met:
        delta = ft_f1 - zs_f1
        print(f"  ✅ IMPROVEMENT: +{delta:.4f} F1 ({delta/max(zs_f1,0.01)*100:.1f}%)")
    print(f"  Model: {saved_path}")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
