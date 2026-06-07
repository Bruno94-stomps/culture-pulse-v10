"""
Sistema de simulações de ML para análise de comportamento do consumidor brasileiro
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from typing import Dict, List, Tuple
import joblib
from pathlib import Path

class ConsumerBehaviorSimulator:
    """Simulador de comportamento do consumidor usando ML"""
    
    def __init__(self, model_path: Path):
        """
        Inicializar simulador
        
        Args:
            model_path: Caminho para salvar/carregar modelos
        """
        self.model_path = model_path
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        # Modelos especializados
        self.consumption_model = None
        self.engagement_model = None
        self.trend_model = None
        
        # Scaler para normalização
        self.scaler = StandardScaler()
        
    def train_models(
        self,
        historical_data: pd.DataFrame,
        features: List[str],
        target_cols: List[str]
    ) -> None:
        """
        Treinar modelos de simulação
        
        Args:
            historical_data: DataFrame com dados históricos
            features: Lista de features para treino
            target_cols: Colunas alvo para predição
        """
        X = historical_data[features]
        
        # Normalizar features
        X_scaled = self.scaler.fit_transform(X)
        
        # Treinar modelo de consumo
        y_consumption = historical_data[target_cols[0]]
        self.consumption_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.consumption_model.fit(X_scaled, y_consumption)
        
        # Treinar modelo de engajamento
        y_engagement = historical_data[target_cols[1]]
        self.engagement_model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            random_state=42
        )
        self.engagement_model.fit(X_scaled, y_engagement)
        
        # Treinar modelo de tendências
        y_trends = historical_data[target_cols[2]]
        self.trend_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            random_state=42
        )
        self.trend_model.fit(X_scaled, y_trends)
        
        # Salvar modelos
        self._save_models()
        
    def load_models(self) -> None:
        """Carregar modelos salvos"""
        try:
            self.consumption_model = joblib.load(
                self.model_path / "consumption_model.joblib"
            )
            self.engagement_model = joblib.load(
                self.model_path / "engagement_model.joblib"
            )
            self.trend_model = joblib.load(
                self.model_path / "trend_model.joblib"
            )
            self.scaler = joblib.load(
                self.model_path / "scaler.joblib"
            )
        except FileNotFoundError as e:
            raise Exception("Modelos não encontrados. Execute o treinamento primeiro.") from e
            
    def _save_models(self) -> None:
        """Salvar modelos treinados"""
        joblib.dump(self.consumption_model,
                   self.model_path / "consumption_model.joblib")
        joblib.dump(self.engagement_model,
                   self.model_path / "engagement_model.joblib")
        joblib.dump(self.trend_model,
                   self.model_path / "trend_model.joblib")
        joblib.dump(self.scaler,
                   self.model_path / "scaler.joblib")
        
    def simulate_scenarios(
        self,
        input_data: pd.DataFrame,
        features: List[str],
        n_scenarios: int = 3
    ) -> List[Dict[str, any]]:
        """
        Simular cenários de comportamento
        
        Args:
            input_data: Dados de entrada para simulação
            features: Features para usar na simulação
            n_scenarios: Número de cenários a gerar
            
        Returns:
            Lista de cenários simulados
        """
        scenarios = []
        X = input_data[features]
        X_scaled = self.scaler.transform(X)
        
        for i in range(n_scenarios):
            # Simular consumo
            consumption_pred = self.consumption_model.predict(X_scaled)
            
            # Simular engajamento
            engagement_pred = self.engagement_model.predict(X_scaled)
            
            # Simular tendências
            trend_pred = self.trend_model.predict(X_scaled)
            
            # Calcular intervalos de confiança
            consumption_conf = self._calculate_confidence_interval(
                self.consumption_model, X_scaled
            )
            
            engagement_conf = self._calculate_confidence_interval(
                self.engagement_model, X_scaled
            )
            
            trend_conf = self._calculate_confidence_interval(
                self.trend_model, X_scaled
            )
            
            # Montar cenário
            scenario = {
                "id": f"scenario_{i+1}",
                "consumption": {
                    "prediction": consumption_pred.mean(),
                    "confidence_interval": consumption_conf
                },
                "engagement": {
                    "prediction": engagement_pred.mean(),
                    "confidence_interval": engagement_conf
                },
                "trend": {
                    "prediction": trend_pred.mean(),
                    "confidence_interval": trend_conf
                },
                "composite_score": self._calculate_composite_score(
                    consumption_pred,
                    engagement_pred,
                    trend_pred
                )
            }
            
            scenarios.append(scenario)
            
        return scenarios
        
    def _calculate_confidence_interval(
        self,
        model: object,
        X: np.ndarray,
        n_bootstraps: int = 100
    ) -> Tuple[float, float]:
        """
        Calcular intervalo de confiança
        
        Args:
            model: Modelo treinado
            X: Dados de entrada
            n_bootstraps: Número de bootstraps
            
        Returns:
            Tupla com limite inferior e superior
        """
        predictions = []
        
        for _ in range(n_bootstraps):
            # Selecionar amostra aleatória
            indices = np.random.randint(0, X.shape[0], X.shape[0])
            sample = X[indices]
            
            # Fazer predição
            pred = model.predict(sample)
            predictions.append(pred.mean())
            
        # Calcular intervalos
        lower = np.percentile(predictions, 2.5)
        upper = np.percentile(predictions, 97.5)
        
        return (lower, upper)
        
    def _calculate_composite_score(
        self,
        consumption: np.ndarray,
        engagement: np.ndarray,
        trend: np.ndarray
    ) -> float:
        """
        Calcular score composto
        
        Args:
            consumption: Predições de consumo
            engagement: Predições de engajamento
            trend: Predições de tendência
            
        Returns:
            Score composto normalizado
        """
        # Pesos para cada componente
        weights = {
            "consumption": 0.4,
            "engagement": 0.3,
            "trend": 0.3
        }
        
        # Normalizar cada componente
        consumption_norm = (consumption - consumption.min()) / (consumption.max() - consumption.min())
        engagement_norm = (engagement - engagement.min()) / (engagement.max() - engagement.min())
        trend_norm = (trend - trend.min()) / (trend.max() - trend.min())
        
        # Calcular score ponderado
        composite_score = (
            weights["consumption"] * consumption_norm.mean() +
            weights["engagement"] * engagement_norm.mean() +
            weights["trend"] * trend_norm.mean()
        )
        
        return round(composite_score * 100, 2)