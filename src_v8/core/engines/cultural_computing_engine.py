"""
Cultural Computing Engine - Implementação baseada na pesquisa do MIT (2024)
Integra embeddings culturais regionais e análise de polaridade cultural vs comercial
"""

import torch
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

@dataclass
class CulturalEmbedding:
    """Representação vetorial de um elemento cultural"""
    term: str
    vector: np.ndarray
    region: str
    cultural_score: float
    commercial_score: float
    
@dataclass
class PolarityAnalysis:
    """Análise de polaridade cultural vs comercial"""
    cultural_score: float
    commercial_score: float
    balance_ratio: float
    recommendations: List[str]

class CulturalComputingEngine:
    """Engine principal para Cultural Computing"""
    
    def __init__(self, model_name: str = "neuralmind/bert-base-portuguese-cased"):
        """Inicializar engine com modelo de embeddings"""
        self.model = SentenceTransformer(model_name)
        self.region_embeddings = self._initialize_region_embeddings()
        self.cultural_markers = self._load_cultural_markers()
        self.commercial_markers = self._load_commercial_markers()
        
    def _initialize_region_embeddings(self) -> Dict[str, np.ndarray]:
        """Inicializar embeddings regionais"""
        regions = {
            "nordeste": [
                "forró", "baião", "cangaço", "bumba-meu-boi",
                "maracatu", "frevo", "capoeira", "acarajé"
            ],
            "norte": [
                "açaí", "tucupi", "boi-bumbá", "carimbó",
                "tacacá", "jambu", "círio", "pirarucu"
            ],
            "sudeste": [
                "samba", "funk", "feijoada", "carnaval",
                "moqueca", "pão de queijo", "congo", "jongo"
            ],
            "sul": [
                "chimarrão", "churrasco", "CTG", "vanera",
                "barreado", "tainha", "querência", "gaúcho"
            ],
            "centro-oeste": [
                "sertanejo", "pequi", "pantanal", "catira",
                "cururu", "pacu", "cerrado", "guaraná"
            ]
        }
        
        region_vectors = {}
        for region, terms in regions.items():
            embeddings = self.model.encode(terms)
            region_vectors[region] = np.mean(embeddings, axis=0)
            
        return region_vectors
        
    def _load_cultural_markers(self) -> List[str]:
        """Carregar marcadores culturais"""
        return [
            "tradição", "história", "ancestralidade", "ritual",
            "comunidade", "identidade", "patrimônio", "memória",
            "manifestação", "celebração", "sabedoria", "costume",
            "artesanato", "folclore", "expressão", "raiz"
        ]
        
    def _load_commercial_markers(self) -> List[str]:
        """Carregar marcadores comerciais"""
        return [
            "venda", "mercado", "produto", "marca",
            "campanha", "marketing", "negócio", "consumo",
            "cliente", "público-alvo", "estratégia", "ROI",
            "conversão", "métrica", "resultado", "performance"
        ]
        
    def analyze_content_polarity(self, content: str) -> PolarityAnalysis:
        """Analisar polaridade cultural vs comercial do conteúdo"""
        content_embedding = self.model.encode(content)
        
        # Calcular similaridade com marcadores culturais
        cultural_embeddings = self.model.encode(self.cultural_markers)
        cultural_sim = np.mean(cosine_similarity(
            [content_embedding], cultural_embeddings)[0])
        
        # Calcular similaridade com marcadores comerciais
        commercial_embeddings = self.model.encode(self.commercial_markers)
        commercial_sim = np.mean(cosine_similarity(
            [content_embedding], commercial_embeddings)[0])
        
        # Calcular ratio de equilíbrio
        total = cultural_sim + commercial_sim
        balance = cultural_sim / total if total > 0 else 0.5
        
        # Gerar recomendações
        recommendations = self._generate_polarity_recommendations(
            cultural_sim, commercial_sim)
            
        return PolarityAnalysis(
            cultural_score=cultural_sim,
            commercial_score=commercial_sim,
            balance_ratio=balance,
            recommendations=recommendations
        )
        
    def generate_regional_embedding(self, content: str) -> Dict[str, float]:
        """Gerar embedding regional para o conteúdo"""
        content_embedding = self.model.encode(content)
        
        # Calcular similaridade com cada região
        regional_scores = {}
        for region, region_embedding in self.region_embeddings.items():
            similarity = float(cosine_similarity(
                [content_embedding], [region_embedding])[0][0])
            regional_scores[region] = similarity
            
        return regional_scores
        
    def _generate_polarity_recommendations(self,
                                         cultural_score: float,
                                         commercial_score: float) -> List[str]:
        """Gerar recomendações baseadas na análise de polaridade"""
        recommendations = []
        
        if cultural_score < 0.3:
            recommendations.extend([
                "Incorporar mais elementos de tradição cultural brasileira",
                "Adicionar referências a rituais e costumes locais",
                "Incluir expressões culturais autênticas"
            ])
            
        if commercial_score > 0.7:
            recommendations.extend([
                "Reduzir linguagem excessivamente comercial",
                "Equilibrar mensagem promocional com valor cultural",
                "Focar mais na experiência cultural que na venda"
            ])
            
        if 0.4 <= cultural_score <= 0.6 and 0.4 <= commercial_score <= 0.6:
            recommendations.append(
                "Manter o equilíbrio atual entre cultura e comercial")
                
        return recommendations[:3]  # Retornar top 3 recomendações
        
    def enrich_cultural_asset(self, asset: Dict) -> Dict:
        """Enriquecer asset cultural com análises do Cultural Computing"""
        try:
            # Analisar polaridade
            polarity = self.analyze_content_polarity(asset['content'])
            
            # Analisar contexto regional
            regional_context = self.generate_regional_embedding(asset['content'])
            
            # Adicionar resultados ao asset
            asset['cultural_computing'] = {
                'polarity_analysis': {
                    'cultural_score': polarity.cultural_score,
                    'commercial_score': polarity.commercial_score,
                    'balance_ratio': polarity.balance_ratio,
                    'recommendations': polarity.recommendations
                },
                'regional_context': regional_context
            }
            
            return asset
            
        except Exception as e:
            logger.error(f"Erro ao enriquecer asset: {e}")
            return asset