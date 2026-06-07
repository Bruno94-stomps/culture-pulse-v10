#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cluster Labeler — Culture Pulse V9.1
======================================
Gera labels legíveis para clusters culturais usando TF-IDF das keywords
discriminativas de cada cluster. Complementa o cluster_stability.py
(que compara clusters temporalmente) com nomes legíveis.

Processo:
  1. Recebe sinais agrupados por cluster_id
  2. Aplica TF-IDF nos textos de cada cluster
  3. Extrai top-N termos discriminativos (que diferenciam um cluster dos outros)
  4. Gera label legível: "Cultura Digital & Streaming" (baseado nos termos)

Integração com cluster_stability:
  - ClusterStabilityAnalyzer gera snapshots com labels numéricos
  - ClusterLabeler transforma labels numéricos em nomes legíveis

Uso:
    from core.clustering import get_cluster_labeler
    labeler = get_cluster_labeler()
    labels = labeler.label_clusters(signals_by_cluster)
    # {"0": {"label": "Funk & Periferia", "keywords": ["funk", "baile", ...], "size": 23}, ...}
"""

import logging
import math
import re
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple

from config import config

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
#  Stopwords PT-BR (compacta)
# ═══════════════════════════════════════════════════════════════════════════════

_STOPWORDS_PT = frozenset(
    "a o e de da do das dos em no na nos nas um uma uns umas que é "
    "para por com não se mais seu sua seus suas como ao aos à às "
    "ou quando muito já também só entre depois sem mesmo antes até "
    "nos foi sobre pode ser são tem foi ter essa esse esta este "
    "pelo pela pelos pelas isso aqui ali lá então tudo ele ela eles elas "
    "me te nos vos lhe lhes meu minha teu tua nós vocês mas pois "
    "qual quais onde porque porquê ainda cada outro outra outros outras "
    "algo alguém ninguém nada tudo toda todo todos todas bem mal "
    "sim dois três etc the and of in for to is was".split()
)

# ═══════════════════════════════════════════════════════════════════════════════
#  TF-IDF Lightweight
# ═══════════════════════════════════════════════════════════════════════════════


def _tokenize(text: str) -> List[str]:
    """Tokenizar texto em palavras (lowercase, sem pontuação, min 3 chars)."""
    text = text.lower()
    tokens = re.findall(r"[a-záàâãéèêíìîóòôõúùûçñ]{3,}", text)
    return [t for t in tokens if t not in _STOPWORDS_PT]


def _compute_tfidf(
    documents: Dict[str, List[str]],
) -> Dict[str, List[Tuple[str, float]]]:
    """Calcular TF-IDF por cluster.
    
    Args:
        documents: {cluster_id: [list of all tokens in that cluster]}
    
    Returns:
        {cluster_id: [(term, tfidf_score), ...] sorted by score desc}
    """
    n_docs = len(documents)
    if n_docs == 0:
        return {}

    # Document frequency (em quantos clusters o termo aparece)
    doc_freq: Counter = Counter()
    cluster_tf: Dict[str, Counter] = {}

    for cid, tokens in documents.items():
        tf = Counter(tokens)
        cluster_tf[cid] = tf
        # Cada termo conta 1x por cluster para DF
        for term in set(tokens):
            doc_freq[term] += 1

    # Calcular TF-IDF
    result: Dict[str, List[Tuple[str, float]]] = {}
    for cid, tf in cluster_tf.items():
        total_tokens = sum(tf.values()) or 1
        scores: List[Tuple[str, float]] = []
        for term, count in tf.items():
            tf_score = count / total_tokens
            idf_score = math.log(1 + n_docs / (1 + doc_freq[term]))
            scores.append((term, tf_score * idf_score))
        scores.sort(key=lambda x: x[1], reverse=True)
        result[cid] = scores

    return result


# ═══════════════════════════════════════════════════════════════════════════════
#  Label Generator
# ═══════════════════════════════════════════════════════════════════════════════

# Mapeamento de termos-chave para categorias legíveis
_CATEGORY_HINTS = {
    "funk": "Funk", "sertanejo": "Sertanejo", "rap": "Rap & Hip-Hop",
    "pagode": "Pagode", "mpb": "MPB", "rock": "Rock",
    "streaming": "Streaming & Digital", "digital": "Digital",
    "tecnologia": "Tecnologia", "inteligência": "IA & Tecnologia",
    "periferia": "Periferia & Comunidade", "comunidade": "Comunidade",
    "gastronomia": "Gastronomia", "comida": "Gastronomia",
    "moda": "Moda", "sustentável": "Sustentabilidade",
    "carnaval": "Carnaval", "futebol": "Futebol",
    "influencer": "Influenciadores", "criador": "Economia Criativa",
    "educação": "Educação", "saúde": "Saúde & Bem-estar",
    "juventude": "Juventude", "família": "Família",
    "natureza": "Natureza & Meio Ambiente", "religião": "Religiosidade",
    "política": "Política", "economia": "Economia",
}


def _generate_label(keywords: List[str], max_parts: int = 3) -> str:
    """Gerar label legível a partir de keywords top do cluster."""
    if not keywords:
        return "Cluster Indefinido"

    parts = []
    used_categories = set()
    for kw in keywords:
        if len(parts) >= max_parts:
            break
        # Tentar mapear para categoria legível
        hint = _CATEGORY_HINTS.get(kw)
        if hint and hint not in used_categories:
            parts.append(hint)
            used_categories.add(hint)
        elif kw.capitalize() not in used_categories and len(parts) < max_parts:
            parts.append(kw.capitalize())
            used_categories.add(kw.capitalize())

    return " & ".join(parts) if parts else keywords[0].capitalize()


# ═══════════════════════════════════════════════════════════════════════════════
#  Engine
# ═══════════════════════════════════════════════════════════════════════════════


class ClusterLabeler:
    """Gera labels legíveis para clusters culturais via TF-IDF."""

    def __init__(self, top_n: int = 5) -> None:
        self._top_n = top_n

    def label_clusters(
        self,
        signals_by_cluster: Dict[str, List[dict]],
    ) -> Dict[str, Dict[str, Any]]:
        """Gerar labels para clusters com consciência de Veracidade (V9.9)."""
        if not signals_by_cluster:
            return {}

        # 1. Calcular confiabilidade média de cada cluster para prefixo de veracidade
        cluster_reliability_prefixes = {}
        for cid, signals in signals_by_cluster.items():
            valid_reliabilities = []
            for s in signals:
                # Tentar extrair reliabilidade do sinal ou da fonte
                rel = s.get('reliability', s.get('confianca', 'MEDIA')).upper()
                valid_reliabilities.append(rel)
            
            most_common_rel = Counter(valid_reliabilities).most_common(1)[0][0]
            
            # Obter label amigável do config centralizado
            # Ex: [SIMULADO] ou [VERIFICADO] baseado no RELIABILITY_LABELS
            if most_common_rel == "BAIXA":
                cluster_reliability_prefixes[cid] = "⚠️ [EXPERIMENTAL] "
            elif most_common_rel == "ALTA":
                cluster_reliability_prefixes[cid] = "✅ [VERIFICADO] "
            else:
                cluster_reliability_prefixes[cid] = ""

        # Construir documentos tokenizados por cluster
        documents: Dict[str, List[str]] = {}
        for cid, signals in signals_by_cluster.items():
            tokens: List[str] = []
            for s in signals:
                text_parts = []
                if s.get("termo"):
                    text_parts.append(str(s["termo"]))
                if s.get("texto"):
                    text_parts.append(str(s["texto"]))
                if s.get("circulo"):
                    text_parts.append(str(s["circulo"]))
                tokens.extend(_tokenize(" ".join(text_parts)))
            documents[str(cid)] = tokens

        # TF-IDF
        tfidf = _compute_tfidf(documents)

        # Gerar labels
        result: Dict[str, Dict[str, Any]] = {}
        for cid, scores in tfidf.items():
            top_terms = [term for term, _ in scores[: self._top_n]]
            top_scores = [(term, round(score, 4)) for term, score in scores[: self._top_n]]
            
            # Aplicar prefixo de veracidade ao label final
            base_label = _generate_label(top_terms)
            final_label = f"{cluster_reliability_prefixes.get(cid, '')}{base_label}"
            
            result[cid] = {
                "label": final_label,
                "keywords": top_terms,
                "size": len(signals_by_cluster.get(cid, [])),
                "tfidf_scores": top_scores,
                "reliability_tier": cluster_reliability_prefixes.get(cid, "").strip()
            }
        return result

    def label_from_flat_signals(
        self,
        signals: List[dict],
        cluster_key: str = "cluster_id",
    ) -> Dict[str, Dict[str, Any]]:
        """Agrupar sinais por cluster_key e gerar labels."""
        by_cluster: Dict[str, List[dict]] = defaultdict(list)
        for s in signals:
            cid = s.get(cluster_key)
            if cid is not None:
                by_cluster[str(cid)].append(s)
        return self.label_clusters(by_cluster)


# ═══════════════════════════════════════════════════════════════════════════════
#  Singleton
# ═══════════════════════════════════════════════════════════════════════════════

_labeler: Optional[ClusterLabeler] = None


def get_cluster_labeler() -> ClusterLabeler:
    global _labeler
    if _labeler is None:
        _labeler = ClusterLabeler()
    return _labeler


def reset_cluster_labeler() -> None:
    global _labeler
    _labeler = None
