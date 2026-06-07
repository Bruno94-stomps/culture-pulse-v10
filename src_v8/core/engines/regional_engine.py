"""
🗺️ Regional Engine V9.1 - Pulso Cultural Core
Sistema de Predição de Reações Regionais Brasileiras

Diferencial Competitivo: Mapeia reações específicas por região (Sul, Sudeste, Nordeste, Norte, Centro-Oeste)
baseado em 16 círculos culturais e sensibilidades locais.

Status: Integrado à Versão 9.1 (API-First)
"""

import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class Region(Enum):
    """Regiões brasileiras para análise regionalizada"""
    SUL = "Sul"
    SUDESTE = "Sudeste"
    NORDESTE = "Nordeste"
    NORTE = "Norte"
    CENTRO_OESTE = "Centro-Oeste"

class Sentiment(Enum):
    """Sentimentos previstos na análise regional"""
    MUITO_POSITIVO = "Muito Positivo"
    POSITIVO = "Positivo"
    NEUTRO = "Neutro"
    NEGATIVO = "Negativo"
    MUITO_NEGATIVO = "Muito Negativo"

class RiskLevel(Enum):
    """Níveis de risco cultural"""
    BAIXO = "Baixo"
    MEDIO = "Médio"
    ALTO = "Alto"
    CRITICO = "Crítico"

@dataclass
class RegionalPrediction:
    """Estrutura de dados para uma previsão de reação regionalizada"""
    region: str
    ib_score: float
    sentiment: str
    risk_level: str
    confidence: float
    circle_fit_scores: Dict[str, float]
    risk_factors: List[str]
    opportunities: List[str]
    recommended_adaptations: List[str]
    expected_engagement: float

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para exportação via API"""
        return {
            'region': self.region,
            'ib_score': round(self.ib_score, 1),
            'sentiment': self.sentiment,
            'risk_level': self.risk_level,
            'confidence': round(self.confidence, 2),
            'circle_fit_scores': self.circle_fit_scores,
            'risk_factors': self.risk_factors,
            'opportunities': self.opportunities,
            'recommended_adaptations': self.recommended_adaptations,
            'expected_engagement': round(self.expected_engagement, 2)
        }

@dataclass
class GeographicSignal:
    """Sinal cultural mapeado geograficamente"""
    city: str
    state: str
    region: str
    lat: float
    lng: float
    intensity: float # 0.0 a 1.0
    sentiment: float # -1.0 a 1.0
    main_circle: str
    trending_topics: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'city': self.city,
            'state': self.state,
            'region': self.region,
            'coordinates': [self.lat, self.lng],
            'intensity': round(self.intensity, 2),
            'sentiment': round(self.sentiment, 2),
            'main_circle': self.main_circle,
            'trending_topics': self.trending_topics
        }

class RegionalEngine:
    """
    🗺️ RegionalEngine V9.1
    
    Evolução do RegionalPredictor para integração com OrchestratorV9.
    Fornece a camada de inteligência geográfica do Pulso Cultural.
    """
    
    def __init__(self):
        """Inicializa motor regional com perfis antropológicos consolidados"""
        self.regional_profiles = self._load_regional_profiles()
        self.regional_circles = self._load_regional_circles()
        self.regional_sensitivities = self._load_regional_sensitivities()
        self.capitals_geo = {
            "São Paulo": {"lat": -23.5505, "lng": -46.6333, "region": Region.SUDESTE.value, "state": "SP"},
            "Rio de Janeiro": {"lat": -22.9068, "lng": -43.1729, "region": Region.SUDESTE.value, "state": "RJ"},
            "Belo Horizonte": {"lat": -19.9167, "lng": -43.9345, "region": Region.SUDESTE.value, "state": "MG"},
            "Salvador": {"lat": -12.9714, "lng": -38.5014, "region": Region.NORDESTE.value, "state": "BA"},
            "Fortaleza": {"lat": -3.7172, "lng": -38.5284, "region": Region.NORDESTE.value, "state": "CE"},
            "Recife": {"lat": -8.0578, "lng": -34.8778, "region": Region.NORDESTE.value, "state": "PE"},
            "Curitiba": {"lat": -25.4290, "lng": -49.2671, "region": Region.SUL.value, "state": "PR"},
            "Porto Alegre": {"lat": -30.0346, "lng": -51.2177, "region": Region.SUL.value, "state": "RS"},
            "Manaus": {"lat": -3.1190, "lng": -60.0217, "region": Region.NORTE.value, "state": "AM"},
            "Belém": {"lat": -1.4550, "lng": -48.5025, "region": Region.NORTE.value, "state": "PA"},
            "Goiânia": {"lat": -16.6869, "lng": -49.2648, "region": Region.CENTRO_OESTE.value, "state": "GO"},
            "Brasília": {"lat": -15.7801, "lng": -47.9292, "region": Region.CENTRO_OESTE.value, "state": "DF"}
        }
        logger.info("✅ RegionalEngine V9.1 inicializado (5 regiões × 16 círculos)")

    def _load_regional_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Mapeamento de valores e identidade por região brasileira"""
        return {
            Region.SUL.value: {
                'dominant_values': ['tradição', 'qualidade', 'europeu', 'conservadorismo'],
                'cultural_identity': 'Identidade gaúcha/europeia, orgulho regional e conservadorismo',
                'viral_receptivity': 0.68,
                'brand_loyalty': 0.82
            },
            Region.SUDESTE.value: {
                'dominant_values': ['diversidade', 'cosmopolita', 'trabalho', 'modernidade'],
                'cultural_identity': 'Multiculturalismo urbano, centro econômico e diversidade',
                'viral_receptivity': 0.76,
                'brand_loyalty': 0.65
            },
            Region.NORDESTE.value: {
                'dominant_values': ['tradição', 'festa', 'família', 'resistência'],
                'cultural_identity': 'Orgulho nordestino, cultura rica e resistência histórica',
                'viral_receptivity': 0.91,
                'brand_loyalty': 0.78
            },
            Region.NORTE.value: {
                'dominant_values': ['natureza', 'tradição indígena', 'família', 'comunidade'],
                'cultural_identity': 'Amazônia, biodiversidade e povos tradicionais',
                'viral_receptivity': 0.72,
                'brand_loyalty': 0.75
            },
            Region.CENTRO_OESTE.value: {
                'dominant_values': ['agro', 'prosperidade', 'família', 'empreendedorismo'],
                'cultural_identity': 'Agronegócio, modernidade rural e expansão econômica',
                'viral_receptivity': 0.73,
                'brand_loyalty': 0.71
            }
        }

    def _load_regional_circles(self) -> Dict[str, List[Tuple[str, float]]]:
        """Pesos dos círculos culturais dominantes por região"""
        return {
            Region.SUL.value: [
                ('familia_tradicoes', 0.92), ('trabalho_prosperidade', 0.85), ('gastronomia_sabores', 0.81)
            ],
            Region.SUDESTE.value: [
                ('trabalho_prosperidade', 0.91), ('tecnologia_digital', 0.88), ('diversidade_inclusao', 0.85)
            ],
            Region.NORDESTE.value: [
                ('musica_festivais', 0.95), ('familia_tradicoes', 0.91), ('identidade_regional', 0.89)
            ],
            Region.NORTE.value: [
                ('familia_tradicoes', 0.89), ('comunidade_vizinhanca', 0.87), ('sustentabilidade_consumo', 0.84)
            ],
            Region.CENTRO_OESTE.value: [
                ('trabalho_prosperidade', 0.88), ('familia_tradicoes', 0.86), ('ambicoes_sonhos', 0.82)
            ]
        }

    def _load_regional_sensitivities(self) -> Dict[str, List[Dict[str, str]]]:
        """Sensores de backlash cultural local"""
        return {
            Region.SUL.value: [
                {'trigger': 'roça', 'reason': 'Pejorativo no Sul; preferem "campo"', 'severity': 'alta', 'alternative': 'campo, interior'},
                {'trigger': 'sotaque gaúcho como piada', 'reason': 'Orgulho regional forte', 'severity': 'crítica', 'alternative': 'Valorizar identidade gaúcha'}
            ],
            Region.NORDESTE.value: [
                {'trigger': 'sotaque como piada', 'reason': 'Histórico de discriminação', 'severity': 'crítica', 'alternative': 'Valorizar sotaque local'},
                {'trigger': 'estereótipo de pobreza', 'reason': 'Reducionismo ofensivo', 'severity': 'crítica', 'alternative': 'Destacar riqueza cultural'}
            ],
            Region.NORTE.value: [
                {'trigger': 'estereótipo indígena', 'reason': 'Redução a clichês', 'severity': 'crítica', 'alternative': 'Consultar comunidades locais'},
                {'trigger': 'exploração da Amazônia', 'reason': 'Altamente sensível', 'severity': 'alta', 'alternative': 'Focar em preservação'}
            ],
            Region.SUDESTE.value: [
                {'trigger': 'elitismo', 'reason': 'Sensível a exclusão social', 'severity': 'média', 'alternative': 'Enfatizar inclusão'}
            ],
            Region.CENTRO_OESTE.value: [
                {'trigger': 'conflito agrário', 'reason': 'Polarização política alta', 'severity': 'alta', 'alternative': 'Evitar tons políticos'}
            ]
        }

    def predict(self, content: str, theme: str, target_circles: List[str], brand_values: List[str]) -> List[RegionalPrediction]:
        """Gera predições para todas as regiões brasileiras"""
        predictions = []
        for region in Region:
            predictions.append(self._predict_single_region(region.value, content, theme, target_circles, brand_values))
        return sorted(predictions, key=lambda p: p.ib_score, reverse=True)

    def _predict_single_region(self, region: str, content: str, theme: str, circles: List[str], values: List[str]) -> RegionalPrediction:
        """Pipeline de predição para uma única região"""
        circle_fit = self._calculate_circle_fit(region, circles)
        risks = self._detect_risk_factors(region, content)
        ib_score = self._calculate_ib(region, circle_fit, theme, values, risks)
        sentiment = self._predict_sentiment(ib_score, risks)
        risk_level = self._evaluate_risk_level(risks, ib_score)
        opps = self._identify_opportunities(region, circle_fit, theme)
        recs = self._generate_recommendations(region, risks, opps, ib_score)
        conf = self._calculate_confidence(circle_fit, risks)
        eng = self._estimate_engagement(region, ib_score, sentiment)

        return RegionalPrediction(
            region=region, ib_score=ib_score, sentiment=sentiment.value,
            risk_level=risk_level.value, confidence=conf, circle_fit_scores=circle_fit,
            risk_factors=[r['trigger'] for r in risks], opportunities=opps,
            recommended_adaptations=recs, expected_engagement=eng
        )

    def _calculate_circle_fit(self, region: str, target_circles: List[str]) -> Dict[str, float]:
        reg_circles = dict(self.regional_circles[region])
        return {c: reg_circles.get(c, 0.3) for c in target_circles} if target_circles else {"geral": 0.5}

    def _detect_risk_factors(self, region: str, content: str) -> List[Dict[str, str]]:
        content_low = content.lower()
        return [s for s in self.regional_sensitivities.get(region, []) if s['trigger'].lower() in content_low]

    def _calculate_ib(self, region: str, circle_fit: Dict[str, float], theme: str, values: List[str], risks: List[Dict[str, str]]) -> float:
        avg_fit = np.mean(list(circle_fit.values()))
        profile = self.regional_profiles[region]
        theme_align = 1.0 if theme in profile['dominant_values'] else 0.5
        val_align = len(set(values) & set(profile['dominant_values'])) / max(len(values), 1)
        
        penalties = sum([0.35 if r['severity'] == 'crítica' else 0.20 if r['severity'] == 'alta' else 0.10 for r in risks])
        ib = (avg_fit * 0.5 + theme_align * 0.3 + val_align * 0.2) - penalties
        return max(0, min(1.0, ib)) * 100

    def _predict_sentiment(self, ib: float, risks: List[Dict[str, str]]) -> Sentiment:
        if any(r['severity'] == 'crítica' for r in risks): return Sentiment.NEGATIVO
        if ib >= 80: return Sentiment.MUITO_POSITIVO
        if ib >= 65: return Sentiment.POSITIVO
        if ib >= 45: return Sentiment.NEUTRO
        return Sentiment.NEGATIVO

    def _evaluate_risk_level(self, risks: List[Dict[str, str]], ib: float) -> RiskLevel:
        if any(r['severity'] == 'crítica' for r in risks) or ib < 35: return RiskLevel.CRITICO
        if any(r['severity'] == 'alta' for r in risks) or ib < 55: return RiskLevel.ALTO
        return RiskLevel.BAIXO

    def _identify_opportunities(self, region: str, fit: Dict[str, float], theme: str) -> List[str]:
        opps = [f"Afinidade alta com {c}" for c, s in fit.items() if s > 0.85]
        if self.regional_profiles[region]['viral_receptivity'] > 0.8: opps.append("Alta viralidade regional detected")
        return opps

    def _generate_recommendations(self, region: str, risks: List[Dict[str, str]], opps: List[str], ib: float) -> List[str]:
        recs = [f"Trocar '{r['trigger']}' por '{r['alternative']}'" for r in risks]
        if ib < 60: recs.append(f"Reforçar valores: {', '.join(self.regional_profiles[region]['dominant_values'][:2])}")
        return recs

    def _calculate_confidence(self, fit: Dict[str, float], risks: List[Dict[str, str]]) -> float:
        return min((len(fit) * 0.2 + (0.4 if risks else 0.2)), 1.0)

    def _estimate_engagement(self, region: str, ib: float, sentiment: Sentiment) -> float:
        base = self.regional_profiles[region]['viral_receptivity']
        mult = 1.2 if sentiment == Sentiment.MUITO_POSITIVO else 0.4 if sentiment == Sentiment.NEGATIVO else 0.8
        return min(base * (ib/100) * mult, 1.0)

    def get_geographic_spread(self, campaign_text: str) -> List[Dict[str, Any]]:
        """
        Gera a dispersão geográfica de um sinal cultural baseada no texto da campanha
        Simula como o sinal se espalha pelas capitais brasileiras.
        """
        signals = []
        
        # Simulação baseada em palavras-chave e afinidade regional
        text_lower = campaign_text.lower()
        
        # Marcadores de afinidade (simplificado para MVP)
        affinity_map = {
            Region.SUDESTE.value: 1.0, # Base
            Region.NORDESTE.value: 0.8,
            Region.SUL.value: 0.6,
            Region.NORTE.value: 0.5,
            Region.CENTRO_OESTE.value: 0.5
        }
        
        # Ajuste por gírias (V9.1 logic)
        if any(w in text_lower for w in ["corre", "asfalto", "postura", "família"]):
            affinity_map[Region.SUDESTE.value] += 0.2
            affinity_map[Region.NORDESTE.value] += 0.1
            
        for city, info in self.capitals_geo.items():
            base_affinity = affinity_map.get(info['region'], 0.5)
            
            # Variabilidade aleatória controlada (Monte Carlo light)
            intensity = min(1.0, max(0.1, base_affinity * (0.8 + np.random.random() * 0.4)))
            
            signal = GeographicSignal(
                city=city,
                state=info['state'],
                region=info['region'],
                lat=info['lat'],
                lng=info['lng'],
                intensity=intensity,
                sentiment=0.5 + (np.random.random() * 0.5), # Geralmente positivo para campanhas bem feitas
                main_circle=self.regional_circles.get(info['region'], [("Geral", 1.0)])[0][0],
                trending_topics=["#culturapulso", f"#{city.replace(' ', '').lower()}"]
            )
            signals.append(signal.to_dict())
            
        return signals
