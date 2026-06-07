#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cross-Impact Matrix Engine — F-14 (FASE 5)
============================================
Análise de impacto cruzado entre dimensões PEST + Análise Morfológica.

Funcionalidade:
  1. Cross-Impact Matrix (CIM): mede influência causal entre P/E/S/T
     - P→E: como política impacta economia
     - E→S: como economia impacta sociedade
     - T→P: como tecnologia impacta política
     etc. (4×4 = 16 relações, 12 off-diagonal)

  2. Análise Morfológica: combina dimensões PEST para gerar cenários
     - Cada dimensão tem N estados possíveis
     - Combinações válidas = cenários plausíveis

  3. Causal Chain Detection: identifica cascatas de impacto
     - P→E→S (política causa impacto econômico que afeta sociedade)

Design:
  - Aprende pesos de co-ocorrência a partir de sinais PEST classificados
  - Sem ML pesado: frequências de co-ocorrência + mutual information
  - Integra com PESTEngine (F-5) para classificação
  - Integra com ScenarioPlanner (F-6) para cenários morfológicos
"""

from __future__ import annotations

import json
import logging
import math
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
#  Constants
# ═══════════════════════════════════════════════════════════════════════════════

PEST_CATEGORIES = ("Political", "Economic", "Social", "Technological")


# ═══════════════════════════════════════════════════════════════════════════════
#  Data Classes
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ImpactEntry:
    """A single observed co-occurrence / impact between two PEST dims."""
    source: str
    target: str
    signal_id: str = ""
    strength: float = 0.0  # 0-1
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CausalChain:
    """A chain of causal impacts: A→B→C→..."""
    chain: List[str]
    total_strength: float = 0.0
    evidence_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MorphologicalScenario:
    """A scenario generated from morphological analysis."""
    name: str
    dimensions: Dict[str, str]  # PEST category → state
    plausibility: float = 0.0  # 0-1
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ═══════════════════════════════════════════════════════════════════════════════
#  Default States for Morphological Analysis
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT_MORPHOLOGICAL_STATES: Dict[str, List[str]] = {
    "Political": [
        "Estabilidade regulatória",
        "Turbulência política",
        "Abertura institucional",
        "Polarização extrema",
    ],
    "Economic": [
        "Crescimento e Prosperidade",
        "Estagnação e Baixa",
        "Choque Inflacionário / Alto Desemprego"  # V9.5 Scenario
    ],
    "Social": [
        "Coesão e Otimismo",
        "Fragmentação e Tensão",
        "Resiliência e 'O Corre'"  # V9.5 Scenario
    ],
    "Technological": [
        "Adoção massiva IA",
        "Resistência tecnológica",
        "Inovação descentralizada",
        "Dependência plataformas",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
#  Configuration
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT_CONFIG: Dict[str, Any] = {
    "min_observations": 3,       # min obs to consider an impact significant
    "decay_factor": 0.95,        # exponential decay per new batch
    "max_chain_length": 4,       # max steps in causal chain (P→E→S→T)
    "plausibility_threshold": 0.3,  # min plausibility for a scenario
    "log_dir": "data/cross_impact",
    "max_entries_per_pair": 500,
}


# ═══════════════════════════════════════════════════════════════════════════════
#  CrossImpactEngine
# ═══════════════════════════════════════════════════════════════════════════════

class CrossImpactEngine:
    """
    Cross-Impact Matrix with Morphological Analysis.

    Builds a 4×4 impact matrix from PEST co-occurrences in cultural signals,
    detects causal chains, and generates morphological scenarios.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self._config = {**DEFAULT_CONFIG, **(config or {})}

        # Impact matrix: (source, target) → list of observations
        self._observations: Dict[Tuple[str, str], List[ImpactEntry]] = {}
        # Morphological states (customizable)
        self._morpho_states: Dict[str, List[str]] = {
            k: list(v) for k, v in DEFAULT_MORPHOLOGICAL_STATES.items()
        }
        self._total_observations = 0

        logger.info(
            "🔗  CrossImpactEngine initialized "
            f"({len(PEST_CATEGORIES)}×{len(PEST_CATEGORIES)} matrix)"
        )

    # ── Properties ────────────────────────────────────────────────────────

    @property
    def config(self) -> Dict[str, Any]:
        return dict(self._config)

    @property
    def categories(self) -> Tuple[str, ...]:
        return PEST_CATEGORIES

    @property
    def total_observations(self) -> int:
        return self._total_observations

    # ── Core: Record impact observation ───────────────────────────────────

    def record_impact(
        self,
        source: str,
        target: str,
        strength: float = 0.5,
        signal_id: str = "",
    ) -> Dict[str, Any]:
        """
        Record an observed impact between two PEST dimensions.

        Args:
            source: Source PEST category
            target: Target PEST category
            strength: Impact strength (0-1)
            signal_id: Optional signal ID

        Returns:
            Dict with recorded impact info
        """
        if source not in PEST_CATEGORIES:
            raise ValueError(f"Invalid source: {source}. Valid: {list(PEST_CATEGORIES)}")
        if target not in PEST_CATEGORIES:
            raise ValueError(f"Invalid target: {target}. Valid: {list(PEST_CATEGORIES)}")
        if source == target:
            raise ValueError("Source and target must be different")

        strength = max(0.0, min(1.0, strength))

        entry = ImpactEntry(
            source=source,
            target=target,
            signal_id=signal_id,
            strength=strength,
        )

        pair = (source, target)
        if pair not in self._observations:
            self._observations[pair] = []

        store = self._observations[pair]
        max_entries = self._config["max_entries_per_pair"]
        if len(store) >= max_entries:
            store.pop(0)

        store.append(entry)
        self._total_observations += 1

        return {
            "status": "recorded",
            "source": source,
            "target": target,
            "strength": round(strength, 4),
            "pair_observations": len(store),
        }

    def record_from_pest_results(
        self,
        pest_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Infer impact observations from PEST classification results.

        When a signal has both primary and secondary PEST categories,
        we infer a co-occurrence impact: primary → secondary.

        Args:
            pest_results: List of PEST classification dicts with
                'primary', 'secondary', 'confidence', optional 'signal_id'

        Returns:
            Dict with processing stats
        """
        recorded = 0
        skipped = 0

        for pr in pest_results:
            primary = pr.get("primary", "")
            secondary = pr.get("secondary", None) or pr.get("secondary", None)
            confidence = float(pr.get("confidence", 0.0))
            sig_id = pr.get("signal_id", "")

            if not primary or not secondary:
                skipped += 1
                continue

            if primary not in PEST_CATEGORIES or secondary not in PEST_CATEGORIES:
                skipped += 1
                continue

            if primary == secondary:
                skipped += 1
                continue

            try:
                self.record_impact(
                    source=primary,
                    target=secondary,
                    strength=confidence,
                    signal_id=sig_id,
                )
                recorded += 1
            except ValueError:
                skipped += 1

        return {"recorded": recorded, "skipped": skipped}

    def batch_record(self, impacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Record multiple explicit impacts."""
        recorded = 0
        failed = 0
        for imp in impacts:
            try:
                self.record_impact(
                    source=imp["source"],
                    target=imp["target"],
                    strength=float(imp.get("strength", 0.5)),
                    signal_id=imp.get("signal_id", ""),
                )
                recorded += 1
            except Exception as exc:
                logger.warning(f"⚠️ batch_record failed: {exc}")
                failed += 1
        return {"recorded": recorded, "failed": failed}

    # ── Core: Get Impact Matrix ───────────────────────────────────────────

    def get_matrix(self) -> Dict[str, Any]:
        """
        Compute the 4×4 cross-impact matrix.

        Returns matrix[source][target] = avg impact strength (0-1).
        Diagonal is always 0 (self-impact not measured).
        """
        min_obs = self._config["min_observations"]
        matrix: Dict[str, Dict[str, float]] = {}
        details: Dict[str, Dict[str, Dict[str, Any]]] = {}

        for src in PEST_CATEGORIES:
            matrix[src] = {}
            details[src] = {}
            for tgt in PEST_CATEGORIES:
                if src == tgt:
                    matrix[src][tgt] = 0.0
                    details[src][tgt] = {"count": 0, "significant": False}
                    continue

                obs = self._observations.get((src, tgt), [])
                count = len(obs)

                if count == 0:
                    avg = 0.0
                    significant = False
                else:
                    avg = sum(e.strength for e in obs) / count
                    significant = count >= min_obs

                matrix[src][tgt] = round(avg, 4)
                details[src][tgt] = {
                    "count": count,
                    "avg_strength": round(avg, 4),
                    "significant": significant,
                }

        return {
            "matrix": matrix,
            "details": details,
            "total_observations": self._total_observations,
        }

    def get_strongest_impacts(self, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Get the top-N strongest impact pairs.
        """
        min_obs = self._config["min_observations"]
        impacts = []

        for (src, tgt), obs in self._observations.items():
            count = len(obs)
            if count < min_obs:
                continue
            avg = sum(e.strength for e in obs) / count
            impacts.append({
                "source": src,
                "target": tgt,
                "avg_strength": round(avg, 4),
                "observation_count": count,
            })

        impacts.sort(key=lambda x: x["avg_strength"], reverse=True)
        return impacts[:top_n]

    # ── Core: Causal Chain Detection ──────────────────────────────────────

    def detect_causal_chains(
        self,
        min_strength: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """
        Detect causal chains through PEST dimensions.

        Example: Political → Economic → Social (policy affects economy
        which affects society).

        Returns chains of length 2+ ordered by total strength.
        """
        min_obs = self._config["min_observations"]
        max_len = self._config["max_chain_length"]

        # Build adjacency with avg strengths
        adj: Dict[str, List[Tuple[str, float, int]]] = defaultdict(list)
        for (src, tgt), obs in self._observations.items():
            count = len(obs)
            if count < min_obs:
                continue
            avg = sum(e.strength for e in obs) / count
            if avg >= min_strength:
                adj[src].append((tgt, avg, count))

        # DFS to find all chains
        chains: List[CausalChain] = []

        def dfs(path: List[str], total_str: float, total_count: int):
            current = path[-1]
            if len(path) >= 3:  # At least 3 nodes = 2 edges
                chains.append(CausalChain(
                    chain=list(path),
                    total_strength=round(total_str, 4),
                    evidence_count=total_count,
                ))
            if len(path) >= max_len:
                return
            for (nxt, strength, count) in adj.get(current, []):
                if nxt not in path:
                    dfs(
                        path + [nxt],
                        total_str + strength,
                        total_count + count,
                    )

        for start in PEST_CATEGORIES:
            dfs([start], 0.0, 0)

        chains.sort(key=lambda c: c.total_strength, reverse=True)
        return [c.to_dict() for c in chains]

    # ── Core: Morphological Analysis ──────────────────────────────────────

    def set_morphological_states(
        self,
        states: Dict[str, List[str]],
    ) -> None:
        """Set custom states for morphological analysis."""
        for cat in PEST_CATEGORIES:
            if cat in states:
                self._morpho_states[cat] = list(states[cat])

    def get_morphological_states(self) -> Dict[str, List[str]]:
        """Get current morphological states."""
        return {k: list(v) for k, v in self._morpho_states.items()}

    def generate_scenarios(
        self,
        max_scenarios: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Generate morphological scenarios by combining PEST states.

        Uses the CIM to assess plausibility: scenarios where
        high-impact pairs are aligned score higher.

        Returns top-N most plausible scenarios.
        """
        matrix_data = self.get_matrix()
        matrix = matrix_data["matrix"]

        all_scenarios: List[MorphologicalScenario] = []

        # Generate cross-product of states (limited)
        # With 4 dims × 4 states = 256 combos — manageable
        states_lists = [
            [(cat, state) for state in self._morpho_states.get(cat, ["default"])]
            for cat in PEST_CATEGORIES
        ]

        def cross_product(lists, current=None):
            if current is None:
                current = []
            if not lists:
                yield dict(current)
                return
            for item in lists[0]:
                yield from cross_product(lists[1:], current + [item])

        for dims in cross_product(states_lists):
            plausibility = self._compute_scenario_plausibility(dims, matrix)
            name = " + ".join(
                f"{cat[:1]}:{state[:20]}" for cat, state in dims.items()
            )
            scenario = MorphologicalScenario(
                name=name,
                dimensions=dims,
                plausibility=round(plausibility, 4),
                description=self._describe_scenario(dims),
            )
            all_scenarios.append(scenario)

        # Sort by plausibility and return top N
        all_scenarios.sort(key=lambda s: s.plausibility, reverse=True)
        threshold = self._config["plausibility_threshold"]
        filtered = [s for s in all_scenarios if s.plausibility >= threshold]

        result = filtered[:max_scenarios]
        return [s.to_dict() for s in result]

    def _compute_scenario_plausibility(
        self,
        dims: Dict[str, str],
        matrix: Dict[str, Dict[str, float]],
    ) -> float:
        """
        Score scenario plausibility based on CIM.

        States with positive indices (first half) align with high impacts,
        states with negative indices (second half) represent disruption.
        """
        categories = list(dims.keys())
        plausibility = 0.5  # base

        for i, src in enumerate(categories):
            for j, tgt in enumerate(categories):
                if i == j:
                    continue
                impact = matrix.get(src, {}).get(tgt, 0.0)
                # State indices: 0,1 = "positive", 2,3 = "disruptive"
                src_states = self._morpho_states.get(src, [])
                tgt_states = self._morpho_states.get(tgt, [])
                src_idx = src_states.index(dims[src]) if dims[src] in src_states else 0
                tgt_idx = tgt_states.index(dims[tgt]) if dims[tgt] in tgt_states else 0

                # Positive pairs (both positive or both disruptive) = more plausible
                both_positive = src_idx < 2 and tgt_idx < 2
                both_disruptive = src_idx >= 2 and tgt_idx >= 2
                alignment = 1.0 if (both_positive or both_disruptive) else -0.5

                plausibility += impact * alignment * 0.1

        return max(0.0, min(1.0, plausibility))

    def _describe_scenario(self, dims: Dict[str, str]) -> str:
        """Generate a brief description of a scenario."""
        parts = []
        for cat, state in dims.items():
            short_cat = cat[0]  # P, E, S, T
            parts.append(f"[{short_cat}] {state}")
        return "; ".join(parts)

    # ── Statistics ────────────────────────────────────────────────────────

    def stats(self) -> Dict[str, Any]:
        """Engine statistics."""
        active_pairs = len(self._observations)
        obs_counts = {
            f"{src}→{tgt}": len(obs)
            for (src, tgt), obs in self._observations.items()
        }
        return {
            "engine": "CrossImpactEngine",
            "version": "1.0.0",
            "categories": list(PEST_CATEGORIES),
            "matrix_size": f"{len(PEST_CATEGORIES)}x{len(PEST_CATEGORIES)}",
            "total_observations": self._total_observations,
            "active_pairs": active_pairs,
            "observation_counts": obs_counts,
            "morphological_states": {
                cat: len(states)
                for cat, states in self._morpho_states.items()
            },
        }

    # ── Persistence ───────────────────────────────────────────────────────

    def export_data(self) -> Dict[str, Any]:
        """Export matrix + observations."""
        return {
            "matrix": self.get_matrix(),
            "observations_count": self._total_observations,
            "morphological_states": self.get_morphological_states(),
        }

    def reset(self) -> None:
        """Reset all state (for testing)."""
        self._observations.clear()
        self._total_observations = 0
        self._morpho_states = {
            k: list(v) for k, v in DEFAULT_MORPHOLOGICAL_STATES.items()
        }

    def simulate_economic_shock(self, intensity: float = 0.8) -> Dict[str, Any]:
        """
        Simula um Choque Econômico e sua propagação para Círculos Culturais (V9.5).
        Mapeia como a queda no E impacta o aumento do 'Corre' e 'Improviso'.
        """
        results = {
            "initial_event": "Choque Inflacionário / Desemprego",
            "intensity": intensity,
            "cascading_impacts": [
                {"dim": "Economic", "change": -0.6 * intensity, "label": "Queda no Poder de Compra"},
                {"dim": "Social", "change": 0.9 * intensity, "label": "Ativação do DNA de Resiliência ('O Corre')"},
                {"dim": "Technological", "change": 0.4 * intensity, "label": "Busca por Soluções de Baixo Custo (Improviso Tech)"}
            ],
            "cultural_activation": {
                "improviso_criatividade": 0.85 * intensity,
                "trabalho_conquista": 0.75 * intensity,
                "festa_celebracao": -0.4 * intensity,  # Queda na celebração supérflua
                "religiosidade_popular": 0.3 * intensity # Aumento na busca por suporte espiritual
            }
        }
        return results

    def simulate_by_lens(self, lens: str, signal_alpha: float = 0.0, signal_slope: float = 0.0) -> Dict[str, Any]:
        """
        Calcula a propagação de impacto baseada na Lente do Onboarding e Alpha/Slope (V9.5).
        
        - Lente PROTECAO: Foca em contenção de riscos e estabilidade (ARI).
        - Lente ACAO: Foca em aceleração de ROI e Momentum.
        - Lente EXPLORACAO: Foca em ruptura e detecção de sinais fracos (Alpha).
        """
        
        # Ajuste de base pela aceleração (Slope)
        # Se Slope > 0, o impacto é amplificado (efeito rede)
        slope_multiplier = 1.0 + (max(0, signal_slope) * 2.0)
        
        base_impacts = {
            "PROTECAO": {
                "chain_type": "Cadeia de Contenção",
                "focus": "Risk & Stability (ARI)",
                "rules": [
                    {"step": "E -> S", "multiplier": 1.4, "label": "Vulnerabilidade Social"},
                    {"step": "S -> P", "multiplier": 1.2, "label": "Pressão Regulatória"}
                ],
                "alpha_threshold": 0.4 # Ignora sinais fracos instáveis
            },
            "ACAO": {
                "chain_type": "Cadeia de Oportunidade",
                "focus": "Momentum & Growth",
                "rules": [
                    {"step": "T -> S", "multiplier": 1.5, "label": "Adoção Comportamental"},
                    {"step": "S -> E", "multiplier": 1.3, "label": "Conversão de Consumo"}
                ],
                "alpha_threshold": 0.6 # Exige sinais com tração mínima
            },
            "EXPLORACAO": {
                "chain_type": "Cadeia de Ruptura",
                "focus": "Pioneering & Dissonance",
                "rules": [
                    {"step": "S -> P", "multiplier": 1.6, "label": "Desafio ao Status Quo"},
                    {"step": "P -> T", "multiplier": 1.4, "label": "Novos Mercados Tech"}
                ],
                "alpha_threshold": 0.1 # Valoriza sinais fracos/oceano azul
            }
        }
        
        lens_config = base_impacts.get(lens, base_impacts["ACAO"])
        
        # Simulação da propagação
        propagation = []
        for rule in lens_config["rules"]:
            propagated_strength = signal_alpha * rule["multiplier"] * slope_multiplier
            propagation.append({
                "path": rule["step"],
                "label": rule["label"],
                "projected_strength": round(min(1.0, propagated_strength), 4),
                "is_significant": propagated_strength > lens_config["alpha_threshold"]
            })
            
        return {
            "lens": lens,
            "chain_type": lens_config["chain_type"],
            "focus": lens_config["focus"],
            "slope_amplification": round(slope_multiplier, 2),
            "propagation_path": propagation
        }

    def get_causal_chains(self, limit: int = 5) -> List[CausalChain]:
        """
        Obter as principais cadeias causais com base na matriz de impacto.
        Limite o número de cadeias retornadas.
        """
        min_obs = self._config["min_observations"]
        chains: List[CausalChain] = []

        for (src, tgt), obs in self._observations.items():
            count = len(obs)
            if count < min_obs:
                continue
            avg = sum(e.strength for e in obs) / count
            chains.append(CausalChain(
                chain=[src, tgt],
                total_strength=round(avg, 4),
                evidence_count=count,
            ))

        chains.sort(key=lambda c: c.total_strength, reverse=True)
        return [c.to_dict() for c in chains[:limit]]


# ═══════════════════════════════════════════════════════════════════════════════
#  Singleton
# ═══════════════════════════════════════════════════════════════════════════════

_engine: Optional[CrossImpactEngine] = None


def get_cross_impact_engine() -> CrossImpactEngine:
    """Get or create singleton."""
    global _engine
    if _engine is None:
        _engine = CrossImpactEngine()
    return _engine


def reset_cross_impact_engine() -> None:
    """Reset singleton (for testing)."""
    global _engine
    _engine = None
