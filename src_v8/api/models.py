#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pydantic Models - Culture Pulse V9.0
Modelos de dados para validação de entrada e saída da API

🎯 RESPONSABILIDADES:
- Validação de dados de entrada
- Serialização de dados de saída
- Documentação automática dos schemas
- Tipagem forte para toda a API
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Literal
from datetime import datetime
from enum import Enum


# Enums para validação
class SegmentEnum(str, Enum):
    """Segmentos disponíveis"""
    calcados = "calçados"
    bebidas = "bebidas"
    cosmeticos = "cosméticos"
    alimentacao = "alimentação"
    moda = "moda"
    tecnologia = "tecnologia"
    servicos = "serviços"
    entretenimento = "entretenimento"
    educacao = "educação"
    saude = "saúde"


class LocationEnum(str, Enum):
    """Localizações disponíveis"""
    sao_paulo_capital = "São Paulo - Capital"
    sao_paulo_interior = "São Paulo - Interior"
    rio_janeiro_capital = "Rio de Janeiro - Capital"
    rio_janeiro_periferia = "Rio de Janeiro - Periferia"
    belo_horizonte = "Belo Horizonte"
    salvador = "Salvador"
    brasilia = "Brasília"
    fortaleza = "Fortaleza"
    recife = "Recife"
    porto_alegre = "Porto Alegre"
    curitiba = "Curitiba"
    manaus = "Manaus"
    goiania = "Goiânia"
    campinas = "Campinas"
    sao_luis = "São Luís"
    natal = "Natal"
    campo_grande = "Campo Grande"
    joao_pessoa = "João Pessoa"
    teresina = "Teresina"
    aracaju = "Aracaju"
    cuiaba = "Cuiabá"
    macapa = "Macapá"
    rio_branco = "Rio Branco"
    boa_vista = "Boa Vista"
    palmas = "Palmas"
    vitoria = "Vitória"


class IdadeEnum(str, Enum):
    """Faixas etárias"""
    jovem = "16-25"
    adulto_jovem = "26-35"
    adulto = "36-45"
    adulto_maduro = "46-55"
    sênior = "56+"


class ClasseEnum(str, Enum):
    """Classes sociais"""
    a = "A"
    b = "B"
    c = "C"
    d = "D"
    e = "E"


class GeneroEnum(str, Enum):
    """Gêneros"""
    masculino = "Masculino"
    feminino = "Feminino"
    todos = "Todos"
    nao_binario = "Não-binário"


# Modelos de entrada (Request)
class DemographicsModel(BaseModel):
    """Modelo de dados demográficos"""
    faixa_etaria: IdadeEnum = Field(..., description="Faixa etária do público-alvo")
    classe_social: ClasseEnum = Field(..., description="Classe social predominante")
    genero: GeneroEnum = Field(..., description="Gênero do público-alvo")
    escolaridade: Optional[str] = Field(None, description="Nível de escolaridade")
    renda_familiar: Optional[str] = Field(None, description="Faixa de renda familiar")


class BrandAnalysisRequest(BaseModel):
    """Modelo para requisição de análise de marca"""
    project_id: Optional[str] = Field(None, description="ID do projeto associado")
    brand_name: str = Field(..., min_length=2, max_length=100, description="Nome da marca")
    segment: SegmentEnum = Field(..., description="Segmento da marca")
    location: LocationEnum = Field(..., description="Localização do público-alvo")
    demographics: DemographicsModel = Field(..., description="Dados demográficos")
    keywords: Optional[List[str]] = Field(None, description="Palavras-chave do projeto")
    regions: Optional[List[str]] = Field(None, description="Regiões de foco do projeto")
    audiences: Optional[List[str]] = Field(None, description="Audiências prioritárias do projeto")
    circles: Optional[List[str]] = Field(None, description="Círculos culturais selecionados")
    period_days: Optional[int] = Field(None, description="Período em dias para coleta de sinais")
    
    # Campo para o Business Consultant (V9.1)
    business_goal: Optional[str] = Field(
        None, 
        description="Explique em uma frase o que você busca (ex: Lançamento de produto para a Geração Z na periferia)"
    )
    
    # Suporte para Contexto Direto do Dashboard (V9.9)
    context_text: Optional[str] = Field(
        None,
        description="Contexto adicional ou briefing específico para refinar a entropia cultural"
    )
    
    # Configuração de Data Mining V9.4
    outlier_mode: Optional[bool] = Field(
        True, # Agora True por padrão para todos os Tiers (Democratização)
        description="Ativa injeção de termos negativos para descoberta de nichos. O impacto varia conforme o Tier do usuário."
    )
    
    @validator('brand_name')
    def validate_brand_name(cls, v):
        """Valida nome da marca"""
        if not v.strip():
            raise ValueError('Nome da marca não pode estar vazio')
        return v.strip()
    
    @validator('keywords', pre=True, always=True)
    def validate_keywords(cls, v):
        if v is None:
            return []
        if not isinstance(v, list):
            raise ValueError('keywords deve ser uma lista de termos')
        if len(v) > 50:
            raise ValueError('Máximo 50 keywords')
        return v
    
    @validator('segment', pre=True, always=True)
    def normalize_segment(cls, v):
        """Normaliza segmentos para os valores aceitos pelo enum."""
        if not v:
            raise ValueError('Segmento é obrigatório')
        normalized = str(v).strip().lower()
        mapping = {
            'alimentacao': 'alimentação',
            'alimentação': 'alimentação',
            'bebidas': 'bebidas',
            'cosmeticos': 'cosméticos',
            'cosméticos': 'cosméticos',
            'calcados': 'calçados',
            'calçados': 'calçados',
            'moda': 'moda',
            'tecnologia': 'tecnologia',
            'serviços': 'serviços',
            'servicos': 'serviços',
            'entretenimento': 'entretenimento',
            'educacao': 'educação',
            'educação': 'educação',
            'saude': 'saúde',
            'saúde': 'saúde',
            'servicos': 'serviços',
            'serviços': 'serviços'
        }
        return mapping.get(normalized, normalized)
    
    @validator('period_days')
    def validate_period_days(cls, v):
        if v is not None and v <= 0:
            raise ValueError('period_days deve ser maior que zero')
        return v


class CirclesAnalysisRequest(BaseModel):
    """Modelo para análise específica de círculos culturais"""
    segment: SegmentEnum = Field(..., description="Segmento para análise")
    location: LocationEnum = Field(..., description="Localização")
    content_data: Dict[str, Any] = Field(..., description="Dados de conteúdo para análise")
    focus_circles: Optional[List[str]] = Field(None, description="Círculos específicos para focar")


class TFIDFAnalysisRequest(BaseModel):
    """Modelo para análise TF-IDF"""
    content_texts: List[str] = Field(..., min_items=1, description="Textos para análise TF-IDF")
    cultural_context: Optional[Dict[str, Any]] = Field(None, description="Contexto cultural adicional")
    custom_terms: Optional[List[str]] = Field(None, description="Termos culturais customizados")


class AlmaAnalysisRequest(BaseModel):
    """Modelo para análise da Alma Brasileira"""
    content_data: Dict[str, Any] = Field(..., description="Dados de conteúdo")
    regional_focus: Optional[str] = Field(None, description="Foco regional específico")


class CampaignMatchRequest(BaseModel):
    """Modelo para teste de aderência de campanha (Match Score)"""
    campaign_text: str = Field(..., min_length=10, description="Texto da campanha ou post")
    brand_name: str = Field(..., description="Nome da marca")
    target_audience: Optional[DemographicsModel] = Field(None, description="Público-alvo específico")
    segment: SegmentEnum = Field(SegmentEnum.servicos, description="Segmento de atuação")
    location: Optional[LocationEnum] = Field(None, description="Localização prioritária")


# Modelos de saída (Response)
class CircleAnalysisResponse(BaseModel):
    """Resposta de análise de um círculo cultural"""
    name: str = Field(..., description="Nome do círculo")
    score: float = Field(..., ge=0, le=1, description="Score do círculo (0-1)")
    # Adicionado metadados de entropia na resposta
    entropy_score: Optional[float] = Field(None, description="Grau de não-obviedade (0-1)")
    is_non_obvious: Optional[bool] = Field(False, description="Flag de insight ouro")
    level: str = Field(..., description="Nível cultural")
    weight: float = Field(..., description="Peso do círculo")
    regional_modifier: float = Field(..., description="Modificador regional")
    segment_modifier: float = Field(..., description="Modificador de segmento")


class CirclesAnalysisResponse(BaseModel):
    """Resposta completa da análise de círculos"""
    overall_score: float = Field(..., ge=0, le=1, description="Score cultural geral")
    cultural_level: str = Field(..., description="Nível cultural geral")
    circles_scores: Dict[str, CircleAnalysisResponse] = Field(..., description="Scores individuais")
    dominant_circles: List[str] = Field(..., description="Círculos dominantes")
    processing_time: float = Field(..., description="Tempo de processamento")


class TFIDFAnalysisResponse(BaseModel):
    """Resposta da análise TF-IDF"""
    relevance_score: float = Field(..., ge=0, le=1, description="Score de relevância cultural")
    cultural_terms: List[str] = Field(..., description="Termos culturais encontrados")
    trends: List[str] = Field(..., description="Tendências detectadas")
    categories: Dict[str, float] = Field(..., description="Scores por categoria cultural")
    top_terms: List[Dict[str, float]] = Field(..., description="Top termos com scores")


class AlmaAnalysisResponse(BaseModel):
    """Resposta da análise Alma Brasileira"""
    alma_score: float = Field(..., ge=0, le=1, description="Score da Alma Brasileira")
    intensity: str = Field(..., description="Intensidade da alma")
    dominant_values: List[str] = Field(..., description="Valores dominantes")
    regional_connection: str = Field(..., description="Conexão regional")
    authenticity: str = Field(..., description="Nível de autenticidade")
    communication_insights: List[str] = Field(..., description="Insights de comunicação")


class RegionalPredictionResponse(BaseModel):
    """Resposta de predição regionalizada (V9.1)"""
    region: str = Field(..., description="Região brasileira")
    ib_score: float = Field(..., description="Score de Identidade Brasileira (0-100)")
    cvi_score: float = Field(0.0, description="Cultural Value Index (0-100) - Compatibilidade Next.js")
    sentiment: str = Field(..., description="Sentimento previsto")
    risk_level: str = Field(..., description="Nível de risco cultural")
    confidence: float = Field(..., description="Nível de confiança da predição")
    circle_fit_scores: Dict[str, float] = Field(..., description="Scores de fit por círculo cultural")
    risk_factors: List[str] = Field(..., description="Fatores de risco identificados")
    opportunities: List[str] = Field(..., description="Oportunidades regionais")
    recommended_adaptations: List[str] = Field(..., description="Adaptações recomendadas para a região")
    expected_engagement: float = Field(..., description="Engajamento esperado (0-1)")


class BrandAnalysisResponse(BaseModel):
    """Resposta completa da análise de marca"""
    client_id: str = Field(..., description="ID do cliente")
    brand_name: str = Field(..., description="Nome da marca")
    segment: str = Field(..., description="Segmento")
    location: str = Field(..., description="Localização")
    demographics: Dict[str, Any] = Field(..., description="Demografia")
    
    # Scores principais
    cultural_score: float = Field(..., ge=0, le=1, description="Score cultural total")
    alma_brasileira_score: float = Field(..., ge=0, le=1, description="Score Alma Brasileira")
    tfidf_relevance: float = Field(..., ge=0, le=1, description="Relevância TF-IDF")
    
    # Análises detalhadas
    circles_analysis: CirclesAnalysisResponse = Field(..., description="Análise dos círculos")
    tfidf_analysis: TFIDFAnalysisResponse = Field(..., description="Análise TF-IDF")
    alma_analysis: AlmaAnalysisResponse = Field(..., description="Análise Alma Brasileira")
    
    # Nova análise regional (V9.1)
    regional_analysis: List[RegionalPredictionResponse] = Field(..., description="Análise regional detalhada")
    
    # Insights
    dominant_circles: List[tuple] = Field(..., description="Top 5 círculos dominantes")
    cultural_trends: List[str] = Field(..., description="Tendências culturais")
    recommendations: List[str] = Field(..., description="Recomendações estratégicas")
    opportunities: List[str] = Field(..., description="Oportunidades identificadas")
    
    # Metadados
    processing_time: float = Field(..., description="Tempo de processamento")
    data_sources: List[str] = Field(..., description="Fontes de dados utilizadas")
    confidence_level: float = Field(..., ge=0, le=1, description="Nível de confiança (agregado das acurácias das fontes)")
    is_verified_aggregate: bool = Field(True, description="Indica se a análise foi baseada em dados reais verificados")
    timestamp: str = Field(..., description="Timestamp da análise")


class ErrorResponse(BaseModel):
    """Modelo de resposta de erro"""
    error: str = Field(..., description="Tipo do erro")
    message: str = Field(..., description="Mensagem de erro")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalhes adicionais")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class HealthResponse(BaseModel):
    """Resposta do health check"""
    status: Literal["healthy", "unhealthy"] = Field(..., description="Status da API")
    version: str = Field(..., description="Versão da API")
    uptime: float = Field(..., description="Tempo de atividade")
    engine_status: str = Field(..., description="Status do Cultural Engine")
    total_analyses: int = Field(..., description="Total de análises realizadas")
    avg_processing_time: float = Field(..., description="Tempo médio de processamento")
    production_mode: bool = Field(..., description="Indica se o serviço está rodando em modo production")
    allow_demo_collection: bool = Field(..., description="Indica se a coleta demo está permitida no ambiente")
    source_policy: str = Field(..., description="Política de fontes operacional: real-only, real-plus-demo-allowed ou demo-allowed")

class APIInfoResponse(BaseModel):
    """Resposta de informações da API"""
    api: Dict[str, Any] = Field(..., description="Informações da API")
    engine: Dict[str, Any] = Field(..., description="Informações do engine")
    endpoints: Dict[str, str] = Field(..., description="Endpoints disponíveis")


# Modelos para Data Collectors
class CulturalSignalData(BaseModel):
    """Dados de um sinal cultural coletado"""
    momentum: float = Field(..., description="Momentum do sinal cultural")
    volume: int = Field(..., description="Volume de dados coletados")
    sentiment: float = Field(..., description="Sentimento associado (-1 a 1)")
    timestamp: str = Field(..., description="Timestamp da coleta")
    source: str = Field(..., description="Fonte dos dados")
    is_verified: bool = Field(True, description="Indica se o dado veio de API real (Biographical Veracity)")
    accuracy_score: float = Field(1.0, ge=0, le=1, description="Score de acurácia biográfica (0-1)")
    reliability: str = Field(..., description="Confiabilidade da fonte (ALTA, MEDIA, BAIXA) - Dinâmico por fonte")
    source_url: Optional[str] = Field(None, description="URL original do post ou conteúdo")
    source_category: Optional[str] = Field(None, description="Categoria cultural da fonte")
    image_url: Optional[str] = Field(None, description="URL da imagem associada ao post")
    extras: Dict[str, Any] = Field(default_factory=dict, description="Dados extras específicos da fonte")


class CollectorResponse(BaseModel):
    """Resposta da coleta de dados culturais"""
    term: str = Field(..., description="Termo cultural analisado")
    context: Dict[str, Any] = Field(..., description="Contexto da análise")
    signals: Dict[str, Optional[CulturalSignalData]] = Field(..., description="Sinais coletados por fonte")
    is_verified_aggregate: bool = Field(True, description="Indica se a maioria das fontes são reais/verificadas")
    timestamp: str = Field(..., description="Timestamp da coleta")
    total_collectors: int = Field(..., description="Total de coletores utilizados")
    successful_collectors: int = Field(..., description="Coletores que retornaram dados")


class CollectorTestResponse(BaseModel):
    """Resposta do teste dos coletores"""
    test_term: str = Field(..., description="Termo usado no teste")
    context: Dict[str, Any] = Field(..., description="Contexto do teste")
    results: Dict[str, Any] = Field(..., description="Resultados por coletor")
    timestamp: str = Field(..., description="Timestamp do teste")


class GeographicSignal(BaseModel):
    """Sinal geográfico de repercussão cultural"""
    city: str
    state: str
    region: str
    coordinates: List[float]
    intensity: float
    sentiment: float
    main_circle: str
    trending_topics: List[str]


class CampaignMatchResponse(BaseModel):
    """Resposta do teste de aderência"""
    match_score: float = Field(..., description="Score de Match Cultural (0-1)")
    authenticity_score: float = Field(..., description="Score de Autenticidade (0-1)")
    sentiment_alignment: float = Field(..., description="Alinhamento de Sentimento (0-1)")
    risks: List[str] = Field(..., description="Principais riscos culturais detectados")
    strengths: List[str] = Field(..., description="Pontos fortes do texto")
    suggestions: List[str] = Field(..., description="Sugestões de ajuste no tom de voz")
    detected_circles: List[str] = Field(..., description="Círculos culturais que mais ressoam")
    geographic_spread: Optional[List[GeographicSignal]] = None
    suggested_sources: Optional[List[str]] = Field(None, description="APIs sugeridas para coleta baseada no comportamento atual")
    strategic_context_applied: Optional[str] = Field(None, description="Contexto do onboarding que guiou esta análise")
