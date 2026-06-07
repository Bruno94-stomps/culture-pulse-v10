"""
🎯 Culture Intelligence Engine V9.0 - Feedback Learning Engine
Sistema de aprendizado contínuo baseado em feedback dos usuários
"""

import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score
import pickle
import os
import json
from typing import Dict, List, Tuple, Optional, Any
import logging
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd

class FeedbackLearningEngine:
    """
    Engine de aprendizado que melhora automaticamente baseado no feedback dos usuários
    Combina regressão (qualidade) + classificação (efetividade)
    """
    
    def __init__(self, model_dir: str = "cache/ml_models"):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Modelos de ML
        self.quality_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.effectiveness_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        
        # Dados de treinamento acumulados
        self.training_data = {
            "features": [],
            "quality_targets": [],
            "effectiveness_targets": [],
            "metadata": []
        }
        
        # Métricas de performance
        self.performance_history = []
        
        # Carregar modelos salvos se existirem
        self.load_models()
    
    def extract_features_from_feedback(self, feedback_data: Dict) -> np.ndarray:
        """
        Extrai features do feedback para ML
        
        Args:
            feedback_data: Dados do feedback coletado
            
        Returns:
            Array numpy com features
        """
        try:
            features = []
            
            # Features básicas
            config = feedback_data.get('original_config', {})
            refinement = feedback_data.get('ai_refinement', {})
            
            # 1. Número de termos originais
            original_terms = config.get('terms', [])
            features.append(len(original_terms) if original_terms else 0)
            
            # 2. Número de termos refinados
            refined_terms = refinement.get('refined_terms', [])
            features.append(len(refined_terms) if refined_terms else 0)
            
            # 3. Confiança do AI
            confidence = refinement.get('confidence_score', 0.5)
            features.append(float(confidence))
            
            # 4. Complexidade do contexto (baseado em tamanho)
            business_context = feedback_data.get('business_context', '')
            features.append(len(business_context.split()) if business_context else 0)
            
            # 5. Hora do dia (pode influenciar qualidade do feedback)
            hour = datetime.now().hour
            features.append(hour / 24.0)  # Normalizar 0-1
            
            # 6. Features culturais (se disponível)
            cultural_score = feedback_data.get('cultural_analysis', {}).get('cultural_score', 0.5)
            features.append(float(cultural_score))
            
            # 7. Diversidade de termos (Jaccard similarity)
            if original_terms and refined_terms:
                intersection = len(set(original_terms) & set(refined_terms))
                union = len(set(original_terms) | set(refined_terms))
                jaccard = intersection / union if union > 0 else 0
                features.append(jaccard)
            else:
                features.append(0.0)
            
            # 8. Sentimento do contexto (básico)
            sentiment_words = ['positivo', 'negativo', 'neutro', 'inovação', 'problema']
            sentiment_score = sum(1 for word in sentiment_words 
                                if word in business_context.lower()) / len(sentiment_words)
            features.append(sentiment_score)
            
            # 9. Complexidade linguística (aproximada)
            avg_word_length = np.mean([len(word) for word in business_context.split()]) if business_context else 0
            features.append(avg_word_length / 10.0)  # Normalizar
            
            # 10. Feature temporal (dia da semana)
            weekday = datetime.now().weekday() / 7.0  # 0-1
            features.append(weekday)
            
            return np.array(features)
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair features: {e}")
            # Retornar features padrão em caso de erro
            return np.zeros(10)
    
    def add_training_sample(self, feedback_data: Dict):
        """
        Adiciona amostra de feedback aos dados de treinamento
        """
        try:
            # Extrair features
            features = self.extract_features_from_feedback(feedback_data)
            
            # Targets
            user_rating = feedback_data.get('user_rating', 3.0)  # 1-5 scale
            effectiveness_score = feedback_data.get('effectiveness_score', 0.5)  # 0-1 scale
            
            # Converter rating para 0-1 para qualidade
            quality_target = (user_rating - 1) / 4.0  # 1-5 -> 0-1
            
            # Converter effectiveness para classificação binária
            effectiveness_target = 1 if effectiveness_score > 0.6 else 0
            
            # Adicionar aos dados de treinamento
            self.training_data["features"].append(features)
            self.training_data["quality_targets"].append(quality_target)
            self.training_data["effectiveness_targets"].append(effectiveness_target)
            self.training_data["metadata"].append({
                "timestamp": datetime.now().isoformat(),
                "session_id": feedback_data.get('session_id', 'unknown'),
                "original_rating": user_rating,
                "original_effectiveness": effectiveness_score
            })
            
            self.logger.info(f"✅ Amostra de treinamento adicionada - Total: {len(self.training_data['features'])}")
            
        except Exception as e:
            self.logger.error(f"Erro ao adicionar amostra: {e}")
    
    def train_models(self, min_samples: int = 10) -> Dict:
        """
        Treina os modelos de ML com os dados acumulados
        
        Args:
            min_samples: Número mínimo de amostras para treinar
            
        Returns:
            Métricas de performance dos modelos
        """
        try:
            n_samples = len(self.training_data["features"])
            
            if n_samples < min_samples:
                self.logger.warning(f"Poucos dados para treinar: {n_samples} < {min_samples}")
                return {"status": "insufficient_data", "samples": n_samples}
            
            # Preparar dados
            X = np.array(self.training_data["features"])
            y_quality = np.array(self.training_data["quality_targets"])
            y_effectiveness = np.array(self.training_data["effectiveness_targets"])
            
            # Split treino/validação
            test_size = min(0.3, max(0.1, 5/n_samples))  # Adaptar ao tamanho dos dados
            
            X_train_q, X_test_q, y_train_q, y_test_q = train_test_split(
                X, y_quality, test_size=test_size, random_state=42
            )
            
            X_train_e, X_test_e, y_train_e, y_test_e = train_test_split(
                X, y_effectiveness, test_size=test_size, random_state=42
            )
            
            # Treinar modelo de qualidade (regressão)
            self.quality_model.fit(X_train_q, y_train_q)
            quality_pred = self.quality_model.predict(X_test_q)
            quality_mse = mean_squared_error(y_test_q, quality_pred)
            quality_r2 = self.quality_model.score(X_test_q, y_test_q)
            
            # Treinar modelo de efetividade (classificação)
            self.effectiveness_model.fit(X_train_e, y_train_e)
            effectiveness_pred = self.effectiveness_model.predict(X_test_e)
            effectiveness_acc = accuracy_score(y_test_e, effectiveness_pred)
            
            # Métricas
            metrics = {
                "status": "success",
                "training_samples": n_samples,
                "quality_mse": float(quality_mse),
                "quality_r2": float(quality_r2),
                "effectiveness_accuracy": float(effectiveness_acc),
                "trained_at": datetime.now().isoformat()
            }
            
            # Salvar performance
            self.performance_history.append(metrics)
            
            # Salvar modelos
            self.save_models()
            
            self.logger.info(f"✅ Modelos treinados - R²: {quality_r2:.3f}, Acc: {effectiveness_acc:.3f}")
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Erro ao treinar modelos: {e}")
            return {"status": "error", "message": str(e)}
    
    def predict_refinement_quality(self, feedback_data: Dict) -> Dict:
        """
        Prediz a qualidade de um refinamento antes de apresentar ao usuário
        """
        try:
            # Extrair features
            features = self.extract_features_from_feedback(feedback_data)
            features = features.reshape(1, -1)  # Formato para predição
            
            # Verificar se modelos estão treinados
            if not hasattr(self.quality_model, 'feature_importances_'):
                return {
                    "predicted_quality": 0.5,
                    "predicted_effectiveness": 0.5,
                    "confidence": 0.0,
                    "status": "models_not_trained"
                }
            
            # Predições
            quality_pred = self.quality_model.predict(features)[0]
            effectiveness_pred = self.effectiveness_model.predict_proba(features)[0]
            
            # Confiança baseada na variância das árvores (para Random Forest)
            quality_confidence = 1.0 - np.std([tree.predict(features)[0] 
                                             for tree in self.quality_model.estimators_])
            quality_confidence = max(0.0, min(1.0, quality_confidence))
            
            # Converter efetividade para probabilidade
            effectiveness_prob = effectiveness_pred[1]  # Probabilidade de ser efetivo
            
            return {
                "predicted_quality": float(quality_pred),
                "predicted_effectiveness": float(effectiveness_prob),
                "confidence": float(quality_confidence),
                "recommendation": self._generate_recommendation(quality_pred, effectiveness_prob),
                "status": "success"
            }
            
        except Exception as e:
            self.logger.error(f"Erro na predição: {e}")
            return {
                "predicted_quality": 0.5,
                "predicted_effectiveness": 0.5,
                "confidence": 0.0,
                "status": "error"
            }
    
    def _generate_recommendation(self, quality: float, effectiveness: float) -> str:
        """Gera recomendação baseada nas predições"""
        if quality > 0.7 and effectiveness > 0.7:
            return "Refinamento de alta qualidade - Recomendado"
        elif quality > 0.5 and effectiveness > 0.5:
            return "Refinamento médio - Aceitar com revisão"
        else:
            return "Refinamento baixa qualidade - Revisar"
    
    def get_feature_importance(self) -> Dict:
        """Retorna importância das features para interpretabilidade"""
        try:
            if not hasattr(self.quality_model, 'feature_importances_'):
                return {"status": "models_not_trained"}
            
            feature_names = [
                "num_original_terms", "num_refined_terms", "ai_confidence",
                "context_complexity", "hour_of_day", "cultural_score",
                "term_diversity", "sentiment_score", "linguistic_complexity",
                "weekday"
            ]
            
            quality_importance = self.quality_model.feature_importances_
            effectiveness_importance = self.effectiveness_model.feature_importances_
            
            importance_data = {}
            for i, name in enumerate(feature_names):
                importance_data[name] = {
                    "quality_importance": float(quality_importance[i]),
                    "effectiveness_importance": float(effectiveness_importance[i])
                }
            
            return {
                "status": "success",
                "feature_importance": importance_data,
                "top_quality_features": sorted(
                    feature_names, 
                    key=lambda x: quality_importance[feature_names.index(x)], 
                    reverse=True
                )[:3],
                "top_effectiveness_features": sorted(
                    feature_names,
                    key=lambda x: effectiveness_importance[feature_names.index(x)],
                    reverse=True
                )[:3]
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular importância: {e}")
            return {"status": "error"}
    
    def save_models(self):
        """Salva modelos treinados"""
        try:
            # Salvar modelos
            with open(os.path.join(self.model_dir, "quality_model.pkl"), "wb") as f:
                pickle.dump(self.quality_model, f)
            
            with open(os.path.join(self.model_dir, "effectiveness_model.pkl"), "wb") as f:
                pickle.dump(self.effectiveness_model, f)
            
            # Salvar dados de treinamento
            with open(os.path.join(self.model_dir, "training_data.json"), "w") as f:
                # Converter arrays numpy para listas para JSON
                data_to_save = {
                    "features": [feat.tolist() for feat in self.training_data["features"]],
                    "quality_targets": self.training_data["quality_targets"],
                    "effectiveness_targets": self.training_data["effectiveness_targets"],
                    "metadata": self.training_data["metadata"]
                }
                json.dump(data_to_save, f, indent=2)
            
            # Salvar histórico de performance
            with open(os.path.join(self.model_dir, "performance_history.json"), "w") as f:
                json.dump(self.performance_history, f, indent=2)
            
            self.logger.info("✅ Modelos salvos com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar modelos: {e}")
    
    def load_models(self):
        """Carrega modelos salvos"""
        try:
            quality_path = os.path.join(self.model_dir, "quality_model.pkl")
            effectiveness_path = os.path.join(self.model_dir, "effectiveness_model.pkl")
            training_path = os.path.join(self.model_dir, "training_data.json")
            performance_path = os.path.join(self.model_dir, "performance_history.json")
            
            # Carregar modelos
            if os.path.exists(quality_path):
                with open(quality_path, "rb") as f:
                    self.quality_model = pickle.load(f)
                    
            if os.path.exists(effectiveness_path):
                with open(effectiveness_path, "rb") as f:
                    self.effectiveness_model = pickle.load(f)
            
            # Carregar dados de treinamento
            if os.path.exists(training_path):
                with open(training_path, "r") as f:
                    data = json.load(f)
                    self.training_data = {
                        "features": [np.array(feat) for feat in data["features"]],
                        "quality_targets": data["quality_targets"],
                        "effectiveness_targets": data["effectiveness_targets"],
                        "metadata": data["metadata"]
                    }
            
            # Carregar histórico
            if os.path.exists(performance_path):
                with open(performance_path, "r") as f:
                    self.performance_history = json.load(f)
            
            self.logger.info("✅ Modelos carregados com sucesso")
            
        except Exception as e:
            self.logger.warning(f"Não foi possível carregar modelos salvos: {e}")
    
    def get_learning_stats(self) -> Dict:
        """Retorna estatísticas do aprendizado"""
        try:
            stats = {
                "total_training_samples": len(self.training_data["features"]),
                "models_trained": hasattr(self.quality_model, 'feature_importances_'),
                "training_sessions": len(self.performance_history),
                "avg_quality_r2": 0.0,
                "avg_effectiveness_acc": 0.0,
                "last_training": None
            }
            
            if self.performance_history:
                # Calcular médias
                quality_scores = [p.get("quality_r2", 0) for p in self.performance_history if "quality_r2" in p]
                effectiveness_scores = [p.get("effectiveness_accuracy", 0) for p in self.performance_history if "effectiveness_accuracy" in p]
                
                if quality_scores:
                    stats["avg_quality_r2"] = np.mean(quality_scores)
                if effectiveness_scores:
                    stats["avg_effectiveness_acc"] = np.mean(effectiveness_scores)
                
                stats["last_training"] = self.performance_history[-1].get("trained_at")
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular stats: {e}")
            return {}

def create_feedback_learning_engine():
    """Factory function para criar learning engine"""
    return FeedbackLearningEngine()

# Test básico
if __name__ == "__main__":
    # Teste rápido
    engine = create_feedback_learning_engine()
    
    # Dados de teste
    test_feedback = {
        "session_id": "test_001",
        "business_context": "Startup fintech São Paulo",
        "original_config": {"terms": ["fintech", "pagamentos"]},
        "ai_refinement": {
            "confidence_score": 0.85,
            "refined_terms": ["fintech", "pagamentos", "PIX", "digital"]
        },
        "user_rating": 4.2,
        "effectiveness_score": 0.75
    }
    
    # Adicionar amostra
    engine.add_training_sample(test_feedback)
    
    # Tentar predição (antes do treinamento)
    prediction = engine.predict_refinement_quality(test_feedback)
    
    print("🎯 Feedback Learning Test:")
    print(f"✅ Amostras de treinamento: {engine.get_learning_stats()['total_training_samples']}")
    print(f"✅ Predição qualidade: {prediction['predicted_quality']:.2f}")
    print(f"✅ Predição efetividade: {prediction['predicted_effectiveness']:.2f}")
    print(f"✅ Status: {prediction['status']}")
