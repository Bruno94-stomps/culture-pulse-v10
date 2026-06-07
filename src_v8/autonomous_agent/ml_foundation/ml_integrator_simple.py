"""
🚀 ML Foundation Integrator V9.0 - Versão Simplificada
Componente principal que integra todos os módulos de Machine Learning
Baseado em scikit-learn e bibliotecas leves; sem dependências pesadas (PYTORCH)
"""

import sys
import os
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

class MLIntegratorSimple:
    """Integrador principal dos componentes de Machine Learning"""
    
    def __init__(self):
        self.cultural_embeddings = None
        self.nlp_processor = None
        self.feedback_learner = None
        self.is_initialized = False
        
        print("🚀 ML Foundation Integrator V9.0 (Simplificado) inicializado!")
        
    def _initialize_components(self) -> Dict[str, bool]:
        """Inicializa todos os componentes ML"""
        results = {}
        
        # 1. Cultural Embeddings (Usar módulo simplificado)
        try:
            from autonomous_agent.ml_foundation.cultural_embeddings_simple import CulturalEmbeddingsSimple
            self.cultural_embeddings = CulturalEmbeddingsSimple()
            results['cultural_embeddings'] = True
            print("✅ Cultural Embeddings: OK")
        except Exception as e:
            results['cultural_embeddings'] = False
            print(f"❌ Cultural Embeddings: {e}")
            
        # 2. Advanced NLP Processor (Usar módulo existente)
        try:
            from autonomous_agent.ml_foundation.advanced_nlp_processor import AdvancedNLPProcessor
            self.nlp_processor = AdvancedNLPProcessor()
            results['nlp_processor'] = True
            print("✅ Advanced NLP: OK")
        except Exception as e:
            results['nlp_processor'] = False
            print(f"❌ Advanced NLP: {e}")
            
        # 3. Feedback Learning Engine (Usar versão avançada)
        try:
            from autonomous_agent.ml_foundation.feedback_learning import FeedbackLearningEngine
            self.feedback_learner = FeedbackLearningEngine()
            results['feedback_learner'] = True
            print("✅ Feedback Learning (avançado): OK")
        except Exception as e:
            results['feedback_learner'] = False
            print(f"❌ Feedback Learning: {e}")
            
        # 4. 🤖 GitHub Models Engine (Corrigir import)
        try:
            from autonomous_agent.ml_foundation.github_models import GitHubModelsEngine
            self.github_models = GitHubModelsEngine()
            
            # Inicializar para configurar is_initialized
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            if not loop.is_running():
                loop.run_until_complete(self.github_models.initialize())
            
            # Verificar se está disponível (aceitar modo demo)
            if hasattr(self.github_models, 'is_available') and self.github_models.is_available():
                connection_test = self.github_models.test_connection()
                results['github_models'] = True
                if connection_test.get('demo_mode'):
                    print("✅ GitHub Models: OK (modo demo)")
                else:
                    print("✅ GitHub Models: OK")
            else:
                results['github_models'] = False
                print("⚠️ GitHub Models: Não disponível")
                
        except Exception as e:
            results['github_models'] = False
            print(f"❌ GitHub Models: {e}")
            self.github_models = None
            
        # Ajustar lógica de inicialização
        essential_components = ['cultural_embeddings', 'nlp_processor', 'feedback_learner']
        essential_working = sum(1 for comp in essential_components if results.get(comp, False))
        
        self.is_initialized = essential_working >= 2  # Pelo menos 2 dos 3 essenciais
        
        total_working = sum(results.values())
        if self.is_initialized:
            github_status = "com GitHub Models" if results.get('github_models') else "sem GitHub Models"
            print(f"🎉 ML Foundation inicializado {github_status}! ({total_working}/4 componentes)")
        else:
            print(f"⚠️ ML Foundation parcialmente inicializado ({total_working}/4 componentes)")
            print("   Componentes essenciais insuficientes para funcionamento completo")
            
        return results
    
    async def initialize_components(self) -> Dict[str, bool]:
        """Método assíncrono para inicializar componentes"""
        return self._initialize_components()
        
    def process_cultural_analysis(self, business_context: str, user_terms: List[str]) -> Dict[str, Any]:
        """Análise cultural completa usando todos os componentes ML"""
        if not self.is_initialized:
            return {"error": "Componentes ML não inicializados"}
            
        try:
            result = {
                "timestamp": datetime.now().isoformat(),
                "business_context": business_context,
                "original_terms": user_terms,
                "analysis": {}
            }
            
            # 1. Análise NLP
            if self.nlp_processor:
                nlp_analysis = self.nlp_processor.analyze_business_context(business_context)
                result["analysis"]["nlp"] = nlp_analysis
                
            # 2. Embeddings culturais
            if self.cultural_embeddings:
                # Treinar com contexto se necessário
                if not self.cultural_embeddings.is_fitted:
                    self.cultural_embeddings.fit_cultural_embeddings([business_context] + user_terms)
                
                # Similaridades culturais
                cultural_similarities = self.cultural_embeddings.get_cultural_similarity(business_context)
                result["analysis"]["cultural_similarities"] = cultural_similarities
                
                # Padrões culturais nos termos
                patterns = self.cultural_embeddings.find_cultural_patterns(user_terms)
                result["analysis"]["cultural_patterns"] = patterns
                
            # 3. Aprendizado com feedback
            if self.feedback_learner:
                quality_prediction = self.feedback_learner.predict_term_quality(user_terms, business_context)
                result["analysis"]["quality_prediction"] = quality_prediction
                
            return result
            
        except Exception as e:
            return {"error": f"Erro na análise: {e}"}
            
    def enhance_terms_with_ml(self, terms: List[str], business_context: str) -> Dict[str, Any]:
        """Melhora termos usando ML + GitHub Models AI"""
        if not self.is_initialized:
            return {"enhanced_terms": terms, "confidence": 0.0}
            
        try:
            enhanced_terms = list(terms)  # Começar com termos originais
            confidence_scores = {}
            suggestions = []
            ai_enhancement = None
            
            # 🤖 1. GITHUB MODELS AI ENHANCEMENT (PRIORIDADE!)
            if hasattr(self, 'github_models') and self.github_models:
                try:
                    ai_result = self.github_models.enhance_terms_with_ai(
                        business_context, 
                        terms
                    )
                    
                    if ai_result.get("success"):
                        enhanced_terms = ai_result.get("enhanced_terms", terms)
                        ai_enhancement = {
                            "used": True,
                            "model": ai_result.get("model_used", "gpt-4o-mini"),
                            "tokens": ai_result.get("tokens_used", 0),
                            "reasoning": ai_result.get("ai_reasoning", "")
                        }
                        print(f"🤖 GitHub Models enhancement aplicado: {len(enhanced_terms)} termos")
                    else:
                        print(f"⚠️ GitHub Models falhou: {ai_result.get('error', 'Erro desconhecido')}")
                        
                except Exception as e:
                    print(f"❌ Erro GitHub Models: {e}")
            
            # 2. Análise NLP para sugestões (complementar)
            if self.nlp_processor:
                nlp_suggestions = self.nlp_processor.suggest_related_terms(business_context, terms)
                suggestions.extend(nlp_suggestions.get("suggestions", []))
                
            # 3. Embeddings para similaridade cultural
            if self.cultural_embeddings:
                for term in terms:
                    similarities = self.cultural_embeddings.get_cultural_similarity(term)
                    max_similarity = max(similarities.values()) if similarities else 0.0
                    confidence_scores[term] = max_similarity
                    
            # 4. Feedback learning para qualidade
            if self.feedback_learner:
                quality_scores = self.feedback_learner.predict_term_quality(enhanced_terms, business_context)
                
                # Adicionar termos de alta qualidade das sugestões
                for suggestion in suggestions:
                    if suggestion not in enhanced_terms:
                        quality = self.feedback_learner.predict_term_quality([suggestion], business_context)
                        if quality.get("average_quality", 0) > 0.7:
                            enhanced_terms.append(suggestion)
                            
            # Calcular confiança geral
            base_confidence = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0.5
            ai_boost = 0.3 if ai_enhancement and ai_enhancement.get("used") else 0.0
            overall_confidence = min(base_confidence + ai_boost, 1.0)
            
            return {
                "enhanced_terms": enhanced_terms,
                "confidence": overall_confidence,
                "term_scores": confidence_scores,
                "suggestions": suggestions,
                "ai_enhancement": ai_enhancement,
                "ml_analysis": "completed_with_ai" if ai_enhancement else "completed_without_ai"
            }
            
        except Exception as e:
            return {
                "enhanced_terms": terms,
                "confidence": 0.0,
                "error": f"Erro no enhancement: {e}"
            }
            
    def train_with_feedback(self, session_data: Dict[str, Any]) -> bool:
        """Treina todos os componentes com feedback do usuário"""
        if not self.is_initialized:
            return False
            
        try:
            success_count = 0
            
            # 1. Treinar embeddings com contexto de negócio
            if self.cultural_embeddings and not self.cultural_embeddings.is_fitted:
                business_context = session_data.get("business_context", "")
                terms = session_data.get("original_config", {}).get("terms", [])
                success = self.cultural_embeddings.fit_cultural_embeddings([business_context] + terms)
                if success:
                    success_count += 1
                    
            # 2. Treinar feedback learner
            if self.feedback_learner:
                success = self.feedback_learner.learn_from_feedback(session_data)
                if success:
                    success_count += 1
                    
            # 3. Atualizar NLP com contexto
            if self.nlp_processor:
                success = self.nlp_processor.update_context_knowledge(
                    session_data.get("business_context", ""),
                    session_data.get("user_rating", 0)
                )
                if success:
                    success_count += 1
                    
            return success_count > 0
            
        except Exception as e:
            print(f"❌ Erro no treinamento: {e}")
            return False
            
    def get_ml_stats(self) -> Dict[str, Any]:
        """Estatísticas de todos os componentes ML + GitHub Models"""
        stats = {
            "initialized": self.is_initialized,
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        if self.cultural_embeddings:
            stats["components"]["embeddings"] = self.cultural_embeddings.get_embedding_stats()
            
        if self.nlp_processor:
            stats["components"]["nlp"] = self.nlp_processor.get_processor_stats()
            
        if self.feedback_learner:
            stats["components"]["learning"] = self.feedback_learner.get_learning_stats()
            
        # 🤖 GitHub Models stats
        if hasattr(self, 'github_models') and self.github_models:
            stats["components"]["github_models"] = self.github_models.get_usage_stats()
        else:
            stats["components"]["github_models"] = {"available": False, "reason": "Not configured"}
            
        return stats

def create_ml_integrator() -> MLIntegratorSimple:
    """Factory function para criar integrador ML"""
    return MLIntegratorSimple()

# Teste básico
if __name__ == "__main__":
    print("🧪 Testando ML Foundation Integrator Simplificado...")
    
    # Criar integrador
    integrator = create_ml_integrator()
    
    # Inicializar componentes
    results = integrator.initialize_components()
    print(f"📊 Resultados da inicialização: {results}")
    
    if integrator.is_initialized:
        # Teste de análise cultural
        test_context = "Startup de tecnologia focada em fintech para pequenas empresas no Brasil"
        test_terms = ["fintech", "tecnologia", "startup"]
        
        analysis = integrator.process_cultural_analysis(test_context, test_terms)
        print(f"✅ Análise cultural: {bool(analysis.get('analysis'))}")
        
        # Teste de enhancement
        enhanced = integrator.enhance_terms_with_ml(test_terms, test_context)
        print(f"✅ Enhancement ML: {enhanced.get('confidence', 0):.2f}")
        
        # Estatísticas
        stats = integrator.get_ml_stats()
        print(f"✅ Stats ML: {len(stats.get('components', {}))}")
        
        print("🎉 ML Foundation Integrator funcionando!")
    else:
        print("❌ Falha na inicialização!")
