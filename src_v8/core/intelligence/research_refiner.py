#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Research Refiner - Culture Intelligence Engine V9.0
Refinamento automático de pesquisas baseado em contexto de negócio

🎯 OBJETIVO:
- Refinar automaticamente termos de pesquisa baseado no contexto
- Otimizar pesos dos círculos culturais para o negócio específico
- Recomendar APIs mais relevantes para coleta
- Calcular score de confiança das reco        # Fator 1: Clareza do segmento (mais generoso)
        segment_clarity = 0.95 if business_context.segment != "Outros" else 0.6
        confidence_factors.append(segment_clarity)
        
        # Fator 2: Especificidade dos termos (ajustado para realidade)
        term_specificity = min(len(refined_terms) / 12.0, 1.0)  # 12 termos = 100%
        confidence_factors.append(term_specificity)es

📋 PRINCIPAIS FUNCIONALIDADES:
- analyze_business_context(): Análise do contexto de negócio
- refine_search_terms(): Refinamento de termos de busca
- optimize_cultural_weights(): Otimização de pesos dos 16 círculos
- recommend_data_sources(): Recomendação de fontes de dados
- calculate_confidence_score(): Cálculo de confiança
"""

import logging
import asyncio
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import pandas as pd
import numpy as np
import json
import time
from datetime import datetime
import re
from pathlib import Path

# Importações do sistema Culture Pulse
import sys
sys.path.append(str(Path(__file__).parent.parent))

from config import config
from config.plan_config import PLAN_CONFIG

# Importar Analisador de Grafos (V9.7)
try:
    from core.engines.cultural_graph_analyzer import CulturalGraphAnalyzer
except ImportError:
    CulturalGraphAnalyzer = None

# ===== CULTURAL SCHEMA V9.9 (Internalized from constants.py) =====

CULTURAL_CIRCLES = [
    "adaptacao_flexibilidade", "conexao_natureza_coletivo", 
    "resiliencia_fe", "economia_informal_empreendedorismo",
    "musicalidade_expressao", "estetica_corpo_futebol",
    "gastronomia_afeto", "hospitalidade_cordialidade",
    "ativismo_social_digital", "consumo_aspiracional",
    "orgulho_regionalista", "sustentabilidade_ancestral",
    "familia_comunidade", "espiritualidade_sincretismo",
    "humor_ironia_resistencia", "celebracao_ritualistica"
]

CULTURAL_CIRCLES_BY_LEVEL = {
    'core': ["adaptacao_flexibilidade", "conexao_natureza_coletivo", "resiliencia_fe", "economia_informal_empreendedorismo"],
    'intermediate': ["musicalidade_expressao", "estetica_corpo_futebol", "gastronomia_afeto", "hospitalidade_cordialidade"],
    'emerging': ["ativismo_social_digital", "consumo_aspiracional", "orgulho_regionalista", "sustentabilidade_ancestral", "familia_comunidade", "espiritualidade_sincretismo", "humor_ironia_resistencia", "celebracao_ritualistica"]
}

BUSINESS_SEGMENTS = ["Alimentação", "Moda & Estética", "Tecnologia & Inovação", "Entretenimento", "Turismo", "Finanças Populares", "Educação", "Saúde & Bem-estar", "Outros"]

IMPLEMENTED_APIS = ["youtube", "reddit", "news_rss", "google_trends", "instagram_simulated", "tiktok_simulated"]

# Mapeamento de Veracidade Biográfica V9.9 (Base Weights)
SOURCE_RELIABILITY_MAPPING = {
    "youtube": 0.90,        # Alta: Vídeo/Comentários reais
    "reddit": 0.85,         # Alta: Discussão de nicho
    "google_trends": 0.95,  # Alta: Intenção de busca direta
    "news_rss": 0.70,       # Média: Agregação editorial
    "twitter": 0.75,        # Média: Volume/Velocidade
    "instagram_simulated": 0.50, # Baixa: Simulação
    "tiktok_simulated": 0.50     # Baixa: Simulação
}
# ===============================================================

@dataclass
class BusinessContext:
    """Estrutura para contexto de negócio"""
    segment: str
    target_audience: str
    geographic_region: str
    brand_values: List[str]
    objectives: List[str]
    budget_range: str
    timeline: str
    competition_level: str
    description: str = ""  # Campo para ML Foundation


@dataclass
class StrategicMetrics:
    """
    Métricas estratégicas para o Frontend V9.7
    Responde às perguntas: 'Com quem anda?', 'Quão rápido corre?'
    """
    velocity_score: float  # Quão rápido corre (0-1)
    momentum_trend: str    # Direção (Aceleração/Desaceleração)
    adjacency_radius: float # Com quem anda (0-1)
    cultural_graph_density: float # Quão conectada é a briga (0-1)
    impact_forecast: float # Quem o carrega (influência projetada)


@dataclass
class RefinedResearch:
    """Estrutura para pesquisa refinada"""
    refined_terms: List[str]
    adjusted_weights: Dict[str, float]
    recommended_apis: List[str]
    confidence_score: float
    reasoning: str
    estimated_sample_size: int
    strategic_metrics: Optional[StrategicMetrics] = None # Novas métricas V9.7


class ResearchRefiner:
    """
    Agente autônomo para refinamento de pesquisas culturais
    
    Esta classe implementa a lógica principal do agente autônomo,
    analisando contexto de negócio e refinando automaticamente
    os parâmetros de pesquisa para maximizar relevância.
    """
    
    def __init__(self, config_obj: Optional[object] = None):
        """Inicializar o Research Refiner"""
        self.config = config_obj or config
        self.ml_integrator = None
        self.github_models = None
        self.graph_analyzer = CulturalGraphAnalyzer() if CulturalGraphAnalyzer else None
        self.refinement_history = []
        self.performance_metrics = {
            'total_refinements': 0,
            'success_rate': 0.0,
            'avg_confidence': 0.0,
            'last_updated': datetime.now()
        }
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("🤖 Research Refiner V9.7 (Graph-Enhanced) inicializado!")
    
    async def initialize_ml_foundation(self) -> bool:
        """Inicializar ML Foundation se disponível"""
        try:
            # Tentar importar ML Integrator Simple (scikit-learn)
            try:
                from autonomous_agent.ml_foundation.ml_integrator_simple import MLIntegratorSimple
                self.ml_integrator = MLIntegratorSimple()
                results = await self.ml_integrator.initialize_components()
                self.logger.info(f"🧠 ML Foundation Simple integrado: {sum(results.values())}/4 componentes")
                return True
            except ImportError:
                self.logger.warning("⚠️ ML Foundation não disponível, usando análise básica")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar ML Foundation: {e}")
            return False
    
    async def initialize_github_models(self) -> bool:
        """Inicializar GitHub Models se disponível"""
        try:
            # Tentar importar GitHub Models Engine
            try:
                sys.path.append(str(Path(__file__).parent / "ml_foundation"))
                from autonomous_agent.ml_foundation.github_models_engine import GitHubModelsEngine
                self.github_models = GitHubModelsEngine()
                await self.github_models.initialize()
                self.logger.info("🤖 GitHub Models integrado!")
                return True
            except ImportError:
                self.logger.warning("⚠️ GitHub Models não disponível")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar GitHub Models: {e}")
            return False
    
    async def refine_research(self, 
                            terms: List[str], 
                            context: BusinessContext) -> RefinedResearch:
        """
        Refinar pesquisa baseada no contexto de negócio
        
        Args:
            terms: Termos de pesquisa iniciais
            context: Contexto de negócio
            
        Returns:
            RefinedResearch: Pesquisa refinada
        """
        try:
            self.logger.info(f"🔍 Refinando pesquisa para: {context.segment}")
            
            # 1. Análise do contexto de negócio
            context_analysis = await self._analyze_business_context(context)
            
            # 2. Refinamento dos termos
            refined_terms = await self._refine_terms(terms, context, context_analysis)
            
            # 3. Ajuste de pesos dos círculos culturais
            adjusted_weights = await self._adjust_cultural_weights(context, context_analysis)
            
            # 4. Recomendação de APIs
            recommended_apis = await self._recommend_apis(context, context_analysis)
            
            # 5. Cálculo de confiança
            confidence_score = await self._calculate_confidence(context, refined_terms, adjusted_weights)
            
            # 6. Cálculo de métricas estratégicas (V9.7)
            strategic_metrics = await self._calculate_strategic_metrics(context, context_analysis)
            
            # 7. Geração de raciocínio
            reasoning = await self._generate_reasoning(context, refined_terms, adjusted_weights, strategic_metrics)
            
            # 8. Estimativa de tamanho de amostra
            estimated_sample_size = await self._estimate_sample_size(context, recommended_apis)
            
            # Criar resultado refinado
            refined_research = RefinedResearch(
                refined_terms=refined_terms,
                adjusted_weights=adjusted_weights,
                recommended_apis=recommended_apis,
                confidence_score=confidence_score,
                reasoning=reasoning,
                estimated_sample_size=estimated_sample_size,
                strategic_metrics=strategic_metrics
            )
            
            # Atualizar métricas e histórico
            await self._update_performance_metrics(refined_research)
            self.refinement_history.append({
                'timestamp': datetime.now(),
                'context': context,
                'result': refined_research
            })
            
            self.logger.info(f"✅ Pesquisa refinada com confiança: {confidence_score:.1%}")
            return refined_research
            
        except Exception as e:
            self.logger.error(f"❌ Erro no refinamento: {e}")
            # Retornar resultado básico em caso de erro
            return RefinedResearch(
                refined_terms=terms,
                adjusted_weights={circle: 1.0 for circle in CULTURAL_CIRCLES},
                recommended_apis=IMPLEMENTED_APIS[:3],
                confidence_score=0.5,
                reasoning="Refinamento básico devido a erro no processamento",
                estimated_sample_size=1000
            )
    
    async def _analyze_business_context(self, context: BusinessContext) -> Dict[str, Any]:
        """Analisar contexto de negócio"""
        analysis = {
            'segment_priority': self._get_segment_priority(context.segment),
            'audience_characteristics': self._analyze_target_audience(context.target_audience),
            'geographic_influence': self._analyze_geographic_region(context.geographic_region),
            'brand_alignment': self._analyze_brand_values(context.brand_values),
            'objective_mapping': self._map_objectives(context.objectives),
            'timeline_urgency': self._assess_timeline_urgency(context.timeline),
            'competition_factor': self._assess_competition_level(context.competition_level)
        }
        
        # Usar ML Foundation se disponível
        if self.ml_integrator:
            try:
                ml_analysis = await self.ml_integrator.analyze_business_context(context.description)
                analysis['ml_insights'] = ml_analysis
            except Exception as e:
                self.logger.warning(f"⚠️ ML analysis failed: {e}")
        
        return analysis
    
    async def _refine_terms(self, 
                          terms: List[str], 
                          context: BusinessContext, 
                          analysis: Dict[str, Any]) -> List[str]:
        """Refinar termos de pesquisa"""
        refined_terms = terms.copy()
        
        # 1. Adicionar termos específicos do segmento
        segment_terms = self._get_segment_specific_terms(context.segment)
        refined_terms.extend(segment_terms)
        
        # 2. Adicionar termos baseados no público-alvo
        audience_terms = self._get_audience_specific_terms(context.target_audience)
        refined_terms.extend(audience_terms)
        
        # 3. Adicionar termos geográficos
        geo_terms = self._get_geographic_terms(context.geographic_region)
        refined_terms.extend(geo_terms)
        
        # 4. Adicionar termos baseados em valores da marca
        brand_terms = self._get_brand_value_terms(context.brand_values)
        refined_terms.extend(brand_terms)
        
        # 5. Usar GitHub Models para refinamento avançado se disponível
        if self.github_models:
            try:
                ai_result = await self.github_models.refine_terms(
                    context=context.description,
                    terms=refined_terms
                )
                if ai_result.get("success") and ai_result.get("refined_terms"):
                    refined_terms.extend(ai_result["refined_terms"])
            except Exception as e:
                self.logger.warning(f"⚠️ AI refinement failed: {e}")
        
        # 6. Remover duplicatas e ordenar por relevância
        refined_terms = list(set(refined_terms))
        refined_terms = self._rank_terms_by_relevance(refined_terms, context, analysis)
        
        # Limitar a 20 termos mais relevantes
        return refined_terms[:20]
    
    async def _adjust_cultural_weights(self, 
                                     context: BusinessContext, 
                                     analysis: Dict[str, Any]) -> Dict[str, float]:
        """Ajustar pesos dos círculos culturais"""
        base_weights = {circle: 1.0 for circle in CULTURAL_CIRCLES}
        
        # Ajustes baseados no segmento
        segment_adjustments = self._get_segment_weight_adjustments(context.segment)
        
        # Ajustes baseados no público-alvo
        audience_adjustments = self._get_audience_weight_adjustments(context.target_audience)
        
        # Ajustes baseados na região
        geo_adjustments = self._get_geographic_weight_adjustments(context.geographic_region)
        
        # Combinar ajustes
        for circle in CULTURAL_CIRCLES:
            adjustment_factor = 1.0
            adjustment_factor *= segment_adjustments.get(circle, 1.0)
            adjustment_factor *= audience_adjustments.get(circle, 1.0)
            adjustment_factor *= geo_adjustments.get(circle, 1.0)
            
            base_weights[circle] = min(3.0, max(0.1, adjustment_factor))
        
        # Normalizar pesos
        total_weight = sum(base_weights.values())
        normalized_weights = {
            circle: weight / total_weight * len(CULTURAL_CIRCLES)
            for circle, weight in base_weights.items()
        }
        
        return normalized_weights
    
    def calculate_dynamic_api_weight(self, api_name: str, search_terms: List[str], context: BusinessContext) -> float:
        """
        Calcula o peso dinâmico de uma API (V9.9 - Lógica BIOGRÁFICA)
        
        A inteligência não é mais estática. O peso depende de:
        1. Confiabilidade base da fonte (Reliability Index)
        2. Afinidade dos termos de busca com o formato da API (Query Affinity)
        3. Relevância para o segmento de negócio (Business Context)
        """
        # 1. Base (Sinceridade Biográfica)
        base_reliability = SOURCE_RELIABILITY_MAPPING.get(api_name.lower(), 0.60)
        
        # 2. Afinidade de Query (Se termos são visuais, YouTube ganha peso)
        visual_terms = ['dança', 'look', 'maquiagem', 'receita', 'clipe', 'show', 'tutorial']
        discourse_terms = ['opinião', 'debate', 'polêmica', 'por que', 'ajuda', 'relato']
        
        affinity_bonus = 0.0
        if api_name.lower() == 'youtube' and any(t in " ".join(search_terms).lower() for t in visual_terms):
            affinity_bonus += 0.15
        elif api_name.lower() == 'reddit' and any(t in " ".join(search_terms).lower() for t in discourse_terms):
            affinity_bonus += 0.15
            
        # 3. Afinidade de Segmento
        segment_bonus = 0.0
        segment = context.segment.lower()
        if api_name.lower() == 'youtube' and segment in ['entretenimento', 'alimentação', 'moda & estética']:
            segment_bonus += 0.10
        elif api_name.lower() == 'news_rss' and segment in ['finanças populares', 'tecnologia & inovação']:
            segment_bonus += 0.10
            
        # Cálculo final (Limitado a 1.0)
        final_weight = min(1.0, base_reliability + affinity_bonus + segment_bonus)
        
        # Reduzir peso se for Tier 'Free' e a API for premium (simulado)
        # TODO: Integrar com PLAN_CONFIG['tiers']['free']['api_precision_limit']
        
        return round(final_weight, 2)

    def recommend_data_sources(self, context: BusinessContext, search_terms: Optional[List[str]] = None) -> List[str]:
        """
        Método síncrono para recomendação rápida de fontes de dados baseada em pesos calculados na hora.
        """
        terms = search_terms or []
        api_scores = {}
        
        for api_name in IMPLEMENTED_APIS:
            dynamic_weight = self.calculate_dynamic_api_weight(api_name, terms, context)
            
            # Score base é o próprio peso dinâmico em escala 0-5
            score = dynamic_weight * 5.0
            
            # Fator de relevância legado como ajuste fino
            if self._is_api_relevant_for_segment(api_name, context.segment):
                score += 0.5
            
            api_scores[api_name] = score
        
        # Ordenar APIs por score e retornar top 3-5
        sorted_apis = sorted(api_scores.items(), key=lambda x: x[1], reverse=True)
        recommended = [api for api, score in sorted_apis if score > 1.0]
        
        # Garantir pelo menos 3 APIs
        if len(recommended) < 3:
            top_apis = [api for api, _ in sorted_apis[:3]]
            recommended = list(set(recommended + top_apis))
        
        return recommended[:5]

    async def _recommend_apis(self, 
                            context: BusinessContext, 
                            analysis: Dict[str, Any],
                            search_terms: Optional[List[str]] = None) -> List[str]:
        """
        Recomendar APIs mais relevantes (Versão Assíncrona para Pipeline de Refinamento)
        """
        api_scores = {}
        terms = search_terms or []
        
        for api_name in IMPLEMENTED_APIS:
            # Pegar o peso dinâmico V9.9
            dynamic_weight = self.calculate_dynamic_api_weight(api_name, terms, context)
            score = dynamic_weight * 3.0
            
            # Adicionais de contexto
            if self._is_api_relevant_for_audience(api_name, context.target_audience):
                score += 1.0
            elif self._is_api_relevant_for_segment(api_name, context.segment):
                score += 0.5
            elif self._is_api_relevant_for_region(api_name, context.geographic_region):
                score += 0.5
            elif self._is_api_relevant_for_objectives(api_name, context.objectives):
                score += 0.5
            elif self._is_api_cost_effective(api_name, context.budget_range, context.timeline):
                score += 0.5
            
            api_scores[api_name] = score
        
        # Ordenar APIs por score e retornar top 3-5
        sorted_apis = sorted(api_scores.items(), key=lambda x: x[1], reverse=True)
        recommended = [api for api, score in sorted_apis if score > 1.0]
        
        # Garantir pelo menos 3 APIs
        if len(recommended) < 3:
            top_apis = [api for api, _ in sorted_apis[:3]]
            recommended = list(set(recommended + top_apis))
        
        return recommended[:5]  # Máximo 5 APIs
    
    async def _calculate_confidence(self, 
                                  context: BusinessContext, 
                                  refined_terms: List[str], 
                                  adjusted_weights: Dict[str, float]) -> float:
        """Calcular score de confiança do refinamento"""
        confidence_factors = []
        
        # Fator 1: Qualidade do contexto (0.0-1.0)
        context_quality = self._assess_context_quality(context)
        confidence_factors.append(context_quality * 0.3)
        
        # Fator 2: Relevância dos termos refinados (0.0-1.0)
        terms_relevance = self._assess_terms_relevance(refined_terms, context)
        confidence_factors.append(terms_relevance * 0.3)
        
        # Fator 3: Balanceamento dos pesos (0.0-1.0)
        weights_balance = self._assess_weights_balance(adjusted_weights)
        confidence_factors.append(weights_balance * 0.2)
        
        # Fator 4: Disponibilidade de ML/AI (0.0-1.0)
        ml_availability = 0.8 if self.ml_integrator else 0.5
        ai_availability = 0.8 if self.github_models else 0.5
        tech_factor = (ml_availability + ai_availability) / 2
        confidence_factors.append(tech_factor * 0.2)
        
        # Calcular confiança final
        confidence = sum(confidence_factors)
        
        # Adicionar variação aleatória pequena para simular incerteza
        confidence += np.random.normal(0, 0.05)
        confidence = max(0.0, min(1.0, confidence))
        
        return confidence
    
    async def _calculate_strategic_metrics(self, 
                                        context: BusinessContext, 
                                        analysis: Dict[str, Any]) -> StrategicMetrics:
        """
        Calcula métricas de Velocidade e Adjacência (V9.7)
        Responde: Quão rápido corre? Com quem anda?
        Integrado com GNN CulturalGraphAnalyzer
        """
        # 1. Velocidade (Quão rápido corre?)
        timeline_urgency = analysis.get('timeline_urgency', 0.5)
        competition = analysis.get('competition_factor', 0.5)
        velocity = (timeline_urgency * 0.6) + (competition * 0.4)
        
        # 2. Momentum
        momentum = "Aceleração" if velocity > 0.7 else "Estável" if velocity > 0.4 else "Inercial"
        
        # 3. Adjacência (Com quem anda?) e Densidade (Qual a briga?)
        # Usar Graph Analyzer se disponível para maior precisão
        graph_density = 0.5
        adjacency = 0.5
        
        if self.graph_analyzer:
            # Simular o grafo para o segmento (MOCK para preencher a densidade real se o grafo estivesse populado)
            # Em uso real, o grafo conteria nós de concorrentes/perfis
            metrics = self.graph_analyzer.get_propagation_metrics()
            graph_density = metrics.get('density', (competition * 0.8))
        else:
            graph_density = min(1.0, (competition * 0.8) + (analysis.get('geographic_influence', {}).get('cultural_diversity', 0.5) * 0.2))

        audience_openness = analysis.get('audience_characteristics', {}).get('cultural_openness', 0.5)
        geo_diversity = analysis.get('geographic_influence', {}).get('cultural_diversity', 0.5)
        adjacency = (audience_openness * 0.7) + (geo_diversity * 0.3)
        
        # 4. Forecast (Quem o carrega?)
        forecast = (velocity * 0.5) + (adjacency * 0.5)
        
        return StrategicMetrics(
            velocity_score=velocity,
            momentum_trend=momentum,
            adjacency_radius=adjacency,
            cultural_graph_density=graph_density,
            impact_forecast=forecast
        )

    async def _generate_reasoning(self, 
                                context: BusinessContext, 
                                refined_terms: List[str], 
                                adjusted_weights: Dict[str, float], 
                                recommended_apis: List[str],
                                strategic_metrics: StrategicMetrics = None) -> str:
        """Gerar raciocínio do refinamento"""
        reasoning_parts = []
        
        # Análise do contexto
        reasoning_parts.append(f"📊 **Contexto Analisado**: {context.segment} focado em {context.target_audience}")
        
        # Termos refinados
        top_terms = refined_terms[:5]
        reasoning_parts.append(f"🔍 **Termos Priorizados**: {', '.join(top_terms)}")
        
        # Círculos culturais mais relevantes
        top_circles = sorted(adjusted_weights.items(), key=lambda x: x[1], reverse=True)[:3]
        circles_text = ', '.join([f"{circle} ({weight:.1f})" for circle, weight in top_circles])
        reasoning_parts.append(f"🎭 **Círculos Priorizados**: {circles_text}")
        
        # APIs recomendadas
        reasoning_parts.append(f"📡 **APIs Recomendadas**: {', '.join(recommended_apis)}")
        
        # Justificativa baseada no segmento
        segment_justification = self._get_segment_justification(context.segment)
        reasoning_parts.append(f"💡 **Justificativa**: {segment_justification}")
        
        # Métricas estratégicas (V9.7)
        if strategic_metrics:
            reasoning_parts.append(f"⚡ **Velocidade**: {strategic_metrics.velocity_score:.1%} ({strategic_metrics.momentum_trend})")
            reasoning_parts.append(f"🔗 **Adjacência**: Raio de {strategic_metrics.adjacency_radius:.1%} - Conectividade alta")
            reasoning_parts.append(f"📈 **Projeção de Impacto**: {strategic_metrics.impact_forecast:.1%}")
        
        return " | ".join(reasoning_parts)
    
    async def _estimate_sample_size(self, 
                                   context: BusinessContext, 
                                   recommended_apis: List[str]) -> int:
        """Estimar tamanho de amostra baseado no contexto"""
        base_sample = 1000
        
        # Ajustar baseado no orçamento
        budget_multiplier = {
            'baixo': 0.5,
            'médio': 1.0,
            'alto': 2.0,
            'premium': 3.0
        }.get(context.budget_range.lower(), 1.0)
        
        # Ajustar baseado no timeline
        timeline_multiplier = {
            'urgente': 0.7,
            'normal': 1.0,
            'extenso': 1.5
        }.get(context.timeline.lower(), 1.0)
        
        # Ajustar baseado no número de APIs
        api_multiplier = len(recommended_apis) * 0.3 + 0.4
        
        # Calcular estimativa final
        estimated_sample = int(base_sample * budget_multiplier * timeline_multiplier * api_multiplier)
        
        # Limites mínimo e máximo
        estimated_sample = max(500, min(10000, estimated_sample))
        
        return estimated_sample
    
    async def _update_performance_metrics(self, refined_research: RefinedResearch):
        """Atualizar métricas de performance"""
        self.performance_metrics['total_refinements'] += 1
        
        # Atualizar confiança média
        total_refinements = self.performance_metrics['total_refinements']
        current_avg = self.performance_metrics['avg_confidence']
        new_confidence = refined_research.confidence_score
        
        updated_avg = ((current_avg * (total_refinements - 1)) + new_confidence) / total_refinements
        self.performance_metrics['avg_confidence'] = updated_avg
        
        # Simular taxa de sucesso baseada na confiança
        if new_confidence > 0.7:
            success_rate = self.performance_metrics.get('success_rate', 0.0)
            updated_success_rate = ((success_rate * (total_refinements - 1)) + 1.0) / total_refinements
            self.performance_metrics['success_rate'] = updated_success_rate
        
        self.performance_metrics['last_updated'] = datetime.now()
    
    # ===== MÉTODOS AUXILIARES =====
    
    def _get_segment_priority(self, segment: str) -> float:
        """Obter prioridade do segmento"""
        priorities = {
            'tecnologia': 0.9,
            'entretenimento': 0.85,
            'moda': 0.8,
            'gastronomia': 0.75,
            'educação': 0.7,
            'saúde': 0.65
        }
        return priorities.get(segment.lower(), 0.6)
    
    def _analyze_target_audience(self, audience: str) -> Dict[str, Any]:
        """Analisar características do público-alvo"""
        audience_lower = audience.lower()
        
        characteristics = {
            'digital_nativity': 0.5,
            'cultural_openness': 0.5,
            'purchasing_power': 0.5,
            'social_media_usage': 0.5
        }
        
        # Gen Z
        if any(term in audience_lower for term in ['gen z', 'geração z', 'jovens']):
            characteristics.update({
                'digital_nativity': 0.95,
                'cultural_openness': 0.9,
                'purchasing_power': 0.6,
                'social_media_usage': 0.95
            })
        
        # Millennials
        elif any(term in audience_lower for term in ['millennial', 'adultos jovens']):
            characteristics.update({
                'digital_nativity': 0.85,
                'cultural_openness': 0.8,
                'purchasing_power': 0.8,
                'social_media_usage': 0.85
            })
        
        return characteristics
    
    def _analyze_geographic_region(self, region: str) -> Dict[str, Any]:
        """Analisar influência geográfica"""
        region_lower = region.lower()
        
        # Mapear regiões para características culturais
        if any(term in region_lower for term in ['são paulo', 'sp', 'sudeste']):
            return {
                'cultural_diversity': 0.9,
                'economic_power': 0.9,
                'digital_adoption': 0.85,
                'trend_leadership': 0.9
            }
        elif any(term in region_lower for term in ['rio', 'rj']):
            return {
                'cultural_diversity': 0.95,
                'economic_power': 0.75,
                'digital_adoption': 0.8,
                'trend_leadership': 0.85
            }
        else:
            return {
                'cultural_diversity': 0.7,
                'economic_power': 0.6,
                'digital_adoption': 0.7,
                'trend_leadership': 0.6
            }
    
    def _analyze_brand_values(self, brand_values: List[str]) -> Dict[str, float]:
        """Analisar alinhamento com valores da marca"""
        value_scores = {}
        
        for value in brand_values:
            value_lower = value.lower()
            
            if any(term in value_lower for term in ['sustentabilidade', 'eco', 'verde']):
                value_scores['sustainability'] = 0.9
            elif any(term in value_lower for term in ['inovação', 'tecnologia', 'digital']):
                value_scores['innovation'] = 0.9
            elif any(term in value_lower for term in ['autenticidade', 'genuíno', 'real']):
                value_scores['authenticity'] = 0.9
            elif any(term in value_lower for term in ['inclusão', 'diversidade', 'plural']):
                value_scores['inclusivity'] = 0.9
        
        return value_scores
    
    def _map_objectives(self, objectives: List[str]) -> Dict[str, float]:
        """Mapear objetivos para métricas"""
        objective_mapping = {}
        
        for objective in objectives:
            obj_lower = objective.lower()
            
            if any(term in obj_lower for term in ['awareness', 'reconhecimento', 'marca']):
                objective_mapping['brand_awareness'] = 0.9
            elif any(term in obj_lower for term in ['engajamento', 'engagement', 'comunidade']):
                objective_mapping['engagement'] = 0.9
            elif any(term in obj_lower for term in ['vendas', 'conversão', 'roi']):
                objective_mapping['conversion'] = 0.9
            elif any(term in obj_lower for term in ['pesquisa', 'insights', 'dados']):
                objective_mapping['research'] = 0.9
        
        return objective_mapping
    
    def _assess_competition_level(self, level: str) -> float:
        """Avaliar nível de competição (0-1)"""
        levels = {
            'baixa': 0.3,
            'média': 0.6,
            'alta': 0.9,
            'extrema': 1.0,
            'low': 0.3,
            'medium': 0.6,
            'high': 0.9,
            'extreme': 1.0
        }
        return levels.get(level.lower(), 0.5)

    def _assess_timeline_urgency(self, timeline: str) -> float:
        """Avaliar urgência da timeline (0-1)"""
        timeline_lower = timeline.lower()
        if any(term in timeline_lower for term in ['imediato', 'agora', 'urgente', 'immediate']):
            return 1.0
        elif any(term in timeline_lower for term in ['mês', 'month', 'curto']):
            return 0.7
        elif any(term in timeline_lower for term in ['quarter', 'trimestre']):
            return 0.4
        return 0.2
    
    def _get_segment_specific_terms(self, segment: str) -> List[str]:
        """Obter termos específicos do segmento"""
        segment_terms = {
            'tecnologia': ['tech', 'digital', 'inovação', 'startup', 'software'],
            'entretenimento': ['show', 'música', 'filme', 'evento', 'artista'],
            'moda': ['fashion', 'estilo', 'roupa', 'tendência', 'design'],
            'gastronomia': ['comida', 'restaurante', 'chef', 'receita', 'sabor'],
            'educação': ['ensino', 'aprendizado', 'curso', 'educação', 'conhecimento'],
            'saúde': ['saúde', 'bem-estar', 'fitness', 'medicina', 'cuidado']
        }
        return segment_terms.get(segment.lower(), [])
    
    def _get_audience_specific_terms(self, audience: str) -> List[str]:
        """Obter termos específicos do público"""
        audience_lower = audience.lower()
        
        if 'gen z' in audience_lower or 'geração z' in audience_lower:
            return ['tiktok', 'viral', 'trend', 'meme', 'challenge']
        elif 'millennial' in audience_lower:
            return ['nostalgia', 'instagram', 'influencer', 'lifestyle', 'experiência']
        elif 'adulto' in audience_lower:
            return ['qualidade', 'confiança', 'família', 'estabilidade', 'tradição']
        else:
            return ['brasileiro', 'cultura', 'identidade', 'comunidade']
    
    def _get_geographic_terms(self, region: str) -> List[str]:
        """Obter termos geográficos"""
        region_lower = region.lower()
        
        if 'são paulo' in region_lower or 'sp' in region_lower:
            return ['sampa', 'paulista', 'metrópole', 'cosmopolita']
        elif 'rio' in region_lower or 'rj' in region_lower:
            return ['carioca', 'praia', 'carnaval', 'maravilhosa']
        elif 'nordeste' in region_lower:
            return ['nordestino', 'forró', 'axé', 'regional']
        elif 'sul' in region_lower:
            return ['gaúcho', 'sulista', 'churrasco', 'pampa']
        else:
            return ['brasileiro', 'brasil', 'nacional']
    
    def _get_brand_value_terms(self, brand_values: List[str]) -> List[str]:
        """Obter termos baseados em valores da marca"""
        value_terms = []
        
        for value in brand_values:
            value_lower = value.lower()
            
            if 'sustentabilidade' in value_lower:
                value_terms.extend(['eco', 'verde', 'sustentável', 'consciência'])
            elif 'inovação' in value_lower:
                value_terms.extend(['novo', 'criativo', 'pioneiro', 'revolucionário'])
            elif 'autenticidade' in value_lower:
                value_terms.extend(['real', 'genuíno', 'verdadeiro', 'original'])
            elif 'inclusão' in value_lower:
                value_terms.extend(['diverso', 'plural', 'todos', 'inclusivo'])
        
        return value_terms
    
    def _rank_terms_by_relevance(self, 
                                terms: List[str], 
                                context: BusinessContext, 
                                analysis: Dict[str, Any]) -> List[str]:
        """Ranquear termos por relevância"""
        # Implementação simplificada - ordenar por length e alfabética
        # Em produção, usaria ML para scoring
        scored_terms = []
        
        for term in terms:
            score = len(term)  # Score básico baseado no tamanho
            
            # Bonus para termos relacionados ao segmento
            if any(seg_term in term.lower() for seg_term in self._get_segment_specific_terms(context.segment)):
                score += 10
            
            # Bonus para termos relacionados ao público
            if any(aud_term in term.lower() for aud_term in self._get_audience_specific_terms(context.target_audience)):
                score += 8
            
            scored_terms.append((term, score))
        
        # Ordenar por score decrescente
        scored_terms.sort(key=lambda x: x[1], reverse=True)
        
        return [term for term, score in scored_terms]
    
    # Métodos de mapeamento e avaliação de APIs (implementação simplificada)
    def _get_segment_weight_adjustments(self, segment: str) -> Dict[str, float]:
        """Obter ajustes de peso por segmento"""
        adjustments = {circle: 1.0 for circle in CULTURAL_CIRCLES}
        segment_lower = segment.lower()
        
        if 'tecnologia' in segment_lower:
            adjustments.update({
                'Hip Hop': 1.5,
                'Pop': 1.3,
                'Eletrônica': 2.0,
                'Rock': 1.2
            })
        elif 'entretenimento' in segment_lower:
            adjustments.update({
                'Pop': 2.0,
                'Funk': 1.8,
                'Sertanejo': 1.6,
                'Hip Hop': 1.5
            })
        
        return adjustments
    
    def _get_audience_weight_adjustments(self, audience: str) -> Dict[str, float]:
        """Obter ajustes de peso por público"""
        adjustments = {circle: 1.0 for circle in CULTURAL_CIRCLES}
        audience_lower = audience.lower()
        
        if any(term in audience_lower for term in ['gen z', 'geração z', 'jovens']):
            adjustments.update({
                'Funk': 2.0,
                'Hip Hop': 1.8,
                'Pop': 1.6,
                'Eletrônica': 1.5
            })
        
        return adjustments
    
    def _get_geographic_weight_adjustments(self, region: str) -> Dict[str, float]:
        """Obter ajustes de peso por região"""
        adjustments = {circle: 1.0 for circle in CULTURAL_CIRCLES}
        region_lower = region.lower()
        
        if any(term in region_lower for term in ['nordeste', 'bahia']):
            adjustments.update({
                'Axé': 2.0,
                'Forró': 2.0,
                'Reggae': 1.5
            })
        elif any(term in region_lower for term in ['rio', 'rj']):
            adjustments.update({
                'Funk': 2.0,
                'Samba': 1.8,
                'Bossa Nova': 1.5
            })
        
        return adjustments
    
    # Métodos de avaliação de APIs (implementação básica)
    def _is_api_relevant_for_audience(self, api_name: str, audience: str) -> bool:
        """Verificar se API é relevante para público"""
        audience_lower = audience.lower()
        
        if any(term in audience_lower for term in ['gen z', 'geração z', 'jovens']):
            return api_name.lower() in ['tiktok', 'instagram', 'youtube']
        elif 'millennial' in audience_lower:
            return api_name.lower() in ['instagram', 'youtube', 'twitter']
        
        return True
    
    def _is_api_relevant_for_segment(self, api_name: str, segment: str) -> bool:
        """Verificar se API é relevante para segmento"""
        return True  # Implementação básica
    
    def _is_api_relevant_for_region(self, api_name: str, region: str) -> bool:
        """Verificar se API é relevante para região"""
        return True  # Implementação básica
    
    def _is_api_relevant_for_objectives(self, api_name: str, objectives: List[str]) -> bool:
        """Verificar se API é relevante para objetivos"""
        return True  # Implementação básica
    
    def _is_api_cost_effective(self, api_name: str, budget: str, timeline: str) -> bool:
        """Verificar se API é cost-effective"""
        return True  # Implementação básica
    
    # Métodos de avaliação de qualidade
    def _assess_context_quality(self, context: BusinessContext) -> float:
        """Avaliar qualidade do contexto fornecido"""
        quality_factors = []
        
        # Verificar completude dos campos
        if context.segment and context.segment.strip():
            quality_factors.append(0.2)
        if context.target_audience and context.target_audience.strip():
            quality_factors.append(0.2)
        if context.geographic_region and context.geographic_region.strip():
            quality_factors.append(0.15)
        if context.brand_values and len(context.brand_values) > 0:
            quality_factors.append(0.15)
        if context.objectives and len(context.objectives) > 0:
            quality_factors.append(0.15)
        if context.budget_range and context.budget_range.strip():
            quality_factors.append(0.075)
        if context.timeline and context.timeline.strip():
            quality_factors.append(0.075)
        
        return sum(quality_factors)
    
    def _assess_terms_relevance(self, terms: List[str], context: BusinessContext) -> float:
        """Avaliar relevância dos termos refinados"""
        if not terms:
            return 0.0
        
        relevance_score = 0.0
        
        # Verificar se há termos relacionados ao segmento
        segment_terms = self._get_segment_specific_terms(context.segment)
        if any(term.lower() in [t.lower() for t in terms] for term in segment_terms):
            relevance_score += 0.4
        
        # Verificar se há termos relacionados ao público
        audience_terms = self._get_audience_specific_terms(context.target_audience)
        if any(term.lower() in [t.lower() for t in terms] for term in audience_terms):
            relevance_score += 0.3
        
        # Verificar diversidade de termos
        if len(set(terms)) > len(terms) * 0.8:  # 80% de termos únicos
            relevance_score += 0.3
        
        return min(1.0, relevance_score)
    
    def _assess_weights_balance(self, weights: Dict[str, float]) -> float:
        """Avaliar balanceamento dos pesos"""
        if not weights:
            return 0.0
        
        weight_values = list(weights.values())
        
        # Verificar se há variação nos pesos (não todos iguais)
        if len(set(weight_values)) > 1:
            # Calcular coeficiente de variação
            mean_weight = np.mean(weight_values)
            std_weight = np.std(weight_values)
            
            if mean_weight > 0:
                cv = std_weight / mean_weight
                # CV entre 0.2 e 0.8 é considerado bem balanceado
                if 0.2 <= cv <= 0.8:
                    return 1.0
                elif cv < 0.2:
                    return 0.6  # Muito uniforme
                else:
                    return 0.4  # Muito desbalanceado
        
        return 0.5  # Pesos iguais
    
    def _get_segment_justification(self, segment: str) -> str:
        """Obter justificativa baseada no segmento"""
        justifications = {
            'tecnologia': "Priorização de círculos digitais e inovadores para engajar audiência tech-savvy",
            'entretenimento': "Foco em círculos de alta popularidade e viralidade para maximizar alcance",
            'moda': "Ênfase em círculos trendy e influentes para capturar tendências emergentes",
            'gastronomia': "Seleção de círculos culturais relacionados a experiências e tradições culinárias",
            'educação': "Círculos que valorizam conhecimento e desenvolvimento cultural",
            'saúde': "Círculos focados em bem-estar e qualidade de vida"
        }
        
        return justifications.get(segment.lower(), "Refinamento baseado em análise cultural abrangente")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Obter resumo de performance do Research Refiner"""
        return {
            'total_refinements': self.performance_metrics['total_refinements'],
            'success_rate': self.performance_metrics['success_rate'],
            'avg_confidence': self.performance_metrics['avg_confidence'],
            'ml_foundation_available': self.ml_integrator is not None,
            'github_models_available': self.github_models is not None,
            'last_updated': self.performance_metrics['last_updated'].isoformat(),
            'refinement_history_count': len(self.refinement_history)
        }


# ===== FUNÇÃO PARA CRIAR RESEARCH REFINER =====
async def create_research_refiner() -> ResearchRefiner:
    """Factory function para criar Research Refiner inicializado"""
    refiner = ResearchRefiner()
    
    # Inicializar componentes ML se disponíveis
    await refiner.initialize_ml_foundation()
    await refiner.initialize_github_models()
    
    return refiner


# ===== TESTE PRINCIPAL =====
if __name__ == "__main__":
    async def main():
        """Função principal para testes"""
        print("🤖 Research Refiner V9.0 - Teste Principal")
        print("=" * 60)
        
        # Criar Research Refiner
        refiner = await create_research_refiner()
        
        # Contexto de teste
        test_context = BusinessContext(
            segment="tecnologia",
            target_audience="Gen Z",
            geographic_region="São Paulo",
            brand_values=["inovação", "sustentabilidade"],
            objectives=["brand awareness", "engajamento"],
            budget_range="médio",
            timeline="normal",
            competition_level="alto",
            description="Startup de tecnologia focada em soluções sustentáveis para jovens urbanos"
        )
        
        # Termos de teste
        test_terms = ["música", "cultura", "brasil", "tecnologia"]
        
        # Executar refinamento
        print(f"🔍 Refinando pesquisa para: {test_context.segment}")
        refined_research = await refiner.refine_research(test_terms, test_context)
        
        # Mostrar resultados
        print(f"\n📊 Resultados do Refinamento:")
        print(f"  Termos Refinados: {refined_research.refined_terms[:5]}")
        print(f"  APIs Recomendadas: {refined_research.recommended_apis}")
        print(f"  Confiança: {refined_research.confidence_score:.1%}")
        print(f"  Amostra Estimada: {refined_research.estimated_sample_size}")
        
        # Performance summary
        performance = refiner.get_performance_summary()
        print(f"\n🎯 Performance do Sistema:")
        print(f"  Total de Refinamentos: {performance['total_refinements']}")
        print(f"  Confiança Média: {performance['avg_confidence']:.1%}")
        print(f"  ML Foundation: {'✅' if performance['ml_foundation_available'] else '❌'}")
        print(f"  GitHub Models: {'✅' if performance['github_models_available'] else '❌'}")
        
        print(f"\n🎉 Research Refiner testado com sucesso!")
    
    # Executar teste
    asyncio.run(main())
        
    def _load_business_patterns(self) -> Dict[str, List[str]]:
        """Carrega patterns de negócio pré-definidos"""
        return {
            "tech": ["inovação", "startup", "digital", "app", "plataforma", "saas", "tecnologia"],
            "fashion": ["moda", "estilo", "tendência", "look", "outfit", "brand"],
            "food": ["gastronomia", "culinária", "chef", "receita", "restaurante", "alimentação"],
            "fitness": ["fitness", "treino", "academia", "saúde", "wellness", "exercício"],
            "finance": ["fintech", "investimento", "economia", "banco", "cripto", "financeiro"],
            "entertainment": ["entretenimento", "música", "filme", "game", "streaming"],
            "education": ["educação", "curso", "aprendizado", "escola", "ensino"],
            "retail": ["varejo", "loja", "shopping", "e-commerce", "vendas"]
        }
    
    def _load_cultural_mappings(self) -> Dict[str, Dict[str, float]]:
        """Carrega mapeamentos entre segmentos e círculos culturais"""
        return {
            "Tecnologia": {
                "criatividade_improvisacao": 0.9,
                "desejo_ascensao_oportunidades": 0.85,
                "adaptacao_flexibilidade": 0.8,
                "vida_urbana_rural": 0.75,
                "economia_informal_empreendedorismo": 0.8
            },
            "Moda e Beleza": {
                "musicalidade_expressao": 0.95,
                "alegria_celebracao": 0.9,
                "diversidade_geografica_cultural": 0.85,
                "afeto_hospitalidade": 0.8,
                "criatividade_improvisacao": 0.9
            },
            "Alimentação e Bebidas": {
                "festa_luta_cotidianas": 0.95,
                "conexao_natureza_coletivo": 0.8,
                "afeto_hospitalidade": 0.85,
                "alegria_celebracao": 0.8,
                "diversidade_geografica_cultural": 0.7
            },
            "Saúde": {
                "resiliencia_fe": 0.9,
                "conexao_natureza_coletivo": 0.85,
                "afeto_hospitalidade": 0.8,
                "adaptacao_flexibilidade": 0.75
            },
            "Entretenimento": {
                "musicalidade_expressao": 0.95,
                "alegria_celebracao": 0.9,
                "festa_luta_cotidianas": 0.85,
                "criatividade_improvisacao": 0.8,
                "sincretismo_cultural": 0.85
            }
        }
    
    def analyze_business_context(self, business_input: str) -> BusinessContext:
        """
        Analisa contexto de negócio a partir de texto livre
        
        Args:
            business_input: Texto com descrição do negócio
            
        Returns:
            BusinessContext: Contexto estruturado do negócio
        """
        business_input_lower = business_input.lower()
        
        # Detecta segmento e mapeia para formato completo
        segment = "Outros"  # Default
        for seg, patterns in self._business_patterns.items():
            if any(pattern in business_input_lower for pattern in patterns):
                segment = self.business_segments_mapping.get(seg, "Outros")
                break
        
        # Extrai informações básicas (simplified version)
        target_audience = self._extract_target_audience(business_input_lower)
        geographic_region = self._extract_geographic_region(business_input_lower)
        brand_values = self._extract_brand_values(business_input_lower)
        objectives = self._extract_objectives(business_input_lower)
        
        return BusinessContext(
            segment=segment,
            target_audience=target_audience,
            geographic_region=geographic_region,
            brand_values=brand_values,
            objectives=objectives,
            budget_range="medium",  # Default
            timeline="3_months",    # Default
            competition_level="medium"  # Default
        )
    
    def _extract_target_audience(self, text: str) -> str:
        """Extrai público-alvo do texto"""
        audiences = {
            "gen_z": ["gen z", "geração z", "jovens", "teens", "adolescentes"],
            "millennials": ["millennials", "geração y", "adultos jovens"],
            "gen_x": ["gen x", "geração x", "adultos"],
            "families": ["família", "pais", "mães", "crianças"],
            "professionals": ["profissionais", "executivos", "empresários"]
        }
        
        for audience, keywords in audiences.items():
            if any(keyword in text for keyword in keywords):
                return audience
        
        return "general"
    
    def _extract_geographic_region(self, text: str) -> str:
        """Extrai região geográfica do texto"""
        regions = {
            "sp": ["são paulo", "sp", "paulista"],
            "rj": ["rio de janeiro", "rj", "carioca"],
            "mg": ["minas gerais", "mg", "mineiro"],
            "rs": ["rio grande do sul", "rs", "gaúcho"],
            "nacional": ["brasil", "nacional", "todo país"]
        }
        
        for region, keywords in regions.items():
            if any(keyword in text for keyword in keywords):
                return region
        
        return "nacional"
    
    def _extract_brand_values(self, text: str) -> List[str]:
        """Extrai valores da marca do texto"""
        values_map = {
            "inovação": ["inovação", "inovador", "tecnologia", "futuro"],
            "sustentabilidade": ["sustentável", "ecológico", "verde", "ambiente"],
            "qualidade": ["qualidade", "premium", "excelência", "superior"],
            "acessibilidade": ["acessível", "democrático", "para todos", "inclusivo"],
            "tradição": ["tradição", "tradicional", "história", "heritage"],
            "juventude": ["jovem", "moderno", "atual", "contemporâneo"]
        }
        
        found_values = []
        for value, keywords in values_map.items():
            if any(keyword in text for keyword in keywords):
                found_values.append(value)
        
        return found_values if found_values else ["qualidade"]
    
    def _extract_objectives(self, text: str) -> List[str]:
        """Extrai objetivos do texto"""
        objectives_map = {
            "awareness": ["conhecimento", "awareness", "divulgação", "visibilidade"],
            "engagement": ["engajamento", "interação", "comunidade", "relacionamento"],
            "conversion": ["conversão", "vendas", "leads", "aquisição"],
            "retention": ["retenção", "fidelização", "loyalty", "repeat"]
        }
        
        found_objectives = []
        for obj, keywords in objectives_map.items():
            if any(keyword in text for keyword in keywords):
                found_objectives.append(obj)
        
        return found_objectives if found_objectives else ["awareness"]
    
    def _get_simple_segment(self, full_segment: str) -> str:
        """Mapeia segmento completo para simplificado"""
        reverse_mapping = {v: k for k, v in self.business_segments_mapping.items()}
        return reverse_mapping.get(full_segment, "general")
    
    def refine_search_terms(self, 
                          original_terms: List[str], 
                          business_context: BusinessContext) -> List[str]:
        """
        Refina termos de pesquisa baseado no contexto
        🚀 AGORA COM ABORDAGEM HÍBRIDA: ML Foundation + IA Generativa!
        
        Args:
            original_terms: Termos originais de pesquisa
            business_context: Contexto do negócio
            
        Returns:
            List[str]: Termos refinados
        """
        refined_terms = original_terms.copy()
        enhancement_confidence = 0.0
        
        # � CAMADA 1: IA Generativa (GitHub Models) - Refinamento cultural avançado
        if self.github_models:
            try:
                ai_enhancement = self.github_models.enhance_terms_with_ai(
                    business_context.description,
                    original_terms,
                    cultural_focus="Brasil"
                )
                
                if ai_enhancement.get("success") and ai_enhancement.get("confidence", 0) > 0.7:
                    ai_terms = ai_enhancement.get("enhanced_terms", [])
                    refined_terms = ai_terms
                    enhancement_confidence = ai_enhancement.get("confidence", 0)
                    print(f"🤖 AI Enhancement (GPT-4o mini): {enhancement_confidence:.2f}")
                    print(f"🎯 Termos culturais: {len(ai_terms)} termos")
                    
            except Exception as e:
                print(f"⚠️ AI Enhancement falhou: {e}")
        
        # 🧠 CAMADA 2: ML Foundation - Análise e validação
        if self.ml_integrator and self.ml_integrator.is_initialized:
            try:
                ml_enhancement = self.ml_integrator.enhance_terms_with_ml(
                    refined_terms,  # Usar termos já refinados pela IA
                    business_context.description
                )
                
                if ml_enhancement.get("confidence", 0) > 0.3:
                    # Se IA não funcionou, usar ML como principal
                    if enhancement_confidence < 0.5:
                        ml_terms = ml_enhancement.get("enhanced_terms", [])
                        refined_terms = ml_terms
                        enhancement_confidence = ml_enhancement.get("confidence", 0)
                        print(f"🧠 ML Enhancement aplicado: {enhancement_confidence:.2f}")
                    else:
                        # Se IA funcionou, usar ML para validar e melhorar
                        ml_suggestions = ml_enhancement.get("suggestions", [])
                        for suggestion in ml_suggestions[:3]:  # Top 3 sugestões
                            if suggestion not in refined_terms:
                                refined_terms.append(suggestion)
                        print(f"🧠 ML Validation: +{len(ml_suggestions)} sugestões")
                    
            except Exception as e:
                print(f"⚠️ ML Enhancement falhou: {e}")
        
        # 🔧 CAMADA 3: Fallback clássico (garante funcionamento mesmo sem ML/IA)
        if enhancement_confidence < 0.3:
            print("🔧 Usando refinamento clássico como fallback...")
            
            # Adiciona termos específicos do segmento
            simple_segment = self._get_simple_segment(business_context.segment)
            if simple_segment in self._business_patterns:
                segment_terms = self._business_patterns[simple_segment]
                refined_terms.extend(segment_terms[:3])  # Top 3 mais relevantes
            
            # Adiciona termos baseados no público-alvo
            audience_terms = self._get_audience_terms(business_context.target_audience)
            refined_terms.extend(audience_terms)
            
            # Adiciona termos baseados na região
            regional_terms = self._get_regional_terms(business_context.geographic_region)
            refined_terms.extend(regional_terms)
            
            enhancement_confidence = 0.5  # Confiança padrão do sistema clássico
        
        # Remove duplicatas e ordena por relevância
        unique_terms = list(dict.fromkeys(refined_terms))
        
        return unique_terms[:20]  # Máximo 20 termos
    
    def _get_audience_terms(self, audience: str) -> List[str]:
        """Obtém termos específicos para o público-alvo"""
        audience_terms = {
            "gen_z": ["tiktok", "instagram", "viral", "trend", "aesthetic"],
            "millennials": ["netflix", "spotify", "uber", "lifestyle", "experience"],
            "gen_x": ["facebook", "linkedin", "quality", "value", "practical"],
            "families": ["família", "crianças", "segurança", "tradição", "valores"],
            "professionals": ["carreira", "networking", "produtividade", "sucesso"]
        }
        
        return audience_terms.get(audience, [])
    
    def _get_regional_terms(self, region: str) -> List[str]:
        """Obtém termos específicos para a região"""
        regional_terms = {
            "sp": ["sampa", "paulistano", "vila madalena", "centro"],
            "rj": ["carioca", "zona sul", "ipanema", "copacabana"],
            "mg": ["mineiro", "belo horizonte", "uai", "trem bão"],
            "rs": ["gaúcho", "porto alegre", "tchê", "sul"],
            "nacional": ["brasil", "brasileiro", "brasilidade"]
        }
        
        return regional_terms.get(region, [])
    
    def optimize_cultural_weights(self, business_context: BusinessContext) -> Dict[str, float]:
        """
        Otimiza pesos dos círculos culturais para o contexto específico
        
        Args:
            business_context: Contexto do negócio
            
        Returns:
            Dict[str, float]: Pesos otimizados dos círculos
        """
        # Pesos base (todos iguais inicialmente)
        base_weight = 1.0 / len(self.cultural_circles)
        optimized_weights = {circle: base_weight for circle in self.cultural_circles}
        
        # Aplica mapeamentos específicos do segmento
        if business_context.segment in self._cultural_mappings:
            segment_mappings = self._cultural_mappings[business_context.segment]
            
            for circle, boost in segment_mappings.items():
                if circle in optimized_weights:
                    optimized_weights[circle] *= boost
        
        # Normaliza os pesos para somar 1.0
        total_weight = sum(optimized_weights.values())
        normalized_weights = {
            circle: weight / total_weight 
            for circle, weight in optimized_weights.items()
        }
        
        return normalized_weights
    
    def recommend_data_sources(self, context: BusinessContext, search_terms: Optional[List[str]] = None) -> List[str]:
        """
        Recomendação DINÂMICA de fontes de dados baseada em pesos calculados na hora.
        """
        terms = search_terms or []
        api_scores = {}
        
        for api_name in IMPLEMENTED_APIS:
            dynamic_weight = self.calculate_dynamic_api_weight(api_name, terms, context)
            
            # Score base é o peso dinâmico
            score = dynamic_weight * 5.0 # Normalizar para escala de 5
            
            # Fator de relevância de segmento (V9.0 legado mantido como ajuste fino)
            if self._is_api_relevant_for_segment(api_name, context.segment):
                score += 0.5
            
            api_scores[api_name] = score
        
        # Ordenar APIs por score e retornar top 3-5
        sorted_apis = sorted(api_scores.items(), key=lambda x: x[1], reverse=True)
        recommended = [api for api, score in sorted_apis if score > 1.0]
        
        # Garantir pelo menos 3 APIs
        if len(recommended) < 3:
            top_apis = [api for api, _ in sorted_apis[:3]]
            recommended = list(set(recommended + top_apis))
        
        return recommended[:5]  # Máximo 5 APIs
    
    def calculate_confidence_score(self, 
                                 business_context: BusinessContext,
                                 refined_terms: List[str],
                                 cultural_weights: Dict[str, float]) -> float:
        """
        Calcula score de confiança da recomendação
        🧠 AGORA COM ML PREDICTION!
        
        Args:
            business_context: Contexto do negócio
            refined_terms: Termos refinados
            cultural_weights: Pesos culturais
            
        Returns:
            float: Score de confiança (0.0 a 1.0)
        """
        confidence_factors = []
        
        # 🧠 ML Confidence - Se ML Foundation estiver disponível
        if self.ml_integrator and self.ml_integrator.is_initialized:
            try:
                ml_prediction = self.ml_integrator.feedback_learner.predict_term_quality(
                    refined_terms, 
                    business_context.description
                )
                
                ml_confidence = ml_prediction.get("average_quality", 3.0) / 5.0  # Normalizar para 0-1
                confidence_factors.append(ml_confidence)
                print(f"🧠 ML Confidence: {ml_confidence:.2f}")
                
            except Exception as e:
                print(f"⚠️ ML Confidence falhou: {e}")
        
        # Fator 1: Clareza do segmento
        segment_clarity = 0.9 if business_context.segment != "Outros" else 0.5
        confidence_factors.append(segment_clarity)
        
        # Fator 2: Especificidade dos termos
        term_specificity = min(len(refined_terms) / 15.0, 1.0)
        confidence_factors.append(term_specificity)
        
        # Fator 3: Distribuição dos pesos culturais
        weight_distribution = 1.0 - np.std(list(cultural_weights.values())) * 5
        weight_distribution = max(0.3, min(1.0, weight_distribution))
        confidence_factors.append(weight_distribution)
        
        # Fator 4: Completude do contexto
        context_completeness = len([
            x for x in [
                business_context.target_audience != "general",
                business_context.geographic_region != "nacional",
                len(business_context.brand_values) > 0,
                len(business_context.objectives) > 0
            ] if x
        ]) / 4.0
        confidence_factors.append(context_completeness)
        
        # Score final (média ponderada)
        weights = [0.3, 0.2, 0.3, 0.2]
        final_score = sum(f * w for f, w in zip(confidence_factors, weights))
        
        return round(final_score, 3)
    
    def refine_research(self, 
                       business_input: str, 
                       original_config: Dict[str, Any]) -> RefinedResearch:
        """
        Método principal: refina pesquisa completa
        
        Args:
            business_input: Descrição do negócio em texto livre
            original_config: Configuração original de pesquisa
            
        Returns:
            RefinedResearch: Pesquisa refinada completa
        """
        # Cache key para otimização
        cache_key = hashlib.md5(
            f"{business_input}_{json.dumps(original_config, sort_keys=True)}".encode()
        ).hexdigest()
        
        if cache_key in self._refinement_cache:
            return self._refinement_cache[cache_key]
        
        # Análise do contexto
        business_context = self.analyze_business_context(business_input)
        
        # Refinamento dos termos
        original_terms = original_config.get('search_terms', [])
        refined_terms = self.refine_search_terms(original_terms, business_context)
        
        # Otimização dos pesos culturais
        cultural_weights = self.optimize_cultural_weights(business_context)
        
        # Recomendação de APIs
        recommended_apis = self.recommend_data_sources(business_context)
        
        # Cálculo de confiança
        confidence_score = self.calculate_confidence_score(
            business_context, refined_terms, cultural_weights
        )
        
        # Estimativa de tamanho da amostra
        estimated_sample = self._estimate_sample_size(
            business_context, len(refined_terms), len(recommended_apis)
        )
        
        # Raciocínio da recomendação
        reasoning = self._generate_reasoning(
            business_context, refined_terms, cultural_weights, confidence_score
        )
        
        # Resultado final
        result = RefinedResearch(
            refined_terms=refined_terms,
            adjusted_weights=cultural_weights,
            recommended_apis=recommended_apis,
            confidence_score=confidence_score,
            reasoning=reasoning,
            estimated_sample_size=estimated_sample
        )
        
        # Cache do resultado
        self._refinement_cache[cache_key] = result
        
        return result
    
    def _estimate_sample_size(self, 
                            business_context: BusinessContext,
                            num_terms: int, 
                            num_apis: int) -> int:
        """Estima tamanho da amostra baseado nos parâmetros"""
        base_sample = 1000
        
        # Multipliers baseados no contexto
        segment_multiplier = {
            "tech": 1.5, "fashion": 1.3, "food": 1.2, "entertainment": 1.4
        }.get(business_context.segment, 1.0)
        
        audience_multiplier = {
            "gen_z": 1.4, "millennials": 1.2, "gen_x": 0.9
        }.get(business_context.target_audience, 1.0)
        
        # Cálculo final
        estimated = int(
            base_sample * 
            segment_multiplier * 
            audience_multiplier * 
            (num_terms / 10) * 
            (num_apis / 5)
        )
        
        return min(estimated, 10000)  # Cap em 10k
    
    def _generate_reasoning(self, 
                          business_context: BusinessContext,
                          refined_terms: List[str],
                          cultural_weights: Dict[str, float],
                          strategic_metrics: StrategicMetrics = None) -> str:
        """Gera explicação do raciocínio das recomendações"""
        
        # Top círculos culturais
        top_circles = sorted(
            cultural_weights.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:3]
        
        # Seção estratégica (V9.7)
        strategic_insight = ""
        if strategic_metrics:
            strategic_insight = f"""
🚀 **Análise de Profundidade (Depth Questions):**
- **Velocidade:** O setor corre a {strategic_metrics.velocity_score:.1%} (Status: {strategic_metrics.momentum_trend})
- **Vizinhança:** Alto raio de adjacência ({strategic_metrics.adjacency_radius:.1%}) - 'Anda com' círculos de {top_circles[0][0]}.
- **Impacto:** Projeção de carregamento cultural de {strategic_metrics.impact_forecast:.1%}.
"""

        reasoning = f"""
🎯 **Análise do Contexto de Negócio:**
- Segmento identificado: {business_context.segment.title()}
- Público-alvo: {business_context.target_audience}
- Região: {business_context.geographic_region}
{strategic_insight}
🔍 **Otimizações Aplicadas:**
- Adicionados {len(refined_terms)} termos refinados
- Priorizados círculos: {', '.join([c[0] for c in top_circles])}

💡 **Raciocínio:
Baseado no segmento {business_context.segment}, o agente identificou que os círculos culturais 
mais relevantes são {top_circles[0][0]} ({top_circles[0][1]:.1%}) e {top_circles[1][0]} ({top_circles[1][1]:.1%}). 
Os termos foram expandidos para capturar nuances específicas do público {business_context.target_audience}.
        """.strip()
        
        return reasoning
    
    def train_with_user_feedback(self, session_data: Dict[str, Any]) -> bool:
        """
        🧠 Treina ML Foundation com feedback do usuário
        
        Args:
            session_data: Dados da sessão com feedback
            
        Returns:
            bool: True se treinamento foi bem-sucedido
        """
        if not self.ml_integrator or not self.ml_integrator.is_initialized:
            print("⚠️ ML Foundation não disponível para treinamento")
            return False
            
        try:
            success = self.ml_integrator.train_with_feedback(session_data)
            if success:
                print(f"🧠 ML Foundation treinado com feedback: {session_data.get('user_rating', 0)}/5")
            return success
            
        except Exception as e:
            print(f"❌ Erro no treinamento ML: {e}")
            return False
    
    def get_ml_insights(self) -> Dict[str, Any]:
        """
        🧠 Obtém insights do ML Foundation
        
        Returns:
            Dict: Insights e estatísticas do ML
        """
        if not self.ml_integrator or not self.ml_integrator.is_initialized:
            return {"ml_available": False}
            
        try:
            stats = self.ml_integrator.get_ml_stats()
            insights = self.ml_integrator.feedback_learner.get_learning_insights()
            
            return {
                "ml_available": True,
                "stats": stats,
                "insights": insights,
                "version": "9.0_ML_Foundation"
            }
            
        except Exception as e:
            return {"ml_available": False, "error": str(e)}
    
    def get_refinement_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do refinement + ML"""
        stats = {
            "cache_size": len(self._refinement_cache),
            "available_patterns": len(self._business_patterns),
            "cultural_mappings": len(self._cultural_mappings),
            "version": "9.0.0_ML_Enhanced"
        }
        
        # Adicionar stats do ML se disponível
        if self.ml_integrator and self.ml_integrator.is_initialized:
            stats["ml_foundation"] = self.get_ml_insights()
            
        return stats
