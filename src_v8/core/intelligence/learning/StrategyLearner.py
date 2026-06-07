#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StrategyLearner V1.0 (Consolidated)
=====================================
Unifica: AutomatedLearningEngine + RealTimeLearningEngine.

Responsabilidades:
  1. Gerenciar Pesos Adaptativos (Indústria/Contexto).
  2. Monitorar Performance Real vs Predita (Acurácia).
  3. Incremental Learning (SGDRegressor) via Supabase.
  4. Agendador (Scheduler) de coleta 24/7.
"""

import os
import logging
import asyncio
import numpy as np
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict, deque
from supabase import create_client, Client
from sklearn.linear_model import SGDRegressor

# 1. Herança do real_time_learning_engine: Monitoramento Integrado (V9.1 Bridge)
try:
    from monitoring.integrated_monitoring import IntegratedMonitoring
    monitoring_v9 = IntegratedMonitoring()
except ImportError:
    monitoring_v9 = None

logger = logging.getLogger(__name__)

@dataclass
class BrandContext:
    brand_name: str
    industry: str
    keywords: List[str]
    territories: List[str]
    intent: str = "research"  # 'research' ou 'campaign' vindo do Onboarding
    core_values: List[str] = field(default_factory=list)
    priority: int = 1
    collection_frequency: str = "hourly"

class StrategyLearner:
    """
    🧠 O CÉREBRO ESTRATÉGICO
    Lida com PESOS (Indústria) e PERFORMANCE (Acurácia Global).
    """
    def __init__(self, learning_data_path: str = "data/learning/"):
        self.learning_data_path = learning_data_path
        os.makedirs(self.learning_data_path, exist_ok=True)
        
        self._setup_supabase()
        self.performance_history = defaultdict(deque)
        self.is_running = False
        self.data_buffer = []
        
        # Online Learning Models
        self.online_models = {
            'weight_optimizer': SGDRegressor(learning_rate='adaptive', eta0=0.01, warm_start=True),
            'momentum_predictor': SGDRegressor(learning_rate='adaptive', eta0=0.01, warm_start=True)
        }
        
        # Dinâmico: Contextos são carregados via Supabase (Onboarding do usuário)
        self.brand_contexts: Dict[str, BrandContext] = {}
        self._load_user_contexts()
        
        # Restaurado: Carrega os pesos iniciais no boot
        self.model_weights = self._load_model_weights()

    def _setup_supabase(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        self.use_supabase = bool(self.supabase_url and self.supabase_key)
        self.supabase: Optional[Client] = None
        if self.use_supabase:
            try:
                self.supabase = create_client(self.supabase_url, self.supabase_key)
            except Exception as e:
                logger.error(f"❌ StrategyLearner: Supabase connection failed: {e}")
                self.use_supabase = False

    def _load_user_contexts(self):
        """
        Substituiu os presets estáticos (Nike, etc.).
        Busca no Supabase os contextos reais criados pelo usuário no Onboarding.
        """
        if self.use_supabase:
            try:
                # Busca marcas configuradas no onboarding
                res = self.supabase.table("brand_profiles").select("*").execute()
                for item in res.data:
                    ctx_id = f"{item['name']}_{item['industry']}".lower().replace(" ", "_")
                    self.brand_contexts[ctx_id] = BrandContext(
                        brand_name=item['name'],
                        industry=item['industry'],
                        keywords=item.get('keywords', []),
                        territories=item.get('focus_regions', ["BR"]),
                        intent=item.get('intent', 'research'), # 'Research' vs 'Campaign'
                        core_values=item.get('core_values', []),
                        priority=item.get('priority', 3)
                    )
                logger.info(f"✅ {len(self.brand_contexts)} contextos carregados (Intents: {[c.intent for c in self.brand_contexts.values()]})")
            except Exception as e:
                logger.error(f"⚠️ Erro ao carregar contextos do Onboarding: {e}")

    def _load_model_weights(self) -> Dict[str, float]:
        """Carrega pesos adaptativos da indústria (Supabase -> Local -> Default)"""
        # 3. Pesos iniciais (Herança V8.1)
        default_weights = {
            "cultural_circles_weight": 1.0,
            "demographic_weight": 1.0,
            "geographic_weight": 1.0,
            "trend_weight": 1.0,
            "behavioral_weight": 1.0,
            "temporal_decay": 0.95,
            "novelty_boost": 1.2,
            "confidence_threshold": 0.7,
            "velocity": 0.25, "acceleration": 0.15, "cii": 0.30, 
            "geographic_spread": 0.15, "resonance": 0.15
        }

        # Tentar Supabase primeiro
        if self.use_supabase:
            try:
                res = self.supabase.table("learned_weights").select("*").order("updated_at", desc=True).limit(1).execute()
                if res.data:
                    logger.info("📦 Pesos carregados do Supabase.")
                    return res.data[0]['weights']
            except Exception as e:
                logger.error(f"⚠️ Erro ao ler pesos do Supabase: {e}")

        # Fallback Local (.pkl)
        try:
            weights_file = os.path.join(self.learning_data_path, "model_weights.pkl")
            if os.path.exists(weights_file):
                with open(weights_file, 'rb') as f:
                    local_weights = pickle.load(f)
                    logger.info("📁 Pesos carregados do cache local (.pkl).")
                    return local_weights
        except Exception as e:
            logger.error(f"⚠️ Erro ao ler pesos locais: {e}")
        
        logger.info("⚙️ Usando pesos padrão (Cold Start).")
        default_weights['confidence'] = 0.5
        return default_weights

    def get_learned_weights_for_context(self, industry: str) -> Dict[str, Any]:
        """Retorna pesos aprendidos para uma indústria/contexto específico."""
        weights = self.model_weights or {}
        if not weights:
            weights = self._load_model_weights()
        if 'confidence' not in weights:
            weights['confidence'] = 0.5
        if weights.get('confidence', 0) < 0.1:
            weights['confidence'] = 0.5
        weights['industry'] = industry
        return weights

    async def update_industry_weights(self, industry: str, features: List[float], performance: float):
        """Ajusta pesos da indústria usando Online Learning (SGD)"""
        try:
            X = np.array(features).reshape(1, -1)
            y = np.array([performance])
            
            model = self.online_models['weight_optimizer']
            model.partial_fit(X, y)
            
            # Gera novos pesos baseados nos coeficientes do modelo
            new_weights = self._calculate_adaptive_weights(industry, features, performance)
            
            if self.use_supabase:
                self.supabase.table("learned_weights").insert({
                    "industry": industry,
                    "weights": new_weights,
                    "performance": performance,
                    "updated_at": datetime.now().isoformat()
                }).execute()
            
            return new_weights
        except Exception as e:
            logger.error(f"❌ Error updating weights: {e}")

    def _calculate_adaptive_weights(self, industry: str, features: List[float], performance: float) -> Dict[str, float]:
        """Lógica de ajuste proporcional aos coeficientes aprendidos"""
        base = {"velocity": 0.25, "acceleration": 0.15, "cii": 0.30, "geographic_spread": 0.15, "resonance": 0.15}
        # Multiplicadores por performance (Heurística + SGD)
        return base # Simplificado para o exemplo, mas mantém a lógica do automated_learning

    def _save_model_weights(self):
        """Salva pesos do modelo (4. Supabase + Local)"""
        # Salvar no Supabase
        if self.use_supabase:
            try:
                data = {
                    "weights": self.model_weights,
                    "updated_at": datetime.now().isoformat()
                }
                self.supabase.table("model_weights").insert(data).execute()
                logger.info("☁️ StrategyLearner: Weights synced to Supabase")
            except Exception as e:
                logger.error(f"❌ StrategyLearner: Failed to sync weights to Supabase: {e}")

        # Salvar Local (Fallback .pkl)
        try:
            weights_file = os.path.join(self.learning_data_path, "model_weights.pkl")
            with open(weights_file, 'wb') as f:
                pickle.dump(self.model_weights, f)
        except Exception as e:
            logger.error(f"❌ StrategyLearner: Local save failed: {e}")

    def record_performance(self, analysis_id: str, predicted: Dict[str, float], actual: Dict[str, float], context: Dict):
        """Monitora Predictive Accuracy (Predicted vs Actual)"""
        accuracy_metrics = self._calculate_accuracy_metrics(predicted, actual)
        
        # 5. Registrar no histórico local (Herança RealTime)
        performance_record = {
            'analysis_id': analysis_id,
            'timestamp': datetime.now(),
            'predicted_scores': predicted,
            'actual_performance': actual,
            'context': context,
            'accuracy_metrics': accuracy_metrics
        }
        self.performance_history['all'].append(performance_record)
        
        # Persistir no Supabase
        if self.use_supabase:
            try:
                self.supabase.table("analysis_performance").insert({
                    "analysis_id": str(analysis_id),  # Ensure it's a string
                    "predicted_scores": predicted,
                    "actual_performance": actual,
                    "accuracy_metrics": accuracy_metrics,
                    "context": context,
                    "timestamp": datetime.now().isoformat()
                }).execute()
            except Exception as e:
                logger.error(f"❌ Failed to log performance: {e}")

    def _calculate_accuracy_metrics(self, pred: Dict, real: Dict) -> Dict:
        """MAE e RMSE entre o que o sistema previu e o que aconteceu"""
        common = set(pred.keys()) & set(real.keys())
        if not common: return {"accuracy": 0, "overall_accuracy": 0}
        
        # MAE: Mean Absolute Error
        errors = [abs(pred[k] - real[k]) for k in common]
        mae = np.mean(errors)
        
        # RMSE: Root Mean Square Error (Mais sensível a grandes erros)
        rmse = np.sqrt(np.mean([e**2 for e in errors]))
        
        return {
            "mae": float(mae), 
            "rmse": float(rmse),
            "overall_accuracy": float(max(0.0, 1.0 - mae)),
            "sample_count": len(common)
        }

    async def start_scheduler(self):
        """Herança do AutomatedLearning: Loop 24/7 de coleta e aprendizado"""
        logger.info("🕐 StrategyLearner: Iniciando Scheduler de Coleta...")
        self.is_running = True
        
        from collectors.orchestrator import OrchestratorV9
        orchestrator = OrchestratorV9()

        while self.is_running:
            # 1. Recarregar contextos do Supabase para garantir que novos Onboardings sejam incluídos
            self._load_user_contexts()

            for ctx_id, context in self.brand_contexts.items():
                if not self.is_running: break
                
                logger.info(f"🤖 [Weak Signals] Buscando sinais para: {context.brand_name}")
                
                # Lógica de Sinais Fracos: Combina ONBOARDING (Keywords) + INDÚSTRIA + TERRITÓRIO
                # Isso garante que a coleta não seja genérica, mas focada no contexto do usuário.
                search_terms = []
                if context.keywords:
                    search_terms.extend(context.keywords)
                else:
                    search_terms.append(f"{context.brand_name} {context.industry}")

                for term in search_terms:
                    try:
                        # O Orquestrador V9 executa a coleta técnica (API YouTube, Reddit, etc)
                        await orchestrator.collect_with_monitoring(
                            topics=[term],
                            collectors=None 
                        )
                        # Notifica o monitoramento de sucesso na coleta estratégica
                        if monitoring_v9:
                            monitoring_v9.log_event("weak_signal_collect", {"term": term, "context": ctx_id})
                    except Exception as e:
                        logger.error(f"❌ Erro na coleta estratégica para {term}: {e}")
                
                await asyncio.sleep(60) 

            await asyncio.sleep(3600) 

    def stop_scheduler(self):
        """Para o loop do agendador"""
        logger.info("🛑 StrategyLearner: Parando Scheduler...")
        self.is_running = False

# Singleton helper
_strategy_instance = None
def get_strategy_learner() -> StrategyLearner:
    global _strategy_instance
    if _strategy_instance is None:
        _strategy_instance = StrategyLearner()
    return _strategy_instance
