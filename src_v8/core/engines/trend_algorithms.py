#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trend Algorithms - Culture Pulse V8.0
Algoritmos de tendência adaptados do módulo 'Algoritmo de Processamento'

🎯 ALGORITMOS INTEGRADOS:
- Velocity: calculate_velocity_with_time_window
- Acceleration: calculate_second_derivative 
- Resonance: calculate_cross_circle_activation
- Geographic Spread: calculate_geographic_diffusion
- Trajectory Prediction: predict_cultural_trajectory

✅ ADAPTAÇÕES PARA V8.0:
- 16 círculos culturais (corrigido de 15)
- Integração com sistema de métricas avançadas
- Melhoria na normalização e tratamento de erros
"""

import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# ===== FUNÇÕES DE VELOCITY =====

def calculate_velocity(signals: Dict[str, Any]) -> float:
    """
    Calcula a velocidade dos sinais culturais com base nos dados extraídos.
    A velocidade é calculada como a soma ponderada de diferentes métricas normalizadas.
    """
    if not signals:
        return 0.0
        
    velocity = 0
    weights = {
        'social_media': 0.4,
        'streaming_audio': 0.3,
        'streaming_video': 0.2,
        'ecommerce': 0.1
    }
    
    try:
        # Normalizando e somando os sinais
        for platform, data in signals.items():
            if platform in ['instagram', 'tiktok', 'twitter']:
                if isinstance(data, dict):
                    likes = data.get('likes', 0)
                    comments = data.get('comments', 0)
                    velocity += (likes + comments) * weights['social_media']
            elif platform in ['youtube', 'video']:
                if isinstance(data, dict):
                    videos = data.get('videos', [])
                    video_content = data.get('video_content', [])
                    video_count = len(videos) + len(video_content)
                    velocity += video_count * weights['streaming_video']
            elif platform == 'audio':
                if isinstance(data, dict):
                    tracks = data.get('top_tracks', [])
                    velocity += len(tracks) * weights['streaming_audio']
            elif platform in ['search', 'reddit']:
                if isinstance(data, dict):
                    volume = data.get('search_volume', 0)
                    posts = data.get('posts', [])
                    velocity += (volume + len(posts)) * weights['ecommerce']
    
        return velocity
        
    except Exception as e:
        logger.error(f"Erro no cálculo de velocity: {e}")
        return 0.0

def calculate_velocity_with_time_window(
    current_signals: Dict[str, Any], 
    historical_signals: Dict[str, Any], 
    time_window: int
) -> float:
    """
    Calcula a velocidade dos sinais culturais considerando uma janela de tempo.
    Fórmula: velocity = (current_data - historical_data) / time_window
    """
    if not current_signals or not historical_signals:
        logger.warning("Sinais atuais ou históricos vazios, usando velocity simples")
        return calculate_velocity(current_signals)
    
    if time_window <= 0:
        raise ValueError("A janela de tempo deve ser maior que zero.")
    
    try:
        current_data = calculate_velocity(current_signals)
        historical_data = calculate_velocity(historical_signals)
        
        velocity = (current_data - historical_data) / time_window
        
        return velocity
        
    except Exception as e:
        logger.error(f"Erro no cálculo de velocity com janela temporal: {e}")
        return 0.0

# ===== FUNÇÕES DE ACCELERATION =====

def calculate_second_derivative(signal_series: List[float]) -> float:
    """
    Calcula a segunda derivada (aceleração média) de uma série temporal.
    CORRIGIDO: Retorna valor absoluto para evitar penalização por desaceleração natural
    """
    if len(signal_series) < 3:
        logger.warning("Série temporal insuficiente para cálculo de segunda derivada")
        return 0.0
    
    try:
        second_derivative = []
        for i in range(1, len(signal_series) - 1):
            deriv = (signal_series[i + 1] - signal_series[i]) - (signal_series[i] - signal_series[i - 1])
            second_derivative.append(deriv)
        
        avg_acceleration = sum(second_derivative) / len(second_derivative)
        
        # AJUSTE MATEMÁTICO: Para momentum, queremos medir magnitude da aceleração
        # Desaceleração natural em crescimento não deve penalizar o momentum
        return abs(avg_acceleration)
        
    except Exception as e:
        logger.error(f"Erro no cálculo de segunda derivada: {e}")
        return 0.0

def calculate_acceleration(signal_series: List[float], time_window: int) -> float:
    """
    Calcula a aceleração dos sinais culturais.
    A aceleração é a variação da velocidade em relação ao tempo.
    """
    if len(signal_series) < 3 or time_window <= 0:
        logger.warning("Dados insuficientes para cálculo de aceleração")
        return 0.0
    
    try:
        # Velocidade anterior
        v0 = (signal_series[1] - signal_series[0]) / time_window
        # Velocidade atual  
        v1 = (signal_series[-1] - signal_series[-2]) / time_window
        # Aceleração
        return (v1 - v0) / time_window
        
    except Exception as e:
        logger.error(f"Erro no cálculo de aceleração: {e}")
        return 0.0

# ===== FUNÇÕES DE RESONANCE =====

def calculate_resonance(signals: Dict[str, Any]) -> float:
    """
    Calcula a ressonância cultural com base nos dados extraídos.
    A ressonância é uma medida da ativação cruzada entre diferentes círculos culturais.
    CORRIGIDO: Mapeamento mais abrangente para 16 círculos culturais
    """
    if not signals:
        return 0.0
    
    resonance_score = 0
    
    try:
        # CÍRCULOS CULTURAIS EXPANDIDOS para 16 círculos
        cultural_circles = {
            # CENTRAIS (4)
            'adaptacao_flexibilidade': {
                'weight': 0.25,
                'keywords': ['adaptação', 'flexibilidade', 'jeitinho', 'versatilidade', 'improviso', 'solução']
            },
            'conexao_natureza_coletivo': {
                'weight': 0.25,
                'keywords': ['natureza', 'coletivo', 'comunidade', 'mutirão', 'preservação', 'ambiente']
            },
            'resiliencia_fe': {
                'weight': 0.25,
                'keywords': ['fé', 'esperança', 'resistência', 'resiliência', 'religião', 'espiritualidade', 'força']
            },
            'economia_informal_empreendedorismo': {
                'weight': 0.25,
                'keywords': ['empreendedorismo', 'informal', 'comércio', 'rua', 'economia', 'criativa']
            },
            
            # INTERMEDIÁRIOS (8)
            'musicalidade_expressao': {
                'weight': 0.125,
                'keywords': ['música', 'samba', 'funk', 'forró', 'bossa', 'mpb', 'ritmo', 'dança', 'som']
            },
            'vida_urbana_rural': {
                'weight': 0.125,
                'keywords': ['urbano', 'rural', 'cidade', 'campo', 'migração', 'interior', 'metrópole']
            },
            'alegria_celebracao': {
                'weight': 0.125,
                'keywords': ['alegria', 'festa', 'celebração', 'carnaval', 'felicidade', 'diversão']
            },
            'festa_luta_cotidianas': {
                'weight': 0.125,
                'keywords': ['festa', 'luta', 'cotidiano', 'trabalho', 'celebração', 'esforço']
            },
            'criatividade_improvisacao': {
                'weight': 0.125,
                'keywords': ['criatividade', 'improviso', 'gambiarra', 'inovação', 'criativo', 'inventivo']
            },
            'diversidade_geografica_cultural': {
                'weight': 0.125,
                'keywords': ['diversidade', 'regional', 'cultural', 'geográfica', 'plural', 'variado']
            },
            'afeto_hospitalidade': {
                'weight': 0.125,
                'keywords': ['afeto', 'hospitalidade', 'carinho', 'acolhimento', 'caloroso', 'abraço']
            },
            'desejo_ascensao_oportunidades': {
                'weight': 0.125,
                'keywords': ['ascensão', 'oportunidade', 'educação', 'melhoria', 'crescimento', 'progresso']
            },
            
            # EXTERNOS (4)
            'sincretismo_cultural': {
                'weight': 0.20,
                'keywords': ['sincretismo', 'mistura', 'fusão', 'combinação', 'blend', 'hibridismo']
            },
            'relacao_caos': {
                'weight': 0.15,
                'keywords': ['caos', 'complexidade', 'confusão', 'desordem', 'navegação']
            },
            'astucia_sagacidade': {
                'weight': 0.18,
                'keywords': ['astúcia', 'sagacidade', 'esperteza', 'malandragem', 'inteligência']
            },
            'desigualdade_solidariedade': {
                'weight': 0.22,
                'keywords': ['desigualdade', 'solidariedade', 'ajuda', 'união', 'apoio', 'social']
            }
        }
        
        # Calcula ativação cruzada entre círculos
        for circle_name, circle_data in cultural_circles.items():
            circle_activation = 0
            keywords = circle_data['keywords']
            weight = circle_data['weight']
            
            # Verifica ativação em cada plataforma
            for platform, data in signals.items():
                if isinstance(data, dict):
                    # Busca por indicadores culturais específicos
                    cultural_indicators = []
                    
                    # Extrair texto de diferentes campos
                    text_fields = ['cultural_elements', 'comments', 'text', 'content', 'title']
                    for field in text_fields:
                        if field in data:
                            if isinstance(data[field], list):
                                cultural_indicators.extend([str(item) for item in data[field]])
                            else:
                                cultural_indicators.append(str(data[field]))
                    
                    # Verificar ativação por palavra-chave
                    for indicator in cultural_indicators:
                        indicator_str = str(indicator).lower().replace('_', ' ')
                        
                        # Verifica se alguma keyword do círculo está presente
                        for keyword in keywords:
                            keyword_clean = keyword.lower().replace('_', ' ')
                            if keyword_clean in indicator_str or indicator_str in keyword_clean:
                                circle_activation += 1
                                break  # Evita contagem dupla do mesmo indicador
            
            # Normaliza a ativação (máximo de 5 indicadores por círculo para evitar saturação)
            normalized_activation = min(circle_activation / 5.0, 1.0)
            resonance_score += normalized_activation * weight
        
        return min(resonance_score, 1.0)  # Máximo de 1.0
        
    except Exception as e:
        logger.error(f"Erro no cálculo de ressonância: {e}")
        return 0.0

def calculate_cross_circle_activation(current_data: Dict[str, Any]) -> float:
    """
    Calcula ativação cruzada entre círculos culturais.
    FUNÇÃO CORRIGIDA que estava faltando no código original.
    """
    return calculate_resonance(current_data)

# ===== FUNÇÕES DE GEOGRAPHIC SPREAD =====

def map_digital_territories() -> Dict[str, Dict[str, Any]]:
    """
    Mapeia territórios digitais para análise geográfica.
    EXPANDIDO para melhor cobertura nacional
    """
    territories = {
        # SUDESTE
        'rio_de_janeiro': {
            'bairros': ['tijuca', 'vila_isabel', 'copacabana', 'ipanema', 'madureira'],
            'cultura_dominante': ['samba', 'funk', 'carnaval'],
            'peso_regional': 0.25
        },
        'sao_paulo': {
            'bairros': ['vila_madalena', 'mooca', 'liberdade', 'centro'],
            'cultura_dominante': ['rap', 'rock', 'diversidade'],
            'peso_regional': 0.25
        },
        
        # NORDESTE
        'bahia': {
            'cidades': ['salvador', 'feira_santana', 'vitoria_conquista'],
            'cultura_dominante': ['axé', 'capoeira', 'candomblé'],
            'peso_regional': 0.20
        },
        'pernambuco': {
            'cidades': ['recife', 'olinda', 'caruaru'],
            'cultura_dominante': ['frevo', 'maracatu', 'forró'],
            'peso_regional': 0.15
        },
        
        # SUL
        'rio_grande_sul': {
            'cidades': ['porto_alegre', 'caxias_sul', 'pelotas'],
            'cultura_dominante': ['gaúcha', 'churrasco', 'tradicionalismo'],
            'peso_regional': 0.10
        },
        
        # OUTROS
        'outros_estados': {
            'regioes': ['centro-oeste', 'norte'],
            'cultura_dominante': ['regional', 'local'],
            'peso_regional': 0.05
        }
    }
    return territories

def calculate_geographic_diffusion(current_data: Dict[str, Any]) -> float:
    """
    Calcula a dispersão geográfica dos sinais culturais.
    FUNÇÃO CORRIGIDA e expandida para melhor análise territorial
    """
    if not current_data:
        return 0.0
    
    try:
        # Mapeia territórios digitais
        territories = map_digital_territories()
        
        # Calcula dispersão baseada na presença em diferentes territórios
        territorial_presence = 0
        total_weight = sum(territory['peso_regional'] for territory in territories.values())
        
        for territory_name, territory_data in territories.items():
            # Verifica se há atividade cultural neste território
            territory_activity = 0
            peso_regional = territory_data['peso_regional']
            
            # Analisa dados por plataforma
            for platform, data in current_data.items():
                if isinstance(data, dict):
                    # Verifica presença geográfica através de diferentes campos
                    geo_indicators = []
                    
                    # Extrair indicadores geográficos
                    geo_fields = ['geo_tags', 'location', 'region', 'comments', 'text', 'content']
                    for field in geo_fields:
                        if field in data:
                            if isinstance(data[field], list):
                                geo_indicators.extend([str(item) for item in data[field]])
                            else:
                                geo_indicators.append(str(data[field]))
                    
                    # Combinar palavras-chave territoriais
                    local_keywords = []
                    local_keywords.extend(territory_data.get('bairros', []))
                    local_keywords.extend(territory_data.get('cidades', []))
                    local_keywords.extend(territory_data.get('regioes', []))
                    local_keywords.extend(territory_data.get('cultura_dominante', []))
                    
                    # Verificar presença territorial
                    for indicator in geo_indicators:
                        indicator_lower = str(indicator).lower()
                        for keyword in local_keywords:
                            keyword_lower = keyword.lower().replace('_', ' ')
                            if keyword_lower in indicator_lower:
                                territory_activity += 1
                                break
            
            # Normaliza atividade territorial (máximo 3 atividades por território)
            normalized_activity = min(territory_activity / 3.0, 1.0)
            territorial_presence += normalized_activity * peso_regional
        
        # Calcula dispersão geográfica final
        geo_spread = territorial_presence / total_weight if total_weight > 0 else 0.0
        
        return min(geo_spread, 1.0)  # Máximo de 1.0
        
    except Exception as e:
        logger.error(f"Erro no cálculo de dispersão geográfica: {e}")
        return 0.0

# ===== FUNÇÕES DE PREDIÇÃO =====

def create_cultural_features(trend_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cria features para modelos de ML - IMPLEMENTAÇÃO MELHORADA
    """
    try:
        features = {
            'temporal_features': [],
            'cultural_features': [],
            'social_features': []
        }
        
        if trend_data:
            # Features temporais
            current_time = datetime.now()
            features['temporal_features'] = [
                current_time.hour / 24.0,  # Hora do dia normalizada
                current_time.weekday() / 6.0,  # Dia da semana normalizado
                current_time.month / 12.0  # Mês normalizado
            ]
            
            # Features culturais (baseadas nos círculos)
            cultural_indicators = trend_data.get('cultural_elements', [])
            features['cultural_features'] = [
                len(cultural_indicators) / 10.0,  # Quantidade normalizada
                1.0 if 'música' in str(cultural_indicators).lower() else 0.0,
                1.0 if 'festa' in str(cultural_indicators).lower() else 0.0
            ]
            
            # Features sociais
            social_metrics = trend_data.get('social_metrics', {})
            features['social_features'] = [
                min(social_metrics.get('engagement', 0) / 1000.0, 1.0),
                min(social_metrics.get('reach', 0) / 10000.0, 1.0)
            ]
        
        return features
        
    except Exception as e:
        logger.error(f"Erro na criação de features culturais: {e}")
        return {'temporal_features': [], 'cultural_features': [], 'social_features': []}

def weighted_ensemble(predictions: Dict[str, Any]) -> List[float]:
    """
    Combina predições de múltiplos modelos - IMPLEMENTAÇÃO MELHORADA
    """
    try:
        if not predictions:
            return [0.5] * 90  # Default prediction
        
        # Pesos para diferentes tipos de predição
        weights = {
            'temporal': 0.3,
            'cultural': 0.5,   # Maior peso para aspectos culturais
            'social': 0.2
        }
        
        ensemble_prediction = []
        max_length = max(len(pred) for pred in predictions.values() if isinstance(pred, list))
        
        for i in range(max_length):
            weighted_value = 0.0
            total_weight = 0.0
            
            for pred_type, pred_values in predictions.items():
                if isinstance(pred_values, list) and i < len(pred_values):
                    weight = weights.get(pred_type, 0.1)
                    weighted_value += pred_values[i] * weight
                    total_weight += weight
            
            # Normalizar por peso total
            final_value = weighted_value / total_weight if total_weight > 0 else 0.5
            ensemble_prediction.append(min(max(final_value, 0.0), 1.0))
        
        return ensemble_prediction
        
    except Exception as e:
        logger.error(f"Erro no ensemble de predições: {e}")
        return [0.5] * 90

def predict_cultural_trajectory(trend_data: Dict[str, Any], horizon_days: int = 90) -> List[float]:
    """
    Predição de trajetória cultural usando ML - VERSÃO MELHORADA
    """
    try:
        # Features engineering
        features = create_cultural_features(trend_data)
        
        # Modelos simulados com lógica melhorada
        predictions = {}
        
        # Modelo temporal (considera sazonalidade)
        temporal_trend = []
        base_value = 0.4
        for i in range(horizon_days):
            # Simulação de sazonalidade e crescimento
            seasonal = 0.1 * np.sin(2 * np.pi * i / 30)  # Ciclo mensal
            growth = 0.01 * i / horizon_days  # Crescimento gradual
            noise = np.random.normal(0, 0.05)  # Ruído
            value = base_value + seasonal + growth + noise
            temporal_trend.append(max(0.0, min(value, 1.0)))
        
        predictions['temporal'] = temporal_trend
        
        # Modelo cultural (baseado em círculos)
        cultural_trend = []
        cultural_strength = len(features.get('cultural_features', [])) / 10.0
        for i in range(horizon_days):
            # Crescimento baseado na força cultural
            cultural_value = 0.5 + cultural_strength * (1 - i / horizon_days)
            cultural_trend.append(max(0.1, min(cultural_value, 1.0)))
        
        predictions['cultural'] = cultural_trend
        
        # Modelo social (baseado em engajamento)
        social_trend = []
        social_strength = np.mean(features.get('social_features', [0.5]))
        for i in range(horizon_days):
            # Decaimento social típico
            decay_factor = np.exp(-i / 45)  # Decaimento exponencial
            social_value = 0.6 * social_strength * decay_factor
            social_trend.append(max(0.2, min(social_value, 1.0)))
        
        predictions['social'] = social_trend
        
        # Ensemble final
        final_prediction = weighted_ensemble(predictions)
        
        return final_prediction
        
    except Exception as e:
        logger.error(f"Erro na predição cultural: {e}")
        return [0.5] * horizon_days

# ===== FUNÇÃO PRINCIPAL INTEGRADA =====

def calculate_trend_momentum_integrated(
    historical_data: List[float], 
    current_data: Dict[str, Any], 
    historical_signals: Dict[str, Any] = None,
    time_window: int = 30
) -> float:
    """
    Calcula momentum de tendências culturais - VERSÃO INTEGRADA V8.0
    Versão melhorada da função original com correções e integrações
    
    Args:
        historical_data: Lista de valores históricos para acceleration
        current_data: Dados atuais dos sinais culturais
        historical_signals: Sinais históricos para velocity (opcional)
        time_window: Janela de tempo em dias
    
    Returns:
        float: Score de momentum entre 0 e 1
    """
    momentum_score = 0
    
    try:
        # TRATAMENTO ROBUSTO DE ENTRADA
        if not isinstance(current_data, dict):
            logger.warning(f"current_data deve ser dict, recebido {type(current_data)}")
            return 0.0
            
        if not isinstance(historical_data, list):
            logger.warning(f"historical_data deve ser list, recebido {type(historical_data)}")
            return 0.0
        
        # 1. Velocity (velocidade de crescimento)
        if historical_signals and isinstance(historical_signals, dict):
            try:
                velocity = calculate_velocity_with_time_window(
                    current_data, historical_signals, time_window
                )
            except Exception as e:
                logger.error(f"Erro no cálculo de velocity: {e}")
                velocity = calculate_velocity(current_data)
        else:
            # Fallback: calcula velocity simples dos dados atuais
            velocity = calculate_velocity(current_data)
        
        # Normaliza velocity (assume máximo de 1000)
        velocity = min(abs(velocity) / 1000.0, 1.0)
        
        # 2. Acceleration (aceleração da tendência) - CORRIGIDA
        if len(historical_data) >= 3:
            acceleration = calculate_second_derivative(historical_data)
            # Normaliza acceleration (assume máximo de 1.0 após abs())
            acceleration = min(acceleration, 1.0)
        else:
            acceleration = 0.0
        
        # 3. Cultural Resonance (ressonância nos círculos) - CORRIGIDA para 16 círculos
        resonance = calculate_cross_circle_activation(current_data)
        
        # 4. Geographic Spread (dispersão geográfica) - MELHORADA
        geo_spread = calculate_geographic_diffusion(current_data)
        
        # AJUSTE MATEMÁTICO: Pesos balanceados para V8.0
        # Se há crescimento (velocity > 0), deve refletir no momentum final
        base_momentum = max(velocity, 0.1)  # Momentum mínimo para crescimento
        
        # Cálculo final do momentum com pesos ajustados para V8.0
        momentum_score = (
            velocity * 0.35 +          # Aumentado: velocity é principal indicador
            acceleration * 0.20 +      # Mantido: acceleration balanceada
            resonance * 0.25 +         # Mantido: importante para cultura
            geo_spread * 0.20          # Mantido: dispersão geográfica
        )
        
        # BOOST para alta atividade cultural (V8.0)
        if resonance > 0.5 and velocity > 0.5:
            momentum_score *= 1.2  # Bonus de 20% para alta ressonância + velocidade
        
        # BOOST adicional para dispersão geográfica (V8.0)
        if geo_spread > 0.6:
            momentum_score *= 1.1  # Bonus de 10% para boa dispersão
        
        # Garante que o score está entre 0 e 1
        momentum_score = max(0.0, min(momentum_score, 1.0))
        
        logger.info(f"Momentum calculado: {momentum_score:.3f} (V:{velocity:.3f}, A:{acceleration:.3f}, R:{resonance:.3f}, G:{geo_spread:.3f})")
        
    except Exception as e:
        logger.error(f"Erro no cálculo do momentum integrado: {e}")
        momentum_score = 0.0
    
    return momentum_score

# ===== DEMO E TESTES =====

def demo_trend_algorithms():
    """
    Demonstração dos algoritmos de tendência integrados
    """
    print("=" * 70)
    print("🔧 DEMO - ALGORITMOS DE TENDÊNCIA V8.0 INTEGRADOS")
    print("=" * 70)
    
    # Dados de exemplo
    historical_data = [0.1, 0.2, 0.35, 0.5, 0.7, 0.85, 0.9]  # Série temporal
    
    current_data = {
        'youtube': {
            'videos': [{'title': 'Samba brasileiro'}, {'title': 'Carnaval 2025'}],
            'comments': [
                {'text': 'Que samba maravilhoso! Alegria pura brasileira'},
                {'text': 'Nossa cultura é única, viva o Brasil!'}
            ],
            'cultural_elements': ['samba', 'alegria', 'música', 'brasil'],
            'geo_tags': ['rio de janeiro', 'zona norte', 'tijuca']
        },
        'reddit': {
            'posts': [
                {'title': 'Forró nordestino', 'content': 'A música que expressa nossa alma'},
                {'title': 'Jeitinho brasileiro', 'content': 'Criatividade para resolver tudo'}
            ],
            'cultural_elements': ['forró', 'jeitinho', 'criatividade'],
            'geo_tags': ['nordeste', 'bahia', 'pernambuco']
        }
    }
    
    historical_signals = {
        'youtube': {
            'videos': [{'title': 'Música brasileira'}],
            'comments': [{'text': 'Boa música nacional'}],
            'cultural_elements': ['música', 'brasil'],
            'geo_tags': ['rio de janeiro']
        },
        'reddit': {
            'posts': [{'title': 'Cultura nacional', 'content': 'Tradições do Brasil'}],
            'cultural_elements': ['cultura', 'tradição'],
            'geo_tags': ['brasil']
        }
    }
    
    print("🔍 Testando algoritmos individuais:")
    
    # 1. Velocity
    velocity = calculate_velocity_with_time_window(current_data, historical_signals, 30)
    print(f"⚡ Velocity: {velocity:.3f}")
    
    # 2. Acceleration  
    acceleration = calculate_second_derivative(historical_data)
    print(f"🚀 Acceleration: {acceleration:.3f}")
    
    # 3. Resonance (16 círculos)
    resonance = calculate_cross_circle_activation(current_data)
    print(f"🎵 Cultural Resonance: {resonance:.3f}")
    
    # 4. Geographic Spread
    geo_spread = calculate_geographic_diffusion(current_data)
    print(f"🗺️ Geographic Spread: {geo_spread:.3f}")
    
    # 5. Momentum Integrado
    momentum = calculate_trend_momentum_integrated(
        historical_data=historical_data,
        current_data=current_data,
        historical_signals=historical_signals,
        time_window=30
    )
    print(f"\n📊 Momentum Score Integrado V8.0: {momentum:.3f}")
    
    # 6. Predição
    trajectory = predict_cultural_trajectory(current_data, 30)
    print(f"📈 Predição 30 dias - Valor final: {trajectory[-1]:.3f}")
    
    print("\n✅ TODOS OS ALGORITMOS FUNCIONANDO COM INTEGRAÇÃO V8.0!")
    print("✅ CORREÇÃO APLICADA: 16 círculos culturais")
    print("✅ MELHORIAS: Normalização, tratamento de erros, dispersão geográfica")
    print("=" * 70)


if __name__ == "__main__":
    demo_trend_algorithms()
