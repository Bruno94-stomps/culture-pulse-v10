"""
🧬 Automated Insights Generation V8.2
==========================================

Sistema de geração automática de insights para Culture Pulse V8.2

Características:
- Insights em tempo real
- Templates inteligentes
- Análise contextual
- Scoring automático
- Recommendations engine
- Pattern recognition
- Trend forecasting
- Business intelligence

Autor: Culture Pulse Team
Data: Setembro 2025
Versão: 8.2.0
"""

import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import statistics
import numpy as np
from collections import defaultdict, Counter

# Importação do BusinessSynthesizer para Filtro de Obviedade (V9.9)
try:
    from core.intelligence.business_synthesizer import get_business_synthesizer
except ImportError:
    try:
        from src_v8.core.business_synthesizer import get_business_synthesizer
    except ImportError:
        get_business_synthesizer = None

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InsightType(Enum):
    """Tipos de insights"""
    TREND = "trend"
    ANOMALY = "anomaly"
    OPPORTUNITY = "opportunity"
    RISK = "risk"
    FORECAST = "forecast"
    COMPARISON = "comparison"
    RECOMMENDATION = "recommendation"

class InsightPriority(Enum):
    """Prioridade do insight"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class BusinessContext(Enum):
    """Contexto de negócio"""
    MARKETING = "marketing"
    PRODUCT = "product"
    STRATEGY = "strategy"
    OPERATIONS = "operations"
    INNOVATION = "innovation"

@dataclass
class Insight:
    """Insight gerado automaticamente"""
    id: str
    type: InsightType
    priority: InsightPriority
    title: str
    description: str
    data_points: List[Any]
    confidence: float
    business_context: List[BusinessContext]
    actionable_items: List[str]
    metadata: Dict[str, Any]
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['type'] = self.type.value
        data['priority'] = self.priority.value
        data['business_context'] = [bc.value for bc in self.business_context]
        data['created_at'] = self.created_at.isoformat()
        if self.expires_at:
            data['expires_at'] = self.expires_at.isoformat()
        return data

class InsightTemplate:
    """Template para geração de insights"""
    
    def __init__(self, insight_type: InsightType, priority: InsightPriority):
        self.insight_type = insight_type
        self.priority = priority
        self.templates = self._load_templates()
        
    def _load_templates(self) -> Dict[str, List[str]]:
        """Carregar templates de insights"""
        return {
            'trend_rising': [
                "📈 {category} está em forte crescimento com {growth:.0%} de aumento nos últimos {period}",
                "🚀 Tendência emergente detectada: {category} cresceu {growth:.0%} em {period}",
                "⭐ {category} ganhando momentum significativo (+{growth:.0%} em {period})",
                "🔥 Explosão cultural em {category}: crescimento de {growth:.0%}"
            ],
            'trend_falling': [
                "📉 Declínio detectado em {category}: queda de {decline:.0%} em {period}",
                "⚠️ {category} perdendo relevância (-{decline:.0%} em {period})",
                "🔻 Tendência descendente: {category} em declínio de {decline:.0%}",
                "📊 Redução significativa em {category} nos últimos {period}"
            ],
            'opportunity_high': [
                "💎 Oportunidade de alto valor identificada em {category}",
                "🎯 Janela de oportunidade aberta: {category} com potencial de {potential:.0%}",
                "✨ Momento ideal para investir em {category}",
                "🚀 {category} apresenta oportunidade estratégica única"
            ],
            'risk_detection': [
                "⚠️ Risco detectado: {category} pode impactar {impact_area}",
                "🚨 Atenção necessária em {category} - risco de {risk_type}",
                "⚡ Monitoramento crítico: {category} apresenta sinais de alerta",
                "🔍 Investigação recomendada em {category}"
            ],
            'anomaly_positive': [
                "🌟 Anomalia positiva: {category} superou expectativas em {metric:.0%}",
                "⚡ Performance excepcional detectada em {category}",
                "🎪 Evento cultural singular: {category} com impacto extraordinário",
                "🏆 {category} alcançou marcos históricos"
            ],
            'forecast_prediction': [
                "🔮 Previsão: {category} deve crescer {forecast:.0%} nos próximos {timeframe}",
                "📊 Projeção indica {trend_direction} de {forecast:.0%} para {category}",
                "🎯 Cenário futuro: {category} com potencial de {forecast:.0%}",
                "📈 Modelo prevê {trend_direction} significativo em {category}"
            ],
            'recommendation_action': [
                "💡 Recomendação: {action} para aproveitar tendência em {category}",
                "🎯 Ação sugerida: {action} pode gerar ROI de {roi:.0%}",
                "⚡ Quick win identificado: {action} em {category}",
                "🚀 Estratégia recomendada: {action} para maximizar {benefit}"
            ]
        }
        
    def generate(self, template_key: str, **kwargs) -> str:
        """Gerar insight usando template"""
        if template_key not in self.templates:
            return f"Insight sobre {kwargs.get('category', 'área analisada')}"
            
        template = np.random.choice(self.templates[template_key])
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.warning(f"Template key missing: {e}")
            return template
            
class TrendAnalyzer:
    """Analisador de tendências para insights"""
    
    def __init__(self):
        self.trend_threshold = 0.15  # 15% mudança para considerar tendência
        self.anomaly_threshold = 2.0  # 2 desvios padrão para anomalia
        
    def analyze_trends(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analisar tendências nos dados"""
        trends = []
        
        # Agrupar por categoria
        categories = defaultdict(list)
        for item in data:
            category = item.get('category', 'geral')
            timestamp = item.get('timestamp', datetime.now())
            score = item.get('score', 0.5)
            
            categories[category].append({
                'timestamp': timestamp,
                'score': score,
                'data': item
            })
            
        # Analisar cada categoria
        for category, items in categories.items():
            if len(items) < 3:  # Mínimo para análise
                continue
                
            # Ordenar por timestamp
            items.sort(key=lambda x: x['timestamp'])
            
            # Calcular tendência
            scores = [item['score'] for item in items]
            x = np.arange(len(scores))
            
            if len(scores) > 1:
                slope = np.polyfit(x, scores, 1)[0]
                change_rate = slope * len(scores)  # Projeção total
                
                # Determinar direção e força
                if abs(change_rate) > self.trend_threshold:
                    trends.append({
                        'category': category,
                        'direction': 'rising' if change_rate > 0 else 'falling',
                        'strength': abs(change_rate),
                        'confidence': min(1.0, abs(change_rate) / self.trend_threshold),
                        'sample_size': len(items),
                        'current_score': scores[-1],
                        'change_rate': change_rate,
                        'timespan': (items[-1]['timestamp'] - items[0]['timestamp']).days
                    })
                    
        return trends
        
    def detect_anomalies(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detectar anomalias nos dados"""
        anomalies = []
        
        # Analisar por categoria
        categories = defaultdict(list)
        for item in data:
            category = item.get('category', 'geral')
            score = item.get('score', 0.5)
            categories[category].append((score, item))
            
        for category, items in categories.items():
            if len(items) < 5:  # Mínimo para detecção de anomalias
                continue
                
            scores = [item[0] for item in items]
            mean_score = statistics.mean(scores)
            std_score = statistics.stdev(scores)
            
            if std_score == 0:  # Evitar divisão por zero
                continue
                
            for score, item in items:
                z_score = abs(score - mean_score) / std_score
                
                if z_score > self.anomaly_threshold:
                    anomalies.append({
                        'category': category,
                        'score': score,
                        'expected_range': (mean_score - std_score, mean_score + std_score),
                        'deviation': z_score,
                        'type': 'positive' if score > mean_score else 'negative',
                        'data': item,
                        'significance': min(1.0, z_score / self.anomaly_threshold)
                    })
                    
        return anomalies

class OpportunityDetector:
    """Detector de oportunidades de negócio"""
    
    def __init__(self):
        self.opportunity_indicators = {
            'high_engagement_low_competition': 0.8,
            'emerging_trend_early_stage': 0.9,
            'positive_sentiment_growing': 0.7,
            'cross_category_correlation': 0.6,
            'seasonal_opportunity': 0.5
        }
        
    def detect_opportunities(self, data: List[Dict[str, Any]], trends: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detectar oportunidades nos dados"""
        opportunities = []
        
        # Analisar tendências emergentes
        for trend in trends:
            if trend['direction'] == 'rising' and trend['confidence'] > 0.7:
                opportunity_score = trend['strength'] * trend['confidence']
                
                if opportunity_score > 0.5:
                    opportunities.append({
                        'type': 'emerging_trend',
                        'category': trend['category'],
                        'score': opportunity_score,
                        'potential': opportunity_score * 100,  # Potencial em %
                        'timeframe': self._estimate_timeframe(trend),
                        'risk_level': self._assess_risk(trend),
                        'investment_recommendation': self._recommend_investment(opportunity_score)
                    })
                    
        # Detectar gaps de mercado
        category_coverage = defaultdict(int)
        for item in data:
            category = item.get('category', 'geral')
            category_coverage[category] += 1
            
        # Identificar categorias sub-representadas
        avg_coverage = statistics.mean(category_coverage.values()) if category_coverage else 0
        
        for category, count in category_coverage.items():
            if count < avg_coverage * 0.5 and count > 0:  # Sub-representada mas existente
                opportunities.append({
                    'type': 'market_gap',
                    'category': category,
                    'score': 0.6,
                    'potential': 75,
                    'gap_size': avg_coverage - count,
                    'competition_level': 'low',
                    'entry_barrier': 'medium'
                })
                
        return opportunities
        
    def _estimate_timeframe(self, trend: Dict[str, Any]) -> str:
        """Estimar timeframe da oportunidade"""
        strength = trend['strength']
        
        if strength > 0.5:
            return "imediato (1-2 meses)"
        elif strength > 0.3:
            return "curto prazo (3-6 meses)"
        else:
            return "médio prazo (6-12 meses)"
            
    def _assess_risk(self, trend: Dict[str, Any]) -> str:
        """Avaliar nível de risco"""
        confidence = trend['confidence']
        sample_size = trend.get('sample_size', 0)
        
        if confidence > 0.8 and sample_size > 10:
            return "baixo"
        elif confidence > 0.6 and sample_size > 5:
            return "médio"
        else:
            return "alto"
            
    def _recommend_investment(self, score: float) -> str:
        """Recomendar nível de investimento"""
        if score > 0.8:
            return "alto investimento recomendado"
        elif score > 0.6:
            return "investimento moderado"
        else:
            return "investimento cauteloso"

class AutomatedInsightsGenerator:
    """Gerador principal de insights automáticos com integração ML Foundation V9.0"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.trend_analyzer = TrendAnalyzer()
        self.opportunity_detector = OpportunityDetector()
        
        # 1. Integração com ML Foundation (Fundação de Inteligência)
        try:
            from autonomous_agent.ml_foundation.ml_integrator_simple import MLIntegratorSimple
            self.ml_foundation = MLIntegratorSimple()
            logger.info("🧠 ML Foundation Integrada ao Motor de Insights")
        except Exception as e:
            self.ml_foundation = None
            logger.warning(f"⚠️ Falha ao integrar ML Foundation: {e}")

        self.templates = {
            InsightType.TREND: InsightTemplate(InsightType.TREND, InsightPriority.HIGH),
            InsightType.OPPORTUNITY: InsightTemplate(InsightType.OPPORTUNITY, InsightPriority.HIGH),
            InsightType.ANOMALY: InsightTemplate(InsightType.ANOMALY, InsightPriority.MEDIUM),
            InsightType.FORECAST: InsightTemplate(InsightType.FORECAST, InsightPriority.MEDIUM),
            InsightType.RECOMMENDATION: InsightTemplate(InsightType.RECOMMENDATION, InsightPriority.HIGH)
        }
        
        self.generated_insights = []
        self.max_insights_history = 1000
        
        logger.info("🧬 Automated Insights Generator V8.2 inicializado")
        
    def generate_insights(self, data: List[Dict[str, Any]], context: str = "cultural_analysis") -> List[Insight]:
        """Gerar insights dinâmicos usando ML Foundation e Onboarding"""
        from core.intelligence.learning.InsightLearner import get_insight_learner
        insight_learner = get_insight_learner()
        
        # 1. Integração com BusinessSynthesizer (Filtro de Obviedade V9.9)
        synthesizer = None
        if get_business_synthesizer:
            synthesizer = get_business_synthesizer()

        # 1. Enriquecimento de NLP via ML Foundation (Advanced Analytics)
        enriched_data = []
        if self.ml_foundation:
            # Tenta converter para um dataset enriquecido antes de filtrar
            for item in data:
                # Extrai sentimentos e entidades se o processor estiver disponível
                if hasattr(self.ml_foundation, 'nlp_processor') and self.ml_foundation.nlp_processor:
                    nlp_info = self.ml_foundation.nlp_processor.process_text(item.get('text', ''))
                    item['sentiment'] = nlp_info.get('sentiment', 'neutral')
                    item['entities'] = nlp_info.get('entities', [])

        # 2. Filtragem de Onboarding (InsightLearner) e Obviedade (Synthesizer)
        filtered_data = []
        for item in data:
            # Check 1: Onboarding Context
            quality = insight_learner.predict_signal_quality(item)
            if quality.get("status") == "blocked_by_onboarding":
                continue

            # Check 2: Entropy/Obviousness Filter (V9.9)
            if synthesizer:
                analysis = synthesizer.synthesize_signal(item.get('text', ''), item.get('category', 'cultural'))
                if not analysis.get("is_non_obvious", True):
                    logger.info(f"⏭️ Sinal ignorado por ser óbvio/clichê: {item.get('text', '')[:50]}...")
                    continue
                # Injete o score de entropia no sinal para priorização posterior
                item['entropy_score'] = analysis.get("entropy_score", 0.5)

            # Boost de Relevância via Embeddings Culturais (ML Foundation)
            if self.ml_foundation and hasattr(self.ml_foundation, 'cultural_embeddings'):
                # Compara o sinal com os círculos da marca configurada
                fit_score = self.ml_foundation.cultural_embeddings.calculate_fit(item.get('text', ''))
                item['score'] = (item.get('score', 0.5) + fit_score) / 2
            filtered_data.append(item)
        
        if not filtered_data:
            logger.warning("⚠️ Todos os sinais foram filtrados por serem óbvios ou fora do contexto de Onboarding.")
            # Retorna um insight informativo em vez de lista vazia para não quebrar a UI
            return [Insight(
                type=InsightType.RECOMMENDATION,
                content="Nenhum insight de alta entropia detectado nos sinais atuais. O sistema filtrou clichês culturais para focar em sinais emergentes.",
                confidence=1.0,
                priority=InsightPriority.LOW,
                category="sistema",
                metadata={"status": "all_filtered_as_obvious"}
            )]

        insights = []
        
        try:
            # 3. Análise de tendências sobre dados filtrados e enriquecidos
            trends = self.trend_analyzer.analyze_trends(filtered_data)
            insights.extend(self._generate_trend_insights(trends, filtered_data))
            
            # 2. Detecção de anomalias
            anomalies = self.trend_analyzer.detect_anomalies(data)
            insights.extend(self._generate_anomaly_insights(anomalies))
            
            # 3. Detecção de oportunidades
            opportunities = self.opportunity_detector.detect_opportunities(data, trends)
            insights.extend(self._generate_opportunity_insights(opportunities))
            
            # 4. Previsões
            forecasts = self._generate_forecasts(trends, data)
            insights.extend(forecasts)
            
            # 5. Recomendações
            recommendations = self._generate_recommendations(trends, opportunities, data)
            insights.extend(recommendations)
            
            # Ordenar por prioridade e confidence
            insights.sort(key=lambda x: (x.priority.value, -x.confidence), reverse=True)
            
            # Armazenar histórico
            self.generated_insights.extend(insights)
            if len(self.generated_insights) > self.max_insights_history:
                self.generated_insights = self.generated_insights[-self.max_insights_history:]
                
            logger.info(f"🧬 Gerados {len(insights)} insights automáticos")
            
        except Exception as e:
            logger.error(f"❌ Erro na geração de insights: {e}")
            
        return insights[:10]  # Top 10 insights
        
    def _generate_trend_insights(self, trends: List[Dict[str, Any]], data: List[Dict[str, Any]]) -> List[Insight]:
        """Gerar insights de tendências"""
        insights = []
        
        for trend in trends:
            if trend['confidence'] < 0.5:
                continue
                
            template_key = f"trend_{trend['direction']}"
            template = self.templates[InsightType.TREND]
            
            # Determinar período
            period = f"{trend.get('timespan', 7)} dias"
            
            title = template.generate(
                template_key,
                category=trend['category'],
                growth=abs(trend['change_rate']),
                decline=abs(trend['change_rate']),
                period=period
            )
            
            # Gerar ações recomendadas
            actionable_items = self._generate_trend_actions(trend)
            
            # Determinar contexto de negócio
            business_context = self._determine_business_context(trend['category'])
            
            insight = Insight(
                id=f"trend_{uuid.uuid4().hex[:8]}",
                type=InsightType.TREND,
                priority=InsightPriority.HIGH if trend['confidence'] > 0.8 else InsightPriority.MEDIUM,
                title=title,
                description=f"Tendência {trend['direction']} detectada em {trend['category']} com {trend['confidence']:.0%} de confiança",
                data_points=[trend],
                confidence=trend['confidence'],
                business_context=business_context,
                actionable_items=actionable_items,
                metadata={
                    'trend_direction': trend['direction'],
                    'change_rate': trend['change_rate'],
                    'sample_size': trend['sample_size']
                },
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=7)
            )
            
            insights.append(insight)
            
        return insights
        
    def _generate_anomaly_insights(self, anomalies: List[Dict[str, Any]]) -> List[Insight]:
        """Gerar insights de anomalias"""
        insights = []
        
        for anomaly in anomalies:
            if anomaly['significance'] < 0.5:
                continue
                
            template = self.templates[InsightType.ANOMALY]
            template_key = f"anomaly_{anomaly['type']}"
            
            title = template.generate(
                template_key,
                category=anomaly['category'],
                metric=anomaly['deviation'] * 100
            )
            
            priority = (
                InsightPriority.CRITICAL if anomaly['significance'] > 0.9
                else InsightPriority.HIGH if anomaly['significance'] > 0.7
                else InsightPriority.MEDIUM
            )
            
            insight = Insight(
                id=f"anomaly_{uuid.uuid4().hex[:8]}",
                type=InsightType.ANOMALY,
                priority=priority,
                title=title,
                description=f"Anomalia {anomaly['type']} detectada em {anomaly['category']}",
                data_points=[anomaly],
                confidence=min(1.0, anomaly['significance']),
                business_context=[BusinessContext.OPERATIONS, BusinessContext.STRATEGY],
                actionable_items=[
                    f"Investigar causa da anomalia em {anomaly['category']}",
                    f"Verificar dados de {anomaly['category']} para validação",
                    f"Monitorar evolução da anomalia"
                ],
                metadata={
                    'deviation': anomaly['deviation'],
                    'anomaly_type': anomaly['type']
                },
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=3)
            )
            
            insights.append(insight)
            
        return insights
        
    def _generate_opportunity_insights(self, opportunities: List[Dict[str, Any]]) -> List[Insight]:
        """Gerar insights de oportunidades"""
        insights = []
        
        for opp in opportunities:
            template = self.templates[InsightType.OPPORTUNITY]
            
            title = template.generate(
                'opportunity_high',
                category=opp['category'],
                potential=opp['potential']
            )
            
            actionable_items = [
                f"Desenvolver estratégia para {opp['category']}",
                f"Alocar recursos para aproveitar oportunidade",
                f"Monitorar competição em {opp['category']}",
                f"Definir KPIs para {opp['category']}"
            ]
            
            insight = Insight(
                id=f"opportunity_{uuid.uuid4().hex[:8]}",
                type=InsightType.OPPORTUNITY,
                priority=InsightPriority.HIGH,
                title=title,
                description=f"Oportunidade de {opp['type']} identificada em {opp['category']}",
                data_points=[opp],
                confidence=opp['score'],
                business_context=[BusinessContext.STRATEGY, BusinessContext.MARKETING],
                actionable_items=actionable_items,
                metadata={
                    'opportunity_type': opp['type'],
                    'potential': opp['potential'],
                    'timeframe': opp.get('timeframe', 'não especificado')
                },
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=14)
            )
            
            insights.append(insight)
            
        return insights
        
    def _generate_forecasts(self, trends: List[Dict[str, Any]], data: List[Dict[str, Any]]) -> List[Insight]:
        """Gerar insights de previsão"""
        insights = []
        
        for trend in trends:
            if trend['confidence'] < 0.6:
                continue
                
            # Prever próximos 30 dias
            current_score = trend['current_score']
            change_rate = trend['change_rate']
            forecast_value = current_score + (change_rate * 4) # 4 semanas
            
            template = self.templates[InsightType.FORECAST]
            
            title = template.generate(
                'forecast_prediction',
                category=trend['category'],
                forecast=abs(forecast_value - current_score) * 100,
                timeframe="30 dias",
                trend_direction=trend['direction']
            )
            
            insight = Insight(
                id=f"forecast_{uuid.uuid4().hex[:8]}",
                type=InsightType.FORECAST,
                priority=InsightPriority.MEDIUM,
                title=title,
                description=f"Previsão para {trend['category']} nos próximos 30 dias",
                data_points=[trend],
                confidence=trend['confidence'] * 0.8,  # Reduzir confidence para previsões
                business_context=[BusinessContext.STRATEGY, BusinessContext.PRODUCT],
                actionable_items=[
                    f"Preparar recursos para mudança em {trend['category']}",
                    f"Ajustar estratégia baseada na previsão",
                    f"Monitorar evolução real vs prevista"
                ],
                metadata={
                    'forecast_horizon': 30,
                    'predicted_change': forecast_value - current_score,
                    'based_on_trend': trend['direction']
                },
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=30)
            )
            
            insights.append(insight)
            
        return insights
        
    def _generate_recommendations(self, trends: List[Dict[str, Any]], opportunities: List[Dict[str, Any]], data: List[Dict[str, Any]]) -> List[Insight]:
        """Gerar recomendações"""
        insights = []
        
        # Recomendações baseadas em tendências
        for trend in trends[:3]:  # Top 3 trends
            if trend['direction'] == 'rising' and trend['confidence'] > 0.7:
                
                template = self.templates[InsightType.RECOMMENDATION]
                
                action = self._suggest_action(trend['category'], trend)
                roi = trend['strength'] * 150  # Estimativa de ROI
                
                title = template.generate(
                    'recommendation_action',
                    action=action,
                    category=trend['category'],
                    roi=roi,
                    benefit="engagement e alcance"
                )
                
                insight = Insight(
                    id=f"recommendation_{uuid.uuid4().hex[:8]}",
                    type=InsightType.RECOMMENDATION,
                    priority=InsightPriority.HIGH,
                    title=title,
                    description=f"Recomendação estratégica para {trend['category']}",
                    data_points=[trend],
                    confidence=trend['confidence'],
                    business_context=[BusinessContext.MARKETING, BusinessContext.STRATEGY],
                    actionable_items=[
                        action,
                        f"Definir orçamento para {trend['category']}",
                        f"Estabelecer timeline de implementação",
                        f"Configurar métricas de acompanhamento"
                    ],
                    metadata={
                        'recommended_action': action,
                        'estimated_roi': roi,
                        'priority_level': 'alta'
                    },
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(days=21)
                )
                
                insights.append(insight)
                
        return insights
        
    def _generate_trend_actions(self, trend: Dict[str, Any]) -> List[str]:
        """Gerar ações para tendências"""
        category = trend['category']
        direction = trend['direction']
        
        if direction == 'rising':
            return [
                f"Aumentar investimento em {category}",
                f"Acelerar produção de conteúdo para {category}",
                f"Expandir parcerias em {category}",
                f"Desenvolver campanhas focadas em {category}"
            ]
        else:
            return [
                f"Reavaliar estratégia para {category}",
                f"Diversificar portfólio além de {category}",
                f"Reduzir exposição a {category}",
                f"Buscar inovação em {category}"
            ]
            
    def _determine_business_context(self, category: str) -> List[BusinessContext]:
        """
        Determinar contexto de negócio dinamicamente via StrategyLearner (Onboarding).
        Usa o Intent (Research/Campaign) para priorizar o contexto.
        """
        from core.intelligence.learning.StrategyLearner import get_strategy_learner
        strategy = get_strategy_learner()
        
        # Tenta encontrar correspondência com o contexto da marca atual
        for ctx_id, ctx in strategy.brand_contexts.items():
            if ctx.industry.lower() in category.lower() or category.lower() in ctx.industry.lower():
                # Se o intent for Campaign, prioriza Marketing
                if ctx.intent == 'campaign':
                    return [BusinessContext.MARKETING, BusinessContext.STRATEGY]
                return [BusinessContext.STRATEGY, BusinessContext.RESEARCH if hasattr(BusinessContext, 'RESEARCH') else BusinessContext.INNOVATION]
        
        return [BusinessContext.STRATEGY]
        
    def _suggest_action(self, category: str, trend: Dict[str, Any]) -> str:
        """
        Sugerir ação baseada no BusinessSynthesizer, regras de Onboarding e Intent.
        """
        from core.intelligence.business_synthesizer import get_business_synthesizer
        from core.intelligence.learning.StrategyLearner import get_strategy_learner
        
        synthesizer = get_business_synthesizer()
        strategy = get_strategy_learner()
        
        # Pega o primeiro intent disponível
        intent = "research"
        if strategy.brand_contexts:
            intent = list(strategy.brand_contexts.values())[0].intent

        # Busca padrões de síntese reais
        patterns = synthesizer.synthesis_patterns
        for p_key, p_val in patterns.items():
            if any(c.lower() in category.lower() for c in p_val.get('primary_circles', [])):
                action = p_val.get('approach', f"Desenvolver estratégia focada em {category}")
                # Ajusta o tom da ação baseado no Intent
                if intent == 'campaign':
                    return f"EXECUTAR: {action} (Foco em Campanha/Ativação)"
                return f"ESTUDAR: {action} (Foco em Research/Deep Context)"
        
        if intent == 'campaign':
            return f"Criar ativação rápida em torno de '{category}' para capturar momentum."
        return f"Aprofundar análise de momentum em {category} para validar fit cultural."
        
    def get_insights_by_priority(self, priority: InsightPriority) -> List[Insight]:
        """Obter insights por prioridade"""
        return [insight for insight in self.generated_insights if insight.priority == priority]
        
    def get_insights_by_type(self, insight_type: InsightType) -> List[Insight]:
        """Obter insights por tipo"""
        return [insight for insight in self.generated_insights if insight.type == insight_type]
        
    def get_active_insights(self) -> List[Insight]:
        """Obter insights ainda válidos"""
        now = datetime.now()
        return [
            insight for insight in self.generated_insights
            if insight.expires_at is None or insight.expires_at > now
        ]

# Singleton
_insights_generator = None

def get_insights_generator(config: Dict[str, Any] = None) -> AutomatedInsightsGenerator:
    """Obter instância singleton do gerador de insights"""
    global _insights_generator
    
    if _insights_generator is None:
        _insights_generator = AutomatedInsightsGenerator(config)
        
    return _insights_generator

if __name__ == "__main__":
    import asyncio
    from collectors.orchestrator import OrchestratorV9
    from core.intelligence.learning.InsightLearner import get_insight_learner
    from core.intelligence.learning.StrategyLearner import get_strategy_learner

    async def run_real_demo():
        print("🧬 Demo Real-Time: Automated Insights Generation V8.2")
        print("=" * 60)
        
        # 1. Inicializar componentes reais
        generator = get_insights_generator()
        orchestrator = OrchestratorV9()
        insight_learner = get_insight_learner()
        strategy = get_strategy_learner()
        
        # 2. Obter contexto do Onboarding (Supabase)
        print("🔍 Carregando contextos de marca do Onboarding...")
        brand_contexts = strategy.brand_contexts
        
        if not brand_contexts:
            print("⚠️ Nenhum perfil de marca encontrado no Supabase. Usando 'cultura' como padrão.")
            topics = ["cultura geral"]
        else:
            # Pega os tópicos principais do primeiro perfil ativo
            first_profile = list(brand_contexts.values())[0]
            topics = [first_profile.brand_name] + first_profile.core_values[:2]
            print(f"✅ Perfil detectado: {first_profile.brand_name} (Indústria: {first_profile.industry})")

        # 3. Coleta Real via APIs (YouTube, Reddit, News)
        print(f"📡 Coletando dados reais para: {topics}...")
        collection = await orchestrator.collect_with_monitoring(topics=topics)
        
        raw_data = collection.get('data', [])
        print(f"📊 {len(raw_data)} sinais brutos coletados.")

        # 4. Filtragem via InsightLearner (Wilson Bound + Onboarding Rules)
        filtered_data = []
        for item in raw_data:
            quality = insight_learner.predict_signal_quality(item)
            if quality.get("status") != "blocked_by_onboarding":
                # Adiciona score de relevância calculado pelo Wilson Bound se disponível
                item['score'] = quality.get("relevance_score", 0.5)
                filtered_data.append(item)
        
        print(f"⚖️ {len(filtered_data)} sinais aprovados após filtros de qualidade/onboarding.")

        # 5. Geração de Insights Dinâmicos
        if filtered_data:
            insights = generator.generate_insights(filtered_data)
            
            print(f"\n� {len(insights)} Insights Estratégicos Gerados:")
            print("-" * 40)
            
            for insight in insights:
                emoji = "📈" if insight.type == InsightType.TREND else "💎" if insight.type == InsightType.OPPORTUNITY else "🔍"
                print(f"{emoji} {insight.type.value.upper()}: {insight.title}")
                print(f"   Prioridade: {insight.priority.value}")
                print(f"   Confiança: {insight.confidence:.0%}")
                print(f"   Contexto: {[c.value for c in insight.business_context]}")
                if insight.actionable_items:
                    print(f"   💡 Ação: {insight.actionable_items[0]}")
                print()
        else:
            print("❌ Dados insuficientes para gerar insights reais nesta rodada.")

    # Executar loop assíncrono
    asyncio.run(run_real_demo())
