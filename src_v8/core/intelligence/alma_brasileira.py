#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alma Brasileira Analyzer - Culture Pulse V8.0
Sistema especializado em análise da identidade cultural brasileira

🎯 RESPONSABILIDADES:
- Análise de autenticidade cultural brasileira
- Detecção de valores e características regionais
- Score de brasilidade e conexão cultural
- Recomendações de comunicação cultural
"""

from typing import Dict, List, Any, Tuple, Optional
import numpy as np
import re
from collections import defaultdict, Counter
import logging

logger = logging.getLogger(__name__)

class AlmaBrasileiraAnalyzer:
    """
    Analisador especializado na Alma Brasileira
    Detecta autenticidade e conexão com valores culturais brasileiros
    """
    
    def __init__(self):
        """Inicializa o analisador da Alma Brasileira"""
        
        # Valores fundamentais da Alma Brasileira
        self.alma_values = {
            'caloroso_hospitaleiro': {
                'weight': 0.20,
                'keywords': [
                    'acolhedor', 'caloroso', 'hospitaleiro', 'receptivo', 'amigável',
                    'carinhoso', 'gentil', 'cordial', 'simpático', 'acolhimento',
                    'abraço', 'beijo', 'carinho', 'afeto', 'amor'
                ],
                'expressions': [
                    'seja bem-vindo', 'fique à vontade', 'como família',
                    'de braços abertos', 'casa aberta', 'portas abertas'
                ]
            },
            'alegre_festivo': {
                'weight': 0.18,
                'keywords': [
                    'alegre', 'feliz', 'festivo', 'animado', 'divertido',
                    'festa', 'celebração', 'comemoração', 'diversão', 'alegria',
                    'sorriso', 'risada', 'gargalhada', 'brincadeira', 'folia'
                ],
                'expressions': [
                    'vamos celebrar', 'que festa', 'que alegria',
                    'hora da festa', 'vamos comemorar', 'que diversão'
                ]
            },
            'criativo_improvisador': {
                'weight': 0.16,
                'keywords': [
                    'criativo', 'improvisador', 'jeitinho', 'gambiarra', 'solução',
                    'criatividade', 'improviso', 'inovação', 'inventivo', 'engenhoso',
                    'desenrolar', 'dar um jeito', 'resolver', 'adaptar'
                ],
                'expressions': [
                    'jeitinho brasileiro', 'dar um jeito', 'quebrar o galho',
                    'gambiarra', 'improviso', 'na criatividade'
                ]
            },
            'musical_ritmado': {
                'weight': 0.15,
                'keywords': [
                    'musical', 'ritmado', 'dançante', 'melodioso', 'harmonioso',
                    'música', 'ritmo', 'dança', 'som', 'batida',
                    'cantoria', 'cantiga', 'melodia', 'harmonia', 'compasso'
                ],
                'expressions': [
                    'no ritmo', 'na batida', 'no compasso',
                    'música boa', 'som massa', 'ritmo gostoso'
                ]
            },
            'resiliente_esperancoso': {
                'weight': 0.14,
                'keywords': [
                    'resiliente', 'forte', 'resistente', 'persistente', 'determinado',
                    'esperança', 'fé', 'coragem', 'garra', 'luta',
                    'superar', 'vencer', 'conquistar', 'perseverar', 'insistir'
                ],
                'expressions': [
                    'não desistir', 'seguir em frente', 'ter fé',
                    'dias melhores', 'vai dar certo', 'força e fé'
                ]
            },
            'emotivo_expressivo': {
                'weight': 0.12,
                'keywords': [
                    'emotivo', 'expressivo', 'sentimental', 'apaixonado', 'intenso',
                    'emoção', 'sentimento', 'paixão', 'coração', 'alma',
                    'emocionar', 'sentir', 'vibrar', 'arrepiar', 'tocante'
                ],
                'expressions': [
                    'do coração', 'com a alma', 'de corpo e alma',
                    'emocionante', 'tocante', 'arrepiante'
                ]
            },
            'solidario_comunitario': {
                'weight': 0.05,
                'keywords': [
                    'solidário', 'unido', 'junto', 'comunitário', 'coletivo',
                    'ajuda', 'apoio', 'união', 'comunidade', 'vizinhança',
                    'mutirão', 'conjunto', 'parceria', 'colaboração', 'cooperação'
                ],
                'expressions': [
                    'juntos somos mais', 'mão na massa', 'todo mundo junto',
                    'união faz a força', 'um por todos', 'lado a lado'
                ]
            }
        }
        
        # Expressões regionais brasileiras
        self.regional_expressions = {
            'Rio de Janeiro': {
                'expressions': ['cara', 'véi', 'massa', 'maneiro', 'legal', 'show', 'gostosa'],
                'cultural_markers': ['carioca', 'zona sul', 'zona norte', 'tijuca', 'barra']
            },
            'São Paulo': {
                'expressions': ['mano', 'cara', 'meu', 'bagulho', 'parada', 'trem'],
                'cultural_markers': ['paulista', 'paulistano', 'centro', 'periferia', 'quebrada']
            },
            'Nordeste': {
                'expressions': ['oxe', 'eita', 'vixe', 'arretado', 'massa', 'bom demais'],
                'cultural_markers': ['nordestino', 'sertão', 'litoral', 'caatinga', 'forró']
            },
            'Sul': {
                'expressions': ['tchê', 'bah', 'guri', 'guria', 'piá', 'barbada'],
                'cultural_markers': ['gaúcho', 'catarinense', 'paranaense', 'sul', 'pampa']
            },
            'Minas Gerais': {
                'expressions': ['uai', 'trem', 'sô', 'né não', 'sei lá', 'tá bom'],
                'cultural_markers': ['mineiro', 'belo horizonte', 'interior', 'montanha']
            }
        }
        
        # Padrões linguísticos brasileiros
        self.linguistic_patterns = {
            'diminutivos': [
                r'\w+inho\b', r'\w+inha\b', r'\w+zinho\b', r'\w+zinha\b'
            ],
            'intensificadores': [
                'muito', 'super', 'mega', 'hiper', 'ultra', 'demais', 'pra caramba'
            ],
            'gerundio_continuo': [
                r'\b(tô|tá|tava|tava|estou|está|estava)\s+\w+ndo\b'
            ]
        }
        
        logger.info("❤️ Alma Brasileira Analyzer inicializado")
    
    def analyze_alma_brasileira(
        self,
        raw_data: Dict[str, Any],
        circles_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Análise completa da Alma Brasileira
        
        Args:
            raw_data: Dados brutos das plataformas
            circles_analysis: Resultado da análise dos círculos
            
        Returns:
            Dict com análise da Alma Brasileira
        """
        logger.info("❤️ Iniciando análise da Alma Brasileira")
        
        try:
            # 1. Extrair texto combinado
            combined_text = self._extract_combined_text(raw_data)
            
            if not combined_text or len(combined_text) < 10:
                return self._empty_alma_result()
            
            # 2. Analisar valores fundamentais
            values_analysis = self._analyze_alma_values(combined_text)
            
            # 3. Detectar características regionais
            regional_analysis = self._analyze_regional_characteristics(combined_text)
            
            # 4. Analisar padrões linguísticos
            linguistic_analysis = self._analyze_linguistic_patterns(combined_text)
            
            # 5. Calcular score de autenticidade
            authenticity_score = self._calculate_authenticity_score(
                values_analysis, regional_analysis, linguistic_analysis
            )
            
            # 6. Integrar com análise dos círculos
            circles_integration = self._integrate_with_circles(
                values_analysis, circles_analysis
            )
            
            # 7. Gerar insights de comunicação
            communication_insights = self._generate_communication_insights(
                values_analysis, regional_analysis, linguistic_analysis
            )
            
            result = {
                'alma_score': authenticity_score['overall_score'],
                'values_analysis': values_analysis,
                'regional_characteristics': regional_analysis,
                'linguistic_authenticity': linguistic_analysis,
                'authenticity_breakdown': authenticity_score,
                'circles_integration': circles_integration,
                'communication_insights': communication_insights,
                'summary': {
                    'alma_intensity': self._classify_alma_intensity(authenticity_score['overall_score']),
                    'dominant_values': self._get_dominant_values(values_analysis),
                    'regional_connection': regional_analysis.get('strongest_region', 'nacional'),
                    'cultural_authenticity': authenticity_score['authenticity_level']
                }
            }
            
            logger.info(f"✅ Alma Brasileira analisada - Score: {authenticity_score['overall_score']:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro na análise da Alma Brasileira: {e}")
            return self._empty_alma_result()
    
    def _extract_combined_text(self, raw_data: Dict[str, Any]) -> str:
        """Extrai e combina texto de todas as plataformas"""
        all_texts = []
        
        for platform, data in raw_data.items():
            if not isinstance(data, dict):
                continue
            
            if platform == 'youtube':
                all_texts.extend([comment.get('text', '') for comment in data.get('comments', [])])
            elif platform == 'reddit':
                for post in data.get('posts', []):
                    all_texts.append(post.get('title', '') + ' ' + post.get('content', ''))
            elif platform == 'news':
                for article in data.get('articles', []):
                    all_texts.append(article.get('title', '') + ' ' + article.get('content', ''))
            elif platform == 'instagram':
                all_texts.extend([post.get('caption', '') for post in data.get('posts', [])])
        
        return ' '.join(all_texts).lower()
    
    def _analyze_alma_values(self, text: str) -> Dict[str, Any]:
        """Analisa valores fundamentais da Alma Brasileira"""
        
        values_scores = {}
        total_matches = 0
        
        for value_name, value_data in self.alma_values.items():
            
            # Contar matches de keywords
            keyword_matches = 0
            for keyword in value_data['keywords']:
                pattern = rf'\b{re.escape(keyword)}\w*\b'
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                keyword_matches += matches
            
            # Contar matches de expressões
            expression_matches = 0
            for expression in value_data['expressions']:
                if expression.lower() in text:
                    expression_matches += 2  # Expressões valem mais
            
            # Score total para o valor
            total_value_matches = keyword_matches + expression_matches
            total_matches += total_value_matches
            
            # Normalizar score (0-1)
            max_possible = len(value_data['keywords']) + (len(value_data['expressions']) * 2)
            normalized_score = min(total_value_matches / max_possible, 1.0) if max_possible > 0 else 0.0
            
            values_scores[value_name] = {
                'score': normalized_score,
                'weighted_score': normalized_score * value_data['weight'],
                'keyword_matches': keyword_matches,
                'expression_matches': expression_matches,
                'weight': value_data['weight']
            }
        
        return {
            'individual_scores': values_scores,
            'total_matches': total_matches,
            'values_detected': len([v for v in values_scores.values() if v['score'] > 0])
        }
    
    def _analyze_regional_characteristics(self, text: str) -> Dict[str, Any]:
        """Analisa características regionais do texto"""
        
        regional_scores = {}
        
        for region, region_data in self.regional_expressions.items():
            
            # Contar expressões regionais
            expression_matches = sum(
                1 for expr in region_data['expressions']
                if expr.lower() in text
            )
            
            # Contar marcadores culturais
            cultural_matches = sum(
                1 for marker in region_data['cultural_markers']
                if marker.lower() in text
            )
            
            # Score regional
            total_possible = len(region_data['expressions']) + len(region_data['cultural_markers'])
            regional_score = (expression_matches + cultural_matches) / total_possible if total_possible > 0 else 0.0
            
            regional_scores[region] = {
                'score': regional_score,
                'expression_matches': expression_matches,
                'cultural_matches': cultural_matches
            }
        
        # Identificar região mais forte
        strongest_region = max(regional_scores.items(), key=lambda x: x[1]['score'])
        
        return {
            'regional_scores': regional_scores,
            'strongest_region': strongest_region[0] if strongest_region[1]['score'] > 0 else 'nacional',
            'regional_strength': strongest_region[1]['score'],
            'has_regional_identity': strongest_region[1]['score'] > 0.1
        }
    
    def _analyze_linguistic_patterns(self, text: str) -> Dict[str, Any]:
        """Analisa padrões linguísticos brasileiros"""
        
        pattern_scores = {}
        
        # Analisar diminutivos
        diminutivos_count = 0
        for pattern in self.linguistic_patterns['diminutivos']:
            diminutivos_count += len(re.findall(pattern, text, re.IGNORECASE))
        
        # Analisar intensificadores
        intensificadores_count = sum(
            text.count(intensifier) for intensifier in self.linguistic_patterns['intensificadores']
        )
        
        # Analisar gerúndio contínuo
        gerundio_count = 0
        for pattern in self.linguistic_patterns['gerundio_continuo']:
            gerundio_count += len(re.findall(pattern, text, re.IGNORECASE))
        
        # Calcular scores normalizados
        text_length = len(text.split())
        
        pattern_scores = {
            'diminutivos': min(diminutivos_count / max(text_length / 100, 1), 1.0),
            'intensificadores': min(intensificadores_count / max(text_length / 50, 1), 1.0),
            'gerundio_continuo': min(gerundio_count / max(text_length / 200, 1), 1.0)
        }
        
        # Score geral de brasilidade linguística
        linguistic_brasilidade = np.mean(list(pattern_scores.values()))
        
        return {
            'pattern_scores': pattern_scores,
            'linguistic_brasilidade': linguistic_brasilidade,
            'brazilian_linguistic_level': self._classify_linguistic_level(linguistic_brasilidade)
        }
    
    def _calculate_authenticity_score(
        self,
        values_analysis: Dict[str, Any],
        regional_analysis: Dict[str, Any],
        linguistic_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calcula score de autenticidade cultural"""
        
        # Peso dos componentes
        weights = {
            'values': 0.6,  # Valores são mais importantes
            'regional': 0.25,
            'linguistic': 0.15
        }
        
        # Score dos valores (média ponderada)
        values_score = sum(
            v['weighted_score'] for v in values_analysis['individual_scores'].values()
        )
        
        # Score regional
        regional_score = regional_analysis['regional_strength']
        
        # Score linguístico
        linguistic_score = linguistic_analysis['linguistic_brasilidade']
        
        # Score geral
        overall_score = (
            values_score * weights['values'] +
            regional_score * weights['regional'] +
            linguistic_score * weights['linguistic']
        )
        
        return {
            'overall_score': overall_score,
            'values_score': values_score,
            'regional_score': regional_score,
            'linguistic_score': linguistic_score,
            'authenticity_level': self._classify_authenticity_level(overall_score),
            'component_weights': weights
        }
    
    def _integrate_with_circles(
        self,
        values_analysis: Dict[str, Any],
        circles_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Integra análise da Alma com círculos culturais"""
        
        # Mapear valores da alma para círculos
        alma_to_circles = {
            'caloroso_hospitaleiro': ['afeto_hospitalidade'],
            'alegre_festivo': ['alegria_celebracao'],
            'criativo_improvisador': ['criatividade_improvisacao'],
            'musical_ritmado': ['musicalidade_expressao'],
            'resiliente_esperancoso': ['resiliencia_fe'],
            'emotivo_expressivo': ['emocional_comportamental'],
            'solidario_comunitario': ['sociocultural']
        }
        
        integration_scores = {}
        circles_scores = circles_analysis.get('circles_scores', {})
        
        for alma_value, related_circles in alma_to_circles.items():
            alma_score = values_analysis['individual_scores'].get(alma_value, {}).get('score', 0.0)
            
            circle_scores = [
                circles_scores.get(circle, {}).get('score', 0.0)
                for circle in related_circles
            ]
            
            avg_circle_score = np.mean(circle_scores) if circle_scores else 0.0
            
            # Correlação entre alma e círculos
            correlation = min(alma_score, avg_circle_score)  # Mínimo indica consistência
            
            integration_scores[alma_value] = {
                'alma_score': alma_score,
                'circles_score': avg_circle_score,
                'correlation': correlation,
                'alignment': 'alta' if correlation > 0.7 else 'média' if correlation > 0.4 else 'baixa'
            }
        
        # Score geral de integração
        overall_integration = np.mean([s['correlation'] for s in integration_scores.values()])
        
        return {
            'individual_integrations': integration_scores,
            'overall_integration_score': overall_integration,
            'integration_level': 'alta' if overall_integration > 0.7 else 'média' if overall_integration > 0.4 else 'baixa'
        }
    
    def _generate_communication_insights(
        self,
        values_analysis: Dict[str, Any],
        regional_analysis: Dict[str, Any],
        linguistic_analysis: Dict[str, Any]
    ) -> List[str]:
        """Gera insights para comunicação cultural"""
        
        insights = []
        
        # Insights baseados nos valores dominantes
        dominant_values = self._get_dominant_values(values_analysis)
        
        for value in dominant_values[:2]:  # Top 2 valores
            if value == 'caloroso_hospitaleiro':
                insights.append("Usar linguagem acolhedora e próxima na comunicação")
            elif value == 'alegre_festivo':
                insights.append("Incorporar elementos festivos e celebrativos")
            elif value == 'criativo_improvisador':
                insights.append("Destacar criatividade e soluções inovadoras")
            elif value == 'musical_ritmado':
                insights.append("Integrar música e ritmos na estratégia")
        
        # Insights regionais
        strongest_region = regional_analysis.get('strongest_region', '')
        if strongest_region != 'nacional':
            insights.append(f"Adaptar linguagem para características {strongest_region.lower()}")
        
        # Insights linguísticos
        if linguistic_analysis['linguistic_brasilidade'] > 0.6:
            insights.append("Usar expressões coloquiais brasileiras autênticas")
        
        return insights
    
    def _get_dominant_values(self, values_analysis: Dict[str, Any]) -> List[str]:
        """Retorna valores dominantes ordenados"""
        individual_scores = values_analysis['individual_scores']
        
        sorted_values = sorted(
            individual_scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        return [value_name for value_name, _ in sorted_values if _['score'] > 0.1]
    
    def _classify_alma_intensity(self, score: float) -> str:
        """Classifica intensidade da Alma Brasileira"""
        if score >= 0.8:
            return 'muito_alta'
        elif score >= 0.6:
            return 'alta'
        elif score >= 0.4:
            return 'média'
        elif score >= 0.2:
            return 'baixa'
        else:
            return 'muito_baixa'
    
    def _classify_authenticity_level(self, score: float) -> str:
        """Classifica nível de autenticidade cultural"""
        if score >= 0.8:
            return 'autêntico'
        elif score >= 0.6:
            return 'moderadamente_autêntico'
        elif score >= 0.4:
            return 'parcialmente_autêntico'
        else:
            return 'pouco_autêntico'
    
    def _classify_linguistic_level(self, score: float) -> str:
        """Classifica nível linguístico brasileiro"""
        if score >= 0.7:
            return 'muito_brasileiro'
        elif score >= 0.5:
            return 'brasileiro'
        elif score >= 0.3:
            return 'moderadamente_brasileiro'
        else:
            return 'pouco_brasileiro'
    
    def _empty_alma_result(self) -> Dict[str, Any]:
        """Retorna resultado vazio em caso de erro"""
        return {
            'alma_score': 0.0,
            'values_analysis': {'individual_scores': {}, 'total_matches': 0, 'values_detected': 0},
            'regional_characteristics': {'regional_scores': {}, 'strongest_region': 'nacional'},
            'linguistic_authenticity': {'pattern_scores': {}, 'linguistic_brasilidade': 0.0},
            'authenticity_breakdown': {'overall_score': 0.0, 'authenticity_level': 'indefinido'},
            'circles_integration': {'overall_integration_score': 0.0, 'integration_level': 'baixa'},
            'communication_insights': [],
            'summary': {
                'alma_intensity': 'indefinida',
                'dominant_values': [],
                'regional_connection': 'nacional',
                'cultural_authenticity': 'indefinido'
            }
        }


# Factory function
def create_alma_analyzer() -> AlmaBrasileiraAnalyzer:
    """Cria instância do analisador Alma Brasileira"""
    return AlmaBrasileiraAnalyzer()


# Para testes diretos
if __name__ == "__main__":
    analyzer = create_alma_analyzer()
    
    # Teste com dados simulados
    test_data = {
        'youtube': {
            'comments': [
                {'text': 'Que alegria, cara! Festa massa demais, né não?'},
                {'text': 'Hospitalidade brasileira não tem igual, meu irmão!'},
                {'text': 'Jeitinho brasileiro sempre dá certo, uai!'}
            ]
        },
        'reddit': {
            'posts': [
                {'title': 'Brasileiro é criativo', 'content': 'Sempre damos um jeito para tudo'},
                {'title': 'Música brasileira', 'content': 'Samba no coração, forró na alma'}
            ]
        }
    }
    
    # Análise dos círculos simulada
    circles_analysis = {
        'circles_scores': {
            'alegria_celebracao': {'score': 0.9},
            'afeto_hospitalidade': {'score': 0.8},
            'criatividade_improvisacao': {'score': 0.7}
        }
    }
    
    result = analyzer.analyze_alma_brasileira(test_data, circles_analysis)
    
    print(f"❤️ Score Alma Brasileira: {result['alma_score']:.2f}")
    print(f"🎯 Intensidade: {result['summary']['alma_intensity']}")
    print(f"🔝 Valores Dominantes: {result['summary']['dominant_values'][:3]}")
    print(f"🌎 Conexão Regional: {result['summary']['regional_connection']}")
    print("✅ Alma Brasileira Analyzer funcionando!")
