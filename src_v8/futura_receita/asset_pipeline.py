from typing import Dict, List, Optional
import logging
from .models import CulturalAsset, RefinedAsset, AssetAnalysisResult
from .cultural_asset_refiner import CulturalAssetRefiner
from core.advanced_analytics.social_media_analyzer import SocialMediaAnalyzer

logger = logging.getLogger(__name__)

class AssetAnalysisPipeline:
    """Pipeline completo para análise de assets culturais"""
    
    def __init__(self):
        """Inicializar componentes do pipeline"""
        self.asset_refiner = CulturalAssetRefiner()
        self.social_analyzer = SocialMediaAnalyzer()
    
    async def process_asset(self, 
                          asset: CulturalAsset,
                          brand_context: Dict[str, any]) -> AssetAnalysisResult:
        """Processar asset cultural completo"""
        try:
            # 1. Refinamento inicial do asset
            refined_asset = await self.asset_refiner.refine_asset(
                asset,
                brand_context
            )
            
            # 2. Análise social se necessária
            social_impact = None
            if brand_context.get('social_validation_required', False):
                social_impact = await self._analyze_social_impact(
                    refined_asset,
                    brand_context
                )
            
            # 3. Gerar recomendações finais
            recommendations = self._generate_final_recommendations(
                refined_asset,
                social_impact
            )
            
            # 4. Calcular métricas finais
            metrics = self._calculate_metrics(
                refined_asset,
                social_impact
            )
            
            # 5. Gerar insights
            insights = self._generate_insights(
                refined_asset,
                social_impact,
                metrics
            )
            
            return AssetAnalysisResult(
                asset=refined_asset,
                social_impact=social_impact,
                recommendations=recommendations,
                metrics=metrics,
                insights=insights
            )
            
        except Exception as e:
            logger.error(f"Erro no processamento do asset: {e}")
            return AssetAnalysisResult(
                asset=refined_asset,
                recommendations=["Erro no processamento completo do asset"]
            )
    
    async def _analyze_social_impact(self,
                                   refined_asset: RefinedAsset,
                                   brand_context: Dict) -> Dict[str, any]:
        """Analisar potencial impacto social do asset"""
        try:
            return await self.social_analyzer.analyze_potential_impact(
                content=refined_asset.original_asset.content,
                image_data=refined_asset.original_asset.image_data,
                target_audience=brand_context.get('target_audience', ''),
                platform=brand_context.get('social_platform', 'general')
            )
        except Exception as e:
            logger.error(f"Erro na análise social: {e}")
            return {}
    
    def _generate_final_recommendations(self,
                                      refined_asset: RefinedAsset,
                                      social_impact: Optional[Dict]) -> List[str]:
        """Gerar recomendações finais combinadas"""
        recommendations = []
        
        # Recomendações do refinamento
        recommendations.extend(refined_asset.recommendations)
        
        # Recomendações baseadas no impacto social
        if social_impact:
            if 'recommendations' in social_impact:
                recommendations.extend(social_impact['recommendations'])
        
        return list(set(recommendations))  # Remover duplicatas
    
    def _calculate_metrics(self,
                         refined_asset: RefinedAsset,
                         social_impact: Optional[Dict]) -> Dict[str, float]:
        """Calcular métricas finais do asset"""
        metrics = {
            'compliance_score': refined_asset.compliance_score,
            'cultural_score': refined_asset.cultural_score,
            'overall_quality': (refined_asset.compliance_score + refined_asset.cultural_score) / 2
        }
        
        if refined_asset.visual_score:
            metrics['visual_score'] = refined_asset.visual_score
        
        if social_impact:
            metrics['social_potential'] = social_impact.get('impact_score', 0.0)
            metrics['engagement_prediction'] = social_impact.get('engagement_prediction', 0.0)
        
        return metrics
    
    def _generate_insights(self,
                         refined_asset: RefinedAsset,
                         social_impact: Optional[Dict],
                         metrics: Dict[str, float]) -> List[str]:
        """Gerar insights baseados em todas as análises"""
        insights = []
        
        # Insights de qualidade
        if metrics['overall_quality'] >= 0.8:
            insights.append("Asset demonstra alta qualidade e alinhamento cultural")
        elif metrics['overall_quality'] < 0.6:
            insights.append("Asset necessita melhorias significativas")
        
        # Insights de impacto social
        if social_impact:
            engagement_pred = social_impact.get('engagement_prediction', 0.0)
            if engagement_pred >= 0.8:
                insights.append("Alto potencial de engajamento nas redes sociais")
            elif engagement_pred < 0.4:
                insights.append("Risco de baixo engajamento social")
        
        # Insights culturais
        if refined_asset.cultural_score >= 0.8:
            insights.append("Forte conexão com elementos culturais brasileiros")
        elif refined_asset.cultural_score < 0.6:
            insights.append("Oportunidade de fortalecer elementos culturais")
        
        return insights