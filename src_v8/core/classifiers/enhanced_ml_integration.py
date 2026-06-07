"""
🧠 ENHANCED ML INTEGRATION V8.2
==========================================
Integração avançada do ML Pipeline com o sistema Culture Pulse

Melhorias implementadas:
1. Intervalos de confiança mais precisos
2. Integração da 'Imaginação de Futuros' com ML
3. Refinamento de pesquisa com confidence boosting
4. Filtros de termos relacionados com ML
5. Agent autônomo melhorado

Author: Culture Pulse V8.2 System
"""

import asyncio
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
import json

# Imports do sistema existente
from autonomous_agent.ml_foundation.back.ml_pipeline import (
    get_ml_pipeline, BrazilianCulturalModel, CulturalFeatureExtractor
)
from core.futures_imagination_engine import FuturesImaginationEngine
from core.intelligence.research_refiner import ResearchRefiner

logger = logging.getLogger(__name__)

@dataclass
class ConfidenceInterval:
    """Intervalo de confiança melhorado"""
    lower_bound: float
    upper_bound: float
    confidence_level: float  # 0.95 = 95%
    method: str  # 'bootstrap', 'analytical', 'bayesian'
    sample_size: int
    uncertainty_factors: Dict[str, float]

@dataclass 
class MLEnhancedResult:
    """Resultado com ML aprimorado"""
    prediction: str
    confidence_interval: ConfidenceInterval
    feature_importance: Dict[str, float]
    cultural_context: Dict[str, Any]
    related_terms: List[str]
    temporal_factors: Dict[str, float]

class EnhancedMLIntegrator:
    """
    🎯 Integrador ML Avançado V8.2
    
    Combina múltiplos modelos ML para:
    - Intervalos de confiança mais precisos
    - Predições culturais contextualizadas
    - Refinamento inteligente de termos
    - Análise temporal integrada
    """
    
    def __init__(self):
        self.ml_pipeline = get_ml_pipeline()
        self.futures_engine = FuturesImaginationEngine()
        self.research_refiner = ResearchRefiner()
        
        # Modelos especializados
        self.confidence_models = {}
        self.term_similarity_model = None
        self.temporal_model = None
        
        self.logger = logger
        self._initialize_specialized_models()
    
    def _initialize_specialized_models(self):
        """Inicializa modelos especializados"""
        try:
            # Modelo de confiança baseado em múltiplas features
            self.confidence_models['cultural'] = self._create_confidence_model('cultural')
            self.confidence_models['temporal'] = self._create_confidence_model('temporal')
            self.confidence_models['regional'] = self._create_confidence_model('regional')
            
            self.logger.info("✅ Modelos especializados inicializados")
        except Exception as e:
            self.logger.warning(f"⚠️ Modelos especializados não disponíveis: {e}")
    
    def _create_confidence_model(self, model_type: str) -> BrazilianCulturalModel:
        """Cria modelo específico para cálculo de confiança"""
        model = BrazilianCulturalModel(f"confidence_{model_type}")
        
        # Dados sintéticos para treinamento (substituir por dados reais)
        training_data = self._generate_confidence_training_data(model_type)
        
        texts = [item['text'] for item in training_data]
        labels = [item['confidence_level'] for item in training_data]
        
        try:
            model.train(texts, labels)
            return model
        except Exception as e:
            self.logger.warning(f"Falha ao treinar modelo {model_type}: {e}")
            return None
    
    def _generate_confidence_training_data(self, model_type: str) -> List[Dict[str, Any]]:
        """Gera dados de treinamento para modelos de confiança"""
        base_data = {
            'cultural': [
                {'text': 'Festival de música sertaneja em Goiás', 'confidence_level': 'high'},
                {'text': 'Evento cultural no centro de São Paulo', 'confidence_level': 'medium'},
                {'text': 'Atividade genérica sem contexto', 'confidence_level': 'low'},
            ],
            'temporal': [
                {'text': 'Carnaval 2024 no Rio de Janeiro', 'confidence_level': 'high'},
                {'text': 'Festa junina em junho', 'confidence_level': 'high'},
                {'text': 'Evento em data aleatória', 'confidence_level': 'low'},
            ],
            'regional': [
                {'text': 'Forró no Nordeste brasileiro', 'confidence_level': 'high'},
                {'text': 'Churrasco no Sul do país', 'confidence_level': 'high'},
                {'text': 'Atividade sem localização', 'confidence_level': 'low'},
            ]
        }
        
        return base_data.get(model_type, base_data['cultural'])
    
    async def calculate_enhanced_confidence_interval(
        self,
        prediction: str,
        text_input: str,
        cultural_context: Dict[str, Any],
        method: str = 'bootstrap'
    ) -> ConfidenceInterval:
        """
        🎯 Calcula intervalo de confiança melhorado
        
        Combina múltiplas fontes de incerteza:
        - Variabilidade do modelo
        - Contexto cultural
        - Fatores temporais
        - Qualidade dos dados
        """
        
        # Coletar probabilidades de múltiplos modelos
        model_probabilities = []
        uncertainty_factors = {}
        
        # 1. Modelo principal
        if self.ml_pipeline.active_model:
            try:
                main_probs = self.ml_pipeline.predict_with_confidence([text_input])
                if main_probs:
                    model_probabilities.append(main_probs[0]['confidence'])
                    uncertainty_factors['model_variance'] = 1.0 - main_probs[0]['confidence']
            except Exception as e:
                self.logger.warning(f"Modelo principal falhou: {e}")
        
        # 2. Modelos de confiança especializados
        for model_type, confidence_model in self.confidence_models.items():
            if confidence_model:
                try:
                    conf_pred = confidence_model.predict([text_input])
                    conf_prob = confidence_model.predict_proba([text_input])
                    if conf_prob.size > 0:
                        model_probabilities.append(np.max(conf_prob))
                        uncertainty_factors[f'{model_type}_uncertainty'] = 1.0 - np.max(conf_prob)
                except Exception as e:
                    self.logger.warning(f"Modelo {model_type} falhou: {e}")
        
        # 3. Fatores contextuais
        context_confidence = self._assess_cultural_context_confidence(cultural_context)
        uncertainty_factors['cultural_context'] = 1.0 - context_confidence
        
        # 4. Fatores temporais
        temporal_confidence = self._assess_temporal_confidence(cultural_context)
        uncertainty_factors['temporal_factors'] = 1.0 - temporal_confidence
        
        # 5. Qualidade dos dados
        data_quality = self._assess_data_quality(text_input)
        uncertainty_factors['data_quality'] = 1.0 - data_quality
        
        # Calcular intervalo baseado no método escolhido
        if method == 'bootstrap':
            return self._bootstrap_confidence_interval(
                model_probabilities, uncertainty_factors
            )
        elif method == 'bayesian':
            return self._bayesian_confidence_interval(
                model_probabilities, uncertainty_factors
            )
        else:  # analytical
            return self._analytical_confidence_interval(
                model_probabilities, uncertainty_factors
            )
    
    def _bootstrap_confidence_interval(
        self,
        probabilities: List[float],
        uncertainty_factors: Dict[str, float]
    ) -> ConfidenceInterval:
        """Intervalo de confiança via Bootstrap"""
        
        if not probabilities:
            return ConfidenceInterval(0.0, 1.0, 0.95, 'bootstrap', 0, uncertainty_factors)
        
        # Bootstrap sampling
        n_bootstrap = 1000
        bootstrap_samples = []
        
        for _ in range(n_bootstrap):
            # Resample with replacement
            sample = np.random.choice(probabilities, size=len(probabilities), replace=True)
            
            # Adicionar ruído baseado nos fatores de incerteza
            noise_level = np.mean(list(uncertainty_factors.values()))
            noise = np.random.normal(0, noise_level * 0.1, len(sample))
            
            adjusted_sample = np.clip(sample + noise, 0, 1)
            bootstrap_samples.append(np.mean(adjusted_sample))
        
        # Calcular percentis
        lower_bound = np.percentile(bootstrap_samples, 2.5)  # 95% CI
        upper_bound = np.percentile(bootstrap_samples, 97.5)
        
        return ConfidenceInterval(
            lower_bound=float(lower_bound),
            upper_bound=float(upper_bound),
            confidence_level=0.95,
            method='bootstrap',
            sample_size=len(probabilities),
            uncertainty_factors=uncertainty_factors
        )
    
    def _bayesian_confidence_interval(
        self,
        probabilities: List[float],
        uncertainty_factors: Dict[str, float]
    ) -> ConfidenceInterval:
        """Intervalo de confiança Bayesiano"""
        
        if not probabilities:
            return ConfidenceInterval(0.0, 1.0, 0.95, 'bayesian', 0, uncertainty_factors)
        
        # Prior Beta(1,1) = Uniform
        alpha_prior, beta_prior = 1, 1
        
        # Update com observações
        successes = sum(probabilities)
        trials = len(probabilities)
        
        alpha_posterior = alpha_prior + successes
        beta_posterior = beta_prior + (trials - successes)
        
        # Credible interval
        from scipy.stats import beta
        lower_bound = beta.ppf(0.025, alpha_posterior, beta_posterior)
        upper_bound = beta.ppf(0.975, alpha_posterior, beta_posterior)
        
        return ConfidenceInterval(
            lower_bound=float(lower_bound),
            upper_bound=float(upper_bound),
            confidence_level=0.95,
            method='bayesian',
            sample_size=len(probabilities),
            uncertainty_factors=uncertainty_factors
        )
    
    def _analytical_confidence_interval(
        self,
        probabilities: List[float],
        uncertainty_factors: Dict[str, float]
    ) -> ConfidenceInterval:
        """Intervalo de confiança analítico"""
        
        if not probabilities:
            return ConfidenceInterval(0.0, 1.0, 0.95, 'analytical', 0, uncertainty_factors)
        
        mean_prob = np.mean(probabilities)
        std_prob = np.std(probabilities) if len(probabilities) > 1 else 0.1
        
        # Ajustar desvio padrão com fatores de incerteza
        uncertainty_adjustment = 1 + np.mean(list(uncertainty_factors.values()))
        adjusted_std = std_prob * uncertainty_adjustment
        
        # Intervalo normal (95%)
        z_score = 1.96
        margin_error = z_score * adjusted_std / np.sqrt(len(probabilities))
        
        lower_bound = max(0, mean_prob - margin_error)
        upper_bound = min(1, mean_prob + margin_error)
        
        return ConfidenceInterval(
            lower_bound=float(lower_bound),
            upper_bound=float(upper_bound),
            confidence_level=0.95,
            method='analytical',
            sample_size=len(probabilities),
            uncertainty_factors=uncertainty_factors
        )
    
    def _assess_cultural_context_confidence(self, context: Dict[str, Any]) -> float:
        """Avalia confiança baseada no contexto cultural"""
        confidence = 0.5  # Base
        
        # Fatores positivos
        if context.get('region') in ['Nordeste', 'Sudeste', 'Sul', 'Norte', 'Centro-Oeste']:
            confidence += 0.2
        
        if context.get('cultural_circles'):
            confidence += min(0.2, len(context['cultural_circles']) * 0.05)
        
        if context.get('demographic_data'):
            confidence += 0.15
        
        # Fatores negativos
        if context.get('data_quality', 'medium') == 'low':
            confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def _assess_temporal_confidence(self, context: Dict[str, Any]) -> float:
        """Avalia confiança baseada em fatores temporais"""
        confidence = 0.6  # Base
        
        # Sazonalidade conhecida
        current_month = datetime.now().month
        if context.get('seasonal_relevance'):
            if current_month in context.get('peak_months', []):
                confidence += 0.3
            elif current_month in context.get('low_months', []):
                confidence -= 0.2
        
        # Tendências temporais
        if context.get('trending', False):
            confidence += 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def _assess_data_quality(self, text: str) -> float:
        """Avalia qualidade dos dados de entrada"""
        if not text or len(text) < 10:
            return 0.2
        
        quality = 0.5
        
        # Tamanho adequado
        if 20 <= len(text) <= 500:
            quality += 0.2
        
        # Presença de contexto cultural
        cultural_keywords = ['brasil', 'cultura', 'região', 'festa', 'música', 'tradição']
        if any(keyword in text.lower() for keyword in cultural_keywords):
            quality += 0.3
        
        return min(1.0, quality)
    
    async def enhance_futures_imagination_with_ml(
        self,
        cultural_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        🔮 Integra ML com Imaginação de Futuros
        
        Melhora as predições usando:
        - Modelos ML para validação de sinais
        - Confidence scoring para cenários
        - Feature importance para insights
        """
        
        # Análise base com Futures Engine
        futures_result = await self.futures_engine.imagine_futures(
            cultural_data, 'ml_enhanced', 'Brasil'
        )
        
        # Enriquecer com ML
        enhanced_signals = []
        for signal in futures_result.get('cultural_signals', []):
            ml_enhancement = await self._enhance_signal_with_ml(signal)
            enhanced_signals.append(ml_enhancement)
        
        # Validar cenários com ML
        enhanced_scenarios = []
        for scenario in futures_result.get('future_scenarios', []):
            ml_validation = await self._validate_scenario_with_ml(scenario)
            enhanced_scenarios.append(ml_validation)
        
        return {
            'original_futures': futures_result,
            'ml_enhanced_signals': enhanced_signals,
            'ml_validated_scenarios': enhanced_scenarios,
            'confidence_improvement': self._calculate_confidence_improvement(
                futures_result, enhanced_signals, enhanced_scenarios
            )
        }
    
    async def _enhance_signal_with_ml(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Enriquece sinal cultural com ML"""
        
        signal_text = f"{signal.get('description', '')} {signal.get('context', '')}"
        
        # Predição ML
        if self.ml_pipeline.active_model:
            try:
                ml_prediction = self.ml_pipeline.predict_with_confidence([signal_text])
                if ml_prediction:
                    signal['ml_validation'] = {
                        'predicted_category': ml_prediction[0]['prediction'],
                        'confidence': ml_prediction[0]['confidence'],
                        'ml_score': ml_prediction[0]['confidence']
                    }
            except Exception as e:
                self.logger.warning(f"ML enhancement falhou para sinal: {e}")
        
        # Análise de features
        feature_extractor = CulturalFeatureExtractor()
        features = feature_extractor.transform([signal_text])
        
        if features.size > 0:
            signal['cultural_features'] = {
                'regional_score': float(features[0][0]) if features.shape[1] > 0 else 0,
                'cultural_density': float(features[0][5]) if features.shape[1] > 5 else 0,
                'emotion_level': float(features[0][7]) if features.shape[1] > 7 else 0
            }
        
        return signal
    
    async def _validate_scenario_with_ml(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Valida cenário futuro com ML"""
        
        scenario_text = f"{scenario.get('name', '')} {scenario.get('description', '')}"
        
        # Calcular probabilidade do cenário
        probability_factors = []
        
        # Fator 1: Consistência histórica
        if 'historical_precedent' in scenario:
            probability_factors.append(scenario['historical_precedent'])
        
        # Fator 2: Tendências atuais
        if 'current_momentum' in scenario:
            probability_factors.append(scenario['current_momentum'])
        
        # Fator 3: Validação ML
        if self.ml_pipeline.active_model:
            try:
                ml_prediction = self.ml_pipeline.predict_with_confidence([scenario_text])
                if ml_prediction:
                    probability_factors.append(ml_prediction[0]['confidence'])
            except Exception:
                pass
        
        # Calcular probabilidade ajustada
        if probability_factors:
            scenario['ml_adjusted_probability'] = np.mean(probability_factors)
            scenario['probability_confidence'] = 1.0 - np.std(probability_factors)
        else:
            scenario['ml_adjusted_probability'] = scenario.get('probability', 0.5)
            scenario['probability_confidence'] = 0.5
        
        return scenario
    
    def _calculate_confidence_improvement(
        self,
        original: Dict[str, Any],
        enhanced_signals: List[Dict[str, Any]],
        enhanced_scenarios: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calcula melhoria na confiança com ML"""
        
        original_confidence = original.get('confidence', 0.5)
        
        # Confiança dos sinais
        signal_confidences = [
            s.get('ml_validation', {}).get('confidence', 0.5)
            for s in enhanced_signals
        ]
        avg_signal_confidence = np.mean(signal_confidences) if signal_confidences else 0.5
        
        # Confiança dos cenários
        scenario_confidences = [
            s.get('probability_confidence', 0.5)
            for s in enhanced_scenarios
        ]
        avg_scenario_confidence = np.mean(scenario_confidences) if scenario_confidences else 0.5
        
        # Confiança combinada
        combined_confidence = (original_confidence + avg_signal_confidence + avg_scenario_confidence) / 3
        
        return {
            'original_confidence': original_confidence,
            'signals_confidence': avg_signal_confidence,
            'scenarios_confidence': avg_scenario_confidence,
            'combined_confidence': combined_confidence,
            'improvement_ratio': combined_confidence / max(original_confidence, 0.1)
        }
    
    async def enhance_research_refinement(
        self,
        original_terms: List[str],
        business_context: str,
        user_objective: str
    ) -> Dict[str, Any]:
        """
        🔍 Melhora refinamento de pesquisa com ML
        
        Combina:
        - Research Refiner existente
        - ML para similaridade semântica
        - Filtros inteligentes de termos
        - Objective-aware optimization
        """
        
        # Análise do contexto com Research Refiner
        context = self.research_refiner.analyze_business_context(business_context)
        
        # Refinamento base
        base_refined = self.research_refiner.refine_search_terms(original_terms, context)
        
        # Enhancement com ML
        ml_enhanced_terms = await self._ml_enhance_terms(
            base_refined, business_context, user_objective
        )
        
        # Filtro inteligente baseado no objetivo
        objective_filtered = await self._filter_terms_by_objective(
            ml_enhanced_terms, user_objective, context
        )
        
        # Score de relevância para cada termo
        term_scores = await self._score_term_relevance(
            objective_filtered, business_context, user_objective
        )
        
        return {
            'original_terms': original_terms,
            'base_refined': base_refined,
            'ml_enhanced': ml_enhanced_terms,
            'objective_filtered': objective_filtered,
            'term_scores': term_scores,
            'final_recommendation': self._get_top_terms(term_scores, 15),
            'enhancement_metrics': {
                'expansion_ratio': len(objective_filtered) / max(len(original_terms), 1),
                'relevance_score': np.mean(list(term_scores.values())) if term_scores else 0,
                'objective_alignment': await self._calculate_objective_alignment(
                    objective_filtered, user_objective
                )
            }
        }
    
    async def _ml_enhance_terms(
        self,
        terms: List[str],
        context: str,
        objective: str
    ) -> List[str]:
        """Enhance terms usando ML"""
        
        enhanced_terms = terms.copy()
        
        # Use ML pipeline para sugerir termos similares
        if self.ml_pipeline.active_model:
            try:
                # Criar contexto expandido
                full_context = f"Contexto: {context}. Objetivo: {objective}. Termos: {', '.join(terms)}"
                
                # Predição para cada termo
                for term in terms:
                    term_context = f"{term} no contexto de {context}"
                    predictions = self.ml_pipeline.predict_with_confidence([term_context])
                    
                    if predictions and predictions[0]['confidence'] > 0.6:
                        # Adicionar termos relacionados baseados na predição
                        predicted_category = predictions[0]['prediction']
                        related_terms = self._get_category_related_terms(predicted_category)
                        enhanced_terms.extend(related_terms[:2])  # Top 2
                        
            except Exception as e:
                self.logger.warning(f"ML enhancement falhou: {e}")
        
        return list(set(enhanced_terms))
    
    def _get_category_related_terms(self, category: str) -> List[str]:
        """Obtém termos relacionados por categoria"""
        category_terms = {
            'nordeste': ['forró', 'axé', 'sertão', 'caatinga'],
            'sudeste': ['samba', 'funk', 'rock', 'rap'],
            'sul': ['gaúcho', 'churrasco', 'tradição'],
            'carnaval': ['folia', 'blocos', 'trio elétrico'],
            'familia': ['união', 'tradição', 'valores'],
            'futebol': ['paixão', 'torcida', 'esporte']
        }
        
        return category_terms.get(category.lower(), [])
    
    async def _filter_terms_by_objective(
        self,
        terms: List[str],
        objective: str,
        context: Any
    ) -> List[str]:
        """Filtra termos baseado no objetivo específico"""
        
        objective_lower = objective.lower()
        
        # Mapear objetivos para tipos de termos relevantes
        objective_filters = {
            'awareness': ['viral', 'trending', 'popular', 'conhecido'],
            'engagement': ['interativo', 'comunidade', 'participação'],
            'conversion': ['compra', 'decisão', 'escolha'],
            'branding': ['identidade', 'valores', 'personalidade'],
            'market_research': ['comportamento', 'preferência', 'hábito']
        }
        
        filtered_terms = terms.copy()
        
        # Identificar tipo de objetivo
        detected_objective = None
        for obj_type, keywords in objective_filters.items():
            if any(keyword in objective_lower for keyword in keywords):
                detected_objective = obj_type
                break
        
        if detected_objective:
            # Adicionar termos específicos do objetivo
            relevant_terms = objective_filters[detected_objective]
            filtered_terms.extend(relevant_terms)
        
        # Remover termos irrelevantes para o objetivo
        if 'technical' not in objective_lower:
            filtered_terms = [t for t in filtered_terms if t not in ['api', 'code', 'tech']]
        
        return list(set(filtered_terms))
    
    async def _score_term_relevance(
        self,
        terms: List[str],
        context: str,
        objective: str
    ) -> Dict[str, float]:
        """Score de relevância para cada termo"""
        
        scores = {}
        
        for term in terms:
            score = 0.5  # Base
            
            # Score por frequência no contexto
            if term.lower() in context.lower():
                score += 0.3
            
            # Score por relevância no objetivo
            if term.lower() in objective.lower():
                score += 0.4
            
            # Score por ML se disponível
            if self.ml_pipeline.active_model:
                try:
                    term_prediction = self.ml_pipeline.predict_with_confidence([
                        f"{term} no contexto de {context}"
                    ])
                    if term_prediction:
                        score += term_prediction[0]['confidence'] * 0.3
                except Exception:
                    pass
            
            scores[term] = min(1.0, score)
        
        return scores
    
    def _get_top_terms(self, term_scores: Dict[str, float], limit: int = 15) -> List[str]:
        """Obtém top N termos por score"""
        sorted_terms = sorted(term_scores.items(), key=lambda x: x[1], reverse=True)
        return [term for term, score in sorted_terms[:limit]]
    
    async def _calculate_objective_alignment(
        self,
        terms: List[str],
        objective: str
    ) -> float:
        """Calcula alinhamento dos termos com o objetivo"""
        
        if not terms:
            return 0.0
        
        objective_words = set(objective.lower().split())
        term_words = set(' '.join(terms).lower().split())
        
        # Jaccard similarity
        intersection = len(objective_words.intersection(term_words))
        union = len(objective_words.union(term_words))
        
        return intersection / union if union > 0 else 0.0

# Instância global
_enhanced_ml_integrator: Optional[EnhancedMLIntegrator] = None

def get_enhanced_ml_integrator() -> EnhancedMLIntegrator:
    """Obtém instância global do integrador ML avançado"""
    global _enhanced_ml_integrator
    if _enhanced_ml_integrator is None:
        _enhanced_ml_integrator = EnhancedMLIntegrator()
    return _enhanced_ml_integrator

# Função de teste
async def test_enhanced_ml_integration():
    """Teste da integração ML avançada"""
    integrator = get_enhanced_ml_integrator()
    
    # Teste 1: Intervalo de confiança
    print("🧪 Testando intervalos de confiança...")
    confidence_interval = await integrator.calculate_enhanced_confidence_interval(
        prediction="nordeste",
        text_input="Forró animado no sertão pernambucano",
        cultural_context={
            'region': 'Nordeste',
            'cultural_circles': ['musica', 'tradicao'],
            'data_quality': 'high'
        }
    )
    print(f"Intervalo: [{confidence_interval.lower_bound:.3f}, {confidence_interval.upper_bound:.3f}]")
    print(f"Método: {confidence_interval.method}")
    
    # Teste 2: Enhancement de termos
    print("\n🔍 Testando refinamento de termos...")
    enhanced_terms = await integrator.enhance_research_refinement(
        original_terms=['música', 'cultura'],
        business_context="Startup de tech focada em música brasileira para Gen Z",
        user_objective="Aumentar engagement com música regional nordestina"
    )
    print(f"Termos finais: {enhanced_terms['final_recommendation'][:5]}")
    print(f"Score de relevância: {enhanced_terms['enhancement_metrics']['relevance_score']:.3f}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_ml_integration())
