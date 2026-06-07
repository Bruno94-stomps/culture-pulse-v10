#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dynamic Demographic Engine - Culture Pulse V8.1
Sistema de multiplicadores demográficos dinâmicos baseados em dados reais
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import json
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class DynamicDemographicEngine:
    """
    Engine que calcula multiplicadores demográficos em tempo real
    baseado em padrões de engajamento reais das APIs
    """
    
    def __init__(self):
        self.base_multipliers = self._load_base_multipliers()
        self.engagement_cache = {}
        self.learning_data = defaultdict(list)
        
    def _load_base_multipliers(self) -> Dict[str, Dict[str, float]]:
        """Multiplicadores base como fallback"""
        return {
            "13-17": {
                "funk": 0.9, "hip_hop": 0.8, "sertanejo": 0.3, "mpb": 0.2,
                "tiktok_trends": 0.95, "gaming": 0.85, "memes": 0.9
            },
            "18-24": {
                "funk": 0.8, "hip_hop": 0.9, "sertanejo": 0.5, "mpb": 0.4,
                "carreira": 0.7, "festa": 0.85, "universidade": 0.8
            },
            "25-34": {
                "funk": 0.6, "hip_hop": 0.7, "sertanejo": 0.8, "mpb": 0.6,
                "carreira": 0.9, "familia": 0.7, "empreendedorismo": 0.8
            },
            "35-44": {
                "sertanejo": 0.9, "mpb": 0.8, "rock": 0.7, "familia": 0.9,
                "estabilidade": 0.85, "educacao_filhos": 0.9
            },
            "45+": {
                "mpb": 0.9, "sertanejo": 0.8, "rock_classico": 0.8,
                "tradicao": 0.9, "qualidade": 0.85, "experiencia": 0.9
            }
        }
    
    def calculate_dynamic_multipliers(
        self, 
        api_data: Dict[str, Any], 
        demographic: str,
        time_window: int = 7
    ) -> Dict[str, float]:
        """
        Calcula multiplicadores dinâmicos baseados em dados reais
        
        Args:
            api_data: Dados coletados das APIs
            demographic: Faixa etária (13-17, 18-24, etc.)
            time_window: Janela temporal em dias
            
        Returns:
            Dict com multiplicadores calculados dinamicamente
        """
        logger.info(f"🔄 Calculando multiplicadores dinâmicos para {demographic}")
        
        try:
            # 1. Analisar padrões de engajamento
            engagement_patterns = self._analyze_engagement_patterns(api_data, demographic)
            
            # 2. Detectar trending topics por demografia
            trending_multipliers = self._calculate_trending_multipliers(api_data, demographic)
            
            # 3. Aplicar aprendizado histórico
            historical_adjustments = self._apply_historical_learning(demographic)
            
            # 4. Combinar todas as fontes
            dynamic_multipliers = self._combine_multipliers(
                self.base_multipliers.get(demographic, {}),
                engagement_patterns,
                trending_multipliers,
                historical_adjustments
            )
            
            # 5. Armazenar para aprendizado
            self._store_learning_data(demographic, dynamic_multipliers, api_data)
            
            logger.info(f"✅ Multiplicadores dinâmicos calculados para {demographic}")
            return dynamic_multipliers
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular multiplicadores: {e}")
            return self.base_multipliers.get(demographic, {})
    
    def _analyze_engagement_patterns(self, api_data: Dict[str, Any], demographic: str) -> Dict[str, float]:
        """Analisa padrões de engajamento reais por demografia"""
        patterns = {}
        
        # Analisar dados do YouTube
        if 'youtube_data' in api_data:
            youtube_patterns = self._analyze_youtube_engagement(api_data['youtube_data'], demographic)
            patterns.update(youtube_patterns)
        
        # Analisar dados do Reddit
        if 'reddit_data' in api_data:
            reddit_patterns = self._analyze_reddit_engagement(api_data['reddit_data'], demographic)
            patterns.update(reddit_patterns)
        
        # Analisar dados do Spotify
        if 'spotify_data' in api_data:
            spotify_patterns = self._analyze_spotify_engagement(api_data['spotify_data'], demographic)
            patterns.update(spotify_patterns)
        
        return patterns
    
    def _analyze_youtube_engagement(self, youtube_data: List[Dict], demographic: str) -> Dict[str, float]:
        """Analisa engajamento específico do YouTube por demografia"""
        patterns = {}
        
        for video in youtube_data:
            # Extrair indicadores de engajamento
            views = video.get('views', 0)
            likes = video.get('likes', 0)
            comments = video.get('comments', 0)
            title = video.get('title', '').lower()
            
            # Calcular taxa de engajamento
            engagement_rate = (likes + comments) / max(views, 1) * 100
            
            # Detectar conteúdo relevante para a demografia
            if self._is_demographic_relevant(title, demographic):
                # Categorizar tipo de conteúdo
                content_type = self._categorize_content(title)
                if content_type not in patterns:
                    patterns[content_type] = []
                patterns[content_type].append(engagement_rate)
        
        # Calcular multiplicadores baseados na média de engajamento
        multipliers = {}
        for content_type, rates in patterns.items():
            avg_rate = np.mean(rates)
            # Converter taxa de engajamento para multiplicador (0.1-1.5)
            multiplier = min(1.5, max(0.1, avg_rate / 10))
            multipliers[content_type] = multiplier
        
        return multipliers
    
    def _analyze_reddit_engagement(self, reddit_data: List[Dict], demographic: str) -> Dict[str, float]:
        """Analisa engajamento específico do Reddit por demografia"""
        patterns = {}
        
        for post in reddit_data:
            score = post.get('score', 0)
            comments = post.get('num_comments', 0)
            title = post.get('title', '').lower()
            subreddit = post.get('subreddit', '')
            
            # Calcular relevância demográfica
            if self._is_subreddit_demographic_relevant(subreddit, demographic):
                content_type = self._categorize_content(title)
                engagement_score = (score + comments) / 10  # Normalizar
                
                if content_type not in patterns:
                    patterns[content_type] = []
                patterns[content_type].append(min(engagement_score, 100))
        
        # Converter para multiplicadores
        multipliers = {}
        for content_type, scores in patterns.items():
            avg_score = np.mean(scores)
            multiplier = min(1.5, max(0.1, avg_score / 50))
            multipliers[content_type] = multiplier
        
        return multipliers
    
    def _analyze_spotify_engagement(self, spotify_data: List[Dict], demographic: str) -> Dict[str, float]:
        """Analisa engajamento musical por demografia"""
        patterns = {}
        
        for track in spotify_data:
            popularity = track.get('popularity', 0)
            genres = track.get('genres', [])
            artist_popularity = track.get('artist_popularity', 0)
            
            for genre in genres:
                if genre not in patterns:
                    patterns[genre] = []
                # Combinar popularidade da música e do artista
                combined_score = (popularity + artist_popularity) / 2
                patterns[genre].append(combined_score)
        
        # Converter para multiplicadores musicais
        multipliers = {}
        for genre, scores in patterns.items():
            avg_score = np.mean(scores)
            multiplier = min(1.5, max(0.1, avg_score / 100))
            multipliers[f"musica_{genre}"] = multiplier
        
        return multipliers
    
    def _calculate_trending_multipliers(self, api_data: Dict[str, Any], demographic: str) -> Dict[str, float]:
        """Calcula multiplicadores baseados em trending topics"""
        trending = {}
        
        # Detectar palavras-chave em alta
        trending_keywords = self._extract_trending_keywords(api_data)
        
        for keyword, frequency in trending_keywords.items():
            # Verificar se é relevante para a demografia
            if self._is_keyword_demographic_relevant(keyword, demographic):
                # Converter frequência para multiplicador
                trend_multiplier = min(1.8, max(0.8, frequency / 100))
                trending[f"trend_{keyword}"] = trend_multiplier
        
        return trending
    
    def _apply_historical_learning(self, demographic: str) -> Dict[str, float]:
        """Aplica aprendizado baseado em dados históricos"""
        adjustments = {}
        
        if demographic in self.learning_data:
            recent_data = self.learning_data[demographic][-10:]  # Últimos 10 registros
            
            if recent_data:
                # Calcular tendências de performance
                for key in recent_data[0].keys():
                    values = [data.get(key, 0) for data in recent_data]
                    if len(values) > 1:
                        # Calcular tendência (crescimento/declínio)
                        trend = (values[-1] - values[0]) / len(values)
                        adjustment = 1.0 + (trend * 0.1)  # Ajuste sutil
                        adjustments[f"historical_{key}"] = max(0.5, min(1.5, adjustment))
        
        return adjustments
    
    def _combine_multipliers(self, base: Dict, engagement: Dict, trending: Dict, historical: Dict) -> Dict[str, float]:
        """Combina todos os multiplicadores em um resultado final"""
        combined = {}
        
        # Começar com multiplicadores base
        combined.update(base)
        
        # Aplicar adjustes de engajamento (peso maior)
        for key, value in engagement.items():
            if key in combined:
                combined[key] = (combined[key] * 0.4) + (value * 0.6)  # 60% peso do engajamento
            else:
                combined[key] = value
        
        # Aplicar multiplicadores de trending (peso menor)
        for key, value in trending.items():
            clean_key = key.replace('trend_', '')
            if clean_key in combined:
                combined[clean_key] = (combined[clean_key] * 0.8) + (value * 0.2)  # 20% peso do trending
            else:
                combined[clean_key] = value
        
        # Aplicar ajustes históricos (peso sutil)
        for key, value in historical.items():
            clean_key = key.replace('historical_', '')
            if clean_key in combined:
                combined[clean_key] = combined[clean_key] * value  # Multiplicador direto
        
        return combined
    
    def _is_demographic_relevant(self, content: str, demographic: str) -> bool:
        """Verifica se conteúdo é relevante para a demografia"""
        demographic_keywords = {
            "13-17": ["escola", "ensino", "vestibular", "jovem", "adolescente", "teen"],
            "18-24": ["faculdade", "universidade", "festa", "balada", "carreira", "estágio"],
            "25-34": ["trabalho", "carreira", "relacionamento", "casa", "independência"],
            "35-44": ["família", "filhos", "estabilidade", "casa própria", "educação"],
            "45+": ["aposentadoria", "saúde", "netos", "experiência", "tradição"]
        }
        
        keywords = demographic_keywords.get(demographic, [])
        return any(keyword in content for keyword in keywords)
    
    def _is_subreddit_demographic_relevant(self, subreddit: str, demographic: str) -> bool:
        """Verifica se subreddit é relevante para demografia"""
        subreddit_mapping = {
            "13-17": ["teenagers", "estudantes", "vestibular"],
            "18-24": ["universidades", "faculdade", "jovens"],
            "25-34": ["carreira", "relacionamentos", "brasil"],
            "35-44": ["pais", "família", "casados"],
            "45+": ["aposentadoria", "maduros", "tradicional"]
        }
        
        relevant_subs = subreddit_mapping.get(demographic, [])
        return any(sub in subreddit.lower() for sub in relevant_subs)
    
    def _is_keyword_demographic_relevant(self, keyword: str, demographic: str) -> bool:
        """Verifica se keyword trending é relevante para demografia"""
        return True  # Por enquanto, considerar todas relevantes
    
    def _categorize_content(self, content: str) -> str:
        """Categoriza tipo de conteúdo"""
        categories = {
            "music": ["música", "cantora", "cantor", "banda", "album", "música"],
            "sports": ["futebol", "esporte", "jogo", "time", "atleta"],
            "entertainment": ["filme", "serie", "ator", "atriz", "novela"],
            "lifestyle": ["moda", "beleza", "casa", "decoração", "viagem"],
            "technology": ["tech", "celular", "app", "internet", "digital"],
            "news": ["notícia", "política", "economia", "brasil"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in content for keyword in keywords):
                return category
        
        return "general"
    
    def _extract_trending_keywords(self, api_data: Dict[str, Any]) -> Dict[str, int]:
        """Extrai palavras-chave em trending"""
        keyword_freq = defaultdict(int)
        
        # Processar todos os textos disponíveis
        all_texts = []
        
        for source, data in api_data.items():
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        text = item.get('title', '') + ' ' + item.get('description', '')
                        all_texts.append(text.lower())
        
        # Contar frequência de palavras relevantes (filtrar palavras muito comuns)
        stop_words = {'de', 'da', 'do', 'das', 'dos', 'e', 'o', 'a', 'os', 'as', 'em', 'no', 'na', 'para', 'com'}
        
        for text in all_texts:
            words = text.split()
            for word in words:
                word = word.strip('.,!?')
                if len(word) > 3 and word not in stop_words:
                    keyword_freq[word] += 1
        
        # Retornar apenas palavras com frequência significativa
        return {k: v for k, v in keyword_freq.items() if v >= 3}
    
    def _store_learning_data(self, demographic: str, multipliers: Dict[str, float], api_data: Dict[str, Any]):
        """Armazena dados para aprendizado futuro"""
        learning_entry = {
            'timestamp': datetime.now().isoformat(),
            'multipliers': multipliers,
            'data_volume': sum(len(data) if isinstance(data, list) else 1 for data in api_data.values())
        }
        
        self.learning_data[demographic].append(learning_entry)
        
        # Manter apenas últimos 50 registros por demografia
        if len(self.learning_data[demographic]) > 50:
            self.learning_data[demographic] = self.learning_data[demographic][-50:]
    
    def get_multiplier_insights(self, demographic: str) -> Dict[str, Any]:
        """Retorna insights sobre os multiplicadores calculados"""
        insights = {
            'demographic': demographic,
            'total_multipliers': len(self.base_multipliers.get(demographic, {})),
            'learning_history_count': len(self.learning_data.get(demographic, [])),
            'last_update': None,
            'top_performing_categories': [],
            'trending_factors': []
        }
        
        if demographic in self.learning_data and self.learning_data[demographic]:
            latest = self.learning_data[demographic][-1]
            insights['last_update'] = latest['timestamp']
            
            # Top performing categories
            multipliers = latest['multipliers']
            sorted_multipliers = sorted(multipliers.items(), key=lambda x: x[1], reverse=True)
            insights['top_performing_categories'] = sorted_multipliers[:5]
        
        return insights

# Função para integração com o dashboard existente
def enhance_demographic_analysis(api_data: Dict[str, Any], demographic: str) -> Dict[str, float]:
    """
    Função principal para integrar com o dashboard existente
    Substitui os multiplicadores fixos por dinâmicos
    """
    engine = DynamicDemographicEngine()
    return engine.calculate_dynamic_multipliers(api_data, demographic)

if __name__ == "__main__":
    # Teste básico
    engine = DynamicDemographicEngine()
    
    # Dados de teste
    test_api_data = {
        'youtube_data': [
            {'title': 'Funk carioca 2024', 'views': 100000, 'likes': 5000, 'comments': 500},
            {'title': 'Carreira tech para jovens', 'views': 50000, 'likes': 2000, 'comments': 200}
        ],
        'reddit_data': [
            {'title': 'Melhor faculdade SP', 'score': 150, 'num_comments': 45, 'subreddit': 'universidades'}
        ]
    }
    
    multipliers = engine.calculate_dynamic_multipliers(test_api_data, "18-24")
    print("✅ Multiplicadores dinâmicos calculados:")
    for key, value in multipliers.items():
        print(f"  {key}: {value:.3f}")