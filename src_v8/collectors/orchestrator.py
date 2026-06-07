#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Orchestrator dos Coletores - Culture Pulse V9.0
Sistema principal que coordena todos os coletores consolidados

🎯 INTEGRADO COM V9.0:
- SecureConfig (configuração segura)
- LatencyMetrics (métricas de performance)
- SourceIndicators (indicadores visuais)
- IntegratedMonitoring (monitoramento sistêmico)
- cultural_dashboard_integrated.py
- Perfis Emergentes Engine
- Detecção de Tensões Engine

🔌 Coletores Consolidados:
- YouTube API (Real)
- Reddit API (Real)  
- Spotify API (Real)
- NewsAPI (Real)
- IBGE API (Real)
- Instagram/Threads (Simulado avançado)
- Meetup (Simulado)
- Google Trends API (Real)

📊 Resultados: 8 fontes de dados consolidadas
🗄️ Database: ProductionDatabaseManager
🚀 V9.0: Monitoramento integrado em tempo real
"""

import asyncio
import logging
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import time

# V9.0 System imports
logger = logging.getLogger(__name__)

# V9.9 Ingestion Systems
try:
    from core.models.production_database_manager import ProductionDatabaseManager
    _DB_MANAGER_AVAILABLE = True
except ImportError:
    _DB_MANAGER_AVAILABLE = False
    logger.warning("⚠️ ProductionDatabaseManager não disponível - modo persistência reduzida")

# 📸 V9.9 Visual Evidence Extraction (Scraping Thumbnails)
try:
    from .utils.metadata_extractor import VisualEvidenceExtractor
    _METADATA_EXTRACTOR_AVAILABLE = True
except ImportError:
    try:
        from collectors.utils.metadata_extractor import VisualEvidenceExtractor
        _METADATA_EXTRACTOR_AVAILABLE = True
    except ImportError:
        _METADATA_EXTRACTOR_AVAILABLE = False
        logger.warning("⚠️ VisualEvidenceExtractor não disponível - selos de veracidade reduzidos")

# S1.1 — Supabase writer (importação opcional: não bloqueia o sistema se ausente)
try:
    from .supabase_writer import write_signals_dict as _supabase_write
    _SUPABASE_WRITER_AVAILABLE = True
except ImportError:
    try:
        from collectors.supabase_writer import write_signals_dict as _supabase_write
        _SUPABASE_WRITER_AVAILABLE = True
    except ImportError:
        _SUPABASE_WRITER_AVAILABLE = False
        _supabase_write = None

try:
    from config.secure_config import SecureConfig
    from monitoring.latency_metrics import LatencyMetrics
    from collectors.data_collectors import DataSourceIndicators as DataSourceIndicators
    # Importação REAL do serviço de monitoramento integrado
    from monitoring.integrated_monitoring import IntegratedMonitoring
    V9_SYSTEMS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ Erro ao carregar sistemas V9.0: {e}. Criando mock de segurança.")
    
    class MockIntegratedMonitoring:
        def __init__(self): pass
        def log_event(self, *args, **kwargs): pass
        def start_session(self, *args, **kwargs): pass
        
    IntegratedMonitoring = MockIntegratedMonitoring
    V9_SYSTEMS_AVAILABLE = False

# Garantia final absoluta que a classe existe no namespace
if 'IntegratedMonitoring' not in globals() and 'IntegratedMonitoring' not in locals():
    IntegratedMonitoring = MockIntegratedMonitoring

# Core system imports
try:
    from ..core.engines.cultural_engine import CulturalAnalysisResult
    from ..core.engines.cultural_metrics_engine import CulturalMetricsEngine
    from ..config.centralized_config import config as settings
    _METRICS_ENGINE_AVAILABLE = True
except ImportError:
    # Para execução standalone
    CulturalAnalysisResult = None
    CulturalMetricsEngine = None
    _METRICS_ENGINE_AVAILABLE = False
    
    class MockAPIConfig:
        def __init__(self):
            import os
            self.YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "mock_key")
            self.REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "mock_id") 
            self.REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "mock_secret")
            self.REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "mock_agent")
            self.SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "mock_id")
            self.SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "mock_secret")
            self.NEWS_API_KEY = os.getenv("NEWS_API_KEY", "mock_key")
    
    class MockSettings:
        def __init__(self):
            self.api = MockAPIConfig()
    
    settings = MockSettings()


class OrchestratorV9:
    """
    🚀 Culture Pulse V9.0 - Orchestrator Modernizado
    
    Sistema central que coordena todos os coletores com:
    - SecureConfig (configuração segura)
    - LatencyMetrics (performance em tempo real)
    - SourceIndicators (status visual das fontes)
    - IntegratedMonitoring (saúde do sistema)
    """
    
    def __init__(self):
        """Inicializa V9.0 com todos os sistemas de monitoramento"""
        # Core configuration
        if V9_SYSTEMS_AVAILABLE:
            self.secure_config = SecureConfig()
            self.latency_metrics = LatencyMetrics()
            self.source_indicators = DataSourceIndicators()
            self.monitoring = IntegratedMonitoring()
        else:
            # Fallback para V8.0
            self.secure_config = None
            self.latency_metrics = None
            self.source_indicators = None
            self.monitoring = None
        
        # Core orchestrator
        self.orchestrator_classic = CulturalDataOrchestrator()
        self.metrics_engine = CulturalMetricsEngine() if _METRICS_ENGINE_AVAILABLE else None
        
        # V9.0 enhanced state
        self.v9_metrics = {
            'total_collections': 0,
            'failed_collections': 0,
            'avg_latency': 0,
            'system_health': 'unknown',
            'last_update': None
        }
        
        logger.info("🚀 OrchestratorV9 inicializado com sistemas V9.0")
    
    async def collect_with_monitoring(self, topics: List[str], 
                                    collectors: List[str] = None,
                                    context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Coleta dados com monitoramento V9.0 completo e consciência de Tier
        
        Args:
            topics: Lista de tópicos para coleta
            collectors: Lista específica de coletores (opcional)
            context: Contexto do usuário (user_id, project_id, user_tier)
            
        Returns:
            Dict com dados coletados + métricas V9.0
        """
        start_time = time.time()
        
        try:
            # 1. Pre-flight check V9.0
            if self.monitoring:
                system_health = self.monitoring.get_system_health()  # Remove await
                if system_health.overall_score < 0.5:
                    logger.warning("⚠️ Sistema com saúde baixa - prosseguindo com cuidado")
            
            # 2. Execução da coleta clássica
            # Converter topics para termo (primeiro tópico)
            termo = topics[0] if topics else "cultura"
            
            collection_result = await self.orchestrator_classic.collect_comprehensive_data(
                termo=termo,
                selected_sources=collectors,
                context=context
            )
            
            # 3. Registro de métricas V9.0
            collection_time = time.time() - start_time
            
            if self.latency_metrics:
                await self.latency_metrics.record_operation(
                    operation='unified_collection',
                    duration=collection_time,
                    success=collection_result.get('success', False)
                )
            
            # 4. Atualização de indicadores
            if self.source_indicators:
                for collector_name in collection_result.get('collectors_used', []):
                    await self.source_indicators.update_source_status(
                        source=collector_name,
                        status='success',
                        latency=collection_time / len(collection_result.get('collectors_used', [1]))
                    )
            
            # 5. Atualização métricas internas V9.0
            self.v9_metrics['total_collections'] += 1
            self.v9_metrics['avg_latency'] = (
                (self.v9_metrics['avg_latency'] * (self.v9_metrics['total_collections'] - 1) + collection_time) /
                self.v9_metrics['total_collections']
            )
            self.v9_metrics['last_update'] = datetime.now().isoformat()
            
            # 6. Resultado V9.0 enhanced
            v9_result = {
                **collection_result,
                'v9_metrics': {
                    'collection_time': collection_time,
                    'system_health': system_health if self.monitoring else None,
                    'latency_score': await self._get_latency_score(),
                    'source_health': await self._get_sources_health()
                }
            }
            
            logger.info(f"✅ Coleta V9.0 concluída em {collection_time:.2f}s")
            return v9_result
            
        except Exception as e:
            # Error handling V9.0
            self.v9_metrics['failed_collections'] += 1
            
            if self.latency_metrics:
                await self.latency_metrics.record_operation(
                    operation='unified_collection',
                    duration=time.time() - start_time,
                    success=False,
                    error=str(e)
                )
            
            logger.error(f"❌ Erro na coleta V9.0: {e}")
            raise
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Dados para dashboard com métricas V9.0 integradas
        
        Returns:
            Dict com dados do dashboard + métricas V9.0
        """
        try:
            # 1. Dados clássicos do dashboard
            classic_data = self.orchestrator_classic.get_collector_status()
            
            # 2. Métricas V9.0 adicionais
            v9_dashboard_data = {
                **classic_data,
                'v9_systems': {
                    'available': V9_SYSTEMS_AVAILABLE,
                    'latency_metrics': await self._get_latency_metrics(),
                    'source_indicators': await self._get_source_indicators(),
                    'system_health': await self._get_system_health(),
                    'orchestrator_metrics': self.v9_metrics
                }
            }
            
            return v9_dashboard_data
            
        except Exception as e:
            logger.error(f"Erro ao obter dados do dashboard V9.0: {e}")
            return {'error': str(e), 'v9_systems': {'available': False}}
    
    async def _get_latency_score(self) -> Optional[float]:
        """Obtém score de latência das métricas V9.0"""
        if not self.latency_metrics:
            return None
        try:
            metrics = await self.latency_metrics.get_current_metrics()
            return metrics.get('average_latency', 0)
        except:
            return None
    
    async def _get_sources_health(self) -> Optional[Dict]:
        """Obtém saúde das fontes de dados"""
        if not self.source_indicators:
            return None
        try:
            return await self.source_indicators.get_all_sources_status()
        except:
            return None
    
    async def _get_latency_metrics(self) -> Optional[Dict]:
        """Métricas de latência para dashboard"""
        if not self.latency_metrics:
            return None
        try:
            return await self.latency_metrics.get_current_metrics()
        except:
            return None
    
    async def _get_source_indicators(self) -> Optional[Dict]:
        """Indicadores de fonte para dashboard"""
        if not self.source_indicators:
            return None
        try:
            return await self.source_indicators.get_all_sources_status()
        except:
            return None
    
    async def _get_system_health(self) -> Optional[Dict]:
        """Saúde do sistema para dashboard"""
        if not self.monitoring:
            return None
        try:
            health_metrics = self.monitoring.get_system_health()  # Remove await
            # Converter SystemHealthMetrics para Dict e normalizar score
            raw_score = health_metrics.overall_score
            normalized_score = raw_score / 100 if raw_score > 1 else raw_score
            
            return {
                'overall_score': normalized_score,
                'details': health_metrics.details if hasattr(health_metrics, 'details') else {}
            }
        except:
            return None


# Backward compatibility alias
if V9_SYSTEMS_AVAILABLE:
    # Usar V9.0 como padrão
    CulturePulseOrchestratorV9 = OrchestratorV9
    logger.info("🚀 Using OrchestratorV9 as default")
else:
    # Fallback para V8.0
    logger.info("📋 Using CulturePulseOrchestrator V8.0 as fallback")

# Import unificado dos coletores consolidados
try:
    from .data_collectors import (
        create_unified_collectors,
        CulturalSignal,
        data_cache
    )
except ImportError:
    # Fallback para teste
    def create_unified_collectors():
        return {}
    
    class CulturalSignal:
        pass
    
    class data_cache:
        @staticmethod
        def get(key, ttl_minutes=60):
            return None
        
        @staticmethod
        def set(key, value):
            pass

# Collectors imports - Usando coletores consolidados
try:
    from .data_collectors import (
        YouTubeCollectorV8, RedditCollectorV8, SpotifyCollectorV8,
        NewsAPICollectorV8, IBGECollectorV8,
        InstagramThreadsCollectorV8, MeetupCollectorV8,
        GoogleTrendsCollectorV8, RSSCollectorV8,
        CulturalSignal, data_cache
    )
except ImportError:
    # Para execução standalone
    from data_collectors import (
        YouTubeCollectorV8, RedditCollectorV8, SpotifyCollectorV8,
        NewsAPICollectorV8, IBGECollectorV8,
        InstagramThreadsCollectorV8, MeetupCollectorV8,
        GoogleTrendsCollectorV8, RSSCollectorV8,
        CulturalSignal, data_cache
    )

logger = logging.getLogger(__name__)


class CulturalDataOrchestrator:
    """
    Orquestrador Principal dos Coletores V8.0/V9.9
    Coordena todas as APIs e fontes de dados com Ingestão por Tier
    """
    
    def __init__(self):
        self.settings = settings
        self._collectors = {}
        self._initialize_collectors()
        
        # 📸 V9.9 Ingestão de Imagens Real-time
        self.metadata_extractor = VisualEvidenceExtractor() if _METADATA_EXTRACTOR_AVAILABLE else None

        # Ingestão de Dados (DuckDB/Supabase)
        if _DB_MANAGER_AVAILABLE:
            self.db_manager = ProductionDatabaseManager()
        else:
            self.db_manager = None

        # Configuração de rate limiting
        self.concurrent_limit = 5  # Max APIs simultâneas
        self.timeout_per_api = 30  # Timeout por API
        
        logger.info("🎯 CulturalDataOrchestrator V8.0/V9.9 inicializado")
    
    def _initialize_collectors(self):
        """Inicializar todos os coletores"""
        try:
            # Coletores principais (baseados no V7.0)
            self._collectors.update({
                'youtube': YouTubeCollectorV8(
                    api_key=self.settings.api.YOUTUBE_API_KEY
                ),
                'reddit': RedditCollectorV8(
                    client_id=self.settings.api.REDDIT_CLIENT_ID,
                    client_secret=self.settings.api.REDDIT_CLIENT_SECRET,
                    user_agent=self.settings.api.REDDIT_USER_AGENT
                ),
                'spotify': SpotifyCollectorV8(
                    client_id=self.settings.api.SPOTIFY_CLIENT_ID,
                    client_secret=self.settings.api.SPOTIFY_CLIENT_SECRET
                ),
                'news': NewsAPICollectorV8(
                    api_key=self.settings.api.NEWS_API_KEY
                ),
                'ibge': IBGECollectorV8(),
                'instagram': InstagramThreadsCollectorV8(),
                'meetup': MeetupCollectorV8(),
                'google_trends': GoogleTrendsCollectorV8(),
                'rss_cultural': RSSCollectorV8()
            })
            
            logger.info(f"✅ {len(self._collectors)} coletores inicializados")
            
        except Exception as e:
            logger.error(f"Erro na inicialização dos coletores: {e}")
            # Coletores mínimos em caso de erro
            self._collectors = {
                'instagram': InstagramThreadsCollectorV8(),
                'meetup': MeetupCollectorV8(),
                'google_trends': GoogleTrendsCollectorV8()
            }
    
    async def collect_comprehensive_data(
        self, 
        termo: str, 
        context: Dict[str, Any] = None,
        selected_sources: List[str] = None
    ) -> Dict[str, CulturalSignal]:
        """
        Coletar dados de todas as fontes disponíveis com ingestão por Tier V9.9
        """
        logger.info(f"🚀 Iniciando coleta abrangente para '{termo}'")
        
        # Extrair contexto de Tier
        user_tier = context.get('user_tier', 'free').lower() if context else 'free'
        user_id = context.get('user_id', 'gen') if context else 'gen'
        
        # 1. Filtro de Tier D+1 (Free) vs Real-time (Pro+)
        # No V9.9, se for Free, tentamos cache primeiro. Se falhar, coletamos D+1.
        
        # Determinar fontes ativas
        active_sources = selected_sources or list(self._collectors.keys())
        active_collectors = {
            name: collector for name, collector in self._collectors.items()
            if name in active_sources
        }
        
        logger.info(f"📡 Coletando de {len(active_collectors)} fontes: {list(active_collectors.keys())} | Tier: {user_tier}")
        
        # Execução paralela com limite de concorrência
        semaphore = asyncio.Semaphore(self.concurrent_limit)
        tasks = []
        
        for source_name, collector in active_collectors.items():
            task = self._collect_with_semaphore(
                semaphore, source_name, collector, termo, context
            )
            tasks.append(task)
        
        # Aguardar todos os resultados
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        collection_time = time.time() - start_time
        
        # Processar resultados
        collected_signals = {}
        successful_collections = 0
        
        for i, result in enumerate(results):
            source_name = list(active_collectors.keys())[i]
            
            if isinstance(result, Exception):
                logger.error(f"❌ Erro em {source_name}: {result}")
                continue
                
            if result:
                # 📸 V9.9 Ingestão de Metadados Visuais (Scraping de Thumbnail para RSS/News)
                if self.metadata_extractor and source_name in ['news', 'rss_cultural']:
                    try:
                        # O result aqui pode ser uma lista de sinais ou um sinal único dependendo do coletor
                        if isinstance(result, list):
                            for sig in result:
                                self.metadata_extractor.enrich_signal_with_media(sig)
                        elif isinstance(result, dict):
                            self.metadata_extractor.enrich_signal_with_media(result)
                    except Exception as ex_media:
                        logger.warning(f"⚠️ Erro ao enriquecer mídia para {source_name}: {ex_media}")

                collected_signals[source_name] = result
                successful_collections += 1
                logger.info(f"✅ {source_name}: OK")
            else:
                logger.warning(f"⚠️ {source_name}: Sem dados")
        
        logger.info(f"🏁 Coleta concluída: {successful_collections}/{len(active_collectors)} fontes bem-sucedidas em {collection_time:.2f}s")
        
        # 2. Ingestão Inteligente V9.9 (Arquivista Unificado)
        if collected_signals:
            await self._ingest_historical_data(termo, collected_signals, user_tier, context)
        
        return collected_signals
    
    async def _ingest_historical_data(self, termo: str, signals: Dict[str, CulturalSignal], tier: str, context: Dict):
        """
        Método unificado de arquivista de inteligência (V9.9)
        Focado em persistência de sinais via Supabase.
        """
        user_id = context.get('user_id') if context else None
        
        # 1. Tentativa Primária: Supabase (S1.1/V9.9)
        supabase_success = False
        if _SUPABASE_WRITER_AVAILABLE and _supabase_write:
            try:
                # Attach context to signals when available for clearer persistence
                if context:
                    for sig in signals.values():
                        try:
                            if context.get('project_id'):
                                setattr(sig, 'project_id', context.get('project_id'))
                            if user_id:
                                setattr(sig, 'user_id', user_id)
                        except Exception:
                            pass

                persisted_count = _supabase_write(
                    signals,
                    project_id=context.get('project_id') if context else None,
                    user_id=user_id,
                )
                if persisted_count and persisted_count > 0:
                    logger.info(f"☁️  Supabase: {persisted_count} sinais persistidos para '{termo}'")
                    supabase_success = True
            except Exception as sb_exc:
                logger.warning(f"⚠️  Falha no Supabase Writer: {sb_exc}. Acionando Fallback Local.")

        # 2. Se o Supabase falhar, não usar DuckDB como fallback automático.
        if not supabase_success:
            logger.error(
                f"❌ Persistência no Supabase falhou para '{termo}' e fallback DuckDB está desativado. "
                "Configure o writer Supabase ou corrija a conexão do backend."
            )

    async def _collect_with_semaphore(
        self, 
        semaphore: asyncio.Semaphore,
        source_name: str,
        collector: Any,
        termo: str,
        context: Dict[str, Any]
    ) -> Optional[CulturalSignal]:
        """Coletar dados com controle de concorrência"""
        async with semaphore:
            try:
                return await asyncio.wait_for(
                    collector.collect_cultural_data(termo, context),
                    timeout=self.timeout_per_api
                )
            except asyncio.TimeoutError:
                logger.warning(f"⏰ Timeout em {source_name}")
                return None
            except Exception as e:
                logger.error(f"💥 Erro em {source_name}: {e}")
                return None
    
    def _resolve_user_intent(self, context: Dict[str, Any]) -> str:
        """Resolve o intent do usuário a partir do contexto de onboarding."""
        if not context:
            return "Pesquisa de Mercado"

        onboarding = context.get('onboarding') or {}
        if not isinstance(onboarding, dict):
            return "Pesquisa de Mercado"

        explicit_intent = onboarding.get('user_intent') or onboarding.get('intent')
        if explicit_intent and isinstance(explicit_intent, str):
            normalized = explicit_intent.strip().lower()
            if 'crise' in normalized or 'reputação' in normalized:
                return 'Crise de Reputação'
            if 'lançamento' in normalized or 'campaign' in normalized or 'campanha' in normalized:
                return 'Lançamento de Produto'
            if 'pesquisa' in normalized or 'research' in normalized:
                return 'Pesquisa de Mercado'
            return explicit_intent

        moment = onboarding.get('moment', '')
        if isinstance(moment, str):
            normalized = moment.strip().lower()
            if 'crise' in normalized or 'reputação' in normalized:
                return 'Crise de Reputação'
            if 'lançamento' in normalized or 'campaign' in normalized or 'campanha' in normalized:
                return 'Lançamento de Produto'
            if 'pesquisa' in normalized or 'research' in normalized:
                return 'Pesquisa de Mercado'

        segment = onboarding.get('segment', '')
        if isinstance(segment, str) and 'research' in segment.lower():
            return 'Pesquisa de Mercado'

        return 'Pesquisa de Mercado'

    def analyze_collected_signals(
        self, 
        signals: Dict[str, CulturalSignal],
        termo: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Analisar e consolidar os sinais coletados
        """
        if not signals:
            return {
                'status': 'error',
                'message': 'Nenhum sinal coletado',
                'termo': termo
            }
        
        logger.info(f"📊 Analisando {len(signals)} sinais para '{termo}'")
        
        # Métricas consolidadas
        total_momentum = sum(signal.momentum for signal in signals.values())
        avg_momentum = total_momentum / len(signals)
        
        total_volume = sum(signal.volume for signal in signals.values())
        avg_sentiment = sum(signal.sentiment for signal in signals.values()) / len(signals)
        
        # Qualidade média dos dados
        avg_quality = sum(signal.score_qualidade for signal in signals.values()) / len(signals)
        
        # Fontes por confiabilidade
        reliability_counts = {}
        for signal in signals.values():
            reliability = signal.fonte_confiabilidade
            reliability_counts[reliability] = reliability_counts.get(reliability, 0) + 1
        
        # Ranking de plataformas por momentum
        platform_ranking = sorted(
            [(platform, signal.momentum) for platform, signal in signals.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Detecção de tendências
        high_momentum_platforms = [
            platform for platform, momentum in platform_ranking
            if momentum >= 70
        ]
        
        # Score de consenso (concordância entre plataformas)
        momentum_values = [signal.momentum for signal in signals.values()]
        momentum_std = (
            sum((x - avg_momentum) ** 2 for x in momentum_values) / len(momentum_values)
        ) ** 0.5
        consensus_score = max(0, 100 - momentum_std)  # Menos desvio = mais consenso
        
        # Resultado consolidado
        analysis_result = {
            'status': 'success',
            'termo': termo,
            'timestamp': datetime.now().isoformat(),
            
            # Métricas principais
            'metricas_consolidadas': {
                'momentum_total': round(total_momentum, 2),
                'momentum_medio': round(avg_momentum, 2),
                'volume_total': total_volume,
                'sentiment_medio': round(avg_sentiment, 3),
                'qualidade_media': round(avg_quality, 3),
                'consenso_score': round(consensus_score, 2)
            },
            
            # Análise por plataforma
            'ranking_plataformas': platform_ranking,
            'plataformas_alta_relevancia': high_momentum_platforms,
            
            # Qualidade dos dados
            'fontes_por_confiabilidade': reliability_counts,
            'total_fontes': len(signals),
            
            # Detalhes dos sinais
            'sinais_detalhados': {
                platform: {
                    'momentum': signal.momentum,
                    'volume': signal.volume,
                    'sentiment': signal.sentiment,
                    'relevancia': signal.relevancia_cultural,
                    'qualidade': signal.score_qualidade,
                    'confiabilidade': signal.fonte_confiabilidade,
                    'dados_extras': signal.dados_extras
                }
                for platform, signal in signals.items()
            }
        }
        
        analysis_result['onboarding_context'] = context.get('onboarding') if context else None
        analysis_result['project_id'] = context.get('project_id') if context else None
        analysis_result['user_id'] = context.get('user_id') if context else None

        if self.metrics_engine:
            try:
                data_points = [signal.to_dict() for signal in signals.values()]
                user_intent = self._resolve_user_intent(context)
                metrics_output = self.metrics_engine.calculate_all_metrics(
                    data={'data_points': data_points},
                    industry=context.get('industry') if context else 'general',
                    historical_data=None,
                    user_intent=user_intent
                )

                analysis_result['weak_signals'] = metrics_output.get('weak_signals', {})
                analysis_result['cultural_metrics'] = {
                    'score_cultural': metrics_output.get('score_cultural'),
                    'momentum_cultural': metrics_output.get('momentum_cultural'),
                    'ensemble_prediction': metrics_output.get('ensemble_prediction'),
                    'confidence': metrics_output.get('confidence'),
                    'user_intent': user_intent
                }
                analysis_result['metrics_engine_output'] = metrics_output
            except Exception as e:
                logger.warning(f"⚠️ Cultural metrics engine failed: {e}")

        logger.info(f"✅ Análise concluída: Momentum médio {avg_momentum:.1f}, Consenso {consensus_score:.1f}%")
        
        return analysis_result
    
    async def quick_cultural_scan(
        self, 
        termo: str,
        priority_sources: List[str] = None,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Scan rápido com fontes prioritárias (para demonstrações)
        """
        # Fontes prioritárias mais rápidas
        if not priority_sources:
            priority_sources = ['instagram', 'meetup', 'news', 'ibge', 'google_trends']
        
        logger.info(f"⚡ Quick scan para '{termo}' com {len(priority_sources)} fontes")
        
        signals = await self.collect_comprehensive_data(
            termo=termo,
            selected_sources=priority_sources,
            context=context
        )
        
        return self.analyze_collected_signals(signals, termo, context=context)
    
    def get_collector_status(self) -> Dict[str, Any]:
        """Status de todos os coletores"""
        status = {
            'total_collectors': len(self._collectors),
            'collectors': {},
            'settings_status': {
                'youtube_api_configured': bool(self.settings.api.YOUTUBE_API_KEY),
                'reddit_api_configured': bool(self.settings.api.REDDIT_CLIENT_ID),
                'spotify_api_configured': bool(self.settings.api.SPOTIFY_CLIENT_ID),
                'news_api_configured': bool(self.settings.api.NEWS_API_KEY)
            }
        }
        
        for name, collector in self._collectors.items():
            collector_type = type(collector).__name__
            status['collectors'][name] = {
                'type': collector_type,
                'status': 'active',
                'requires_api_key': name in ['youtube', 'reddit', 'spotify', 'news']
            }
        
        return status


# Instância global do orquestrador
cultural_orchestrator = CulturalDataOrchestrator()

REAL_DATA_SOURCES = ['youtube', 'reddit', 'spotify', 'news', 'ibge']
SIMULATED_DATA_SOURCES = ['instagram', 'meetup']
ALLOW_DEMO_COLLECTION = os.getenv("ALLOW_DEMO_COLLECTION", "false").strip().lower() in ("1", "true", "yes", "y")
IS_PRODUCTION = os.getenv("ENVIRONMENT", "production").strip().lower() == "production"


def _filter_sources_for_environment(sources: List[str] = None) -> List[str]:
    if IS_PRODUCTION:
        if sources is None:
            return REAL_DATA_SOURCES

        demo_sources = [s for s in sources if s in SIMULATED_DATA_SOURCES]
        if demo_sources and not ALLOW_DEMO_COLLECTION:
            raise ValueError(
                f"Demo sources not allowed in production: {demo_sources}. "
                f"Use only real sources: {REAL_DATA_SOURCES}."
            )

    return sources


# Funções de conveniência para uso em outras partes do sistema
async def collect_cultural_data(
    termo: str, 
    context: Dict[str, Any] = None,
    sources: List[str] = None
) -> Dict[str, Any]:
    """Função principal para coletar dados culturais"""
    selected_sources = _filter_sources_for_environment(sources)
    signals = await cultural_orchestrator.collect_comprehensive_data(
        termo=termo,
        context=context,
        selected_sources=selected_sources
    )
    
    return cultural_orchestrator.analyze_collected_signals(signals, termo, context=context)


async def quick_cultural_analysis(termo: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Análise cultural rápida para demos"""
    if IS_PRODUCTION:
        return await collect_cultural_data(termo=termo, sources=REAL_DATA_SOURCES, context=context)

    return await cultural_orchestrator.quick_cultural_scan(termo, context=context)


def get_data_collection_status() -> Dict[str, Any]:
    """Status do sistema de coleta"""
    return cultural_orchestrator.get_collector_status()


# Para testes e demonstração
if __name__ == "__main__":
    # Importar dependências para teste standalone
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    
    # Mock para imports que não existem
    class MockCulturalAnalysisResult:
        pass
    
    class MockSettings:
        def __init__(self):
            self.youtube_api_key = "test_key"
            self.reddit_client_id = "test_id" 
            self.reddit_client_secret = "test_secret"
            self.reddit_user_agent = "test_agent"
            self.spotify_client_id = "test_spotify_id"
            self.spotify_client_secret = "test_spotify_secret"
            self.news_api_key = "test_news_key"
    
    def get_settings():
        return MockSettings()
    
    async def test_orchestrator():
        """Teste do orquestrador completo"""
        print("🧪 Testando CulturalDataOrchestrator V8.0")
        print("=" * 60)
        
        # Criar instância do orquestrador para teste
        orchestrator = CulturalDataOrchestrator()
        
        # Status inicial
        status = orchestrator.get_collector_status()
        print(f"📊 Status: {status['total_collectors']} coletores ativos")
        print()
        
        # Teste quick scan
        termo_teste = "samba"
        print(f"⚡ Quick scan para '{termo_teste}'...")
        
        result = await orchestrator.quick_cultural_scan(termo_teste)
        
        if result['status'] == 'success':
            metrics = result['metricas_consolidadas']
            print(f"✅ Sucesso!")
            print(f"   Momentum médio: {metrics['momentum_medio']:.1f}")
            print(f"   Volume total: {metrics['volume_total']}")
            print(f"   Sentiment médio: {metrics['sentiment_medio']:.3f}")
            print(f"   Consenso: {metrics['consenso_score']:.1f}%")
            print(f"   Fontes: {result['total_fontes']}")
            
            print("\n🏆 Ranking de plataformas:")
            for i, (platform, momentum) in enumerate(result['ranking_plataformas'][:3], 1):
                print(f"   {i}. {platform}: {momentum:.1f}")
        else:
            print(f"❌ Erro: {result.get('message', 'Desconhecido')}")
        
        print("\n🏁 Teste concluído!")
    
    asyncio.run(test_orchestrator())
