#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Brand Intelligence Analyzer - Analisa presença digital e gera insights de vendas
Conecta dados das plataformas + Twin Engine para recomendar estratégias
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter

# Adicionar paths
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from core.advanced_analytics.brazilian_cultural_twin_v9 import BrazilianCulturalTwinV9, REGIOES_BRASIL
    TWIN_AVAILABLE = True
except ImportError:
    TWIN_AVAILABLE = False


@dataclass
class BrandHealthScore:
    """Score de saúde da marca por plataforma"""
    platform: str
    visibility_score: float  # 0-100
    engagement_score: float  # 0-100
    growth_score: float  # 0-100
    conversion_score: float  # 0-100
    overall_score: float  # 0-100
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)


@dataclass
class AudienceInsight:
    """Insight sobre audiência da marca"""
    segment_name: str
    size_percentage: float
    engagement_level: str  # high, medium, low
    dominant_platform: str
    age_range: str
    social_class: str
    region: str
    cultural_circles: List[str] = field(default_factory=list)
    content_preferences: List[str] = field(default_factory=list)


@dataclass
class SalesOpportunity:
    """Oportunidade de vendas identificada"""
    opportunity_type: str  # product_launch, market_expansion, content_strategy, etc
    priority: str  # high, medium, low
    estimated_impact: str  # revenue increase, engagement boost, etc
    target_audience: str
    recommended_actions: List[str] = field(default_factory=list)
    platforms_to_leverage: List[str] = field(default_factory=list)
    timeline: str
    estimated_roi: float
    confidence_score: float


@dataclass
class CompetitiveIntelligence:
    """Inteligência competitiva"""
    market_position: str  # leader, challenger, follower, nicher
    visibility_vs_market: float  # -100 to +100
    engagement_vs_market: float
    content_gap_analysis: List[str] = field(default_factory=list)
    untapped_opportunities: List[str] = field(default_factory=list)


class BrandIntelligenceAnalyzer:
    """Analisador de inteligência de marca"""
    
    def __init__(self):
        if TWIN_AVAILABLE:
            self.twin_engine = BrazilianCulturalTwinV9()
        else:
            self.twin_engine = None
    
    # ===== ANÁLISE DE SAÚDE DA MARCA =====
    
    def analyze_brand_health(
        self,
        platform_data: Dict[str, Any]
    ) -> Dict[str, BrandHealthScore]:
        """
        Analisa saúde da marca em cada plataforma
        """
        
        health_scores = {}
        
        for platform_name, data in platform_data.items():
            
            if platform_name == 'gmb':
                score = self._analyze_gmb_health(data)
            elif platform_name == 'shopping':
                score = self._analyze_shopping_health(data)
            elif platform_name == 'instagram':
                score = self._analyze_instagram_health(data)
            elif platform_name == 'youtube':
                score = self._analyze_youtube_health(data)
            elif platform_name == 'trends':
                score = self._analyze_trends_health(data)
            else:
                continue
            
            health_scores[platform_name] = score
        
        return health_scores
    
    def _analyze_gmb_health(self, data) -> BrandHealthScore:
        """Analisa Google My Business"""
        
        # Visibility: baseado em buscas e visualizações
        total_views = data.views_maps + data.views_search
        visibility = min(100, (total_views / 10000) * 100)
        
        # Engagement: baseado em ações
        total_actions = data.actions_website + data.actions_calls + data.actions_directions
        engagement = min(100, (total_actions / 2000) * 100)
        
        # Growth: baseado em descoberta vs direto
        discovery_ratio = data.discovery_searches / max(1, data.total_searches)
        growth = discovery_ratio * 100
        
        # Conversion: baseado em rating e ações
        conversion = (data.reviews_avg_rating / 5) * 100
        
        overall = np.mean([visibility, engagement, growth, conversion])
        
        strengths = []
        weaknesses = []
        
        if data.reviews_avg_rating >= 4.0:
            strengths.append("Avaliações positivas dos clientes")
        else:
            weaknesses.append("Rating baixo - precisa melhorar experiência")
        
        if discovery_ratio > 0.4:
            strengths.append("Boa descoberta orgânica")
        else:
            weaknesses.append("Baixa descoberta - melhorar SEO local")
        
        if total_actions > 1000:
            strengths.append("Alto engajamento com ações")
        else:
            weaknesses.append("Poucas ações - otimizar CTA")
        
        return BrandHealthScore(
            platform='Google My Business',
            visibility_score=visibility,
            engagement_score=engagement,
            growth_score=growth,
            conversion_score=conversion,
            overall_score=overall,
            strengths=strengths,
            weaknesses=weaknesses
        )
    
    def _analyze_shopping_health(self, data) -> BrandHealthScore:
        """Analisa Google Shopping"""
        
        # Visibility: impressões
        visibility = min(100, (data.impressions / 100000) * 100)
        
        # Engagement: CTR
        engagement = min(100, (data.ctr / 5) * 100)
        
        # Growth: posição média
        growth = max(0, 100 - (data.avg_position * 5))
        
        # Conversion: taxa de conversão
        conv_rate = (data.conversions / max(1, data.clicks)) * 100
        conversion = min(100, conv_rate * 20)
        
        overall = np.mean([visibility, engagement, growth, conversion])
        
        strengths = []
        weaknesses = []
        
        if data.ctr > 3.0:
            strengths.append("CTR acima da média")
        else:
            weaknesses.append("CTR baixo - melhorar títulos e imagens")
        
        if data.avg_position < 10:
            strengths.append("Boa posição nos resultados")
        else:
            weaknesses.append("Posição baixa - aumentar bids ou relevância")
        
        if conv_rate > 2:
            strengths.append("Boa taxa de conversão")
        else:
            weaknesses.append("Conversão baixa - otimizar landing pages")
        
        return BrandHealthScore(
            platform='Google Shopping',
            visibility_score=visibility,
            engagement_score=engagement,
            growth_score=growth,
            conversion_score=conversion,
            overall_score=overall,
            strengths=strengths,
            weaknesses=weaknesses
        )
    
    def _analyze_instagram_health(self, data) -> BrandHealthScore:
        """Analisa Instagram"""
        
        # Visibility: seguidores
        visibility = min(100, (data.followers / 100000) * 100)
        
        # Engagement: taxa de engajamento
        engagement = min(100, (data.engagement_rate / 5) * 100)
        
        # Growth: taxa de crescimento
        growth = min(100, (data.growth_rate / 3) * 100)
        
        # Conversion: baseado em comentários e shares
        conversion = min(100, ((data.avg_comments + data.avg_shares) / 200) * 100)
        
        overall = np.mean([visibility, engagement, growth, conversion])
        
        strengths = []
        weaknesses = []
        
        if data.engagement_rate > 3.0:
            strengths.append("Engajamento acima da média")
        else:
            weaknesses.append("Engajamento baixo - criar conteúdo mais interativo")
        
        if data.growth_rate > 2.0:
            strengths.append("Crescimento orgânico saudável")
        else:
            weaknesses.append("Crescimento lento - considerar parcerias")
        
        if len(data.top_content) > 0:
            strengths.append(f"Tem {len(data.top_content)} conteúdos de destaque")
        
        return BrandHealthScore(
            platform='Instagram',
            visibility_score=visibility,
            engagement_score=engagement,
            growth_score=growth,
            conversion_score=conversion,
            overall_score=overall,
            strengths=strengths,
            weaknesses=weaknesses
        )
    
    def _analyze_youtube_health(self, data) -> BrandHealthScore:
        """Analisa YouTube"""
        
        # Visibility: inscritos
        visibility = min(100, (data.followers / 50000) * 100)
        
        # Engagement: taxa de engajamento
        engagement = min(100, (data.engagement_rate / 5) * 100)
        
        # Growth: taxa de crescimento
        growth = min(100, (data.growth_rate / 3) * 100)
        
        # Conversion: baseado em watch time implícito
        conversion = min(100, (data.avg_views / 10000) * 100)
        
        overall = np.mean([visibility, engagement, growth, conversion])
        
        strengths = []
        weaknesses = []
        
        if data.avg_views > 5000:
            strengths.append("Boa média de visualizações")
        else:
            weaknesses.append("Visualizações baixas - otimizar thumbnails e títulos")
        
        if data.engagement_rate > 2.0:
            strengths.append("Audiência engajada")
        else:
            weaknesses.append("Baixo engajamento - criar CTAs no vídeo")
        
        return BrandHealthScore(
            platform='YouTube',
            visibility_score=visibility,
            engagement_score=engagement,
            growth_score=growth,
            conversion_score=conversion,
            overall_score=overall,
            strengths=strengths,
            weaknesses=weaknesses
        )
    
    def _analyze_trends_health(self, trends_data: Dict) -> BrandHealthScore:
        """Analisa Google Trends (agregado de keywords)"""
        
        avg_interest = np.mean([data.avg_interest for data in trends_data.values()])
        
        rising_count = sum(1 for data in trends_data.values() if data.trend_direction == 'rising')
        falling_count = sum(1 for data in trends_data.values() if data.trend_direction == 'falling')
        
        # Visibility: interesse médio
        visibility = avg_interest
        
        # Engagement: número de queries relacionadas
        total_related = sum(len(data.related_queries) for data in trends_data.values())
        engagement = min(100, (total_related / 20) * 100)
        
        # Growth: tendências crescentes
        growth = (rising_count / len(trends_data)) * 100
        
        # Conversion: queries em alta
        total_rising = sum(len(data.rising_queries) for data in trends_data.values())
        conversion = min(100, (total_rising / 15) * 100)
        
        overall = np.mean([visibility, engagement, growth, conversion])
        
        strengths = []
        weaknesses = []
        
        if rising_count > falling_count:
            strengths.append(f"{rising_count} keywords em alta")
        else:
            weaknesses.append(f"{falling_count} keywords em queda - revisar estratégia")
        
        if avg_interest > 60:
            strengths.append("Alto interesse de busca")
        else:
            weaknesses.append("Interesse baixo - aumentar awareness")
        
        return BrandHealthScore(
            platform='Google Trends',
            visibility_score=visibility,
            engagement_score=engagement,
            growth_score=growth,
            conversion_score=conversion,
            overall_score=overall,
            strengths=strengths,
            weaknesses=weaknesses
        )
    
    # ===== ANÁLISE DE AUDIÊNCIA =====
    
    def analyze_audience_segments(
        self,
        platform_data: Dict[str, Any]
    ) -> List[AudienceInsight]:
        """
        Identifica e analisa segmentos de audiência
        """
        
        segments = []
        
        # Agregar dados demográficos de todas as plataformas
        all_age_data = {}
        platform_followers = {}
        
        for platform_name, data in platform_data.items():
            if platform_name in ['instagram', 'youtube']:
                platform_followers[platform_name] = data.followers
                
                if 'age_ranges' in data.audience_demographics:
                    for age_range, percentage in data.audience_demographics['age_ranges'].items():
                        if age_range not in all_age_data:
                            all_age_data[age_range] = []
                        all_age_data[age_range].append({
                            'platform': platform_name,
                            'percentage': percentage
                        })
        
        # Criar insights por faixa etária
        for age_range, platforms_data in all_age_data.items():
            # Encontrar plataforma dominante
            dominant = max(platforms_data, key=lambda x: x['percentage'])
            
            # Calcular tamanho médio do segmento
            avg_percentage = np.mean([p['percentage'] for p in platforms_data])
            
            # Determinar nível de engajamento
            if avg_percentage > 30:
                engagement = 'high'
            elif avg_percentage > 15:
                engagement = 'medium'
            else:
                engagement = 'low'
            
            # Mapear para classe social (estimativa)
            if age_range in ['18-24', '13-17']:
                social_class = 'C'
            elif age_range in ['25-34', '35-44']:
                social_class = 'B'
            else:
                social_class = 'C'
            
            # Criar insight
            segment = AudienceInsight(
                segment_name=f"Público {age_range} anos",
                size_percentage=avg_percentage,
                engagement_level=engagement,
                dominant_platform=dominant['platform'],
                age_range=age_range,
                social_class=social_class,
                region='Sudeste',  # Padrão - melhorar com dados regionais
                cultural_circles=self._map_age_to_circles(age_range),
                content_preferences=self._map_age_to_content(age_range)
            )
            
            segments.append(segment)
        
        # Ordenar por tamanho
        segments.sort(key=lambda x: x.size_percentage, reverse=True)
        
        return segments
    
    def _map_age_to_circles(self, age_range: str) -> List[str]:
        """Mapeia faixa etária para círculos culturais prováveis"""
        
        mapping = {
            '13-17': ['tecnologia_inovacao', 'musica_festivais', 'moda_identidade'],
            '18-24': ['musica_festivais', 'esportes_competicao', 'tecnologia_inovacao'],
            '25-34': ['carreira_empreendedorismo', 'relacionamentos_amor', 'consumo_consciente'],
            '35-44': ['familia_tradicoes', 'saude_bemestar', 'educacao_cultura'],
            '45-54': ['familia_tradicoes', 'espiritualidade_fe', 'comunidade_local'],
            '55+': ['familia_tradicoes', 'saude_bemestar', 'espiritualidade_fe']
        }
        
        return mapping.get(age_range, ['familia_tradicoes'])
    
    def _map_age_to_content(self, age_range: str) -> List[str]:
        """Mapeia faixa etária para preferências de conteúdo"""
        
        mapping = {
            '13-17': ['Reels curtos', 'TikTok trends', 'Memes', 'Challenges'],
            '18-24': ['Stories interativos', 'Tutoriais', 'Behind the scenes', 'UGC'],
            '25-34': ['Dicas práticas', 'Testemunhos', 'Comparações', 'Reviews'],
            '35-44': ['Guias completos', 'Estudos de caso', 'Webinars', 'Expert content'],
            '45-54': ['Conteúdo educativo', 'Vídeos longos', 'Entrevistas', 'Explicativos'],
            '55+': ['Conteúdo tradicional', 'Passo a passo', 'Histórias reais', 'Depoimentos']
        }
        
        return mapping.get(age_range, ['Conteúdo genérico'])
    
    # ===== IDENTIFICAÇÃO DE OPORTUNIDADES =====
    
    def identify_sales_opportunities(
        self,
        platform_data: Dict[str, Any],
        health_scores: Dict[str, BrandHealthScore],
        audience_segments: List[AudienceInsight]
    ) -> List[SalesOpportunity]:
        """
        Identifica oportunidades de vendas baseadas nos dados
        """
        
        opportunities = []
        
        # Oportunidade 1: Expandir para plataforma sub-utilizada
        platform_scores = {name: score.overall_score for name, score in health_scores.items()}
        lowest_platform = min(platform_scores.items(), key=lambda x: x[1])
        
        if lowest_platform[1] < 50:
            opportunities.append(SalesOpportunity(
                opportunity_type='platform_expansion',
                priority='high',
                estimated_impact='20-30% aumento de alcance',
                target_audience=f'Público da {lowest_platform[0]}',
                recommended_actions=[
                    f'Criar estratégia específica para {lowest_platform[0]}',
                    'Adaptar conteúdo para formato da plataforma',
                    'Investir em ads iniciais para tração',
                    'Testar 3-5 formatos de conteúdo diferentes'
                ],
                platforms_to_leverage=[lowest_platform[0]],
                timeline='30-60 dias',
                estimated_roi=2.5,
                confidence_score=0.75
            ))
        
        # Oportunidade 2: Focar em segmento de alta engajamento
        high_engagement_segments = [s for s in audience_segments if s.engagement_level == 'high']
        
        if high_engagement_segments:
            top_segment = high_engagement_segments[0]
            
            opportunities.append(SalesOpportunity(
                opportunity_type='audience_deepening',
                priority='high',
                estimated_impact='15-25% aumento de conversão',
                target_audience=top_segment.segment_name,
                recommended_actions=[
                    f'Criar linha de produtos para {top_segment.age_range}',
                    f'Focar conteúdo em {top_segment.dominant_platform}',
                    f'Criar campanhas sobre: {", ".join(top_segment.cultural_circles[:2])}',
                    'Desenvolver programa de embaixadores nesse segmento'
                ],
                platforms_to_leverage=[top_segment.dominant_platform],
                timeline='45-90 dias',
                estimated_roi=3.2,
                confidence_score=0.85
            ))
        
        # Oportunidade 3: Aproveitar tendências em alta
        if 'trends' in platform_data:
            rising_trends = []
            for keyword, data in platform_data['trends'].items():
                if data.trend_direction == 'rising':
                    rising_trends.append((keyword, data.avg_interest))
            
            if rising_trends:
                top_trend = max(rising_trends, key=lambda x: x[1])
                
                opportunities.append(SalesOpportunity(
                    opportunity_type='trend_capitalization',
                    priority='medium',
                    estimated_impact='10-20% aumento de tráfego orgânico',
                    target_audience='Buscadores ativos',
                    recommended_actions=[
                        f'Criar conteúdo sobre "{top_trend[0]}"',
                        'Otimizar SEO para keyword em alta',
                        'Lançar campanha de awareness',
                        'Criar landing page específica'
                    ],
                    platforms_to_leverage=['google_shopping', 'instagram', 'youtube'],
                    timeline='14-30 dias',
                    estimated_roi=2.8,
                    confidence_score=0.70
                ))
        
        # Oportunidade 4: Melhorar conversão em Google Shopping
        if 'shopping' in platform_data:
            shopping_data = platform_data['shopping']
            
            if shopping_data.ctr < 3.0 or shopping_data.avg_position > 10:
                opportunities.append(SalesOpportunity(
                    opportunity_type='conversion_optimization',
                    priority='high',
                    estimated_impact='30-50% aumento de conversões',
                    target_audience='Compradores em busca ativa',
                    recommended_actions=[
                        'Melhorar qualidade de imagens dos produtos',
                        'Otimizar títulos com keywords de alta conversão',
                        'Aumentar bids nos produtos top',
                        'Adicionar reviews e ratings',
                        'Criar promoções específicas'
                    ],
                    platforms_to_leverage=['google_shopping'],
                    timeline='15-30 dias',
                    estimated_roi=4.5,
                    confidence_score=0.90
                ))
        
        # Oportunidade 5: Alavancar GMB para vendas locais
        if 'gmb' in platform_data:
            gmb_data = platform_data['gmb']
            
            if gmb_data.actions_directions > gmb_data.actions_website:
                opportunities.append(SalesOpportunity(
                    opportunity_type='local_sales_boost',
                    priority='medium',
                    estimated_impact='25-40% aumento de visitas à loja',
                    target_audience='Público local/proximidade',
                    recommended_actions=[
                        'Criar promoções exclusivas para quem visita',
                        'Adicionar posts semanais no GMB',
                        'Oferecer "Retirada em loja" com desconto',
                        'Incentivar check-ins e reviews',
                        'Criar eventos presenciais mensais'
                    ],
                    platforms_to_leverage=['gmb'],
                    timeline='30-60 dias',
                    estimated_roi=3.5,
                    confidence_score=0.80
                ))
        
        # Ordenar por prioridade e ROI
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        opportunities.sort(
            key=lambda x: (priority_order[x.priority], x.estimated_roi),
            reverse=True
        )
        
        return opportunities
    
    # ===== INTELIGÊNCIA COMPETITIVA =====
    
    def analyze_competitive_position(
        self,
        health_scores: Dict[str, BrandHealthScore],
        market_benchmarks: Optional[Dict[str, float]] = None
    ) -> CompetitiveIntelligence:
        """
        Analisa posição competitiva (requer dados de mercado)
        """
        
        # Benchmarks padrão de mercado (médias do setor)
        if market_benchmarks is None:
            market_benchmarks = {
                'instagram_engagement': 2.5,
                'youtube_views': 5000,
                'shopping_ctr': 2.5,
                'gmb_rating': 4.0
            }
        
        # Calcular score geral da marca
        overall_brand_score = np.mean([score.overall_score for score in health_scores.values()])
        
        # Determinar posição no mercado
        if overall_brand_score >= 80:
            position = 'leader'
        elif overall_brand_score >= 60:
            position = 'challenger'
        elif overall_brand_score >= 40:
            position = 'follower'
        else:
            position = 'nicher'
        
        # Análise de gaps de conteúdo
        content_gaps = []
        for platform, score in health_scores.items():
            if score.overall_score < 60:
                content_gaps.extend(score.weaknesses)
        
        # Oportunidades não exploradas
        untapped = []
        for platform, score in health_scores.items():
            if score.visibility_score < 50:
                untapped.append(f"Aumentar visibilidade em {platform}")
            if score.engagement_score < 50:
                untapped.append(f"Melhorar engajamento em {platform}")
        
        return CompetitiveIntelligence(
            market_position=position,
            visibility_vs_market=10.0,  # Placeholder
            engagement_vs_market=5.0,  # Placeholder
            content_gap_analysis=content_gaps[:5],
            untapped_opportunities=list(set(untapped))[:5]
        )
    
    # ===== GERADOR DE RELATÓRIO COMPLETO =====
    
    def generate_complete_report(
        self,
        brand_name: str,
        platform_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Gera relatório completo de inteligência da marca
        """
        
        print(f"📊 Analisando presença digital de {brand_name}...")
        
        # 1. Saúde da marca
        health_scores = self.analyze_brand_health(platform_data)
        
        # 2. Segmentos de audiência
        audience_segments = self.analyze_audience_segments(platform_data)
        
        # 3. Oportunidades de vendas
        sales_opportunities = self.identify_sales_opportunities(
            platform_data,
            health_scores,
            audience_segments
        )
        
        # 4. Inteligência competitiva
        competitive_intel = self.analyze_competitive_position(health_scores)
        
        # Compilar relatório
        report = {
            'brand_name': brand_name,
            'analysis_date': datetime.now().isoformat(),
            'overall_score': np.mean([score.overall_score for score in health_scores.values()]),
            'health_by_platform': {
                platform: {
                    'overall': score.overall_score,
                    'visibility': score.visibility_score,
                    'engagement': score.engagement_score,
                    'growth': score.growth_score,
                    'conversion': score.conversion_score,
                    'strengths': score.strengths,
                    'weaknesses': score.weaknesses
                }
                for platform, score in health_scores.items()
            },
            'audience_segments': [
                {
                    'name': seg.segment_name,
                    'size': seg.size_percentage,
                    'engagement': seg.engagement_level,
                    'platform': seg.dominant_platform,
                    'age_range': seg.age_range,
                    'social_class': seg.social_class,
                    'cultural_circles': seg.cultural_circles,
                    'content_preferences': seg.content_preferences
                }
                for seg in audience_segments
            ],
            'sales_opportunities': [
                {
                    'type': opp.opportunity_type,
                    'priority': opp.priority,
                    'impact': opp.estimated_impact,
                    'target': opp.target_audience,
                    'actions': opp.recommended_actions,
                    'platforms': opp.platforms_to_leverage,
                    'timeline': opp.timeline,
                    'roi': opp.estimated_roi,
                    'confidence': opp.confidence_score
                }
                for opp in sales_opportunities
            ],
            'competitive_intelligence': {
                'position': competitive_intel.market_position,
                'visibility_vs_market': competitive_intel.visibility_vs_market,
                'engagement_vs_market': competitive_intel.engagement_vs_market,
                'content_gaps': competitive_intel.content_gap_analysis,
                'untapped_opportunities': competitive_intel.untapped_opportunities
            },
            'top_3_priorities': [
                {
                    'title': opp.opportunity_type.replace('_', ' ').title(),
                    'why': opp.estimated_impact,
                    'how': opp.recommended_actions[0],
                    'when': opp.timeline
                }
                for opp in sales_opportunities[:3]
            ]
        }
        
        return report


def main():
    """Teste do analisador"""
    
    # Mock data de exemplo (viria do collector)
    mock_platform_data = {
        'instagram': type('obj', (object,), {
            'followers': 125340,
            'engagement_rate': 4.8,
            'growth_rate': 2.3,
            'avg_views': 15670,
            'avg_likes': 2340,
            'avg_comments': 156,
            'avg_shares': 89,
            'audience_demographics': {
                'age_ranges': {
                    '18-24': 32.4,
                    '25-34': 38.9,
                    '35-44': 15.6
                }
            }
        })(),
        'shopping': type('obj', (object,), {
            'impressions': 125340,
            'clicks': 4520,
            'ctr': 3.6,
            'avg_position': 8.4,
            'conversions': 234
        })()
    }
    
    analyzer = BrandIntelligenceAnalyzer()
    report = analyzer.generate_complete_report('Marca Exemplo', mock_platform_data)
    
    print(f"\n✅ Relatório gerado!")
    print(f"   Score geral: {report['overall_score']:.1f}/100")
    print(f"   Oportunidades identificadas: {len(report['sales_opportunities'])}")
    print(f"   Segmentos de audiência: {len(report['audience_segments'])}")


if __name__ == "__main__":
    main()
