#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Geo-Cultural Mapping Engine - Culture Pulse V8.1
Sistema de mapeamento cultural por localização geográfica precisa
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
import json
import logging

logger = logging.getLogger(__name__)

class GeoCulturalEngine:
    """
    Engine de mapeamento geo-cultural que analisa diferenças culturais
    por bairros, regiões e características geográficas específicas
    """
    
    def __init__(self):
        self.regional_profiles = self._define_regional_profiles()
        self.neighborhood_profiles = self._define_neighborhood_profiles()
        self.cultural_gradients = self._define_cultural_gradients()
        self.socioeconomic_mapping = self._define_socioeconomic_mapping()
    
    def _define_regional_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Define perfis culturais por região/estado brasileiro"""
        return {
            "rio_de_janeiro": {
                "cultural_identity": "carioca_lifestyle",
                "music_preference": {"funk": 0.9, "samba": 0.8, "pagode": 0.85, "hip_hop": 0.7},
                "lifestyle_factors": {
                    "praia_culture": 0.95, "outdoor_life": 0.9, "fashion_conscious": 0.8,
                    "social_energy": 0.9, "rhythm_oriented": 0.95
                },
                "communication_style": "informal_warm",
                "brand_affinity": "authentic_brazilian",
                "economic_indicators": {"tourism": 0.8, "services": 0.9, "creativity": 0.85}
            },
            "sao_paulo": {
                "cultural_identity": "paulistano_cosmopolitan", 
                "music_preference": {"hip_hop": 0.85, "indie": 0.7, "eletronica": 0.8, "rap": 0.9},
                "lifestyle_factors": {
                    "work_culture": 0.95, "urban_life": 0.95, "innovation": 0.9,
                    "efficiency": 0.85, "diversity": 0.9
                },
                "communication_style": "direct_efficient",
                "brand_affinity": "international_quality",
                "economic_indicators": {"business": 0.95, "tech": 0.85, "finance": 0.9}
            },
            "minas_gerais": {
                "cultural_identity": "mineiro_tradicional",
                "music_preference": {"sertanejo": 0.9, "mpb": 0.85, "rock": 0.7, "tradicional": 0.9},
                "lifestyle_factors": {
                    "family_values": 0.95, "tradition": 0.9, "hospitality": 0.95,
                    "food_culture": 0.95, "quality_life": 0.85
                },
                "communication_style": "warm_traditional",
                "brand_affinity": "heritage_quality",
                "economic_indicators": {"mining": 0.8, "agriculture": 0.85, "tourism": 0.7}
            },
            "bahia": {
                "cultural_identity": "baiano_afro_culture",
                "music_preference": {"axe": 0.95, "reggae": 0.8, "funk": 0.7, "afrobeat": 0.9},
                "lifestyle_factors": {
                    "cultural_richness": 0.95, "artistic": 0.9, "spiritual": 0.8,
                    "community": 0.9, "celebration": 0.95
                },
                "communication_style": "expressive_cultural",
                "brand_affinity": "authentic_roots",
                "economic_indicators": {"tourism": 0.9, "culture": 0.95, "agriculture": 0.7}
            },
            "rio_grande_do_sul": {
                "cultural_identity": "gaucho_pride",
                "music_preference": {"sertanejo": 0.8, "rock": 0.85, "tradicional_gaucha": 0.95, "mpb": 0.7},
                "lifestyle_factors": {
                    "regional_pride": 0.95, "tradition": 0.9, "quality_focus": 0.9,
                    "european_influence": 0.8, "rural_values": 0.85
                },
                "communication_style": "formal_proud",
                "brand_affinity": "quality_heritage",
                "economic_indicators": {"agriculture": 0.9, "industry": 0.8, "wine": 0.85}
            }
        }
    
    def _define_neighborhood_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Define perfis culturais específicos por bairro/zona"""
        return {
            # Rio de Janeiro - Bairros
            "copacabana_ipanema": {
                "region": "rio_de_janeiro",
                "profile_type": "elite_beach",
                "cultural_multipliers": {
                    "lifestyle_luxury": 1.8, "fashion": 1.6, "tourism": 1.9,
                    "international": 1.5, "beach_culture": 1.9
                },
                "demographic_skew": {"25-34": 1.3, "35-44": 1.4, "45+": 1.2},
                "socioeconomic": "A/B",
                "brand_affinity": ["luxury", "international", "lifestyle"]
            },
            "zona_sul_geral": {
                "region": "rio_de_janeiro", 
                "profile_type": "middle_upper_beach",
                "cultural_multipliers": {
                    "beach_lifestyle": 1.6, "social_life": 1.5, "culture": 1.4,
                    "fashion": 1.3, "dining": 1.5
                },
                "demographic_skew": {"18-24": 1.2, "25-34": 1.4, "35-44": 1.3},
                "socioeconomic": "B/C",
                "brand_affinity": ["brazilian_premium", "lifestyle", "social"]
            },
            "zona_norte_rio": {
                "region": "rio_de_janeiro",
                "profile_type": "traditional_carioca",
                "cultural_multipliers": {
                    "funk_culture": 1.9, "samba": 1.8, "community": 1.7,
                    "authentic_rio": 1.9, "family_oriented": 1.6
                },
                "demographic_skew": {"13-17": 1.4, "18-24": 1.5, "25-34": 1.3},
                "socioeconomic": "C/D",
                "brand_affinity": ["authentic", "affordable", "community"]
            },
            "zona_oeste_rio": {
                "region": "rio_de_janeiro",
                "profile_type": "suburban_carioca", 
                "cultural_multipliers": {
                    "family_values": 1.7, "community": 1.6, "value_conscious": 1.8,
                    "local_pride": 1.5, "practical": 1.7
                },
                "demographic_skew": {"25-34": 1.3, "35-44": 1.5, "45+": 1.4},
                "socioeconomic": "C/D/E",
                "brand_affinity": ["value", "family", "practical"]
            },
            
            # São Paulo - Regiões
            "vila_madalena_pinheiros": {
                "region": "sao_paulo",
                "profile_type": "creative_professional",
                "cultural_multipliers": {
                    "creative_culture": 1.8, "indie_scene": 1.7, "innovation": 1.6,
                    "artistic": 1.8, "trendsetter": 1.7
                },
                "demographic_skew": {"21-24": 1.4, "25-28": 1.5, "29-34": 1.3},
                "socioeconomic": "A/B",
                "brand_affinity": ["innovative", "creative", "authentic"]
            },
            "centro_sp": {
                "region": "sao_paulo",
                "profile_type": "business_urban",
                "cultural_multipliers": {
                    "business_culture": 1.9, "efficiency": 1.8, "cosmopolitan": 1.6,
                    "time_conscious": 1.9, "quality": 1.5
                },
                "demographic_skew": {"25-34": 1.4, "35-44": 1.5, "21-24": 1.2},
                "socioeconomic": "A/B/C",
                "brand_affinity": ["premium", "efficient", "international"]
            },
            "periferia_sp": {
                "region": "sao_paulo", 
                "profile_type": "working_class_urban",
                "cultural_multipliers": {
                    "hip_hop_culture": 1.9, "community_strength": 1.8, "hustle": 1.9,
                    "authentic_expression": 1.8, "value_consciousness": 1.9
                },
                "demographic_skew": {"13-17": 1.5, "18-24": 1.6, "25-34": 1.4},
                "socioeconomic": "C/D/E",
                "brand_affinity": ["authentic", "affordable", "empowering"]
            },
            
            # Belo Horizonte
            "savassi_funcionarios": {
                "region": "minas_gerais",
                "profile_type": "modern_mineiro",
                "cultural_multipliers": {
                    "cultural_sophistication": 1.5, "gastronomy": 1.7, "tradition_modern": 1.6,
                    "quality_life": 1.6, "family_professional": 1.5
                },
                "demographic_skew": {"25-34": 1.3, "35-44": 1.4, "21-24": 1.2},
                "socioeconomic": "B/C",
                "brand_affinity": ["quality", "traditional", "sophisticated"]
            },
            
            # Salvador
            "pelourinho_centro": {
                "region": "bahia",
                "profile_type": "cultural_historic",
                "cultural_multipliers": {
                    "afro_culture": 1.9, "artistic_expression": 1.8, "tourism_cultural": 1.7,
                    "spiritual": 1.6, "celebration": 1.9
                },
                "demographic_skew": {"18-24": 1.3, "25-34": 1.4, "35-44": 1.2},
                "socioeconomic": "B/C/D",
                "brand_affinity": ["cultural", "authentic", "expressive"]
            }
        }
    
    def _define_cultural_gradients(self) -> Dict[str, Dict[str, float]]:
        """Define gradientes culturais por características geográficas"""
        return {
            "coastal_influence": {
                "beach_lifestyle": 1.8, "relaxed_attitude": 1.6, "tourism_openness": 1.5,
                "outdoor_activities": 1.7, "social_gathering": 1.5
            },
            "urban_density": {
                "efficiency_focus": 1.6, "tech_adoption": 1.5, "diversity_acceptance": 1.7,
                "innovation_openness": 1.6, "time_pressure": 1.8
            },
            "rural_proximity": {
                "family_values": 1.7, "tradition_respect": 1.8, "community_bonds": 1.6,
                "authentic_preference": 1.7, "quality_over_quantity": 1.5
            },
            "economic_hub": {
                "business_mindset": 1.8, "international_exposure": 1.6, "premium_acceptance": 1.5,
                "efficiency_value": 1.7, "status_consciousness": 1.4
            },
            "cultural_heritage": {
                "traditional_values": 1.8, "cultural_pride": 1.9, "authentic_expression": 1.7,
                "community_identity": 1.6, "heritage_respect": 1.8
            }
        }
    
    def _define_socioeconomic_mapping(self) -> Dict[str, Dict[str, float]]:
        """Mapeia características socioeconômicas por região"""
        return {
            "A_high_income": {
                "premium_preference": 1.8, "international_brands": 1.6, "luxury_acceptance": 1.9,
                "quality_focus": 1.7, "status_symbols": 1.5
            },
            "B_upper_middle": {
                "quality_value": 1.6, "brand_consciousness": 1.5, "lifestyle_investment": 1.5,
                "experience_focus": 1.6, "aspiration_driven": 1.4
            },
            "C_middle_class": {
                "value_consciousness": 1.8, "practical_focus": 1.7, "family_priority": 1.6,
                "brand_trust": 1.5, "community_influence": 1.5
            },
            "D_working_class": {
                "price_sensitivity": 1.9, "functionality_focus": 1.8, "community_trust": 1.7,
                "authentic_brands": 1.6, "word_of_mouth": 1.8
            },
            "E_low_income": {
                "necessity_focus": 1.9, "durability_priority": 1.8, "community_reliance": 1.9,
                "local_brands": 1.7, "practical_value": 1.9
            }
        }
    
    def analyze_geo_cultural_fit(
        self, 
        location_input: str, 
        brand_context: str,
        demographic: str = None
    ) -> Dict[str, Any]:
        """
        Analisa fit geo-cultural para uma localização específica
        
        Args:
            location_input: Localização (ex: "Rio de Janeiro - Zona Sul")
            brand_context: Contexto da marca
            demographic: Demografia opcional
            
        Returns:
            Análise completa de fit geo-cultural
        """
        logger.info(f"🗺️ Analisando fit geo-cultural para {location_input}")
        
        # Parse da localização
        parsed_location = self._parse_location(location_input)
        
        # Obter perfis relevantes
        regional_profile = self._get_regional_profile(parsed_location)
        neighborhood_profile = self._get_neighborhood_profile(parsed_location)
        gradient_factors = self._calculate_gradient_factors(parsed_location)
        socioeconomic_factors = self._get_socioeconomic_factors(parsed_location)
        
        # Calcular multiplicadores combinados
        combined_multipliers = self._combine_geo_factors(
            regional_profile, neighborhood_profile, gradient_factors, socioeconomic_factors
        )
        
        # Analisar fit com brand
        brand_fit_score = self._calculate_brand_fit(combined_multipliers, brand_context)
        
        # Gerar insights específicos
        insights = self._generate_geo_insights(parsed_location, combined_multipliers, brand_context)
        
        return {
            'location': parsed_location,
            'regional_profile': regional_profile,
            'neighborhood_profile': neighborhood_profile,
            'cultural_multipliers': combined_multipliers,
            'brand_fit_score': brand_fit_score,
            'insights': insights,
            'recommendations': self._generate_geo_recommendations(insights, brand_fit_score)
        }
    
    def _parse_location(self, location_input: str) -> Dict[str, str]:
        """Parse da entrada de localização em componentes estruturados"""
        parsed = {
            'raw_input': location_input,
            'region': 'brasil',
            'state': None, 
            'city': None,
            'neighborhood': None,
            'zone': None
        }
        
        location_lower = location_input.lower()
        
        # Identificar estados/regiões principais
        region_mapping = {
            'rio de janeiro': {'state': 'rio_de_janeiro', 'city': 'rio_de_janeiro'},
            'são paulo': {'state': 'sao_paulo', 'city': 'sao_paulo'},
            'minas gerais': {'state': 'minas_gerais'},
            'belo horizonte': {'state': 'minas_gerais', 'city': 'belo_horizonte'},
            'salvador': {'state': 'bahia', 'city': 'salvador'},
            'bahia': {'state': 'bahia'},
            'porto alegre': {'state': 'rio_grande_do_sul', 'city': 'porto_alegre'},
            'rio grande do sul': {'state': 'rio_grande_do_sul'}
        }
        
        for region, data in region_mapping.items():
            if region in location_lower:
                parsed.update(data)
                parsed['region'] = data.get('state', region.replace(' ', '_'))
                break
        
        # Identificar zonas/bairros específicos
        zone_mapping = {
            'zona sul': 'zona_sul_geral',
            'copacabana': 'copacabana_ipanema',
            'ipanema': 'copacabana_ipanema',
            'zona norte': 'zona_norte_rio',
            'zona oeste': 'zona_oeste_rio',
            'periferia': 'periferia_sp' if 'são paulo' in location_lower else 'periferia_geral',
            'centro': 'centro_sp' if 'são paulo' in location_lower else 'centro_geral',
            'vila madalena': 'vila_madalena_pinheiros',
            'pinheiros': 'vila_madalena_pinheiros',
            'savassi': 'savassi_funcionarios',
            'funcionários': 'savassi_funcionarios',
            'pelourinho': 'pelourinho_centro'
        }
        
        for zone, zone_id in zone_mapping.items():
            if zone in location_lower:
                parsed['neighborhood'] = zone_id
                parsed['zone'] = zone
                break
        
        return parsed
    
    def _get_regional_profile(self, parsed_location: Dict[str, str]) -> Dict[str, Any]:
        """Obtém perfil regional baseado na localização"""
        region = parsed_location.get('region', 'brasil')
        return self.regional_profiles.get(region, self.regional_profiles.get('brasil', {}))
    
    def _get_neighborhood_profile(self, parsed_location: Dict[str, str]) -> Dict[str, Any]:
        """Obtém perfil de bairro/zona específico"""
        neighborhood = parsed_location.get('neighborhood')
        if neighborhood and neighborhood in self.neighborhood_profiles:
            return self.neighborhood_profiles[neighborhood]
        return {}
    
    def _calculate_gradient_factors(self, parsed_location: Dict[str, str]) -> Dict[str, float]:
        """Calcula fatores de gradiente cultural baseados em características geográficas"""
        factors = {}
        location_str = parsed_location['raw_input'].lower()
        
        # Detectar características geográficas
        if any(term in location_str for term in ['praia', 'costa', 'litoral', 'copacabana', 'ipanema']):
            factors.update(self.cultural_gradients['coastal_influence'])
        
        if any(term in location_str for term in ['centro', 'downtown', 'negócios', 'financeiro']):
            factors.update(self.cultural_gradients['urban_density'])
            factors.update(self.cultural_gradients['economic_hub'])
        
        if any(term in location_str for term in ['interior', 'rural', 'fazenda', 'campo']):
            factors.update(self.cultural_gradients['rural_proximity'])
        
        if any(term in location_str for term in ['histórico', 'cultural', 'tradicional', 'patrimônio']):
            factors.update(self.cultural_gradients['cultural_heritage'])
        
        return factors
    
    def _get_socioeconomic_factors(self, parsed_location: Dict[str, str]) -> Dict[str, float]:
        """Determina fatores socioeconômicos baseado na localização"""
        neighborhood = parsed_location.get('neighborhood')
        
        if neighborhood and neighborhood in self.neighborhood_profiles:
            socioeconomic = self.neighborhood_profiles[neighborhood].get('socioeconomic', 'C')
            
            # Mapear para fatores
            if 'A' in socioeconomic:
                return self.socioeconomic_mapping['A_high_income']
            elif 'B' in socioeconomic:
                return self.socioeconomic_mapping['B_upper_middle'] 
            elif 'C' in socioeconomic:
                return self.socioeconomic_mapping['C_middle_class']
            elif 'D' in socioeconomic:
                return self.socioeconomic_mapping['D_working_class']
            else:
                return self.socioeconomic_mapping['E_low_income']
        
        # Fallback baseado em termos da localização
        location_str = parsed_location['raw_input'].lower()
        
        if any(term in location_str for term in ['luxury', 'premium', 'elite', 'alto padrão']):
            return self.socioeconomic_mapping['A_high_income']
        elif any(term in location_str for term in ['classe média', 'middle', 'centro']):
            return self.socioeconomic_mapping['C_middle_class']
        elif any(term in location_str for term in ['periferia', 'subúrbio', 'popular']):
            return self.socioeconomic_mapping['D_working_class']
        
        return self.socioeconomic_mapping['C_middle_class']  # Default
    
    def _combine_geo_factors(self, regional: Dict, neighborhood: Dict, gradient: Dict, socioeconomic: Dict) -> Dict[str, float]:
        """Combina todos os fatores geo-culturais em multiplicadores finais"""
        combined = {}
        
        # Fatores regionais (peso base)
        for factor in ['music_preference', 'lifestyle_factors']:
            if factor in regional:
                for key, value in regional[factor].items():
                    combined[f"regional_{key}"] = value
        
        # Fatores de bairro (peso alto - mais específico)
        if 'cultural_multipliers' in neighborhood:
            for key, value in neighborhood['cultural_multipliers'].items():
                combined[f"neighborhood_{key}"] = value * 1.2  # Boost por ser mais específico
        
        # Fatores de gradiente (peso médio)
        for key, value in gradient.items():
            combined[f"gradient_{key}"] = value * 0.8
        
        # Fatores socioeconômicos (peso alto para brand fit)
        for key, value in socioeconomic.items():
            combined[f"socioeco_{key}"] = value * 1.1
        
        return combined
    
    def _calculate_brand_fit(self, multipliers: Dict[str, float], brand_context: str) -> float:
        """Calcula score de fit entre multiplicadores geo-culturais e contexto da marca"""
        brand_words = brand_context.lower().split()
        total_score = 0
        matching_factors = 0
        
        for multiplier_key, multiplier_value in multipliers.items():
            for brand_word in brand_words:
                # Verificar match semântico entre palavra da marca e fator cultural
                if self._semantic_match(brand_word, multiplier_key):
                    total_score += multiplier_value * 10
                    matching_factors += 1
        
        # Normalizar score (0-100)
        if matching_factors > 0:
            return min(100, total_score / matching_factors * 10)
        
        return 50  # Score neutro se não há matches claros
    
    def _semantic_match(self, brand_word: str, cultural_factor: str) -> bool:
        """Verifica match semântico entre palavra da marca e fator cultural"""
        # Remover prefixos dos fatores
        clean_factor = cultural_factor.replace('regional_', '').replace('neighborhood_', '').replace('gradient_', '').replace('socioeco_', '')
        
        # Matches diretos
        if brand_word in clean_factor or clean_factor in brand_word:
            return True
        
        # Matches semânticos
        semantic_mapping = {
            'luxury': ['premium', 'high_income', 'elite', 'sophisticated'],
            'authentic': ['traditional', 'cultural', 'heritage', 'roots'],
            'young': ['teen', 'university', 'early_career', 'trendsetter'],
            'family': ['family_values', 'community', 'traditional'],
            'urban': ['city', 'metropolitan', 'cosmopolitan', 'modern'],
            'lifestyle': ['life', 'living', 'culture', 'style'],
            'music': ['funk', 'samba', 'hip_hop', 'mpb', 'rhythm'],
            'beach': ['coastal', 'praia', 'summer', 'relaxed'],
            'fashion': ['style', 'trendy', 'modern', 'design']
        }
        
        for concept, related_terms in semantic_mapping.items():
            if brand_word == concept or brand_word in related_terms:
                return any(term in clean_factor for term in related_terms)
        
        return False
    
    def _generate_geo_insights(self, location: Dict, multipliers: Dict, brand_context: str) -> List[str]:
        """Gera insights específicos baseados na análise geo-cultural"""
        insights = []
        
        # Insight sobre localização
        if location.get('neighborhood'):
            neighborhood = self.neighborhood_profiles.get(location['neighborhood'], {})
            if neighborhood:
                insights.append(f"📍 Região {neighborhood.get('profile_type', 'específica')} com perfil socioeconômico {neighborhood.get('socioeconomic', 'misto')}")
        
        # Insights sobre multiplicadores mais altos
        top_multipliers = sorted(multipliers.items(), key=lambda x: x[1], reverse=True)[:3]
        for factor, value in top_multipliers:
            if value > 1.5:
                clean_factor = factor.replace('regional_', '').replace('neighborhood_', '').replace('gradient_', '').replace('socioeco_', '')
                insights.append(f"🎯 Alta afinidade com {clean_factor.replace('_', ' ')} (score: {value:.1f})")
        
        # Insights sobre brand fit
        if any(word in brand_context.lower() for word in ['luxury', 'premium', 'alto padrão']):
            if any('high_income' in mult or 'premium' in mult for mult in multipliers.keys()):
                insights.append("💎 Excelente fit para posicionamento premium na região")
            else:
                insights.append("⚠️ Posicionamento premium pode não ressoar nesta localização")
        
        return insights
    
    def _generate_geo_recommendations(self, insights: List[str], brand_fit_score: float) -> List[str]:
        """Gera recomendações baseadas na análise"""
        recommendations = []
        
        if brand_fit_score >= 80:
            recommendations.append("🚀 Localização ideal para a marca - investir pesado")
        elif brand_fit_score >= 60:
            recommendations.append("✅ Boa localização - ajustar messaging para contexto local")
        elif brand_fit_score >= 40:
            recommendations.append("⚠️ Localização desafiadora - requer adaptação significativa")
        else:
            recommendations.append("❌ Baixo fit - considerar outras regiões prioritariamente")
        
        # Recomendações específicas baseadas nos insights
        insight_text = ' '.join(insights).lower()
        
        if 'premium' in insight_text and 'alta afinidade' in insight_text:
            recommendations.append("💰 Investir em experiências premium e exclusivas")
        
        if 'community' in insight_text or 'família' in insight_text:
            recommendations.append("👨‍👩‍👧‍👦 Focar em valores familiares e comunitários na comunicação")
        
        if 'cultural' in insight_text or 'autêntico' in insight_text:
            recommendations.append("🎭 Enfatizar autenticidade e conexão cultural local")
        
        return recommendations

# Função para integração
def enhance_geo_cultural_analysis(location: str, brand_context: str, demographic: str = None) -> Dict[str, Any]:
    """Função principal para integração com dashboard existente"""
    engine = GeoCulturalEngine()
    return engine.analyze_geo_cultural_fit(location, brand_context, demographic)

if __name__ == "__main__":
    # Teste
    engine = GeoCulturalEngine()
    
    # Teste Havaianas na Zona Sul do Rio
    result = enhance_geo_cultural_analysis(
        "Rio de Janeiro - Zona Sul",
        "chinelos praia lifestyle jovem",
        "18-24"
    )
    
    print(f"✅ Brand fit score: {result['brand_fit_score']:.1f}")
    print("📋 Insights:")
    for insight in result['insights']:
        print(f"  {insight}")
    print("💡 Recomendações:")
    for rec in result['recommendations']:
        print(f"  {rec}")