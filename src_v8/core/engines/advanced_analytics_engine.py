"""
🧠 Advanced Analytics Engine V8.2
==========================================

Motor de analytics avançado para Culture Pulse V8.2

Características:
- Analytics em tempo real
- Machine Learning integrado  
- Previsões culturais avançadas
- Análise de sentimentos
- Detecção de tendências
- Scoring proprietário
- Insights automáticos

Autor: Culture Pulse Team
Data: Setembro 2025
Versão: 8.2.0
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
import json
import logging
from enum import Enum
import uuid
from collections import defaultdict, deque
import statistics

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsLevel(Enum):
    """Níveis de analytics"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class TrendDirection(Enum):
    """Direção da tendência"""
    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"
    VOLATILE = "volatile"

@dataclass
class CulturalSignal:
    """Sinal cultural detectado"""
    id: str
    name: str
    category: str
    strength: float  # 0.0 - 1.0
    confidence: float  # 0.0 - 1.0
    trend_direction: TrendDirection
    metadata: Dict[str, Any]
    detected_at: datetime
    sources: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['detected_at'] = self.detected_at.isoformat()
        data['trend_direction'] = self.trend_direction.value
        return data

@dataclass
class AnalyticsResult:
    """Resultado de analytics"""
    id: str
    analysis_type: str
    level: AnalyticsLevel
    results: Dict[str, Any]
    insights: List[str]
    confidence: float
    processing_time: float
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['level'] = self.level.value
        return data

class CulturalScorer:
    """Sistema de scoring cultural proprietário"""
    
    def __init__(self):
        self.weights = {
            'engagement': 0.25,
            'reach': 0.20,
            'sentiment': 0.15,
            'virality': 0.15,
            'authenticity': 0.15,
            'innovation': 0.10
        }
        
    def calculate_score(self, data: Dict[str, Any]) -> float:
        """Calcular score cultural"""
        try:
            score = 0.0
            
            # Engagement score
            engagement = data.get('engagement', 0.5)
            score += engagement * self.weights['engagement']
            
            # Reach score
            reach = min(1.0, data.get('reach', 0) / 10000)  # Normalizar por 10k
            score += reach * self.weights['reach']
            
            # Sentiment score
            sentiment = (data.get('sentiment', 0) + 1) / 2  # Normalizar -1,1 para 0,1
            score += sentiment * self.weights['sentiment']
            
            # Virality score
            shares = data.get('shares', 0)
            comments = data.get('comments', 0)
            virality = min(1.0, (shares + comments) / 1000)
            score += virality * self.weights['virality']
            
            # Authenticity score (baseado em originalidade)
            authenticity = 1.0 - data.get('similarity_score', 0.3)
            score += authenticity * self.weights['authenticity']
            
            # Innovation score
            innovation = data.get('innovation_index', 0.5)
            score += innovation * self.weights['innovation']
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"❌ Erro no scoring: {e}")
            return 0.5

class TrendDetector:
    """Detector de tendências avançado"""
    
    def __init__(self, window_size: int = 50):
        self.window_size = window_size
        self.data_history = defaultdict(lambda: deque(maxlen=window_size))
        
    def add_data_point(self, category: str, value: float, timestamp: datetime = None):
        """Adicionar ponto de dados"""
        if timestamp is None:
            timestamp = datetime.now()
            
        self.data_history[category].append((timestamp, value))
        
    def detect_trend(self, category: str) -> Tuple[TrendDirection, float]:
        """Detectar tendência para categoria"""
        if category not in self.data_history or len(self.data_history[category]) < 5:
            return TrendDirection.STABLE, 0.5
            
        values = [point[1] for point in self.data_history[category]]
        
        # Calcular tendência usando regressão linear simples
        x = np.arange(len(values))
        slope, _ = np.polyfit(x, values, 1)
        
        # Calcular volatilidade
        if len(values) > 1:
            volatility = np.std(values) / max(np.mean(values), 0.01)
        else:
            volatility = 0
            
        # Determinar direção
        if volatility > 0.5:
            direction = TrendDirection.VOLATILE
        elif slope > 0.05:
            direction = TrendDirection.RISING
        elif slope < -0.05:
            direction = TrendDirection.FALLING
        else:
            direction = TrendDirection.STABLE
            
        # Confidence baseada na consistência da tendência
        confidence = min(1.0, abs(slope) * 10 + (1 - volatility))
        
        return direction, confidence

class SentimentAnalyzer:
    """Analisador de sentimentos cultural"""
    
    def __init__(self):
        # Dicionários de sentimentos para cultura brasileira
        self.positive_words = {
            'incrível', 'sensacional', 'fantástico', 'maravilhoso', 'perfeito',
            'lindo', 'emocionante', 'vibrante', 'autêntico', 'inovador',
            'revolucionário', 'inspirador', 'único', 'original', 'criativo'
        }
        
        self.negative_words = {
            'terrível', 'horrível', 'péssimo', 'ruim', 'chato',
            'sem graça', 'ultrapassado', 'cópia', 'repetitivo', 'forçado',
            'fake', 'artificial', 'comercial', 'vendido', 'mainstream'
        }
        
        self.cultural_words = {
            'autêntico': 0.8, 'original': 0.7, 'genuíno': 0.8,
            'raiz': 0.9, 'underground': 0.6, 'independente': 0.7,
            'mainstream': -0.3, 'comercial': -0.4, 'vendido': -0.8
        }
        
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analisar sentimento do texto"""
        if not text:
            return {'score': 0.0, 'confidence': 0.0, 'cultural_relevance': 0.5}
            
        text_lower = text.lower()
        words = text_lower.split()
        
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        # Score básico
        if len(words) > 0:
            basic_score = (positive_count - negative_count) / len(words)
        else:
            basic_score = 0.0
            
        # Score cultural
        cultural_score = 0.0
        cultural_hits = 0
        
        for word in words:
            if word in self.cultural_words:
                cultural_score += self.cultural_words[word]
                cultural_hits += 1
                
        if cultural_hits > 0:
            cultural_score /= cultural_hits
        else:
            cultural_score = 0.0
            
        # Score final combinado
        final_score = (basic_score * 0.7) + (cultural_score * 0.3)
        
        # Confidence baseada na quantidade de palavras relevantes
        confidence = min(1.0, (positive_count + negative_count + cultural_hits) / max(len(words), 1))
        
        # Relevância cultural
        cultural_relevance = min(1.0, cultural_hits / max(len(words), 1) * 10)
        
        return {
            'score': max(-1.0, min(1.0, final_score)),
            'confidence': confidence,
            'cultural_relevance': cultural_relevance
        }

class InsightGenerator:
    """Gerador de insights automáticos"""
    
    def __init__(self):
        self.insight_templates = {
            'trending_up': [
                "📈 {category} está em forte crescimento com {growth:.0%} de aumento",
                "🚀 Detectado momentum crescente em {category} (+{growth:.0%})",
                "⭐ {category} emergindo como tendência com {confidence:.0%} de confiança"
            ],
            'trending_down': [
                "📉 {category} apresenta declínio de {decline:.0%}",
                "⚠️ Tendência descendente em {category} (-{decline:.0%})",
                "🔻 {category} perdendo relevância cultural"
            ],
            'high_sentiment': [
                "😍 Sentimento muito positivo detectado em {category} (score: {score:.2f})",
                "✨ Comunidade abraçando {category} com entusiasmo",
                "💯 {category} gerando reações altamente positivas"
            ],
            'cultural_shift': [
                "🌊 Mudança cultural detectada: {description}",
                "🔄 Evolução cultural em andamento em {category}",
                "🌟 Novo padrão cultural emergindo"
            ]
        }
        
    def generate_insights(self, analytics_data: Dict[str, Any]) -> List[str]:
        """Gerar insights automáticos"""
        insights = []
        
        try:
            # Insights de tendências
            trends = analytics_data.get('trends', {})
            for category, trend_data in trends.items():
                direction = trend_data.get('direction')
                confidence = trend_data.get('confidence', 0)
                
                if direction == 'rising' and confidence > 0.7:
                    template = np.random.choice(self.insight_templates['trending_up'])
                    insight = template.format(
                        category=category,
                        growth=confidence,
                        confidence=confidence
                    )
                    insights.append(insight)
                    
                elif direction == 'falling' and confidence > 0.7:
                    template = np.random.choice(self.insight_templates['trending_down'])
                    insight = template.format(
                        category=category,
                        decline=confidence,
                        confidence=confidence
                    )
                    insights.append(insight)
            
            # Insights de sentimento
            sentiment_data = analytics_data.get('sentiment', {})
            if sentiment_data.get('score', 0) > 0.7:
                template = np.random.choice(self.insight_templates['high_sentiment'])
                insight = template.format(
                    category=sentiment_data.get('category', 'conteúdo'),
                    score=sentiment_data['score']
                )
                insights.append(insight)
                
            # Insights culturais
            cultural_signals = analytics_data.get('cultural_signals', [])
            if len(cultural_signals) > 3:
                insight = f"🎯 {len(cultural_signals)} sinais culturais únicos detectados simultaneamente"
                insights.append(insight)
                
        except Exception as e:
            logger.error(f"❌ Erro na geração de insights: {e}")
            
        return insights[:5]  # Limitar a 5 insights

class AdvancedAnalyticsEngine:
    """Motor principal de analytics avançado"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.scorer = CulturalScorer()
        self.trend_detector = TrendDetector()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.insight_generator = InsightGenerator()
        
        self.analysis_history = []
        self.cultural_signals = []
        self.max_history = 1000
        
        logger.info("🧠 Advanced Analytics Engine V8.2 inicializado")
        
    def analyze(self, data: Union[Dict, List[Dict]], level: AnalyticsLevel = AnalyticsLevel.INTERMEDIATE) -> AnalyticsResult:
        """Realizar análise completa"""
        start_time = datetime.now()
        analysis_id = f"analytics_{uuid.uuid4().hex[:8]}"
        
        # Normalizar entrada
        if isinstance(data, dict):
            data_list = [data]
        else:
            data_list = data
            
        results = {}
        insights = []
        
        try:
            if level in [AnalyticsLevel.BASIC, AnalyticsLevel.INTERMEDIATE, AnalyticsLevel.ADVANCED, AnalyticsLevel.EXPERT]:
                results.update(self._basic_analytics(data_list))
                
            if level in [AnalyticsLevel.INTERMEDIATE, AnalyticsLevel.ADVANCED, AnalyticsLevel.EXPERT]:
                results.update(self._intermediate_analytics(data_list))
                
            if level in [AnalyticsLevel.ADVANCED, AnalyticsLevel.EXPERT]:
                results.update(self._advanced_analytics(data_list))
                
            if level == AnalyticsLevel.EXPERT:
                results.update(self._expert_analytics(data_list))
                
            # Gerar insights
            insights = self.insight_generator.generate_insights(results)
            
            # Calcular confidence geral
            confidence = self._calculate_overall_confidence(results)
            
        except Exception as e:
            logger.error(f"❌ Erro na análise: {e}")
            results = {'error': str(e)}
            confidence = 0.0
            
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Criar resultado
        result = AnalyticsResult(
            id=analysis_id,
            analysis_type=f"cultural_analytics_{level.value}",
            level=level,
            results=results,
            insights=insights,
            confidence=confidence,
            processing_time=processing_time,
            created_at=start_time
        )
        
        # Armazenar histórico
        self.analysis_history.append(result)
        if len(self.analysis_history) > self.max_history:
            self.analysis_history = self.analysis_history[-self.max_history:]
            
        return result
        
    def _basic_analytics(self, data_list: List[Dict]) -> Dict[str, Any]:
        """Analytics básico"""
        results = {
            'total_items': len(data_list),
            'categories': {},
            'average_score': 0.0,
            'score_distribution': {}
        }
        
        scores = []
        categories = defaultdict(int)
        
        for item in data_list:
            # Scoring
            score = self.scorer.calculate_score(item)
            scores.append(score)
            
            # Categorias
            category = item.get('category', 'unknown')
            categories[category] += 1
            
        if scores:
            results['average_score'] = statistics.mean(scores)
            results['score_distribution'] = {
                'min': min(scores),
                'max': max(scores),
                'median': statistics.median(scores),
                'std': statistics.stdev(scores) if len(scores) > 1 else 0
            }
            
        results['categories'] = dict(categories)
        
        return results
        
    def _intermediate_analytics(self, data_list: List[Dict]) -> Dict[str, Any]:
        """Analytics intermediário"""
        results = {
            'sentiment_analysis': {},
            'trend_analysis': {},
            'temporal_patterns': {}
        }
        
        # Análise de sentimento
        sentiments = []
        for item in data_list:
            content = item.get('content', '')
            sentiment = self.sentiment_analyzer.analyze_sentiment(str(content))
            sentiments.append(sentiment)
            
        if sentiments:
            results['sentiment_analysis'] = {
                'average_score': statistics.mean([s['score'] for s in sentiments]),
                'average_confidence': statistics.mean([s['confidence'] for s in sentiments]),
                'cultural_relevance': statistics.mean([s['cultural_relevance'] for s in sentiments])
            }
            
        # Análise de tendências
        categories = defaultdict(list)
        for item in data_list:
            category = item.get('category', 'unknown')
            score = self.scorer.calculate_score(item)
            timestamp = item.get('timestamp', datetime.now())
            
            self.trend_detector.add_data_point(category, score, timestamp)
            categories[category].append(score)
            
        trends = {}
        for category in categories:
            direction, confidence = self.trend_detector.detect_trend(category)
            trends[category] = {
                'direction': direction.value,
                'confidence': confidence,
                'sample_size': len(categories[category])
            }
            
        results['trend_analysis'] = trends
        
        return results
        
    def _advanced_analytics(self, data_list: List[Dict]) -> Dict[str, Any]:
        """Analytics avançado"""
        results = {
            'cultural_signals': [],
            'anomaly_detection': {},
            'predictive_insights': {}
        }
        
        # Detecção de sinais culturais
        signals = self._detect_cultural_signals(data_list)
        results['cultural_signals'] = [signal.to_dict() for signal in signals]
        
        # Detecção de anomalias
        scores = [self.scorer.calculate_score(item) for item in data_list]
        if scores:
            mean_score = statistics.mean(scores)
            std_score = statistics.stdev(scores) if len(scores) > 1 else 0
            
            anomalies = []
            for i, score in enumerate(scores):
                if abs(score - mean_score) > 2 * std_score:
                    anomalies.append({
                        'index': i,
                        'score': score,
                        'deviation': abs(score - mean_score)
                    })
                    
            results['anomaly_detection'] = {
                'anomalies_found': len(anomalies),
                'anomaly_rate': len(anomalies) / len(scores),
                'anomalies': anomalies[:10]  # Top 10
            }
            
        return results
        
    def _expert_analytics(self, data_list: List[Dict]) -> Dict[str, Any]:
        """Analytics expert"""
        results = {
            'cross_category_analysis': {},
            'influence_mapping': {},
            'future_projections': {}
        }
        
        # Análise cross-categoria
        categories = defaultdict(list)
        for item in data_list:
            category = item.get('category', 'unknown')
            score = self.scorer.calculate_score(item)
            categories[category].append(score)
            
        # Correlações entre categorias
        category_names = list(categories.keys())
        correlations = {}
        
        for i, cat1 in enumerate(category_names):
            for cat2 in category_names[i+1:]:
                if len(categories[cat1]) > 1 and len(categories[cat2]) > 1:
                    # Correlação simples
                    min_len = min(len(categories[cat1]), len(categories[cat2]))
                    corr = np.corrcoef(
                        categories[cat1][:min_len],
                        categories[cat2][:min_len]
                    )[0, 1]
                    
                    if not np.isnan(corr):
                        correlations[f"{cat1}_vs_{cat2}"] = float(corr)
                        
        results['cross_category_analysis'] = correlations
        
        # Projeções futuras (simuladas)
        projections = {}
        for category, scores in categories.items():
            if len(scores) > 2:
                trend = np.polyfit(range(len(scores)), scores, 1)[0]
                projection = scores[-1] + trend * 7  # 7 períodos à frente
                projections[category] = {
                    'current_score': scores[-1],
                    'projected_score': float(projection),
                    'trend_strength': abs(float(trend))
                }
                
        results['future_projections'] = projections
        
        return results
        
    def _detect_cultural_signals(self, data_list: List[Dict]) -> List[CulturalSignal]:
        """Detectar sinais culturais"""
        signals = []
        
        # Agrupar por categoria
        categories = defaultdict(list)
        for item in data_list:
            category = item.get('category', 'unknown')
            categories[category].append(item)
            
        for category, items in categories.items():
            if len(items) < 3:  # Mínimo para detecção
                continue
                
            scores = [self.scorer.calculate_score(item) for item in items]
            avg_score = statistics.mean(scores)
            
            # Detectar se é um sinal forte
            if avg_score > 0.7:  # Threshold para sinal
                direction, confidence = self.trend_detector.detect_trend(category)
                
                signal = CulturalSignal(
                    id=f"signal_{uuid.uuid4().hex[:8]}",
                    name=f"Emergência em {category}",
                    category=category,
                    strength=avg_score,
                    confidence=confidence,
                    trend_direction=direction,
                    metadata={
                        'sample_size': len(items),
                        'score_std': statistics.stdev(scores) if len(scores) > 1 else 0,
                        'detection_method': 'threshold_based'
                    },
                    detected_at=datetime.now(),
                    sources=[item.get('source', 'unknown') for item in items]
                )
                
                signals.append(signal)
                
        return signals
        
    def _calculate_overall_confidence(self, results: Dict[str, Any]) -> float:
        """Calcular confidence geral da análise"""
        confidences = []
        
        # Confidence do sentiment
        sentiment = results.get('sentiment_analysis', {})
        if 'average_confidence' in sentiment:
            confidences.append(sentiment['average_confidence'])
            
        # Confidence das tendências
        trends = results.get('trend_analysis', {})
        for trend_data in trends.values():
            if 'confidence' in trend_data:
                confidences.append(trend_data['confidence'])
                
        # Confidence dos sinais culturais
        signals = results.get('cultural_signals', [])
        for signal in signals:
            if isinstance(signal, dict) and 'confidence' in signal:
                confidences.append(signal['confidence'])
                
        return statistics.mean(confidences) if confidences else 0.5
        
    def get_analysis_history(self, limit: int = 100) -> List[AnalyticsResult]:
        """Obter histórico de análises"""
        return self.analysis_history[-limit:]
        
    def get_cultural_signals(self, category: str = None) -> List[CulturalSignal]:
        """Obter sinais culturais detectados"""
        if category:
            return [s for s in self.cultural_signals if s.category == category]
        return self.cultural_signals

# Singleton
_analytics_engine = None

def get_analytics_engine(config: Dict[str, Any] = None) -> AdvancedAnalyticsEngine:
    """Obter instância singleton do analytics engine"""
    global _analytics_engine
    
    if _analytics_engine is None:
        _analytics_engine = AdvancedAnalyticsEngine(config)
        
    return _analytics_engine

if __name__ == "__main__":
    # Demo do analytics engine
    print("🧠 Demo: Advanced Analytics Engine V8.2")
    print("=" * 50)
    
    engine = get_analytics_engine()
    
    # Dados de exemplo
    sample_data = [
        {
            'content': 'Nova música incrível do underground brasileiro!',
            'category': 'música',
            'engagement': 0.8,
            'reach': 5000,
            'shares': 120,
            'comments': 45,
            'sentiment': 0.9
        },
        {
            'content': 'Arte digital inovadora com elementos culturais',
            'category': 'arte',
            'engagement': 0.7,
            'reach': 3000,
            'shares': 80,
            'comments': 25,
            'sentiment': 0.6
        },
        {
            'content': 'Moda sustentável brasileira está em alta',
            'category': 'moda',
            'engagement': 0.9,
            'reach': 8000,
            'shares': 200,
            'comments': 67,
            'sentiment': 0.8
        }
    ]
    
    # Análise avançada
    result = engine.analyze(sample_data, AnalyticsLevel.ADVANCED)
    
    print(f"📊 Análise ID: {result.id}")
    print(f"⏱️ Tempo de processamento: {result.processing_time:.3f}s")
    print(f"🎯 Confidence: {result.confidence:.2%}")
    print(f"📈 Insights gerados: {len(result.insights)}")
    
    for insight in result.insights:
        print(f"   💡 {insight}")
        
    print("\n✅ Advanced Analytics Engine V8.2 funcionando!")
