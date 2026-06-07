#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TF-IDF Endpoints - Culture Pulse V8.0
Endpoints para análise TF-IDF cultural

🎯 FUNCIONALIDADES:
- Análise TF-IDF especializada em cultura brasileira
- Detecção de termos culturais relevantes
- Análise de tendências culturais
- Categorização de conteúdo cultural
"""

import sys
import os

# Adicionar path para imports absolutos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List, Optional
import logging

from api.models import TFIDFAnalysisRequest, TFIDFAnalysisResponse, ErrorResponse
from api.middleware.auth import get_current_client, ClientInfo
from core.Abas.Camada2_Presença_Cultura.tfidf_analyzer import TFIDFCulturalAnalyzer

logger = logging.getLogger(__name__)

# Criar router
tfidf_router = APIRouter()


@tfidf_router.post(
    "/analyze",
    response_model=TFIDFAnalysisResponse,
    summary="Análise TF-IDF Cultural",
    description="""
    **Executa análise TF-IDF especializada em termos culturais brasileiros**
    
    Analisa textos para identificar:
    - Relevância de termos culturais brasileiros
    - Tendências culturais emergentes
    - Categorização por aspectos culturais
    - Score de relevância cultural total
    
    ### Categorias Culturais Analisadas:
    - **Música**: samba, forró, MPB, funk, sertanejo
    - **Festividades**: carnaval, festa junina, ano novo
    - **Gastronomia**: feijoada, açaí, churrasco, coxinha
    - **Esportes**: futebol, vôlei, capoeira
    - **Religiosidade**: candomblé, umbanda, católica
    - **Regionalismo**: nordestino, carioca, paulista, gaúcho
    - **Tradições**: folclore, artesanato, literatura
    
    ### Parâmetros:
    - `content_texts`: Lista de textos para análise (mínimo 1)
    - `cultural_context`: Contexto cultural adicional (opcional)
    - `custom_terms`: Termos culturais customizados (opcional)
    """,
    responses={
        200: {"description": "Análise TF-IDF executada com sucesso"},
        400: {"description": "Textos inválidos ou insuficientes"},
        500: {"description": "Erro no processamento TF-IDF"}
    }
)
async def analyze_tfidf(
    request: TFIDFAnalysisRequest,
    current_client: ClientInfo = Depends(get_current_client)
):
    """Executar análise TF-IDF cultural"""
    
    try:
        logger.info(f"Análise TF-IDF - {len(request.content_texts)} textos - Cliente: {current_client.id}")
        
        # Validar entrada
        if not request.content_texts or len(request.content_texts) == 0:
            raise HTTPException(
                status_code=400,
                detail="Pelo menos um texto deve ser fornecido"
            )
        
        # Criar analisador TF-IDF
        analyzer = TFIDFCulturalAnalyzer()
        
        # Preparar dados para análise
        content_data = {
            "texts": request.content_texts,
            "context": request.cultural_context or {},
            "custom_terms": request.custom_terms or []
        }
        
        # Executar análise
        result = analyzer.analyze_cultural_relevance(
            content_data=content_data,
            circles_analysis={}  # Opcional para análise isolada
        )
        
        # Converter para formato da API
        response = _convert_tfidf_result(result, request.content_texts)
        
        logger.info(f"TF-IDF concluído - Relevância: {response['relevance_score']:.2f}")
        
        return response
        
    except Exception as e:
        logger.error(f"Erro na análise TF-IDF: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "tfidf_analysis_error",
                "message": str(e)
            }
        )


@tfidf_router.get(
    "/terms",
    summary="Termos Culturais Disponíveis",
    description="Lista todos os termos culturais utilizados na análise TF-IDF"
)
async def get_cultural_terms(
    category: Optional[str] = Query(None, description="Filtrar por categoria cultural"),
    current_client: ClientInfo = Depends(get_current_client)
):
    """Listar termos culturais disponíveis"""
    
    # Importar termos do analisador
    from core.Abas.Camada2_Presença_Cultura.tfidf_analyzer import TFIDFCulturalAnalyzer
    
    analyzer = TFIDFCulturalAnalyzer()
    
    # Obter categorias de termos (simulado - implementar no analyzer real)
    cultural_terms = {
        "musica": [
            "samba", "forró", "mpb", "bossa nova", "funk", "sertanejo",
            "axé", "pagode", "rock nacional", "música popular"
        ],
        "festividades": [
            "carnaval", "festa junina", "reveillon", "oktoberfest",
            "festa country", "micareta", "bumba meu boi"
        ],
        "gastronomia": [
            "feijoada", "açaí", "churrasco", "coxinha", "brigadeiro",
            "tapioca", "pão de açúcar", "cachaça", "guaraná"
        ],
        "esportes": [
            "futebol", "vôlei", "capoeira", "surf", "jiu-jitsu",
            "basquete", "handebol", "natação"
        ],
        "religiosidade": [
            "candomblé", "umbanda", "católica", "evangélica", "espírita",
            "sincretismo", "fé", "devoção", "santo", "orixá"
        ],
        "regionalismo": [
            "nordestino", "carioca", "paulista", "gaúcho", "mineiro",
            "baiano", "pernambucano", "amazônico", "pantaneiro"
        ],
        "tradicoes": [
            "folclore", "artesanato", "literatura", "cordel",
            "repente", "viola", "sanfona", "culinária típica"
        ]
    }
    
    if category:
        if category not in cultural_terms:
            available_categories = list(cultural_terms.keys())
            raise HTTPException(
                status_code=400,
                detail=f"Categoria inválida. Disponíveis: {available_categories}"
            )
        
        return {
            "category": category,
            "terms": cultural_terms[category],
            "total_terms": len(cultural_terms[category])
        }
    
    return {
        "total_categories": len(cultural_terms),
        "total_terms": sum(len(terms) for terms in cultural_terms.values()),
        "categories": cultural_terms
    }


@tfidf_router.post(
    "/batch",
    summary="Análise TF-IDF em Lote",
    description="Executa análise TF-IDF para múltiplos conjuntos de textos"
)
async def batch_tfidf_analysis(
    datasets: List[Dict[str, Any]],
    current_client: ClientInfo = Depends(get_current_client)
):
    """Análise TF-IDF em lote para múltiplos datasets"""
    
    if len(datasets) > 10:  # Limite para evitar sobrecarga
        raise HTTPException(
            status_code=400,
            detail="Máximo 10 datasets por requisição em lote"
        )
    
    try:
        analyzer = TFIDFCulturalAnalyzer()
        results = []
        
        for i, dataset in enumerate(datasets):
            if "texts" not in dataset:
                raise HTTPException(
                    status_code=400,
                    detail=f"Dataset {i+1} deve conter campo 'texts'"
                )
            
            # Executar análise para cada dataset
            result = analyzer.analyze_cultural_relevance(
                content_data=dataset,
                circles_analysis={}
            )
            
            # Converter resultado
            converted_result = _convert_tfidf_result(result, dataset["texts"])
            converted_result["dataset_id"] = dataset.get("id", f"dataset_{i+1}")
            
            results.append(converted_result)
        
        return {
            "total_datasets": len(datasets),
            "processed_successfully": len(results),
            "results": results,
            "summary": _generate_batch_summary(results)
        }
        
    except Exception as e:
        logger.error(f"Erro na análise em lote: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro no processamento em lote: {str(e)}"
        )


@tfidf_router.get(
    "/trends",
    summary="Tendências Culturais Detectadas",
    description="Retorna tendências culturais emergentes baseadas em análises recentes"
)
async def get_cultural_trends(
    period: str = Query("7d", description="Período de análise (1d, 7d, 30d)"),
    region: Optional[str] = Query(None, description="Filtrar por região"),
    current_client: ClientInfo = Depends(get_current_client)
):
    """Obter tendências culturais detectadas"""
    
    # Simulação de tendências (em produção, vir de análises reais)
    trends_data = {
        "7d": {
            "emerging_terms": [
                {"term": "sustentabilidade", "growth": 45.2, "category": "valores"},
                {"term": "música eletrônica", "growth": 32.1, "category": "musica"},
                {"term": "comida plant-based", "growth": 28.7, "category": "gastronomia"}
            ],
            "declining_terms": [
                {"term": "fast fashion", "decline": -23.1, "category": "moda"},
                {"term": "música sertaneja", "decline": -12.4, "category": "musica"}
            ],
            "regional_highlights": {
                "sudeste": ["sustentabilidade", "tecnologia", "arte urbana"],
                "nordeste": ["turismo cultural", "artesanato", "música regional"],
                "sul": ["gastronomia alemã", "ecoturismo", "tecnologia rural"]
            }
        }
    }
    
    if period not in trends_data:
        raise HTTPException(
            status_code=400,
            detail="Período inválido. Use: 1d, 7d, 30d"
        )
    
    data = trends_data[period]
    
    if region and region in data.get("regional_highlights", {}):
        return {
            "period": period,
            "region": region,
            "regional_trends": data["regional_highlights"][region],
            "analysis_date": "2025-01-24",
            "data_points": "simulated"
        }
    
    return {
        "period": period,
        "emerging_trends": data["emerging_terms"],
        "declining_trends": data["declining_terms"],
        "regional_highlights": data["regional_highlights"],
        "analysis_date": "2025-01-24",
        "total_analyses": "simulated"
    }


# Funções auxiliares
def _convert_tfidf_result(result: Dict[str, Any], original_texts: List[str]) -> Dict[str, Any]:
    """Converte resultado do analisador para formato da API"""
    
    return {
        "relevance_score": result.get("relevance_score", 0.0),
        "cultural_terms": result.get("cultural_terms", [])[:20],  # Top 20
        "trends": result.get("trends", []),
        "categories": result.get("categories", {}),
        "top_terms": [
            {"term": term, "score": 0.0}  # Implementar scores reais
            for term in result.get("cultural_terms", [])[:10]
        ]
    }


def _generate_batch_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Gera resumo da análise em lote"""
    
    if not results:
        return {"message": "Nenhum resultado para sumarizar"}
    
    # Calcular médias
    avg_relevance = sum(r["relevance_score"] for r in results) / len(results)
    
    # Contar termos únicos
    all_terms = set()
    for result in results:
        all_terms.update(result["cultural_terms"])
    
    return {
        "average_relevance_score": round(avg_relevance, 3),
        "unique_cultural_terms": len(all_terms),
        "total_trends_detected": sum(len(r["trends"]) for r in results),
        "most_relevant_dataset": max(results, key=lambda x: x["relevance_score"])["dataset_id"]
    }
