#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ADVANCED PATTERN ANALYZER V8.0
============================
Sistema avançado de análise de padrões culturais

Funcionalidades:
- Cross-Brand Pattern Detection
- Anomaly Detection (Isolation Forest)
- Cross-Correlation Analysis
- Intelligent Clustering
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN, KMeans
from sklearn.metrics import silhouette_score
from scipy import stats
from scipy.signal import correlate
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from datetime import datetime
import joblib
from core.technical.anomaly_detection import AnomalyDetection

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CrossBrandPattern:
    """Padrão identificado entre marcas"""
    pattern_id: str
    brands_involved: List[str]
    pattern_type: str
    strength: float
    confidence: float
    temporal_span: Tuple[datetime, datetime]
    key_indicators: Dict[str, float]
    cultural_context: str
    recommendations: List[str]

# Removido dataclass CulturalAnomaly - usando do módulo anomaly_detection.py

@dataclass
class CrossCorrelation:
    """Correlação entre sinais culturais"""
    signal_pair: Tuple[str, str]
    correlation_score: float
    lag: int
    significance: float
    stability: float
    insights: List[str]
    implications: List[str]

@dataclass
class ContentCluster:
    """Cluster de conteúdo similar"""
    cluster_id: str
    size: int
    centroid_features: Dict[str, float]
    coherence_score: float
    representative_items: List[str]
    cultural_theme: str
    key_characteristics: List[str]

class AdvancedPatternAnalyzer:
    """Analisador avançado de padrões culturais"""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Inicializar analisador
        
        Args:
            model_path: Caminho para modelos
        """
        self.scaler = StandardScaler()
        self.dbscan = DBSCAN(
            eps=0.5,
            min_samples=5
        )
        self.kmeans = KMeans(
            n_clusters=5,
            random_state=42
        )
        self.anomaly_detector = AnomalyDetection()
        
    def analyze_cross_brand_patterns(
        self,
        brand_data: Dict[str, pd.DataFrame],
        metrics: List[str],
        time_window: str = "30D"
    ) -> List[CrossBrandPattern]:
        """
        Detectar padrões entre marcas
        
        Args:
            brand_data: Dados históricos por marca
            metrics: Métricas para análise
            time_window: Janela temporal
            
        Returns:
            Lista de padrões identificados
        """
        patterns = []
        
        # Preparar dados
        aligned_data = self._align_brand_data(brand_data, metrics, time_window)
        
        # Detectar correlações
        correlations = self._detect_brand_correlations(aligned_data)
        
        # Identificar padrões comuns
        common_patterns = self._identify_common_patterns(aligned_data)
        
        # Analisar movimentos sincronizados
        synchronized_moves = self._analyze_synchronized_movements(
            aligned_data,
            correlations
        )
        
        # Consolidar padrões
        for pattern_type, pattern_data in [
            ("correlation", correlations),
            ("common", common_patterns),
            ("synchronized", synchronized_moves)
        ]:
            for pattern in pattern_data:
                pattern_obj = CrossBrandPattern(
                    pattern_id=f"pattern_{len(patterns)+1}",
                    brands_involved=pattern["brands"],
                    pattern_type=pattern_type,
                    strength=pattern["strength"],
                    confidence=pattern["confidence"],
                    temporal_span=(
                        pattern["start_date"],
                        pattern["end_date"]
                    ),
                    key_indicators=pattern["indicators"],
                    cultural_context=pattern["context"],
                    recommendations=pattern["recommendations"]
                )
                patterns.append(pattern_obj)
        
        return patterns
        
    def detect_anomalies(
        self,
        time_series: pd.DataFrame,
        sensitivity: float = 0.1
    ):
        """
        Detectar anomalias usando o módulo AnomalyDetection
        
        Args:
            time_series: Série temporal de métricas
            sensitivity: Sensibilidade da detecção
            
        Returns:
            Lista de anomalias detectadas
        """
        return self.anomaly_detector.detect_anomalies(
            time_series,
            list(time_series.columns),
            sensitivity
        )
        
    def analyze_cross_correlations(
        self,
        signals: Dict[str, pd.Series],
        max_lag: int = 30
    ) -> List[CrossCorrelation]:
        """
        Analisar correlações entre sinais culturais
        
        Args:
            signals: Dicionário de séries temporais
            max_lag: Máximo lag para análise
            
        Returns:
            Lista de correlações identificadas
        """
        correlations = []
        
        # Analisar cada par de sinais
        signal_names = list(signals.keys())
        for i in range(len(signal_names)):
            for j in range(i + 1, len(signal_names)):
                sig1_name = signal_names[i]
                sig2_name = signal_names[j]
                
                # Calcular correlação cruzada
                sig1 = signals[sig1_name]
                sig2 = signals[sig2_name]
                
                correlation, lag = self._calculate_cross_correlation(
                    sig1,
                    sig2,
                    max_lag
                )
                
                # Calcular significância
                significance = self._calculate_significance(correlation)
                
                # Calcular estabilidade
                stability = self._calculate_correlation_stability(
                    sig1,
                    sig2,
                    correlation
                )
                
                # Gerar insights
                insights = self._generate_correlation_insights(
                    sig1_name,
                    sig2_name,
                    correlation,
                    lag
                )
                
                # Identificar implicações
                implications = self._identify_correlation_implications(
                    correlation,
                    significance,
                    stability
                )
                
                correlations.append(CrossCorrelation(
                    signal_pair=(sig1_name, sig2_name),
                    correlation_score=correlation,
                    lag=lag,
                    significance=significance,
                    stability=stability,
                    insights=insights,
                    implications=implications
                ))
        
        return correlations
        
    def cluster_content(
        self,
        content_data: pd.DataFrame,
        n_clusters: Optional[int] = None
    ) -> List[ContentCluster]:
        """
        Realizar clustering inteligente de conteúdo
        
        Args:
            content_data: DataFrame com features do conteúdo
            n_clusters: Número de clusters (opcional)
            
        Returns:
            Lista de clusters identificados
        """
        clusters = []
        
        # Preparar dados
        X = self.scaler.fit_transform(content_data)
        
        # Determinar número ideal de clusters se não fornecido
        if n_clusters is None:
            n_clusters = self._determine_optimal_clusters(X)
            
        # Realizar clustering
        self.kmeans.set_params(n_clusters=n_clusters)
        labels = self.kmeans.fit_predict(X)
        
        # Avaliar clusters
        for i in range(n_clusters):
            cluster_mask = labels == i
            cluster_data = content_data[cluster_mask]
            
            # Calcular centroide
            centroid = self._calculate_cluster_centroid(cluster_data)
            
            # Avaliar coerência
            coherence = self._calculate_cluster_coherence(
                cluster_data,
                centroid
            )
            
            # Identificar itens representativos
            representatives = self._find_representative_items(
                cluster_data,
                centroid
            )
            
            # Identificar tema cultural
            theme = self._identify_cultural_theme(
                cluster_data,
                centroid
            )
            
            # Extrair características principais
            characteristics = self._extract_key_characteristics(
                cluster_data,
                centroid
            )
            
            clusters.append(ContentCluster(
                cluster_id=f"cluster_{i+1}",
                size=len(cluster_data),
                centroid_features=centroid,
                coherence_score=coherence,
                representative_items=representatives,
                cultural_theme=theme,
                key_characteristics=characteristics
            ))
        
        return clusters
        
    def _align_brand_data(
        self,
        brand_data: Dict[str, pd.DataFrame],
        metrics: List[str],
        time_window: str
    ) -> pd.DataFrame:
        """Alinhar dados de diferentes marcas"""
        aligned_data = {}
        
        for brand, data in brand_data.items():
            # Resample e alinhar timestamps
            resampled = data[metrics].resample(time_window).mean()
            aligned_data[brand] = resampled
            
        return pd.concat(aligned_data, axis=1)
        
    def _detect_brand_correlations(
        self,
        aligned_data: pd.DataFrame
    ) -> List[Dict]:
        """Detectar correlações entre marcas"""
        correlations = []
        brands = aligned_data.columns.levels[0] if isinstance(aligned_data.columns, pd.MultiIndex) else [c.split('_')[0] for c in aligned_data.columns]
        
        for i, brand1 in enumerate(brands):
            for brand2 in brands[i+1:]:
                # Extrair dados das marcas
                brand1_data = aligned_data[brand1] if isinstance(aligned_data.columns, pd.MultiIndex) else aligned_data.filter(like=f"{brand1}_")
                brand2_data = aligned_data[brand2] if isinstance(aligned_data.columns, pd.MultiIndex) else aligned_data.filter(like=f"{brand2}_")
                
                # Calcular correlação entre métricas
                correlation_matrix = brand1_data.corrwith(brand2_data)
                avg_correlation = correlation_matrix.mean()
                
                # Calcular força e confiança
                strength = abs(avg_correlation)
                confidence = self._calculate_correlation_confidence(correlation_matrix)
                
                if strength > 0.3:  # Limiar mínimo de correlação
                    correlations.append({
                        "brands": [brand1, brand2],
                        "strength": strength,
                        "confidence": confidence,
                        "start_date": aligned_data.index[0],
                        "end_date": aligned_data.index[-1],
                        "indicators": correlation_matrix.to_dict(),
                        "context": self._generate_correlation_context(brand1, brand2, correlation_matrix),
                        "recommendations": self._generate_correlation_recommendations(brand1, brand2, correlation_matrix)
                    })
        
        return correlations
        
    def _identify_common_patterns(
        self,
        aligned_data: pd.DataFrame
    ) -> List[Dict]:
        """Identificar padrões comuns"""
        patterns = []
        
        # Detectar tendências comuns
        trends = self._detect_common_trends(aligned_data)
        
        # Detectar sazonalidades
        seasonalities = self._detect_seasonalities(aligned_data)
        
        # Detectar comportamentos cíclicos
        cycles = self._detect_cycles(aligned_data)
        
        # Consolidar padrões
        for trend in trends:
            patterns.append({
                "brands": trend["brands"],
                "pattern_type": "trend",
                "strength": trend["strength"],
                "confidence": trend["confidence"],
                "start_date": trend["start_date"],
                "end_date": trend["end_date"],
                "indicators": trend["indicators"],
                "context": f"Tendência comum identificada: {trend['description']}",
                "recommendations": trend["recommendations"]
            })
            
        for seasonality in seasonalities:
            patterns.append({
                "brands": seasonality["brands"],
                "pattern_type": "seasonality",
                "strength": seasonality["strength"],
                "confidence": seasonality["confidence"],
                "start_date": seasonality["start_date"],
                "end_date": seasonality["end_date"],
                "indicators": seasonality["indicators"],
                "context": f"Padrão sazonal: {seasonality['description']}",
                "recommendations": seasonality["recommendations"]
            })
            
        for cycle in cycles:
            patterns.append({
                "brands": cycle["brands"],
                "pattern_type": "cycle",
                "strength": cycle["strength"],
                "confidence": cycle["confidence"],
                "start_date": cycle["start_date"],
                "end_date": cycle["end_date"],
                "indicators": cycle["indicators"],
                "context": f"Ciclo identificado: {cycle['description']}",
                "recommendations": cycle["recommendations"]
            })
            
        return patterns
        
    def _detect_common_trends(self, data: pd.DataFrame) -> List[Dict]:
        """Detectar tendências comuns entre marcas"""
        trends = []
        brands = data.columns.levels[0] if isinstance(data.columns, pd.MultiIndex) else [c.split('_')[0] for c in data.columns]
        
        for metric in data.columns.levels[1] if isinstance(data.columns, pd.MultiIndex) else set(c.split('_')[1] for c in data.columns):
            trend_data = {}
            for brand in brands:
                series = data[brand][metric] if isinstance(data.columns, pd.MultiIndex) else data[f"{brand}_{metric}"]
                trend_data[brand] = self._calculate_trend(series)
            
            similar_trends = self._group_similar_trends(trend_data)
            
            for group in similar_trends:
                if len(group["brands"]) > 1:
                    trends.append({
                        "brands": group["brands"],
                        "strength": group["similarity"],
                        "confidence": group["confidence"],
                        "start_date": data.index[0],
                        "end_date": data.index[-1],
                        "indicators": {metric: group["trend_stats"]},
                        "description": group["description"],
                        "recommendations": self._generate_trend_recommendations(group)
                    })
        
        return trends
        
    def _detect_seasonalities(self, data: pd.DataFrame) -> List[Dict]:
        """Detectar padrões sazonais"""
        seasonalities = []
        brands = data.columns.levels[0] if isinstance(data.columns, pd.MultiIndex) else [c.split('_')[0] for c in data.columns]
        
        for metric in data.columns.levels[1] if isinstance(data.columns, pd.MultiIndex) else set(c.split('_')[1] for c in data.columns):
            for period in ["W", "M", "Q"]:  # Semanal, Mensal, Trimestral
                seasonal_patterns = {}
                
                for brand in brands:
                    series = data[brand][metric] if isinstance(data.columns, pd.MultiIndex) else data[f"{brand}_{metric}"]
                    pattern = self._analyze_seasonality(series, period)
                    if pattern["strength"] > 0.3:
                        seasonal_patterns[brand] = pattern
                
                similar_patterns = self._group_similar_seasonalities(seasonal_patterns)
                
                for group in similar_patterns:
                    if len(group["brands"]) > 1:
                        seasonalities.append({
                            "brands": group["brands"],
                            "strength": group["similarity"],
                            "confidence": group["confidence"],
                            "start_date": data.index[0],
                            "end_date": data.index[-1],
                            "indicators": {metric: group["seasonal_stats"]},
                            "description": group["description"],
                            "recommendations": self._generate_seasonality_recommendations(group)
                        })
        
        return seasonalities
        
    def _detect_cycles(self, data: pd.DataFrame) -> List[Dict]:
        """Detectar padrões cíclicos"""
        cycles = []
        brands = data.columns.levels[0] if isinstance(data.columns, pd.MultiIndex) else [c.split('_')[0] for c in data.columns]
        
        for metric in data.columns.levels[1] if isinstance(data.columns, pd.MultiIndex) else set(c.split('_')[1] for c in data.columns):
            cycle_patterns = {}
            
            for brand in brands:
                series = data[brand][metric] if isinstance(data.columns, pd.MultiIndex) else data[f"{brand}_{metric}"]
                pattern = self._analyze_cycles(series)
                if pattern["strength"] > 0.3:
                    cycle_patterns[brand] = pattern
            
            similar_cycles = self._group_similar_cycles(cycle_patterns)
            
            for group in similar_cycles:
                if len(group["brands"]) > 1:
                    cycles.append({
                        "brands": group["brands"],
                        "strength": group["similarity"],
                        "confidence": group["confidence"],
                        "start_date": data.index[0],
                        "end_date": data.index[-1],
                        "indicators": {metric: group["cycle_stats"]},
                        "description": group["description"],
                        "recommendations": self._generate_cycle_recommendations(group)
                    })
        
        return cycles
        
    def _analyze_synchronized_movements(
        self,
        aligned_data: pd.DataFrame,
        correlations: List[Dict]
    ) -> List[Dict]:
        """Analisar movimentos sincronizados"""
        movements = []
        
        # Implementar análise de movimentos
        # TODO: Implementar lógica real
        
        return movements
        
    # Removidas funções relacionadas a anomalias - usando módulo anomaly_detection.py
        
    def _calculate_cross_correlation(
        self,
        sig1: pd.Series,
        sig2: pd.Series,
        max_lag: int
    ) -> Tuple[float, int]:
        """Calcular correlação cruzada"""
        # Normalizar sinais
        sig1_norm = (sig1 - sig1.mean()) / sig1.std()
        sig2_norm = (sig2 - sig2.mean()) / sig2.std()
        
        # Calcular correlação
        corr = correlate(sig1_norm, sig2_norm, mode='full')
        lags = np.arange(-len(sig1) + 1, len(sig1))
        
        # Encontrar lag ótimo
        max_corr_idx = np.argmax(np.abs(corr))
        max_lag = lags[max_corr_idx]
        
        # Limitar ao max_lag especificado
        if abs(max_lag) > max_lag:
            max_lag = max_lag if max_lag > 0 else -max_lag
            
        return corr[max_corr_idx], max_lag
        
    def _calculate_significance(self, correlation: float) -> float:
        """Calcular significância estatística"""
        # Implementar cálculo de significância
        # TODO: Implementar lógica real
        return 0.95
        
    def _calculate_correlation_stability(
        self,
        sig1: pd.Series,
        sig2: pd.Series,
        correlation: float
    ) -> float:
        """Calcular estabilidade da correlação"""
        # Implementar cálculo de estabilidade
        # TODO: Implementar lógica real
        return 0.8
        
    def _generate_correlation_insights(
        self,
        sig1_name: str,
        sig2_name: str,
        correlation: float,
        lag: int
    ) -> List[str]:
        """Gerar insights sobre correlação"""
        insights = []
        
        # Analisar força da correlação
        if abs(correlation) > 0.7:
            strength = "forte"
        elif abs(correlation) > 0.4:
            strength = "moderada"
        else:
            strength = "fraca"
            
        # Analisar direção
        direction = "positiva" if correlation > 0 else "negativa"
        
        # Analisar lag temporal
        if lag == 0:
            timing = "simultâneo"
        else:
            lead_signal = sig1_name if lag > 0 else sig2_name
            lag_signal = sig2_name if lag > 0 else sig1_name
            timing = f"com {abs(lag)} períodos de atraso, onde {lead_signal} lidera {lag_signal}"
            
        insights.append(f"Correlação {strength} e {direction} {timing}")
        
        # Insights específicos baseados na força
        if abs(correlation) > 0.7:
            insights.append(f"Alta sincronicidade entre {sig1_name} e {sig2_name}")
            insights.append("Potencial para estratégias coordenadas")
        elif abs(correlation) > 0.4:
            insights.append(f"Padrões compartilhados entre {sig1_name} e {sig2_name}")
            insights.append("Oportunidade para análise conjunta")
            
        # Insights baseados no lag
        if abs(lag) > 0:
            insights.append(f"Potencial relação causal ou influência direcional")
            insights.append(f"Oportunidade para previsão usando {lead_signal}")
            
        return insights
        
    def _identify_correlation_implications(
        self,
        correlation: float,
        significance: float,
        stability: float
    ) -> List[str]:
        """Identificar implicações da correlação"""
        implications = []
        
        # Implementar identificação de implicações
        # TODO: Implementar lógica real
        
        return implications
        
    def _determine_optimal_clusters(
        self,
        X: np.ndarray,
        max_clusters: int = 10
    ) -> int:
        """Determinar número ótimo de clusters"""
        best_score = -1
        best_n = 2
        
        for n in range(2, min(len(X), max_clusters + 1)):
            kmeans = KMeans(n_clusters=n, random_state=42)
            labels = kmeans.fit_predict(X)
            score = silhouette_score(X, labels)
            
            if score > best_score:
                best_score = score
                best_n = n
                
        return best_n
        
    def _calculate_cluster_centroid(
        self,
        cluster_data: pd.DataFrame
    ) -> Dict[str, float]:
        """Calcular centroide do cluster"""
        return cluster_data.mean().to_dict()
        
    def _calculate_cluster_coherence(
        self,
        cluster_data: pd.DataFrame,
        centroid: Dict[str, float]
    ) -> float:
        """Calcular coerência do cluster"""
        distances = []
        for _, row in cluster_data.iterrows():
            dist = np.sqrt(sum(
                (row[k] - v) ** 2 for k, v in centroid.items()
            ))
            distances.append(dist)
            
        return 1 / (1 + np.mean(distances))
        
    def _find_representative_items(
        self,
        cluster_data: pd.DataFrame,
        centroid: Dict[str, float]
    ) -> List[str]:
        """Encontrar itens mais representativos"""
        distances = []
        
        # Calcular distância de cada item ao centroide
        for idx, row in cluster_data.iterrows():
            dist = np.sqrt(sum(
                (row[k] - v) ** 2 for k, v in centroid.items()
            ))
            distances.append((idx, dist))
            
        # Ordenar por proximidade ao centroide
        distances.sort(key=lambda x: x[1])
        
        # Retornar os 5 itens mais próximos
        return [str(idx) for idx, _ in distances[:5]]
        
    def _identify_cultural_theme(
        self,
        cluster_data: pd.DataFrame,
        centroid: Dict[str, float]
    ) -> str:
        """Identificar tema cultural do cluster"""
        # Análise das principais características
        main_features = sorted(
            centroid.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:3]
        
        # Mapeamento de temas culturais
        theme_mapping = {
            "engajamento": ["interacao", "comentarios", "compartilhamentos"],
            "identidade": ["autenticidade", "valores", "tradicao"],
            "inovacao": ["tecnologia", "mudanca", "tendencias"],
            "comunidade": ["colaboracao", "social", "participacao"],
            "lifestyle": ["estilo", "consumo", "aspiracoes"],
            "sustentabilidade": ["ambiental", "social", "responsabilidade"]
        }
        
        # Pontuação para cada tema
        theme_scores = {theme: 0.0 for theme in theme_mapping}
        
        # Calcular pontuação de cada tema
        for feature, value in main_features:
            for theme, keywords in theme_mapping.items():
                if any(keyword in feature.lower() for keyword in keywords):
                    theme_scores[theme] += abs(value)
                    
        # Identificar tema dominante
        dominant_theme = max(theme_scores.items(), key=lambda x: x[1])[0]
        
        return f"Tema Cultural: {dominant_theme.title()}"
        
    def _extract_key_characteristics(
        self,
        cluster_data: pd.DataFrame,
        centroid: Dict[str, float]
    ) -> List[str]:
        """Extrair características principais"""
        characteristics = []
        
        # Análise de valores centrais
        for feature, value in sorted(
            centroid.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:5]:
            direction = "alto" if value > 0 else "baixo"
            characteristics.append(f"{feature}: Nível {direction} ({abs(value):.2f})")
            
        # Análise de dispersão
        for feature in centroid.keys():
            std = cluster_data[feature].std()
            if std < 0.1:
                characteristics.append(f"{feature}: Muito consistente")
            elif std > 0.5:
                characteristics.append(f"{feature}: Alta variabilidade")
                
        # Análise de correlações internas
        correlations = cluster_data.corr()
        strong_correlations = []
        
        for i in range(len(correlations.columns)):
            for j in range(i + 1, len(correlations.columns)):
                if abs(correlations.iloc[i, j]) > 0.7:
                    feature1 = correlations.columns[i]
                    feature2 = correlations.columns[j]
                    relation = "positiva" if correlations.iloc[i, j] > 0 else "negativa"
                    strong_correlations.append(
                        f"Forte correlação {relation} entre {feature1} e {feature2}"
                    )
                    
        characteristics.extend(strong_correlations[:3])
        
        return characteristics