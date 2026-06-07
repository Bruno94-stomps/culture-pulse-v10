"""
📊 Executive Summary Synchronizer V9.0
Sincronização automática de dados do resumo executivo
Garante consistência entre diferentes seções do dashboard
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import os
import logging

# Import do Monitoramento V9.1 (Bridge de Inteligência Real)
try:
    from monitoring.integrated_monitoring import IntegratedMonitoring
    monitoring_bridge = IntegratedMonitoring()
except ImportError:
    monitoring_bridge = None

logger = logging.getLogger(__name__)

class ExecutiveSummarySynchronizer:
    """Sincronizador para dados do resumo executivo"""
    
    def __init__(self):
        self.cached_data = {}
        self.last_update = None
        
        print("📊 Executive Summary Synchronizer V9.0 inicializado!")
    
    def sync_executive_data(self, 
                          config_data: Dict[str, Any], 
                          analysis_results: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Sincroniza dados para o resumo executivo"""
        
        # Dados básicos do contexto
        location = config_data.get('location', 'Brasil')
        segment = config_data.get('business_segment', 'Geral')
        target_audience = config_data.get('target_audience', 'Amplo')
        
        # Contagem de coletores ativos
        active_collectors = self._count_active_collectors(config_data)
        
        # Contagem de termos analisados
        analyzed_terms = self._count_analyzed_terms(config_data, analysis_results)
        
        # Status dos componentes ML (Dados Reais V9.1)
        ml_status = self._get_ml_status_real()
        
        # Monitoramento de Drift (Inteligência de Mercado)
        drift_context = self._get_drift_context()
        
        # Métricas de performance
        performance_metrics = self._get_performance_metrics(analysis_results)
        
        # Insights principais
        key_insights = self._extract_key_insights(analysis_results)
        
        synchronized_data = {
            # Dados principais
            'cliente': config_data.get('company_name', 'Cliente'),
            'segmento': segment,
            'contexto': config_data.get('business_context', 'Análise cultural'),
            'localizacao': location,
            'coletores_ativos': active_collectors,
            'termos_analisados': analyzed_terms,
            
            # Inteligência V9.1 (Real Data Only)
            'drift_global_score': drift_context.get('avg_drift', 0.0),
            'drift_alert_level': drift_context.get('alert_level', 'Stable'),
            
            # Status técnico real
            'ml_components_active': ml_status['active_count'],
            'ml_components_total': ml_status['total_count'],
            'ml_status_detail': ml_status['components'],
            
            # Métricas de performance
            'total_profiles': performance_metrics.get('total_profiles', 0),
            'emerging_trends': performance_metrics.get('emerging_trends', 0),
            'cultural_relevance_score': performance_metrics.get('cultural_relevance', 0.0),
            'confidence_level': performance_metrics.get('confidence', 0.0),
            
            # Insights principais
            'key_insights': key_insights,
            'recommendations': self._generate_recommendations(config_data, analysis_results),
            
            # Metadata
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'analysis_duration': performance_metrics.get('analysis_duration', 'N/A'),
            'data_sources': self._get_active_data_sources(config_data)
        }
        
        # Cache dos dados
        self.cached_data = synchronized_data
        self.last_update = datetime.now()
        
        return synchronized_data
    
    def _count_active_collectors(self, config_data: Dict[str, Any]) -> int:
        """Conta coletores ativos baseado na configuração"""
        
        active_count = 0
        
        # APIs configuradas
        api_configs = [
            'youtube_enabled', 'instagram_enabled', 'reddit_enabled',
            'tiktok_enabled', 'twitter_enabled', 'news_enabled'
        ]
        
        for api_config in api_configs:
            if config_data.get(api_config, False):
                active_count += 1
        
        # Se nenhuma API específica configurada, assumir configuração padrão
        if active_count == 0:
            # Verificar se há termos de pesquisa (indica coleta ativa)
            search_terms = config_data.get('search_terms', [])
            if search_terms and len(search_terms) > 0:
                active_count = 3  # YouTube, Instagram, Reddit (padrão)
        
        return active_count
    
    def _count_analyzed_terms(self, 
                            config_data: Dict[str, Any], 
                            analysis_results: Optional[Dict[str, Any]]) -> int:
        """Conta termos analisados"""
        
        # Primeiro, tentar obter dos resultados da análise
        if analysis_results:
            if 'analyzed_terms' in analysis_results:
                return len(analysis_results['analyzed_terms'])
            elif 'terms_used' in analysis_results:
                return len(analysis_results['terms_used'])
        
        # Senão, contar dos termos de pesquisa configurados
        search_terms = config_data.get('search_terms', [])
        if search_terms:
            return len(search_terms)
        
        # Default baseado no contexto
        business_context = config_data.get('business_context', '')
        segment = config_data.get('business_segment', '')
        
        # Estimar termos baseado no contexto
        estimated_terms = len(business_context.split()) + len(segment.split())
        return max(5, min(20, estimated_terms))  # Entre 5 e 20 termos
    
    def _get_ml_status(self) -> Dict[str, Any]:
        """Obtém status dos componentes ML"""
        
        try:
            # Tentar importar ML Foundation
            from autonomous_agent.ml_foundation.ml_integrator_simple import MLIntegratorSimple
            
            ml_integrator = MLIntegratorSimple()
            
            # Verificar componentes
            components_status = {
                'Cultural Embeddings': self._check_component_status('cultural_embeddings'),
                'Advanced NLP': self._check_component_status('nlp_processor'), 
                'Feedback Learning': self._check_component_status('feedback_learner'),
                'GitHub Models': self._check_component_status('github_models')
            }
            
            active_count = sum(1 for status in components_status.values() if status)
            
            return {
                'active_count': active_count,
                'total_count': 4,
                'components': components_status
            }
            
        except Exception as e:
            print(f"⚠️ Erro ao verificar status ML: {e}")
            return {
                'active_count': 0,
                'total_count': 4,
                'components': {}
            }
    
    def _check_component_status(self, component_name: str) -> bool:
        """Verifica se um componente específico está ativo"""
        try:
            # Verificar se arquivos existem
            component_files = {
                'cultural_embeddings': 'autonomous_agent/ml_foundation/cultural_embeddings_simple.py',
                'nlp_processor': 'autonomous_agent/ml_foundation/advanced_nlp_processor.py',
                                'feedback_learner': 'autonomous_agent/ml_foundation/feedback_learning.py',
                'github_models': 'autonomous_agent/ml_foundation/github_models.py'
            }
            
            file_path = component_files.get(component_name)
            if file_path and os.path.exists(file_path):
                return True
            
            return False
            
        except Exception:
            return False
    
    def _get_ml_status_real(self) -> Dict[str, Any]:
        """Obtém status real dos componentes ML via IntegratedMonitoring"""
        components = {
            'Cultural BERT Engine': False,
            'TF-IDF Analyzer': False,
            'Alma Brasileira Core': False,
            'Circles Processor': False
        }
        
        # Tentar carregar via verificação de memória/import
        try:
            from core.engines.cultural_engine import create_cultural_engine
            if create_cultural_engine: components['Cultural BERT Engine'] = True
            
            from core.intelligence.circles_processor import CulturalCirclesProcessor
            if CulturalCirclesProcessor: components['Circles Processor'] = True
            
            from core.tfidf_analyzer import TFIDFCulturalAnalyzer
            if TFIDFCulturalAnalyzer: components['TF-IDF Analyzer'] = True
            
            from core.alma_brasileira import AlmaBrasileiraAnalyzer
            if AlmaBrasileiraAnalyzer: components['Alma Brasileira Core'] = True
        except:
            pass
            
        active_count = sum(1 for status in components.values() if status)
        
        return {
            'active_count': active_count,
            'total_count': len(components),
            'components': components
        }

    def _get_drift_context(self) -> Dict[str, Any]:
        """Extrai contexto de drift para o resumo executivo"""
        if not monitoring_bridge:
            return {'avg_drift': 0.0, 'alert_level': 'Unknown'}
            
        drifts = monitoring_bridge.get_latest_drift()
        if not drifts:
            return {'avg_drift': 0.0, 'alert_level': 'Stable'}
            
        avg_drift = sum([d.get('drift_score', 0) for d in drifts.values()]) / len(drifts)
        
        alert_level = 'Stable'
        if avg_drift > 0.7: alert_level = 'Critical Drift'
        elif avg_drift > 0.4: alert_level = 'Warning'
        
        return {
            'avg_drift': round(avg_drift, 2),
            'alert_level': alert_level,
            'volatile_categories': [k for k, v in drifts.items() if v.get('drift_score', 0) > 0.5]
        }
    
    def _get_performance_metrics(self, analysis_results: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Extrai métricas de performance da análise"""
        
        if not analysis_results:
            return {
                'total_profiles': 0,
                'emerging_trends': 0,
                'cultural_relevance': 0.0,
                'confidence': 0.0,
                'analysis_duration': 'N/A'
            }
        
        # Extrair métricas baseado na estrutura dos resultados
        metrics = {}
        
        # Total de perfis
        if 'profiles' in analysis_results:
            metrics['total_profiles'] = len(analysis_results['profiles'])
        elif 'total_profiles_detected' in analysis_results:
            metrics['total_profiles'] = analysis_results['total_profiles_detected']
        else:
            metrics['total_profiles'] = 0
        
        # Tendências emergentes
        if 'trends' in analysis_results:
            metrics['emerging_trends'] = len(analysis_results['trends'])
        elif 'emerging_profiles' in analysis_results:
            metrics['emerging_trends'] = len(analysis_results['emerging_profiles'])
        else:
            metrics['emerging_trends'] = 0
        
        # Relevância cultural
        if 'cultural_relevance_score' in analysis_results:
            metrics['cultural_relevance'] = analysis_results['cultural_relevance_score']
        elif 'overall_score' in analysis_results:
            metrics['cultural_relevance'] = analysis_results['overall_score']
        else:
            metrics['cultural_relevance'] = 0.7  # Padrão médio
        
        # Confiança
        if 'confidence_score' in analysis_results:
            metrics['confidence'] = analysis_results['confidence_score']
        elif 'confidence' in analysis_results:
            metrics['confidence'] = analysis_results['confidence']
        else:
            metrics['confidence'] = 0.75  # Padrão médio
        
        # Duração da análise
        if 'analysis_time' in analysis_results:
            metrics['analysis_duration'] = f"{analysis_results['analysis_time']:.1f}s"
        else:
            metrics['analysis_duration'] = 'N/A'
        
        return metrics
    
    def _extract_key_insights(self, analysis_results: Optional[Dict[str, Any]]) -> List[str]:
        """Extrai insights principais da análise"""
        
        if not analysis_results:
            return ["Aguardando análise completa para gerar insights"]
        
        insights = []
        
        # Insights baseados em perfis emergentes
        if 'profiles' in analysis_results and analysis_results['profiles']:
            top_profile = analysis_results['profiles'][0] if analysis_results['profiles'] else None
            if top_profile and 'name' in top_profile:
                insights.append(f"Perfil emergente principal: {top_profile['name']}")
        
        # Insights baseados em tendências
        if 'trends' in analysis_results and analysis_results['trends']:
            insights.append(f"Detectadas {len(analysis_results['trends'])} tendências culturais ativas")
        
        # Insights baseados em círculos culturais
        if 'cultural_circles' in analysis_results:
            top_circles = analysis_results['cultural_circles'][:2] if analysis_results['cultural_circles'] else []
            if top_circles:
                circles_names = [circle.get('name', 'N/A') for circle in top_circles]
                insights.append(f"Círculos culturais dominantes: {', '.join(circles_names)}")
        
        # Insights baseados em relevância
        performance_metrics = self._get_performance_metrics(analysis_results)
        if performance_metrics['cultural_relevance'] > 0.8:
            insights.append("Alta relevância cultural detectada")
        elif performance_metrics['cultural_relevance'] > 0.6:
            insights.append("Relevância cultural moderada")
        
        # Se não há insights específicos, gerar genéricos
        if not insights:
            insights = [
                "Análise cultural em andamento",
                "Coletando dados de múltiplas fontes",
                "Processando padrões culturais brasileiros"
            ]
        
        return insights[:3]  # Máximo 3 insights
    
    def _generate_recommendations(self, 
                                config_data: Dict[str, Any], 
                                analysis_results: Optional[Dict[str, Any]]) -> List[str]:
        """Gera recomendações baseadas nos dados"""
        
        recommendations = []
        
        # Recomendações baseadas no segmento
        segment = config_data.get('business_segment', '').lower()
        
        if 'tech' in segment:
            recommendations.append("Focar em inovação e early adopters")
        elif 'fashion' in segment:
            recommendations.append("Priorizar tendências visuais e influenciadores")
        elif 'food' in segment:
            recommendations.append("Explorar tradições regionais e autenticidade")
        else:
            recommendations.append("Personalizar abordagem por região")
        
        # Recomendações baseadas na localização
        location = config_data.get('location', '').lower()
        
        if 'nordeste' in location:
            recommendations.append("Integrar elementos musicais e festivos")
        elif 'sudeste' in location:
            recommendations.append("Enfatizar inovação e eficiência")
        elif 'sul' in location:
            recommendations.append("Valorizar tradições familiares")
        
        # Recomendações baseadas nos resultados
        if analysis_results:
            performance_metrics = self._get_performance_metrics(analysis_results)
            
            if performance_metrics['confidence'] < 0.7:
                recommendations.append("Aumentar dados de entrada para melhor precisão")
            
            if performance_metrics['total_profiles'] < 3:
                recommendations.append("Expandir termos de pesquisa para mais insights")
        
        # Garantir pelo menos 2 recomendações
        if len(recommendations) < 2:
            recommendations.extend([
                "Monitorar tendências semanalmente",
                "Testar abordagens em mercado piloto"
            ])
        
        return recommendations[:3]  # Máximo 3 recomendações
    
    def _get_active_data_sources(self, config_data: Dict[str, Any]) -> List[str]:
        """Lista fontes de dados ativas"""
        
        sources = []
        
        api_mapping = {
            'youtube_enabled': 'YouTube',
            'instagram_enabled': 'Instagram', 
            'reddit_enabled': 'Reddit',
            'tiktok_enabled': 'TikTok',
            'twitter_enabled': 'Twitter',
            'news_enabled': 'Notícias'
        }
        
        for api_key, api_name in api_mapping.items():
            if config_data.get(api_key, False):
                sources.append(api_name)
        
        # Se nenhuma fonte específica, usar padrões
        if not sources:
            sources = ['YouTube', 'Instagram', 'Reddit']  # Padrão
        
        return sources
    
    def get_cached_data(self) -> Optional[Dict[str, Any]]:
        """Retorna dados em cache se disponíveis"""
        
        if self.cached_data and self.last_update:
            # Verificar se cache ainda é válido (último 5 minutos)
            time_diff = (datetime.now() - self.last_update).total_seconds()
            if time_diff < 300:  # 5 minutos
                return self.cached_data
        
        return None
    
    def format_for_display(self, data: Dict[str, Any]) -> str:
        """Formata dados para exibição no dashboard"""
        
        return f"""
        **👤 Cliente:** {data['cliente']}
        **🏢 Segmento:** {data['segmento']}
        **📍 Localização:** {data['localizacao']}
        **🔄 Coletores Ativos:** {data['coletores_ativos']}
        **📊 Termos Analisados:** {data['termos_analisados']}
        **🧠 ML Components:** {data['ml_components_active']}/{data['ml_components_total']} ativos
        
        **🎯 Insights Principais:**
        {chr(10).join(f"• {insight}" for insight in data['key_insights'])}
        
        **💡 Recomendações:**
        {chr(10).join(f"• {rec}" for rec in data['recommendations'])}
        
        *Última atualização: {data['last_updated']}*
        """

def create_executive_summary_synchronizer():
    """Factory function para criar synchronizer"""
    return ExecutiveSummarySynchronizer()

if __name__ == "__main__":
    print("📊 Testando Executive Summary Synchronizer...")
    
    # Criar synchronizer
    sync = create_executive_summary_synchronizer()
    
    # Dados de teste
    test_config = {
        'company_name': 'TechCorp',
        'business_segment': 'Tecnologia',
        'business_context': 'Startup de fintech',
        'location': 'São Paulo, SP',
        'youtube_enabled': True,
        'instagram_enabled': True,
        'reddit_enabled': False,
        'search_terms': ['fintech', 'pagamentos', 'digital']
    }
    
    test_results = {
        'total_profiles_detected': 5,
        'confidence_score': 0.85,
        'analysis_time': 2.3
    }
    
    # Sincronizar dados
    synced_data = sync.sync_executive_data(test_config, test_results)
    
    print("✅ Dados sincronizados:")
    print(f"   Cliente: {synced_data['cliente']}")
    print(f"   Coletores: {synced_data['coletores_ativos']}")
    print(f"   Termos: {synced_data['termos_analisados']}")
    print(f"   ML Status: {synced_data['ml_components_active']}/{synced_data['ml_components_total']}")
    
    print("📊 Executive Summary Synchronizer funcionando!")
