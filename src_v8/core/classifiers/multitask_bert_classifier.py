#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S3.2 │ P18A — Multi-Task BERTimbau Classifier
Culture Pulse V9.0 — Sprint 3, Passo 2

PROBLEMA:
  Cada tarefa (círculo, tensão, intensidade) é tratada isoladamente.
  Nenhuma representação compartilhada entre tarefas — o TextCNN S3.1
  usa BERTimbau congelado como feature extractor, sem fine-tuning.

SOLUÇÃO:
  Multi-Task Learning (MTL) com BERTimbau fine-tunable como backbone
  compartilhado + 4 task-specific heads.

ARQUITETURA:
  ┌──────────────────────────────────────────────────────────────────┐
  │  Input: texto (termo + narrativa)                                │
  │                                                                  │
  │  BERTimbau (fine-tunable backbone)                               │
  │  └── CLS token → 768d shared representation                     │
  │                                                                  │
  │  + S2.2/S2.3 features (8d)  → Linear(8→32) → 32d               │
  │                                                                  │
  │  Merged: 800d → LayerNorm → Dropout(0.3)                        │
  │                                                                  │
  │  Head 1: circle   │ Linear(800→256→9)  │ CrossEntropy (9 cls)   │
  │  Head 2: tension  │ Linear(800→128→7)  │ CrossEntropy (7 cls)   │
  │  Head 3: alma     │ Linear(800→128→1)  │ MSE regression [0,1]   │
  │  Head 4: intens.  │ Linear(800→128→1)  │ MSE regression [0,1]   │
  └──────────────────────────────────────────────────────────────────┘

LABELS (from Supabase enrichment — P9 FIX):
  Circle (9 classes):
    Música & Ritmo, Gastronomia & Sabor, Arte Visual & Moda,
    Tecnologia & Digital, Saúde & Bem-estar, Adaptação & Flexibilidade,
    Política & Cidadania, Conexão com Natureza & Coletivo, Cultura Geral
  Tension (7 classes):
    tradicao_vs_moderno, elitismo_vs_popularizacao, digital_vs_presencial,
    individualismo_vs_coletivismo, local_vs_global,
    consumo_vs_sustentabilidade, none
  Alma Score: float [0.0, 1.0] — regression
  Intensidade: float [0.0, 1.0] — regression

REFERÊNCIA:
  Paper A (Deshpande 2025) — MTL melhora generalização com head conjunto
  Caruana (1997) — Multi-task Learning, Machine Learning 28(1)

CRITÉRIO DE ACEITE:
  MTL ≥ single-task (S3.1 TextCNN) em pelo menos 3 das 4 heads

USO:
  from core.classifiers.multitask_bert_classifier import (
      CulturalMTLBert, MTLDataset, prepare_mtl_data, train_mtl, save_mtl_model
  )

Autor: Culture Pulse Team
Data: 2026-02-19
Sprint: S3.2 │ P18A
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
# LABEL MAPPINGS
# ═══════════════════════════════════════════════════════════════════════

# 9 circle classes from SignalSynthesizer enrichment (P9 FIX)
CIRCLE_LABELS_MTL = [
    "Música & Ritmo",
    "Gastronomia & Sabor",
    "Arte Visual & Moda",
    "Tecnologia & Digital",
    "Saúde & Bem-estar",
    "Adaptação & Flexibilidade",
    "Política & Cidadania",
    "Conexão com Natureza & Coletivo",
    "Cultura Geral",
]
CIRCLE2IDX = {lb: i for i, lb in enumerate(CIRCLE_LABELS_MTL)}
IDX2CIRCLE = {i: lb for lb, i in CIRCLE2IDX.items()}
NUM_CIRCLES_MTL = len(CIRCLE_LABELS_MTL)

# 7 tension classes (6 named + "none")
TENSION_LABELS_MTL = [
    "tradicao_vs_moderno",
    "elitismo_vs_popularizacao",
    "digital_vs_presencial",
    "individualismo_vs_coletivismo",
    "local_vs_global",
    "consumo_vs_sustentabilidade",
    "none",
]
TENSION2IDX = {lb: i for i, lb in enumerate(TENSION_LABELS_MTL)}
IDX2TENSION = {i: lb for lb, i in TENSION2IDX.items()}
NUM_TENSIONS_MTL = len(TENSION_LABELS_MTL)

# S2.2/S2.3 feature columns (same as S3.1)
FEATURE_COLUMNS = [
    "momentum_scaled", "volume_scaled", "sentiment_scaled", "score_scaled",
    "novelty_score", "signal_strength", "composite_rank_score", "ner_penalty",
]


# ═══════════════════════════════════════════════════════════════════════
# PYTORCH MODEL
# ═══════════════════════════════════════════════════════════════════════

import torch
import torch.nn as nn
import torch.nn.functional as F


class CulturalMTLBert(nn.Module):
    """
    Multi-Task Learning classifier with BERTimbau backbone.

    Architecture:
      BERTimbau (fine-tunable) → CLS (768d)
      + Feature branch (8d → 32d)
      = 800d merged representation
      → 4 task-specific heads

    Key differences from S3.1 TextCNN:
      - BERTimbau backbone is FINE-TUNED (not frozen)
      - Uses CLS pooling instead of Conv1d over token sequence
      - 4 heads instead of 3 (+ alma regression)
      - Tension is multi-class (7) instead of binary
      - Alma + Intensity are regression instead of classification
    """

    def __init__(
        self,
        bert_model_name: str = "neuralmind/bert-base-portuguese-cased",
        feature_dim: int = 8,
        num_circles: int = NUM_CIRCLES_MTL,
        num_tensions: int = NUM_TENSIONS_MTL,
        dropout: float = 0.3,
        freeze_bert_layers: int = 8,
    ):
        """
        Args:
            bert_model_name: HuggingFace model identifier
            feature_dim: dimensionality of engineered features
            num_circles: number of circle classes
            num_tensions: number of tension classes
            dropout: dropout rate for heads
            freeze_bert_layers: number of lower BERT layers to freeze
                (0=all tunable, 12=all frozen). Recommended: 8-10 for
                small datasets (~186 samples) to avoid catastrophic forgetting.
        """
        super().__init__()

        from transformers import AutoModel

        self.bert = AutoModel.from_pretrained(bert_model_name)
        self.hidden_size = self.bert.config.hidden_size  # 768

        # Freeze lower layers to prevent catastrophic forgetting
        self._freeze_bert_layers(freeze_bert_layers)

        # Feature branch
        self.feature_fc = nn.Sequential(
            nn.Linear(feature_dim, 64),
            nn.GELU(),
            nn.LayerNorm(64),
            nn.Dropout(0.1),
            nn.Linear(64, 32),
            nn.GELU(),
        )
        feat_out_dim = 32

        # Merge
        merged_dim = self.hidden_size + feat_out_dim  # 800
        self.merge_norm = nn.LayerNorm(merged_dim)
        self.merge_dropout = nn.Dropout(dropout)

        # ─── Head 1: Circle classification (9 classes) ───
        self.circle_head = nn.Sequential(
            nn.Linear(merged_dim, 256),
            nn.GELU(),
            nn.Dropout(dropout * 0.5),
            nn.Linear(256, num_circles),
        )

        # ─── Head 2: Tension classification (7 classes) ───
        self.tension_head = nn.Sequential(
            nn.Linear(merged_dim, 128),
            nn.GELU(),
            nn.Dropout(dropout * 0.5),
            nn.Linear(128, num_tensions),
        )

        # ─── Head 3: Alma score regression (0.0–1.0) ───
        self.alma_head = nn.Sequential(
            nn.Linear(merged_dim, 128),
            nn.GELU(),
            nn.Dropout(dropout * 0.5),
            nn.Linear(128, 1),
            nn.Sigmoid(),
        )

        # ─── Head 4: Intensity regression (0.0–1.0) ───
        self.intensity_head = nn.Sequential(
            nn.Linear(merged_dim, 128),
            nn.GELU(),
            nn.Dropout(dropout * 0.5),
            nn.Linear(128, 1),
            nn.Sigmoid(),
        )

    def _freeze_bert_layers(self, n_layers: int):
        """Freeze the first n_layers of BERT encoder."""
        # Always freeze embeddings for small data
        for param in self.bert.embeddings.parameters():
            param.requires_grad = False

        # Freeze first n_layers encoder layers
        for i, layer in enumerate(self.bert.encoder.layer):
            if i < n_layers:
                for param in layer.parameters():
                    param.requires_grad = False

        trainable = sum(p.numel() for p in self.bert.parameters() if p.requires_grad)
        total = sum(p.numel() for p in self.bert.parameters())
        logger.info(
            f"BERTimbau: frozen {n_layers}/12 layers. "
            f"Trainable: {trainable:,}/{total:,} params "
            f"({trainable/total*100:.1f}%)"
        )

    def forward(
        self,
        input_ids: torch.Tensor,       # (batch, seq_len)
        attention_mask: torch.Tensor,   # (batch, seq_len)
        features: torch.Tensor,         # (batch, 8)
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass.

        Returns:
            circle_logits:     (batch, 9)
            tension_logits:    (batch, 7)
            alma_score:        (batch, 1) in [0, 1]
            intensity_score:   (batch, 1) in [0, 1]
        """
        # BERTimbau forward → CLS token
        bert_out = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        cls = bert_out.last_hidden_state[:, 0, :]  # (batch, 768)

        # Feature branch
        feat_out = self.feature_fc(features)  # (batch, 32)

        # Merge
        merged = torch.cat([cls, feat_out], dim=1)  # (batch, 800)
        merged = self.merge_norm(merged)
        merged = self.merge_dropout(merged)

        # Heads
        circle_logits = self.circle_head(merged)     # (batch, 9)
        tension_logits = self.tension_head(merged)   # (batch, 7)
        alma = self.alma_head(merged)                # (batch, 1)
        intensity = self.intensity_head(merged)      # (batch, 1)

        return circle_logits, tension_logits, alma, intensity

    def predict(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        features: torch.Tensor,
    ) -> Dict[str, Any]:
        """Predict with human-readable output."""
        self.eval()
        with torch.no_grad():
            c_logits, t_logits, alma, intensity = self.forward(
                input_ids, attention_mask, features
            )

            c_probs = F.softmax(c_logits, dim=-1)
            t_probs = F.softmax(t_logits, dim=-1)

            circle_idx = c_probs.argmax(dim=-1).item()
            tension_idx = t_probs.argmax(dim=-1).item()

            return {
                "circle": IDX2CIRCLE[circle_idx],
                "circle_idx": circle_idx,
                "circle_probs": c_probs[0].tolist(),
                "tension": IDX2TENSION[tension_idx],
                "tension_idx": tension_idx,
                "tension_probs": t_probs[0].tolist(),
                "alma_score": alma.item(),
                "intensity": intensity.item(),
            }


# ═══════════════════════════════════════════════════════════════════════
# DATASET
# ═══════════════════════════════════════════════════════════════════════

class MTLDataset(torch.utils.data.Dataset):
    """
    Dataset for MTL training.

    V9.1 DYNAMIC PADDING: Stores raw texts instead of pre-tokenised tensors.
    Tokenisation + padding happens per mini-batch in the collate function,
    padding only to the longest sequence in each batch.

    Each sample:
      text:            str raw text
      features:        (8,) S2.2+S2.3 engineered features
      circle_label:    int (0-8)
      tension_label:   int (0-6)
      alma_label:      float (0.0-1.0)
      intensity_label: float (0.0-1.0)
    """

    def __init__(
        self,
        texts: List[str],                 # raw texts
        features: np.ndarray,              # (N, 8)
        circle_labels: np.ndarray,         # (N,) int
        tension_labels: np.ndarray,        # (N,) int
        alma_labels: np.ndarray,           # (N,) float
        intensity_labels: np.ndarray,      # (N,) float
    ):
        self.texts = texts
        self.features = torch.FloatTensor(features)
        self.circle_labels = torch.LongTensor(circle_labels)
        self.tension_labels = torch.LongTensor(tension_labels)
        self.alma_labels = torch.FloatTensor(alma_labels)
        self.intensity_labels = torch.FloatTensor(intensity_labels)

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        return {
            "text": self.texts[idx],
            "features": self.features[idx],
            "circle": self.circle_labels[idx],
            "tension": self.tension_labels[idx],
            "alma": self.alma_labels[idx],
            "intensity": self.intensity_labels[idx],
        }


def make_mtl_collate_fn(tokenizer, max_length: int = 64):
    """
    Creates a collate function for MTL that tokenises + pads dynamically
    per batch. Handles both text tokens AND engineered features.

    Args:
        tokenizer: HuggingFace tokenizer (AutoTokenizer)
        max_length: upper bound for truncation (safety limit)

    Returns:
        collate_fn compatible with torch DataLoader
    """
    import torch

    def _collate(batch):
        texts = [item["text"] for item in batch]
        features = torch.stack([item["features"] for item in batch])
        circles = torch.stack([item["circle"] for item in batch])
        tensions = torch.stack([item["tension"] for item in batch])
        almas = torch.stack([item["alma"] for item in batch])
        intensities = torch.stack([item["intensity"] for item in batch])

        enc = tokenizer(
            texts,
            padding="longest",       # pad to longest in THIS batch
            truncation=True,
            max_length=max_length,   # safety truncation limit
            return_tensors="pt",
        )

        return {
            "input_ids": enc["input_ids"],
            "attention_mask": enc["attention_mask"],
            "features": features,
            "circle": circles,
            "tension": tensions,
            "alma": almas,
            "intensity": intensities,
        }

    return _collate


# ═══════════════════════════════════════════════════════════════════════
# DATA PREPARATION
# ═══════════════════════════════════════════════════════════════════════

def prepare_mtl_data(
    signals: List[dict],
    tokenizer=None,
    max_seq_len: int = 64,
) -> Tuple[List[str], np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, List[int]]:
    """
    Prepare training data from Supabase signals (P9 FIX enriched).

    V9.1 DYNAMIC PADDING: No longer pre-tokenises. Returns raw texts;
    tokenisation + dynamic padding happens per mini-batch via
    make_mtl_collate_fn() in the DataLoader.

    NOTE: tokenizer param kept for backward compatibility but is no longer used.

    Uses labels from raw_data enrichment (circulo_label, tensao_cultural,
    alma_score, intensidade) rather than Snorkel labels — because these
    are richer (9 circles + 7 tensions + continuous scores).

    Returns:
        texts:            List[str] raw texts
        features:         (N, 8) float
        circle_labels:    (N,) int
        tension_labels:   (N,) int
        alma_labels:      (N,) float
        intensity_labels: (N,) float
        valid_ids:        list of signal IDs included
    """
    all_texts = []
    all_features = []
    all_circles = []
    all_tensions = []
    all_almas = []
    all_intensities = []
    valid_ids = []

    skipped_no_enrichment = 0
    skipped_no_circle = 0

    for s in signals:
        sid = s["id"]
        rd = s.get("raw_data", {}) or {}

        # Skip non-enriched signals (model_training_log, etc.)
        circulo_label = rd.get("circulo_label")
        if not circulo_label or circulo_label not in CIRCLE2IDX:
            skipped_no_circle += 1
            continue

        # ─── Text input ───
        termo = s.get("termo", "") or ""
        narrativa = str(rd.get("narrativa", "") or "")
        signal_name = str(rd.get("signal_name", "") or "")

        # Build text: signal_name + termo + first 200 chars of narrativa
        text_parts = []
        if signal_name:
            text_parts.append(signal_name)
        text_parts.append(termo)
        if narrativa:
            text_parts.append(narrativa[:200])
        text = ". ".join(text_parts)

        # ─── Engineered features (8d) ───
        s22 = rd.get("s22_features", {}) or {}
        s23 = rd.get("s23_scaled", {}) or {}
        feat = []
        for col in FEATURE_COLUMNS:
            val = s23.get(col) or s22.get(col)
            feat.append(float(val) if val is not None else 0.0)

        # ─── Labels from enrichment ───
        circle_idx = CIRCLE2IDX[circulo_label]

        tensao = rd.get("tensao_cultural")
        if tensao and tensao in TENSION2IDX:
            tension_idx = TENSION2IDX[tensao]
        else:
            tension_idx = TENSION2IDX["none"]

        alma = float(rd.get("alma_score", 0.0) or 0.0)
        alma = max(0.0, min(1.0, alma))

        intensidade = float(rd.get("intensidade", 0.5) or 0.5)
        intensidade = max(0.0, min(1.0, intensidade))

        all_texts.append(text)
        all_features.append(feat)
        all_circles.append(circle_idx)
        all_tensions.append(tension_idx)
        all_almas.append(alma)
        all_intensities.append(intensidade)
        valid_ids.append(sid)

    logger.info(
        f"MTL data: {len(valid_ids)} valid signals, "
        f"skipped {skipped_no_circle} (no enriched circulo_label)"
    )

    return (
        all_texts,
        np.array(all_features, dtype=np.float32),
        np.array(all_circles, dtype=np.int64),
        np.array(all_tensions, dtype=np.int64),
        np.array(all_almas, dtype=np.float32),
        np.array(all_intensities, dtype=np.float32),
        valid_ids,
    )


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


def train_mtl(
    texts: List[str],
    features: np.ndarray,
    circle_labels: np.ndarray,
    tension_labels: np.ndarray,
    alma_labels: np.ndarray,
    intensity_labels: np.ndarray,
    epochs: int = 20,
    batch_size: int = 8,
    lr: float = 2e-5,
    holdout_ratio: float = 0.2,
    device: str = "cpu",
    label_smoothing: float = 0.1,
    freeze_bert_layers: int = 8,
    loss_weights: Optional[Dict[str, float]] = None,
    max_seq_len: int = 64,
    model_name: str = "neuralmind/bert-base-portuguese-cased",
) -> Tuple["CulturalMTLBert", Dict[str, Any]]:
    """
    Train CulturalMTLBert on prepared data.

    V9.1 DYNAMIC PADDING: Accepts raw texts instead of pre-tokenised
    arrays. Tokenisation + padding happens per mini-batch via
    make_mtl_collate_fn() → ~20-40% compute savings on short texts.

    Args:
        texts: list of N raw text strings
        features: (N, 8) engineered features
        circle_labels: (N,) int circle class indices
        tension_labels: (N,) int tension class indices
        alma_labels: (N,) float alma scores [0, 1]
        intensity_labels: (N,) float intensity scores [0, 1]
        epochs: number of training epochs
        batch_size: mini-batch size (small for BERTimbau on CPU)
        lr: learning rate (2e-5 standard for BERT fine-tuning)
        holdout_ratio: fraction for validation
        device: 'cpu' or 'cuda'
        label_smoothing: smoothing for CrossEntropy
        freeze_bert_layers: freeze bottom N of 12 BERT layers
        loss_weights: dict of task → weight (default: balanced)
        max_seq_len: safety-cap for truncation (default 64)
        model_name: HuggingFace model name for tokenizer

    Returns:
        model: trained CulturalMTLBert
        metrics: dict with evaluation results
    """
    from transformers import AutoTokenizer

    if loss_weights is None:
        loss_weights = {
            "circle": 1.0,
            "tension": 0.7,
            "alma": 0.5,
            "intensity": 0.3,
        }

    N = len(texts)

    # ─── Load tokenizer for dynamic collate_fn ───
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    collate_fn = make_mtl_collate_fn(tokenizer, max_length=max_seq_len)
    logger.info(f"Dynamic padding collate_fn created (max_length={max_seq_len})")

    # ─── Stratified train/val split (by circle) ───
    np.random.seed(42)
    train_indices = []
    val_indices = []
    for c in range(NUM_CIRCLES_MTL):
        c_idx = np.where(circle_labels == c)[0]
        np.random.shuffle(c_idx)
        split = max(1, int(len(c_idx) * (1 - holdout_ratio)))
        train_indices.extend(c_idx[:split].tolist())
        val_indices.extend(c_idx[split:].tolist())

    train_idx = np.array(train_indices)
    val_idx = np.array(val_indices)
    np.random.shuffle(train_idx)
    np.random.shuffle(val_idx)

    train_ds = MTLDataset(
        [texts[i] for i in train_idx],
        features[train_idx], circle_labels[train_idx],
        tension_labels[train_idx], alma_labels[train_idx],
        intensity_labels[train_idx],
    )
    val_ds = MTLDataset(
        [texts[i] for i in val_idx],
        features[val_idx], circle_labels[val_idx],
        tension_labels[val_idx], alma_labels[val_idx],
        intensity_labels[val_idx],
    )

    train_loader = torch.utils.data.DataLoader(
        train_ds, batch_size=batch_size, shuffle=True,
        drop_last=False, collate_fn=collate_fn,
    )
    val_loader = torch.utils.data.DataLoader(
        val_ds, batch_size=batch_size, collate_fn=collate_fn,
    )

    # ─── Model ───
    model = CulturalMTLBert(
        feature_dim=features.shape[1],
        num_circles=NUM_CIRCLES_MTL,
        num_tensions=NUM_TENSIONS_MTL,
        dropout=0.3,
        freeze_bert_layers=freeze_bert_layers,
    ).to(device)

    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    logger.info(
        f"MTL Model: {total_params:,} total params, "
        f"{trainable_params:,} trainable ({trainable_params/total_params*100:.1f}%)"
    )

    # ─── Loss functions ───
    circle_weights = compute_class_weights(circle_labels[train_idx], NUM_CIRCLES_MTL).to(device)
    tension_weights = compute_class_weights(tension_labels[train_idx], NUM_TENSIONS_MTL).to(device)

    circle_loss_fn = nn.CrossEntropyLoss(weight=circle_weights, label_smoothing=label_smoothing)
    tension_loss_fn = nn.CrossEntropyLoss(weight=tension_weights, label_smoothing=label_smoothing)
    alma_loss_fn = nn.MSELoss()
    intensity_loss_fn = nn.MSELoss()

    # ─── Optimizer: differential learning rates ───
    # BERT backbone gets lower LR; heads get higher LR
    bert_params = list(model.bert.parameters())
    head_params = (
        list(model.feature_fc.parameters()) +
        list(model.circle_head.parameters()) +
        list(model.tension_head.parameters()) +
        list(model.alma_head.parameters()) +
        list(model.intensity_head.parameters()) +
        list(model.merge_norm.parameters())
    )

    optimizer = torch.optim.AdamW([
        {"params": [p for p in bert_params if p.requires_grad], "lr": lr},
        {"params": head_params, "lr": lr * 10},  # heads: 10x backbone LR
    ], weight_decay=0.01)

    # Warmup + cosine annealing
    warmup_steps = max(1, len(train_loader) * 2)  # 2 epochs warmup
    total_steps = len(train_loader) * epochs

    def lr_lambda(step):
        if step < warmup_steps:
            return (step + 1) / warmup_steps
        progress = (step - warmup_steps) / max(1, total_steps - warmup_steps)
        return 0.5 * (1 + math.cos(math.pi * progress))

    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)

    # ─── Training loop ───
    history = {
        "train_loss": [], "val_loss": [],
        "val_circle_f1": [], "val_circle_acc": [],
        "val_tension_f1": [], "val_tension_acc": [],
        "val_alma_mae": [], "val_intensity_mae": [],
    }
    best_val_score = -float("inf")
    best_model_state = None

    logger.info(f"Training MTL: {len(train_ds)} train, {len(val_ds)} val, {epochs} epochs")

    for epoch in range(epochs):
        # ── Train ──
        model.train()
        train_losses = []

        for batch in train_loader:
            ids = batch["input_ids"].to(device)
            mask = batch["attention_mask"].to(device)
            feat = batch["features"].to(device)
            c_label = batch["circle"].to(device)
            t_label = batch["tension"].to(device)
            a_label = batch["alma"].to(device)
            i_label = batch["intensity"].to(device)

            c_logits, t_logits, alma_pred, int_pred = model(ids, mask, feat)

            loss_c = circle_loss_fn(c_logits, c_label) * loss_weights["circle"]
            loss_t = tension_loss_fn(t_logits, t_label) * loss_weights["tension"]
            loss_a = alma_loss_fn(alma_pred.squeeze(), a_label) * loss_weights["alma"]
            loss_i = intensity_loss_fn(int_pred.squeeze(), i_label) * loss_weights["intensity"]

            loss = loss_c + loss_t + loss_a + loss_i

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()

            train_losses.append(loss.item())

        # ── Validate ──
        model.eval()
        val_losses = []
        all_c_preds, all_c_true = [], []
        all_t_preds, all_t_true = [], []
        all_a_preds, all_a_true = [], []
        all_i_preds, all_i_true = [], []

        with torch.no_grad():
            for batch in val_loader:
                ids = batch["input_ids"].to(device)
                mask = batch["attention_mask"].to(device)
                feat = batch["features"].to(device)
                c_label = batch["circle"].to(device)
                t_label = batch["tension"].to(device)
                a_label = batch["alma"].to(device)
                i_label = batch["intensity"].to(device)

                c_logits, t_logits, alma_pred, int_pred = model(ids, mask, feat)

                loss_c = circle_loss_fn(c_logits, c_label)
                loss_t = tension_loss_fn(t_logits, t_label)
                loss_a = alma_loss_fn(alma_pred.squeeze(), a_label)
                loss_i = intensity_loss_fn(int_pred.squeeze(), i_label)
                val_losses.append((loss_c + loss_t + loss_a + loss_i).item())

                all_c_preds.extend(c_logits.argmax(dim=1).cpu().tolist())
                all_c_true.extend(c_label.cpu().tolist())
                all_t_preds.extend(t_logits.argmax(dim=1).cpu().tolist())
                all_t_true.extend(t_label.cpu().tolist())
                all_a_preds.extend(alma_pred.squeeze().cpu().tolist())
                all_a_true.extend(a_label.cpu().tolist())
                all_i_preds.extend(int_pred.squeeze().cpu().tolist())
                all_i_true.extend(i_label.cpu().tolist())

        # Metrics
        circle_f1 = _f1_macro(all_c_true, all_c_preds, NUM_CIRCLES_MTL)
        circle_acc = sum(p == t for p, t in zip(all_c_preds, all_c_true)) / max(1, len(all_c_true))
        tension_f1 = _f1_macro(all_t_true, all_t_preds, NUM_TENSIONS_MTL)
        tension_acc = sum(p == t for p, t in zip(all_t_preds, all_t_true)) / max(1, len(all_t_true))
        alma_mae = np.mean(np.abs(np.array(all_a_preds) - np.array(all_a_true))) if all_a_true else 1.0
        intensity_mae = np.mean(np.abs(np.array(all_i_preds) - np.array(all_i_true))) if all_i_true else 1.0

        avg_train = np.mean(train_losses) if train_losses else 0
        avg_val = np.mean(val_losses) if val_losses else 0

        history["train_loss"].append(avg_train)
        history["val_loss"].append(avg_val)
        history["val_circle_f1"].append(circle_f1)
        history["val_circle_acc"].append(circle_acc)
        history["val_tension_f1"].append(tension_f1)
        history["val_tension_acc"].append(tension_acc)
        history["val_alma_mae"].append(alma_mae)
        history["val_intensity_mae"].append(intensity_mae)

        # Composite score: weighted F1s + (1 - MAEs)
        composite = (
            circle_f1 * 0.4 +
            tension_f1 * 0.3 +
            (1.0 - alma_mae) * 0.2 +
            (1.0 - intensity_mae) * 0.1
        )

        if composite > best_val_score:
            best_val_score = composite
            best_model_state = {k: v.clone() for k, v in model.state_dict().items()}

        if (epoch + 1) % 5 == 0 or epoch == 0:
            logger.info(
                f"Epoch {epoch+1:>3}/{epochs}: "
                f"train={avg_train:.4f}, val={avg_val:.4f} | "
                f"circle_f1={circle_f1:.4f}, tension_f1={tension_f1:.4f}, "
                f"alma_mae={alma_mae:.4f}, int_mae={intensity_mae:.4f}"
            )

    # ─── Restore best model ───
    if best_model_state is not None:
        model.load_state_dict(best_model_state)
        logger.info(f"Restored best model (composite={best_val_score:.4f})")

    # ─── Final evaluation ───
    model.eval()
    all_c_preds, all_c_true = [], []
    all_t_preds, all_t_true = [], []
    all_a_preds, all_a_true = [], []
    all_i_preds, all_i_true = [], []

    with torch.no_grad():
        for batch in val_loader:
            ids = batch["input_ids"].to(device)
            mask = batch["attention_mask"].to(device)
            feat = batch["features"].to(device)

            c_logits, t_logits, alma_pred, int_pred = model(ids, mask, feat)

            all_c_preds.extend(c_logits.argmax(dim=1).cpu().tolist())
            all_c_true.extend(batch["circle"].tolist())
            all_t_preds.extend(t_logits.argmax(dim=1).cpu().tolist())
            all_t_true.extend(batch["tension"].tolist())
            all_a_preds.extend(alma_pred.squeeze().cpu().tolist())
            all_a_true.extend(batch["alma"].tolist())
            all_i_preds.extend(int_pred.squeeze().cpu().tolist())
            all_i_true.extend(batch["intensity"].tolist())

    final_metrics = {
        "circle_f1_macro": _f1_macro(all_c_true, all_c_preds, NUM_CIRCLES_MTL),
        "circle_accuracy": sum(p == t for p, t in zip(all_c_preds, all_c_true)) / max(1, len(all_c_true)),
        "circle_per_class": _per_class_metrics(all_c_true, all_c_preds, NUM_CIRCLES_MTL, IDX2CIRCLE),
        "tension_f1_macro": _f1_macro(all_t_true, all_t_preds, NUM_TENSIONS_MTL),
        "tension_accuracy": sum(p == t for p, t in zip(all_t_preds, all_t_true)) / max(1, len(all_t_true)),
        "tension_per_class": _per_class_metrics(all_t_true, all_t_preds, NUM_TENSIONS_MTL, IDX2TENSION),
        "alma_mae": float(np.mean(np.abs(np.array(all_a_preds) - np.array(all_a_true)))),
        "alma_r2": float(_r2_score(all_a_true, all_a_preds)),
        "intensity_mae": float(np.mean(np.abs(np.array(all_i_preds) - np.array(all_i_true)))),
        "intensity_r2": float(_r2_score(all_i_true, all_i_preds)),
        "best_composite_score": best_val_score,
        "n_train": len(train_ds),
        "n_val": len(val_ds),
        "epochs": epochs,
        "freeze_bert_layers": freeze_bert_layers,
        "loss_weights": loss_weights,
        "history": history,
    }

    return model, final_metrics


# ═══════════════════════════════════════════════════════════════════════
# METRICS HELPERS
# ═══════════════════════════════════════════════════════════════════════

def _f1_macro(y_true: list, y_pred: list, num_classes: int) -> float:
    """Compute macro F1 score without sklearn."""
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


def _per_class_metrics(
    y_true: list, y_pred: list, num_classes: int, idx2label: dict
) -> Dict[str, Dict[str, float]]:
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

        label = idx2label.get(c, str(c))
        result[label] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "support": support,
        }
    return result


def _r2_score(y_true: list, y_pred: list) -> float:
    """Compute R² (coefficient of determination)."""
    y_true = np.array(y_true, dtype=np.float64)
    y_pred = np.array(y_pred, dtype=np.float64)
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0


# ═══════════════════════════════════════════════════════════════════════
# SAVE / LOAD
# ═══════════════════════════════════════════════════════════════════════

def save_mtl_model(model: CulturalMTLBert, metrics: dict, path: Path):
    """Save MTL model weights + metrics."""
    path.mkdir(parents=True, exist_ok=True)

    # Save only the state dict (not the full HF model)
    torch.save(model.state_dict(), path / "mtl_bert_weights.pt")

    # Save metrics (filter non-serializable)
    clean = {k: v for k, v in metrics.items() if k != "history"}
    clean["history_epochs"] = len(metrics.get("history", {}).get("train_loss", []))
    with open(path / "mtl_training_metrics.json", "w") as f:
        json.dump(clean, f, indent=2, default=str)

    # Save label mappings for reproducibility
    with open(path / "label_mappings.json", "w") as f:
        json.dump({
            "circle_labels": CIRCLE_LABELS_MTL,
            "tension_labels": TENSION_LABELS_MTL,
            "circle2idx": CIRCLE2IDX,
            "tension2idx": TENSION2IDX,
        }, f, indent=2, ensure_ascii=False)

    logger.info(f"MTL model saved to {path}")


def load_mtl_model(path: Path, device: str = "cpu") -> Tuple[CulturalMTLBert, dict]:
    """Load MTL model from disk."""
    model = CulturalMTLBert()
    state_dict = torch.load(path / "mtl_bert_weights.pt", map_location=device)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()

    with open(path / "mtl_training_metrics.json") as f:
        metrics = json.load(f)

    logger.info(f"MTL model loaded from {path}")
    return model, metrics
