#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⏰ Temporal Embedder
Adiciona dimensões temporais aos embeddings para capturar sazonalidade cultural

Features:
- Embeddings cíclicos para sazonalidade (Carnaval, Copa, Natal)
- Componentes anuais, mensais, semanais
- Eventos culturais brasileiros fixos
- Concatenação com BERTimbau (768d + 8d temporal = 776d)

Autor: Culture Pulse V9.1
Data: Fevereiro 2026
"""

import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class TemporalEmbedder:
    """
    Adiciona embeddings posicionais temporais para capturar sazonalidade cultural
    
    Inspiração: Transformers usam positional embeddings para sequências
    Aqui: usamos temporal embeddings para ciclos culturais anuais
    """
    
    def __init__(self):
        # Eventos culturais brasileiros (dia do ano)
        self.cultural_events = {
            'ano_novo': 1,
            'carnaval': 60,  # ~final de fevereiro (varia)
            'pascoa': 110,  # ~abril (varia)
            'dia_trabalho': 121,  # 1º de maio
            'dia_maes': 135,  # ~2º domingo maio
            'festas_juninas': 165,  # ~junho
            'dia_pais': 228,  # ~2º domingo agosto
            'independencia': 254,  # 7 de setembro
            'dia_criancas': 285,  # 12 de outubro
            'halloween': 304,  # 31 de outubro (crescente no BR)
            'black_friday': 330,  # ~final novembro
            'natal': 359,  # 25 de dezembro
            'reveillon': 365,  # 31 de dezembro
        }
        
        # Eventos esportivos recorrentes
        self.sporting_events = {
            'copa_mundo': None,  # A cada 4 anos (2026, 2030)
            'olimpiadas': None,  # A cada 4 anos (2024, 2028)
            'carnaval_sp': 60,
            'carnaval_rio': 60,
            'rock_in_rio': 265,  # ~setembro (bienal)
            'lollapalooza': 90,  # ~março/abril
        }
        
        logger.info("✅ TemporalEmbedder initialized with Brazilian cultural events")
    
    def encode_with_time(
        self, 
        text_embedding: np.ndarray,
        timestamp: datetime,
        include_events: bool = True
    ) -> np.ndarray:
        """
        Concatena embedding de texto com temporal embedding
        
        Args:
            text_embedding: BERTimbau embedding (768d)
            timestamp: Data/hora do sinal
            include_events: Incluir proximidade de eventos culturais
        
        Returns:
            Embedding combinado (768d + 8d temporal = 776d)
        """
        temporal_emb = self._compute_temporal_embedding(timestamp, include_events)
        
        # Concatenar: [768d texto] + [8d temporal] = 776d
        combined = np.concatenate([text_embedding, temporal_emb])
        
        return combined
    
    def _compute_temporal_embedding(
        self, 
        timestamp: datetime,
        include_events: bool = True
    ) -> np.ndarray:
        """
        Calcula embedding temporal (8 dimensões)
        
        Componentes:
        1-2: Sazonalidade anual (sin, cos)
        3-4: Sazonalidade mensal (sin, cos)
        5-6: Sazonalidade semanal (sin, cos)
        7: Proximidade de evento cultural (0-1)
        8: Intensidade do período (0-1)
        """
        day_of_year = timestamp.timetuple().tm_yday
        day_of_week = timestamp.weekday()
        day_of_month = timestamp.day
        
        # Componente 1-2: Ciclo anual (365 dias)
        annual_sin = np.sin(2 * np.pi * day_of_year / 365)
        annual_cos = np.cos(2 * np.pi * day_of_year / 365)
        
        # Componente 3-4: Ciclo mensal (30 dias aproximado)
        monthly_sin = np.sin(2 * np.pi * day_of_month / 30)
        monthly_cos = np.cos(2 * np.pi * day_of_month / 30)
        
        # Componente 5-6: Ciclo semanal (7 dias)
        weekly_sin = np.sin(2 * np.pi * day_of_week / 7)
        weekly_cos = np.cos(2 * np.pi * day_of_week / 7)
        
        # Componente 7: Proximidade de evento cultural
        event_proximity = 0.0
        if include_events:
            event_proximity = self._calculate_event_proximity(day_of_year)
        
        # Componente 8: Intensidade do período (alta temporada cultural)
        # Exemplo: Carnaval + Festas Juninas + Natal = high intensity
        period_intensity = self._calculate_period_intensity(day_of_year)
        
        temporal_emb = np.array([
            annual_sin,
            annual_cos,
            monthly_sin,
            monthly_cos,
            weekly_sin,
            weekly_cos,
            event_proximity,
            period_intensity
        ])
        
        return temporal_emb
    
    def _calculate_event_proximity(self, day_of_year: int) -> float:
        """
        Calcula proximidade do evento cultural mais próximo (0-1)
        
        1.0 = no dia do evento
        0.5 = 1 semana do evento
        0.0 = >30 dias do evento
        """
        min_distance = 365  # Máximo
        
        for event_name, event_day in self.cultural_events.items():
            # Distância circular (ano é cíclico)
            dist = min(
                abs(day_of_year - event_day),
                365 - abs(day_of_year - event_day)
            )
            
            min_distance = min(min_distance, dist)
        
        # Converter distância para proximidade (0-1)
        # 0 dias = 1.0, 30 dias = 0.0
        if min_distance <= 30:
            proximity = 1.0 - (min_distance / 30)
        else:
            proximity = 0.0
        
        return proximity
    
    def _calculate_period_intensity(self, day_of_year: int) -> float:
        """
        Calcula intensidade cultural do período (0-1)
        
        Períodos de alta intensidade:
        - Carnaval (fev/mar): 0.9
        - Festas Juninas (jun): 0.8
        - Natal/Ano Novo (dez): 1.0
        - Copa do Mundo (se ano de copa): 1.0
        
        Outros períodos: baseline 0.3
        """
        # Baseline
        intensity = 0.3
        
        # Carnaval (dias 45-75)
        if 45 <= day_of_year <= 75:
            intensity = 0.9
        
        # Festas Juninas (dias 150-180)
        elif 150 <= day_of_year <= 180:
            intensity = 0.8
        
        # Natal/Ano Novo (dias 345-365 e 1-10)
        elif day_of_year >= 345 or day_of_year <= 10:
            intensity = 1.0
        
        # Black Friday (dias 320-335)
        elif 320 <= day_of_year <= 335:
            intensity = 0.7
        
        # Dia das Mães/Pais (picos comerciais)
        elif 130 <= day_of_year <= 140 or 220 <= day_of_year <= 235:
            intensity = 0.6
        
        return intensity
    
    def get_cultural_context(self, timestamp: datetime) -> Dict:
        """
        Retorna contexto cultural completo da data
        
        Útil para narrativas automáticas:
        "Este sinal surge em contexto de Carnaval, período de alta intensidade cultural"
        """
        day_of_year = timestamp.timetuple().tm_yday
        
        # Encontrar evento mais próximo
        closest_event = None
        min_distance = 365
        
        for event_name, event_day in self.cultural_events.items():
            dist = min(
                abs(day_of_year - event_day),
                365 - abs(day_of_year - event_day)
            )
            
            if dist < min_distance:
                min_distance = dist
                closest_event = event_name
        
        # Calcular embeddings
        temporal_emb = self._compute_temporal_embedding(timestamp, include_events=True)
        
        return {
            'timestamp': timestamp.isoformat(),
            'day_of_year': day_of_year,
            'day_of_week': timestamp.strftime('%A'),
            'month': timestamp.strftime('%B'),
            'closest_event': closest_event,
            'days_to_event': min_distance,
            'event_proximity': temporal_emb[6],
            'period_intensity': temporal_emb[7],
            'season': self._get_season(day_of_year),
            'is_holiday_season': temporal_emb[7] > 0.7,
            'is_commercial_peak': self._is_commercial_peak(day_of_year),
        }
    
    def _get_season(self, day_of_year: int) -> str:
        """Retorna estação do ano (Hemisfério Sul)"""
        if 355 <= day_of_year or day_of_year <= 79:
            return 'Verão'
        elif 80 <= day_of_year <= 171:
            return 'Outono'
        elif 172 <= day_of_year <= 265:
            return 'Inverno'
        else:
            return 'Primavera'
    
    def _is_commercial_peak(self, day_of_year: int) -> bool:
        """Verifica se é período de pico comercial"""
        commercial_periods = [
            (130, 140),  # Dia das Mães
            (220, 235),  # Dia dos Pais
            (280, 290),  # Dia das Crianças
            (320, 335),  # Black Friday
            (345, 365),  # Natal
        ]
        
        for start, end in commercial_periods:
            if start <= day_of_year <= end:
                return True
        
        return False
    
    def batch_encode(
        self,
        embeddings_with_timestamps: List[Tuple[np.ndarray, datetime]]
    ) -> np.ndarray:
        """
        Processa múltiplos embeddings em batch
        
        Args:
            embeddings_with_timestamps: Lista de (embedding, timestamp)
        
        Returns:
            Array (N, 776) com embeddings temporais
        """
        results = []
        
        for text_emb, timestamp in embeddings_with_timestamps:
            temporal_emb = self.encode_with_time(text_emb, timestamp)
            results.append(temporal_emb)
        
        return np.array(results)


# Exemplo de uso
if __name__ == "__main__":
    embedder = TemporalEmbedder()
    
    # Teste 1: Embedding durante Carnaval
    fake_bertimbau_emb = np.random.randn(768)  # Simula BERTimbau
    carnaval_date = datetime(2026, 2, 15)  # Carnaval 2026
    
    temporal_emb = embedder.encode_with_time(fake_bertimbau_emb, carnaval_date)
    print(f"Embedding shape: {temporal_emb.shape}")  # (776,)
    print(f"Temporal component: {temporal_emb[-8:]}")
    
    # Teste 2: Contexto cultural
    context = embedder.get_cultural_context(carnaval_date)
    print("\nContexto Cultural (Carnaval):")
    for key, value in context.items():
        print(f"  {key}: {value}")
    
    # Teste 3: Comparar Carnaval vs Natal
    natal_date = datetime(2026, 12, 25)
    context_natal = embedder.get_cultural_context(natal_date)
    
    print("\nContexto Cultural (Natal):")
    for key, value in context_natal.items():
        print(f"  {key}: {value}")
    
    # Teste 4: Verificar se detecta eventos
    print("\n" + "="*50)
    print("TESTE: Proximidade de eventos ao longo do ano")
    print("="*50)
    
    for month in range(1, 13):
        date = datetime(2026, month, 15)
        context = embedder.get_cultural_context(date)
        print(f"{date.strftime('%B')}: Evento mais próximo = {context['closest_event']} "
              f"(distância: {context['days_to_event']} dias, "
              f"intensidade: {context['period_intensity']:.2f})")
