#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Learning Utils - Culture Pulse V9.1
Resgatado de dashboard/utils.py para suportar o progresso de aprendizado do Active Learning.
"""

import numpy as np
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class LearningAnalytics:
    @staticmethod
    def calculate_trend(historical_data: List[float], periods: int = 5) -> str:
        """
        Calcula tendência dos dados (ex: acurácia do modelo ao longo do tempo).
        Resgatado de dashboard/utils.py:102
        """
        if len(historical_data) < periods:
            return "Dados insuficientes"
        
        recent_avg = np.mean(historical_data[-periods:])
        previous_avg = np.mean(historical_data[-periods*2:-periods]) if len(historical_data) >= periods*2 else historical_data[0]
        
        if previous_avg == 0: return "📈 Subindo (New)"
        
        change = (recent_avg - previous_avg) / previous_avg * 100
        
        if change > 5:
            return f"📈 Subindo ({change:.1f}%)"
        elif change < -5:
            return f"📉 Descendo ({change:.1f}%)"
        else:
            return f"➡️ Estável ({change:.1f}%)"

    @staticmethod
    def normalize_learning_scores(scores: Dict[str, float]) -> Dict[str, float]:
        """
        Normaliza scores de aprendizado para escala 0-100.
        Resgatado de dashboard/utils.py:86
        """
        normalized = {}
        for key, value in scores.items():
            if value <= 1.0:  # Assumir que está em escala 0-1
                normalized[key] = round(value * 100, 2)
            else:
                normalized[key] = round(value, 2)
        return normalized

    @staticmethod
    def get_status_color(score: float) -> str:
        """
        Retorna cor baseada no score de confiança/aprendizado.
        Resgatado de dashboard/utils.py:516
        """
        if score >= 80 or score >= 0.8:
            return "#2ECC71"  # Verde (Alta Confiança)
        elif score >= 60 or score >= 0.6:
            return "#F39C12"  # Laranja (Em Aprendizado)
        else:
            return "#E74C3C"  # Vermelho (Incerteza/Baixa)
