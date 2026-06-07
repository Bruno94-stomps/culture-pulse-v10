#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clustering Engine - Culture Pulse V9.0
Engine de clusterização para detectar públicos emergentes usando HDBSCAN + características culturais

🎯 RESPONSABILIDADES:
- Detectar públicos emergentes usando HDBSCAN (Hierarchical Density-Based Spatial Clustering)
- Agrupar sinais por similaridade demográfica/comportamental/cultural
- Identificar nichos e micro-tendências
- Gerar perfis de audiência com características culturais

📊 ALGORITMOS:
- HDBSCAN: Clustering hierárquico baseado em densidade
- PCA: Redução de dimensionalidade para visualização
- Silhouette Score: Validação da qualidade dos clusters

🔬 ACADEMIC COMPLIANCE:
Papers referenciam clustering para identificar padrões emergentes não-óbvios.
HDBSCAN é superior ao K-means por:
- Não exigir número de clusters predefinido
- Detectar clusters de formas arbitrárias
- Robusto a ruído e outliers
- Hierárquico (multi-escala)
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from dataclasses import dataclass
from collections import Counter, defaultdict
import logging

logger = logging.getLogger(__name__)

try:
    import hdbscan
    HDBSCAN_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ HDBSCAN não disponível. Instale: pip install hdbscan")
    HDBSCAN_AVAILABLE = False

try:
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import silhouette_score
    SKLEARN_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ scikit-learn não disponível")
    SKLEARN_AVAILABLE = False


@dataclass
class AudienceCluster:
    """Representa um cluster de público emergente"""
    cluster_id: int
    profile_name: str
    size: int
    signals: List[str]
    demographic_features: Dict[str, Any]
    behavioral_features: Dict[str, Any]
    cultural_features: Dict[str, Any]
    emergence_score: float
    coherence_score: float  # Silhouette score
    top_platforms: List[str]
    top_keywords: List[str]
    avg_sentiment: float
    growth_velocity: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'cluster_id': self.cluster_id,
            'profile_name': self.profile_name,
            'size': self.size,
            'signals': self.signals,
            'demographic_features': self.demographic_features,
            'behavioral_features': self.behavioral_features,
            'cultural_features': self.cultural_features,
            'emergence_score': self.emergence_score,
            'coherence_score': self.coherence_score,
            'top_platforms': self.top_platforms,
            'top_keywords': self.top_keywords,
            'avg_sentiment': self.avg_sentiment,
            'growth_velocity': self.growth_velocity
        }


class ClusteringEngine:
    """
    Engine de clusterização para detectar públicos emergentes
    Usa HDBSCAN + características culturais para agrupar sinais
    """
    
    def __init__(self, min_cluster_size: int = 3, min_samples: int = 2):
        """
        Inicializa o engine de clusterização
        
        Args:
            min_cluster_size: Tamanho mínimo de um cluster
            min_samples: Número mínimo de amostras em uma vizinhança
        """
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples
        
        if not HDBSCAN_AVAILABLE or not SKLEARN_AVAILABLE:
            logger.warning("⚠️ ClusteringEngine em modo limitado (bibliotecas faltando)")
        
        logger.info("📊 ClusteringEngine inicializado")
    
    def _safe_volume(self, ws) -> float:
        """
        Safely extract volume/engagement metrics from WeakSignal with fallbacks.
        Supports multiple attribute names for robustness against:
        - LLM-generated signals
        - Synthetic data
        - Manual inputs
        - Incomplete data
        
        Args:
            ws: WeakSignal object
            
        Returns:
            float: Volume/engagement value or 0 if not found
        """
        return (
            getattr(ws, 'volume_atual', None)
            or getattr(ws, 'volume', None)
            or getattr(ws, 'engajamento', None)
            or 0
        )
    
    def detect_emerging_audiences(
        self,
        weak_signals: List[Any],
        use_cultural_features: bool = True
    ) -> List[AudienceCluster]:
        """
        Detecta públicos emergentes usando HDBSCAN
        
        Args:
            weak_signals: Lista de sinais fracos
            use_cultural_features: Se deve incluir features culturais
            
        Returns:
            Lista de clusters de público detectados
        """
        if not weak_signals:
            logger.warning("⚠️ Nenhum sinal fornecido para clustering")
            return []
        
        if not HDBSCAN_AVAILABLE or not SKLEARN_AVAILABLE:
            logger.warning("⚠️ HDBSCAN não disponível, usando clustering simples")
            return self._simple_clustering(weak_signals)
        
        try:
            # 1. Extrair features de cada sinal
            features_matrix, signal_metadata = self._extract_features(
                weak_signals,
                use_cultural_features
            )
            
            if features_matrix.shape[0] < self.min_cluster_size:
                logger.warning(f"⚠️ Poucos sinais ({features_matrix.shape[0]}) para clustering robusto")
                return self._simple_clustering(weak_signals)
            
            # 2. Normalizar features
            scaler = StandardScaler()
            features_normalized = scaler.fit_transform(features_matrix)
            
            # 3. Aplicar HDBSCAN
            clusterer = hdbscan.HDBSCAN(
                min_cluster_size=self.min_cluster_size,
                min_samples=self.min_samples,
                metric='euclidean',
                cluster_selection_method='eom'  # Excess of Mass
            )
            
            cluster_labels = clusterer.fit_predict(features_normalized)
            
            # 4. Calcular qualidade dos clusters (silhouette score)
            n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
            
            if n_clusters < 2:
                logger.warning("⚠️ Menos de 2 clusters detectados")
                return self._simple_clustering(weak_signals)
            
            # Calcular silhouette apenas para pontos não-ruído
            valid_indices = cluster_labels != -1
            if valid_indices.sum() > 1:
                silhouette_avg = silhouette_score(
                    features_normalized[valid_indices],
                    cluster_labels[valid_indices]
                )
                logger.info(f"📊 Silhouette Score: {silhouette_avg:.3f} ({n_clusters} clusters)")
            else:
                silhouette_avg = 0.0
            
            # 5. Construir objetos AudienceCluster
            clusters = self._build_clusters(
                weak_signals,
                cluster_labels,
                signal_metadata,
                clusterer.probabilities_ if hasattr(clusterer, 'probabilities_') else None
            )
            
            logger.info(f"✅ {len(clusters)} públicos emergentes detectados")
            return clusters
            
        except Exception as e:
            logger.error(f"❌ Erro no clustering: {e}")
            return self._simple_clustering(weak_signals)
    
    def _extract_features(
        self,
        weak_signals: List[Any],
        use_cultural: bool
    ) -> Tuple[np.ndarray, List[Dict]]:
        """
        Extrai features numéricas de cada sinal para clustering
        
        Returns:
            (features_matrix, signal_metadata)
        """
        features_list = []
        metadata_list = []
        
        for ws in weak_signals:
            features = []
            
            # === FEATURES DEMOGRÁFICAS ===
            # Idade média (inferida da plataforma)
            platform_age_map = {
                'tiktok': 20,
                'instagram': 27,
                'youtube': 35,
                'reddit': 30,
                'twitter': 33,
                'facebook': 40
            }
            avg_age = np.mean([
                platform_age_map.get(p.lower(), 30) 
                for p in ws.plataformas
            ])
            features.append(avg_age)
            
            # Diversidade de plataformas
            features.append(len(ws.plataformas))
            
            # === FEATURES COMPORTAMENTAIS ===
            # Volume de engajamento
            volume = self._safe_volume(ws)
            features.append(np.log1p(volume))  # Log para normalizar
            
            # Velocidade de crescimento
            features.append(ws.growth_velocity if hasattr(ws, 'growth_velocity') else 0.5)
            
            # Sentimento
            features.append(ws.sentiment_positivo if hasattr(ws, 'sentiment_positivo') else 0.5)
            
            # Momentum
            momentum = ws.current_momentum if hasattr(ws, 'current_momentum') else ws.weak_signal_score
            features.append(momentum / 100.0)  # Normalizar para [0, 1]
            
            # === FEATURES CULTURAIS (se habilitado) ===
            if use_cultural:
                from core.intelligence.research_refiner import CULTURAL_CIRCLES
                # Ressonância em círculos culturais (V9.9 - Dinâmico)
                max_circles = len(CULTURAL_CIRCLES) or 16.0
                if hasattr(ws, 'cultural_circles') and ws.cultural_circles:
                    features.append(len(ws.cultural_circles) / max_circles)
                else:
                    features.append(0.0)
                
                # Autenticidade cultural
                if hasattr(ws, 'authenticity_score'):
                    features.append(ws.authenticity_score / 100.0)
                else:
                    features.append(0.5)
                
                # Tensões culturais
                if hasattr(ws, 'tensao_media'):
                    features.append(ws.tensao_media / 100.0)
                else:
                    features.append(0.0)
            
            features_list.append(features)
            
            # Metadata para reconstruir clusters depois
            volume = self._safe_volume(ws)
            metadata_list.append({
                'termo': ws.termo,
                'plataformas': ws.plataformas,
                'volume': volume,
                'sentiment': ws.sentiment_positivo if hasattr(ws, 'sentiment_positivo') else 0.5,
                'growth_velocity': ws.growth_velocity if hasattr(ws, 'growth_velocity') else 0.5,
                'contextos': ws.contextos if hasattr(ws, 'contextos') else []
            })
        
        return np.array(features_list), metadata_list
    
    def _build_clusters(
        self,
        weak_signals: List[Any],
        cluster_labels: np.ndarray,
        signal_metadata: List[Dict],
        probabilities: Optional[np.ndarray]
    ) -> List[AudienceCluster]:
        """
        Constrói objetos AudienceCluster a partir dos labels do HDBSCAN
        """
        clusters = []
        
        # Agrupar sinais por cluster
        cluster_dict = defaultdict(list)
        for i, label in enumerate(cluster_labels):
            if label != -1:  # Ignorar ruído (-1)
                cluster_dict[label].append((i, weak_signals[i], signal_metadata[i]))
        
        # Construir cada cluster
        for cluster_id, members in cluster_dict.items():
            indices, signals, metadata = zip(*members)
            
            # Calcular features agregadas
            all_platforms = []
            all_keywords = []
            sentiments = []
            velocities = []
            volumes = []
            
            for meta in metadata:
                all_platforms.extend(meta['plataformas'])
                all_keywords.append(meta['termo'])
                sentiments.append(meta['sentiment'])
                velocities.append(meta['growth_velocity'])
                volumes.append(meta['volume'])
            
            # Top plataformas
            platform_counts = Counter(all_platforms)
            top_platforms = [p for p, _ in platform_counts.most_common(3)]
            
            # Características demográficas
            demographic_features = {
                'platform_diversity': len(set(all_platforms)),
                'primary_platforms': top_platforms,
                'age_profile': self._infer_age_profile(top_platforms)
            }
            
            # Características comportamentais
            behavioral_features = {
                'avg_engagement': np.mean(volumes),
                'avg_growth_velocity': np.mean(velocities),
                'engagement_variance': np.std(volumes),
                'total_signals': len(signals)
            }
            
            # Características culturais
            cultural_features = {
                'avg_sentiment': np.mean(sentiments),
                'sentiment_polarity': 'positive' if np.mean(sentiments) > 0.6 else 'neutral' if np.mean(sentiments) > 0.4 else 'negative'
            }
            
            # Score de emergência
            emergence_score = (
                len(signals) * 0.3 +  # Tamanho do cluster
                np.mean(velocities) * 100 * 0.4 +  # Velocidade de crescimento
                len(set(all_platforms)) * 5 * 0.2 +  # Diversidade de plataformas
                np.mean(sentiments) * 100 * 0.1  # Sentimento
            )
            
            # Coherence score (silhouette para este cluster)
            if probabilities is not None:
                cluster_probabilities = [probabilities[i] for i in indices]
                coherence_score = np.mean(cluster_probabilities) * 100
            else:
                coherence_score = 75.0  # Default
            
            # Nome do perfil
            profile_name = self._generate_profile_name(
                demographic_features,
                behavioral_features,
                cultural_features
            )
            
            cluster = AudienceCluster(
                cluster_id=cluster_id,
                profile_name=profile_name,
                size=len(signals),
                signals=all_keywords,
                demographic_features=demographic_features,
                behavioral_features=behavioral_features,
                cultural_features=cultural_features,
                emergence_score=emergence_score,
                coherence_score=coherence_score,
                top_platforms=top_platforms,
                top_keywords=all_keywords[:5],
                avg_sentiment=np.mean(sentiments),
                growth_velocity=np.mean(velocities)
            )
            
            clusters.append(cluster)
        
        # Ordenar por emergence score
        clusters.sort(key=lambda c: c.emergence_score, reverse=True)
        
        return clusters
    
    def _infer_age_profile(self, platforms: List[str]) -> str:
        """Infere perfil de idade baseado nas plataformas"""
        platform_age_profiles = {
            'tiktok': 'Gen Z (16-24)',
            'instagram': 'Millennials (25-34)',
            'youtube': 'Multi-generational (18-45)',
            'reddit': 'Tech-savvy (20-35)',
            'twitter': 'Early Adopters (25-40)',
            'facebook': 'Mature (35+)'
        }
        
        if not platforms:
            return 'Unknown'
        
        # Usar a plataforma mais comum
        main_platform = platforms[0].lower() if platforms else ''
        return platform_age_profiles.get(main_platform, 'Multi-generational')
    
    def _generate_profile_name(
        self,
        demo: Dict,
        behav: Dict,
        cultural: Dict
    ) -> str:
        """Gera nome descritivo para o perfil de público"""
        age_profile = demo.get('age_profile', 'Unknown')
        sentiment = cultural.get('sentiment_polarity', 'neutral')
        
        # Adjetivos baseados em comportamento
        if behav['avg_growth_velocity'] > 0.7:
            intensity = 'Highly Active'
        elif behav['avg_growth_velocity'] > 0.5:
            intensity = 'Active'
        else:
            intensity = 'Emerging'
        
        # Sentiment modifier
        sentiment_mod = {
            'positive': 'Enthusiastic',
            'neutral': 'Curious',
            'negative': 'Critical'
        }.get(sentiment, 'Interested')
        
        return f"{intensity} {sentiment_mod} {age_profile}"
    
    def _simple_clustering(self, weak_signals: List[Any]) -> List[AudienceCluster]:
        """
        Fallback: clustering simples baseado em plataformas
        Usado quando HDBSCAN não está disponível ou falha
        """
        logger.info("📊 Usando clustering simplificado (baseado em plataformas)")
        
        # Agrupar por plataforma principal
        platform_groups = defaultdict(list)
        for ws in weak_signals:
            main_platform = ws.plataformas[0] if ws.plataformas else 'unknown'
            platform_groups[main_platform].append(ws)
        
        clusters = []
        for cluster_id, (platform, signals) in enumerate(platform_groups.items()):
            if len(signals) < 2:
                continue
            
            # Calcular métricas agregadas
            avg_sentiment = np.mean([
                ws.sentiment_positivo if hasattr(ws, 'sentiment_positivo') else 0.5
                for ws in signals
            ])
            
            avg_velocity = np.mean([
                ws.growth_velocity if hasattr(ws, 'growth_velocity') else 0.5
                for ws in signals
            ])
            
            total_volume = sum([
                self._safe_volume(ws)
                for ws in signals
            ])
            
            cluster = AudienceCluster(
                cluster_id=cluster_id,
                profile_name=f"{platform.title()} Community",
                size=len(signals),
                signals=[ws.termo for ws in signals],
                demographic_features={'platform': platform},
                behavioral_features={'avg_engagement': total_volume / len(signals)},
                cultural_features={'avg_sentiment': avg_sentiment},
                emergence_score=len(signals) * 20 + avg_velocity * 30,
                coherence_score=65.0,
                top_platforms=[platform],
                top_keywords=[ws.termo for ws in signals[:5]],
                avg_sentiment=avg_sentiment,
                growth_velocity=avg_velocity
            )
            
            clusters.append(cluster)
        
        return sorted(clusters, key=lambda c: c.emergence_score, reverse=True)
