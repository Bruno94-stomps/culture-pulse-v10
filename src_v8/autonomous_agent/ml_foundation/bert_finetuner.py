#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S3.3 │ P6 — BERTimbau Fine-Tuning para Domínio Cultural Brasileiro
Culture Pulse V9.0 — Sprint 3, Passo 3

PROBLEMA:
  O SemanticExpander opera BERTimbau em modo zero-shot — embeddings genéricos
  que não capturam distinções culturais finas. Termos como "pagode" e "sertanejo"
  ficam próximos no espaço genérico, mas culturalmente divergem bastante.

SOLUÇÃO:
  Fine-tuning supervisionado do BERTimbau usando Snorkel pseudo-labels (S2.1).
  O modelo adapta embeddings ao domínio cultural brasileiro, melhorando:
  - Classificação de círculos culturais
  - Qualidade das expansões semânticas (cosine similarity domain-aware)

ARQUITETURA:
  ┌──────────────────────────────────────────────────────────────────────┐
  │ Input: texto (termo + narrativa enriquecida)                        │
  │                                                                     │
  │ BERTimbau (ALL layers trainable, lr=2e-5)                           │
  │ └── CLS token → 768d domain-adapted representation                 │
  │ └── Classifier head: Linear(768→256→K)                              │
  │                                                                     │
  │ Output: circle class (7 Snorkel classes)                            │
  │ Loss: CrossEntropyLoss + label_smoothing=0.1                        │
  │                                                                     │
  │ DELIVERY:                                                           │
  │ 1. Fine-tuned BERTimbau (melhor para cosine similarity)             │
  │ 2. Classifier head (classificação direta)                           │
  │ 3. Domain embedder (semantic_expander.py replacement)               │
  └──────────────────────────────────────────────────────────────────────┘

DADOS:
  - Fonte: Supabase cultural_signals JOIN signal_labels
  - Labels: Snorkel 7 classes (MUSICA, GASTRONOMIA, MODA, TECNOLOGIA,
            JUVENTUDE, NATUREZA, FAMILIA)
  - N: 186 sinais, 155 high-confidence (>=0.7)
  - Texto: "termo. narrativa_enriquecida" (~312 chars médio)

CRITÉRIO DE ACEITE:
  F1 macro fine-tuned > F1 macro zero-shot em holdout
  (zero-shot = BERTimbau genérico + cosine vs protótipos de classe)

REFERÊNCIA:
  Devlin et al. (2019) — BERT: Pre-training of Deep Bidirectional Transformers
  Souza et al. (2020) — BERTimbau: Pretrained BERT Models for Brazilian Portuguese

USO:
  from core.bert_finetuner import (
      BERTimbauFinetuner, FinetuneDataset,
      prepare_finetune_data, finetune_bertimbau,
      save_finetuned_model, load_finetuned_model,
      extract_domain_embeddings, zero_shot_classify,
  )

Autor: Culture Pulse Team
Data: 2026-02-20
Sprint: S3.3 │ P6
"""

import json
import logging
import math
import os
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════
# LABEL SCHEMA — Snorkel 7-class (from S2.1)
# ═══════════════════════════════════════════════════════════════════════
SNORKEL_LABELS = [
    "MUSICA",
    "GASTRONOMIA",
    "MODA",
    "TECNOLOGIA",
    "JUVENTUDE",
    "NATUREZA",
    "FAMILIA",
]
SNORKEL2IDX = {lb: i for i, lb in enumerate(SNORKEL_LABELS)}
IDX2SNORKEL = {i: lb for lb, i in SNORKEL2IDX.items()}
NUM_SNORKEL_CLASSES = len(SNORKEL_LABELS)

# Protótipos textuais para zero-shot baseline (cosine vs label embeddings)
CIRCLE_PROTOTYPES = {
    "MUSICA": "música brasileira ritmo samba funk pagode sertanejo forró MPB axé",
    "GASTRONOMIA": "gastronomia culinária comida brasileira feijoada açaí tapioca tempero sabor",
    "MODA": "moda estilo design fashion roupas tendência visual arte vestuário",
    "TECNOLOGIA": "tecnologia digital inovação inteligência artificial startup app blockchain",
    "JUVENTUDE": "juventude jovens geração cultura urbana comportamento tendência futuro",
    "NATUREZA": "natureza sustentabilidade meio ambiente ecologia verde biodiversidade",
    "FAMILIA": "família tradição comunidade valores gerações laços união convivência",
}

MODEL_NAME = "neuralmind/bert-base-portuguese-cased"


# ═══════════════════════════════════════════════════════════════════════
# DATASET
# ═══════════════════════════════════════════════════════════════════════
try:
    import torch
    from torch.utils.data import Dataset, DataLoader
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    logger.warning("⚠️ PyTorch not available — fine-tuning disabled")


class FinetuneDataset:
    """
    Dataset for BERTimbau fine-tuning.

    V9.1 DYNAMIC PADDING: Stores raw texts + labels instead of pre-tokenised
    tensors. Tokenisation + padding happens per mini-batch in the collate_fn,
    padding only to the longest sequence in each batch (not to max_length).
    This reduces wasted compute by ~20-40% for short texts.
    """

    def __init__(
        self,
        texts: List[str],
        labels: "torch.Tensor",
        sample_weights: Optional["torch.Tensor"] = None,
    ):
        self.texts = texts
        self.labels = labels
        self.sample_weights = sample_weights  # Snorkel confidence as weight

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        item = {
            "text": self.texts[idx],
            "labels": self.labels[idx],
        }
        if self.sample_weights is not None:
            item["sample_weight"] = self.sample_weights[idx]
        return item


def make_dynamic_collate_fn(tokenizer, max_length: int = 128):
    """
    Creates a collate function that tokenises + pads dynamically per batch.

    Instead of padding every sample to max_length (128), this pads only to
    the longest sequence in the current mini-batch. For a batch where the
    longest text has 23 tokens, all samples are padded to 23 — not 128.

    Args:
        tokenizer: HuggingFace tokenizer (AutoTokenizer)
        max_length: upper bound for truncation (safety limit)

    Returns:
        collate_fn compatible with torch DataLoader
    """
    import torch

    def _collate(batch):
        texts = [item["text"] for item in batch]
        labels = torch.stack([item["labels"] for item in batch])

        enc = tokenizer(
            texts,
            padding="longest",       # pad to longest in THIS batch
            truncation=True,
            max_length=max_length,   # safety truncation limit
            return_tensors="pt",
        )

        result = {
            "input_ids": enc["input_ids"],
            "attention_mask": enc["attention_mask"],
            "labels": labels,
        }

        if "sample_weight" in batch[0]:
            weights = torch.stack([item["sample_weight"] for item in batch])
            result["sample_weight"] = weights

        return result

    return _collate


# ═══════════════════════════════════════════════════════════════════════
# MODEL
# ═══════════════════════════════════════════════════════════════════════

class BERTimbauFinetuner:
    """
    BERTimbau with a classification head for cultural circle detection.

    Two modes:
      1. classify(text) → predicted circle label
      2. embed(text)    → 768d domain-adapted embedding (for SemanticExpander)
    """

    def __init__(self, num_classes: int = NUM_SNORKEL_CLASSES, dropout: float = 0.3):
        if not HAS_TORCH:
            raise ImportError("PyTorch required for BERTimbauFinetuner")

        import torch.nn as nn
        from transformers import AutoModel

        self.num_classes = num_classes
        self.backbone = AutoModel.from_pretrained(MODEL_NAME)
        hidden = self.backbone.config.hidden_size  # 768

        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden, 256),
            nn.GELU(),
            nn.Dropout(dropout * 0.5),
            nn.Linear(256, num_classes),
        )

        # Move to parameter group
        self._all_params = list(self.backbone.parameters()) + list(self.classifier.parameters())

    # ── Forward ─────────────────────────────────────────────────────────
    def forward(self, input_ids, attention_mask):
        import torch
        outputs = self.backbone(input_ids=input_ids, attention_mask=attention_mask)
        cls_emb = outputs.last_hidden_state[:, 0, :]  # [B, 768]
        logits = self.classifier(cls_emb)              # [B, K]
        return logits, cls_emb

    def parameters(self):
        return self._all_params

    def train(self):
        self.backbone.train()
        self.classifier.train()

    def eval(self):
        self.backbone.eval()
        self.classifier.eval()

    def to(self, device):
        self.backbone = self.backbone.to(device)
        self.classifier = self.classifier.to(device)
        return self

    def state_dict(self):
        return {
            "backbone": self.backbone.state_dict(),
            "classifier": self.classifier.state_dict(),
        }

    def load_state_dict(self, sd):
        self.backbone.load_state_dict(sd["backbone"])
        self.classifier.load_state_dict(sd["classifier"])


# ═══════════════════════════════════════════════════════════════════════
# DATA PREPARATION
# ═══════════════════════════════════════════════════════════════════════

def prepare_finetune_data(
    signals: List[Dict],
    labels: List[Dict],
    min_confidence: float = 0.5,
    val_ratio: float = 0.15,
    max_len: int = 128,
) -> Tuple["FinetuneDataset", "FinetuneDataset", dict]:
    """
    V9.9: Integração com Contexto de Onboarding (User Intent).
    Adiciona o briefing do usuário como prefixo semântico para o treinamento,
    ensinando o BERTimbau a entender 'objetivos de negócio'.

    Prepare datasets from Supabase data.

    V9.1 DYNAMIC PADDING: No longer pre-tokenises. Stores raw texts and
    labels; tokenisation + dynamic padding happens per mini-batch via
    make_dynamic_collate_fn() in the DataLoader.

    Args:
        signals: cultural_signals rows (id, termo, raw_data)
        labels: signal_labels rows (signal_id, label, confidence)
        min_confidence: filter low-quality Snorkel labels
        val_ratio: fraction held out for validation
        max_len: max token length (BERTimbau) — used as truncation limit

    Returns:
        (train_ds, val_ds, info_dict)
    """
    import torch

    # Build signal lookup
    sig_map = {s["id"]: s for s in signals}

    # Filter labels by confidence & build (text, label, weight) tuples
    samples = []
    for lb in labels:
        if lb["label"] not in SNORKEL2IDX:
            continue
        if lb["confidence"] < min_confidence:
            continue
        sig = sig_map.get(lb["signal_id"])
        if not sig:
            continue

        raw = sig.get("raw_data") or {}
        # NOVO: Injetar o User Intent/Contexto de Onboarding se disponível
        # Isso ensina o modelo que 'Samba' pode ter sentidos diferentes para 'Marketing' vs 'Crise'
        user_intent = raw.get("user_intent_context", "Geral")
        narrative = raw.get("narrativa", raw.get("narrative", ""))
        
        # O modelo agora aprende a relação: [INTENT] -> Termo -> Narrativa
        text = f"[{user_intent}] {sig.get('termo', '')}. {narrative}".strip()
        
        if len(text) < 10:
            continue

        samples.append({
            "text": text,
            "label_idx": SNORKEL2IDX[lb["label"]],
            "label_name": lb["label"],
            "confidence": lb["confidence"],
        })

    if not samples:
        raise ValueError("No samples after filtering — check data/confidence threshold")

    # Shuffle deterministically
    rng = np.random.RandomState(42)
    rng.shuffle(samples)

    # Split
    n_val = max(1, int(len(samples) * val_ratio))
    val_samples = samples[:n_val]
    train_samples = samples[n_val:]

    def _build_dataset(ss):
        texts = [s["text"] for s in ss]
        label_t = torch.tensor([s["label_idx"] for s in ss], dtype=torch.long)
        weight_t = torch.tensor([s["confidence"] for s in ss], dtype=torch.float)
        return FinetuneDataset(texts, label_t, weight_t)

    train_ds = _build_dataset(train_samples)
    val_ds = _build_dataset(val_samples)

    # Class distribution
    train_dist = Counter(s["label_name"] for s in train_samples)
    val_dist = Counter(s["label_name"] for s in val_samples)

    info = {
        "n_total": len(samples),
        "n_train": len(train_samples),
        "n_val": len(val_samples),
        "min_confidence": min_confidence,
        "train_distribution": dict(train_dist.most_common()),
        "val_distribution": dict(val_dist.most_common()),
    }

    logger.info(f"✅ Prepared {info['n_train']} train + {info['n_val']} val samples")
    return train_ds, val_ds, info


# ═══════════════════════════════════════════════════════════════════════
# TRAINING
# ═══════════════════════════════════════════════════════════════════════

def finetune_bertimbau(
    train_ds: "FinetuneDataset",
    val_ds: "FinetuneDataset",
    num_epochs: int = 5,
    batch_size: int = 16,
    lr: float = 2e-5,
    warmup_ratio: float = 0.1,
    label_smoothing: float = 0.1,
    use_sample_weights: bool = True,
    patience: int = 3,
    max_len: int = 128,
) -> Tuple[BERTimbauFinetuner, Dict]:
    """
    Fine-tune BERTimbau for circle classification.

    V9.1 DYNAMIC PADDING: Uses make_dynamic_collate_fn() so each mini-batch
    is padded only to its longest sequence, not to max_len. Reduces wasted
    compute by ~20-40% for datasets with short cultural terms.

    Uses:
      - Dynamic padding per mini-batch (V9.1)
      - Linear warmup + cosine decay
      - Label smoothing (CrossEntropy)
      - Optional per-sample weighting (Snorkel confidence)
      - Early stopping on val F1

    Returns:
        (model, history)
    """
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader
    from transformers import AutoTokenizer

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"🖥️  Device: {device}")

    model = BERTimbauFinetuner(num_classes=NUM_SNORKEL_CLASSES)
    model.to(device)

    # Count params
    total_p = sum(p.numel() for p in model.parameters())
    train_p = sum(p.numel() for p in model.parameters() if p.requires_grad)
    logger.info(f"📊 Parameters: {total_p:,} total, {train_p:,} trainable ({100*train_p/total_p:.1f}%)")

    # Dynamic padding collate function
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    collate_fn = make_dynamic_collate_fn(tokenizer, max_length=max_len)
    logger.info(f"⚡ Dynamic padding enabled (truncation limit: {max_len})")

    # Optimiser: single lr for backbone+head (full fine-tune)
    optimiser = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)

    # Scheduler: linear warmup + cosine decay
    n_batches = math.ceil(len(train_ds) / batch_size)
    total_steps = n_batches * num_epochs
    warmup_steps = max(1, int(total_steps * warmup_ratio))

    def lr_lambda(step):
        if step < warmup_steps:
            return step / warmup_steps
        progress = (step - warmup_steps) / max(1, total_steps - warmup_steps)
        return 0.5 * (1.0 + math.cos(math.pi * progress))

    scheduler = torch.optim.lr_scheduler.LambdaLR(optimiser, lr_lambda)

    # Loss
    loss_fn = nn.CrossEntropyLoss(label_smoothing=label_smoothing, reduction="none")

    # Data loaders — collate_fn applies dynamic padding per batch
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, collate_fn=collate_fn)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, collate_fn=collate_fn)

    # Training loop
    history = {"train_loss": [], "val_loss": [], "val_f1": [], "val_acc": [], "lr": []}
    best_f1 = -1.0
    best_state = None
    no_improve = 0

    t0 = time.time()

    for epoch in range(1, num_epochs + 1):
        # ── Train ────────────────────────────────────────────────────
        model.train()
        epoch_loss = 0.0
        n_samples = 0

        for batch in train_loader:
            ids = batch["input_ids"].to(device)
            mask = batch["attention_mask"].to(device)
            labs = batch["labels"].to(device)
            weights = batch.get("sample_weight")

            logits, _ = model.forward(ids, mask)
            per_sample_loss = loss_fn(logits, labs)

            if use_sample_weights and weights is not None:
                w = weights.to(device)
                loss = (per_sample_loss * w).mean()
            else:
                loss = per_sample_loss.mean()

            optimiser.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimiser.step()
            scheduler.step()

            epoch_loss += loss.item() * ids.size(0)
            n_samples += ids.size(0)

        avg_train_loss = epoch_loss / max(1, n_samples)

        # ── Validate ─────────────────────────────────────────────────
        val_metrics = _evaluate(model, val_loader, loss_fn, device)

        history["train_loss"].append(avg_train_loss)
        history["val_loss"].append(val_metrics["loss"])
        history["val_f1"].append(val_metrics["f1_macro"])
        history["val_acc"].append(val_metrics["accuracy"])
        current_lr = scheduler.get_last_lr()[0]
        history["lr"].append(current_lr)

        logger.info(
            f"Epoch {epoch:2d}/{num_epochs} │ "
            f"train_loss={avg_train_loss:.4f} │ "
            f"val_loss={val_metrics['loss']:.4f} │ "
            f"val_F1={val_metrics['f1_macro']:.4f} │ "
            f"val_acc={val_metrics['accuracy']:.4f} │ "
            f"lr={current_lr:.2e}"
        )

        # Early stopping
        if val_metrics["f1_macro"] > best_f1:
            best_f1 = val_metrics["f1_macro"]
            best_state = {k: v.cpu().clone() if hasattr(v, "cpu") else v
                          for k, v in model.state_dict().items()}
            # deep copy state dicts
            import copy
            best_state = copy.deepcopy(model.state_dict())
            no_improve = 0
        else:
            no_improve += 1
            if no_improve >= patience:
                logger.info(f"⏹️  Early stop at epoch {epoch} (patience={patience})")
                break

    elapsed = time.time() - t0
    logger.info(f"⏱️  Training time: {elapsed:.1f}s")

    # Restore best
    if best_state is not None:
        model.load_state_dict(best_state)

    history["training_time_s"] = elapsed
    history["best_val_f1"] = best_f1
    history["stopped_epoch"] = epoch

    return model, history


def _evaluate(model, loader, loss_fn, device) -> Dict:
    """Evaluate model on a DataLoader, returning loss + metrics."""
    import torch

    model.eval()
    all_preds = []
    all_labels = []
    total_loss = 0.0
    n_samples = 0

    with torch.no_grad():
        for batch in loader:
            ids = batch["input_ids"].to(device)
            mask = batch["attention_mask"].to(device)
            labs = batch["labels"].to(device)

            logits, _ = model.forward(ids, mask)
            per_sample_loss = loss_fn(logits, labs)
            total_loss += per_sample_loss.sum().item()
            n_samples += ids.size(0)

            preds = logits.argmax(dim=-1).cpu().numpy()
            all_preds.extend(preds.tolist())
            all_labels.extend(labs.cpu().numpy().tolist())

    avg_loss = total_loss / max(1, n_samples)
    accuracy = sum(1 for p, l in zip(all_preds, all_labels) if p == l) / max(1, len(all_preds))

    # F1 macro
    from sklearn.metrics import f1_score, classification_report
    f1_macro = f1_score(all_labels, all_preds, average="macro", zero_division=0)

    # Per-class
    present_labels = sorted(set(all_labels) | set(all_preds))
    target_names = [IDX2SNORKEL.get(i, f"cls_{i}") for i in present_labels]
    report_str = classification_report(
        all_labels, all_preds,
        labels=present_labels,
        target_names=target_names,
        zero_division=0,
    )

    return {
        "loss": avg_loss,
        "accuracy": accuracy,
        "f1_macro": f1_macro,
        "predictions": all_preds,
        "labels": all_labels,
        "report": report_str,
    }


# ═══════════════════════════════════════════════════════════════════════
# ZERO-SHOT BASELINE (cosine similarity)
# ═══════════════════════════════════════════════════════════════════════

def zero_shot_classify(
    texts: List[str],
    labels: List[int],
    model_name: str = MODEL_NAME,
    max_len: int = 128,
) -> Dict:
    """
    Zero-shot baseline: embed texts & prototypes with generic BERTimbau,
    classify by nearest prototype (cosine similarity).

    Returns metrics dict.
    """
    import torch
    from transformers import AutoTokenizer, AutoModel
    from sklearn.metrics import f1_score, classification_report

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    model.eval()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    def _embed(text_list):
        enc = tokenizer(
            text_list, padding=True, truncation=True,
            max_length=max_len, return_tensors="pt",
        )
        with torch.no_grad():
            out = model(
                input_ids=enc["input_ids"].to(device),
                attention_mask=enc["attention_mask"].to(device),
            )
        return out.last_hidden_state[:, 0, :].cpu().numpy()  # [N, 768]

    # Embed prototypes
    proto_texts = [CIRCLE_PROTOTYPES[lb] for lb in SNORKEL_LABELS]
    proto_embs = _embed(proto_texts)  # [K, 768]

    # Embed input texts (batch of 32)
    all_embs = []
    for i in range(0, len(texts), 32):
        batch = texts[i : i + 32]
        embs = _embed(batch)
        all_embs.append(embs)
    all_embs = np.vstack(all_embs)  # [N, 768]

    # Cosine similarity → argmax
    from numpy.linalg import norm
    proto_norm = proto_embs / (norm(proto_embs, axis=1, keepdims=True) + 1e-9)
    text_norm = all_embs / (norm(all_embs, axis=1, keepdims=True) + 1e-9)
    sim = text_norm @ proto_norm.T  # [N, K]
    preds = sim.argmax(axis=1).tolist()

    accuracy = sum(1 for p, l in zip(preds, labels) if p == l) / max(1, len(preds))
    f1_macro = f1_score(labels, preds, average="macro", zero_division=0)

    present = sorted(set(labels) | set(preds))
    target_names = [IDX2SNORKEL.get(i, f"cls_{i}") for i in present]
    report = classification_report(
        labels, preds, labels=present,
        target_names=target_names, zero_division=0,
    )

    return {
        "method": "zero-shot cosine (generic BERTimbau)",
        "accuracy": accuracy,
        "f1_macro": f1_macro,
        "predictions": preds,
        "report": report,
    }


# ═══════════════════════════════════════════════════════════════════════
# DOMAIN EMBEDDING EXTRACTION
# ═══════════════════════════════════════════════════════════════════════

def extract_domain_embeddings(
    model: BERTimbauFinetuner,
    texts: List[str],
    max_len: int = 128,
    batch_size: int = 32,
) -> np.ndarray:
    """
    Extract domain-adapted 768d embeddings from fine-tuned backbone.

    These embeddings are the S3.3 deliverable that replaces generic
    BERTimbau embeddings in SemanticExpander.

    Returns:
        np.ndarray shape (N, 768)
    """
    import torch
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    device = next(model.backbone.parameters()).device

    model.eval()
    all_embs = []

    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i : i + batch_size]
        enc = tokenizer(
            batch_texts, padding=True, truncation=True,
            max_length=max_len, return_tensors="pt",
        )
        with torch.no_grad():
            _, cls_emb = model.forward(
                enc["input_ids"].to(device),
                enc["attention_mask"].to(device),
            )
        all_embs.append(cls_emb.cpu().numpy())

    return np.vstack(all_embs)


# ═══════════════════════════════════════════════════════════════════════
# SAVE / LOAD
# ═══════════════════════════════════════════════════════════════════════

def save_finetuned_model(
    model: BERTimbauFinetuner,
    history: Dict,
    output_dir: str = "models/bertimbau_cultural_v1",
) -> str:
    """Save fine-tuned model + training history."""
    import torch

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    torch.save(model.state_dict(), out / "finetuned_weights.pt")

    meta = {
        "model_name": MODEL_NAME,
        "num_classes": model.num_classes,
        "labels": SNORKEL_LABELS,
        "history": {k: v for k, v in history.items() if k != "best_state"},
        "saved_at": datetime.utcnow().isoformat(),
        "sprint": "S3.3",
    }
    with open(out / "training_metrics.json", "w") as f:
        json.dump(meta, f, indent=2, default=str)

    logger.info(f"💾 Model saved to {out}")
    return str(out)


def load_finetuned_model(
    model_dir: str = "models/bertimbau_cultural_v1",
) -> BERTimbauFinetuner:
    """Load a previously saved fine-tuned model."""
    import torch

    d = Path(model_dir)
    with open(d / "training_metrics.json") as f:
        meta = json.load(f)

    model = BERTimbauFinetuner(num_classes=meta["num_classes"])
    sd = torch.load(d / "finetuned_weights.pt", map_location="cpu")
    model.load_state_dict(sd)
    model.eval()

    logger.info(f"✅ Loaded fine-tuned model from {d} ({meta['num_classes']} classes)")
    return model


# ═══════════════════════════════════════════════════════════════════════
# STANDALONE TEST
# ═══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    print("=" * 65)
    print("  S3.3 — BERTimbau Fine-tuner: module check")
    print("=" * 65)
    print(f"  Labels: {NUM_SNORKEL_CLASSES} classes = {SNORKEL_LABELS}")
    print(f"  Model: {MODEL_NAME}")
    print(f"  PyTorch available: {HAS_TORCH}")
    if HAS_TORCH:
        m = BERTimbauFinetuner()
        total_p = sum(p.numel() for p in m.parameters())
        print(f"  Total params: {total_p:,}")
    print("  ✅ Module loads OK")
