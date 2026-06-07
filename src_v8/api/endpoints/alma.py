#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alma Brasileira Endpoints - Culture Pulse V8.0
Endpoints para análise da Alma Brasileira

🎯 FUNCIONALIDADES:
- Análise da autenticidade cultural brasileira
- Medição de valores e características nacionais
- Conexão regional com a essência brasileira
- Insights de comunicação autêntica
"""

import sys
import os

# Adicionar path para imports absolutos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List, Optional
import logging

from api.models import AlmaAnalysisRequest, AlmaAnalysisResponse, ErrorResponse
from api.middleware.auth import get_current_client, ClientInfo
from core.alma_brasileira import AlmaBrasileiraAnalyzer

logger = logging.getLogger(__name__)

# Criar router
alma_router = APIRouter()


@alma_router.post(
    "/analyze",
    response_model=AlmaAnalysisResponse,
    summary="Análise da Alma Brasileira",
    description="""
    **Executa análise da autenticidade e essência cultural brasileira**
    
    Mede o quão autêntico e conectado com a alma brasileira 
    está um conteúdo, marca ou comunicação.
    
    ### Os 7 Valores da Alma Brasileira:
    
    1. **Alegre e Festivo** (peso 1.3)
       - Tendência à celebração e otimismo
       - Capacidade de encontrar alegria nas situações
    
    2. **Criativo e Improvisador** (peso 1.2)
       - Habilidade de improvisar e criar soluções
       - "Jeitinho brasileiro" como expressão cultural
    
    3. **Acolhedor e Hospitaleiro** (peso 1.1)
       - Calor humano e receptividade
       - Cultura da hospitalidade genuína
    
    4. **Resiliente e Persistente** (peso 1.0)
       - Capacidade de superar adversidades
       - Otimismo diante das dificuldades
    
    5. **Sensual e Expressivo** (peso 0.9)
       - Expressão corporal e sensualidade
       - Comunicação através do corpo e gestos
    
    6. **Musical e Ritmado** (peso 0.8)
       - Conexão natural com música e ritmo
       - Expressão através da musicalidade
    
    7. **Místico e Spiritual** (peso 0.7)
       - Dimensão espiritual e transcendente
       - Sincretismo religioso e crenças
    
    ### Retorno:
    - Score de autenticidade (0-1)
    - Intensidade da alma brasileira
    - Valores dominantes identificados
    - Conexão regional específica
    - Insights para comunicação autêntica
    """,
    responses={
        200: {"description": "Análise da Alma Brasileira executada"},
        400: {"description": "Dados de conteúdo inválidos"},
        500: {"description": "Erro no processamento"}
    }
)
async def analyze_alma(
    request: AlmaAnalysisRequest,
    current_client: ClientInfo = Depends(get_current_client)
):
    """Executar análise da Alma Brasileira"""
    
    try:
        logger.info(f"Análise Alma Brasileira - Cliente: {current_client.id}")
        
        # Criar analisador
        analyzer = AlmaBrasileiraAnalyzer()
        
        # Executar análise
        result = analyzer.analyze_alma_brasileira(
            content_data=request.content_data,
            circles_analysis={},  # Opcional para análise isolada
            regional_focus=request.regional_focus
        )
        
        # Converter para formato da API
        response = _convert_alma_result(result)
        
        logger.info(f"Alma Brasileira analisada - Score: {response['alma_score']:.2f}")
        
        return response
        
    except Exception as e:
        logger.error(f"Erro na análise da Alma Brasileira: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "alma_analysis_error",
                "message": str(e)
            }
        )


@alma_router.get(
    "/values",
    summary="Valores da Alma Brasileira",
    description="Lista detalhada dos 7 valores fundamentais da Alma Brasileira"
)
async def get_alma_values(
    include_examples: bool = Query(True, description="Incluir exemplos de cada valor"),
    current_client: ClientInfo = Depends(get_current_client)
):
    """Listar valores da Alma Brasileira"""
    
    values = {
        "alegre_festivo": {
            "name": "Alegre e Festivo",
            "weight": 1.3,
            "description": "Tendência natural à celebração e otimismo brasileiro",
            "keywords": ["festa", "alegria", "celebração", "otimismo", "diversão"],
            "examples": [
                "Carnaval e festividades populares",
                "Capacidade de transformar problemas em soluções criativas",
                "Encontrar motivo para celebrar em pequenas conquistas"
            ] if include_examples else [],
            "regional_expressions": {
                "nordeste": "Festas juninas e forró",
                "sudeste": "Carnaval carioca e paulista", 
                "sul": "Oktoberfest e festivais de inverno",
                "norte": "Festival de Parintins",
                "centro_oeste": "Festivais de música sertaneja"
            } if include_examples else {}
        },
        "criativo_improvisador": {
            "name": "Criativo e Improvisador",
            "weight": 1.2,
            "description": "Habilidade de improvisar e criar soluções inovadoras",
            "keywords": ["criatividade", "improviso", "jeitinho", "inovação", "adaptação"],
            "examples": [
                "Jeitinho brasileiro para resolver problemas",
                "Adaptação criativa a limitações de recursos",
                "Inovação em situações adversas"
            ] if include_examples else [],
            "regional_expressions": {
                "nordeste": "Adaptação ao clima semiárido",
                "sudeste": "Inovação tecnológica e empresarial",
                "sul": "Cooperativismo e soluções coletivas",
                "norte": "Adaptação à natureza amazônica",
                "centro_oeste": "Inovação no agronegócio"
            } if include_examples else {}
        },
        "acolhedor_hospitaleiro": {
            "name": "Acolhedor e Hospitaleiro",
            "weight": 1.1,
            "description": "Calor humano e receptividade genuína",
            "keywords": ["hospitalidade", "acolhimento", "carinho", "proximidade", "generosidade"],
            "examples": [
                "Receber bem visitantes e estrangeiros",
                "Cultura do 'cafezinho' e conversas",
                "Solidariedade em momentos difíceis"
            ] if include_examples else [],
            "regional_expressions": {
                "nordeste": "Hospitalidade sertaneja",
                "sudeste": "Diversidade e inclusão urbana",
                "sul": "Tradição de receber bem",
                "norte": "Hospitalidade ribeirinha",
                "centro_oeste": "Cultura rural acolhedora"
            } if include_examples else {}
        },
        "resiliente_persistente": {
            "name": "Resiliente e Persistente",
            "weight": 1.0,
            "description": "Capacidade de superar adversidades com otimismo",
            "keywords": ["resilência", "persistência", "superação", "força", "determinação"],
            "examples": [
                "Superação de crises econômicas",
                "Adaptação a mudanças sociais",
                "Manter esperança em situações difíceis"
            ] if include_examples else [],
            "regional_expressions": {
                "nordeste": "Resistência à seca",
                "sudeste": "Adaptação urbana",
                "sul": "Persistência no trabalho",
                "norte": "Resistência às distâncias",
                "centro_oeste": "Desbravamento de fronteiras"
            } if include_examples else {}
        },
        "sensual_expressivo": {
            "name": "Sensual e Expressivo",
            "weight": 0.9,
            "description": "Expressão corporal e comunicação através do corpo",
            "keywords": ["sensualidade", "expressão", "corpo", "dança", "gesticulação"],
            "examples": [
                "Dança como expressão cultural",
                "Gesticulação expressiva na comunicação",
                "Valorização da beleza e do corpo"
            ] if include_examples else [],
            "regional_expressions": {
                "nordeste": "Forró e dança regional",
                "sudeste": "Samba e expressão urbana",
                "sul": "Dança tradicional gaúcha",
                "norte": "Danças folclóricas amazônicas",
                "centro_oeste": "Dança country e sertaneja"
            } if include_examples else {}
        },
        "musical_ritmado": {
            "name": "Musical e Ritmado",
            "weight": 0.8,
            "description": "Conexão natural com música e ritmo",
            "keywords": ["música", "ritmo", "melodia", "harmonia", "compasso"],
            "examples": [
                "Diversidade musical brasileira",
                "Música como parte do cotidiano",
                "Criação de novos ritmos e estilos"
            ] if include_examples else [],
            "regional_expressions": {
                "nordeste": "Forró, axé e frevo",
                "sudeste": "Samba, bossa nova e rock",
                "sul": "Música gaúcha e alemã",
                "norte": "Música amazônica e boi-bumbá",
                "centro_oeste": "Sertanejo e música country"
            } if include_examples else {}
        },
        "mistico_espiritual": {
            "name": "Místico e Espiritual",
            "weight": 0.7,
            "description": "Dimensão espiritual e transcendente",
            "keywords": ["espiritualidade", "místico", "fé", "transcendência", "sagrado"],
            "examples": [
                "Sincretismo religioso brasileiro",
                "Crenças populares e superstições",
                "Busca por sentido espiritual"
            ] if include_examples else [],
            "regional_expressions": {
                "nordeste": "Religiosidade popular",
                "sudeste": "Diversidade religiosa urbana",
                "sul": "Tradições cristãs",
                "norte": "Espiritualidade indígena",
                "centro_oeste": "Religiosidade rural"
            } if include_examples else {}
        }
    }
    
    return {
        "total_values": len(values),
        "description": "Os 7 valores fundamentais que compõem a Alma Brasileira",
        "values": values,
        "analysis_method": "Cada valor é analisado e ponderado para compor o score final",
        "score_interpretation": {
            "0.8-1.0": "Muito autêntico - forte conexão com a alma brasileira",
            "0.6-0.79": "Autêntico - boa conexão cultural",
            "0.4-0.59": "Moderado - conexão parcial",
            "0.2-0.39": "Baixo - pouca autenticidade",
            "0.0-0.19": "Muito baixo - desconectado da alma brasileira"
        }
    }


@alma_router.get(
    "/regional-analysis",
    summary="Análise Regional da Alma",
    description="Como a Alma Brasileira se expressa em diferentes regiões"
)
async def regional_alma_analysis(
    region: str = Query(..., description="Região para análise detalhada"),
    current_client: ClientInfo = Depends(get_current_client)
):
    """Análise da Alma Brasileira por região específica"""
    
    regional_data = {
        "nordeste": {
            "dominant_values": ["alegre_festivo", "resiliente_persistente", "mistico_espiritual"],
            "characteristics": [
                "Forte religiosidade popular",
                "Cultura da festividade e celebração",
                "Resistência histórica às adversidades",
                "Rica tradição musical e dançante"
            ],
            "cultural_expressions": [
                "Forró e música regional",
                "Festas juninas tradicionais",
                "Artesanato e cultura popular",
                "Religiosidade sincrética"
            ],
            "communication_insights": [
                "Valorizar tradições familiares",
                "Usar linguagem calorosa e próxima",
                "Incorporar elementos musicais",
                "Respeitar valores religiosos"
            ]
        },
        "sudeste": {
            "dominant_values": ["criativo_improvisador", "acolhedor_hospitaleiro", "sensual_expressivo"],
            "characteristics": [
                "Diversidade cultural urbana",
                "Inovação e empreendedorismo",
                "Cosmopolitismo com brasilidade",
                "Centro econômico e cultural"
            ],
            "cultural_expressions": [
                "Samba e bossa nova",
                "Arte urbana e grafite",
                "Gastronomia diversificada",
                "Movimentos culturais"
            ],
            "communication_insights": [
                "Combinar tradição e modernidade",
                "Valorizar diversidade e inclusão",
                "Usar referências urbanas",
                "Apostar em inovação criativa"
            ]
        },
        "sul": {
            "dominant_values": ["resiliente_persistente", "acolhedor_hospitaleiro", "criativo_improvisador"],
            "characteristics": [
                "Influência europeia forte",
                "Cultura do trabalho e cooperação",
                "Tradições bem preservadas",
                "Hospitalidade rural e urbana"
            ],
            "cultural_expressions": [
                "Cultura gaúcha e tradições",
                "Oktoberfest e festivais",
                "Chimarrão e costumes",
                "Música tradicional"
            ],
            "communication_insights": [
                "Respeitar tradições locais",
                "Valorizar qualidade e autenticidade",
                "Usar elementos de cooperação",
                "Incluir referências rurais"
            ]
        },
        "norte": {
            "dominant_values": ["mistico_espiritual", "resiliente_persistente", "acolhedor_hospitaleiro"],
            "characteristics": [
                "Conexão profunda com a natureza",
                "Influência indígena marcante",
                "Cultura ribeirinha única",
                "Biodiversidade cultural"
            ],
            "cultural_expressions": [
                "Festival de Parintins",
                "Lendas e folclore amazônico",
                "Culinária regional exótica",
                "Artesanato indígena"
            ],
            "communication_insights": [
                "Valorizar sustentabilidade",
                "Incluir elementos naturais",
                "Respeitar sabedoria ancestral",
                "Usar storytelling regional"
            ]
        },
        "centro_oeste": {
            "dominant_values": ["criativo_improvisador", "resiliente_persistente", "alegre_festivo"],
            "characteristics": [
                "Espírito desbravador",
                "Cultura agropecuária moderna",
                "Mistura de tradições",
                "Crescimento e desenvolvimento"
            ],
            "cultural_expressions": [
                "Música sertaneja e country",
                "Festivais agropecuários",
                "Culinária do cerrado",
                "Rodeios e tradições rurais"
            ],
            "communication_insights": [
                "Valorizar progresso e tradição",
                "Usar elementos rurais modernos",
                "Incluir temas de crescimento",
                "Apostar em comunidade"
            ]
        }
    }
    
    if region not in regional_data:
        available_regions = list(regional_data.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Região inválida. Disponíveis: {available_regions}"
        )
    
    return {
        "region": region,
        "analysis": regional_data[region],
        "alma_brasileira_expression": f"A Alma Brasileira no {region.title()} se expressa através de...",
        "recommendation": "Use estes insights para criar comunicação autêntica e regionalmente relevante"
    }


@alma_router.post(
    "/compare-brands",
    summary="Comparar Autenticidade de Marcas",
    description="Compara o nível de autenticidade brasileira entre diferentes marcas"
)
async def compare_brands_authenticity(
    brands_data: List[Dict[str, Any]],
    current_client: ClientInfo = Depends(get_current_client)
):
    """Comparar autenticidade brasileira entre marcas"""
    
    if len(brands_data) < 2:
        raise HTTPException(
            status_code=400,
            detail="Forneça pelo menos 2 marcas para comparação"
        )
    
    if len(brands_data) > 5:
        raise HTTPException(
            status_code=400,
            detail="Máximo 5 marcas por comparação"
        )
    
    try:
        analyzer = AlmaBrasileiraAnalyzer()
        comparison_results = []
        
        for brand_data in brands_data:
            if "brand_name" not in brand_data or "content_data" not in brand_data:
                raise HTTPException(
                    status_code=400,
                    detail="Cada marca deve ter 'brand_name' e 'content_data'"
                )
            
            # Executar análise
            result = analyzer.analyze_alma_brasileira(
                content_data=brand_data["content_data"],
                circles_analysis={}
            )
            
            comparison_results.append({
                "brand_name": brand_data["brand_name"],
                "alma_score": result.get("alma_score", 0.0),
                "intensity": _get_intensity_from_score(result.get("alma_score", 0.0)),
                "dominant_values": result.get("dominant_values", [])[:3],
                "authenticity_level": _get_authenticity_from_score(result.get("alma_score", 0.0))
            })
        
        # Ordenar por score
        comparison_results.sort(key=lambda x: x["alma_score"], reverse=True)
        
        return {
            "comparison_type": "brand_authenticity",
            "total_brands": len(comparison_results),
            "results": comparison_results,
            "ranking": [brand["brand_name"] for brand in comparison_results],
            "insights": _generate_comparison_insights(comparison_results)
        }
        
    except Exception as e:
        logger.error(f"Erro na comparação de marcas: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro na comparação: {str(e)}"
        )


# Funções auxiliares
def _convert_alma_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Converte resultado do analisador para formato da API"""
    
    return {
        "alma_score": result.get("alma_score", 0.0),
        "intensity": _get_intensity_from_score(result.get("alma_score", 0.0)),
        "dominant_values": result.get("dominant_values", [])[:5],
        "regional_connection": result.get("regional_connection", "Brasil"),
        "authenticity": _get_authenticity_from_score(result.get("alma_score", 0.0)),
        "communication_insights": result.get("communication_insights", [])
    }


def _get_intensity_from_score(score: float) -> str:
    """Converte score para intensidade da alma"""
    if score >= 0.8:
        return "muito_intensa"
    elif score >= 0.6:
        return "intensa"
    elif score >= 0.4:
        return "moderada"
    elif score >= 0.2:
        return "baixa"
    else:
        return "muito_baixa"


def _get_authenticity_from_score(score: float) -> str:
    """Converte score para nível de autenticidade"""
    if score >= 0.8:
        return "muito_autêntico"
    elif score >= 0.6:
        return "autêntico"
    elif score >= 0.4:
        return "moderadamente_autêntico"
    elif score >= 0.2:
        return "pouco_autêntico"
    else:
        return "não_autêntico"


def _generate_comparison_insights(results: List[Dict[str, Any]]) -> List[str]:
    """Gera insights da comparação entre marcas"""
    
    if not results:
        return []
    
    insights = []
    
    # Marca mais autêntica
    most_authentic = results[0]
    least_authentic = results[-1]
    
    insights.append(f"{most_authentic['brand_name']} apresenta maior autenticidade brasileira")
    insights.append(f"Diferença de {abs(most_authentic['alma_score'] - least_authentic['alma_score']):.2f} pontos entre extremos")
    
    # Analisar distribuição
    high_authentic = [r for r in results if r["alma_score"] >= 0.6]
    if len(high_authentic) >= len(results) // 2:
        insights.append("Maioria das marcas demonstra boa autenticidade brasileira")
    else:
        insights.append("Oportunidade de melhorar conexão com a alma brasileira")
    
    return insights
