"""
Sistema de Análise Temporal Cultural
Baseado na pesquisa de Oxford (2024) sobre análise temporal cultural
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import pandas as pd
from scipy.optimize import curve_fit
import logging

logger = logging.getLogger(__name__)

@dataclass
class TemporalPattern:
    """Padrão temporal identificado"""
    pattern_type: str  # 'seasonal', 'cyclical', 'trend', 'event'
    period: int  # em dias
    strength: float
    phase: float
    confidence: float
    
@dataclass
class CulturalDecay:
    """Informações sobre decaimento cultural"""
    half_life: float  # em dias
    decay_rate: float
    residual_strength: float
    prediction_curve: List[Tuple[datetime, float]]
    
@dataclass
class SeasonalityAnalysis:
    """Análise de sazonalidade cultural"""
    seasonal_patterns: List[Dict[str, any]]
    major_events: List[Dict[str, any]]
    regional_variations: Dict[str, List[Dict[str, any]]]

class TemporalCulturalAnalyzer:
    """Analisador de padrões temporais culturais"""
    
    def __init__(self):
        """Inicializar analisador temporal"""
        self.seasonal_events = self._initialize_seasonal_events()
        self.regional_patterns = self._initialize_regional_patterns()
        
    def _initialize_seasonal_events(self) -> Dict[str, Dict[str, any]]:
        """Inicializar eventos sazonais brasileiros"""
        return {
            'carnaval': {
                'month': 2,
                'duration': 5,
                'strength': 0.95,
                'regional_impact': {
                    'rio_de_janeiro': 1.0,
                    'salvador': 0.95,
                    'recife': 0.9,
                    'sao_paulo': 0.8
                }
            },
            'sao_joao': {
                'month': 6,
                'duration': 30,
                'strength': 0.85,
                'regional_impact': {
                    'nordeste': 0.95,
                    'norte': 0.7,
                    'sudeste': 0.5,
                    'sul': 0.3
                }
            },
            'reveillon': {
                'month': 12,
                'duration': 2,
                'strength': 0.9,
                'regional_impact': {
                    'rio_de_janeiro': 1.0,
                    'nordeste': 0.9,
                    'sudeste': 0.85,
                    'sul': 0.8
                }
            }
        }
        
    def _initialize_regional_patterns(self) -> Dict[str, List[Dict[str, any]]]:
        """Inicializar padrões regionais"""
        return {
            'norte': [
                {
                    'event': 'festival_parintins',
                    'month': 6,
                    'duration': 3,
                    'strength': 0.9
                },
                {
                    'event': 'cirio_nazare',
                    'month': 10,
                    'duration': 15,
                    'strength': 0.95
                }
            ],
            'nordeste': [
                {
                    'event': 'sao_joao',
                    'month': 6,
                    'duration': 30,
                    'strength': 0.95
                },
                {
                    'event': 'carnaval',
                    'month': 2,
                    'duration': 5,
                    'strength': 0.9
                }
            ],
            'sudeste': [
                {
                    'event': 'carnaval_rio',
                    'month': 2,
                    'duration': 5,
                    'strength': 1.0
                }
            ],
            'sul': [
                {
                    'event': 'oktoberfest',
                    'month': 10,
                    'duration': 18,
                    'strength': 0.85
                }
            ]
        }
        
    def calculate_cultural_decay(self, 
                               initial_strength: float,
                               timepoints: List[datetime],
                               measurements: List[float]) -> CulturalDecay:
        """Calcular decaimento cultural"""
        try:
            # Converter tempos para dias desde o início
            t0 = min(timepoints)
            days = [(t - t0).days for t in timepoints]
            
            # Função de decaimento exponencial
            def decay_func(t, half_life, residual):
                return initial_strength * (
                    (1 - residual) * np.exp(-np.log(2) * t / half_life) + 
                    residual
                )
            
            # Ajustar curva
            popt, _ = curve_fit(
                decay_func, days, measurements,
                p0=[30, 0.2],  # estimativas iniciais
                bounds=([1, 0], [365, 1])  # limites
            )
            
            half_life, residual = popt
            decay_rate = np.log(2) / half_life
            
            # Gerar curva de predição
            future_days = list(range(max(days) + 90))  # +90 dias
            prediction = [
                (t0 + timedelta(days=d),
                 float(decay_func(d, half_life, residual)))
                for d in future_days
            ]
            
            return CulturalDecay(
                half_life=float(half_life),
                decay_rate=float(decay_rate),
                residual_strength=float(residual),
                prediction_curve=prediction
            )
            
        except Exception as e:
            logger.error(f"Erro no cálculo de decaimento: {e}")
            return None
            
    def analyze_seasonality(self, 
                          timeseries: pd.Series,
                          region: str = None) -> SeasonalityAnalysis:
        """Analisar sazonalidade cultural"""
        try:
            # Detectar padrões sazonais
            seasonal_patterns = []
            
            # Analisar eventos principais
            for event, info in self.seasonal_events.items():
                # Verificar se há picos nos períodos esperados
                event_strength = self._analyze_event_strength(
                    timeseries, info['month'], info['duration']
                )
                
                if event_strength > 0.3:  # threshold mínimo
                    regional_strength = 1.0
                    if region and region in info['regional_impact']:
                        regional_strength = info['regional_impact'][region]
                        
                    seasonal_patterns.append({
                        'event': event,
                        'month': info['month'],
                        'duration': info['duration'],
                        'detected_strength': event_strength,
                        'regional_modifier': regional_strength,
                        'final_strength': event_strength * regional_strength
                    })
            
            # Identificar eventos principais
            major_events = [
                pattern for pattern in seasonal_patterns
                if pattern['final_strength'] > 0.7
            ]
            
            # Analisar variações regionais
            regional_variations = {}
            if region:
                regional_patterns = self.regional_patterns.get(region, [])
                for pattern in regional_patterns:
                    strength = self._analyze_event_strength(
                        timeseries,
                        pattern['month'],
                        pattern['duration']
                    )
                    if strength > 0.3:
                        if region not in regional_variations:
                            regional_variations[region] = []
                        regional_variations[region].append({
                            'event': pattern['event'],
                            'detected_strength': strength,
                            'expected_strength': pattern['strength'],
                            'alignment': strength / pattern['strength']
                        })
            
            return SeasonalityAnalysis(
                seasonal_patterns=seasonal_patterns,
                major_events=major_events,
                regional_variations=regional_variations
            )
            
        except Exception as e:
            logger.error(f"Erro na análise de sazonalidade: {e}")
            return None
            
    def _analyze_event_strength(self,
                              timeseries: pd.Series,
                              event_month: int,
                              duration: int) -> float:
        """Analisar força de um evento sazonal"""
        try:
            # Filtrar dados do período do evento
            event_data = timeseries[
                (timeseries.index.month == event_month) &
                (timeseries.index.day <= duration)
            ]
            
            if len(event_data) == 0:
                return 0.0
                
            # Calcular média do período
            event_mean = event_data.mean()
            
            # Calcular média geral
            overall_mean = timeseries.mean()
            
            # Calcular força relativa
            relative_strength = (event_mean - overall_mean) / overall_mean
            
            return max(0, min(1, relative_strength))
            
        except Exception as e:
            logger.error(f"Erro na análise de evento: {e}")
            return 0.0
            
    def detect_temporal_patterns(self,
                               timeseries: pd.Series) -> List[TemporalPattern]:
        """Detectar padrões temporais na série"""
        patterns = []
        
        try:
            # Análise de periodicidade
            if len(timeseries) >= 14:  # mínimo 2 semanas
                # Padrão semanal
                weekly = self._analyze_weekly_pattern(timeseries)
                if weekly:
                    patterns.append(weekly)
                    
                # Padrão mensal
                if len(timeseries) >= 60:  # mínimo 2 meses
                    monthly = self._analyze_monthly_pattern(timeseries)
                    if monthly:
                        patterns.append(monthly)
                        
            # Detectar tendência
            trend = self._analyze_trend_pattern(timeseries)
            if trend:
                patterns.append(trend)
                
            return patterns
            
        except Exception as e:
            logger.error(f"Erro na detecção de padrões: {e}")
            return []
            
    def _analyze_weekly_pattern(self,
                              timeseries: pd.Series) -> Optional[TemporalPattern]:
        """Analisar padrão semanal"""
        try:
            # Agrupar por dia da semana
            daily_means = timeseries.groupby(
                timeseries.index.dayofweek).mean()
            
            # Calcular variação
            variation = daily_means.std() / daily_means.mean()
            
            if variation > 0.1:  # threshold mínimo de variação
                return TemporalPattern(
                    pattern_type='cyclical',
                    period=7,
                    strength=min(1.0, variation * 2),
                    phase=daily_means.argmax(),
                    confidence=0.8
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Erro na análise semanal: {e}")
            return None
            
    def _analyze_monthly_pattern(self,
                               timeseries: pd.Series) -> Optional[TemporalPattern]:
        """Analisar padrão mensal"""
        try:
            # Agrupar por dia do mês
            monthly_means = timeseries.groupby(
                timeseries.index.day).mean()
            
            # Calcular variação
            variation = monthly_means.std() / monthly_means.mean()
            
            if variation > 0.15:  # threshold mínimo de variação
                return TemporalPattern(
                    pattern_type='cyclical',
                    period=30,
                    strength=min(1.0, variation * 2),
                    phase=monthly_means.argmax(),
                    confidence=0.7
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Erro na análise mensal: {e}")
            return None
            
    def _analyze_trend_pattern(self,
                             timeseries: pd.Series) -> Optional[TemporalPattern]:
        """Analisar tendência"""
        try:
            # Calcular coeficiente de correlação com tempo
            time_num = np.arange(len(timeseries))
            correlation = np.corrcoef(time_num, timeseries.values)[0, 1]
            
            if abs(correlation) > 0.3:  # threshold mínimo
                return TemporalPattern(
                    pattern_type='trend',
                    period=len(timeseries),
                    strength=abs(correlation),
                    phase=1 if correlation > 0 else -1,
                    confidence=min(1.0, abs(correlation) * 1.5)
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Erro na análise de tendência: {e}")
            return None