#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cross-Verification Engine V1.0 (V9.9)
=====================================
Implementa a lógica de "Confirmação Cross-Platform" (Sinal de Densidade).
Um sinal só é 100% verificado se houver evidência em mais de uma família de fonte
ou se a densidade de menções em plataformas diferentes for alta.
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class CrossVerificationEngine:
    """
    Engine para validação cruzada de sinais entre múltiplas plataformas.
    """
    
    def __init__(self):
        # Famílias de fontes para evitar "auto-confirmação" na mesma plataforma
        self.source_families = {
            'video': ['youtube', 'tiktok', 'vimeo'],
            'social': ['reddit', 'twitter', 'x', 'instagram', 'threads'],
            'editorial': ['news', 'rss_cultural', 'g1', 'cnn', 'estadao'],
            'audio': ['spotify', 'deezer', 'podcasts']
        }

    def verify_signal_consistency(self, signal: Dict, batch_context: List[Dict] = None) -> Dict[str, Any]:
        """
        Analisa a consistência de um sinal baseado no contexto de coleta.
        """
        source = signal.get('source', '').lower() or signal.get('plataforma', '').lower()
        title = signal.get('title', '').strip().lower()
        
        # 1. Identificar família da fonte atual
        current_family = 'unknown'
        for family, sources in self.source_families.items():
            if any(s in source for s in sources):
                current_family = family
                break
        
        # 2. Se não houver contexto de lote, a verificação cross-platform falha por falta de dados
        if not batch_context:
            return {
                'is_verified': False, 
                'cross_platform_count': 1,
                'families_found': [current_family],
                'verification_score': 0.1
            }
            
        # 3. Procurar sinais similares no lote (mesmo título ou keywords próximas)
        similarity_count = 0
        other_families = {current_family}
        
        for other in batch_context:
            other_title = other.get('title', '').strip().lower()
            other_source = other.get('source', '').lower() or other.get('plataforma', '').lower()
            
            # Checagem de similaridade simples (V9.9)
            if title in other_title or other_title in title:
                similarity_count += 1
                for family, sources in self.source_families.items():
                    if any(s in other_source for s in sources):
                        other_families.add(family)
        
        # 4. Cálculo de Verificação Cruzada
        # Um sinal é cross-platform verificado se aparecer em > 1 família diferente
        is_cross_verified = len(other_families) >= 2
        verification_score = min(1.0, (len(other_families) * 0.4) + (similarity_count * 0.1))
        
        return {
            'is_verified': is_cross_verified,
            'cross_platform_count': similarity_count,
            'families_found': list(other_families),
            'verification_score': verification_score
        }

# Singleton helper
_cross_instance = None
def get_cross_verification_engine() -> CrossVerificationEngine:
    global _cross_instance
    if _cross_instance is None:
        _cross_instance = CrossVerificationEngine()
    return _cross_instance
