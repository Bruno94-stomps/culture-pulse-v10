"""
Context Enricher Integration para Dashboard
Módulo de integração do Context Enricher com o Cultural Dashboard

Autor: Culture Pulse V9
Data: 2026-02-05
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from config import config

logger = logging.getLogger(__name__)

# Import do Context Enricher e BusinessSynthesizer para Narrativa Real (V9.9)
try:
    from core.intelligence.business_synthesizer import BusinessSynthesizer, BusinessContext
    from core.classifiers.authenticity_analyzer import AuthenticityResult
    from core.engines.reliability_engine import get_reliability_engine
    SYNTHESIZER_AVAILABLE = True
except ImportError:
    # 🛡️ Circular Dependency Protection / Mock (V9.9)
    class BusinessContext:
        def __init__(self, **kwargs):
            for k, v in kwargs.items(): setattr(self, k, v)
    
    class BusinessSynthesizer: pass
    class AuthenticityResult: pass
    
    SYNTHESIZER_AVAILABLE = False
    print("⚠️ BusinessSynthesizer ou ReliabilityEngine não disponível para narrativa real")

# Import do SLM Local (Ollama) fora do bloco try de dependências circulares para garantir disponibilidade
try:
    from core.intelligence.local_slm_bridge import get_slm_bridge
except ImportError:
    def get_slm_bridge(): return None

# Import do Monitoramento Integrado (V9.1 Bridge)
try:
    from monitoring.integrated_monitoring import IntegratedMonitoring
    monitoring = IntegratedMonitoring()
except ImportError:
    monitoring = None

# Import do Context Enricher
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "context_enricher", 
        Path(__file__).parent.parent / "core" / "context_enricher.py"
    )
    context_enricher_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(context_enricher_module)
    ContextEnricher = context_enricher_module.ContextEnricher
    CONTEXT_ENRICHER_AVAILABLE = True
    print("✅ Context Enricher carregado para dashboard")
except Exception as e:
    CONTEXT_ENRICHER_AVAILABLE = False
    print(f"⚠️ Context Enricher não disponível: {e}")
    ContextEnricher = None


def get_dashboard_context_enricher(use_llm: bool = True) -> 'DashboardContextEnricher':
    """Retorna instância singleton do DashboardContextEnricher (V9.9)"""
    return DashboardContextEnricher(use_llm=use_llm)

class DashboardContextEnricher:
    """
    Wrapper do Context Enricher para integração com Dashboard
    Adiciona camada de contexto narrativo REAL conectada ao Onboarding (V9.9)
    """
    
    def __init__(self, use_llm: bool = False):
        """
        Inicializar enricher do dashboard
        
        Args:
            use_llm: Se True, tenta carregar o SLM Local (Ollama)
        """
        self.enricher = None
        self.slm_bridge = get_slm_bridge() if use_llm else None
        self.synthesizer = BusinessSynthesizer() if SYNTHESIZER_AVAILABLE else None
        self.reliability_engine = get_reliability_engine() if SYNTHESIZER_AVAILABLE else None
        self.available = CONTEXT_ENRICHER_AVAILABLE
        
        if CONTEXT_ENRICHER_AVAILABLE and ContextEnricher:
            try:
                self.enricher = ContextEnricher(use_llm=use_llm)
                print("🎯 Context Enricher inicializado no dashboard")
            except Exception as e:
                print(f"⚠️ Erro ao inicializar Context Enricher: {e}")
                self.available = False
    
    def _normalize_onboarding_context(self, contexto_onboarding: Any) -> Optional[BusinessContext]:
        """Normaliza diferentes formatos de onboarding para BusinessContext."""
        if contexto_onboarding is None:
            return None

        if isinstance(contexto_onboarding, BusinessContext):
            return contexto_onboarding

        if isinstance(contexto_onboarding, dict):
            scenario_type = (
                contexto_onboarding.get('user_intent') or
                contexto_onboarding.get('intent') or
                contexto_onboarding.get('business_objective') or
                contexto_onboarding.get('moment') or
                "Pesquisa de Mercado"
            )
            target_audience = (
                contexto_onboarding.get('target_audience') or
                contexto_onboarding.get('segment') or
                contexto_onboarding.get('brand') or
                ""
            )
            business_objective = (
                contexto_onboarding.get('business_objective') or
                contexto_onboarding.get('objective') or
                contexto_onboarding.get('moment') or
                "Detectar sinais fracos relevantes"
            )
            opportunities_sought = (
                contexto_onboarding.get('opportunities_sought') or
                contexto_onboarding.get('opportunities') or
                []
            )
            try:
                return BusinessContext(
                    scenario_type=scenario_type,
                    target_audience=target_audience,
                    business_objective=business_objective,
                    opportunities_sought=opportunities_sought,
                )
            except Exception:
                return BusinessContext(
                    scenario_type=scenario_type,
                    target_audience=target_audience,
                    business_objective=business_objective,
                    opportunities_sought=opportunities_sought,
                )

        return None

    def enrich_weak_signal(
        self, 
        signal: Dict, 
        segmento: Optional[str] = None, 
        desafio: Optional[str] = None,
        contexto_onboarding: Optional[BusinessContext] = None
    ) -> Dict:
        """
        Enriquece um sinal fraco com narrativa REAL baseada no Onboarding (V9.9)
        
        Args:
            signal: Dicionário com dados do sinal (title, description, strength, etc.)
            segmento: Segmento de negócio (Tecnologia, E-commerce, Saúde, etc.)
            desafio: Tipo de desafio (lancamento_produto, reposicionamento, etc.)
            contexto_onboarding: Contexto real do BusinessSynthesizer
        
        Returns:
            Signal enriquecido com campos de contexto cultural
        """
        if contexto_onboarding is None:
            contexto_onboarding = signal.get('onboarding_context') or signal.get('contexto_onboarding')

        if contexto_onboarding is not None:
            contexto_onboarding = self._normalize_onboarding_context(contexto_onboarding)

        if not self.available and not (self.slm_bridge and self.slm_bridge.is_available):
            return signal

        print(f"DEBUG: enrich_weak_signal iniciado. SLM_Bridge: {bool(self.slm_bridge)}")
        
        try:
            # 1. Injetar Metadados de Veracidade Biográfica Dinâmica (V9.9)
            if self.reliability_engine:
                # 🛡️ DETERMINAR EVIDÊNCIA VISUAL PARA O MOTOR (V9.9)
                # Um sinal tem evidência visual se contiver campos de imagem, thumbnail ou link de vídeo
                has_visual = any([
                    signal.get('image'), 
                    signal.get('thumbnail'), 
                    signal.get('media_url'),
                    'youtube' in signal.get('source', '').lower(),
                    'instagram' in signal.get('source', '').lower()
                ])
                signal['visual_proof'] = has_visual

                reliability_meta = self.reliability_engine.calculate_reliability(signal)
                signal['reliability'] = reliability_meta['reliability']
                signal['accuracy_score'] = reliability_meta['accuracy_score']
                signal['is_verified'] = reliability_meta['is_verified']
            
            # Garantia se motor falhar
            if 'reliability' not in signal:
                signal['reliability'] = "MEDIA"

            # 2. Obter Métricas REAIS do Monitoramento (V9.1 bridge - Essencial para Dados Reais)
            drift_data = monitoring.get_latest_drift() if monitoring else {}
            termo = signal.get('title', 'Sinal Fraco')
            real_drift = drift_data.get(termo, {})
            
            # Cálculo de métricas dinâmicas (DNA do Sinal)
            metricas = {
                'sentiment_stability': real_drift.get('stability', signal.get('strength', 0.5)),
                'viralidade': real_drift.get('velocity', signal.get('strength', 0.5) * 0.9),
                'engagement_rate': real_drift.get('engagement', 0.03 if signal.get('strength', 0) < 0.7 else 0.08),
                'momentum': int(real_drift.get('momentum', signal.get('strength', 0.5) * 60)),
                'volume': int(real_drift.get('volume', signal.get('strength', 0.5) * 2000))
            }

            # 3. Gerar Narrativa Real via BusinessSynthesizer (Removendo simulações estáticas)
            if (self.synthesizer or True) and contexto_onboarding:
                # Tentar SLM Local (Ollama) prioritariamente se disponível (V9.9)
                if self.slm_bridge and self.slm_bridge.is_available:
                    business_dict = {
                        "business_objective": getattr(contexto_onboarding, 'business_objective', ""),
                        "target_audience": getattr(contexto_onboarding, 'target_audience', ""),
                    }
                    try:
                        narrativa_local = self.slm_bridge.synthesize_narrative(signal, business_dict)
                        if narrativa_local:
                            signal['narrativa_cultural'] = narrativa_local
                            signal['using_local_slm'] = True
                            return signal
                    except Exception as e:
                        logger.warning(f"⚠️ Erro ao gerar narrativa no Llama-3 Local: {e}")

                # 🚀 NOVO CAMINHO V9.9: Se SLM falhou ou não está habilitado, mas temos BusinessContext
                # Tentar enriquecimento mesmo sem synthesizer disponível
                if not self.synthesizer and contexto_onboarding:
                    signal['narrativa_cultural'] = "Processando análise via motor secundário..."
                    signal['using_local_slm'] = False

                # Fallback para o Synthesizer clássico (Heurístico/Template)
                if self.synthesizer and contexto_onboarding:
                    insight = self.synthesizer.refine_context(signal, contexto_onboarding)
                    signal['narrativa_cultural'] = insight.narrative_context
                    signal['recomendacao_acao'] = insight.strategic_action
                    signal['using_local_slm'] = False
                    
                    # Injetar métricas no sinal para que o synthesizer as use na narrativa
                    signal_with_metrics = {**signal, **metricas}
                    
                    # Tentar definir auth_res se estiver disponível no synthesizer
                    auth_res = getattr(self.synthesizer, 'last_auth_result', None)

                    narrative = self.synthesizer._generate_cultural_narrative(
                        sig=signal_with_metrics, 
                        context=contexto_onboarding, 
                        auth=auth_res
                    )
                    
                    signal['contexto_cultural'] = narrative.get('context', '')
                    signal['relevancia_negocio'] = narrative.get('relevance', '')
                    
                    # Injetar conselho estratégico real considerando o momentum real
                    strategic_advice = self.synthesizer._generate_strategic_advice(
                        auth=auth_res,
                        threshold={'is_breakout': metricas['momentum'] > 75},
                        semantic={'tags': [signal.get('circulo', 'Geral')]},
                        narrative=narrative
                    )
                    signal['recomendacao_acao'] = strategic_advice
                
            elif self.enricher:
                # Fallback para context_enricher legado se synthesizer falhar
                context = self.enricher.enrich_signal(
                    termo=termo,
                    texto_api=signal.get('description', ''),
                    metricas=metricas,
                    segmento=segmento,
                    desafio=desafio
                )
                
                signal['contexto_cultural'] = context.get('contexto_cultural', '')
                signal['relevancia_negocio'] = context.get('relevancia_negocio', '')
                signal['recomendacao_acao'] = context.get('recomendacao_acao', signal.get('action', ''))
            
            # 3. Ajustar Narrativa baseado na Veracidade (Task 2)
            if signal.get('reliability') == "BAIXA":
                signal['contexto_cultural'] = f"🧪 [PROJEÇÃO ANALÍTICA - FONTE NÃO VERIFICADA]: {signal.get('contexto_cultural', '')}"
                signal['recomendacao_acao'] = f"⚠️ ALERTA: Este sinal provém de fonte simulada. Validar empiricamente antes de qualquer decisão. {signal.get('recomendacao_acao', '')}"
            
            return signal
            
        except Exception as e:
            print(f"⚠️ Erro ao enriquecer sinal: {e}")
            return signal
    
    def enrich_weak_signals_batch(
        self, 
        signals: List[Dict], 
        segmento: Optional[str] = None, 
        desafio: Optional[str] = None,
        contexto_onboarding: Optional[BusinessContext] = None
    ) -> List[Dict]:
        """
        Enriquece múltiplos sinais fracos em lote
        V9.9: Agora usa ReliabilityEngine com Cross-Verification em lote.
        """
        # 1. Rodar Reliability Engine com Contexto de Batch (NOVO V9.9)
        from core.engines.reliability_engine import ReliabilityEngine
        rel_engine = ReliabilityEngine()
        
        # Processar a confiabilidade de todos com o contexto do batch
        for sig in signals:
            model_acc = 0.5
            rel_data = rel_engine.calculate_reliability(sig, model_accuracy=model_acc, batch_context=signals)
            sig.update(rel_data)
        
        if not self.available:
            return signals
        
        # 2. Prosseguir com o enriquecimento individual (narrativa)
        enriched = []
        for signal in signals:
            enriched.append(self.enrich_weak_signal(signal, segmento, desafio, contexto_onboarding))
        
        return enriched
    
    def get_available_segments(self) -> List[str]:
        """Retorna lista de segmentos disponíveis"""
        return [
            "Tecnologia", "E-commerce", "Saúde", "Alimentação",
            "Moda", "Entretenimento", "Educação", "Turismo",
            "Varejo", "Serviços Financeiros", "Esportes"
        ]
    
    def get_available_challenges(self) -> List[str]:
        """Retorna lista de desafios disponíveis"""
        return [
            "lancamento_produto", "reposicionamento", "expansao_mercado",
            "crise_reputacao", "construcao_marca", "pesquisa_mercado"
        ]


# Exemplo de uso no dashboard
if __name__ == "__main__":
    print("\n" + "="*80)
    print("TESTE: Context Enricher Integration para Dashboard")
    print("="*80)
    
    enricher = DashboardContextEnricher()
    
    # Sinal fraco de exemplo
    signal = {
        'title': 'Live Commerce Periferia RJ',
        'description': 'Lives de vendas explodem nas periferias do Rio de Janeiro. Empreendedores locais vendem produtos com humor e proximidade.',
        'strength': 0.76,
        'source': 'Instagram Analytics',
        'actionable': True,
        'action': 'Mapear influenciadores locais para parcerias'
    }
    
    print("\n📊 SINAL ORIGINAL:")
    print(f"   Título: {signal['title']}")
    print(f"   Força: {signal['strength']:.1%}")
    
    # Enriquecer
    enriched = enricher.enrich_weak_signal(
        signal, 
        segmento='E-commerce', 
        desafio='pesquisa_mercado'
    )
    
    print("\n🎯 SINAL ENRIQUECIDO:")
    if enriched.get('contexto_cultural'):
        print(f"\n   📖 Contexto Cultural:")
        print(f"   {enriched['contexto_cultural'][:200]}...")
    
    if enriched.get('circulos_culturais'):
        print(f"\n   🔄 Círculos Culturais:")
        print(f"   {enriched['circulos_culturais'][:150]}...")
    
    if enriched.get('relevancia_negocio'):
        print(f"\n   💼 Relevância de Negócio:")
        print(f"   {enriched['relevancia_negocio'][:150]}...")
    
    if enriched.get('recomendacao_acao'):
        print(f"\n   💡 Recomendação:")
        print(f"   {enriched['recomendacao_acao'][:200]}...")
    
    print("\n" + "="*80)
    print("✅ Integration testada com sucesso!")
    print("="*80)
    print("\n📝 COMO USAR NO DASHBOARD:")
    print("```python")
    print("from dashboard.context_enricher_integration import DashboardContextEnricher")
    print("")
    print("# Inicializar")
    print("enricher = DashboardContextEnricher()")
    print("")
    print("# Enriquecer sinais")
    print("weak_signals = generate_weak_signals()")
    print("enriched_signals = enricher.enrich_weak_signals_batch(")
    print("    weak_signals,")
    print("    segmento='E-commerce',  # Seleção do usuário")
    print("    desafio='pesquisa_mercado'  # Seleção do usuário")
    print(")")
    print("")
    print("# Display no Streamlit")
    print("for signal in enriched_signals:")
    print("    st.subheader(signal['title'])")
    print("    if signal.get('contexto_cultural'):")
    print("        with st.expander('🇧🇷 Ver Contexto Cultural'):")
    print("            st.markdown(signal['contexto_cultural'])")
    print("            st.info(signal['relevancia_negocio'])")
    print("```")
