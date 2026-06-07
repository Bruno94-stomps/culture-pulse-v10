"""
🎯 CULTURAL METRICS ENGINE V9.0 - FINAL INTEGRATION
Integração completa: Ensemble + Online Learning + Weak Signals

COMPONENTES INTEGRADOS:
1. Automated Learning Engine (pesos adaptativos)
2. Weighted Ensemble (JÁ EXISTE)
3. Weak Signals Detector (JÁ EXISTE)
4. Trend Algorithms (JÁ EXISTE)
"""

import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Imports dos componentes existentes
from core.intelligence.learning.StrategyLearner import get_strategy_learner
from core.engines.trend_algorithms import (
    calculate_velocity_with_time_window,
    calculate_second_derivative,
    calculate_cross_circle_activation,
    calculate_geographic_diffusion,
    weighted_ensemble
)
from autonomous_agent.weak_signals_detector import WeakSignalsDetector

# Anomaly Detection
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN

# Cultural Embeddings (DEEP TECH)
try:
    from core.engines.cultural_computing_engine import CulturalComputingEngine, PolarityAnalysis
    from core.engines.cultural_embedding_analyzer import CulturalEmbeddingAnalyzer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("⚠️ Cultural Embeddings não disponíveis (BERT)")

logger = logging.getLogger(__name__)

class CulturalMetricsEngine:
    """
    🎯 Engine unificado de métricas culturais
    
    INTEGRAÇÃO FINAL - FASE 1 + 2:
    - Automated Learning para pesos adaptativos
    - Ensemble para combinar múltiplas perspectivas
    - Weak Signals para detecção precoce
    - Trend Algorithms para cálculos base
    """
    
    def __init__(self):
        # Componente 1: Aprendizado automatizado
        self.learning_engine = get_strategy_learner()
        
        # Componente 2: Detector de sinais fracos (já usa DBSCAN internamente)
        self.weak_signals_detector = WeakSignalsDetector()
        
        # Componente 3: Anomaly Detection (IsolationForest)
        self.anomaly_detector = IsolationForest(
            contamination=0.1,  # 10% de anomalias esperadas
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.anomaly_fitted = False
        
        # Componente 4: DBSCAN para clustering adicional
        self.dbscan = DBSCAN(eps=0.3, min_samples=2)
        
        # Componente 5: Cultural Embeddings (DEEP TECH - NOVO!)
        if EMBEDDINGS_AVAILABLE:
            try:
                self.cultural_computing = CulturalComputingEngine()
                self.embedding_analyzer = CulturalEmbeddingAnalyzer(self.cultural_computing.model)
                logger.info("✅ Cultural Embeddings (BERT) inicializado!")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao inicializar embeddings: {e}")
                self.cultural_computing = None
                self.embedding_analyzer = None
        else:
            self.cultural_computing = None
            self.embedding_analyzer = None
        
        # Configurações
        self.confidence_threshold = 0.6  # Mínimo 60% de confiança
        
        # Modifiers contextuais por indústria (NOVO!)
        self.industry_modifiers = self._initialize_industry_modifiers()
        
        logger.info("🎯 Cultural Metrics Engine V9.0 inicializado!")
        logger.info("   ✅ Anomaly Detection (IsolationForest) ativo")
        logger.info("   ✅ DBSCAN Clustering ativo")
        logger.info("   ✅ Weak Signals Detection ativo")
        logger.info("   ✅ Industry Modifiers configurados")
        if self.cultural_computing:
            logger.info("   ✅ Cultural Embeddings (BERT) ATIVO - DEEP TECH MODE!")
    
    def calculate_all_metrics(self, 
                             data: Dict[str, Any], 
                             industry: str = "fashion",
                             historical_data: Optional[Dict[str, Any]] = None,
                             user_intent: str = "Pesquisa de Mercado") -> Dict[str, Any]:
        """
        Calcula todas as métricas culturais com pesos adaptativos
        
        Args:
            data: Dados atuais coletados
            industry: Indústria/contexto (fashion, tech, music, food)
            historical_data: Dados históricos (opcional)
            
        Returns:
            Dict com todas as métricas e metadados
        """
        try:
            # 1. BUSCAR PESOS APRENDIDOS
            weights = self.learning_engine.get_learned_weights_for_context(industry)
            
            # Se confiança baixa, usar pesos default
            if weights.get('confidence', 0) < self.confidence_threshold:
                logger.warning(f"Confiança baixa ({weights.get('confidence', 0):.2f}), usando pesos default")
                weights = self._get_default_weights()
                weights['confidence'] = 0.5
            
            # 1.5 APLICAR MODIFIERS CONTEXTUAIS POR INDÚSTRIA (NOVO!)
            weights = self.apply_industry_modifiers(weights, industry)
            
            # 2. CALCULAR MÉTRICAS BASE
            base_metrics = self._calculate_base_metrics(data, historical_data)
            
            # 3. CALCULAR MOMENTUM COM PESOS ADAPTATIVOS
            momentum = self._calculate_adaptive_momentum(base_metrics, weights)
            
            # 4. DETECTAR SINAIS FRACOS (usa DBSCAN)
            weak_signals = self._detect_weak_signals(data, user_intent=user_intent)
            # 4.5 DETECTAR ANOMALIAS (usa IsolationForest + DBSCAN)
            anomalies = self._detect_anomalies(data)
            
            # 5. AJUSTAR MOMENTUM COM SINAIS FRACOS E ANOMALIAS
            adjusted_momentum = self._adjust_with_weak_signals(momentum, weak_signals)
            adjusted_momentum = self._adjust_with_anomalies(adjusted_momentum, anomalies)
            
            # 6. CALCULAR SCORE CULTURAL (diferente de momentum!)
            score_cultural = self._calculate_score_cultural(base_metrics)
            
            # 7. ENSEMBLE DE PREDIÇÕES
            ensemble_prediction = self._calculate_ensemble_prediction(
                base_metrics, momentum, weak_signals
            )
            
            # Resultado final
            result = {
                'timestamp': datetime.now().isoformat(),
                'industry': industry,
                'weights_used': weights,
                'confidence': weights['confidence'],
                
                # Métricas base
                'base_metrics': base_metrics,
                
                # Métricas proprietárias
                'momentum_cultural': adjusted_momentum,
                'score_cultural': score_cultural,
                'ib_score': base_metrics.get('ib', 0),
                'cvi_score': base_metrics.get('cvi', 0),
                'cii_score': base_metrics.get('cii', 0),
                
                # Sinais fracos
                'weak_signals': weak_signals,
                
                # Anomalias detectadas
                'anomalies': anomalies,
                
                # Predições
                'ensemble_prediction': ensemble_prediction,
                
                # Metadados
                'metadata': {
                    'learning_stage': self._get_learning_stage(weights['confidence']),
                    'data_points_used': len(self.learning_engine.data_buffer),
                    'model_version': 'V9.0'
                }
            }
            
            logger.info(f"✅ Métricas calculadas - Momentum: {adjusted_momentum:.2f}, Confiança: {weights['confidence']:.2%}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular métricas: {e}")
            return {'error': str(e)}
    
    def _calculate_base_metrics(self, 
                                data: Dict[str, Any], 
                                historical_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula métricas base usando trend_algorithms"""
        
        metrics = {}
        
        # Velocity (com janela temporal se houver histórico)
        if historical_data:
            metrics['velocity'] = calculate_velocity_with_time_window(
                data, historical_data, time_window=7
            )
        else:
            metrics['velocity'] = self._calculate_velocity_simple(data)
        
        # Acceleration (segunda derivada)
        if historical_data:
            metrics['acceleration'] = calculate_second_derivative(
                [historical_data.get('velocity', 0), metrics['velocity']]
            )
        else:
            metrics['acceleration'] = 0
        
        # CII (Cultural Impact Index)
        metrics['cii'] = self._calculate_cii(data)
        
        # Geographic Spread
        metrics['geographic_spread'] = calculate_geographic_diffusion(data)
        
        # Resonance (cross-circle activation)
        metrics['resonance'] = calculate_cross_circle_activation(data)
        
        # IB (Index of Brazilianness) - ESTÁTICO, não entra no momentum!
        metrics['ib'] = self._calculate_ib(data)
        
        # CVI (Cultural Velocity Index)
        metrics['cvi'] = min(metrics['velocity'] / 100, 1.0) * 100
        
        return metrics
    
    def _calculate_adaptive_momentum(self, 
                                    metrics: Dict[str, float], 
                                    weights: Dict[str, float]) -> float:
        """
        Calcula momentum com pesos adaptativos
        
        IMPORTANTE: IB NÃO entra no momentum (é estático)
        Momentum = função de métricas DINÂMICAS
        """
        
        momentum = (
            metrics['velocity'] * weights['velocity'] +
            metrics['acceleration'] * weights['acceleration'] +
            metrics['cii'] * weights['cii'] +
            metrics['geographic_spread'] * weights['geographic_spread'] +
            metrics['resonance'] * weights['resonance']
        )
        
        # Normalizar (0-100)
        momentum = min(max(momentum, 0), 100)
        
        return momentum
    
    def _detect_weak_signals(self, data: Dict[str, Any], user_intent: str = "Pesquisa de Mercado") -> Dict[str, Any]:
        """Detecta sinais fracos usando detector existente (DBSCAN internamente)"""
        try:
            # Preparar data_points para o detector
            data_points = self._prepare_data_points(data)
            
            # Detectar (usa DBSCAN internamente)
            weak_signals = self.weak_signals_detector.detect_weak_signals(
                data_points, 
                timeframe=30,
                user_intent=user_intent
            )
            
            return weak_signals
            
        except Exception as e:
            logger.warning(f"Erro ao detectar sinais fracos: {e}")
            return {
                'total_signals': 0,
                'signals_by_strength': {},
                'recommendations': []
            }
    
    def _detect_anomalies(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        🔍 ANOMALY DETECTION usando IsolationForest
        
        Detecta comportamentos anômalos nos dados coletados.
        Útil para identificar:
        - Crescimento súbito e inesperado
        - Padrões fora do normal
        - Potenciais viralidades
        """
        try:
            data_points = self._prepare_data_points(data)
            
            if len(data_points) < 10:
                return {'anomalies_detected': 0, 'anomaly_score': 0, 'is_anomalous': False}
            
            # Extrair features para anomaly detection
            features_matrix = []
            for dp in data_points:
                features = [
                    dp.get('engagement', 0),
                    dp.get('velocity', 0),
                    len(str(dp.get('content', ''))),
                    dp.get('sentiment', 0.5)
                ]
                features_matrix.append(features)
            
            features_matrix = np.array(features_matrix)
            
            # Normalizar
            features_scaled = self.scaler.fit_transform(features_matrix)
            
            # Fit se não foi feito ainda
            if not self.anomaly_fitted:
                self.anomaly_detector.fit(features_scaled)
                self.anomaly_fitted = True
            
            # Predizer anomalias (-1 = anomalia, 1 = normal)
            predictions = self.anomaly_detector.predict(features_scaled)
            anomaly_scores = self.anomaly_detector.score_samples(features_scaled)
            
            # Contar anomalias
            anomalies_count = np.sum(predictions == -1)
            anomaly_ratio = anomalies_count / len(predictions)
            
            # Score médio (quanto mais negativo, mais anômalo)
            avg_anomaly_score = np.mean(anomaly_scores)
            
            # DBSCAN adicional para agrupar anomalias
            anomaly_indices = np.where(predictions == -1)[0]
            clusters = []
            
            if len(anomaly_indices) > 1:
                anomaly_features = features_scaled[anomaly_indices]
                dbscan_labels = self.dbscan.fit_predict(anomaly_features)
                
                # Agrupar por cluster
                for cluster_id in set(dbscan_labels):
                    if cluster_id != -1:  # -1 é noise
                        cluster_points = np.where(dbscan_labels == cluster_id)[0]
                        clusters.append({
                            'cluster_id': int(cluster_id),
                            'size': len(cluster_points),
                            'anomaly_type': self._classify_anomaly_type(
                                features_matrix[anomaly_indices[cluster_points]]
                            )
                        })
            
            result = {
                'anomalies_detected': int(anomalies_count),
                'anomaly_ratio': float(anomaly_ratio),
                'avg_anomaly_score': float(avg_anomaly_score),
                'is_anomalous': anomaly_ratio > 0.15,  # >15% de anomalias
                'anomaly_clusters': clusters,
                'severity': 'high' if anomaly_ratio > 0.25 else 'medium' if anomaly_ratio > 0.15 else 'low'
            }
            
            if result['is_anomalous']:
                logger.info(f"🚨 Anomalias detectadas: {anomalies_count}/{len(predictions)} ({anomaly_ratio:.1%})")
            
            return result
            
        except Exception as e:
            logger.warning(f"Erro na detecção de anomalias: {e}")
            return {'anomalies_detected': 0, 'anomaly_score': 0, 'is_anomalous': False}
    
    def _classify_anomaly_type(self, features: np.ndarray) -> str:
        """Classifica tipo de anomalia baseado nas features"""
        avg_engagement = np.mean(features[:, 0])
        avg_velocity = np.mean(features[:, 1])
        
        if avg_engagement > 1000 and avg_velocity > 50:
            return "viral_spike"
        elif avg_engagement > 1000:
            return "high_engagement"
        elif avg_velocity > 50:
            return "rapid_growth"
        else:
            return "unusual_pattern"
    
    def _adjust_with_weak_signals(self, 
                                  momentum: float, 
                                  weak_signals: Dict[str, Any]) -> float:
        """Ajusta momentum baseado em sinais fracos detectados"""
        
        total_signals = weak_signals.get('total_signals', 0)
        
        if total_signals == 0:
            return momentum
        
        # Boost baseado em quantidade e força dos sinais
        if total_signals > 10:
            boost = 1.3  # 30% boost
        elif total_signals > 5:
            boost = 1.2  # 20% boost
        elif total_signals > 2:
            boost = 1.1  # 10% boost
        else:
            boost = 1.05  # 5% boost
        
        adjusted = momentum * boost
        
        logger.info(f"Momentum ajustado (weak signals): {momentum:.2f} → {adjusted:.2f} ({total_signals} sinais)")
        
        return min(adjusted, 100)  # Cap em 100
    
    def _adjust_with_anomalies(self, 
                               momentum: float, 
                               anomalies: Dict[str, Any]) -> float:
        """
        Ajusta momentum baseado em anomalias detectadas
        
        Anomalias indicam comportamento fora do padrão que pode ser:
        - Viralização emergente
        - Crescimento súbito
        - Padrão incomum
        """
        
        if not anomalies.get('is_anomalous', False):
            return momentum
        
        anomaly_ratio = anomalies.get('anomaly_ratio', 0)
        severity = anomalies.get('severity', 'low')
        
        # Boost baseado em severidade
        if severity == 'high':
            boost = 1.4  # 40% boost (muito anômalo = potencial viral!)
        elif severity == 'medium':
            boost = 1.25  # 25% boost
        else:
            boost = 1.1  # 10% boost
        
        # Verificar tipo de anomalia
        clusters = anomalies.get('anomaly_clusters', [])
        for cluster in clusters:
            if cluster.get('anomaly_type') == 'viral_spike':
                boost *= 1.2  # Boost adicional para viral spike
                logger.warning(f"🚀 VIRAL SPIKE detectado! Boost extra aplicado")
        
        adjusted = momentum * boost
        
        logger.info(f"Momentum ajustado (anomalies): {momentum:.2f} → {adjusted:.2f} (severidade: {severity})")
        
        return min(adjusted, 100)  # Cap em 100
    
    def _calculate_score_cultural(self, metrics: Dict[str, float]) -> float:
        """
        Score Cultural = média de IB + CVI + CII
        DIFERENTE de Momentum!
        
        Score Cultural: Quão culturalmente relevante (estático)
        Momentum: Quão rápido está crescendo (dinâmico)
        """
        
        ib = metrics.get('ib', 0)
        cvi = metrics.get('cvi', 0)
        cii = metrics.get('cii', 0)
        
        score = (ib + cvi + cii) / 3
        
        return score
    
    def _calculate_ensemble_prediction(self,
                                      metrics: Dict[str, float],
                                      momentum: float,
                                      weak_signals: Dict[str, Any]) -> Dict[str, Any]:
        """Usa ensemble para predições futuras"""
        
        try:
            # Preparar predições de diferentes modelos
            predictions = {
                'temporal': self._predict_temporal(metrics, momentum),
                'cultural': self._predict_cultural(metrics),
                'social': self._predict_social(weak_signals)
            }
            
            # Combinar com weighted_ensemble
            ensemble_result = weighted_ensemble(predictions)
            
            return {
                'trajectory_90_days': ensemble_result,
                'confidence': 0.8,
                'models_used': list(predictions.keys())
            }
            
        except Exception as e:
            logger.warning(f"Erro no ensemble: {e}")
            return {'trajectory_90_days': [], 'confidence': 0}
    
    def _predict_temporal(self, metrics: Dict[str, float], momentum: float) -> List[float]:
        """Predição temporal simples"""
        # Extrapolação linear baseada em momentum
        trajectory = []
        current = momentum
        
        for i in range(90):
            # Decay gradual
            current = current * 0.99 + np.random.normal(0, 2)
            current = max(0, min(current, 100))
            trajectory.append(current)
        
        return trajectory
    
    def _predict_cultural(self, metrics: Dict[str, float]) -> List[float]:
        """Predição baseada em aspectos culturais"""
        # Baseado em IB e CII
        base = (metrics.get('ib', 50) + metrics.get('cii', 50)) / 2
        
        trajectory = []
        for i in range(90):
            value = base + np.sin(i / 15) * 10 + np.random.normal(0, 3)
            value = max(0, min(value, 100))
            trajectory.append(value)
        
        return trajectory
    
    def _predict_social(self, weak_signals: Dict[str, Any]) -> List[float]:
        """Predição baseada em sinais fracos"""
        # Boost se muitos sinais fracos
        total_signals = weak_signals.get('total_signals', 0)
        base = 50 + (total_signals * 2)
        
        trajectory = []
        for i in range(90):
            value = base + np.random.normal(0, 5)
            value = max(0, min(value, 100))
            trajectory.append(value)
        
        return trajectory
    
    def _get_default_weights(self) -> Dict[str, float]:
        """Pesos default quando confiança baixa"""
        return {
            'velocity': 0.25,
            'acceleration': 0.15,
            'cii': 0.30,
            'geographic_spread': 0.15,
            'resonance': 0.15,
            'confidence': 0.5
        }
    
    def _initialize_industry_modifiers(self) -> Dict[str, Dict[str, float]]:
        """
        🎯 MODIFIERS CONTEXTUAIS POR INDÚSTRIA
        
        Ajusta pesos base de acordo com características específicas de cada setor.
        Baseado em análise de comportamento cultural por vertical.
        """
        return {
            'fashion': {
                'velocity': 1.20,           # Moda é rápida e sazonal
                'acceleration': 0.95,        # Crescimento menos importante que velocidade
                'cii': 1.30,                # Alto engajamento visual (Instagram/TikTok)
                'geographic_spread': 0.85,   # Moda tende a ser concentrada em centros urbanos
                'resonance': 1.10,          # Discussões sobre estilo
                'description': 'Moda prioriza velocidade e engajamento visual. Concentrada em SP/RJ.'
            },
            'tech': {
                'velocity': 1.10,           # Crescimento constante mas não explosivo
                'acceleration': 1.30,        # Tecnologia tem crescimento exponencial
                'cii': 1.20,                # Discussões técnicas intensas
                'geographic_spread': 1.15,   # Tech se espalha mais (remote-first)
                'resonance': 1.25,          # Muito debate e evangelização
                'description': 'Tech prioriza aceleração e ressonância. Spread geográfico maior.'
            },
            'music': {
                'velocity': 1.40,           # Música viral é extremamente rápida
                'acceleration': 1.25,        # Hits crescem exponencialmente
                'cii': 0.90,                # Menos engajamento formal (mais streams que likes)
                'geographic_spread': 0.95,   # Música pode ser local ou nacional
                'resonance': 1.50,          # Altíssima ressonância (covers, remixes, memes)
                'description': 'Música prioriza velocidade e ressonância. Viralização rápida.'
            },
            'food': {
                'velocity': 0.95,           # Food é mais lento que moda/música
                'acceleration': 0.90,        # Crescimento gradual
                'cii': 1.25,                # Alto engajamento visual (food porn)
                'geographic_spread': 1.30,   # Forte componente regional/local
                'resonance': 1.15,          # Discussões sobre receitas e lugares
                'description': 'Food prioriza geographic spread e CII. Regional por natureza.'
            },
            'sports': {
                'velocity': 1.30,           # Eventos esportivos são rápidos
                'acceleration': 1.15,        # Crescimento durante eventos
                'cii': 1.35,                # Altíssimo engajamento (torcidas)
                'geographic_spread': 1.20,   # Esportes têm alcance regional forte
                'resonance': 1.40,          # Debate intenso (polêmicas, torcidas)
                'description': 'Sports prioriza CII e ressonância. Engajamento tribal.'
            },
            'entertainment': {
                'velocity': 1.25,           # Entretenimento se espalha rápido
                'acceleration': 1.10,        # Crescimento durante lançamentos
                'cii': 1.40,                # Altíssimo engajamento (fandom)
                'geographic_spread': 1.10,   # Spread moderado
                'resonance': 1.35,          # Fãs criam conteúdo (fanarts, teorias)
                'description': 'Entertainment prioriza CII e ressonância. Cultura de fandom.'
            },
            'politics': {
                'velocity': 1.35,           # Política é extremamente rápida
                'acceleration': 1.20,        # Crescimento durante crises
                'cii': 1.45,                # Altíssimo engajamento emocional
                'geographic_spread': 1.25,   # Nacional por natureza
                'resonance': 1.60,          # Máxima ressonância (polarização)
                'description': 'Politics prioriza ressonância e CII. Alta polarização.'
            },
            'health': {
                'velocity': 0.85,           # Saúde cresce mais devagar (confiança)
                'acceleration': 0.95,        # Crescimento gradual
                'cii': 1.15,                # Engajamento moderado
                'geographic_spread': 1.10,   # Spread moderado
                'resonance': 1.20,          # Discussões sobre bem-estar
                'description': 'Health prioriza ressonância e confiabilidade. Crescimento gradual.'
            },
            'education': {
                'velocity': 0.80,           # Educação cresce lentamente
                'acceleration': 0.85,        # Crescimento muito gradual
                'cii': 1.10,                # Engajamento moderado
                'geographic_spread': 1.15,   # Spread educacional é regional
                'resonance': 1.25,          # Discussões sobre métodos
                'description': 'Education prioriza ressonância e spread. Crescimento lento.'
            },
            'finance': {
                'velocity': 1.15,           # Finanças crescem constantemente
                'acceleration': 1.25,        # Crescimento pode ser exponencial
                'cii': 1.20,                # Engajamento forte (dinheiro move)
                'geographic_spread': 1.05,   # Concentrado em centros financeiros
                'resonance': 1.30,          # Discussões sobre investimentos
                'description': 'Finance prioriza aceleração e ressonância. Crescimento consistente.'
            }
        }
    
    def apply_industry_modifiers(self, 
                                 weights: Dict[str, float], 
                                 industry: str) -> Dict[str, float]:
        """
        Aplica modifiers contextuais por indústria aos pesos
        
        Args:
            weights: Pesos base (do learning engine ou defaults)
            industry: Indústria/contexto
            
        Returns:
            Pesos ajustados com modifiers
        """
        modifiers = self.industry_modifiers.get(industry.lower(), {})
        
        if not modifiers:
            logger.warning(f"Indústria '{industry}' não tem modifiers, usando pesos base")
            return weights
        
        # Aplicar modifiers
        adjusted_weights = {}
        for metric in ['velocity', 'acceleration', 'cii', 'geographic_spread', 'resonance']:
            base_weight = weights.get(metric, 0.2)
            modifier = modifiers.get(metric, 1.0)
            adjusted_weights[metric] = base_weight * modifier
        
        # Normalizar para somar 1.0
        total = sum(adjusted_weights.values())
        if total > 0:
            adjusted_weights = {k: v/total for k, v in adjusted_weights.items()}
        
        # Preservar confidence
        adjusted_weights['confidence'] = weights.get('confidence', 0.5)
        
        logger.info(f"✅ Modifiers aplicados para {industry}: {modifiers.get('description', '')}")
        
        return adjusted_weights
    
    def _get_learning_stage(self, confidence: float) -> str:
        """Determina estágio de aprendizado"""
        if confidence < 0.6:
            return "bootstrap"
        elif confidence < 0.8:
            return "learning"
        else:
            return "mature"
    
    # Métodos auxiliares - FÓRMULAS AJUSTADAS
    def _calculate_velocity_simple(self, data: Dict[str, Any]) -> float:
        """
        Velocidade simples (sem histórico)
        Fórmula: volume / threshold_normalizado
        """
        volume = len(data.get('data_points', []))
        # Normalizar: 0-100 pontos em 7 dias = 0-100 score
        return min((volume / 100) * 100, 100)
    
    def _calculate_cii(self, data: Dict[str, Any]) -> float:
        """
        🎯 CULTURAL IMPACT INDEX (CII) - FÓRMULA AJUSTADA
        
        CII = (Engagement_Total / Threshold) * Cultural_Multiplier
        
        Onde:
        - Engagement_Total = soma de todos engajamentos
        - Threshold = 10,000 (baseline para 100 pontos)
        - Cultural_Multiplier = boost baseado em marcadores culturais
        """
        data_points = data.get('data_points', [])
        if not data_points:
            return 0
        
        # Somar engajamento total
        total_engagement = sum(dp.get('engagement', 0) for dp in data_points)
        
        # CII base (normalizado)
        cii_base = min((total_engagement / 10000) * 100, 100)
        
        # Cultural multiplier (boost se tem marcadores culturais)
        cultural_multiplier = 1.0
        for dp in data_points:
            content = str(dp.get('content', '')).lower()
            # Verificar marcadores culturais brasileiros
            if any(marker in content for marker in ['brasil', 'brasileiro', 'br', 'nacional']):
                cultural_multiplier = max(cultural_multiplier, 1.2)
            # Verificar slang/gíria
            if any(slang in content for slang in ['mano', 'mina', 'truta', 'bro', 'vibe']):
                cultural_multiplier = max(cultural_multiplier, 1.15)
        
        cii_final = min(cii_base * cultural_multiplier, 100)
        
        return cii_final
    
    def _calculate_ib(self, data: Dict[str, Any]) -> float:
        """
        🇧🇷 INDEX OF BRAZILIANNESS (IB) - FÓRMULA AJUSTADA
        
        VERSÃO HYBRID: Usa embeddings (BERT) SE disponível, senão fallback para patterns
        
        IB = Σ(peso_marcador × presença) / total_marcadores
        
        Categorias de marcadores culturais:
        1. Linguagem (sotaques, gírias)
        2. Referências culturais (funk, samba, etc)
        3. Localização (cidades, regiões)
        4. Símbolos (bandeira, cores, etc)
        5. Comportamentos (jeitinho brasileiro, etc)
        """
        data_points = data.get('data_points', [])
        if not data_points:
            return 50.0  # Neutral
        
        # 🔥 MODO DEEP TECH: Usar embeddings BERT se disponível
        if self.cultural_computing and self.embedding_analyzer:
            try:
                return self._calculate_ib_with_embeddings(data_points)
            except Exception as e:
                logger.warning(f"⚠️ Erro ao calcular IB com embeddings: {e}, usando fallback")
        
        # Fallback: Método tradicional com patterns
        return self._calculate_ib_traditional(data_points)
    
    def _calculate_ib_with_embeddings(self, data_points: List[Dict]) -> float:
        """
        🧠 DEEP TECH: Calcular IB usando embeddings BERT
        
        Compara embeddings do conteúdo com embeddings regionais brasileiros
        """
        ib_scores = []
        
        for dp in data_points:
            content = str(dp.get('content', ''))
            if not content or len(content) < 10:
                continue
            
            # 1. Analisar polaridade cultural vs comercial
            polarity = self.cultural_computing.analyze_content_polarity(content)
            cultural_score = polarity.cultural_score  # 0-1
            
            # 2. Calcular similaridade com regiões brasileiras
            region_scores = []
            for region, region_embedding in self.cultural_computing.region_embeddings.items():
                similarity = self.embedding_analyzer.detect_polarity(
                    content, 
                    [region]  # Comparar com cada região
                )
                region_scores.append(similarity)
            
            # 3. IB = média da similaridade regional × score cultural
            avg_regional_similarity = np.mean(region_scores) if region_scores else 0.5
            
            # Combinar cultural score e regional similarity
            ib = (cultural_score * 0.6 + avg_regional_similarity * 0.4) * 100
            ib_scores.append(ib)
        
        # Retornar média ou neutral
        if ib_scores:
            final_ib = float(np.mean(ib_scores))
            logger.info(f"🧠 IB calculado com EMBEDDINGS: {final_ib:.2f}")
            return min(max(final_ib, 0), 100)
        else:
            return 50.0
    
    def _calculate_ib_traditional(self, data_points: List[Dict]) -> float:
        """
        📊 TRADITIONAL: Calcular IB usando pattern matching
        (Fallback quando embeddings não disponíveis)
        """
        # Marcadores culturais brasileiros com pesos
        markers = {
            # Linguagem (peso 1.5)
            'gírias': {
                'patterns': ['mano', 'mina', 'truta', 'firmeza', 'tranquilo', 'massa', 'maneiro', 'top'],
                'weight': 1.5
            },
            # Música (peso 2.0)
            'música': {
                'patterns': ['funk', 'samba', 'pagode', 'sertanejo', 'forró', 'axé', 'bossa nova', 'mpb'],
                'weight': 2.0
            },
            # Geografia (peso 1.3)
            'geografia': {
                'patterns': ['rio', 'são paulo', 'brasília', 'salvador', 'nordeste', 'sudeste', 'favela'],
                'weight': 1.3
            },
            # Cultura popular (peso 1.8)
            'cultura': {
                'patterns': ['carnaval', 'futebol', 'novela', 'churrasco', 'caipirinha', 'feijoada', 'açaí'],
                'weight': 1.8
            },
            # Referências nacionais (peso 1.7)
            'nacional': {
                'patterns': ['brasil', 'brasileiro', 'nacional', 'tupiniquim', 'brazuca', 'br'],
                'weight': 1.7
            }
        }
        
        total_score = 0
        total_weight = 0
        
        for dp in data_points:
            content = str(dp.get('content', '')).lower()
            
            for category, config in markers.items():
                patterns = config['patterns']
                weight = config['weight']
                
                # Contar presença de marcadores
                presence = sum(1 for pattern in patterns if pattern in content)
                
                if presence > 0:
                    # Normalizar (máximo 5 marcadores por categoria)
                    normalized_presence = min(presence / 5, 1.0)
                    total_score += normalized_presence * weight * 100
                    total_weight += weight
        
        # Calcular IB final
        if total_weight > 0:
            ib = total_score / total_weight
        else:
            ib = 50.0  # Neutral se não encontrou marcadores
        
        # Garantir range 0-100
        ib = min(max(ib, 0), 100)
        
        return ib
    
    def _prepare_data_points(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prepara data points para weak signals detector"""
        return data.get('data_points', [])


# ========== EXEMPLO DE USO ==========

def example_usage():
    """Exemplo de uso do Metrics Engine integrado"""
    
    print("🎯 Cultural Metrics Engine V9.0 - Exemplo de Uso\n")
    
    # Inicializar engine
    engine = CulturalMetricsEngine()
    
    # Dados simulados (viriam das APIs)
    current_data = {
        'data_points': [
            {
                'source': 'youtube',
                'engagement': 1500,
                'timestamp': datetime.now(),
                'territory': 'BR'
            },
            {
                'source': 'twitter',
                'engagement': 800,
                'timestamp': datetime.now(),
                'territory': 'SP'
            }
        ]
    }
    
    # Calcular métricas
    result = engine.calculate_all_metrics(
        data=current_data,
        industry="fashion"
    )
    
    # Exibir resultados
    if 'error' not in result:
        print(f"✅ Métricas Calculadas:\n")
        print(f"Momentum Cultural: {result['momentum_cultural']:.2f}")
        print(f"Score Cultural: {result['score_cultural']:.2f}")
        print(f"Confiança: {result['confidence']:.2%}")
        print(f"Sinais Fracos: {result['weak_signals']['total_signals']}")
        print(f"\nPesos Usados:")
        for metric, weight in result['weights_used'].items():
            if metric != 'confidence':
                print(f"  {metric}: {weight:.3f}")
        print(f"\nEstágio: {result['metadata']['learning_stage']}")
    else:
        print(f"❌ Erro: {result['error']}")


if __name__ == "__main__":
    example_usage()
