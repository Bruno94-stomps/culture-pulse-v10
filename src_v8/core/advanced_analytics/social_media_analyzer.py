#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SOCIAL MEDIA ANALYZER V8.0
=========================
Analisador de Redes Sociais para o Culture Pulse

Funcionalidades principais:
- Análise de engajamento
- Análise de sentimento
- Detecção de tendências
- Métricas culturais em redes sociais
- Cache de resultados

Integração: Culture Pulse V8.0 MVP
"""

from typing import Dict, List, Optional, Union, TYPE_CHECKING
from dataclasses import dataclass
from datetime import datetime
import json
import hashlib
from pathlib import Path
import logging

if TYPE_CHECKING:
    from ...dormant.engines.cultural_asset_system.cultural_asset_generator import CulturalAsset

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SocialMediaMetrics:
    """Estrutura para métricas de redes sociais"""
    platform: str
    engagement_rate: float
    sentiment_score: float
    cultural_relevance: float
    trend_alignment: float
    regional_performance: Dict[str, float]
    demographic_reach: Dict[str, float]
    timestamp: datetime

@dataclass
class SocialTrend:
    """Estrutura para tendências identificadas"""
    trend_id: str
    name: str
    strength: float  # 0-1
    platforms: List[str]
    regions: List[str]
    sentiment: float  # -1 to 1
    related_topics: List[str]
    first_detected: datetime
    last_updated: datetime

class SocialMediaAnalyzer:
    """Analisador principal de redes sociais"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Inicializar analisador com cache opcional"""
        self.cache_dir = Path(cache_dir) if cache_dir else Path("cache/social_analysis")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurações de cache
        self.cache_config = {
            "enabled": True,
            "ttl_seconds": 86400,  # 24 horas
            "max_size_mb": 100,
            "min_hits": 2  # Número mínimo de hits para manter em cache
        }
        
        # Inicializar métricas e limpeza de cache
        self._initialize_metrics()
        self._cleanup_old_cache()
        
    def _initialize_metrics(self) -> None:
        """Inicializar sistemas de métricas"""
        self.engagement_weights = {
            "likes": 1.0,
            "comments": 2.0,
            "shares": 3.0,
            "saves": 2.5,
            "clicks": 1.5
        }
        
        self.sentiment_thresholds = {
            "very_negative": -0.8,
            "negative": -0.3,
            "neutral": 0.3,
            "positive": 0.8,
            "very_positive": 1.0
        }
        
        self.trend_detection = {
            "min_mentions": 100,
            "growth_rate_threshold": 1.5,
            "timeframe_hours": 24,
            "relevance_threshold": 0.6
        }
        
    def analyze_social_presence(
        self,
        brand_name: str,
        platforms: List[str],
        timeframe: str = "7d"
    ) -> Dict[str, SocialMediaMetrics]:
        """
        Analisar presença em redes sociais
        
        Args:
            brand_name: Nome da marca
            platforms: Lista de plataformas para análise
            timeframe: Período de análise (1d, 7d, 30d, etc)
            
        Returns:
            Dict com métricas por plataforma
        """
        cache_key = self._generate_cache_key(f"presence_{brand_name}_{timeframe}")
        cached_result = self._get_cached_result(cache_key)
        
        if cached_result:
            return cached_result
            
        metrics = {}
        for platform in platforms:
            # Simular coleta de dados da plataforma
            raw_metrics = self._collect_platform_metrics(platform, brand_name, timeframe)
            
            # Calcular métricas de engajamento
            engagement_rate = self._calculate_engagement_rate(raw_metrics)
            
            # Análise de sentimento
            sentiment_score = self._analyze_sentiment(raw_metrics.get("comments", []))
            
            # Relevância cultural
            cultural_relevance = self._assess_cultural_relevance(
                platform, raw_metrics, brand_name
            )
            
            # Alinhamento com tendências
            trend_alignment = self._calculate_trend_alignment(
                platform, raw_metrics, brand_name
            )
            
            # Performance regional
            regional_performance = self._analyze_regional_performance(
                platform, raw_metrics
            )
            
            # Alcance demográfico
            demographic_reach = self._analyze_demographic_reach(
                platform, raw_metrics
            )
            
            metrics[platform] = SocialMediaMetrics(
                platform=platform,
                engagement_rate=engagement_rate,
                sentiment_score=sentiment_score,
                cultural_relevance=cultural_relevance,
                trend_alignment=trend_alignment,
                regional_performance=regional_performance,
                demographic_reach=demographic_reach,
                timestamp=datetime.now()
            )
            
        self._cache_result(cache_key, metrics)
        return metrics
        
    def detect_trends(
        self,
        keywords: List[str],
        platforms: List[str],
        min_strength: float = 0.3
    ) -> List[SocialTrend]:
        """
        Detectar tendências relacionadas nas redes sociais
        
        Args:
            keywords: Palavras-chave para monitorar
            platforms: Plataformas para análise
            min_strength: Força mínima da tendência (0-1)
            
        Returns:
            Lista de tendências detectadas
        """
        cache_key = self._generate_cache_key(f"trends_{'_'.join(keywords)}")
        cached_result = self._get_cached_result(cache_key)
        
        if cached_result:
            return cached_result
            
        trends = []
        
        for platform in platforms:
            # Coletar menções e hashtags relacionadas
            mentions = self._collect_platform_mentions(platform, keywords)
            
            # Analisar crescimento e força da tendência
            for topic, data in mentions.items():
                growth_rate = self._calculate_growth_rate(data)
                
                if growth_rate >= self.trend_detection["growth_rate_threshold"]:
                    trend_strength = self._calculate_trend_strength(
                        data,
                        growth_rate
                    )
                    
                    if trend_strength >= min_strength:
                        trend = SocialTrend(
                            trend_id=f"trend_{len(trends)+1}",
                            name=topic,
                            strength=trend_strength,
                            platforms=[platform],
                            regions=self._detect_trend_regions(data),
                            sentiment=self._analyze_sentiment(data.get("comments", [])),
                            related_topics=self._find_related_topics(topic, data),
                            first_detected=data["first_seen"],
                            last_updated=datetime.now()
                        )
                        trends.append(trend)
        
        self._cache_result(cache_key, trends)
        return trends
        
    def analyze_cultural_engagement(
        self,
        content: str,
        target_regions: List[str],
        target_demographics: List[str]
    ) -> Dict[str, float]:
        """
        Analisar engajamento cultural em conteúdo social
        
        Args:
            content: Conteúdo para análise
            target_regions: Regiões alvo
            target_demographics: Demografia alvo
            
        Returns:
            Dict com scores de engajamento cultural
        """
        cache_key = self._generate_cache_key(f"engagement_{hashlib.md5(content.encode()).hexdigest()}")
        cached_result = self._get_cached_result(cache_key)
        
        if cached_result:
            return cached_result
            
        # Análise do conteúdo
        content_metrics = self._analyze_content_metrics(content)
        
        # Calcular relevância cultural
        cultural_relevance = self._calculate_cultural_relevance(
            content_metrics,
            target_regions,
            target_demographics
        )
        
        # Avaliar adequação regional
        regional_fit = self._evaluate_regional_fit(
            content_metrics,
            target_regions
        )
        
        # Calcular alinhamento demográfico
        demographic_alignment = self._calculate_demographic_alignment(
            content_metrics,
            target_demographics
        )
        
        engagement_scores = {
            "cultural_relevance": cultural_relevance,
            "regional_fit": regional_fit,
            "demographic_alignment": demographic_alignment
        }
        
        self._cache_result(cache_key, engagement_scores)
        return engagement_scores
        
    def _generate_cache_key(self, base_key: str) -> str:
        """Gerar chave única para cache"""
        return hashlib.md5(base_key.encode()).hexdigest()
        
    def _get_cached_result(self, cache_key: str) -> Optional[Union[Dict, List]]:
        """Recuperar resultado do cache"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
            
        try:
            with cache_file.open("r") as f:
                cached_data = json.load(f)
                
            # Verificar idade do cache (24h)
            if datetime.fromtimestamp(cache_file.stat().st_mtime) < \
               datetime.now().timestamp() - 86400:
                return None
                
            return cached_data
        except Exception as e:
            logger.warning(f"Erro ao ler cache: {e}")
            return None
            
    def _cache_result(self, cache_key: str, data: Union[Dict, List]) -> None:
        """Salvar resultado em cache"""
        if not self.cache_config["enabled"]:
            return
            
        cache_file = self.cache_dir / f"{cache_key}.json"
        meta_file = self.cache_dir / f"{cache_key}.meta"
        
        try:
            # Salvar dados
            with cache_file.open("w") as f:
                json.dump(data, f, indent=2, default=str)
            
            # Salvar metadados
            meta_data = {
                "created": datetime.now().timestamp(),
                "hits": 1,
                "size": len(str(data)),
                "last_access": datetime.now().timestamp()
            }
            
            with meta_file.open("w") as f:
                json.dump(meta_data, f)
                
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {e}")
            
    def _cleanup_old_cache(self) -> None:
        """Limpar cache antigo e pouco usado"""
        try:
            total_size = 0
            files_meta = []
            
            # Coletar informações de todos os arquivos
            for meta_file in self.cache_dir.glob("*.meta"):
                try:
                    with meta_file.open("r") as f:
                        meta = json.load(f)
                    
                    data_file = self.cache_dir / f"{meta_file.stem}.json"
                    if data_file.exists():
                        size = data_file.stat().st_size
                        total_size += size
                        files_meta.append({
                            "meta_file": meta_file,
                            "data_file": data_file,
                            "meta": meta,
                            "size": size
                        })
                except Exception as e:
                    logger.warning(f"Erro ao ler metadados: {e}")
                    continue
            
            # Ordenar por última acesso e hits
            files_meta.sort(
                key=lambda x: (x["meta"]["last_access"], x["meta"]["hits"])
            )
            
            # Remover arquivos até atingir limite de tamanho
            max_size = self.cache_config["max_size_mb"] * 1024 * 1024
            for file_meta in files_meta:
                if total_size <= max_size:
                    break
                    
                if file_meta["meta"]["hits"] < self.cache_config["min_hits"]:
                    try:
                        file_meta["meta_file"].unlink()
                        file_meta["data_file"].unlink()
                        total_size -= file_meta["size"]
                    except Exception as e:
                        logger.warning(f"Erro ao remover arquivo: {e}")
                        
        except Exception as e:
            logger.error(f"Erro na limpeza do cache: {e}")
            
    def enrich_cultural_asset(self, asset: 'CulturalAsset') -> 'CulturalAsset':
        """
        Enriquecer um asset cultural com dados de redes sociais
        
        Args:
            asset: CulturalAsset para enriquecer
            
        Returns:
            CulturalAsset enriquecido com dados sociais
        """
        # Analisar engajamento cultural do conteúdo
        social_engagement = self.analyze_cultural_engagement(
            content=asset.content,
            target_regions=list(asset.regional_variants.keys()),
            target_demographics=asset.target_circles
        )
        
        # Detectar tendências relacionadas
        related_trends = self.detect_trends(
            keywords=[t for t in asset.content.split() if len(t) > 4],
            platforms=["instagram", "twitter", "facebook"],
            min_strength=0.4
        )
        
        # Atualizar scores culturais
        asset.cultural_scores.update({
            "social_relevance": social_engagement["cultural_relevance"],
            "social_regional_fit": social_engagement["regional_fit"],
            "social_demographic_fit": social_engagement["demographic_alignment"]
        })
        
        # Adicionar recomendações baseadas em tendências
        if related_trends:
            asset.recommendations.extend([
                f"💡 Alinhar com tendência: {trend.name} (força: {trend.strength:.2f})"
                for trend in related_trends[:3]
            ])
        
        return asset