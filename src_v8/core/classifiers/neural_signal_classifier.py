#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S3.1 │ P17 — TextCNN Neural Signal Classifier
Culture Pulse V9.0 — Sprint 3, Passo 1

PROBLEMA:
  Detecção de sinais é 100% TF-IDF + regras. Zero redes neurais no pipeline.

SOLUÇÃO:
  TextCNN sobre embeddings BERTimbau (768d) para classificação multi-output:
    Head 1: círculo cultural (7 classes do Snorkel)
    Head 2: tensão cultural (binário)
    Head 3: intensidade (baixa/média/alta)

ARQUITETURA:
  ┌──────────────────────────────────────────────────────────┐
  │  Input: BERTimbau CLS embedding (768d)                   │
  │  + S2.2/S2.3 features (8d) = 776d feature vector        │
  │                                                          │
  │  TextCNN Branch:                                         │
  │  ├── Conv1d(kernel=2) → ReLU → MaxPool → 64 filters     │
  │  ├── Conv1d(kernel=3) → ReLU → MaxPool → 64 filters     │
  │  └── Conv1d(kernel=4) → ReLU → MaxPool → 64 filters     │
  │  → Concatenate → 192d                                    │
  │                                                          │
  │  Feature Branch:                                         │
  │  └── Linear(8→32) → ReLU → 32d                          │
  │                                                          │
  │  Merged: 224d → Dropout(0.5)                             │
  │                                                          │
  │  Head 1: Linear(224→128→7)  → Softmax (círculo)         │
  │  Head 2: Linear(224→64→1)   → Sigmoid (tensão)          │
  │  Head 3: Linear(224→64→3)   → Softmax (intensidade)     │
  └──────────────────────────────────────────────────────────┘

  Pipeline Híbrido:
  TF-IDF filtra candidatos → TextCNN reclassifica top-K → output final

DADOS DE TREINO:
  186 sinais com pseudo-labels Snorkel (S2.1)
  7 classes: MUSICA(73), GASTRONOMIA(30), MODA(28), TECNOLOGIA(28),
             JUVENTUDE(14), NATUREZA(7), FAMILIA(6)
  Class weights para lidar com imbalance

USO:
  from core.classifiers.neural_signal_classifier import CulturalTextCNN, train_classifier

Autor: Culture Pulse Team
Data: 2026-02-19
Sprint: S3.1 │ P17
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
# LABEL MAPPING
# ═══════════════════════════════════════════════════════════════════════

# 7 Snorkel labels from S2.1
CIRCLE_LABELS = [
    "MUSICA",
    "GASTRONOMIA",
    "MODA",
    "TECNOLOGIA",
    "JUVENTUDE",
    "NATUREZA",
    "FAMILIA",
]
LABEL2IDX = {lb: i for i, lb in enumerate(CIRCLE_LABELS)}
IDX2LABEL = {i: lb for lb, i in LABEL2IDX.items()}
NUM_CIRCLES = len(CIRCLE_LABELS)

# Intensity mapping from S2.3 scaled_composite_score
INTENSITY_LABELS = ["baixa", "media", "alta"]
NUM_INTENSITIES = 3

# Tension: derived from enrichment data
NUM_TENSION = 1  # binary


# ═══════════════════════════════════════════════════════════════════════
# PYTORCH MODEL
# ═══════════════════════════════════════════════════════════════════════

import torch
import torch.nn as nn
import torch.nn.functional as F


class CulturalTextCNN(nn.Module):
    """
    Multi-output TextCNN for cultural signal classification.

    Architecture v2: Uses full BERTimbau token sequence (not just CLS).
    Conv1d slides over the token dimension with 768-channel embeddings,
    which is the canonical TextCNN design (Kim, 2014).

    Input:
      token_embeddings: (batch, seq_len, 768) — full BERTimbau output
      features: (batch, 8) — S2.2/S2.3 engineered features

    Outputs:
      circle_logits: (batch, 7) — cultural circle classification
      tension_logit: (batch, 1) — binary tension detection
      intensity_logits: (batch, 3) — signal intensity (low/med/high)

    Also supports CLS-only mode (768d) via cls_mode=True for inference
    when full token sequences are not available.
    """

    def __init__(
        self,
        embed_dim: int = 768,
        feature_dim: int = 8,
        num_circles: int = NUM_CIRCLES,
        num_intensities: int = NUM_INTENSITIES,
        num_filters: int = 128,
        kernel_sizes: Tuple[int, ...] = (2, 3, 4),
        dropout: float = 0.4,
    ):
        super().__init__()

        self.embed_dim = embed_dim
        self.feature_dim = feature_dim

        # ─── TextCNN branch (Kim 2014 style) ───
        # Conv1d: in_channels=embed_dim(768), slides over seq_len (tokens)
        self.convs = nn.ModuleList([
            nn.Conv1d(
                in_channels=embed_dim,
                out_channels=num_filters,
                kernel_size=k,
            )
            for k in kernel_sizes
        ])

        cnn_out_dim = num_filters * len(kernel_sizes)  # 384

        # ─── Feature branch ───
        self.feature_fc = nn.Sequential(
            nn.Linear(feature_dim, 64),
            nn.ReLU(),
            nn.BatchNorm1d(64),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
        )
        feat_out_dim = 32

        # ─── Merge ───
        merged_dim = cnn_out_dim + feat_out_dim  # 416
        self.dropout = nn.Dropout(dropout)
        self.bn_merged = nn.BatchNorm1d(merged_dim)

        # ─── Head 1: Circle classification (7 classes) ───
        self.circle_head = nn.Sequential(
            nn.Linear(merged_dim, 128),
            nn.ReLU(),
            nn.Dropout(dropout * 0.5),
            nn.Linear(128, num_circles),
        )

        # ─── Head 2: Tension detection (binary) ───
        self.tension_head = nn.Sequential(
            nn.Linear(merged_dim, 64),
            nn.ReLU(),
            nn.Dropout(dropout * 0.5),
            nn.Linear(64, 1),
        )

        # ─── Head 3: Intensity (3 classes) ───
        self.intensity_head = nn.Sequential(
            nn.Linear(merged_dim, 64),
            nn.ReLU(),
            nn.Dropout(dropout * 0.5),
            nn.Linear(64, num_intensities),
        )

    def forward(
        self,
        embeddings: torch.Tensor,    # (batch, seq_len, 768) or (batch, 768)
        features: torch.Tensor,       # (batch, 8)
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass.

        Args:
          embeddings: Token-level BERTimbau output (batch, seq_len, 768)
                      OR CLS-only (batch, 768) — auto-detected.
          features: Engineered features (batch, 8)

        Returns:
          circle_logits:    (batch, 7) raw logits
          tension_logit:    (batch, 1) raw logit (apply sigmoid)
          intensity_logits: (batch, 3) raw logits
        """
        # Handle CLS-only input: (batch, 768) → (batch, 1, 768)
        if embeddings.dim() == 2:
            embeddings = embeddings.unsqueeze(1)

        # Conv1d expects (batch, channels, seq_len)
        # embeddings is (batch, seq_len, 768) → transpose to (batch, 768, seq_len)
        x = embeddings.transpose(1, 2)

        # Apply convolutions + ReLU + global max pool
        conv_outs = []
        for conv in self.convs:
            c = F.relu(conv(x))              # (batch, num_filters, new_len)
            c = F.adaptive_max_pool1d(c, 1)  # (batch, num_filters, 1)
            c = c.squeeze(-1)                # (batch, num_filters)
            conv_outs.append(c)

        cnn_out = torch.cat(conv_outs, dim=1)  # (batch, 384)

        # Feature branch
        feat_out = self.feature_fc(features)    # (batch, 32)

        # Merge
        merged = torch.cat([cnn_out, feat_out], dim=1)  # (batch, 416)
        merged = self.bn_merged(merged)
        merged = self.dropout(merged)

        # Heads
        circle_logits = self.circle_head(merged)
        tension_logit = self.tension_head(merged)
        intensity_logits = self.intensity_head(merged)

        return circle_logits, tension_logit, intensity_logits

    def predict(
        self,
        embeddings: torch.Tensor,
        features: torch.Tensor,
    ) -> Dict[str, Any]:
        """
        Predict with human-readable output.

        Returns dict with:
          circle: str, circle_probs: list,
          tension: bool, tension_prob: float,
          intensity: str, intensity_probs: list
        """
        self.eval()
        with torch.no_grad():
            c_logits, t_logit, i_logits = self.forward(embeddings, features)

            c_probs = F.softmax(c_logits, dim=-1)
            t_prob = torch.sigmoid(t_logit)
            i_probs = F.softmax(i_logits, dim=-1)

            circle_idx = c_probs.argmax(dim=-1).item()
            intensity_idx = i_probs.argmax(dim=-1).item()

            return {
                "circle": IDX2LABEL[circle_idx],
                "circle_idx": circle_idx,
                "circle_probs": c_probs[0].tolist(),
                "tension": t_prob.item() > 0.5,
                "tension_prob": t_prob.item(),
                "intensity": INTENSITY_LABELS[intensity_idx],
                "intensity_idx": intensity_idx,
                "intensity_probs": i_probs[0].tolist(),
            }


# ═══════════════════════════════════════════════════════════════════════
# DATASET
# ═══════════════════════════════════════════════════════════════════════

class CulturalSignalDataset(torch.utils.data.Dataset):
    """
    Dataset for training CulturalTextCNN.

    Each sample:
      embedding: (seq_len, 768) BERTimbau token-level embeddings
      features: 8d S2.2+S2.3 engineered features
      circle_label: int (0-6)
      tension_label: float (0 or 1)
      intensity_label: int (0-2)
    """

    def __init__(
        self,
        embeddings: np.ndarray,    # (N, seq_len, 768)
        features: np.ndarray,      # (N, 8)
        circle_labels: np.ndarray,  # (N,) int
        tension_labels: np.ndarray, # (N,) float
        intensity_labels: np.ndarray,  # (N,) int
    ):
        self.embeddings = torch.FloatTensor(embeddings)
        self.features = torch.FloatTensor(features)
        self.circle_labels = torch.LongTensor(circle_labels)
        self.tension_labels = torch.FloatTensor(tension_labels)
        self.intensity_labels = torch.LongTensor(intensity_labels)

    def __len__(self):
        return len(self.embeddings)

    def __getitem__(self, idx):
        return {
            "embedding": self.embeddings[idx],
            "features": self.features[idx],
            "circle": self.circle_labels[idx],
            "tension": self.tension_labels[idx],
            "intensity": self.intensity_labels[idx],
        }


# ═══════════════════════════════════════════════════════════════════════
# DATA PREPARATION
# ═══════════════════════════════════════════════════════════════════════

FEATURE_COLUMNS = [
    "momentum_scaled", "volume_scaled", "sentiment_scaled", "score_scaled",
    "novelty_score", "signal_strength", "composite_rank_score", "ner_penalty",
]


def prepare_training_data(
    signals: List[dict],
    labels: List[dict],
    bertimbau_model=None,
    bertimbau_tokenizer=None,
    max_seq_len: int = 64,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, List[int]]:
    """
    Prepare training data from Supabase signals + Snorkel labels.

    Returns:
      embeddings: (N, max_seq_len, 768) — full token sequences, zero-padded
      features: (N, 8)
      circle_labels: (N,)
      tension_labels: (N,)
      intensity_labels: (N,)
      valid_ids: list of signal IDs included
    """
    # Build label lookup: signal_id → label info
    label_map = {}
    for l in labels:
        sid = l["signal_id"]
        if sid not in label_map or l.get("confidence", 0) > label_map[sid].get("confidence", 0):
            label_map[sid] = l

    # Generate BERTimbau embeddings if model provided
    if bertimbau_model is not None and bertimbau_tokenizer is not None:
        embeddings_cache = _generate_embeddings(signals, bertimbau_model, bertimbau_tokenizer, max_seq_len)
    else:
        embeddings_cache = {}

    all_embeddings = []
    all_features = []
    all_circles = []
    all_tensions = []
    all_intensities = []
    valid_ids = []

    for s in signals:
        sid = s["id"]
        if sid not in label_map:
            continue

        lbl = label_map[sid]["label"]
        if lbl not in LABEL2IDX:
            continue

        rd = s.get("raw_data", {}) or {}
        s22 = rd.get("s22_features", {}) or {}
        s23 = rd.get("s23_scaled", {}) or {}

        # ─── Embedding ───
        if sid in embeddings_cache:
            emb = embeddings_cache[sid]
        else:
            # Fallback: zero-padded random (not ideal)
            emb = np.zeros((max_seq_len, 768), dtype=np.float32)
            logger.warning(f"Signal {sid}: using zero embedding fallback")

        # ─── Engineered features (8d) ───
        feat = []
        for col in FEATURE_COLUMNS:
            val = s23.get(col) or s22.get(col)
            feat.append(float(val) if val is not None else 0.0)

        # ─── Circle label ───
        circle_idx = LABEL2IDX[lbl]

        # ─── Tension label ───
        # Derive from term semantics — political, social justice, inequality terms
        tension = _derive_tension_label(s, rd, lbl)

        # ─── Intensity label ───
        # Derive from scaled_composite_score (S2.3)
        composite = s23.get("scaled_composite_score", 0.5)
        if composite is None:
            composite = 0.5

        if composite >= 0.55:
            intensity = 2  # alta
        elif composite >= 0.40:
            intensity = 1  # media
        else:
            intensity = 0  # baixa

        all_embeddings.append(emb)
        all_features.append(feat)
        all_circles.append(circle_idx)
        all_tensions.append(tension)
        all_intensities.append(intensity)
        valid_ids.append(sid)

    return (
        np.array(all_embeddings, dtype=np.float32),
        np.array(all_features, dtype=np.float32),
        np.array(all_circles, dtype=np.int64),
        np.array(all_tensions, dtype=np.float32),
        np.array(all_intensities, dtype=np.int64),
        valid_ids,
    )


# Tension keywords for heuristic labeling
_TENSION_KEYWORDS = {
    "fake news", "deepfake", "ativismo", "desigualdade", "burnout",
    "protesto", "crise", "conflito", "racismo", "machismo",
    "cancelamento", "polariza", "censura", "preconceito", "violência",
    "discrimina", "corrupção", "injustiça", "exploração", "opressão",
    "lgbtq", "feminismo", "milícia", "tráfico", "genocídio",
    "favelização", "gentrificação", "colonialismo", "imperialismo",
}


def _derive_tension_label(signal: dict, raw_data: dict, snorkel_label: str) -> float:
    """
    Derive tension label from signal content using multiple heuristics.

    Returns 0.0 or 1.0 for binary tension.
    """
    # 1. Check term content for tension keywords
    termo = (signal.get("termo", "") or "").lower()
    expl = str(raw_data.get("explicacao", "") or "").lower()
    text = f"{termo} {expl}"

    for kw in _TENSION_KEYWORDS:
        if kw in text:
            return 1.0

    # 2. Snorkel-label heuristic: FAMILIA and JUVENTUDE circles
    #    often involve generational/social tension
    if snorkel_label in ("FAMILIA", "JUVENTUDE"):
        return 1.0

    # 3. Sentiment extremes indicate tension
    s22 = raw_data.get("s22_features", {}) or {}
    sentiment = s22.get("sentiment_scaled")
    if sentiment is not None:
        if float(sentiment) < -0.5:
            return 1.0

    # 4. High novelty + political/behavioral circle
    circulo = (signal.get("circulo", "") or "").lower()
    if circulo in ("política", "comportamento"):
        return 1.0

    return 0.0


def _generate_embeddings(
    signals: List[dict], model, tokenizer, max_seq_len: int = 64
) -> Dict[int, np.ndarray]:
    """
    Generate BERTimbau token-level embeddings for all signals.

    Returns dict of signal_id → (max_seq_len, 768) padded arrays.
    """
    import torch

    model.eval()
    cache = {}

    for s in signals:
        sid = s["id"]
        rd = s.get("raw_data", {}) or {}

        # Build text: termo + explicacao
        text = s.get("termo", "")
        expl = str(rd.get("explicacao", ""))
        if expl and expl != "None":
            text = f"{text}. {expl}"
        text = text[:512]  # Limit length

        inputs = tokenizer(
            text,
            return_tensors="pt",
            padding="max_length",
            truncation=True,
            max_length=max_seq_len,
        )

        with torch.no_grad():
            outputs = model(**inputs)
            # Full token sequence: (1, seq_len, 768) → (seq_len, 768)
            emb = outputs.last_hidden_state.squeeze(0).numpy()

        # Ensure consistent shape
        if emb.shape[0] < max_seq_len:
            pad = np.zeros((max_seq_len - emb.shape[0], 768), dtype=np.float32)
            emb = np.vstack([emb, pad])
        elif emb.shape[0] > max_seq_len:
            emb = emb[:max_seq_len]

        cache[sid] = emb.astype(np.float32)

    logger.info(f"Generated {len(cache)} BERTimbau token-level embeddings (seq_len={max_seq_len})")
    return cache


# ═══════════════════════════════════════════════════════════════════════
# TRAINING
# ═══════════════════════════════════════════════════════════════════════

def compute_class_weights(labels: np.ndarray, num_classes: int) -> torch.Tensor:
    """Compute inverse-frequency class weights for imbalanced data."""
    counts = Counter(labels.tolist())
    total = sum(counts.values())
    weights = []
    for i in range(num_classes):
        c = counts.get(i, 1)
        weights.append(total / (num_classes * c))
    return torch.FloatTensor(weights)


def train_classifier(
    embeddings: np.ndarray,
    features: np.ndarray,
    circle_labels: np.ndarray,
    tension_labels: np.ndarray,
    intensity_labels: np.ndarray,
    epochs: int = 80,
    batch_size: int = 16,
    lr: float = 5e-4,
    holdout_ratio: float = 0.2,
    device: str = "cpu",
    label_smoothing: float = 0.1,
) -> Tuple["CulturalTextCNN", Dict[str, Any]]:
    """
    Train CulturalTextCNN on prepared data.

    Returns:
      model: trained CulturalTextCNN
      metrics: dict with training history + evaluation metrics
    """
    N = len(embeddings)

    # ─── Stratified Train/val split ───
    # Group by circle label for stratified split
    np.random.seed(42)
    train_indices = []
    val_indices = []
    for c in range(NUM_CIRCLES):
        c_idx = np.where(circle_labels == c)[0]
        np.random.shuffle(c_idx)
        split = max(1, int(len(c_idx) * (1 - holdout_ratio)))
        train_indices.extend(c_idx[:split].tolist())
        val_indices.extend(c_idx[split:].tolist())

    train_idx = np.array(train_indices)
    val_idx = np.array(val_indices)
    np.random.shuffle(train_idx)
    np.random.shuffle(val_idx)

    train_ds = CulturalSignalDataset(
        embeddings[train_idx], features[train_idx],
        circle_labels[train_idx], tension_labels[train_idx],
        intensity_labels[train_idx],
    )
    val_ds = CulturalSignalDataset(
        embeddings[val_idx], features[val_idx],
        circle_labels[val_idx], tension_labels[val_idx],
        intensity_labels[val_idx],
    )

    train_loader = torch.utils.data.DataLoader(
        train_ds, batch_size=batch_size, shuffle=True, drop_last=False
    )
    val_loader = torch.utils.data.DataLoader(val_ds, batch_size=batch_size)

    # Determine embedding dimensions
    feat_dim = features.shape[1]

    # ─── Model ───
    model = CulturalTextCNN(
        embed_dim=768,
        feature_dim=feat_dim,
        num_circles=NUM_CIRCLES,
        num_intensities=NUM_INTENSITIES,
        num_filters=128,
        kernel_sizes=(2, 3, 4),
        dropout=0.4,
    ).to(device)

    # ─── Loss functions with class weights + label smoothing ───
    circle_weights = compute_class_weights(circle_labels[train_idx], NUM_CIRCLES).to(device)
    intensity_weights = compute_class_weights(intensity_labels[train_idx], NUM_INTENSITIES).to(device)

    circle_loss_fn = nn.CrossEntropyLoss(weight=circle_weights, label_smoothing=label_smoothing)
    tension_loss_fn = nn.BCEWithLogitsLoss()
    intensity_loss_fn = nn.CrossEntropyLoss(weight=intensity_weights, label_smoothing=label_smoothing)

    # Loss weights (circle is primary task)
    loss_weights = {"circle": 1.0, "tension": 0.3, "intensity": 0.5}

    # ─── Optimizer ───
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)

    # Warmup + cosine annealing
    warmup_epochs = 5
    def lr_lambda(epoch):
        if epoch < warmup_epochs:
            return (epoch + 1) / warmup_epochs
        progress = (epoch - warmup_epochs) / max(1, epochs - warmup_epochs)
        return 0.5 * (1 + math.cos(math.pi * progress))

    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)

    # ─── Training loop ───
    history = {"train_loss": [], "val_loss": [], "val_circle_f1": [], "val_circle_acc": []}
    best_val_f1 = 0.0
    best_model_state = None

    logger.info(f"Training: {len(train_ds)} train, {len(val_ds)} val, {epochs} epochs")
    logger.info(f"Circle weights: {circle_weights.tolist()}")

    for epoch in range(epochs):
        # ── Train ──
        model.train()
        train_losses = []

        for batch in train_loader:
            emb = batch["embedding"].to(device)
            feat = batch["features"].to(device)
            c_label = batch["circle"].to(device)
            t_label = batch["tension"].to(device)
            i_label = batch["intensity"].to(device)

            c_logits, t_logit, i_logits = model(emb, feat)

            loss_c = circle_loss_fn(c_logits, c_label) * loss_weights["circle"]
            loss_t = tension_loss_fn(t_logit.squeeze(), t_label) * loss_weights["tension"]
            loss_i = intensity_loss_fn(i_logits, i_label) * loss_weights["intensity"]

            loss = loss_c + loss_t + loss_i

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            train_losses.append(loss.item())

        scheduler.step()

        # ── Validate ──
        model.eval()
        val_losses = []
        all_c_preds = []
        all_c_true = []
        all_i_preds = []
        all_i_true = []
        all_t_preds = []
        all_t_true = []

        with torch.no_grad():
            for batch in val_loader:
                emb = batch["embedding"].to(device)
                feat = batch["features"].to(device)
                c_label = batch["circle"].to(device)
                t_label = batch["tension"].to(device)
                i_label = batch["intensity"].to(device)

                c_logits, t_logit, i_logits = model(emb, feat)

                loss_c = circle_loss_fn(c_logits, c_label)
                loss_t = tension_loss_fn(t_logit.squeeze(), t_label)
                loss_i = intensity_loss_fn(i_logits, i_label)
                val_losses.append((loss_c + loss_t + loss_i).item())

                all_c_preds.extend(c_logits.argmax(dim=1).cpu().tolist())
                all_c_true.extend(c_label.cpu().tolist())
                all_i_preds.extend(i_logits.argmax(dim=1).cpu().tolist())
                all_i_true.extend(i_label.cpu().tolist())
                all_t_preds.extend((torch.sigmoid(t_logit) > 0.5).int().squeeze().cpu().tolist())
                all_t_true.extend(t_label.int().cpu().tolist())

        # Metrics
        circle_acc = sum(p == t for p, t in zip(all_c_preds, all_c_true)) / len(all_c_true)
        circle_f1 = _f1_macro(all_c_true, all_c_preds, NUM_CIRCLES)
        intensity_acc = sum(p == t for p, t in zip(all_i_preds, all_i_true)) / len(all_i_true) if all_i_true else 0
        tension_acc = sum(p == t for p, t in zip(all_t_preds, all_t_true)) / len(all_t_true) if all_t_true else 0

        avg_train = sum(train_losses) / len(train_losses)
        avg_val = sum(val_losses) / len(val_losses)

        history["train_loss"].append(avg_train)
        history["val_loss"].append(avg_val)
        history["val_circle_f1"].append(circle_f1)
        history["val_circle_acc"].append(circle_acc)

        if circle_f1 > best_val_f1:
            best_val_f1 = circle_f1
            best_model_state = {k: v.clone() for k, v in model.state_dict().items()}

        if (epoch + 1) % 10 == 0 or epoch == 0:
            logger.info(
                f"Epoch {epoch+1:>3}/{epochs}: "
                f"train_loss={avg_train:.4f}, val_loss={avg_val:.4f}, "
                f"circle_f1={circle_f1:.4f}, circle_acc={circle_acc:.4f}, "
                f"intensity_acc={intensity_acc:.4f}, tension_acc={tension_acc:.4f}"
            )

    # ─── Restore best model ───
    if best_model_state is not None:
        model.load_state_dict(best_model_state)
        logger.info(f"Restored best model (F1={best_val_f1:.4f})")

    # ─── Final evaluation ───
    model.eval()
    all_c_preds = []
    all_c_true = []
    all_i_preds = []
    all_i_true = []
    all_t_preds = []
    all_t_true = []

    with torch.no_grad():
        for batch in val_loader:
            emb = batch["embedding"].to(device)
            feat = batch["features"].to(device)

            c_logits, t_logit, i_logits = model(emb, feat)

            all_c_preds.extend(c_logits.argmax(dim=1).cpu().tolist())
            all_c_true.extend(batch["circle"].tolist())
            all_i_preds.extend(i_logits.argmax(dim=1).cpu().tolist())
            all_i_true.extend(batch["intensity"].tolist())
            all_t_preds.extend((torch.sigmoid(t_logit) > 0.5).int().squeeze().cpu().tolist())
            all_t_true.extend(batch["tension"].int().tolist())

    final_metrics = {
        "circle_f1_macro": _f1_macro(all_c_true, all_c_preds, NUM_CIRCLES),
        "circle_accuracy": sum(p == t for p, t in zip(all_c_preds, all_c_true)) / len(all_c_true),
        "circle_per_class": _per_class_f1(all_c_true, all_c_preds, NUM_CIRCLES),
        "intensity_accuracy": sum(p == t for p, t in zip(all_i_preds, all_i_true)) / len(all_i_true) if all_i_true else 0,
        "tension_accuracy": sum(p == t for p, t in zip(all_t_preds, all_t_true)) / len(all_t_true) if all_t_true else 0,
        "best_epoch_f1": best_val_f1,
        "n_train": len(train_ds),
        "n_val": len(val_ds),
        "history": history,
    }

    return model, final_metrics


# ═══════════════════════════════════════════════════════════════════════
# METRICS HELPERS
# ═══════════════════════════════════════════════════════════════════════

def _f1_macro(y_true: list, y_pred: list, num_classes: int) -> float:
    """Compute macro F1 score without sklearn dependency."""
    f1s = []
    for c in range(num_classes):
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == c and p == c)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != c and p == c)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == c and p != c)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        f1s.append(f1)

    return sum(f1s) / len(f1s) if f1s else 0.0


def _per_class_f1(y_true: list, y_pred: list, num_classes: int) -> Dict[str, Dict[str, float]]:
    """Compute per-class precision, recall, F1."""
    result = {}
    for c in range(num_classes):
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == c and p == c)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != c and p == c)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == c and p != c)
        support = sum(1 for t in y_true if t == c)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        label = IDX2LABEL.get(c, str(c))
        result[label] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "support": support,
        }
    return result


# ═══════════════════════════════════════════════════════════════════════
# HYBRID PIPELINE
# ═══════════════════════════════════════════════════════════════════════

class HybridClassifier:
    """
    Hybrid pipeline: TF-IDF filters → TextCNN reclassifies top-K.

    In production:
      1. TF-IDF (existing) classifies all incoming signals → quick, rule-based
      2. TextCNN reclassifies the top-K most uncertain ones → neural refinement
      3. Agreement between both → high confidence
      4. Disagreement → flag for human review
    """

    def __init__(
        self,
        textcnn_model: CulturalTextCNN,
        bertimbau_model=None,
        bertimbau_tokenizer=None,
        confidence_threshold: float = 0.7,
    ):
        self.textcnn = textcnn_model
        self.bert_model = bertimbau_model
        self.bert_tokenizer = bertimbau_tokenizer
        self.confidence_threshold = confidence_threshold

    def classify(
        self,
        signal: dict,
        tfidf_prediction: Optional[str] = None,
        max_seq_len: int = 64,
    ) -> Dict[str, Any]:
        """
        Classify a single signal using hybrid pipeline.

        Args:
            signal: Supabase signal dict
            tfidf_prediction: Optional TF-IDF classification for comparison
            max_seq_len: Token sequence length for BERTimbau

        Returns:
            Classification result with confidence and agreement info
        """
        rd = signal.get("raw_data", {}) or {}
        s22 = rd.get("s22_features", {}) or {}
        s23 = rd.get("s23_scaled", {}) or {}

        # Build feature vector
        feat = []
        for col in FEATURE_COLUMNS:
            val = s23.get(col) or s22.get(col)
            feat.append(float(val) if val is not None else 0.0)
        feat_tensor = torch.FloatTensor([feat])

        # Generate token-level embedding
        if self.bert_model and self.bert_tokenizer:
            text = signal.get("termo", "")
            expl = str(rd.get("explicacao", ""))
            if expl and expl != "None":
                text = f"{text}. {expl}"

            inputs = self.bert_tokenizer(
                text, return_tensors="pt", padding="max_length",
                truncation=True, max_length=max_seq_len,
            )
            with torch.no_grad():
                out = self.bert_model(**inputs)
                emb = out.last_hidden_state  # (1, seq_len, 768)
        else:
            emb = torch.randn(1, max_seq_len, 768) * 0.01

        # TextCNN prediction
        result = self.textcnn.predict(emb, feat_tensor)

        # Compare with TF-IDF
        if tfidf_prediction:
            result["tfidf_prediction"] = tfidf_prediction
            result["agreement"] = result["circle"].upper() == tfidf_prediction.upper()
            result["needs_review"] = not result["agreement"]
        else:
            result["agreement"] = None
            result["needs_review"] = max(result["circle_probs"]) < self.confidence_threshold

        return result


# ═══════════════════════════════════════════════════════════════════════
# SAVE/LOAD
# ═══════════════════════════════════════════════════════════════════════

def save_model(model: CulturalTextCNN, metrics: dict, path: Path):
    """Save model + metrics to disk."""
    path.mkdir(parents=True, exist_ok=True)

    torch.save(model.state_dict(), path / "textcnn_weights.pt")

    with open(path / "training_metrics.json", "w") as f:
        # Filter non-serializable items
        clean = {k: v for k, v in metrics.items() if k != "history"}
        clean["history_epochs"] = len(metrics.get("history", {}).get("train_loss", []))
        json.dump(clean, f, indent=2, default=str)

    logger.info(f"Model saved to {path}")


def load_model(path: Path, device: str = "cpu") -> Tuple[CulturalTextCNN, dict]:
    """Load model + metrics from disk."""
    model = CulturalTextCNN()
    model.load_state_dict(torch.load(path / "textcnn_weights.pt", map_location=device))
    model.to(device)
    model.eval()

    with open(path / "training_metrics.json") as f:
        metrics = json.load(f)

    logger.info(f"Model loaded from {path}")
    return model, metrics
