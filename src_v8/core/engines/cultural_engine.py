#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core Cultural Engine - Culture Pulse V8.0
Sistema principal de análise cultural brasileira refatorado

🎯 RESPONSABILIDADES:
- Orquestração de todos os componentes culturais
- Interface unificada para análise
- Gerenciamento de cache e performance
- Integração com APIs e processadores
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging

try:
    from .circles_processor import CulturalCirclesProcessor
except ImportError:
    from ..intelligence.circles_processor import CulturalCirclesProcessor

try:
    from .tfidf_analyzer import TFIDFCulturalAnalyzer
except ImportError:
    from ..classifiers.tfidf_analyzer import TFIDFCulturalAnalyzer

try:
    from .alma_brasileira import AlmaBrasileiraAnalyzer
except ImportError:
    from ..intelligence.alma_brasileira import AlmaBrasileiraAnalyzer

try:
    from .business_synthesizer import BusinessSynthesizer, BusinessContext
except ImportError:
    from ..intelligence.business_synthesizer import BusinessSynthesizer, BusinessContext
from .regional_engine import RegionalEngine

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CulturalAnalysisResult:
    """Resultado unificado de análise cultural"""
    client_id: str
    brand_name: str
    segment: str
    location: str
    demographics: Dict[str, Any]
    
    # Scores principais
    cultural_score: float  # Score total dos círculos culturais (0-1)
    alma_brasileira_score: float  # Score alma brasileira (0-1)
    tfidf_relevance: float  # Relevância TF-IDF (0-1)
    
    # Círculos culturais detalhados
    circles_analysis: Dict[str, Dict[str, Any]]
    dominant_circles: List[Tuple[str, float]]  # Top 5 círculos
    
    # Insights e tendências
    cultural_trends: List[str]
    recommendations: List[str]
    opportunities: List[str]
    
    # Metadados
    processing_time: float
    data_sources: List[str]
    confidence_level: float
    timestamp: str
    
    # Dados brutos para análise posterior
    raw_data: Dict[str, Any]

    # Dados regionais (V9.1)
    regional_analysis: List[Dict[str, Any]] = None


class CulturalEngine:
    """
    Engine principal do Culture Pulse V8.0
    Orquestra todos os componentes de análise cultural
    """
    
    def __init__(self):
        """Inicializa o engine cultural"""
        logger.info("🧠 Inicializando Culture Pulse V8.0 Engine")
        
        # Componentes principais
        self.circles_processor = CulturalCirclesProcessor()
        self.tfidf_analyzer = TFIDFCulturalAnalyzer()
        self.alma_analyzer = AlmaBrasileiraAnalyzer()
        self.business_synthesizer = BusinessSynthesizer()
        self.regional_engine = RegionalEngine()
        
        # Cache e performance
        self._analysis_cache = {}
        self._performance_metrics = {}
        
        logger.info("✅ Cultural Engine inicializado com sucesso")
    
    async def analyze_brand_culture(
        self,
        client_id: str,
        brand_name: str,
        segment: str,
        location: str,
        demographics: Dict[str, Any],
        search_terms: Optional[List[str]] = None,
        business_goal: Optional[str] = None,
        outlier_mode: bool = True, # Default True para V9.4
        collection_limit: int = 10,   # Proporcional ao Tier (V9.4)
        user_tier: str = "free" # Novo parâmetro para V9.9
    ) -> CulturalAnalysisResult:
        """
        Análise cultural completa com Data Mining de Nicho democratizado (V9.4).
        
        Args:
            client_id: ID do cliente
            brand_name: Nome da marca
            segment: Segmento
            location: Localização
            demographics: Dados demográficos
            search_terms: Termos específicos
            business_goal: Objetivo de negócio
            outlier_mode: Ativa mineração de nichos
            collection_limit: Volume máximo de sinais por Tier
            user_tier: Plano do usuário para orquestração e cache
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"🔍 Alma Brasileira V9.9: {brand_name} | Tier: {user_tier} | Outlier: {outlier_mode} | Limit: {collection_limit}")
            
            # --- FASE 1: CONSULTORIA E DEFINIÇÃO DE TERMOS ---
            refined_context = None
            if business_goal:
                refined_context = await self.business_synthesizer.analyze_business_context(business_goal)
                if not search_terms:
                    # Combinamos a marca com os "oportunidades buscadas" identificadas pela IA
                    search_terms = [brand_name] + refined_context.opportunities_sought
            
            # 1. Preparar termos de busca (Fallback se ainda estiver vazio)
            if not search_terms:
                search_terms = self._generate_search_terms(brand_name, segment)
            
            # 2. Coletar dados respeitando limites de Tier e modo de mineração
            raw_data = await self._collect_platform_data(
                search_terms, 
                location, 
                demographics, 
                outlier_mode=outlier_mode,
                collection_limit=collection_limit,
                user_tier=user_tier # Passando tier para coleta
            )
            
            # 3. Análise pelos círculos com novo motor de pesos (Entropy Weights)
            circles_analysis = self.circles_processor.analyze_cultural_circles(
                raw_data, segment, location
            )
            
            # 4. Análise TF-IDF cultural
            tfidf_analysis = self.tfidf_analyzer.analyze_cultural_relevance(
                raw_data, circles_analysis
            )
            
            # 5. Análise Alma Brasileira
            alma_analysis = self.alma_analyzer.analyze_alma_brasileira(
                raw_data, circles_analysis
            )
            
            # 6. Análise Regionalizada (V9.1)
            regional_predictions = self.regional_engine.predict(
                content=brand_name + " " + segment,
                theme=segment, # Simplificado para o tema principal
                target_circles=[c[0] for c in circles_analysis.get('top_circles', [])],
                brand_values=alma_analysis.get('detected_values', [])
            )
            regional_data = [p.to_dict() for p in regional_predictions]

            # 7. Consolidar resultados
            
            # P9 — Veracidade & Confiança Biográfica (Cálculo Agregado)
            # A confiança da análise é a média da acurácia de todos os sinais coletados
            all_signals = []
            for source_signals in raw_data.values():
                if isinstance(source_signals, list):
                    all_signals.extend(source_signals)
                else:
                    all_signals.append(source_signals)
            
            avg_accuracy = 0.0
            verified_count = 0
            if all_signals:
                total_acc = sum(getattr(s, 'accuracy_score', 0.0) for s in all_signals)
                avg_accuracy = total_acc / len(all_signals)
                verified_count = sum(1 for s in all_signals if getattr(s, 'is_verified', False))
            
            result = CulturalAnalysisResult(
                client_id=client_id,
                brand_name=brand_name,
                segment=segment,
                location=location,
                demographics=demographics,
                cultural_score=circles_analysis.get('overall_score', 0),
                alma_brasileira_score=alma_analysis.get('alma_score', 0),
                tfidf_relevance=tfidf_analysis.get('relevance_score', 0),
                circles_analysis=circles_analysis,
                dominant_circles=circles_analysis.get('top_circles', []),
                cultural_trends=tfidf_analysis.get('emerging_trends', []),
                recommendations=self._generate_recommendations(circles_analysis, alma_analysis, segment),
                opportunities=self._generate_opportunities(circles_analysis, location, demographics),
                regional_analysis=regional_data,
                processing_time=(datetime.now() - start_time).total_seconds(),
                data_sources=list(raw_data.keys()),
                confidence_level=avg_accuracy,  # P9 — Agora baseado na acurácia real dos dados
                timestamp=datetime.now().isoformat(),
                raw_data={
                    **raw_data,
                    'is_verified_aggregate': verified_count > (len(all_signals) / 2) if all_signals else False,
                    'accuracy_score': avg_accuracy
                }
            )
            
            # 8. Cache do resultado
            self._cache_result(result)
            
            logger.info(f"✅ Análise concluída: {brand_name} - Score: {result.cultural_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro na análise cultural: {e}")
            raise
    
    def _generate_search_terms(self, brand_name: str, segment: str) -> List[str]:
        """Gera termos de busca baseados na marca e segmento"""
        base_terms = [brand_name.lower()]
        
        # Termos por segmento
        segment_terms = {
            'calçados': ['tênis', 'sapato', 'sandália', 'chinelo'],
            'bebidas': ['cerveja', 'refrigerante', 'suco', 'energético'],
            'cosméticos': ['maquiagem', 'perfume', 'creme', 'shampoo'],
            'alimentação': ['comida', 'lanche', 'doce', 'salgado'],
            'moda': ['roupa', 'camisa', 'vestido', 'calça'],
            'tecnologia': ['celular', 'app', 'digital', 'tech']
        }
        
        if segment.lower() in segment_terms:
            base_terms.extend(segment_terms[segment.lower()])
        
        return base_terms
    
    async def _collect_platform_data(
        self, 
        search_terms: List[str], 
        location: str, 
        demographics: Dict[str, Any],
        outlier_mode: bool = True,
        collection_limit: int = 10,
        user_tier: str = "free" # Novo parâmetro para V9.9
    ) -> Dict[str, Any]:
        """Coleta dados reais-time das plataformas via OrchestratorV9"""
        
        try:
            # Selecionar o termo principal
            termo_principal = search_terms[0] if search_terms else "Cultura Brasileira"
            
            logger.info(f"📡 Real-time Coleta V9.9: {termo_principal} (Tier: {user_tier}, Outlier: {outlier_mode})")
            
            # Preparar o contexto completo para o orquestrador (V9.1 + V9.3 + V9.9)
            collection_context = {
                "location": location,
                "demographics": demographics,
                "additional_terms": search_terms[1:] if len(search_terms) > 1 else [],
                "user_tier": user_tier, # Tier real vindo da API
                "outlier_mode": outlier_mode,
                "collection_limit": collection_limit
            }
            
            from collectors.orchestrator import CulturalDataOrchestrator
            orchestrator = CulturalDataOrchestrator()
            raw_signals = await orchestrator.collect_comprehensive_data(
                termo=termo_principal,
                context=collection_context
            )
            
            # Formatar para o engine (compatibilidade CulturalSignal -> dict)
            formatted_data = {}
            for platform, signal in raw_signals.items():
                if hasattr(signal, 'to_dict'):
                    formatted_data[platform] = signal.to_dict()
                else:
                    formatted_data[platform] = signal # fallback se já for dict
            
            return formatted_data
            
        except Exception as e:
            logger.error(f"❌ Erro na coleta real-time: {e}")
            # Fallback seguro
            return {
                'youtube': {'videos': [], 'comments': [], 'metrics': {}},
                'reddit': {'posts': [], 'comments': [], 'metrics': {}},
                'spotify': {'tracks': [], 'playlists': [], 'metrics': {}},
                'news': {'articles': [], 'sentiment': [], 'metrics': {}},
                'ibge': {'demographics': [], 'social': [], 'metrics': {}},
                'instagram': {'posts': [], 'stories': [], 'metrics': {}},
                'meetup': {'events': [], 'groups': [], 'metrics': {}}
            }
    
    def _consolidate_analysis(
        self,
        client_id: str,
        brand_name: str,
        segment: str,
        location: str,
        demographics: Dict[str, Any],
        circles_analysis: Dict[str, Any],
        tfidf_analysis: Dict[str, Any],
        alma_analysis: Dict[str, Any],
        raw_data: Dict[str, Any],
        start_time: datetime
    ) -> CulturalAnalysisResult:
        """Consolida todos os resultados em um objeto final"""
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Calcular scores principais
        cultural_score = circles_analysis['overall_score']
        alma_score = alma_analysis['alma_score']
        tfidf_score = tfidf_analysis['relevance_score']
        
        # Círculos dominantes (top 5)
        dominant_circles = sorted(
            circles_analysis['circles_scores'].items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )[:5]
        
        # Gerar insights e recomendações
        recommendations = self._generate_recommendations(
            circles_analysis, alma_analysis, segment
        )
        
        opportunities = self._generate_opportunities(
            circles_analysis, location, demographics
        )
        
        return CulturalAnalysisResult(
            client_id=client_id,
            brand_name=brand_name,
            segment=segment,
            location=location,
            demographics=demographics,
            cultural_score=cultural_score,
            alma_brasileira_score=alma_score,
            tfidf_relevance=tfidf_score,
            circles_analysis=circles_analysis,
            dominant_circles=dominant_circles,
            cultural_trends=tfidf_analysis.get('trends', []),
            recommendations=recommendations,
            opportunities=opportunities,
            processing_time=processing_time,
            data_sources=list(raw_data.keys()),
            confidence_level=self._calculate_confidence(raw_data),
            timestamp=datetime.now().isoformat(),
            raw_data=raw_data
        )
    
    def _generate_recommendations(
        self,
        circles_analysis: Dict[str, Any],
        alma_analysis: Dict[str, Any],
        segment: str
    ) -> List[str]:
        """Gera recomendações estratégicas baseadas na análise"""
        recommendations = []
        
        # Baseado nos círculos dominantes
        top_circles = sorted(
            circles_analysis['circles_scores'].items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )[:3]
        
        for circle_name, circle_data in top_circles:
            if circle_name == 'alegria_celebracao' and circle_data['score'] > 0.8:
                recommendations.append("Apostar em campanhas festivas e celebrativas")
            elif circle_name == 'musicalidade_expressao' and circle_data['score'] > 0.8:
                recommendations.append("Integrar música e ritmos locais na comunicação")
            elif circle_name == 'afeto_hospitalidade' and circle_data['score'] > 0.8:
                recommendations.append("Enfatizar proximidade e relacionamento humano")
        
        return recommendations
    
    def _generate_opportunities(
        self,
        circles_analysis: Dict[str, Any],
        location: str,
        demographics: Dict[str, Any]
    ) -> List[str]:
        """Gera oportunidades de mercado baseadas na análise"""
        opportunities = []
        
        # Oportunidades baseadas na localização
        if 'Rio de Janeiro' in location:
            opportunities.append("Patrocínio de eventos de samba e música local")
            opportunities.append("Parcerias com influenciadores cariocas")
        
        # Oportunidades baseadas na demografia
        if demographics.get('faixa_etaria') == '18-25':
            opportunities.append("Campanhas em redes sociais com linguagem jovem")
        
        return opportunities
    
    def _calculate_confidence(self, raw_data: Dict[str, Any]) -> float:
        """Calcula nível de confiança baseado na qualidade dos dados"""
        # Implementar lógica de confiança baseada na quantidade e qualidade dos dados
        total_data_points = sum(len(platform_data) for platform_data in raw_data.values())
        return min(total_data_points / 1000, 1.0)  # Máximo 1.0
    
    def _cache_result(self, result: CulturalAnalysisResult):
        """Armazena resultado no cache para consultas futuras"""
        cache_key = f"{result.client_id}_{result.brand_name}_{result.segment}_{result.location}"
        self._analysis_cache[cache_key] = result
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de performance do engine"""
        return {
            'total_analyses': len(self._analysis_cache),
            'cache_size': len(self._analysis_cache),
            'avg_processing_time': self._calculate_avg_processing_time(),
            'engine_status': 'operational'
        }
    
    def _calculate_avg_processing_time(self) -> float:
        """Calcula tempo médio de processamento"""
        if not self._analysis_cache:
            return 0.0
        
        times = [result.processing_time for result in self._analysis_cache.values()]
        return sum(times) / len(times)


# Factory function para criar instância do engine
def create_cultural_engine() -> CulturalEngine:
    """Cria e retorna instância do Cultural Engine"""
    return CulturalEngine()


# Para testes diretos
if __name__ == "__main__":
    import asyncio
    
    async def test_engine():
        engine = create_cultural_engine()
        
        # Teste com marca Rider
        result = await engine.analyze_brand_culture(
            client_id="test_client",
            brand_name="Rider",
            segment="calçados",
            location="Rio de Janeiro - Periferia",
            demographics={
                "faixa_etaria": "18-35",
                "classe_social": "C/D",
                "genero": "Todos"
            }
        )
        
        print(f"🎯 Análise: {result.brand_name}")
        print(f"📊 Score Cultural: {result.cultural_score:.2f}")
        print(f"❤️ Alma Brasileira: {result.alma_brasileira_score:.2f}")
        print(f"🔝 Círculos Dominantes: {[c[0] for c in result.dominant_circles[:3]]}")
        print(f"💡 Recomendações: {len(result.recommendations)}")
        print("✅ Engine funcionando!")
    
    asyncio.run(test_engine())
