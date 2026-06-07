"""
SEGMENT COMPARISON - SPRINT 4
Comparação de sinais entre diferentes segmentos usando Context Enricher

Permite CMO ver como o mesmo sinal cultural é percebido em contextos
de indústria diferentes, facilitando decisões de reposicionamento.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from core.contextual_intelligence_engine import ContextualIntelligenceEngine
    CONTEXT_ENGINE_AVAILABLE = True
except ImportError:
    CONTEXT_ENGINE_AVAILABLE = False


# Segmentos disponíveis (mesma lista do onboarding)
SEGMENTOS = [
    "Alimentação & Bebidas",
    "Entretenimento & Mídia",
    "Tecnologia & Inovação",
    "Moda & Beleza",
    "Educação & Cultura",
    "Esportes & Fitness",
    "Varejo & E-commerce",
    "Turismo & Hospitalidade",
    "Saúde & Bem-estar",
    "Finanças & Investimentos",
    "Imóveis & Construção",
    "Automotivo & Mobilidade",
    "Outro"
]


@dataclass
class SegmentAnalysis:
    """Resultado da análise de um sinal em um segmento específico"""
    segmento: str
    score: float
    relevancia: str  # "Alta", "Média", "Baixa"
    narrativas: List[str]
    circulos_relevantes: Dict[str, float]  # {círculo: score}
    territorio_cultural: str
    insights: List[str]
    delta_score: Optional[float] = None  # Diferença vs outro segmento


def analyze_signal_for_segment(
    signal: Any,
    segmento: str,
    objetivo: str = "Pesquisa de Mercado"
) -> SegmentAnalysis:
    """
    Analisa um sinal cultural com Context Enricher configurado para segmento específico.
    
    Args:
        signal: WeakSignal object
        segmento: Nome do segmento (ex: "Alimentação & Bebidas")
        objetivo: Objetivo de negócio
    
    Returns:
        SegmentAnalysis com análise contextualizada
    """
    
    # Extrair dados do sinal
    termo = getattr(signal, 'termo', getattr(signal, 'search_term', 'Desconhecido'))
    volume = getattr(signal, 'volume', 0)
    sentiment = getattr(signal, 'sentiment', 0.5)
    
    # Criar perfil temporário para o segmento
    temp_profile = {
        'segmento': segmento,
        'objetivo': objetivo,
        'brand_topic': termo
    }
    
    # Usar Context Enricher se disponível
    if CONTEXT_ENGINE_AVAILABLE:
        try:
            engine = ContextualIntelligenceEngine()
            
            # Configurar contexto
            business_context = {
                'segment': segmento,
                'challenge': objetivo,
                'target_audience': []
            }
            
            # Enriquecer sinal
            enriched = engine.enrich_signal(
                term=termo,
                volume=volume,
                sentiment=sentiment,
                business_context=business_context
            )
            
            # Extrair dados enriquecidos
            narrativas = [
                n.get('text', '') 
                for n in enriched.get('narratives', [])[:3]
            ]
            
            circulos = enriched.get('cultural_circles', {})
            territorio = enriched.get('cultural_territory', 'Não definido')
            
            # Calcular relevância baseada no score
            score = enriched.get('enrichment_score', 50.0)
            if score >= 70:
                relevancia = "Alta"
            elif score >= 50:
                relevancia = "Média"
            else:
                relevancia = "Baixa"
            
            # Gerar insights
            insights = []
            if score >= 70:
                insights.append(f"Sinal altamente relevante para {segmento}")
            if len(narrativas) > 0:
                insights.append(f"{len(narrativas)} narrativas culturais identificadas")
            if circulos:
                top_circulo = max(circulos.items(), key=lambda x: x[1])[0]
                insights.append(f"Círculo dominante: {top_circulo}")
            
            return SegmentAnalysis(
                segmento=segmento,
                score=score,
                relevancia=relevancia,
                narrativas=narrativas,
                circulos_relevantes=circulos,
                territorio_cultural=territorio,
                insights=insights
            )
            
        except Exception as e:
            logger.warning(f"Erro ao usar Context Enricher: {e}")
    
    # Fallback: Análise heurística
    score = (volume / 1000) * 50 + sentiment * 50  # Score simplificado
    score = min(score, 100)
    
    # Narrativas heurísticas baseadas no segmento
    narrativas_map = {
        "Alimentação & Bebidas": [
            f"Tendência gastronômica emergente relacionada a '{termo}'",
            "Potencial para inovação culinária",
            "Oportunidade de fusão regional"
        ],
        "Entretenimento & Mídia": [
            f"Conteúdo viral potencial sobre '{termo}'",
            "Oportunidade para criação de eventos",
            "Engajamento em redes sociais"
        ],
        "Tecnologia & Inovação": [
            f"Inovação tecnológica relacionada a '{termo}'",
            "Potencial para desenvolvimento de produto",
            "Solução digital emergente"
        ]
    }
    
    narrativas = narrativas_map.get(segmento, [
        f"Tendência emergente em {segmento}",
        f"Oportunidade de mercado para '{termo}'",
        "Sinal cultural em evolução"
    ])
    
    # Círculos heurísticos
    circulos = {
        "🎵 Música & Ritmos": 0.5,
        "🍖 Gastronomia Regional": 0.7 if "Alimentação" in segmento else 0.3,
        "📱 Digital & Inovação": 0.8 if "Tecnologia" in segmento else 0.4
    }
    
    relevancia = "Alta" if score >= 70 else "Média" if score >= 50 else "Baixa"
    
    insights = [
        f"Score {relevancia.lower()} para {segmento}",
        f"Volume de {volume:,} menções",
        f"Sentiment {sentiment*100:.0f}%"
    ]
    
    return SegmentAnalysis(
        segmento=segmento,
        score=score,
        relevancia=relevancia,
        narrativas=narrativas[:3],
        circulos_relevantes=circulos,
        territorio_cultural=f"Território cultural de {segmento}",
        insights=insights
    )


def compare_signal_across_segments(
    signal: Any,
    segment_a: str,
    segment_b: str
) -> Dict[str, SegmentAnalysis]:
    """
    Compara análise do mesmo sinal em 2 segmentos diferentes.
    
    Args:
        signal: WeakSignal object
        segment_a: Primeiro segmento
        segment_b: Segundo segmento
    
    Returns:
        Dict com análises para cada segmento
    """
    
    # Analisar para cada segmento
    analysis_a = analyze_signal_for_segment(signal, segment_a)
    analysis_b = analyze_signal_for_segment(signal, segment_b)
    
    # Calcular deltas
    analysis_a.delta_score = analysis_a.score - analysis_b.score
    analysis_b.delta_score = analysis_b.score - analysis_a.score
    
    return {
        'segment_a': analysis_a,
        'segment_b': analysis_b
    }
