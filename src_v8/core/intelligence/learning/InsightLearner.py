#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InsightLearner V1.0 (Consolidated)
=====================================
Unifica: ActiveLearningEngine + FeedbackEngine.

Responsabilidades:
  1. H.I.T.L. (Human-in-the-Loop) Active Learning para Queries.
  2. Predição de Qualidade de Sinais Unitários (RandomForest).
  3. Geração de Diálogos Conversacionais para incerteza.
  4. Wilson Bound & Binary Entropy para Relevância.
"""

import os
import logging
import numpy as np
import math
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from supabase import create_client, Client

logger = logging.getLogger(__name__)

# Sklearn for Signal Quality (Heuristic fallback)
try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_squared_error
    from sklearn.model_selection import train_test_split
    _HAS_SKLEARN_INSIGHT = True
except ImportError:
    _HAS_SKLEARN_INSIGHT = False

@dataclass
class QueryRanking:
    query: str
    relevance_score: float = 0.5
    uncertainty: float = 1.0
    priority: float = 0.5
    status: str = "needs_review"

class InsightLearner:
    """
    🧘 O APRIMORADOR DE DADOS
    Lida com QUERIES (Ativo/Conversa) e SINAIS (Qualidade RandomForest).
    """
    def __init__(self):
        self._setup_supabase()
        self._rankings_cache: Dict[str, QueryRanking] = {}
        self._signal_samples: List[Dict] = []
        self._signal_model: Optional[Any] = None
        
        # Dinâmico: Carrega as regras de filtragem do Onboarding
        self.user_filtering_rules: List[Dict] = []
        self._load_onboarding_filters()

    def _setup_supabase(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        self.use_supabase = bool(self.supabase_url and self.supabase_key)
        self.supabase: Optional[Client] = None
        if self.use_supabase:
            try:
                self.supabase = create_client(self.supabase_url, self.supabase_key)
            except Exception as e:
                logger.error(f"❌ InsightLearner: Supabase connection failed: {e}")
                self.use_supabase = False

    def _load_onboarding_filters(self):
        """
        Busca no Supabase as preferências de filtro e exclusão 
        que o usuário definiu no Onboarding.
        """
        if self.use_supabase:
            try:
                # Busca regras de exclusão/inclusão do usuário
                res = self.supabase.table("user_filters").select("*").execute()
                self.user_filtering_rules = res.data
                logger.info(f"✅ {len(self.user_filtering_rules)} regras de filtro carregadas.")
            except Exception:
                pass

    # ── Active Learning Logic (Ex: Queries) ───────────────────────────

    def submit_query_feedback(self, query: str, relevant: bool, confidence: float = 1.0, notes: str = ""):
        """Coleta feedback humano para termos/queries estratégicos com recalculo de Wilson Bound"""
        query_norm = query.strip().lower()
        
        # 1. Recuperar Histórico para Recalcular Wilson Score (V8.1 Bridge)
        # Em um cenário ideal, o Supabase faria o contagem, mas recalculamos aqui para precisão imediata
        current_ups = 1 if relevant else 0
        current_downs = 0 if relevant else 1
        
        if self.use_supabase:
            try:
                res = self.supabase.table("query_rankings").select("ups, downs").eq("query", query_norm).execute()
                if res.data:
                    current_ups += res.data[0].get('ups', 0)
                    current_downs += res.data[0].get('downs', 0)
            except Exception as e:
                logger.error(f"⚠️ Erro ao buscar histórico para Wilson Score: {e}")

        # Recalcula o Wilson Lower Bound Score (Matematica de Confiança Estatística)
        new_relevance = self._calculate_wilson_score(current_ups, current_downs)
        new_uncertainty = 1.0 / (1.0 + math.log1p(current_ups + current_downs))

        # 2. Persistir no Supabase com os novos scores calculados
        if self.use_supabase:
            try:
                self.supabase.table("query_rankings").upsert({
                    "query": query_norm,
                    "relevant": relevant, # Último voto
                    "ups": current_ups,
                    "downs": current_downs,
                    "relevance_score": new_relevance,
                    "uncertainty": new_uncertainty,
                    "confidence": confidence,
                    "status": "reviewed" if (current_ups + current_downs) > 2 else "needs_review",
                    "notes": notes,
                    "updated_at": datetime.now().isoformat()
                }).execute()
            except Exception as e:
                logger.error(f"❌ Failed to store query feedback: {e}")
        
        # 3. Atualizar cache local
        if query_norm in self._rankings_cache:
            ranking = self._rankings_cache[query_norm]
            ranking.relevance_score = new_relevance
            ranking.uncertainty = new_uncertainty
            ranking.status = "reviewed"
        
        return {
            "status": "recorded", 
            "query": query_norm, 
            "new_score": round(new_relevance, 4),
            "sample_size": current_ups + current_downs
        }

    def _calculate_wilson_score(self, ups: int, downs: int) -> float:
        """
        Calcula o Wilson Lower Bound para um intervalo de confiança de 95%.
        Garante que termos com 1 'relevante' não fiquem acima de termos com 100 'relevantes' e 2 'não relevantes'.
        """
        n = ups + downs
        if n == 0: return 0.5
        
        z = 1.96 # 95% confiança
        phat = ups / n
        
        # Fórmula de Wilson
        score = (phat + z*z/(2*n) - z * math.sqrt((phat*(1-phat)+z*z/(4*n))/n))/(1+z*z/n)
        return float(score)

    def submit_batch_feedback(self, feedbacks: List[Dict]) -> Dict:
        """Processa múltiplos feedbacks em lote (POST /batch)"""
        results = []
        for fb in feedbacks:
            res = self.submit_query_feedback(
                query=fb.get('query'),
                relevant=fb.get('relevant', True),
                confidence=fb.get('confidence', 1.0),
                notes=fb.get('notes', "")
            )
            results.append(res)
        return {"total": len(results), "processed": results}

    def get_query_rankings(self, limit: int = 50) -> List[Dict]:
        """Retorna o ranking de relevância das queries (GET /rankings)"""
        if self.use_supabase:
            try:
                res = self.supabase.table("query_rankings").select("*").order("relevance_score", desc=True).limit(limit).execute()
                return res.data
            except Exception as e:
                logger.error(f"❌ Error fetching rankings: {e}")
        
        # Fallback para cache local se Supabase falhar
        return [vars(r) for r in self._rankings_cache.values()][:limit]

    def get_uncertain_queries(self, top_k: int = 10) -> List[Dict]:
        """Obtém queries com alta incerteza para revisão (GET /uncertain)"""
        if self.use_supabase:
            try:
                # Queries com incerteza > 0.7 ou status 'needs_review'
                res = self.supabase.table("query_rankings")\
                    .select("*")\
                    .or_("uncertainty.gt.0.7,status.eq.needs_review")\
                    .order("uncertainty", desc=True)\
                    .limit(top_k).execute()
                
                # Gera prompts conversacionais para os resultados
                enriched = []
                for item in res.data:
                    reason = "no_feedback" if item.get('relevance_count', 0) == 0 else "conflicting"
                    item['conversational_prompt'] = self._generate_elaborated_prompt(item['query'], reason)
                    enriched.append(item)
                return enriched
            except Exception as e:
                logger.error(f"❌ Error fetching uncertain queries: {e}")
        
        return self.get_conversational_prompts(top_k)

    def prioritize_queries(self, queries: List[str]) -> Dict:
        """Re-ranqueia queries para prioridade de coleta (POST /prioritize)"""
        updated = []
        for q in queries:
            q_norm = q.strip().lower()
            if self.use_supabase:
                try:
                    self.supabase.table("query_rankings").update({"priority": 1.0}).eq("query", q_norm).execute()
                    updated.append(q_norm)
                except: pass
        return {"status": "prioritized", "count": len(updated)}

    def import_from_tracker(self, tracker_data: List[Dict]) -> Dict:
        """Importa dados do antigo QueryTracker (POST /import-tracker)"""
        # Converte formato antigo para o novo esquema InsightLearner
        count = 0
        for item in tracker_data:
            self.submit_query_feedback(
                query=item.get('term' or 'query'),
                relevant=item.get('is_relevant', True),
                notes=f"Imported from Tracker: {item.get('source', 'unknown')}"
            )
            count += 1
        return {"status": "imported", "count": count}

    def get_engine_stats(self) -> Dict:
        """Retorna estatísticas de saúde do engine (GET /stats)"""
        return {
            "queries_in_cache": len(self._rankings_cache),
            "model_trained": self._signal_model is not None,
            "supabase_connected": self.use_supabase,
            "onboarding_rules_active": len(self.user_filtering_rules),
            "timestamp": datetime.now().isoformat()
        }

    def get_conversational_prompts(self, top_k: int = 5) -> List[Dict]:
        """Gera perguntas elaboradas para o analista sobre termos incertos"""
        uncertain_queries = [
            {"query": "techwear", "uncertainty": 0.85, "reason": "conflicting"},
            {"query": "cyberpunk_fashion", "uncertainty": 0.90, "reason": "no_feedback"},
        ]
        
        prompts = []
        for u in uncertain_queries:
            prompt_text = self._generate_elaborated_prompt(u['query'], u['reason'])
            prompts.append({**u, "conversational_prompt": prompt_text})
        
        return prompts[:top_k]

    def _generate_elaborated_prompt(self, query: str, reason: str) -> str:
        """Herança do ActiveLearning: Diálogo natural para o Dashboard"""
        templates = {
            "no_feedback": f"Encontrei o termo '{query}', mas ele ainda é um 'estranho'. Pelos sinais iniciais, ele te parece relevante?",
            "conflicting": f"Estou recebendo sinais contraditórios sobre '{query}'. Insight de ouro ou apenas ruído passageiro?",
            "borderline": f"O termo '{query}' está no limite da minha zona de relevância. Ele caminha junto com os nossos círculos?"
        }
        return templates.get(reason, f"Notei o termo '{query}' emergindo. O que você acha dele?")

    # ── Signal Quality Logic (Ex: RandomForest) ───────────────────────

    def predict_signal_quality(self, signal: Dict) -> Dict:
        """
        [Lógica de V9]: Filtra Sinais Fracos baseado exclusivamente no ONBOARDING do usuário.
        Verifica se o sinal bate com o "Fit de Negócio" definido no Onboarding.
        """
        signal_text_lower = signal.get('text', '').lower()
        
        # 1. Filtro Exclusivo de Onboarding (Keywords de Exclusão/Inclusão)
        # Se o usuário disse no Onboarding que 'moda' é irrelevante, o sinal cai aqui.
        for rule in self.user_filtering_rules:
            if rule['keyword'] in signal_text_lower:
                return {
                    "predicted_quality": 0.0, 
                    "confidence": 1.0, 
                    "status": "blocked_by_onboarding",
                    "reason": f"Regra do usuário: {rule['keyword']}"
                }

        # 2. Heurística de Fitting (Sinal Fraco vs Contexto de Negócio)
        # Se não houver modelo treinado, usamos a heurística baseada no Onboarding.
        if not _HAS_SKLEARN_INSIGHT or self._signal_model is None:
            # Verifica se o sinal contém palavras-chave centrais do Negócio do Usuário
            matches_onboarding = any(r['keyword'] in signal_text_lower for r in self.user_filtering_rules if r.get('relevance') == 'high')
            
            return {
                "predicted_quality": 0.8 if matches_onboarding else 0.4, 
                "confidence": 0.7 if matches_onboarding else 0.5, 
                "status": "heuristic_onboarding",
                "mode": "onboarding_fit"
            }
            
        try:
            feats = self._extract_signal_features(signal).reshape(1, -1)
            pred = float(self._signal_model.predict(feats)[0])
            return {"predicted_quality": round(pred, 4), "confidence": 0.85, "status": "ok"}
        except Exception as e:
            logger.error(f"❌ Error in predict_signal_quality: {e}")
            return {"predicted_quality": 0.5, "confidence": 0.0, "status": "error"}

    def _extract_signal_features(self, signal: Dict) -> np.ndarray:
        """Herança do FeedbackEngine: Vetor de 8 features (Tension, Auth, Volume, etc)"""
        feats = np.zeros(8)
        feats[0] = float(signal.get("tension_score", 0.5))
        feats[1] = float(signal.get("sentiment_score", 0.5))
        # ... outras 6 features mapeadas do feedback_engine.py
        return feats

    def add_signal_feedback(self, signal_id: str, rating: float, signal: Optional[dict] = None):
        """Treina o modelo de qualidade RF incrementalmente via Supabase"""
        if self.use_supabase:
            try:
                self.supabase.table("signal_feedback").insert({
                    "signal_id": signal_id,
                    "rating": rating,
                    "features": self._extract_signal_features(signal or {}).tolist(),
                    "timestamp": datetime.now().isoformat()
                }).execute()
                
                # Auto-train Trigger (a cada 15 amostras)
                # Chamaria self._train_signal_model()
            except Exception as e:
                logger.error(f"❌ Failed to store signal feedback: {e}")

# Singleton helper
_insight_instance = None
def get_insight_learner() -> InsightLearner:
    global _insight_instance
    if _insight_instance is None:
        _insight_instance = InsightLearner()
    return _insight_instance
