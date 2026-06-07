#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dynamic Reliability Engine V1.0 (V9.9)
=====================================
Calcula a veracidade biográfica (Reliability) de sinais culturais 
baseado em:
1. Fonte do dado (Autoridade base).
2. Evidência Visual (Scraping real vs texto puro).
3. Histórico de Precisão (Performance do StrategyLearner).
4. Feedback do Analista (Active Learning loops).
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# 📸 V9.9 Importação de Cross-Verification Engine
try:
    from core.classifiers.cross_verification import get_cross_verification_engine
    CROSS_VERIFIER_AVAILABLE = True
except ImportError:
    CROSS_VERIFIER_AVAILABLE = False

logger = logging.getLogger(__name__)

class ReliabilityEngine:
    """
    Motor que classifica a confiabilidade de um sinal 
    como ALTA, MEDIA ou BAIXA de forma dinâmica.
    """
    
    def __init__(self, performance_engine: Optional[Any] = None):
        # Integrado com StrategyLearner para histórico de acurácia
        self.performance_engine = performance_engine
        self.cross_verifier = get_cross_verification_engine() if CROSS_VERIFIER_AVAILABLE else None
        
        # Pesos de decisão (V9.9 logic)
        self.weights = {
            'source_authority': 0.4,
            'visual_evidence': 0.4,
            'historical_accuracy': 0.2
        }

    def calculate_reliability(self, signal: Dict, model_accuracy: float = 0.5, batch_context: List[Dict] = None) -> Dict[str, Any]:
        """
        Determina o status de Reliability e o Accuracy Score final.
        """
        source = str(signal.get('source', '') or signal.get('plataforma', '')).lower()
        has_visual = signal.get('visual_proof', False)
        
        # 1. Source Authority (V9.9 logic)
        base_scores = {
            'youtube': 0.95,
            'twitter': 0.85,
            'g1': 0.90,
            'cnn': 0.90,
            'google': 0.85,
            'news': 0.90,
            'rss_cultural': 0.80,
            'spotify': 0.90,
            'instagram': 0.70,  # Fontes simuladas ou via scraping indireto
            'simulated': 0.20
        }
        
        authority = 0.5 # Default
        for key, val in base_scores.items():
            if key in source:
                authority = val
                break
                
        # 2. Visual Proof Multiplier
        # Ter imagem no V9.9 é prova de veracidade (Proof of Life)
        visual_score = 0.95 if has_visual else 0.15
        
        # 3. Final Calculation Score (0.0 a 1.0)
        final_score = (
            (authority * self.weights['source_authority']) +
            (visual_score * self.weights['visual_evidence']) +
            (model_accuracy * self.weights['historical_accuracy'])
        )

        # 🚀 3.1 Cross-Verification Multiplier (V9.9 - NOVO)
        # Se o sinal for confirmado em múltiplas famílias de plataformas, ele ganha um bônus de veracidade.
        cross_verified = False
        if self.cross_verifier and batch_context:
            cross_data = self.cross_verifier.verify_signal_consistency(signal, batch_context)
            if cross_data['is_verified']:
                final_score = min(1.0, final_score + 0.15) # Bônus Cross-Platform
                cross_verified = True
        
        # 4. Map to Label (Reliability Labels V9.9)
        label = "BAIXA"
        if final_score > 0.80:
            label = "ALTA"
        elif final_score > 0.50:
            label = "MEDIA"
            
        # 5. Determine if it's "Verifiable"
        # Um sinal VERIFICADO no V9.9 exige Reliability ALTA OU Confirmação Cross-Platform
        is_verified = (label == "ALTA") or (label == "MEDIA" and has_visual) or (cross_verified)
        
        return {
            'reliability': label,
            'accuracy_score': round(float(final_score), 3),
            'is_verified': is_verified,
            'visual_proof': has_visual,
            'cross_verified': cross_verified,
            'calculation_details': {
                'authority': authority,
                'visual': visual_score,
                'historical': model_accuracy,
                'cross_platform': 0.15 if cross_verified else 0.0
            }
        }

# Singleton helper
_reliability_instance = None
def get_reliability_engine(perf_engine=None) -> ReliabilityEngine:
    global _reliability_instance
    if _reliability_instance is None:
        _reliability_instance = ReliabilityEngine(perf_engine)
    return _reliability_instance
