#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Collectors Package - Culture Pulse V9.0
Sistema consolidado de coleta de dados

🎯 COLETORES CONSOLIDADOS:
- YouTube API (Real)
- Reddit API (Real) 
- NewsAPI (Real)
- Spotify API (Real)
- IBGE API (Real)
- Instagram/Threads (Simulado)
- Meetup API (Simulado)
- Google Trends (Real)

🚀 MELHORIAS V9.0:
- Sistema de coleta consolidado e funcional
- Integração completa com SecureConfig
- Rate limiting automático
- Cache otimizado
- Error handling robusto
- 8 coletores totalmente funcionais
"""

__version__ = "9.0.0"
__author__ = "Culture Pulse Team"

from .data_collectors import (
    # Classes principais
    CulturalSignal,
    DataCollectorCache,
    
    # Coletores básicos
    YouTubeCollectorV8,
    RedditCollectorV8,
    SpotifyCollectorV8,
    
    # Coletores estendidos (consolidados)
    NewsAPICollectorV8,
    IBGECollectorV8,
    GoogleTrendsCollectorV8,
    
    # Coletores simulados
    InstagramThreadsCollectorV8,
    MeetupCollectorV8,
    
    # Funções utilitárias
    create_unified_collectors,
    test_collectors,
    
    # Cache global
    data_cache
)

from .orchestrator import CulturalDataOrchestrator

# Aliases para compatibilidade
create_data_collectors = create_unified_collectors
CollectorOrchestrator = CulturalDataOrchestrator  # Alias para compatibilidade

__all__ = [
    # Classes de dados
    'CulturalSignal',
    'DataCollectorCache',
    
    # Coletores individuais
    'YouTubeCollectorV8',
    'RedditCollectorV8',
    'SpotifyCollectorV8',
    'NewsAPICollectorV8',
    'IBGECollectorV8',
    'GoogleTrendsCollectorV8',
    'InstagramThreadsCollectorV8',
    'MeetupCollectorV8',
    
    # Orquestrador
    'CulturalDataOrchestrator',
    'CollectorOrchestrator',  # Alias
    
    # Funções utilitárias
    'create_unified_collectors',
    'create_data_collectors',  # Alias
    'test_collectors',
    
    # Cache
    'data_cache'
]
