"""
Analisador de presença de marca no contexto brasileiro
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class BrandPresenceMetrics:
    """Métricas de presença da marca"""
    total_reach: int
    engagement_rate: float
    cultural_relevance: float
    regional_distribution: Dict[str, float]
    demographic_affinity: Dict[str, float]
    content_performance: Dict[str, float]
    conversation_sentiment: Dict[str, float]
    trend_alignment: float

@dataclass
class MarketContext:
    """Contexto de mercado brasileiro"""
    region: str
    segment: str
    competitors: List[str]
    market_share: float
    growth_rate: float
    cultural_factors: List[str]
    local_trends: List[str]

class BrazilianBrandPresenceAnalyzer:
    """Analisador de presença de marca no contexto brasileiro"""
    
    def __init__(self):
        """Inicializar analisador"""
        self._initialize_regional_contexts()
        self._initialize_cultural_segments()
        
    def _initialize_regional_contexts(self):
        """Inicializar contextos regionais"""
        self.regional_contexts = {
            "norte": {
                "population_weight": 0.08,
                "digital_penetration": 0.65,
                "cultural_factors": [
                    "amazônica",
                    "indígena",
                    "ribeirinha"
                ],
                "consumption_patterns": {
                    "online_shopping": 0.55,
                    "social_media": 0.70,
                    "traditional_retail": 0.85
                }
            },
            "nordeste": {
                "population_weight": 0.27,
                "digital_penetration": 0.70,
                "cultural_factors": [
                    "sertaneja",
                    "litorânea",
                    "festividades"
                ],
                "consumption_patterns": {
                    "online_shopping": 0.60,
                    "social_media": 0.85,
                    "traditional_retail": 0.80
                }
            },
            "centro_oeste": {
                "population_weight": 0.08,
                "digital_penetration": 0.75,
                "cultural_factors": [
                    "agronegócio",
                    "moderna",
                    "tradicional"
                ],
                "consumption_patterns": {
                    "online_shopping": 0.70,
                    "social_media": 0.80,
                    "traditional_retail": 0.75
                }
            },
            "sudeste": {
                "population_weight": 0.42,
                "digital_penetration": 0.85,
                "cultural_factors": [
                    "urbana",
                    "multicultural",
                    "inovadora"
                ],
                "consumption_patterns": {
                    "online_shopping": 0.85,
                    "social_media": 0.90,
                    "traditional_retail": 0.70
                }
            },
            "sul": {
                "population_weight": 0.15,
                "digital_penetration": 0.80,
                "cultural_factors": [
                    "européia",
                    "tradicionalista",
                    "tecnológica"
                ],
                "consumption_patterns": {
                    "online_shopping": 0.80,
                    "social_media": 0.85,
                    "traditional_retail": 0.75
                }
            }
        }
        
    def _initialize_cultural_segments(self):
        """Inicializar segmentos culturais"""
        self.cultural_segments = {
            "jovem_urbano": {
                "age_range": (16, 29),
                "digital_affinity": 0.9,
                "cultural_traits": [
                    "conectado",
                    "multicultural",
                    "experiencial"
                ]
            },
            "familia_tradicional": {
                "age_range": (30, 50),
                "digital_affinity": 0.7,
                "cultural_traits": [
                    "valores familiares",
                    "qualidade",
                    "confiança"
                ]
            },
            "maduro_estabelecido": {
                "age_range": (51, 70),
                "digital_affinity": 0.5,
                "cultural_traits": [
                    "tradicional",
                    "conservador",
                    "qualidade"
                ]
            }
        }
        
    def analyze_brand_presence(
        self,
        brand_data: Dict[str, any],
        market_context: MarketContext
    ) -> BrandPresenceMetrics:
        """
        Analisar presença da marca
        
        Args:
            brand_data: Dados da marca
            market_context: Contexto de mercado
            
        Returns:
            Métricas de presença da marca
        """
        # Calcular alcance total
        total_reach = self._calculate_total_reach(
            brand_data,
            market_context.region
        )
        
        # Análise de engajamento
        engagement_rate = self._analyze_engagement(
            brand_data
        )
        
        # Relevância cultural
        cultural_relevance = self._assess_cultural_relevance(
            brand_data,
            market_context
        )
        
        # Distribuição regional
        regional_distribution = self._analyze_regional_distribution(
            brand_data,
            market_context
        )
        
        # Afinidade demográfica
        demographic_affinity = self._analyze_demographic_affinity(
            brand_data
        )
        
        # Performance de conteúdo
        content_performance = self._analyze_content_performance(
            brand_data
        )
        
        # Sentimento das conversações
        conversation_sentiment = self._analyze_conversation_sentiment(
            brand_data
        )
        
        # Alinhamento com tendências
        trend_alignment = self._calculate_trend_alignment(
            brand_data,
            market_context.local_trends
        )
        
        return BrandPresenceMetrics(
            total_reach=total_reach,
            engagement_rate=engagement_rate,
            cultural_relevance=cultural_relevance,
            regional_distribution=regional_distribution,
            demographic_affinity=demographic_affinity,
            content_performance=content_performance,
            conversation_sentiment=conversation_sentiment,
            trend_alignment=trend_alignment
        )
        
    def _calculate_total_reach(
        self,
        brand_data: Dict[str, any],
        region: str
    ) -> int:
        """Calcular alcance total da marca"""
        base_reach = brand_data.get("followers", 0)
        regional_weight = self.regional_contexts[region]["population_weight"]
        digital_penetration = self.regional_contexts[region]["digital_penetration"]
        
        return int(base_reach * regional_weight * digital_penetration)
        
    def _analyze_engagement(
        self,
        brand_data: Dict[str, any]
    ) -> float:
        """Analisar taxa de engajamento"""
        total_interactions = sum([
            brand_data.get("likes", 0),
            brand_data.get("comments", 0) * 2,
            brand_data.get("shares", 0) * 3
        ])
        
        total_reach = brand_data.get("reach", 1)  # evitar divisão por zero
        
        return round(total_interactions / total_reach * 100, 2)
        
    def _assess_cultural_relevance(
        self,
        brand_data: Dict[str, any],
        market_context: MarketContext
    ) -> float:
        """Avaliar relevância cultural"""
        # Análise de alinhamento cultural
        cultural_alignment = self._calculate_cultural_alignment(
            brand_data,
            market_context.cultural_factors
        )
        
        # Análise de ressonância local
        local_resonance = self._analyze_local_resonance(
            brand_data,
            market_context.region
        )
        
        # Análise de autenticidade
        authenticity = self._assess_authenticity(
            brand_data,
            market_context.cultural_factors
        )
        
        # Média ponderada
        weights = {
            "alignment": 0.4,
            "resonance": 0.35,
            "authenticity": 0.25
        }
        
        relevance = (
            cultural_alignment * weights["alignment"] +
            local_resonance * weights["resonance"] +
            authenticity * weights["authenticity"]
        )
        
        return round(relevance * 100, 2)
        
    def _analyze_regional_distribution(
        self,
        brand_data: Dict[str, any],
        market_context: MarketContext
    ) -> Dict[str, float]:
        """Analisar distribuição regional"""
        distribution = {}
        
        for region in self.regional_contexts:
            base_presence = brand_data.get(f"presence_{region}", 0)
            population_weight = self.regional_contexts[region]["population_weight"]
            digital_penetration = self.regional_contexts[region]["digital_penetration"]
            
            distribution[region] = round(
                base_presence * population_weight * digital_penetration,
                2
            )
            
        return distribution
        
    def _analyze_demographic_affinity(
        self,
        brand_data: Dict[str, any]
    ) -> Dict[str, float]:
        """Analisar afinidade demográfica"""
        affinities = {}
        
        for segment, traits in self.cultural_segments.items():
            # Calcular afinidade baseada em traits culturais
            trait_match = self._calculate_trait_match(
                brand_data.get("brand_traits", []),
                traits["cultural_traits"]
            )
            
            # Ajustar por afinidade digital
            digital_alignment = self._calculate_digital_alignment(
                brand_data.get("digital_presence", 0.5),
                traits["digital_affinity"]
            )
            
            affinities[segment] = round(
                (trait_match * 0.7 + digital_alignment * 0.3) * 100,
                2
            )
            
        return affinities
        
    def _analyze_content_performance(
        self,
        brand_data: Dict[str, any]
    ) -> Dict[str, float]:
        """Analisar performance de conteúdo"""
        return {
            "engagement_rate": self._analyze_engagement(brand_data),
            "virality_score": self._calculate_virality(brand_data),
            "retention_rate": self._calculate_retention(brand_data),
            "conversion_rate": self._calculate_conversion(brand_data)
        }
        
    def _analyze_conversation_sentiment(
        self,
        brand_data: Dict[str, any]
    ) -> Dict[str, float]:
        """Analisar sentimento das conversações"""
        return {
            "positive": brand_data.get("positive_sentiment", 0.6),
            "neutral": brand_data.get("neutral_sentiment", 0.3),
            "negative": brand_data.get("negative_sentiment", 0.1)
        }
        
    def _calculate_trend_alignment(
        self,
        brand_data: Dict[str, any],
        local_trends: List[str]
    ) -> float:
        """Calcular alinhamento com tendências"""
        brand_topics = brand_data.get("content_topics", [])
        aligned_trends = set(brand_topics).intersection(set(local_trends))
        
        return round(len(aligned_trends) / len(local_trends) if local_trends else 0, 2)
        
    def _calculate_cultural_alignment(
        self,
        brand_data: Dict[str, any],
        cultural_factors: List[str]
    ) -> float:
        """Calcular alinhamento cultural"""
        brand_factors = brand_data.get("cultural_elements", [])
        matched_factors = set(brand_factors).intersection(set(cultural_factors))
        
        return len(matched_factors) / len(cultural_factors) if cultural_factors else 0
        
    def _analyze_local_resonance(
        self,
        brand_data: Dict[str, any],
        region: str
    ) -> float:
        """Analisar ressonância local"""
        regional_context = self.regional_contexts[region]
        local_engagement = brand_data.get(f"engagement_{region}", 0)
        
        return local_engagement * regional_context["digital_penetration"]
        
    def _assess_authenticity(
        self,
        brand_data: Dict[str, any],
        cultural_factors: List[str]
    ) -> float:
        """Avaliar autenticidade da marca"""
        brand_values = brand_data.get("brand_values", [])
        cultural_alignment = set(brand_values).intersection(set(cultural_factors))
        
        return len(cultural_alignment) / len(cultural_factors) if cultural_factors else 0
        
    def _calculate_trait_match(
        self,
        brand_traits: List[str],
        segment_traits: List[str]
    ) -> float:
        """Calcular correspondência de traits"""
        matched_traits = set(brand_traits).intersection(set(segment_traits))
        return len(matched_traits) / len(segment_traits) if segment_traits else 0
        
    def _calculate_digital_alignment(
        self,
        brand_digital: float,
        segment_digital: float
    ) -> float:
        """Calcular alinhamento digital"""
        return 1 - abs(brand_digital - segment_digital)
        
    def _calculate_virality(
        self,
        brand_data: Dict[str, any]
    ) -> float:
        """Calcular score de viralidade"""
        shares = brand_data.get("shares", 0)
        reach = brand_data.get("reach", 1)
        
        return round(shares / reach * 100, 2)
        
    def _calculate_retention(
        self,
        brand_data: Dict[str, any]
    ) -> float:
        """Calcular taxa de retenção"""
        return brand_data.get("retention_rate", 0.5)
        
    def _calculate_conversion(
        self,
        brand_data: Dict[str, any]
    ) -> float:
        """Calcular taxa de conversão"""
        return brand_data.get("conversion_rate", 0.3)