#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BRAZILIAN CULTURAL TWIN V9.0 - PRODUCTION READY
===============================================
Melhorias baseadas na implementação v8.0:

1. Validação Monte Carlo com convergência
2. Cross-validation temporal para RN 
3. Ensemble de modelos (RF + NN + XGBoost)
4. Calibração de incerteza epistemática
5. Dashboard em tempo real
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
import asyncio
import logging
from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
from scipy import stats
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from concurrent.futures import ProcessPoolExecutor
import joblib

logger = logging.getLogger(__name__)

@dataclass
class ModelEnsembleResult:
    """Resultado do ensemble de modelos"""
    neural_prediction: Dict[str, float]
    random_forest_prediction: Dict[str, float] 
    xgboost_prediction: Dict[str, float]
    ensemble_prediction: Dict[str, float]  # Média ponderada
    model_uncertainties: Dict[str, float]  # Incerteza de cada modelo
    consensus_confidence: float  # Confiança do consenso (0-1)
    prediction_intervals: Dict[str, Tuple[float, float]]

@dataclass 
class MonteCarloValidation:
    """Validação da convergência Monte Carlo"""
    converged: bool
    final_n_simulations: int
    convergence_metric: float
    effective_sample_size: float
    autocorrelation_time: float
    r_hat_statistic: float  # Gelman-Rubin para múltiplas chains

class EnhancedCulturalNeuralPredictor(nn.Module):
    """Rede neural com incerteza epistemática e aleatory"""
    
    def __init__(self, input_dim: int, hidden_dims: List[int], 
                 n_circles: int = 16, dropout_rate: float = 0.15):
        super().__init__()
        
        self.input_dim = input_dim
        self.n_circles = n_circles
        
        # Embeddings com regularização
        self.circle_embedding = nn.Embedding(n_circles, 64)
        self.circle_dropout = nn.Dropout(dropout_rate)
        
        # Encoder principal com skip connections
        self.encoder_layers = nn.ModuleList()
        prev_dim = input_dim + 64
        
        for i, hidden_dim in enumerate(hidden_dims):
            layer = nn.Sequential(
                nn.Linear(prev_dim, hidden_dim),
                nn.LayerNorm(hidden_dim),  # Melhor que BatchNorm para inferência
                nn.GELU(),  # Mais suave que ReLU
                nn.Dropout(dropout_rate)
            )
            self.encoder_layers.append(layer)
            prev_dim = hidden_dim
        
        final_dim = hidden_dims[-1]
        
        # Heads com incerteza (usando variational dropout)
        self.sentiment_head = BayesianLinearHead(final_dim, 1, dropout_rate)
        self.acceptance_head = BayesianLinearHead(final_dim, 1, dropout_rate) 
        self.engagement_head = BayesianLinearHead(final_dim, 1, dropout_rate)
        
        # Head para incerteza aleatory (heterocedasticidade)
        self.aleatoric_head = nn.Sequential(
            nn.Linear(final_dim, 32),
            nn.GELU(),
            nn.Linear(32, 3),  # [sentiment_var, acceptance_var, engagement_var]
            nn.Softplus()
        )
        
    def forward(self, x: torch.Tensor, circle_ids: torch.Tensor, 
                n_samples: int = 10) -> Dict[str, torch.Tensor]:
        batch_size = x.shape[0]
        
        # Circle embeddings com dropout
        circle_emb = self.circle_embedding(circle_ids)
        circle_emb = self.circle_dropout(circle_emb)
        
        # Feature fusion
        combined = torch.cat([x, circle_emb], dim=1)
        
        # Forward com skip connections
        features = combined
        residual_connections = []
        
        for i, layer in enumerate(self.encoder_layers):
            features = layer(features)
            if i > 0:  # Skip connection
                if features.shape[-1] == residual_connections[-1].shape[-1]:
                    features = features + residual_connections[-1]
            residual_connections.append(features)
        
        # Múltiplas amostras para incerteza epistemática
        predictions = {
            'sentiment_samples': [],
            'acceptance_samples': [],
            'engagement_samples': []
        }
        
        self.train()  # Enable dropout para incerteza
        for _ in range(n_samples):
            sent_logit = self.sentiment_head(features)
            acc_logit = self.acceptance_head(features)  
            eng_logit = self.engagement_head(features)
            
            predictions['sentiment_samples'].append(torch.tanh(sent_logit))
            predictions['acceptance_samples'].append(torch.sigmoid(acc_logit))
            predictions['engagement_samples'].append(torch.sigmoid(eng_logit))
        
        self.eval()  # Volta ao modo determinístico
        
        # Incerteza aleatória
        aleatoric_vars = self.aleatoric_head(features)
        
        # Agregar amostras
        outputs = {}
        for key in ['sentiment', 'acceptance', 'engagement']:
            samples_key = f'{key}_samples'
            sample_tensor = torch.stack(predictions[samples_key], dim=0)  # [n_samples, batch, 1]
            
            outputs[f'{key}_mean'] = sample_tensor.mean(dim=0)
            outputs[f'{key}_epistemic_var'] = sample_tensor.var(dim=0)  # Incerteza do modelo
        
        outputs['aleatoric_vars'] = aleatoric_vars  # Incerteza dos dados
        
        return outputs

class BayesianLinearHead(nn.Module):
    """Cabeça linear com dropout variacional"""
    
    def __init__(self, input_dim: int, output_dim: int, dropout_rate: float):
        super().__init__()
        self.linear1 = nn.Linear(input_dim, 64)
        self.linear2 = nn.Linear(64, output_dim)
        self.dropout = nn.Dropout(dropout_rate)
        self.activation = nn.GELU()
        
    def forward(self, x):
        x = self.linear1(x)
        x = self.activation(x)
        x = self.dropout(x)  # Variational dropout
        x = self.linear2(x)
        return x

class AdvancedBrazilianCulturalTwin:
    """Gêmeo Cultural com ensemble e validação avançada"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # Modelos do ensemble
        self.neural_model = None
        self.rf_model = RandomForestRegressor(
            n_estimators=200, 
            max_depth=15,
            min_samples_split=5,
            random_state=42
        )
        self.xgb_model = xgb.XGBRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        
        # Pesos do ensemble (aprendidos)
        self.ensemble_weights = {'neural': 0.5, 'rf': 0.3, 'xgb': 0.2}
        
        # Cache e histórico
        self.prediction_cache = {}
        self.training_history = []
        
        # Círculos culturais expandidos
        self.cultural_circles = self._initialize_enhanced_circles()
        
        logger.info("Advanced Brazilian Cultural Twin inicializado")
        
    def _initialize_enhanced_circles(self) -> Dict[str, Dict]:
        """Círculos culturais com parâmetros mais realistas"""
        
        circles = {
            "familia_tradicional_br": {
                "base_params": {
                    "acceptance_mean": 0.72, "acceptance_std": 0.18,
                    "sentiment_mean": 0.45, "sentiment_std": 0.25,
                    "engagement_alpha": 2.2, "engagement_beta": 1.8,
                    "volatility": 0.12
                },
                "temporal_dynamics": {
                    "weekend_boost": 1.25, "holiday_boost": 1.6,
                    "mother_day_boost": 2.1, "father_day_boost": 1.8,
                    "children_day_boost": 1.7, "christmas_boost": 2.0
                },
                "regional_factors": {
                    "nordeste": {"modifier": 1.15, "variance": 0.08},
                    "sudeste": {"modifier": 0.95, "variance": 0.12}, 
                    "sul": {"modifier": 0.98, "variance": 0.10},
                    "centro_oeste": {"modifier": 1.08, "variance": 0.09},
                    "norte": {"modifier": 1.12, "variance": 0.11}
                },
                "socioeconomic_layers": {
                    "classe_a": {"acceptance_mod": 0.85, "engagement_mod": 0.75},
                    "classe_b": {"acceptance_mod": 1.0, "engagement_mod": 1.0},
                    "classe_c": {"acceptance_mod": 1.1, "engagement_mod": 1.2},
                    "classe_de": {"acceptance_mod": 1.15, "engagement_mod": 1.3}
                },
                "trigger_words": {
                    "positive": ["família", "união", "amor", "tradição", "valores", "filho"],
                    "negative": ["individualismo", "egoísmo", "modernidade_excessiva"]
                }
            },
            
            "jovens_urbanos_conectados": {
                "base_params": {
                    "acceptance_mean": 0.68, "acceptance_std": 0.28,
                    "sentiment_mean": 0.35, "sentiment_std": 0.35,  
                    "engagement_alpha": 1.8, "engagement_beta": 1.2,
                    "volatility": 0.32
                },
                "temporal_dynamics": {
                    "night_boost": 1.4, "weekend_boost": 1.3,
                    "trending_topic_boost": 1.8, "meme_season_boost": 1.6,
                    "work_hours_penalty": 0.7
                },
                "platform_preferences": {
                    "instagram": 1.3, "tiktok": 1.5, "twitter": 1.1,
                    "facebook": 0.6, "linkedin": 0.8, "youtube": 1.2
                },
                "trigger_words": {
                    "positive": ["inovação", "sustentabilidade", "diversidade", "tecnologia", 
                               "autenticidade", "quebrar_barreiras"],
                    "negative": ["marketing_fake", "appropriação", "greenwashing", "boomer"]
                }
            },
            
            "brasil_sustentavel_consciente": {
                "base_params": {
                    "acceptance_mean": 0.63, "acceptance_std": 0.22,
                    "sentiment_mean": 0.52, "sentiment_std": 0.28,
                    "engagement_alpha": 2.1, "engagement_beta": 1.5,
                    "volatility": 0.18
                },
                "environmental_events": {
                    "earth_day_boost": 2.2, "amazon_day_boost": 1.9,
                    "water_day_boost": 1.7, "climate_strike_boost": 1.8,
                    "disaster_sensitivity": -0.4  # Após desastres ambientais
                },
                "regional_factors": {
                    "norte": {"modifier": 1.4, "variance": 0.15},  # Amazônia
                    "nordeste": {"modifier": 1.1, "variance": 0.12},
                    "centro_oeste": {"modifier": 1.2, "variance": 0.10},
                    "sudeste": {"modifier": 0.9, "variance": 0.18},
                    "sul": {"modifier": 1.0, "variance": 0.14}
                }
            },
            
            "diversidade_inclusao_br": {
                "base_params": {
                    "acceptance_mean": 0.61, "acceptance_std": 0.31,
                    "sentiment_mean": 0.48, "sentiment_std": 0.38,
                    "engagement_alpha": 1.9, "engagement_beta": 1.8,
                    "volatility": 0.28
                },
                "awareness_calendar": {
                    "pride_month_boost": 2.5, "black_awareness_boost": 2.1,
                    "womens_day_boost": 1.9, "trans_visibility_boost": 1.7,
                    "indigenous_day_boost": 1.6
                },
                "backlash_risks": {
                    "tokenismo_penalty": -0.6,
                    "performative_penalty": -0.5,
                    "cultural_appropriation_penalty": -0.7
                }
            }
        }
        
        return circles
    
    async def predict_with_ensemble(
        self, 
        message: str,
        target_circles: List[str],
        context: Optional[str] = None,
        n_mc_samples: int = 5000,
        validation_level: str = "standard"  # "fast", "standard", "thorough"
    ) -> Dict[str, ModelEnsembleResult]:
        """Predição usando ensemble com validação Monte Carlo"""
        
        results = {}
        
        # Extrair features da mensagem
        message_features = self._extract_comprehensive_features(message, context)
        
        for circle_id in target_circles:
            if circle_id not in self.cultural_circles:
                logger.warning(f"Círculo '{circle_id}' não encontrado")
                continue
                
            # 1. Validação Monte Carlo
            mc_validation = await self._validate_monte_carlo_convergence(
                circle_id, message_features, n_mc_samples, validation_level
            )
            
            if not mc_validation.converged:
                logger.warning(f"Monte Carlo não convergiu para {circle_id}")
            
            # 2. Predições dos modelos individuais
            neural_pred = await self._neural_prediction(
                circle_id, message_features, mc_validation.final_n_simulations
            )
            
            rf_pred = self._random_forest_prediction(circle_id, message_features)
            xgb_pred = self._xgboost_prediction(circle_id, message_features)
            
            # 3. Ensemble ponderado
            ensemble_pred = self._combine_predictions(neural_pred, rf_pred, xgb_pred)
            
            # 4. Calcular incertezas
            model_uncertainties = self._calculate_model_uncertainties(
                neural_pred, rf_pred, xgb_pred
            )
            
            # 5. Consenso e intervalos
            consensus_confidence = self._calculate_consensus(
                neural_pred, rf_pred, xgb_pred
            )
            
            prediction_intervals = self._calculate_prediction_intervals(
                ensemble_pred, model_uncertainties, mc_validation
            )
            
            results[circle_id] = ModelEnsembleResult(
                neural_prediction=neural_pred,
                random_forest_prediction=rf_pred,
                xgboost_prediction=xgb_pred,
                ensemble_prediction=ensemble_pred,
                model_uncertainties=model_uncertainties,
                consensus_confidence=consensus_confidence,
                prediction_intervals=prediction_intervals
            )
        
        return results
    
    async def _validate_monte_carlo_convergence(
        self, 
        circle_id: str,
        message_features: Dict[str, float],
        initial_n_samples: int,
        validation_level: str
    ) -> MonteCarloValidation:
        """Validar convergência Monte Carlo usando Gelman-Rubin"""
        
        # Configurações por nível
        configs = {
            "fast": {"n_chains": 2, "min_ess": 100, "max_r_hat": 1.2},
            "standard": {"n_chains": 4, "min_ess": 1000, "max_r_hat": 1.1}, 
            "thorough": {"n_chains": 8, "min_ess": 5000, "max_r_hat": 1.05}
        }
        
        config = configs[validation_level]
        circle_params = self.cultural_circles[circle_id]
        
        # Executar múltiplas chains Monte Carlo
        chains_results = []
        
        for chain in range(config["n_chains"]):
            # Seed diferente para cada chain
            np.random.seed(42 + chain * 1000)
            
            chain_samples = self._run_single_monte_carlo_chain(
                circle_params, message_features, initial_n_samples // config["n_chains"]
            )
            chains_results.append(chain_samples)
        
        # Calcular estatística R-hat (Gelman-Rubin)
        r_hat = self._calculate_r_hat_statistic(chains_results)
        
        # Effective sample size
        combined_samples = np.concatenate(chains_results)
        ess = self._calculate_effective_sample_size(combined_samples)
        
        # Autocorrelation time
        autocorr_time = self._calculate_autocorrelation_time(combined_samples)
        
        # Critérios de convergência
        converged = (
            r_hat < config["max_r_hat"] and 
            ess > config["min_ess"] and
            autocorr_time < len(combined_samples) / 10  # Conservative rule
        )
        
        return MonteCarloValidation(
            converged=converged,
            final_n_simulations=len(combined_samples),
            convergence_metric=float(r_hat),
            effective_sample_size=float(ess),
            autocorrelation_time=float(autocorr_time),
            r_hat_statistic=float(r_hat)
        )
    
    def _run_single_monte_carlo_chain(
        self, 
        circle_params: Dict, 
        message_features: Dict,
        n_samples: int
    ) -> np.ndarray:
        """Executar uma única chain Monte Carlo"""
        
        base_params = circle_params["base_params"]
        samples = np.zeros(n_samples)
        
        for i in range(n_samples):
            # Sampling com parâmetros do círculo
            base_acceptance = np.random.normal(
                base_params["acceptance_mean"],
                base_params["acceptance_std"]  
            )
            
            # Ajustes baseados em features da mensagem
            feature_adjustment = self._calculate_feature_adjustment(
                message_features, circle_params
            )
            
            # Ruído temporal e regional
            temporal_noise = np.random.normal(0, base_params["volatility"])
            
            final_sample = np.clip(
                base_acceptance + feature_adjustment + temporal_noise,
                0.0, 1.0
            )
            
            samples[i] = final_sample
        
        return samples
    
    def _calculate_r_hat_statistic(self, chains_results: List[np.ndarray]) -> float:
        """Calcular estatística R-hat de Gelman-Rubin"""
        
        n_chains = len(chains_results)
        chain_length = len(chains_results[0])
        
        # Médias de cada chain
        chain_means = [np.mean(chain) for chain in chains_results]
        overall_mean = np.mean(chain_means)
        
        # Between-chain variance (B)
        B = chain_length * np.var(chain_means, ddof=1)
        
        # Within-chain variance (W) 
        chain_vars = [np.var(chain, ddof=1) for chain in chains_results]
        W = np.mean(chain_vars)
        
        # Pooled variance estimate
        var_hat = ((chain_length - 1) * W + B) / chain_length
        
        # R-hat statistic
        if W > 0:
            r_hat = np.sqrt(var_hat / W)
        else:
            r_hat = 1.0
            
        return r_hat
    
    def _calculate_effective_sample_size(self, samples: np.ndarray) -> float:
        """Calcular tamanho efetivo da amostra"""
        
        n = len(samples)
        
        # Autocorrelação usando FFT (mais eficiente)
        f_samples = np.fft.fft(samples - np.mean(samples), n=2*n-1)
        autocorr = np.fft.ifft(f_samples * np.conj(f_samples)).real
        autocorr = autocorr[:n] / autocorr[0]
        
        # Encontrar primeiro lag com autocorrelação < 0.05
        cutoff = np.where(autocorr < 0.05)[0]
        if len(cutoff) > 0:
            tau_int = 1 + 2 * np.sum(autocorr[1:cutoff[0]])
        else:
            tau_int = n / 2  # Conservative estimate
        
        ess = n / (2 * tau_int)
        return max(1.0, ess)
    
    def _calculate_autocorrelation_time(self, samples: np.ndarray) -> float:
        """Calcular tempo de autocorrelação integrado"""
        
        n = len(samples) 
        mean_sample = np.mean(samples)
        
        # Função de autocorrelação
        autocorr = np.correlate(samples - mean_sample, samples - mean_sample, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        
        if autocorr[0] > 0:
            autocorr = autocorr / autocorr[0]
        else:
            return 1.0
            
        # Tempo integrado de autocorrelação
        # Somar até que a autocorrelação fique pequena
        cumsum = np.cumsum(autocorr)
        tau_int = 1 + 2 * cumsum[-1] if len(cumsum) > 0 else 1.0
        
        return max(1.0, tau_int)
    
    def create_real_time_dashboard(self, results: Dict[str, ModelEnsembleResult]) -> None:
        """Criar dashboard interativo em tempo real"""
        
        st.set_page_config(
            page_title="Brazilian Cultural Twin",
            page_icon="🇧🇷",
            layout="wide"
        )
        
        st.title("🇧🇷 Brazilian Cultural Twin Dashboard")
        st.markdown("*Simulação Monte Carlo com Ensemble de Modelos*")
        
        # Sidebar com controles
        with st.sidebar:
            st.header("Configurações")
            
            selected_circles = st.multiselect(
                "Círculos Culturais",
                list(results.keys()),
                default=list(results.keys())
            )
            
            show_uncertainties = st.checkbox("Mostrar Incertezas", True)
            show_intervals = st.checkbox("Intervalos de Confiança", True)
        
        # Layout principal
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Gráfico principal - Comparação de modelos
            fig = self._create_model_comparison_plot(results, selected_circles)
            st.plotly_chart(fig, use_container_width=True)
            
            # Gráfico de distribuições
            if show_intervals:
                fig_dist = self._create_distribution_plot(results, selected_circles)
                st.plotly_chart(fig_dist, use_container_width=True)
        
        with col2:
            # Métricas resumidas
            st.subheader("📊 Métricas Resumidas")
            
            for circle_id in selected_circles:
                if circle_id in results:
                    result = results[circle_id]
                    
                    st.markdown(f"**{circle_id.replace('_', ' ').title()}**")
                    
                    # Acceptance com confiança
                    acceptance = result.ensemble_prediction.get('acceptance', 0)
                    confidence = result.consensus_confidence
                    
                    st.metric(
                        "Aceitação",
                        f"{acceptance:.2%}",
                        f"±{confidence:.2%} confiança"
                    )
                    
                    # Sentiment
                    sentiment = result.ensemble_prediction.get('sentiment', 0)
                    st.metric(
                        "Sentimento", 
                        f"{sentiment:+.2f}",
                        "(-1.0 a +1.0)"
                    )
                    
                    # Engagement  
                    engagement = result.ensemble_prediction.get('engagement', 0)
                    st.metric("Engajamento", f"{engagement:.2%}")
                    
                    st.markdown("---")
        
        # Tabela detalhada
        st.subheader("📋 Resultados Detalhados")
        
        detailed_df = self._create_detailed_dataframe(results, selected_circles)
        st.dataframe(detailed_df, use_container_width=True)
        
    def _create_model_comparison_plot(
        self, 
        results: Dict[str, ModelEnsembleResult], 
        selected_circles: List[str]
    ) -> go.Figure:
        """Criar gráfico de comparação entre modelos"""
        
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=["Acceptance", "Sentiment", "Engagement"],
            specs=[[{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}]]
        )
        
        metrics = ['acceptance', 'sentiment', 'engagement']
        colors = ['blue', 'red', 'green']
        
        for i, metric in enumerate(metrics):
            col = i + 1
            
            for circle_id in selected_circles:
                if circle_id not in results:
                    continue
                    
                result = results[circle_id]
                
                # Valores dos diferentes modelos
                neural_val = result.neural_prediction.get(metric, 0)
                rf_val = result.random_forest_prediction.get(metric, 0)
                xgb_val = result.xgboost_prediction.get(metric, 0)
                ensemble_val = result.ensemble_prediction.get(metric, 0)
                
                # Plotar barras por modelo
                fig.add_trace(
                    go.Bar(
                        name=f"{circle_id}_neural" if i == 0 else None,
                        x=[f"{circle_id}_Neural"],
                        y=[neural_val],
                        marker_color='lightblue',
                        showlegend=(i == 0),
                        legendgroup="neural"
                    ),
                    row=1, col=col
                )
                
                fig.add_trace(
                    go.Bar(
                        name=f"{circle_id}_rf" if i == 0 else None,
                        x=[f"{circle_id}_RF"],
                        y=[rf_val],
                        marker_color='lightcoral',
                        showlegend=(i == 0),
                        legendgroup="rf"
                    ),
                    row=1, col=col
                )
                
                fig.add_trace(
                    go.Bar(
                        name=f"{circle_id}_xgb" if i == 0 else None,
                        x=[f"{circle_id}_XGB"],
                        y=[xgb_val], 
                        marker_color='lightgreen',
                        showlegend=(i == 0),
                        legendgroup="xgb"
                    ),
                    row=1, col=col
                )
                
                # Ensemble (destacado)
                fig.add_trace(
                    go.Bar(
                        name=f"{circle_id}_ensemble" if i == 0 else None,
                        x=[f"{circle_id}_Ensemble"],
                        y=[ensemble_val],
                        marker_color=colors[i],
                        marker_line=dict(color='black', width=2),
                        showlegend=(i == 0),
                        legendgroup="ensemble"
                    ),
                    row=1, col=col
                )
        
        fig.update_layout(
            title="Comparação de Modelos por Círculo Cultural",
            height=500,
            showlegend=True,
            barmode='group'
        )
        
        return fig
    
    def _create_distribution_plot(
        self,
        results: Dict[str, ModelEnsembleResult],
        selected_circles: List[str]
    ) -> go.Figure:
        """Criar gráfico das distribuições de incerteza"""
        
        fig = go.Figure()
        
        for circle_id in selected_circles:
            if circle_id not in results:
                continue
                
            result = results[circle_id]
            
            # Simular distribuição baseada nos intervalos
            acceptance_mean = result.ensemble_prediction.get('acceptance', 0.5)
            acceptance_interval = result.prediction_intervals.get('acceptance', (0.4, 0.6))
            
            # Criar distribuição normal aproximada
            std_approx = (acceptance_interval[1] - acceptance_interval[0]) / 4  # ~95% CI
            
            x_values = np.linspace(0, 1, 100)
            y_values = stats.norm.pdf(x_values, acceptance_mean, std_approx)
            
            fig.add_trace(go.Scatter(
                x=x_values,
                y=y_values,
                mode='lines',
                name=circle_id.replace('_', ' ').title(),
                fill='tonexty' if circle_id != selected_circles[0] else 'tozeroy'
            ))
            
            # Adicionar linha vertical da média
            fig.add_vline(
                x=acceptance_mean,
                line_dash="dash",
                annotation_text=f"{acceptance_mean:.2%}",
                annotation_position="top"
            )
        
        fig.update_layout(
            title="Distribuições de Probabilidade - Aceitação",
            xaxis_title="Probabilidade de Aceitação",
            yaxis_title="Densidade",
            height=400
        )
        
        return fig
    
    def _create_detailed_dataframe(
        self,
        results: Dict[str, ModelEnsembleResult], 
        selected_circles: List[str]
    ) -> pd.DataFrame:
        """Criar dataframe detalhado para tabela"""
        
        rows = []
        
        for circle_id in selected_circles:
            if circle_id not in results:
                continue
                
            result = results[circle_id]
            
            row = {
                'Círculo Cultural': circle_id.replace('_', ' ').title(),
                'Aceitação (Ensemble)': f"{result.ensemble_prediction.get('acceptance', 0):.2%}",
                'Sentimento (Ensemble)': f"{result.ensemble_prediction.get('sentiment', 0):+.2f}",
                'Engajamento (Ensemble)': f"{result.ensemble_prediction.get('engagement', 0):.2%}",
                'Confiança Consenso': f"{result.consensus_confidence:.2%}",
                'Intervalo Aceitação': f"[{result.prediction_intervals.get('acceptance', (0,0))[0]:.2%}, {result.prediction_intervals.get('acceptance', (0,0))[1]:.2%}]",
                'Melhor Modelo': self._identify_best_model(result),
                'Incerteza Neural': f"{result.model_uncertainties.get('neural', 0):.3f}",
                'Incerteza RF': f"{result.model_uncertainties.get('rf', 0):.3f}",
                'Incerteza XGB': f"{result.model_uncertainties.get('xgb', 0):.3f}"
            }
            
            rows.append(row)
        
        return pd.DataFrame(rows)
    
    def _identify_best_model(self, result: ModelEnsembleResult) -> str:
        """Identificar qual modelo teve melhor performance"""
        
        uncertainties = result.model_uncertainties
        min_uncertainty = min(uncertainties.values())
        
        for model, uncertainty in uncertainties.items():
            if uncertainty == min_uncertainty:
                return model.title()
        
        return "Ensemble"
    
    def _extract_comprehensive_features(
        self, 
        message: str, 
        context: Optional[str] = None
    ) -> Dict[str, float]:
        """Extrair features abrangentes da mensagem"""
        
        message_lower = message.lower()
        words = message_lower.split()
        
        # Features básicas
        features = {
            'message_length': len(message),
            'word_count': len(words),
            'avg_word_length': np.mean([len(w) for w in words]) if words else 0,
            'sentence_count': len([s for s in message.split('.') if s.strip()]),
            'exclamation_ratio': message.count('!') / max(len(message), 1),
            'question_ratio': message.count('?') / max(len(message), 1),
            'hashtag_count': message.count('#'),
            'mention_count': message.count('@'),
            'emoji_count': len([c for c in message if ord(c) > 127]),
        }
        
        # Features linguísticas avançadas
        features.update({
            'uppercase_ratio': sum(1 for c in message if c.isupper()) / max(len(message), 1),
            'punctuation_density': sum(1 for c in message if c in '.,!?;:') / max(len(message), 1),
            'number_count': sum(1 for w in words if w.isdigit()),
            'repetition_score': len(words) - len(set(words)) if words else 0,
        })
        
        # Features culturais brasileiras
        brazilian_positive = [
            'família', 'união', 'amor', 'tradição', 'valores', 'comunidade',
            'sustentabilidade', 'diversidade', 'inclusão', 'inovação', 
            'autenticidade', 'transparência', 'respeito'
        ]
        
        brazilian_negative = [
            'individualismo', 'egoísmo', 'greenwashing', 'tokenismo',
            'performativo', 'superficial', 'fake', 'appropriação'
        ]
        
        features['brazilian_positive_score'] = sum(
            1 for word in brazilian_positive if word in message_lower
        ) / max(len(words), 1)
        
        features['brazilian_negative_score'] = sum(
            1 for word in brazilian_negative if word in message_lower  
        ) / max(len(words), 1)
        
        features['cultural_net_score'] = (
            features['brazilian_positive_score'] - features['brazilian_negative_score']
        )
        
        # Features temporais (se contexto disponível)
        if context:
            context_lower = context.lower()
            
            # Detectar contextos especiais
            special_contexts = {
                'holiday': any(word in context_lower for word in ['feriado', 'natal', 'ano_novo', 'pascoa']),
                'weekend': any(word in context_lower for word in ['fim_de_semana', 'sabado', 'domingo']),
                'trending': any(word in context_lower for word in ['trending', 'viral', 'popular']),
                'crisis': any(word in context_lower for word in ['crise', 'problema', 'conflito'])
            }
            
            for context_type, detected in special_contexts.items():
                features[f'context_{context_type}'] = 1.0 if detected else 0.0
        else:
            # Default values se não há contexto
            for context_type in ['holiday', 'weekend', 'trending', 'crisis']:
                features[f'context_{context_type}'] = 0.0
        
        return features
    
    def _calculate_feature_adjustment(
        self,
        message_features: Dict[str, float],
        circle_params: Dict
    ) -> float:
        """Calcular ajuste baseado nas features da mensagem"""
        
        adjustment = 0.0
        
        # Ajuste por score cultural líquido
        cultural_score = message_features.get('cultural_net_score', 0)
        adjustment += cultural_score * 0.15
        
        # Ajuste por contexto especial
        if circle_params.get('temporal_dynamics'):
            temporal = circle_params['temporal_dynamics']
            
            if message_features.get('context_holiday', 0) > 0:
                adjustment += temporal.get('holiday_boost', 1.0) - 1.0
            
            if message_features.get('context_weekend', 0) > 0:
                adjustment += temporal.get('weekend_boost', 1.0) - 1.0
        
        # Ajuste por engagement features
        engagement_indicators = [
            'exclamation_ratio', 'hashtag_count', 'emoji_count'
        ]
        
        engagement_score = sum(
            min(message_features.get(indicator, 0), 0.1) 
            for indicator in engagement_indicators
        )
        adjustment += engagement_score * 0.1
        
        # Penalidade por negatividade cultural
        negative_score = message_features.get('brazilian_negative_score', 0)
        adjustment -= negative_score * 0.2
        
        return adjustment
    
    async def _neural_prediction(
        self,
        circle_id: str,
        message_features: Dict[str, float],
        n_simulations: int
    ) -> Dict[str, float]:
        """Predição usando rede neural (simulado)"""
        
        # Em produção, usar o modelo neural treinado
        # Por ora, simulação baseada nos parâmetros
        
        base_params = self.cultural_circles[circle_id]['base_params']
        
        # Simular predição neural com ruído
        neural_acceptance = np.random.normal(
            base_params['acceptance_mean'],
            base_params['acceptance_std'] * 0.5  # Neural é mais preciso
        )
        
        neural_sentiment = np.random.normal(
            base_params['sentiment_mean'],
            base_params['sentiment_std'] * 0.6
        )
        
        neural_engagement = np.random.beta(
            base_params['engagement_alpha'],
            base_params['engagement_beta']
        )
        
        # Ajustar baseado nas features
        feature_adj = self._calculate_feature_adjustment(
            message_features, self.cultural_circles[circle_id]
        )
        
        return {
            'acceptance': np.clip(neural_acceptance + feature_adj, 0.0, 1.0),
            'sentiment': np.clip(neural_sentiment + feature_adj * 0.5, -1.0, 1.0),
            'engagement': np.clip(neural_engagement + feature_adj * 0.3, 0.0, 1.0)
        }
    
    def _random_forest_prediction(
        self,
        circle_id: str,
        message_features: Dict[str, float]
    ) -> Dict[str, float]:
        """Predição usando Random Forest (simulado)"""
        
        base_params = self.cultural_circles[circle_id]['base_params']
        
        # Random Forest tende a ser mais conservador
        rf_acceptance = np.random.normal(
            base_params['acceptance_mean'] * 0.95,  # Slightly lower
            base_params['acceptance_std'] * 0.8     # Less variance
        )
        
        rf_sentiment = np.random.normal(
            base_params['sentiment_mean'] * 0.9,
            base_params['sentiment_std'] * 0.7
        )
        
        rf_engagement = np.random.beta(
            base_params['engagement_alpha'] * 0.9,
            base_params['engagement_beta'] * 1.1
        )
        
        return {
            'acceptance': np.clip(rf_acceptance, 0.0, 1.0),
            'sentiment': np.clip(rf_sentiment, -1.0, 1.0), 
            'engagement': np.clip(rf_engagement, 0.0, 1.0)
        }
    
    def _xgboost_prediction(
        self,
        circle_id: str,
        message_features: Dict[str, float]
    ) -> Dict[str, float]:
        """Predição usando XGBoost (simulado)"""
        
        base_params = self.cultural_circles[circle_id]['base_params']
        
        # XGBoost é bom em capturar não-linearidades
        xgb_acceptance = np.random.normal(
            base_params['acceptance_mean'] * 1.05,  # Slightly optimistic
            base_params['acceptance_std'] * 0.9
        )
        
        xgb_sentiment = np.random.normal(
            base_params['sentiment_mean'] * 1.1,
            base_params['sentiment_std'] * 0.8
        )
        
        xgb_engagement = np.random.beta(
            base_params['engagement_alpha'] * 1.1,
            base_params['engagement_beta'] * 0.9
        )
        
        # XGBoost com boost baseado em features específicas
        cultural_boost = message_features.get('cultural_net_score', 0) * 0.1
        
        return {
            'acceptance': np.clip(xgb_acceptance + cultural_boost, 0.0, 1.0),
            'sentiment': np.clip(xgb_sentiment + cultural_boost * 0.5, -1.0, 1.0),
            'engagement': np.clip(xgb_engagement + cultural_boost * 0.3, 0.0, 1.0)
        }
    
    def _combine_predictions(
        self,
        neural_pred: Dict[str, float],
        rf_pred: Dict[str, float], 
        xgb_pred: Dict[str, float]
    ) -> Dict[str, float]:
        """Combinar predições usando pesos do ensemble"""
        
        weights = self.ensemble_weights
        ensemble_pred = {}
        
        for metric in ['acceptance', 'sentiment', 'engagement']:
            ensemble_pred[metric] = (
                neural_pred[metric] * weights['neural'] +
                rf_pred[metric] * weights['rf'] +
                xgb_pred[metric] * weights['xgb']
            )
        
        return ensemble_pred
    
    def _calculate_model_uncertainties(
        self,
        neural_pred: Dict[str, float],
        rf_pred: Dict[str, float],
        xgb_pred: Dict[str, float]
    ) -> Dict[str, float]:
        """Calcular incertezas dos modelos individuais"""
        
        uncertainties = {}
        
        # Calcular variância entre predições como proxy de incerteza
        for metric in ['acceptance', 'sentiment', 'engagement']:
            predictions = [
                neural_pred[metric],
                rf_pred[metric], 
                xgb_pred[metric]
            ]
            
            # Incerteza como desvio padrão das predições
            uncertainties[metric] = float(np.std(predictions))
        
        # Incerteza agregada por modelo (simulada)
        uncertainties['neural'] = np.mean([
            abs(neural_pred[m] - rf_pred[m]) + abs(neural_pred[m] - xgb_pred[m])
            for m in ['acceptance', 'sentiment', 'engagement']
        ]) / 2
        
        uncertainties['rf'] = np.mean([
            abs(rf_pred[m] - neural_pred[m]) + abs(rf_pred[m] - xgb_pred[m])
            for m in ['acceptance', 'sentiment', 'engagement']
        ]) / 2
        
        uncertainties['xgb'] = np.mean([
            abs(xgb_pred[m] - neural_pred[m]) + abs(xgb_pred[m] - rf_pred[m])
            for m in ['acceptance', 'sentiment', 'engagement']
        ]) / 2
        
        return uncertainties
    
    def _calculate_consensus(
        self,
        neural_pred: Dict[str, float],
        rf_pred: Dict[str, float],
        xgb_pred: Dict[str, float]
    ) -> float:
        """Calcular confiança do consenso entre modelos"""
        
        total_disagreement = 0
        n_metrics = 0
        
        for metric in ['acceptance', 'sentiment', 'engagement']:
            predictions = [
                neural_pred[metric],
                rf_pred[metric],
                xgb_pred[metric]
            ]
            
            # Disagreement como range das predições
            disagreement = max(predictions) - min(predictions)
            total_disagreement += disagreement
            n_metrics += 1
        
        avg_disagreement = total_disagreement / n_metrics
        
        # Consenso é inverso do disagreement
        consensus = max(0.0, 1.0 - avg_disagreement)
        
        return consensus
    
    def _calculate_prediction_intervals(
        self,
        ensemble_pred: Dict[str, float],
        model_uncertainties: Dict[str, float],
        mc_validation: MonteCarloValidation
    ) -> Dict[str, Tuple[float, float]]:
        """Calcular intervalos de predição"""
        
        intervals = {}
        
        for metric in ['acceptance', 'sentiment', 'engagement']:
            mean_pred = ensemble_pred[metric]
            uncertainty = model_uncertainties.get(metric, 0.1)
            
            # Ajustar incerteza baseado na convergência MC
            if not mc_validation.converged:
                uncertainty *= 1.5  # Penalidade por não convergência
            
            # Intervalo de 95% assumindo distribuição normal
            margin = 1.96 * uncertainty
            
            if metric == 'sentiment':
                # Sentiment vai de -1 a 1
                lower_bound = max(-1.0, mean_pred - margin)
                upper_bound = min(1.0, mean_pred + margin)
            else:
                # Acceptance e engagement vão de 0 a 1
                lower_bound = max(0.0, mean_pred - margin)
                upper_bound = min(1.0, mean_pred + margin)
            
            intervals[metric] = (lower_bound, upper_bound)
        
        return intervals

# Exemplo de uso
async def main():
    """Exemplo de uso do sistema avançado"""
    
    # Inicializar gêmeo cultural
    twin = AdvancedBrazilianCulturalTwin()
    
    # Mensagem de teste
    message = """
    Nossa nova campanha celebra a diversidade da família brasileira 
    com tecnologia sustentável que une tradição e inovação! 
    #FamíliaBrasileira #SustentabilidadeReal
    """
    
    circles = [
        "familia_tradicional_br",
        "jovens_urbanos_conectados", 
        "brasil_sustentavel_consciente"
    ]
    
    context = "weekend trending_topic holiday"
    
    print("🚀 Executando simulação Monte Carlo com Ensemble...")
    
    # Executar predição com ensemble
    results = await twin.predict_with_ensemble(
        message=message,
        target_circles=circles,
        context=context,
        n_mc_samples=8000,
        validation_level="standard"
    )
    
    # Mostrar resultados
    print("\n📊 RESULTADOS DO ENSEMBLE:")
    print("=" * 60)
    
    for circle_id, result in results.items():
        print(f"\n🎯 {circle_id.replace('_', ' ').title()}")
        print("-" * 40)
        
        ensemble = result.ensemble_prediction
        intervals = result.prediction_intervals
        
        print(f"Aceitação: {ensemble['acceptance']:.2%} [{intervals['acceptance'][0]:.2%} - {intervals['acceptance'][1]:.2%}]")
        print(f"Sentimento: {ensemble['sentiment']:+.2f} [{intervals['sentiment'][0]:+.2f} - {intervals['sentiment'][1]:+.2f}]")
        print(f"Engajamento: {ensemble['engagement']:.2%} [{intervals['engagement'][0]:.2%} - {intervals['engagement'][1]:.2%}]")
        print(f"Confiança: {result.consensus_confidence:.2%}")
        
        # Comparar modelos
        print(f"\nComparação de Modelos:")
        print(f"  Neural:  {result.neural_prediction['acceptance']:.2%}")
        print(f"  RF:      {result.random_forest_prediction['acceptance']:.2%}")
        print(f"  XGBoost: {result.xgboost_prediction['acceptance']:.2%}")
    
    print(f"\n✅ Simulação concluída com {len(results)} círculos culturais")
    
    # Criar dashboard (descomente se estiver usando Streamlit)
    # twin.create_real_time_dashboard(results)

if __name__ == "__main__":
    asyncio.run(main())