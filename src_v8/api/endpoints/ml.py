#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Endpoints FastAPI para ML Pipeline - Culture Pulse V9.0
API REST para treinamento e predição de modelos ML

🎯 FUNCIONALIDADES:
- Endpoints para treinamento de modelos
- Predições em lote e individuais
- Gestão de modelos
- Métricas de performance
- Monitoramento de drift
"""

import sys
import os

# Adicionar path para imports absolutos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

try:
    from autonomous_agent.ml_foundation.back.ml_pipeline import (
        get_ml_pipeline,
        create_sample_training_data,
        BusinessContext as PipelineBusinessContext,
    )
except ImportError as exc:
    get_ml_pipeline = None
    create_sample_training_data = None
    PipelineBusinessContext = None
    from fastapi import HTTPException
    def get_ml_pipeline(*args, **kwargs):
        raise HTTPException(status_code=503, detail="ML pipeline unavailable: missing autonomous_agent.ml_foundation.back.ml_pipeline")
    def create_sample_training_data(*args, **kwargs):
        raise HTTPException(status_code=503, detail="ML sample data unavailable: missing autonomous_agent.ml_foundation.back.ml_pipeline")

from api.middleware.auth import get_current_client

try:
    from core.intelligence.local_slm_bridge import get_slm_bridge
except Exception:
    get_slm_bridge = None

logger = logging.getLogger(__name__)

# Modelos Pydantic
class TrainingData(BaseModel):
    """Dados para treinamento"""
    text: str = Field(..., description="Texto para análise cultural")
    cultural_circle: str = Field(..., description="Círculo cultural (label)")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadados adicionais")

class TrainModelRequest(BaseModel):
    """Requisição de treinamento"""
    model_name: str = Field(..., description="Nome do modelo")
    training_data: List[TrainingData] = Field(..., description="Dados de treinamento")
    target_column: str = Field(default="cultural_circle", description="Coluna target")
    
class BusinessContext(BaseModel):
    brand: Optional[str] = Field(default=None, description="Marca do projeto")
    segment: Optional[str] = Field(default=None, description="Segmento de mercado")
    objective: Optional[str] = Field(default=None, description="Objetivo do projeto")
    keywords: Optional[List[str]] = Field(default=None, description="Keywords associadas ao projeto")
    audiences: Optional[List[str]] = Field(default=None, description="Públicos-alvo do projeto")
    regions: Optional[List[str]] = Field(default=None, description="Regiões geográficas relevantes")
    circles: Optional[List[str]] = Field(default=None, description="Círculos culturais ou temas estratégicos")
    project_id: Optional[str] = Field(default=None, description="ID do projeto")
    user_id: Optional[str] = Field(default=None, description="ID do usuário")
    period_days: Optional[int] = Field(default=None, description="Duração do projeto em dias")
    business_goal: Optional[str] = Field(default=None, description="Objetivo de negócio definido no onboarding")

    class Config:
        extra = "allow"

class PredictionRequest(BaseModel):
    """Requisição de predição"""
    texts: List[str] = Field(..., description="Textos para análise")
    model_name: Optional[str] = Field(default=None, description="Nome do modelo (usa ativo se não especificado)")
    return_confidence: bool = Field(default=True, description="Retornar scores de confiança")
    business_context: Optional[BusinessContext] = Field(default=None, description="Contexto de negócio para alinhamento")

class PredictionResponse(BaseModel):
    """Resposta de predição"""
    predictions: List[Dict[str, Any]] = Field(..., description="Predições com metadados")
    model_used: str = Field(..., description="Nome do modelo utilizado")
    processing_time: float = Field(..., description="Tempo de processamento")

class ModelInfo(BaseModel):
    """Informações do modelo"""
    name: str
    trained: bool
    classes_count: int
    is_active: bool
    performance: Optional[Dict[str, Any]] = None


class StrategyLearnerStatusResponse(BaseModel):
    """Status do StrategyLearner"""
    engine_name: str
    status: str
    is_running: bool
    context_count: int
    contexts: List[str]
    data_buffer_size: int
    performance_history_count: int
    supabase_connected: bool
    model_weights: Dict[str, float]
    last_updated: Optional[str]


# Router
ml_router = APIRouter(prefix="/api/v8/ml", tags=["Machine Learning"])

def is_ml_pipeline_available() -> bool:
    if get_ml_pipeline is None:
        return False
    try:
        get_ml_pipeline()
        return True
    except Exception:
        return False


def is_ollama_available() -> bool:
    if get_slm_bridge is None:
        return False
    try:
        return get_slm_bridge().is_available
    except Exception:
        return False


@ml_router.get("/models", response_model=List[ModelInfo])
async def list_models():
    """Lista todos os modelos ML disponíveis"""
    try:
        pipeline = get_ml_pipeline()
        models = pipeline.list_models()
        return [ModelInfo(**{**model, "is_active": model.get("active", False)}) for model in models]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar modelos: {e}")

@ml_router.get("/strategy-status", response_model=StrategyLearnerStatusResponse)
async def get_strategy_learner_status():
    """Retorna o status do StrategyLearner (learning engine)."""
    try:
        from core.intelligence.learning.StrategyLearner import get_strategy_learner

        strategy = get_strategy_learner()
        return StrategyLearnerStatusResponse(
            engine_name="StrategyLearner",
            status="running" if strategy.is_running else "stopped",
            is_running=strategy.is_running,
            context_count=len(strategy.brand_contexts),
            contexts=list(strategy.brand_contexts.keys()),
            data_buffer_size=len(getattr(strategy, "data_buffer", [])),
            performance_history_count=sum(len(v) for v in strategy.performance_history.values()),
            supabase_connected=getattr(strategy, "use_supabase", False),
            model_weights={k: float(v) for k, v in getattr(strategy, "model_weights", {}).items()},
            last_updated=None,
        )
    except Exception as e:
        logger.error(f"GET /api/v8/ml/strategy-status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@ml_router.post("/models/{model_name}/train")
async def train_model(
    model_name: str,
    request: TrainModelRequest,
    background_tasks: BackgroundTasks
):
    """
    Treina um modelo ML com dados culturais
    
    O treinamento é executado em background para não bloquear a API
    """
    try:
        pipeline = get_ml_pipeline()
        
        # Converter dados para formato interno
        training_data = [
            {
                'text': item.text,
                'cultural_circle': item.cultural_circle,
                **(item.metadata or {})
            }
            for item in request.training_data
        ]
        
        # Verificar se há dados suficientes
        if len(training_data) < 10:
            raise HTTPException(
                status_code=400,
                detail="Mínimo de 10 amostras necessárias para treinamento"
            )
        
        # Iniciar treinamento em background
        def train_task():
            try:
                logger.info(f"Iniciando treinamento do modelo {model_name}")
                metrics = pipeline.train_model(model_name, training_data, request.target_column)
                f1_score = metrics.get("metrics", {}).get("f1_score")
                logger.info(f"Treinamento concluído: {model_name} - F1: {f1_score:.3f}" if f1_score is not None else f"Treinamento concluído: {model_name}")
            except Exception as e:
                logger.error(f"Falha no treinamento de {model_name}: {e}")
        
        background_tasks.add_task(train_task)
        
        return {
            "message": f"Treinamento iniciado para modelo '{model_name}'",
            "training_samples": len(training_data),
            "target_column": request.target_column,
            "status": "training_started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no treinamento: {e}")

@ml_router.post("/models/{model_name}/activate")
async def activate_model(model_name: str):
    """Ativa um modelo para uso em predições"""
    try:
        pipeline = get_ml_pipeline()
        pipeline.set_active_model(model_name)
        
        return {
            "message": f"Modelo '{model_name}' ativado com sucesso",
            "active_model": model_name
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ativar modelo: {e}")

@ml_router.post("/predict", response_model=PredictionResponse)
async def predict_cultural(request: PredictionRequest):
    """
    Realiza predições de análise cultural
    
    Analisa textos e retorna classificações culturais com scores de confiança
    """
    try:
        start_time = datetime.now()
        pipeline = get_ml_pipeline()

        business_context = (
            PipelineBusinessContext(**request.business_context.model_dump())
            if request.business_context else None
        )

        if request.return_confidence:
            predictions = pipeline.predict_with_confidence(
                request.texts,
                request.model_name,
                business_context,
            )
        else:
            simple_predictions = pipeline.predict(
                request.texts,
                request.model_name,
                business_context,
            )
            predictions = [
                {
                    'text': text,
                    'prediction': pred,
                    'confidence': None
                }
                for text, pred in zip(request.texts, simple_predictions)
            ]
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return PredictionResponse(
            predictions=predictions,
            model_used=request.model_name or pipeline.active_model,
            processing_time=processing_time
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na predição: {e}")

class BusinessInsightRequest(BaseModel):
    texts: List[str] = Field(..., description="Textos para análise de insight")
    model_name: Optional[str] = Field(default=None, description="Nome do modelo")
    business_context: Optional[BusinessContext] = Field(default=None, description="Contexto de negócio")

@ml_router.post("/analyze/business-insights")
async def analyze_business_insights(request: BusinessInsightRequest):
    """Gera insights de negócio a partir do ML Pipeline"""
    try:
        pipeline = get_ml_pipeline()
        business_context = (
            PipelineBusinessContext(**request.business_context.model_dump())
            if request.business_context else None
        )
        analysis = pipeline.analyze_business_insights(
            request.texts,
            business_context,
            request.model_name,
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise de insights: {e}")

@ml_router.get("/models/{model_name}/performance")
async def get_model_performance(model_name: str):
    """Obtém métricas de performance de um modelo"""
    try:
        pipeline = get_ml_pipeline()
        performance = pipeline.get_model_performance(model_name)
        
        if performance is None:
            raise HTTPException(
                status_code=404,
                detail=f"Modelo '{model_name}' não encontrado ou não treinado"
            )
        
        return {
            "model_name": model_name,
            "performance": performance
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter performance: {e}")

@ml_router.post("/models/sample-data")
async def create_sample_training():
    """
    Cria dados de treinamento de exemplo
    
    Útil para demonstração e testes iniciais
    """
    try:
        sample_data = create_sample_training_data()
        
        return {
            "message": "Dados de exemplo criados",
            "sample_count": len(sample_data),
            "data": sample_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar dados exemplo: {e}")

@ml_router.post("/models/demo/quick-train")
async def quick_demo_training(background_tasks: BackgroundTasks):
    """
    Treinamento rápido de demonstração
    
    Treina modelo com dados sintéticos para demonstração
    """
    try:
        pipeline = get_ml_pipeline()
        sample_data = create_sample_training_data()
        
        # Expandir dados de exemplo para ter amostras suficientes
        expanded_data = sample_data * 5  # Repetir 5x para ter dados suficientes
        
        def demo_train_task():
            try:
                logger.info("Iniciando treinamento demo")
                metrics = pipeline.train_model("cultural_demo", expanded_data)
                pipeline.set_active_model("cultural_demo")
                f1_score = metrics.get("metrics", {}).get("f1_score")
                logger.info(f"Demo treinado: F1-Score = {f1_score:.3f}" if f1_score is not None else "Demo treinado")
            except Exception as e:
                logger.error(f"Falha no treinamento demo: {e}")
        
        background_tasks.add_task(demo_train_task)
        
        return {
            "message": "Treinamento demo iniciado",
            "model_name": "cultural_demo",
            "training_samples": len(expanded_data),
            "status": "demo_training_started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no treinamento demo: {e}")

@ml_router.get("/health")
async def ml_health_check():
    """Health check do sistema ML"""
    try:
        pipeline = get_ml_pipeline()
        models = pipeline.list_models()
        
        active_model = pipeline.active_model
        trained_models = [m for m in models if m['trained']]

        production_mode = os.getenv("ENVIRONMENT", "production").strip().lower() == "production"
        allow_demo_collection = os.getenv("ALLOW_DEMO_COLLECTION", "false").strip().lower() in ("1", "true", "yes", "y")
        source_policy = "real-only" if production_mode and not allow_demo_collection else "real-plus-demo-allowed" if production_mode else "demo-allowed"
        
        return {
            "status": "healthy",
            "total_models": len(models),
            "trained_models": len(trained_models),
            "active_model": active_model,
            "ml_pipeline_ready": True,
            "ollama_available": is_ollama_available(),
            "production_mode": production_mode,
            "allow_demo_collection": allow_demo_collection,
            "source_policy": source_policy
        }
        
    except Exception as e:
        production_mode = os.getenv("ENVIRONMENT", "production").strip().lower() == "production"
        allow_demo_collection = os.getenv("ALLOW_DEMO_COLLECTION", "false").strip().lower() in ("1", "true", "yes", "y")
        source_policy = "real-only" if production_mode and not allow_demo_collection else "real-plus-demo-allowed" if production_mode else "demo-allowed"

        return {
            "status": "unhealthy",
            "error": str(e),
            "ml_pipeline_ready": False,
            "ollama_available": is_ollama_available(),
            "production_mode": production_mode,
            "allow_demo_collection": allow_demo_collection,
            "source_policy": source_policy
        }

# Exemplo de uso avançado
@ml_router.post("/analyze/cultural-profile")
async def analyze_cultural_profile(
    texts: List[str],
    business_context: Optional[BusinessContext] = None,
    include_regional_analysis: bool = True,
    include_cultural_topics: bool = True
):
    """
    Análise avançada de perfil cultural
    
    Combina predições ML com análise de features culturais específicas
    """
    try:
        pipeline = get_ml_pipeline()
        
        predictions = pipeline.predict_with_confidence(
            texts,
            business_context=business_context,
        )
        
        cultural_analysis = []
        
        if include_regional_analysis or include_cultural_topics:
            from autonomous_agent.ml_foundation.back.ml_pipeline import CulturalFeatureExtractor
            
            extractor = CulturalFeatureExtractor()
            features = extractor.transform(texts)
            
            for text, pred, feat in zip(texts, predictions, features):
                analysis = {
                    "text": text,
                    "main_prediction": pred,
                    "regional_indicators": feat[:5] if include_regional_analysis else None,
                    "cultural_topics_score": feat[5] if include_cultural_topics else None,
                    "social_markers_score": feat[6] if include_cultural_topics else None,
                    "emotion_score": feat[7] if include_cultural_topics else None,
                }
                cultural_analysis.append(analysis)
        
        return {
            "analysis": cultural_analysis or predictions,
            "summary": {
                "total_texts": len(texts),
                "dominant_culture": max(set(p['prediction'] for p in predictions)) if predictions else "unknown",
                "avg_confidence": round(sum(p['confidence'] for p in predictions) / len(predictions), 3) if predictions else 0.0,
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise cultural: {e}")

# Adicionar ao main.py
def include_ml_router(app):
    """Inclui router ML na aplicação"""
    app.include_router(
        ml_router,
        dependencies=[Depends(get_current_client)]
    )
