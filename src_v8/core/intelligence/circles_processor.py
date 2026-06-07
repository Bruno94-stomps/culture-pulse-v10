#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cultural Circles Processor V9.0 - Versão Consolidada e Otimizada
Sistema unificado dos 16 Círculos Culturais Brasileiros

🎯 MELHORIAS V9.0:
- Compatibilidade total com AdvancedCulturalMetrics
- Otimizações de performance
- Melhor integração com análise de tendências
- Sistema de cache aprimorado
- Multiplicadores dinâmicos refinados
"""

from typing import Dict, List, Any, Tuple, Optional
import numpy as np
import re
from collections import defaultdict, Counter
import logging
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# ===== S4.3 — UNKNOWN CIRCLE THRESHOLD =====
# Sinais com max circle score < este threshold são classificados como
# "emergente_desconhecido" em vez de silenciosamente cair em "geral".
UNKNOWN_CIRCLE_THRESHOLD = 0.15  # score otimizado (após multiplicadores)

# ===== CONFIGURAÇÕES DE PRODUÇÃO =====
INDUSTRY_SEGMENTS = [
    "Alimentação e Bebidas", "Moda e Beleza", "Tecnologia", "Entretenimento",
    "Educação", "Saúde", "Turismo", "Varejo", "Serviços Financeiros",
    "Automotivo", "Imobiliário", "Telecomunicações", "Energia",
    "Agronegócio", "Construção Civil", "Esportes", "Cultura e Arte",
    "ONGs e Terceiro Setor", "Governo e Setor Público", "Outros"
]

BUSINESS_CONTEXTS = {
    "Lançamento de Produto": {
        "description": "Análise cultural para lançamento de novos produtos",
        "cultural_priority": ["adaptacao_flexibilidade", "criatividade_improvisacao", "musicalidade_expressao"]
    },
    "Crise de Reputação": {
        "description": "Monitoramento cultural durante crises de imagem",
        "cultural_priority": ["resiliencia_fe", "afeto_hospitalidade", "desigualdade_solidariedade"]
    },
    "Pesquisa de Mercado": {
        "description": "Entendimento cultural do mercado e consumidores",
        "cultural_priority": ["diversidade_geografica_cultural", "vida_urbana_rural", "desejo_ascensao_oportunidades"]
    },
    "Engajamento de Marca": {
        "description": "Estratégias de engajamento cultural",
        "cultural_priority": ["alegria_celebracao", "festa_luta_cotidianas", "musicalidade_expressao"]
    },
    "Expansão Regional": {
        "description": "Análise cultural para novos mercados",
        "cultural_priority": ["sincretismo_cultural", "diversidade_geografica_cultural", "adaptacao_flexibilidade"]
    },
    "Inovação e Desenvolvimento": {
        "description": "Desenvolvimento de produtos culturalmente relevantes",
        "cultural_priority": ["criatividade_improvisacao", "economia_informal_empreendedorismo", "astucia_sagacidade"]
    }
}

PRODUCTION_LOCATIONS = [
    "Brasil", "São Paulo - Capital", "Rio de Janeiro - Capital",
    "Belo Horizonte", "Salvador", "Brasília", "Recife", "Porto Alegre"
]

DEMOGRAPHIC_SEGMENTS = {
    '13-17': {'name': "13-17 anos (Gen Z)", 'default': True},
    '18-24': {'name': "18-24 anos (Gen Z/Millennial)", 'default': True},
    '25-34': {'name': "25-34 anos (Millennial)", 'default': True},
    '35-44': {'name': "35-44 anos (Millennial/Gen X)", 'default': False},
    '45+': {'name': "45+ anos (Gen X/Boomer)", 'default': False}
}

# ===== ENUMS E CLASSES =====
class CircleLevel(Enum):
    CENTRAL = "centrais"
    INTERMEDIARY = "intermediarios"
    EXTERNAL = "externos"

class IndustrySegment(Enum):
    ALIMENTACAO_BEBIDAS = "Alimentação e Bebidas"
    MODA_BELEZA = "Moda e Beleza"
    TECNOLOGIA = "Tecnologia"
    ENTRETENIMENTO = "Entretenimento"
    EDUCACAO = "Educação"
    SAUDE = "Saúde"
    TURISMO = "Turismo"
    VAREJO = "Varejo"
    SERVICOS_FINANCEIROS = "Serviços Financeiros"
    AUTOMOTIVO = "Automotivo"
    IMOBILIARIO = "Imobiliário"
    TELECOMUNICACOES = "Telecomunicações"
    ENERGIA = "Energia"
    AGRONEGOCIO = "Agronegócio"
    CONSTRUCAO_CIVIL = "Construção Civil"
    ESPORTES = "Esportes"
    CULTURA_ARTE = "Cultura e Arte"
    ONGS_TERCEIRO_SETOR = "ONGs e Terceiro Setor"
    GOVERNO_SETOR_PUBLICO = "Governo e Setor Público"
    OUTROS = "Outros"

@dataclass
class CulturalCircleAdvanced:
    """Representação avançada de um círculo cultural com multiplicadores"""
    id: str
    name: str
    level: CircleLevel
    base_weight: float
    keywords: List[str]
    description: str
    industry_multipliers: Dict[IndustrySegment, float] = field(default_factory=dict)
    context_multipliers: Dict[str, float] = field(default_factory=dict)
    regional_multipliers: Dict[str, float] = field(default_factory=dict)
    demographic_multipliers: Dict[str, float] = field(default_factory=dict)

# ===== CLASSE PRINCIPAL ÚNICA =====
class CulturalCirclesProcessor:
    """
    Processador unificado dos 16 Círculos Culturais da Alma Brasileira
    Versão consolidada e corrigida V8.1
    """
    
    def __init__(self):
        """Inicializa o processador com os 16 círculos culturais"""
        self.cultural_circles = self._initialize_cultural_circles()
        self.industry_weights = self._initialize_industry_weights()
        self.context_weights = self._initialize_context_weights()
        self.production_config = {
            'industry_segments': INDUSTRY_SEGMENTS,
            'business_contexts': BUSINESS_CONTEXTS,
            'locations': PRODUCTION_LOCATIONS,
            'demographics': DEMOGRAPHIC_SEGMENTS
        }
        logger.info("[CIRCLES] Cultural Circles Processor V9.0 inicializado - 16 círculos ativos")
    
    def _initialize_cultural_circles(self) -> Dict[str, Dict[str, Any]]:
        """Inicializa os círculos culturais em estrutura compatível com dashboard"""
        
        return {
            "centrais": {
                "adaptacao_flexibilidade": {
                    "name": "Adaptação & Flexibilidade",
                    "description": "Capacidade de se adaptar e ser flexível diante das mudanças - Jeitinho brasileiro",
                    "weight": 1.3,
                    "keywords": ['adaptação', 'flexível', 'mudança', 'ajuste', 'molda', 'versátil', 'jeitinho'],
                    "level": CircleLevel.CENTRAL,
                    "context_multipliers": {
                        "Lançamento de Produto": 1.4,
                        "Crise de Reputação": 1.3,
                        "Inovação e Desenvolvimento": 1.3,
                        "Expansão Regional": 1.2
                    },
                    "regional_multipliers": {
                        'São Paulo - Capital': 1.2,
                        'Rio de Janeiro - Capital': 1.2,
                        'Recife': 1.3,
                        'Salvador': 1.3,
                        'Brasil': 1.0
                    },
                    "demographic_multipliers": {
                        '18-24': 1.2,
                        '25-34': 1.3,
                        '35-44': 1.1,
                        '45+': 1.0
                    }
                },
                "conexao_natureza_coletivo": {
                    "name": "Conexão com Natureza & Coletivo",
                    "description": "Conexão profunda com a natureza e senso de coletividade",
                    "weight": 1.2,
                    "keywords": ['natureza', 'coletivo', 'comunidade', 'meio ambiente', 'sustentável', 'conjunto'],
                    "level": CircleLevel.CENTRAL,
                    "context_multipliers": {
                        "Expansão Regional": 1.3,
                        "Pesquisa de Mercado": 1.2,
                        "Engajamento de Marca": 1.2
                    },
                    "regional_multipliers": {
                        'Porto Alegre': 1.3,
                        'Brasília': 1.4,
                        'Brasil': 1.2
                    },
                    "demographic_multipliers": {
                        '25-34': 1.2,
                        '35-44': 1.3,
                        '45+': 1.4,
                        '18-24': 1.0
                    }
                },
                "resiliencia_fe": {
                    "name": "Resistência & Fé",
                    "description": "Capacidade de resistir e superar adversidades com fé",
                    "weight": 1.4,
                    "keywords": ['força', 'resistência', 'fé', 'esperança', 'superação', 'persistência', 'aguenta'],
                    "level": CircleLevel.CENTRAL,
                    "context_multipliers": {
                        "Crise de Reputação": 1.5,
                        "Engajamento de Marca": 1.3,
                        "Pesquisa de Mercado": 1.2
                    },
                    "regional_multipliers": {
                        'Salvador': 1.5,
                        'Recife': 1.5,
                        'Rio de Janeiro - Capital': 1.4,
                        'Brasil': 1.0
                    },
                    "demographic_multipliers": {
                        '35-44': 1.3,
                        '45+': 1.4,
                        '25-34': 1.2,
                        '18-24': 1.0
                    }
                },
                "economia_informal_empreendedorismo": {
                    "name": "Economia Informal & Empreendedorismo",
                    "description": "Habilidade para economia informal e empreendedorismo",
                    "weight": 1.1,
                    "keywords": ['informal', 'empreender', 'negócio', 'virar', 'ganhar', 'trabalhar', 'sobreviver'],
                    "level": CircleLevel.CENTRAL,
                    "context_multipliers": {
                        "Inovação e Desenvolvimento": 1.4,
                        "Lançamento de Produto": 1.3,
                        "Pesquisa de Mercado": 1.2
                    },
                    "regional_multipliers": {
                        'Rio de Janeiro - Capital': 1.5,
                        'São Paulo - Capital': 1.3,
                        'Salvador': 1.4,
                        'Brasil': 1.0
                    },
                    "demographic_multipliers": {
                        '18-24': 1.4,
                        '25-34': 1.5,
                        '35-44': 1.2,
                        '45+': 1.0
                    }
                }
            },
            "intermediarios": {
                "musicalidade_expressao": {
                    "name": "Musicalidade & Expressão",
                    "description": "Expressão através da música e arte",
                    "weight": 1.0,
                    "keywords": ['música', 'cantar', 'dança', 'ritmo', 'som', 'expressão', 'arte'],
                    "level": CircleLevel.INTERMEDIARY,
                    "context_multipliers": {
                        "Engajamento de Marca": 1.5,
                        "Lançamento de Produto": 1.3,
                        "Expansão Regional": 1.2
                    },
                    "regional_multipliers": {
                        'Salvador': 1.4,
                        'Rio de Janeiro - Capital': 1.3,
                        'Recife': 1.5,
                        'Brasil': 1.0
                    },
                    "demographic_multipliers": {
                        '13-17': 1.4,
                        '18-24': 1.5,
                        '25-34': 1.3,
                        '35-44': 1.0
                    }
                },
                "vida_urbana_rural": {
                    "name": "Vida Urbana & Rural",
                    "description": "Equilíbrio entre experiências urbanas e rurais",
                    "weight": 0.9,
                    "keywords": ['cidade', 'campo', 'urbano', 'rural', 'interior', 'metrópole', 'roça'],
                    "level": CircleLevel.INTERMEDIARY,
                    "context_multipliers": {
                        "Pesquisa de Mercado": 1.3,
                        "Expansão Regional": 1.2
                    },
                    "regional_multipliers": {
                        'Porto Alegre': 1.3,
                        'Belo Horizonte': 1.3,
                        'Brasília': 1.3,
                        'Brasil': 1.0
                    },
                    "demographic_multipliers": {
                        '35-44': 1.2,
                        '45+': 1.3,
                        '25-34': 1.1,
                        '18-24': 1.0
                    }
                },
                "alegria_celebracao": {
                    "name": "Alegria & Celebração",
                    "description": "Tendência natural à alegria e celebração",
                    "weight": 1.0,
                    "keywords": ['alegria', 'festa', 'celebrar', 'comemorar', 'feliz', 'diversão'],
                    "level": CircleLevel.INTERMEDIARY,
                    "context_multipliers": {
                        "Engajamento de Marca": 1.4,
                        "Lançamento de Produto": 1.3,
                        "Expansão Regional": 1.2
                    },
                    "regional_multipliers": {
                        'Salvador': 1.4,
                        'Rio de Janeiro - Capital': 1.3,
                        'Brasil': 1.0
                    },
                    "demographic_multipliers": {
                        '13-17': 1.4,
                        '18-24': 1.5,
                        '25-34': 1.2,
                        '35-44': 1.0
                    }
                },
                "criatividade_improvisacao": {
                    "name": "Criatividade & Improvisação",
                    "description": "Capacidade criativa e de improvisação",
                    "weight": 1.0,
                    "keywords": ['criativo', 'improvisar', 'inventar', 'criar', 'inovar', 'solução', 'jeito'],
                    "level": CircleLevel.INTERMEDIARY,
                    "context_multipliers": {
                        "Inovação e Desenvolvimento": 1.5,
                        "Lançamento de Produto": 1.4,
                        "Engajamento de Marca": 1.3
                    },
                    "regional_multipliers": {
                        'São Paulo - Capital': 1.3,
                        'Rio de Janeiro - Capital': 1.4,
                        'Brasil': 1.0
                    },
                    "demographic_multipliers": {
                        '18-24': 1.4,
                        '25-34': 1.3,
                        '13-17': 1.2,
                        '35-44': 1.0
                    }
                },
                "afeto_hospitalidade": {
                    "name": "Afeto & Hospitalidade",
                    "description": "Calorosa recepção e afeto nas relações interpessoais",
                    "weight": 1.0,
                    "keywords": ['afeto', 'carinho', 'hospitalidade', 'acolher', 'caloroso', 'abraço', 'receber'],
                    "level": CircleLevel.INTERMEDIARY,
                    "context_multipliers": {
                        "Engajamento de Marca": 1.4,
                        "Crise de Reputação": 1.3,
                        "Pesquisa de Mercado": 1.2
                    },
                    "regional_multipliers": {
                        'Salvador': 1.4,
                        'Recife': 1.4,
                        'Rio de Janeiro - Capital': 1.3,
                        'Brasil': 1.0
                    },
                    "demographic_multipliers": {
                        '35-44': 1.3,
                        '45+': 1.4,
                        '25-34': 1.2,
                        '18-24': 1.0
                    }
                },
                "desigualdade_solidariedade": {
                    "name": "Desigualdade & Solidariedade",
                    "description": "Consciência social e solidariedade em face da desigualdade",
                    "weight": 0.9,
                    "keywords": ['desigualdade', 'solidariedade', 'justiça', 'comunidade', 'ajudar', 'suporte'],
                    "level": CircleLevel.INTERMEDIARY,
                    "context_multipliers": {
                        "Pesquisa de Mercado": 1.3,
                        "Crise de Reputação": 1.2
                    },
                    "regional_multipliers": {
                        'São Paulo - Capital': 1.3,
                        'Rio de Janeiro - Capital': 1.2,
                        'Brasil': 1.0
                    },
                    "demographic_multipliers": {
                        '25-34': 1.2,
                        '35-44': 1.3,
                        '45+': 1.4,
                        '18-24': 1.0
                    }
                },
                "diversidade_geografica_cultural": {
                    "name": "Diversidade Geográfica & Cultural",
                    "description": "Diversidade cultural e geográfica do Brasil",
                    "weight": 0.9,
                    "keywords": ['diversidade', 'cultural', 'geográfico', 'variedade', 'pluralidade', 'riqueza'],
                    "level": CircleLevel.INTERMEDIARY,
                    "context_multipliers": {
                        "Expansão Regional": 1.4,
                        "Pesquisa de Mercado": 1.3,
                        "Engajamento de Marca": 1.2
                    },
                    "regional_multipliers": {
                        'Porto Alegre': 1.3,
                        'Belo Horizonte': 1.3,
                        'Brasília': 1.3,
                        'Brasil': 1.0
                    },
                    "demographic_multipliers": {
                        '25-34': 1.2,
                        '35-44': 1.3,
                        '45+': 1.4,
                        '18-24': 1.0
                    }
                },
                "desejo_ascensao_oportunidades": {
                    "name": "Desejo, Ascensão & Oportunidades",
                    "description": "Busca por ascensão social e oportunidades",
                    "weight": 1.0,
                    "keywords": ['desejo', 'ascensão', 'oportunidade', 'sucesso', 'crescimento', 'progresso'],
                    "level": CircleLevel.INTERMEDIARY,
                    "context_multipliers": {
                        "Pesquisa de Mercado": 1.4,
                        "Engajamento de Marca": 1.2,
                        "Expansão Regional": 1.1
                    },
                    "regional_multipliers": {
                        'São Paulo - Capital': 1.3,
                        'Rio de Janeiro - Capital': 1.2,
                        'Brasil': 1.0
                    },
                    "demographic_multipliers": {
                        '18-24': 1.2,
                        '25-34': 1.3,
                        '35-44': 1.1,
                        '45+': 1.0
                    }
                }
            },
            "externos": {
                "sincretismo_cultural": {
                    "name": "Sincretismo Cultural",
                    "description": "Capacidade de sincretismo e fusão cultural",
                    "weight": 0.8,
                    "keywords": ['mistura', 'fusão', 'sincretismo', 'multicultural', 'híbrido', 'combinação'],
                    "level": CircleLevel.EXTERNAL,
                    "context_multipliers": {
                        "Expansão Regional": 1.4,
                        "Pesquisa de Mercado": 1.2,
                        "Engajamento de Marca": 1.1
                    },
                    "regional_multipliers": {
                        'Salvador': 1.4,
                        'Rio de Janeiro - Capital': 1.2,
                        'São Paulo - Capital': 1.3,
                        'Brasil': 1.0
                    },
                    "demographic_multipliers": {
                        '25-34': 1.2,
                        '18-24': 1.1,
                        '35-44': 1.0
                    }
                },
                "festa_luta_cotidianas": {
                    "name": "Festa, Luta & Cotidiano",
                    "description": "Celebração da vida cotidiana e resistência",
                    "weight": 0.8,
                    "keywords": ['festa', 'luta', 'cotidiano', 'resistência', 'cultura', 'comunidade'],
                    "level": CircleLevel.EXTERNAL,
                    "context_multipliers": {
                        "Inovação e Desenvolvimento": 1.3,
                        "Lançamento de Produto": 1.2,
                        "Crise de Reputação": 1.1
                    },
                    "regional_multipliers": {
                        'Rio de Janeiro - Capital': 1.4,
                        'São Paulo - Capital': 1.2,
                        'Brasil': 1.0
                    },
                    "demographic_multipliers": {
                        '25-34': 1.2,
                        '35-44': 1.3,
                        '45+': 1.4,
                        '18-24': 1.0
                    }
                },
                "tradição_cultural": {
                    "name": "Tradição Cultural",
                    "description": "Valorização das tradições culturais brasileiras",
                    "weight": 0.8,
                    "keywords": ['tradição', 'cultura', 'história', 'legado', 'ancestralidade', 'raiz'],
                    "level": CircleLevel.EXTERNAL,
                    "context_multipliers": {
                        "Pesquisa de Mercado": 1.3,
                        "Engajamento de Marca": 1.2,
                        "Expansão Regional": 1.1
                    },
                    "regional_multipliers": {
                        'Porto Alegre': 1.3,
                        'Belo Horizonte': 1.2,
                        'Brasil': 1.0
                    },
                    "demographic_multipliers": {
                        '35-44': 1.2,
                        '45+': 1.3,
                        '25-34': 1.1,
                        '18-24': 1.0
                    }
                },
                "astucia_sagacidade": {
                    "name": "Astúcia & Sagacidade",
                    "description": "Astúcia e sagacidade para resolver problemas",
                    "weight": 0.8,
                    "keywords": ['astuto', 'sagaz', 'esperto', 'malandro', 'inteligente', 'hábil', 'jeitinho'],
                    "level": CircleLevel.EXTERNAL,
                    "context_multipliers": {
                        "Inovação e Desenvolvimento": 1.3,
                        "Lançamento de Produto": 1.2,
                        "Crise de Reputação": 1.1
                    },
                    "regional_multipliers": {
                        'Rio de Janeiro - Capital': 1.4,
                        'São Paulo - Capital': 1.2,
                        'Brasil': 1.0
                    },
                    "demographic_multipliers": {
                        '25-34': 1.3,
                        '18-24': 1.2,
                        '35-44': 1.1,
                        '45+': 1.0
                    }
                }
            }
        }
    
    def _initialize_industry_weights(self) -> Dict[str, Dict[str, float]]:
        """Define pesos por indústria"""
        return {
            "Tecnologia": {
                'innovation_creativity': 0.40,
                'problem_solving': 0.30,
                'connectivity': 0.20,
                'adaptation': 0.10
            },
            "Entretenimento": {
                'expression_creativity': 0.40,
                'cultural_authenticity': 0.30,
                'community_belonging': 0.20,
                'innovation': 0.10
            },
            "Alimentação e Bebidas": {
                'cultural_tradition': 0.35,
                'regional_identity': 0.30,
                'social_connection': 0.25,
                'innovation': 0.10
            }
        }
    
    def _initialize_context_weights(self) -> Dict[str, Dict[str, float]]:
        """Define pesos por contexto de negócio"""
        return {
            "Lançamento de Produto": {
                'innovation_impact': 0.35,
                'market_adaptation': 0.25,
                'cultural_resonance': 0.25,
                'consumer_connection': 0.15
            },
            "Crise de Reputação": {
                'trust_rebuilding': 0.40,
                'community_support': 0.30,
                'authenticity': 0.20,
                'resilience': 0.10
            },
            "Pesquisa de Mercado": {
                'market_understanding': 0.35,
                'cultural_insights': 0.30,
                'consumer_behavior': 0.25,
                'regional_variations': 0.10
            }
        }
    
    def analyze_cultural_circles(
        self,
        raw_data: Dict[str, Any],
        industry_segment: str = "Outros",
        business_context: str = "Pesquisa de Mercado",
        location: str = "Brasil",
        demographic: str = "25-34"
    ) -> Dict[str, Any]:
        """
        Análise completa pelos círculos culturais com suporte a Pesos de Entropia (V9.4)
        
        Args:
            raw_data: Dados brutos de todas as plataformas
            industry_segment: Segmento da indústria
            business_context: Contexto de negócio
            location: Localização geográfica
            demographic: Faixa demográfica
            
        Returns:
            Dict com análise completa dos círculos
        """
        logger.info(f"🔍 Alma Brasileira V9.4: Analisando círculos para {industry_segment}")
        
        try:
            # 1. Extrair sinais individuais para aplicar pesos de descoberta
            # Em V9.4, não apenas combinamos o texto, mas pesamos cada sinal.
            weighted_text_segments = []
            from core.intelligence.business_synthesizer import BusinessSynthesizer
            synthesizer = BusinessSynthesizer()

            for platform, platform_data in raw_data.items():
                # Se os dados já vieram processados com is_outlier, aplicamos o peso
                if isinstance(platform_data, dict) and "termo" in platform_data:
                    text = f"{platform_data.get('termo', '')} {platform_data.get('descricao', '')}"
                    # Cálculo de profundidade para obter o discovery_factor
                    # Nota: Círculo 'geral' como fallback inicial
                    depth = synthesizer.calculate_signal_depth(text, "festa_celebracao")
                    weight = depth.get("discovery_factor", 1.0)
                    
                    # Multiplicamos o texto (simulação de peso para o motor de busca de keywords)
                    # Sinais com peso 1.5 (Outliers) aparecem 'mais' para o contador de keywords.
                    repeat_count = max(1, int(weight * 2)) 
                    weighted_text_segments.extend([text] * repeat_count)
                else:
                    # Fallback para dados brutos não estruturados
                    weighted_text_segments.append(str(platform_data))

            combined_text = " ".join(weighted_text_segments)
            
            # 2. Calcular scores brutos (O motor interno de keywords agora 'enxerga' mais os outliers)
            raw_scores = self._calculate_raw_circles_scores(combined_text)
            
            # 3. Aplicar multiplicadores
            optimized_scores = self._optimize_all_circles(
                raw_scores, business_context, location, demographic
            )
            
            # 4. Calcular score geral
            overall_score = self._calculate_overall_cultural_score(optimized_scores)
            
            # 5. Identificar dominantes
            dominant_circles = self._identify_dominant_circles(optimized_scores)
            
            # 6. Gerar insights
            insights = self._generate_insights(optimized_scores, business_context)
            
            return {
                'overall_score': overall_score,
                'circles_scores': optimized_scores,
                'dominant_circles': dominant_circles,
                'cultural_level': self._classify_cultural_level(overall_score),
                'industry_segment': industry_segment,
                'business_context': business_context,
                'regional_context': location,
                'demographic_context': demographic,
                'insights': insights,
                'processing_metadata': {
                    'total_text_analyzed': len(combined_text),
                    'circles_processed': len(self.cultural_circles),
                    'version': '8.1',
                    'production_aligned': True
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na análise: {e}")
            return self._empty_analysis_result()
    
    def _extract_combined_text(self, raw_data: Dict[str, Any]) -> str:
        """Extrai texto de todas as plataformas incluindo payloads de análise direta"""
        combined_texts = []
        
        # Suporte a texto direto para análise de campanha (S4.3 Fix)
        if "campaign_analysis" in raw_data:
            combined_texts.append(raw_data["campaign_analysis"].get("text", ""))

        for platform, data in raw_data.items():
            if platform == "campaign_analysis":
                continue
            if isinstance(data, dict):
                    combined_texts.extend([post.get('caption', '') for post in data.get('posts', [])])
        
        return ' '.join(combined_texts).lower()
    
    def _calculate_raw_circles_scores(self, text: str) -> Dict[str, float]:
        """Calcula scores brutos por círculo com bônus para textos curtos de campanha"""
        raw_scores = {}
        text_len = len(text.split())
        is_short_text = text_len < 50

        for level, circles in self.cultural_circles.items():
            for circle_id, circle_data in circles.items():
                keyword_matches = 0
                total_keywords = len(circle_data['keywords'])
                
                for keyword in circle_data['keywords']:
                    # Regex case-insensitive que pega a palavra e variações
                    pattern = rf'\b{re.escape(keyword.lower())}\w*\b'
                    matches = len(re.findall(pattern, text.lower()))
                    keyword_matches += min(matches, 3)
                
                # Se for texto curto, aumentamos a sensibilidade (S4.3 Fix)
                denominator = (total_keywords * (1 if is_short_text else 3))
                raw_score = keyword_matches / denominator if denominator > 0 else 0.0
                raw_scores[circle_id] = min(raw_score, 1.0)
        
        return raw_scores
    
    def _optimize_all_circles(
        self,
        raw_scores: Dict[str, float],
        business_context: str,
        location: str,
        demographic: str
    ) -> Dict[str, Dict]:
        """Aplica multiplicadores aos scores"""
        optimized = {}
        
        for level, circles in self.cultural_circles.items():
            for circle_id, circle_data in circles.items():
                if circle_id in raw_scores:
                    raw_score = raw_scores[circle_id]
                    
                    # Aplicar multiplicadores
                    context_boost = circle_data.get('context_multipliers', {}).get(business_context, 1.0)
                    regional_boost = circle_data.get('regional_multipliers', {}).get(location, 1.0)
                    demographic_boost = circle_data.get('demographic_multipliers', {}).get(demographic, 1.0)
                    
                    # Score otimizado
                    optimized_score = min(
                        raw_score * circle_data['weight'] * context_boost * regional_boost * demographic_boost,
                        1.0
                    )
                    
                    optimized[circle_id] = {
                        'score': optimized_score,
                        'raw_score': raw_score,
                        'level': level,
                        'name': circle_data['name'],
                        'weight_applied': circle_data['weight'],
                        'context_boost': context_boost,
                        'regional_boost': regional_boost,
                        'demographic_boost': demographic_boost,
                        'description': circle_data['description'],
                        'keywords': circle_data['keywords']
                    }
        
        return optimized
    
    def _calculate_overall_cultural_score(self, circles_scores: Dict[str, Dict[str, Any]]) -> float:
        """Calcula score cultural geral"""
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for circle_data in circles_scores.values():
            total_weighted_score += circle_data['score'] * circle_data['weight_applied']
            total_weight += circle_data['weight_applied']
        
        return total_weighted_score / total_weight if total_weight > 0 else 0.0
    
    def _identify_dominant_circles(
        self,
        circles_scores: Dict[str, Dict[str, Any]]
    ) -> List[Tuple[str, float, str]]:
        """Identifica círculos dominantes"""
        sorted_circles = sorted(
            circles_scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        return [
            (data['name'], data['score'], data['level']) 
            for name, data in sorted_circles[:5]
        ]
    
    def _generate_insights(
        self, 
        circles_scores: Dict[str, Dict[str, Any]],
        business_context: str
    ) -> Dict[str, Any]:
        """Gera insights baseados nos scores"""
        
        insights = {}
        
        # Top e bottom círculos
        top_circles = sorted(circles_scores.items(), key=lambda x: x[1]['score'], reverse=True)[:3]
        bottom_circles = sorted(circles_scores.items(), key=lambda x: x[1]['score'])[:3]
        
        insights['general'] = {
            'strongest_aspects': [
                f"{data['name']} ({data['score']:.2f})" 
                for _, data in top_circles
            ],
            'improvement_opportunities': [
                f"{data['name']} ({data['score']:.2f})" 
                for _, data in bottom_circles
            ],
            'strategic_recommendations': self._generate_recommendations(circles_scores, business_context)
        }
        
        return insights
    
    def _generate_recommendations(
        self, 
        circles_scores: Dict[str, Dict[str, Any]],
        business_context: str
    ) -> List[str]:
        """Gera recomendações estratégicas"""
        recommendations = []
        
        # Análise por níveis
        level_scores = {}
        for level in ['centrais', 'intermediarios', 'externos']:
            scores = [data['score'] for data in circles_scores.values() if data['level'] == level]
            level_scores[level] = np.mean(scores) if scores else 0.0
        
        if level_scores['centrais'] < 0.5:
            recommendations.append("🎯 Priorizar fortalecimento dos círculos centrais da brasilidade")
        
        if level_scores['intermediarios'] > 0.7:
            recommendations.append("🚀 Aproveitar força nos círculos intermediários para expansão")
        
        # Recomendações por contexto
        if business_context == "Lançamento de Produto":
            recommendations.append("🎨 Enfatizar criatividade e inovação na comunicação")
        elif business_context == "Crise de Reputação":
            recommendations.append("💪 Demonstrar resiliência e autenticidade da marca")
        elif business_context == "Pesquisa de Mercado":
            recommendations.append("🗺️ Mapear diversidade cultural e regional")
        
        return recommendations
    
    def _classify_cultural_level(self, overall_score: float) -> str:
        """Classifica nível cultural"""
        if overall_score >= 0.8:
            return 'muito_alto'
        elif overall_score >= 0.6:
            return 'alto'
        elif overall_score >= 0.4:
            return 'medio'
        elif overall_score >= 0.2:
            return 'baixo'
        else:
            return 'muito_baixo'
    
    def _empty_analysis_result(self) -> Dict[str, Any]:
        """Resultado vazio em caso de erro"""
        return {
            'overall_score': 0.0,
            'circles_scores': {},
            'dominant_circles': [],
            'cultural_level': 'indefinido',
            'business_context': '',
            'regional_context': '',
            'demographic_context': '',
            'insights': {},
            'processing_metadata': {'error': True, 'version': '8.1'}
        }

    # ── S4.3 — Unknown Category Handler ─────────────────────────────────────

    # 16 círculos temáticos do dashboard (NÃO confundir com dimensões Alma Brasileira)
    THEMATIC_CIRCLES = {
        "Música Popular": [
            "música", "musica", "funk", "sertanejo", "pagode", "forró", "mpb",
            "rap", "hip hop", "reggaeton", "bossa nova", "axé", "álbum", "show",
            "cantor", "cantora", "spotify", "playlist", "dj", "mc", "ritmo",
        ],
        "Gastronomia": [
            "gastronomia", "comida", "receita", "restaurante", "chef",
            "culinária", "culinaria", "feijoada", "açaí", "acai", "churrasco",
            "cozinha", "alimento", "sabor", "ingrediente", "prato",
        ],
        "Moda & Estilo": [
            "moda", "estilo", "roupa", "fashion", "tendência", "look",
            "streetwear", "marca", "grife", "desfile", "coleção",
        ],
        "Tecnologia": [
            "tecnologia", "tech", "inteligência artificial", "ia", "ai",
            "startup", "app", "aplicativo", "digital", "software", "pix",
            "fintech", "inovação", "computador", "programação",
        ],
        "Esporte": [
            "futebol", "esporte", "gol", "campeonato", "time", "jogador",
            "copa", "flamengo", "corinthians", "palmeiras", "vôlei", "basquete",
            "surf", "skate", "mma", "ufc", "olímpico", "atleta",
        ],
        "Comportamento": [
            "comportamento", "hábito", "habito", "saúde mental", "mindfulness",
            "bem-estar", "lifestyle", "rotina", "produtividade", "autocuidado",
        ],
        "Política": [
            "política", "politica", "governo", "eleição", "eleicao", "partido",
            "congresso", "senado", "deputado", "voto", "democracia",
        ],
        "Sustentabilidade": [
            "sustentabilidade", "sustentável", "reciclagem", "eco", "carbono",
            "verde", "renovável", "ambiental", "meio ambiente", "poluição",
        ],
        "Arte & Cinema": [
            "arte", "cinema", "filme", "série", "serie", "novela", "teatro",
            "pintura", "exposição", "museu", "netflix", "streaming", "ator",
        ],
        "Educação": [
            "educação", "educacao", "escola", "universidade", "ensino",
            "professor", "aluno", "aprendizado", "vestibular", "enem",
        ],
        "Espiritualidade": [
            "espiritualidade", "religião", "religiao", "igreja", "oração",
            "meditação", "yoga", "fé", "candomblé", "umbanda", "evangélico",
        ],
        "Turismo": [
            "turismo", "viagem", "hotel", "praia", "destino", "passagem",
            "férias", "resort", "mochilão", "trilha", "ecoturismo",
        ],
        "Juventude": [
            "juventude", "jovem", "geração z", "gen z", "tiktoker", "influencer",
            "viral", "meme", "trend", "desafio", "challenge",
        ],
        "Família & Lar": [
            "família", "familia", "lar", "casa", "filho", "mãe", "pai",
            "bebê", "maternidade", "paternidade", "decoração", "reforma",
        ],
        "Economia": [
            "economia", "inflação", "inflacao", "dólar", "bolsa", "investimento",
            "mercado", "pib", "juros", "selic", "emprego", "desemprego",
        ],
        "Saúde & Bem-estar": [
            "saúde", "saude", "hospital", "médico", "medico", "vacina",
            "fitness", "academia", "exercício", "dieta", "nutrição", "sus",
        ],
    }

    def classify_signal_circle(
        self,
        text: str,
        plataforma: str = "reddit",
        threshold: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Classifica um sinal em um dos 16 círculos temáticos OU em 'emergente_desconhecido'.

        S4.3: usa keyword matching contra os 16 círculos temáticos do dashboard.
        Quando nenhum círculo atinge o threshold, marca como emergente_desconhecido.
        Diferente de analyze_cultural_circles que analisa dimensões Alma Brasileira.

        Args:
            text: Texto combinado do sinal (título + conteúdo)
            plataforma: Nome da plataforma de origem
            threshold: Score mínimo para aceitar (default: UNKNOWN_CIRCLE_THRESHOLD)

        Returns:
            Dict com:
              circulo: str — nome do círculo ou "emergente_desconhecido"
              circle_score: float — score do círculo vencedor (0-1)
              is_unknown: bool — True se nenhum círculo atingiu o threshold
              top_scores: List[Tuple[str, float]] — top 3 scores
              rejection_reason: Optional[str] — motivo da rejeição
              circles_detail: Dict — todos os scores
        """
        if threshold is None:
            threshold = UNKNOWN_CIRCLE_THRESHOLD

        if not text or not text.strip():
            return {
                "circulo": "emergente_desconhecido",
                "circle_score": 0.0,
                "is_unknown": True,
                "top_scores": [],
                "rejection_reason": "texto_vazio",
                "circles_detail": {},
            }

        text_lower = text.lower()
        words = set(text_lower.split())

        # Calcular score para cada círculo via keyword matching
        # Normalização: 3+ matches = score 1.0 (um texto real raramente tem >5 keywords)
        MATCH_SATURATION = 3  # número de matches para score máximo
        circle_scores: Dict[str, float] = {}
        for circle_name, keywords in self.THEMATIC_CIRCLES.items():
            matches = 0
            for kw in keywords:
                # Multi-word keywords: check substring
                if " " in kw:
                    if kw in text_lower:
                        matches += 1
                else:
                    if kw in words:
                        matches += 1
            # Normalizar: score = min(matches/MATCH_SATURATION, 1.0)
            score = min(matches / MATCH_SATURATION, 1.0) if MATCH_SATURATION > 0 else 0.0
            circle_scores[circle_name] = round(score, 4)

        # Ordenar por score (top 3 para diagnóstico)
        sorted_circles = sorted(
            circle_scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        top_scores = [(name, score) for name, score in sorted_circles[:3]]
        max_score = top_scores[0][1] if top_scores else 0.0
        best_circle = top_scores[0][0] if top_scores else "geral"

        if max_score < threshold:
            logger.info(
                f"🆕 Sinal classificado como emergente_desconhecido "
                f"(max_score={max_score:.3f} < threshold={threshold}). "
                f"Top3: {top_scores}"
            )
            return {
                "circulo": "emergente_desconhecido",
                "circle_score": max_score,
                "is_unknown": True,
                "top_scores": top_scores,
                "rejection_reason": f"max_score {max_score:.3f} < threshold {threshold}",
                "circles_detail": circle_scores,
            }

        return {
            "circulo": best_circle,
            "circle_score": max_score,
            "is_unknown": False,
            "top_scores": top_scores,
            "rejection_reason": None,
            "circles_detail": circle_scores,
        }
    
    def get_circles_info(self) -> Dict[str, Any]:
        """Retorna informações dos círculos"""
        circles_by_level = {}
        total_circles = 0
        
        for level, circles in self.cultural_circles.items():
            circles_by_level[level] = []
            for circle_id, circle_data in circles.items():
                circles_by_level[level].append({
                    'id': circle_id,
                    'name': circle_data['name'],
                    'weight': circle_data['weight'],
                    'keywords_count': len(circle_data['keywords']),
                    'description': circle_data['description']
                })
                total_circles += 1
        
        return {
            'total_circles': total_circles,
            'version': '8.1',
            'circles_by_level': circles_by_level,
            'business_contexts': list(BUSINESS_CONTEXTS.keys()),
            'industry_segments': INDUSTRY_SEGMENTS,
            'locations': PRODUCTION_LOCATIONS,
            'demographics': list(DEMOGRAPHIC_SEGMENTS.keys()),
            'features': [
                'Multiplicadores por contexto de negócio',
                'Multiplicadores regionais',
                'Multiplicadores demográficos',
                'Sistema de recomendações',
                'Análise de padrões culturais',
                'Insights automáticos'
            ]
        }
    
    def get_production_config(self) -> Dict[str, Any]:
        """Retorna configuração de produção"""
        return {
            'industry_segments': INDUSTRY_SEGMENTS,
            'business_contexts': list(BUSINESS_CONTEXTS.keys()),
            'business_contexts_detailed': BUSINESS_CONTEXTS,
            'locations': PRODUCTION_LOCATIONS,
            'demographics': DEMOGRAPHIC_SEGMENTS,
            'version': '8.1',
            'production_aligned': True
        }
    
    def validate_production_inputs(
        self, 
        industry_segment: str, 
        business_context: str, 
        location: str, 
        demographic: str
    ) -> Dict[str, bool]:
        """Valida inputs de produção"""
        return {
            'industry_segment_valid': industry_segment in INDUSTRY_SEGMENTS,
            'business_context_valid': business_context in BUSINESS_CONTEXTS.keys(),
            'location_valid': location in PRODUCTION_LOCATIONS,
            'demographic_valid': demographic in DEMOGRAPHIC_SEGMENTS.keys(),
            'all_valid': all([
                industry_segment in INDUSTRY_SEGMENTS,
                business_context in BUSINESS_CONTEXTS.keys(),
                location in PRODUCTION_LOCATIONS,
                demographic in DEMOGRAPHIC_SEGMENTS.keys()
            ])
        }

# ===== INSTÂNCIA GLOBAL (CORRIGIDA) =====
cultural_processor = CulturalCirclesProcessor()

# ===== FUNÇÕES DE CONVENIÊNCIA =====
def analyze_brand_culture(
    raw_data: Dict[str, Any],
    segment: str,
    location: str,
    demographic: str = "25-34"
) -> Dict[str, Any]:
    """Função de conveniência para análise cultural"""
    # Mapear segment antigo para industry_segment + business_context
    industry_mapping = {
        'calçados': 'Moda e Beleza',
        'música': 'Entretenimento',
        'gastronomia': 'Alimentação e Bebidas',
        'moda': 'Moda e Beleza',
        'esportes': 'Esportes',
        'tecnologia': 'Tecnologia'
    }
    
    industry_segment = industry_mapping.get(segment.lower(), 'Outros')
    business_context = "Pesquisa de Mercado"  # Contexto padrão
    
    return cultural_processor.analyze_cultural_circles(
        raw_data, industry_segment, business_context, location, demographic
    )

def get_circle_score(
    circle_id: str,
    base_score: float,
    business_context: str = "Pesquisa de Mercado",
    region: str = "Brasil",
    demographic: str = "25-34"
) -> float:
    """Função para calcular score de círculo específico"""
    # Encontrar círculo na estrutura
    for level, circles in cultural_processor.cultural_circles.items():
        if circle_id in circles:
            circle_data = circles[circle_id]
            context_mult = circle_data.get('context_multipliers', {}).get(business_context, 1.0)
            regional_mult = circle_data.get('regional_multipliers', {}).get(region, 1.0)
            demo_mult = circle_data.get('demographic_multipliers', {}).get(demographic, 1.0)
            
            return min(base_score * circle_data['weight'] * context_mult * regional_mult * demo_mult, 1.0)
    
    return base_score

def get_system_info() -> Dict[str, Any]:
    """Função para informações do sistema"""
    return cultural_processor.get_circles_info()

def validate_inputs(industry_segment: str, business_context: str, location: str, demographic: str) -> Dict[str, bool]:
    """Função para validar inputs"""
    return cultural_processor.validate_production_inputs(industry_segment, business_context, location, demographic)

def create_circles_processor() -> CulturalCirclesProcessor:
    """
    Factory function para criar uma instância do CulturalCirclesProcessor
    Compatibilidade com sistema de imports legacy
    """
    return CulturalCirclesProcessor()

# ===== TESTE E INICIALIZAÇÃO =====
if __name__ == "__main__":
    print("🎯 Cultural Circles Processor V8.1 - Versão Limpa Inicializada")
    
    # Mostrar informações do sistema
    info = get_system_info()
    print(f"📊 Total de círculos: {info['total_circles']}")
    print(f"🎭 Contextos disponíveis: {len(info['business_contexts'])}")
    print(f"📍 Localizações: {len(info['locations'])}")
    print(f"👥 Demografia: {len(info['demographics'])}")
    
    # Teste básico
    sample_data = {
        'youtube': {
            'comments': [
                {'text': 'Adorei o jeitinho brasileiro de fazer música'},
                {'text': 'Essa criatividade é resistência pura'}
            ]
        },
        'instagram': {
            'posts': [
                {'caption': 'Celebrando nossa diversidade cultural'},
                {'caption': 'Arte que vem da periferia com muito amor'}
            ]
        }
    }
    
    # Teste da análise
    result = analyze_brand_culture(
        sample_data, 
        "música", 
        "Rio de Janeiro - Capital", 
        "18-24"
    )
    
    print(f"\n📊 Score Cultural Geral: {result['overall_score']:.2f}")
    print(f"🏆 Círculos Dominantes: {[f'{name} ({score:.2f})' for name, score, level in result['dominant_circles'][:3]]}")
    print(f"🎭 Nível Cultural: {result['cultural_level']}")
    
    # Validação
    validation = validate_inputs("Tecnologia", "Inovação e Desenvolvimento", "São Paulo - Capital", "25-34")
    print(f"\n✅ Validação de inputs: {validation['all_valid']}")
    
    print("\n🔥 Sistema pronto para uso!")