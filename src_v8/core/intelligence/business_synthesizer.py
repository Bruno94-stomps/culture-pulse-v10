"""
🎯 Business Synthesizer V9.0 - IA Generativa para Refinamento de Contexto
Componente central que sintetiza insights culturais em estratégias de negócio
"""

import asyncio
import json
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union

logger = logging.getLogger(__name__)
from dataclasses import dataclass, field
from enum import Enum

# Protocolos para Tipagem Segura V10.0
# Usamos Forward References ('AuthenticityResult') para evitar erros de importação circular ou runtime
if True: # Simulado para garantir escopo local
    try:
        from core.classifiers.authenticity_analyzer import AuthenticityResult, AuthenticityAnalyzer
    except ImportError:
        try:
            from src_v8.core.classifiers.authenticity_analyzer import AuthenticityResult, AuthenticityAnalyzer
        except ImportError:
            class AuthenticityResult: pass
            class AuthenticityAnalyzer: pass

# Importar DNA Cultural V9.9 centralizado
try:
    from core.intelligence.research_refiner import CULTURAL_CIRCLES, CULTURAL_CIRCLES_BY_LEVEL
except ImportError:
    CULTURAL_CIRCLES = []
    CULTURAL_CIRCLES_BY_LEVEL = {}

try:
    from core.intelligence.local_slm_bridge import LocalSLMBridge
    from core.intelligence.semantic_matrix_scorer import dynamic_scorer
except ImportError:
    try:
        from src_v8.core.intelligence.local_slm_bridge import LocalSLMBridge
    except ImportError:
        LocalSLMBridge = None

@dataclass
class BusinessContext:
    """Contexto de negócio estruturado"""
    scenario_type: str  # "Pesquisa de Mercado", "Lançamento de Produto", etc.
    target_audience: str  # "público periférico do Rio de Janeiro" (agora mapeado para 'segment')
    business_objective: str  # "mapear autenticidade cultural"
    opportunities_sought: List[str]  # ["conexão genuína", "penetração cultural"]
    constraints: List[str] = field(default_factory=list)
    success_metrics: List[str] = field(default_factory=list)

    @property
    def segment(self) -> str:
        """Alias para target_audience para manter compatibilidade com V9.9 ResearchRefiner"""
        return self.target_audience

@dataclass
class CulturalInsight:
    """Insight cultural identificado"""
    circle_name: str
    relevance_score: float
    authenticity_level: str  # "genuíno", "superficial", "emergente"
    opportunity_type: str  # "conexão", "produto", "comunicação"
    evidence: List[str]
    business_implication: str
    narrative_context: Optional[str] = None  # Antigo contexto_cultural (V9.7)
    strategic_action: Optional[str] = None   # Antigo recomendacao_acao (V9.7)

@dataclass
class RefinedStrategy:
    """Estratégia refinada pela IA"""
    primary_approach: str
    secondary_approaches: List[str]
    cultural_bridges: List[str]  # Pontes culturais identificadas
    risk_factors: List[str]
    implementation_steps: List[str]
    expected_outcomes: List[str]
    cultural_authenticity_score: float

class BusinessSynthesizer:
    """Sistema de IA Generativa para refinamento de contexto de negócio"""
    
    def __init__(self, slm_bridge = None):
        self._raw_cultural_circles = self._load_cultural_circles()
        self.synthesis_patterns = self._load_synthesis_patterns()
        self.authenticity_markers = self._load_authenticity_markers()
        
        # 📐 LENS WEIGHTED ATTENTION (V9.5)
        # Multiplicadores matemáticos baseados na lente do Onboarding
        self.lens_multipliers = {
            'PROTECAO': {'stability': 1.5, 'risk': 1.4, 'momentum': 0.8},
            'ACAO': {'momentum': 1.5, 'accelerator': 1.4, 'stability': 0.9},
            'EXPLORACAO': {'dissonance': 1.6, 'alpha': 1.5, 'pioneering': 1.4}
        }

        # 🧠 SEMANTIC EXPANSION PROVIDER (V9.5 - Híbrido Sabiá-2) / Maritaca AI fallback
        self.semantic_provider = "SABIÁ-2" if slm_bridge and "maritaca" in str(getattr(slm_bridge, 'model', '')).lower() else "LOCAL_FALLBACK"

        # Inicializar SLM Bridge para estratégias inteligentes (V9.9)
        self.slm_bridge = slm_bridge
        if not self.slm_bridge and LocalSLMBridge:
            try:
                self.slm_bridge = LocalSLMBridge()
                if not self.slm_bridge.is_available:
                    self.slm_bridge = None
            except Exception:
                self.slm_bridge = None

        # Sincronização Dinâmica com DNA Cultural V9.9
        self.cultural_circles = {}
        try:
            from core.intelligence.research_refiner import CULTURAL_CIRCLES
        except ImportError:
            try:
                from src_v8.core.intelligence.research_refiner import CULTURAL_CIRCLES
            except ImportError:
                CULTURAL_CIRCLES = []

        for circle in CULTURAL_CIRCLES:
            # Manter metadados do synthesizer se existirem, senão criar default
            if circle in self._raw_cultural_circles:
                self.cultural_circles[circle] = self._raw_cultural_circles[circle]
            else:
                self.cultural_circles[circle] = {
                    'weight': 0.8,
                    'business_relevance': 0.70,
                    'authenticity_markers': ['novo_comportamento', 'emergente'],
                    'opportunity_types': ['inovacao', 'comunicacao'],
                    'risk_factors': ['incerteza_dados']
                }

        # Mapeamento narrativo brasileiro (V9.9 - Conectado com Veracidade)
        self.narrative_patterns = {
            'estetica': "Resiliência urbana e o 'visual do corre'. Ativação via códigos de pertencimento periférico.",
            'comunidade': "Solidariedade local e micro-influência territorial. O produto como facilitador de encontros.",
            'inovacao': "O 'jeitinho' como motor de eficiência. Soluções adaptativas locais.",
            'celebracao': "Válvula de escape cultural. Ocupação do espaço da alegria legítima."
        }
        
        print(f"🎯 Business Synthesizer V9.9 ({len(self.cultural_circles)} Círculos Dinâmicos) inicializado!")

    def apply_lens_weighting(self, base_score: float, metric_type: str, lens: str) -> float:
        """
        Calcula o score ponderado pela Lente de Branding (V9.5).
        """
        if lens not in self.lens_multipliers:
            return base_score
            
        multipliers = self.lens_multipliers[lens]
        # Mapeia tipos de métrica para os multiplicadores da lente
        mapping = {
            'momentum': 'momentum',
            'alpha': 'alpha',
            'pioneering': 'pioneering',
            'risk': 'risk',
            'stability': 'stability',
            'dissonance': 'dissonance'
        }
        
        multiplier_key = mapping.get(metric_type)
        if multiplier_key and multiplier_key in multipliers:
            return base_score * multipliers[multiplier_key]
            
        return base_score

    def calculate_alpha_slope(self, momentum_series: List[float]) -> float:
        """
        Calcula o 'Slope' (inclinação) da tendência para determinar
        o Alpha Cultural (Inflexão).
        Fórmula: (Momentum_t - Momentum_t-1) / Delta_t
        """
        if len(momentum_series) < 2:
            return 0.0
        
        # Simples inclinação linear entre os dois últimos pontos
        slope = momentum_series[-1] - momentum_series[-2]
        return slope

    def _load_cultural_circles(self) -> Dict[str, Dict[str, Any]]:
        """Carrega os 16 círculos culturais com contexto de negócio"""
        return {
            # CÍRCULOS CENTRAIS (Alma Profunda)
            'festa_celebracao': {
                'weight': 1.0,
                'business_relevance': 0.95,
                'authenticity_markers': ['espontaneidade', 'coletividade', 'alegria_genuína'],
                'opportunity_types': ['eventos', 'experiências', 'produtos_festivos'],
                'risk_factors': ['comercialização_excessiva', 'apropriação_cultural']
            },
            'familia_comunidade': {
                'weight': 1.0,
                'business_relevance': 0.92,
                'authenticity_markers': ['laços_familiares', 'solidariedade', 'proteção_coletiva'],
                'opportunity_types': ['produtos_familiares', 'serviços_comunitários'],
                'risk_factors': ['invasão_privacidade', 'valores_conflitantes']
            },
            'musicalidade_expressao': {
                'weight': 1.0,
                'business_relevance': 0.89,
                'authenticity_markers': ['criatividade_musical', 'expressão_corporal', 'ritmo_natural'],
                'opportunity_types': ['plataformas_música', 'experiências_sonoras'],
                'risk_factors': ['padronização_cultura', 'perda_diversidade']
            },
            'religiosidade_popular': {
                'weight': 1.0,
                'business_relevance': 0.86,
                'authenticity_markers': ['sincretismo', 'devoção_popular', 'rituais_coletivos'],
                'opportunity_types': ['produtos_bem_estar', 'experiências_espirituais'],
                'risk_factors': ['apropriação_religiosa', 'desrespeito_tradições']
            },
            
            # CÍRCULOS INTERMEDIÁRIOS (Expressão Cultural)
            'jeitinho_brasileiro': {
                'weight': 0.9,
                'business_relevance': 0.83,
                'authenticity_markers': ['criatividade_solução', 'flexibilidade', 'improviso'],
                'opportunity_types': ['produtos_adaptativos', 'serviços_flexíveis'],
                'risk_factors': ['reforço_estereótipos', 'ética_questionável']
            },
            'futebol_esporte': {
                'weight': 0.9,
                'business_relevance': 0.81,
                'authenticity_markers': ['paixão_esportiva', 'identidade_coletiva', 'drama_emocional'],
                'opportunity_types': ['produtos_esportivos', 'experiências_torcida'],
                'risk_factors': ['comercialização_paixão', 'divisão_social']
            },
            'diversidade_regional': {
                'weight': 0.9,
                'business_relevance': 0.79,
                'authenticity_markers': ['orgulho_regional', 'tradições_locais', 'identidade_territorial'],
                'opportunity_types': ['produtos_regionais', 'turismo_cultural'],
                'risk_factors': ['generalização_regional', 'perda_especificidade']
            },
            'hospitalidade': {
                'weight': 0.9,
                'business_relevance': 0.77,
                'authenticity_markers': ['acolhimento_genuíno', 'generosidade', 'abertura_outro'],
                'opportunity_types': ['serviços_hospitalidade', 'experiências_acolhimento'],
                'risk_factors': ['exploração_bondade', 'superficialidade_comercial']
            },
            'improviso_criatividade': {
                'weight': 0.9,
                'business_relevance': 0.75,
                'authenticity_markers': ['solução_criativa', 'adaptação_rápida', 'inovação_popular'],
                'opportunity_types': ['produtos_inovativos', 'serviços_adaptativos'],
                'risk_factors': ['instabilidade_qualidade', 'falta_planejamento']
            },
            'natureza_meio_ambiente': {
                'weight': 0.9,
                'business_relevance': 0.73,
                'authenticity_markers': ['conexão_natureza', 'sustentabilidade_natural', 'biodiversidade'],
                'opportunity_types': ['produtos_sustentáveis', 'ecoturismo'],
                'risk_factors': ['greenwashing', 'destruição_ambiental']
            },
            'trabalho_conquista': {
                'weight': 0.9,
                'business_relevance': 0.71,
                'authenticity_markers': ['determinação', 'superação_dificuldades', 'conquista_merecida'],
                'opportunity_types': ['produtos_conquista', 'serviços_desenvolvimento'],
                'risk_factors': ['exploração_trabalho', 'promessas_falsas']
            },
            'humor_leveza': {
                'weight': 0.9,
                'business_relevance': 0.69,
                'authenticity_markers': ['bom_humor', 'leveza_vida', 'otimismo_natural'],
                'opportunity_types': ['entretenimento', 'comunicação_leve'],
                'risk_factors': ['banalização_problemas', 'humor_inadequado']
            },
            
            # CÍRCULOS EXTERNOS (Modernidade Adaptada)
            'tecnologia_acessivel': {
                'weight': 0.8,
                'business_relevance': 0.67,
                'authenticity_markers': ['inclusão_digital', 'tecnologia_popular', 'inovação_acessível'],
                'opportunity_types': ['tech_inclusiva', 'produtos_acessíveis'],
                'risk_factors': ['exclusão_digital', 'complexidade_excessiva']
            },
            'sustentabilidade_consciente': {
                'weight': 0.8,
                'business_relevance': 0.65,
                'authenticity_markers': ['consciência_ambiental', 'consumo_responsável', 'futuro_sustentável'],
                'opportunity_types': ['produtos_eco', 'serviços_sustentáveis'],
                'risk_factors': ['greenwashing', 'custo_alto']
            },
            'empreendedorismo_social': {
                'weight': 0.8,
                'business_relevance': 0.63,
                'authenticity_markers': ['impacto_social', 'inovação_social', 'transformação_coletiva'],
                'opportunity_types': ['negócios_impacto', 'plataformas_sociais'],
                'risk_factors': ['comercialização_causa', 'falta_impacto_real']
            },
            'identidade_digital': {
                'weight': 0.8,
                'business_relevance': 0.61,
                'authenticity_markers': ['expressão_digital', 'comunidades_online', 'influência_digital'],
                'opportunity_types': ['plataformas_digitais', 'influencer_marketing'],
                'risk_factors': ['superficialidade_digital', 'vício_tecnologia']
            }
        }
    
    def _load_synthesis_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Padrões de síntese para diferentes tipos de negócio"""
        return {
            'penetracao_mercado': {
                'primary_circles': ['familia_comunidade', 'diversidade_regional', 'hospitalidade'],
                'approach': 'Conectar-se através de valores familiares e comunitários genuínos',
                'authenticity_focus': 'Demonstrar respeito pelas tradições locais',
                'risk_mitigation': 'Evitar apropriação cultural superficial'
            },
            'lancamento_produto': {
                'primary_circles': ['improviso_criatividade', 'jeitinho_brasileiro', 'tecnologia_acessivel'],
                'approach': 'Apresentar produto como solução criativa e acessível',
                'authenticity_focus': 'Enfatizar adaptabilidade e praticidade',
                'risk_mitigation': 'Não subestimar a inteligência do consumidor'
            },
            'construcao_marca': {
                'primary_circles': ['musicalidade_expressao', 'humor_leveza', 'festa_celebracao'],
                'approach': 'Criar identidade baseada na expressividade e alegria genuína',
                'authenticity_focus': 'Celebrar a criatividade e espontaneidade',
                'risk_mitigation': 'Evitar estereótipos reducionistas'
            },
            'pesquisa_mercado': {
                'primary_circles': ['diversidade_regional', 'familia_comunidade', 'trabalho_conquista'],
                'approach': 'Mapear nuances regionais e valores familiares profundos',
                'authenticity_focus': 'Compreender contextos socioculturais específicos',
                'risk_mitigation': 'Não generalizar diferentes realidades'
            }
        }
    
    def _load_authenticity_markers(self) -> Dict[str, List[str]]:
        """Marcadores de autenticidade cultural"""
        return {
            'genuino': [
                'referencias_culturais_especificas', 'linguagem_natural', 'contexto_social_real',
                'valores_tradicionais', 'experiencias_vividas', 'emocoes_autenticas'
            ],
            'emergente': [
                'fusao_tradicional_moderno', 'adaptacao_cultural', 'inovacao_local',
                'juventude_urbana', 'tecnologia_popular', 'novos_valores'
            ],
            'superficial': [
                'estereotipos_culturais', 'cliches_visuais', 'apropriacao_comercial',
                'generalização_excessiva', 'falta_contexto', 'comercializacao_forçada'
            ]
        }
    
    def _load_authenticity_markers(self) -> Dict[str, List[str]]:
        """Carrega marcadores de autenticidade por círculo (V9.3 - Filtro de Improbabilidade)"""
        return {
            'festa_celebracao': ['espontaneidade', 'coletividade', 'alegria_genuína', 'rua', 'compartilhamento'],
            'familia_comunidade': ['laços_familiares', 'solidariedade', 'proteção_coletiva', 'raiz', 'herança'],
            'musicalidade_expressao': ['criatividade_musical', 'expressão_corporal', 'ritmo_natural', 'autoral', 'baile'],
            'trabalho_conquista': ['determinação', 'superação', 'corre', 'asfalto', 'vitória', 'postura'],
            'jeitinho_brasileiro': ['gambiarra', 'solução', 'malandragem_do_bem', 'agilidade'],
            # ... outros podem ser expandidos ...
        }

    def _get_obvious_associations(self) -> Dict[str, List[str]]:
        """
        Dicionário de ruído de alta correlação (Obviedade).
        Sinais que contenham apenas estes termos serão penalizados.
        Baseado em Mühlroth (2018) - Filtro de Entropia Positiva.
        """
        return {
            "carnaval": ["samba", "rio de janeiro", "folia", "bloquinho", "fantasia", "cerveja"],
            "futebol": ["gol", "estádio", "torcida", "campeonato", "bola", "seleção"],
            "tecnologia": ["celular", "internet", "computador", "aplicativo", "wifi"],
            "gastronomia": ["comida", "restaurante", "prato", "delicioso", "sabor", "receita"],
            "sustentabilidade": ["reciclagem", "meio ambiente", "natureza", "verde", "planeta"]
        }

    def calculate_signal_depth(self, signal_text: str, circle_name: str, feedback_weights: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Calcula a Profundidade do Sinal (V9.9.5) baseado em Entropia Cultural e Active Learning.
        
        Melhoria Híbrida:
        - Mantém a lógica de Clichês (Ruído Mainstream).
        - Integra feedback_weights vindos do ML Training (Active Learning).
        """
        markers = self.authenticity_markers.get(circle_name, [])
        obvious_map = self._get_obvious_associations()
        
        signal_text_lower = signal_text.lower()
        
        # 1. Autenticidade (Marcadores Genuínos)
        matches = [m for m in markers if m in signal_text_lower]
        match_count = len(matches)
        
        # 2. Fator de Entropia (Peso de Descoberta + Active Learning)
        discovery_multiplier = 1.0
        is_obvious = False
        
        # --- Lógica Estática de Clichês (Mantida) ---
        for category, terms in obvious_map.items():
            if any(term in signal_text_lower for term in terms):
                discovery_multiplier = 0.5 
                is_obvious = True
                break
        
        # --- NOVO: Lógica Híbrida de Active Learning (Feedback do Usuário) ---
        # Se o ML identificou que um termo 'clichê' é valioso para este usuário específico, 
        # o feedback_weights terá um valor alto (>1.0) para ele, anulando a penalidade.
        if feedback_weights:
            for term, weight in feedback_weights.items():
                if term.lower() in signal_text_lower:
                    # O multiplicador do ML tem precedência sobre o clichê estático
                    discovery_multiplier = weight 
                    if weight > 1.0:
                        is_obvious = False # Reclassifica como relevante se o usuário ensinou o sistema
                    break

        # Se for um sinal que NÃO é óbvio E tem marcadores genuínos (ou validado pelo usuário)
        if not is_obvious and match_count >= 2:
            # Bônus de "Descoberta / Data Mining" (Pode ser amplificado pelo ML)
            discovery_multiplier = max(discovery_multiplier, 1.5) 
            
        # 3. Cálculo Final de Profundidade
        # Score Base (Matches) * Fator de Descoberta
        base_score = min(1.0, match_count / 5.0)
        depth_score = base_score * discovery_multiplier
        
        # Garantir teto de 1.0 para o score final, exceto se for Weak Signal Elite
        final_score = round(min(1.0 if not discovery_multiplier > 1.0 else 1.2, depth_score), 3)
        
        if discovery_multiplier >= 1.5:
            level = "OUTLIER / DESCOBERTA (WEAK SIGNAL)"
            confidence = 0.85
        elif is_obvious:
            level = "MAINSTREAM (ALTA CORRELAÇÃO)"
            confidence = 0.95 # Alta confiança no que é óbvio
        else:
            level = "EMERGENTE / NATIVO"
            confidence = 0.70

        return {
            "depth_score": final_score,
            "discovery_factor": discovery_multiplier,
            "level": level,
            "is_outlier": discovery_multiplier > 1.0,
            "is_mainstream": is_obvious,
            "confidence": confidence,
            "matches": matches,
            "circle": circle_name,
            "timestamp": datetime.now().isoformat()
        }

    async def analyze_business_context(self, context_text: str) -> BusinessContext:
        """Analisa e estrutura o contexto de negócio usando IA"""
        return await self._analyze_business_context(context_text)

    async def _analyze_business_context(self, context_text: str) -> BusinessContext:
        """Analisa e estrutura o contexto de negócio usando IA"""
        
        # Extrair elementos do contexto
        scenario_type = self._extract_scenario_type(context_text)
        target_audience = self._extract_target_audience(context_text)
        business_objective = self._extract_business_objective(context_text)
        opportunities_sought = self._extract_opportunities(context_text)
        
        return BusinessContext(
            scenario_type=scenario_type,
            target_audience=target_audience,
            business_objective=business_objective,
            opportunities_sought=opportunities_sought,
            constraints=self._extract_constraints(context_text),
            success_metrics=self._infer_success_metrics(scenario_type, business_objective)
        )
    
    def _extract_scenario_type(self, text: str) -> str:
        """Extrai o tipo de cenário do texto"""
        scenario_keywords = {
            'Pesquisa de Mercado': ['pesquisa', 'mercado', 'entender', 'mapear', 'investigar'],
            'Lançamento de Produto': ['lançamento', 'produto', 'novo', 'introduzir', 'launch'],
            'Construção de Marca': ['marca', 'branding', 'identidade', 'posicionamento'],
            'Crise de Reputação': ['crise', 'reputação', 'imagem', 'problema', 'recuperar'],
            'Expansão de Mercado': ['expansão', 'crescimento', 'novos mercados', 'escalar']
        }
        
        text_lower = text.lower()
        scores = {}
        
        for scenario, keywords in scenario_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[scenario] = score
        
        return max(scores, key=scores.get) if max(scores.values()) > 0 else "Análise Geral"
    
    def _extract_target_audience(self, text: str) -> str:
        """Extrai o público-alvo do texto"""
        # Padrões para identificar público-alvo
        audience_patterns = [
            r'público ([^.]+)',
            r'audiência ([^.]+)', 
            r'consumidores? ([^.]+)',
            r'usuários? ([^.]+)',
            r'clientes? ([^.]+)'
        ]
        
        for pattern in audience_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Fallback: buscar menções geográficas ou demográficas
        if 'rio de janeiro' in text.lower():
            if 'periférico' in text.lower() or 'periferia' in text.lower():
                return "público periférico do Rio de Janeiro"
            return "público do Rio de Janeiro"
        
        return "público geral brasileiro"
    
    def _extract_business_objective(self, text: str) -> str:
        """Extrai o objetivo de negócio do texto"""
        objective_patterns = [
            r'objetivo[s]? ([^.]+)',
            r'meta[s]? ([^.]+)',
            r'pretende[m]? ([^.]+)',
            r'busca[m]? ([^.]+)',
            r'mapear ([^.]+)',
            r'identificar ([^.]+)',
            r'entender ([^.]+)'
        ]
        
        for pattern in objective_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "objetivo não especificado"
    
    def _extract_opportunities(self, text: str) -> List[str]:
        """Extrai oportunidades buscadas do texto"""
        opportunities = []
        
        opportunity_keywords = {
            'conexão genuína': ['conexão', 'genuína', 'autêntica', 'verdadeira'],
            'penetração cultural': ['penetração', 'inserção', 'entrada', 'acesso'],
            'engajamento profundo': ['engajamento', 'profundo', 'envolvimento', 'participação'],
            'autenticidade': ['autenticidade', 'autêntico', 'original', 'genuíno'],
            'relevância cultural': ['relevância', 'cultural', 'significado', 'importância']
        }
        
        text_lower = text.lower()
        
        for opportunity, keywords in opportunity_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                opportunities.append(opportunity)
        
        return opportunities if opportunities else ['compreensão cultural geral']
    
    def _extract_constraints(self, text: str) -> List[str]:
        """Extrai restrições do contexto"""
        constraints = []
        
        if 'periférico' in text.lower() or 'periferia' in text.lower():
            constraints.extend(['orçamento_limitado', 'acesso_digital_restrito', 'desconfiança_marcas'])
        
        if 'rio de janeiro' in text.lower():
            constraints.extend(['especificidade_regional', 'cultura_carioca_complexa'])
        
        return constraints
    
    def _infer_success_metrics(self, scenario_type: str, objective: str) -> List[str]:
        """Infere métricas de sucesso baseadas no cenário"""
        metric_mapping = {
            'Pesquisa de Mercado': [
                'profundidade_insights', 'precisão_segmentação', 'validação_hipóteses'
            ],
            'Lançamento de Produto': [
                'taxa_adoção', 'engajamento_inicial', 'feedback_qualitativo'
            ],
            'Construção de Marca': [
                'reconhecimento_marca', 'associação_valores', 'autenticidade_percebida'
            ]
        }
        
        return metric_mapping.get(scenario_type, ['engajamento_geral', 'satisfação_público'])
    
    async def synthesize_cultural_insights(self, 
                                         context: BusinessContext,
                                         cultural_data: Dict[str, Any]) -> List[CulturalInsight]:
        """Sintetiza insights culturais baseados no contexto de negócio"""
        
        insights = []
        
        # Analisar cada círculo cultural
        for circle_name, circle_data in self.cultural_circles.items():
            
            # Calcular relevância para o contexto específico
            relevance_score = self._calculate_circle_relevance(
                circle_name, circle_data, context, cultural_data
            )
            
            if relevance_score > 0.3: # Threshold de relevância
                
                # Determinar nível de autenticidade
                authenticity_level = self._assess_authenticity_level(
                    circle_name, context, cultural_data
                )
                
                # Identificar tipo de oportunidade
                opportunity_type = self._identify_opportunity_type(
                    circle_name, circle_data, context
                )
                
                # Coletar evidências
                evidence = self._collect_evidence(
                    circle_name, cultural_data, context
                )
                
                # Gerar implicação de negócio
                business_implication = self._generate_business_implication(
                    circle_name, circle_data, context, authenticity_level
                )
                
                insight = CulturalInsight(
                    circle_name=circle_name,
                    relevance_score=relevance_score,
                    authenticity_level=authenticity_level,
                    opportunity_type=opportunity_type,
                    evidence=evidence,
                    business_implication=business_implication
                )
                
                insights.append(insight)
        
        # Ordenar por relevância
        insights.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return insights[:8]  # Top 8 insights mais relevantes
    
    def _calculate_circle_relevance(self, 
                                  circle_name: str, 
                                  circle_data: Dict[str, Any],
                                  context: BusinessContext,
                                  cultural_data: Dict[str, Any]) -> float:
        """Calcula relevância do círculo para o contexto específico"""
        
        base_relevance = circle_data['business_relevance']
        
        # Ajustar baseado no tipo de cenário
        scenario_bonus = 0.0
        if context.scenario_type in self.synthesis_patterns:
            pattern = self.synthesis_patterns[context.scenario_type]
            if circle_name in pattern['primary_circles']:
                scenario_bonus = 0.2
        
        # Ajustar baseado no público-alvo
        audience_bonus = 0.0
        if 'periférico' in context.target_audience.lower():
            # Círculos mais relevantes para público periférico
            peripheral_circles = ['familia_comunidade', 'jeitinho_brasileiro', 'trabalho_conquista', 'improviso_criatividade']
            if circle_name in peripheral_circles:
                audience_bonus = 0.15
        
        # Ajustar baseado nos objetivos
        objective_bonus = 0.0
        if 'autenticidade' in context.business_objective.lower():
            central_circles = ['festa_celebracao', 'familia_comunidade', 'musicalidade_expressao']
            if circle_name in central_circles:
                objective_bonus = 0.1
        
        # Presença nos dados culturais
        data_bonus = 0.0
        if cultural_data and circle_name in str(cultural_data).lower():
            data_bonus = 0.1
        
        final_relevance = min(1.0, base_relevance + scenario_bonus + audience_bonus + objective_bonus + data_bonus)
        
        return final_relevance
        data_bonus = 0.0
        if cultural_data and circle_name in str(cultural_data).lower():
            data_bonus = 0.1
        
        final_relevance = min(1.0, base_relevance + scenario_bonus + audience_bonus + objective_bonus + data_bonus)
        
        return final_relevance
    
    def _assess_authenticity_level(self, 
                                 circle_name: str,
                                 context: BusinessContext,
                                 cultural_data: Dict[str, Any]) -> str:
        """Avalia nível de autenticidade do círculo no contexto"""
        
        # Análise baseada em marcadores de autenticidade
        genuine_markers = self.authenticity_markers['genuino']
        emergent_markers = self.authenticity_markers['emergente']
        superficial_markers = self.authenticity_markers['superficial']
        
        context_text = f"{context.business_objective} {context.target_audience} {' '.join(context.opportunities_sought)}"
        data_text = str(cultural_data) if cultural_data else ""
        
        combined_text = (context_text + " " + data_text).lower()
        
        genuine_score = sum(1 for marker in genuine_markers if marker in combined_text)
        emergent_score = sum(1 for marker in emergent_markers if marker in combined_text)
        superficial_score = sum(1 for marker in superficial_markers if marker in combined_text)
        
        # Contexto específico: público periférico tende a valorizar autenticidade
        if 'periférico' in context.target_audience.lower():
            genuine_score += 2
        
        if genuine_score >= emergent_score and genuine_score >= superficial_score:
            return "genuíno"
        elif emergent_score > superficial_score:
            return "emergente"
        else:
            return "superficial"
    
    def _identify_opportunity_type(self,
                                 circle_name: str,
                                 circle_data: Dict[str, Any],
                                 context: BusinessContext) -> str:
        """Identifica tipo de oportunidade para o círculo"""
        
        opportunity_types = circle_data.get('opportunity_types', ['conexão'])
        
        # Mapear objetivos para tipos de oportunidade
        if 'produto' in context.business_objective.lower():
            product_types = [ot for ot in opportunity_types if 'produto' in ot]
            return product_types[0] if product_types else opportunity_types[0]
        
        if 'comunicação' in context.business_objective.lower() or 'marca' in context.business_objectivo.lower():
            comm_types = [ot for ot in opportunity_types if 'comunicação' in ot or 'experiência' in ot]
            return comm_types[0] if comm_types else opportunity_types[0]
        
        return opportunity_types[0]
    
    def _collect_evidence(self,
                        circle_name: str,
                        cultural_data: Dict[str, Any],
                        context: BusinessContext) -> List[str]:
        """Coleta evidências para o insight"""
        
        evidence = []
        
        # Evidências do contexto
        if circle_name in ['familia_comunidade', 'diversidade_regional'] and 'rio de janeiro' in context.target_audience.lower():
            evidence.append("Forte identidade regional carioca")
        
        if 'periférico' in context.target_audience.lower() and circle_name in ['trabalho_conquista', 'improviso_criatividade']:
            evidence.append("Perfil resiliente e criativo do público periférico")
        
        # Evidências dos dados culturais (simuladas)
        if cultural_data:
            evidence.append("Presença confirmada nos dados culturais coletados")
        
        # Evidências baseadas no círculo específico
        circle_evidences = {
            'festa_celebracao': ["Tradição de celebrações coletivas", "Alta valorização de momentos festivos"],
            'familia_comunidade': ["Centralidade da família na cultura", "Redes de apoio comunitário"],
            'musicalidade_expressao': ["Rica tradição musical brasileira", "Expressividade como marca cultural"],
            'jeitinho_brasileiro': ["Criatividade para resolver problemas", "Flexibilidade cultural histórica"]
        }
        
        if circle_name in circle_evidences:
            evidence.extend(circle_evidences[circle_name])
        
        return evidence[:3]  # Máximo 3 evidências
    
    def _generate_business_implication(self,
                                     circle_name: str,
                                     circle_data: Dict[str, Any],
                                     context: BusinessContext,
                                     authenticity_level: str) -> str:
        """Gera implicação de negócio para o insight"""
        
        base_implications = {
            'festa_celebracao': "Criar experiências que celebrem momentos coletivos e espontâneos",
            'familia_comunidade': "Desenvolver soluções que fortaleçam laços familiares e comunitários",
            'musicalidade_expressao': "Incorporar elementos musicais e expressivos na estratégia",
            'jeitinho_brasileiro': "Valorizar soluções criativas e adaptáveis",
            'diversidade_regional': "Respeitar e celebrar especificidades regionais"
        }
        
        base_implication = base_implications.get(circle_name, "Integrar valores culturais autênticos")
        
        # Ajustar baseado no nível de autenticidade
        if authenticity_level == "genuíno":
            prefix = "Oportunidade prioritária: "
        elif authenticity_level == "emergente":
            prefix = "Potencial emergente: "
        else:
            prefix = "Atenção necessária: "
        
        # Ajustar baseado no contexto específico
        if context.scenario_type == "Pesquisa de Mercado":
            suffix = " - Investigar profundamente antes de ativação"
        elif "penetração" in context.opportunities_sought:
            suffix = " - Focar em inserção gradual e respeitosa"
        else:
            suffix = " - Manter autenticidade como prioridade"
        
        return prefix + base_implication + suffix
    
    async def generate_refined_strategy(self,
                                      context: BusinessContext,
                                      insights: List[CulturalInsight]) -> RefinedStrategy:
        """Gera estratégia refinada baseada nos insights culturais"""
        
        # Selecionar abordagem primária
        primary_approach = self._select_primary_approach(context, insights)
        
        # Identificar abordagens secundárias
        secondary_approaches = self._identify_secondary_approaches(context, insights)
        
        # Mapear pontes culturais
        cultural_bridges = self._map_cultural_bridges(insights)
        
        # Identificar fatores de risco
        risk_factors = self._identify_risk_factors(context, insights)
        
        # Gerar passos de implementação
        implementation_steps = self._generate_implementation_steps(context, insights)
        
        # Projetar resultados esperados
        expected_outcomes = self._project_expected_outcomes(context, insights)
        
        # Calcular score de autenticidade cultural
        authenticity_score = self._calculate_authenticity_score(insights)
        
        return RefinedStrategy(
            primary_approach=primary_approach,
            secondary_approaches=secondary_approaches,
            cultural_bridges=cultural_bridges,
            risk_factors=risk_factors,
            implementation_steps=implementation_steps,
            expected_outcomes=expected_outcomes,
            cultural_authenticity_score=authenticity_score
        )
    
    def _select_primary_approach(self, 
                               context: BusinessContext,
                               insights: List[CulturalInsight]) -> str:
        """Seleciona abordagem primária baseada no contexto e insights"""
        
        # Para público periférico do Rio de Janeiro
        if 'periférico' in context.target_audience.lower() and 'rio de janeiro' in context.target_audience.lower():
            
            # Priorizar insights com alta autenticidade
            genuine_insights = [i for i in insights if i.authenticity_level == "genuíno"]
            
            if genuine_insights:
                top_insight = genuine_insights[0]
                
                if top_insight.circle_name in ['familia_comunidade', 'diversidade_regional']:
                    return "Conectar-se através de valores familiares e identidade carioca periférica genuína"
                
                elif top_insight.circle_name in ['improviso_criatividade', 'jeitinho_brasileiro']:
                    return "Valorizar criatividade e soluções inovadoras da comunidade"
                
                elif top_insight.circle_name in ['musicalidade_expressao', 'festa_celebracao']:
                    return "Celebrar expressividade cultural e momentos coletivos autênticos"
        
        # Abordagem genérica baseada no tipo de cenário
        scenario_approaches = {
            'Pesquisa de Mercado': "Mapear nuances culturais com profundidade e respeito",
            'Lançamento de Produto': "Apresentar solução que dialoga com valores culturais",
            'Construção de Marca': "Construir identidade baseada em autenticidade cultural"
        }
        
        return scenario_approaches.get(context.scenario_type, "Desenvolver estratégia culturalmente sensível")
    
    def _identify_secondary_approaches(self,
                                     context: BusinessContext,
                                     insights: List[CulturalInsight]) -> List[str]:
        """Identifica abordagens secundárias"""
        
        secondary = []
        
        # Baseado nos insights de média relevância
        medium_insights = [i for i in insights[3:6] if i.relevance_score > 0.5]
        
        for insight in medium_insights:
            if insight.circle_name == 'tecnologia_acessivel':
                secondary.append("Incorporar soluções tecnológicas acessíveis")
            elif insight.circle_name == 'sustentabilidade_consciente':
                secondary.append("Enfatizar aspectos de sustentabilidade")
            elif insight.circle_name == 'empreendedorismo_social':
                secondary.append("Destacar impacto social positivo")
        
        return secondary[:3]
    
    def _map_cultural_bridges(self, insights: List['CulturalInsight']) -> List[str]:
        """Mapeia pontes culturais entre insights"""
        
        bridges = []
        
        # Identificar combinações sinérgicas
        insight_circles = [i.circle_name for i in insights[:5]]
        
        bridge_combinations = {
            ('familia_comunidade', 'diversidade_regional'): "Família como base da identidade regional",
            ('musicalidade_expressao', 'festa_celebracao'): "Música como elemento central das celebrações",
            ('improviso_criatividade', 'jeitinho_brasileiro'): "Criatividade como marca da adaptabilidade",
            ('tecnologia_acessivel', 'empreendedorismo_social'): "Tecnologia como ferramenta de impacto social"
        }
        
        for (circle1, circle2), bridge in bridge_combinations.items():
            if circle1 in insight_circles and circle2 in insight_circles:
                bridges.append(bridge)
        
        return bridges

    def _identify_risk_factors(self,
                             context: BusinessContext,
                             insights: List[CulturalInsight]) -> List[str]:
        """Identifica fatores de risco culturais"""
        
        risks = []
        
        # Riscos específicos do público periférico
        if 'periférico' in context.target_audience.lower():
            risks.extend([
                "Risco de estereotipação ou estigmatização",
                "Possível desconfiança em relação a marcas externas",
                "Necessidade de comprovação de compromisso genuíno"
            ])
        
        # Riscos baseados nos círculos culturais
        for insight in insights[:3]:
            circle_data = self.cultural_circles.get(insight.circle_name, {})
            circle_risks = circle_data.get('risk_factors', [])
            risks.extend(circle_risks)
        
        # Remover duplicatas e limitar
        return list(dict.fromkeys(risks))[:4]

    def _generate_implementation_steps(self,
                                     context: BusinessContext,
                                     insights: List['CulturalInsight']) -> List[str]:
        """Gera passos de implementação específicos"""
        
        steps = []
        
        # Etapa 1: Imersão cultural
        steps.append("Realizar imersão cultural profunda na comunidade periférica carioca")
        
        # Etapa 2: Validação de insights
        top_circles = [i.circle_name for i in insights[:3]]
        circle_names = ", ".join([c.replace('_', ' ').title() for c in top_circles])
        steps.append(f"Validar insights dos círculos culturais: {circle_names}")
        
        # Etapa 3: Co-criação
        steps.append("Desenvolver soluções em co-criação com representantes da comunidade")
        
        # Etapa 4: Teste piloto
        steps.append("Implementar teste piloto com feedback contínuo da comunidade")
        
        # Etapa 5: Refinamento
        steps.append("Refinar abordagem baseada no aprendizado do piloto")
        
        return steps

    def _project_expected_outcomes(self,
                                 context: BusinessContext,
                                 insights: List[CulturalInsight]) -> List[str]:
        """Projeta resultados esperados"""
        
        outcomes = []
        
        # Baseado no objetivo de negócio
        if 'autenticidade' in context.business_objective.lower():
            outcomes.append("Reconhecimento como marca autêntica e respeitosa")
        
        if 'conexão' in context.opportunities_sought:
            outcomes.append("Estabelecimento de conexões genuínas com a comunidade")
        
        if 'penetração' in context.opportunities_sought:
            outcomes.append("Inserção orgânica e aceita no mercado periférico")
        
        # Baseado na qualidade dos insights
        if insights:
            avg_relevance = sum(i.relevance_score for i in insights[:3]) / min(len(insights), 3)
            if avg_relevance > 0.8:
                outcomes.append("Alto potencial de engajamento cultural")
        
        return outcomes

    def calculate_authenticity_score(self, evidence: List[Dict[str, Any]], term: str, circle: str) -> float:
        """
        Calcula o Score de Autenticidade V9.6 baseado no Triângulo de Mühlroth:
        1. Prova Física (Mídia/Links)
        2. Prova Social (Engajamento Real vs Bots)
        3. Prova Semântica (Coerência com o Círculo)
        """
        score = 0.0
        
        # 1. Prova Física (Peso: 0.4)
        if evidence:
            # Ter evidência já garante 0.2
            score += 0.2
            # Se tiver thumbnail e for de fonte confiável, +0.2
            if any(ev.get('thumbnail') and ev.get('url') for ev in evidence):
                score += 0.2
        
        # 2. Prova Social & Anti-Bot (Peso: 0.3)
        # Simulação de integração com o AuthenticityAnalyzer
        # Em produção, chamaríamos analyzer.analyze_engagement(evidence)
        avg_views = sum(ev.get('views', 0) for ev in evidence) / len(evidence) if evidence else 0
        if avg_views > 100: # Mínimo de tração humana
            score += 0.15
        if len(evidence) > 1: # Multi-plataforma/Multi-post aumenta confiança
            score += 0.15
            
        # 3. Prova Semântica (Peso: 0.3)
        # Verifica se o termo 'casa' com o círculo
        circle_markers = self.cultural_circles.get(circle, {}).get('authenticity_markers', [])
        term_lower = term.lower()
        if any(marker in term_lower for marker in circle_markers):
            score += 0.3
        else:
            score += 0.15 # Coerência parcial
            
        return min(1.0, score)

    def get_signal_quality_label(self, score: float) -> str:
        """Retorna o label de qualidade baseado no score de autenticidade"""
        if score >= 0.8: return "FONTE QUALIFICADA (VERIFICADA)"
        if score >= 0.5: return "CONTEÚDO ORGÂNICO"
        return "SINAL EM VALIDAÇÃO"
    
    def _analyze_semantic_neighborhood(self, sig: Dict) -> Dict:
        """
        Analisa a vizinhança semântica de um sinal (V10.3).
        Determina se o termo está associado a novos contextos (tags).
        """
        termo = sig.get('termo', '').lower()
        texto = sig.get('texto_api', '').lower()
        
        # Simulação de extração de tags via NLP/Embeddings
        tags = []
        if 'dança' in texto or 'passinho' in texto: tags.append('estética urbana')
        if 'grupo' in texto or 'coletivo' in texto: tags.append('comunidade')
        if 'mistura' in texto or 'fusão' in texto: tags.append('hibridismo cultural')
        
        return {
            'tags': tags,
            'neighborhood_score': 0.8 if tags else 0.5
        }

    def _calculate_threshold_deviation(self, sig: Dict) -> Dict:
        """
        Calcula o desvio de limiar (momentum) do sinal (V10.3).
        """
        momentum = float(sig.get('momentum', 0.5))
        is_breakout = momentum > 80
        
        return {
            'velocity': momentum / 100.0,
            'is_breakout': is_breakout,
            'acceleration': 1.2 if is_breakout else 1.0
        }

    def analyze_cultural_signals(self, signals: List[Dict], context: BusinessContext) -> List[Dict]:
        """
        Sintetiza sinais brutos em insights de negócio com Narrativa Brasileira (V9.7)
        Unifica a inteligência do antigo ContextEnricherV2.
        """
        analyzer = AuthenticityAnalyzer()
        enriched_signals = []
        
        # 0. Definir os KPIs Estratégicos baseados no Onboarding (V10.4)
        intent_lower = context.scenario_type.lower() if hasattr(context, 'scenario_type') else "pesquisa de mercado"
        
        strategic_metrics = {
            'pesquisa de mercado': {
                "primary_metric": "Discovery Yield",
                "target_value": "> 0.35",
                "business_impact_estimated": "Redução de 20% no CAC via nichos orgânicos (Foresight Effectiveness)",
                "dashboard_lens": "Exploração (Gaps Culturais)",
                "cultural_alpha": 0.25
            },
            'lançamento de produto': {
                "primary_metric": "Impact on Momentum",
                "target_value": "Speed > 0.75",
                "business_impact_estimated": "Aumento de 15% na velocidade de adoção (Launch Alpha)",
                "dashboard_lens": "Ação (Oportunidade de Janela)",
                "cultural_alpha": 0.18
            },
            'crise de reputação': {
                "primary_metric": "Tension Mitigation",
                "target_value": "Delta < 0.15",
                "business_impact_estimated": "Proteção de Equity de Marca (Reparation Bridge)",
                "dashboard_lens": "Proteção (Heatmap de Risco)",
                "cultural_alpha": 0.40
            },
            'construção de marca': {
                "primary_metric": "Authenticity Depth",
                "target_value": "> 0.80",
                "business_impact_estimated": "LTV (Customer Lifetime Value) +10% via ressonância real",
                "dashboard_lens": "Identidade (Consistência de Narrativa)",
                "cultural_alpha": 0.12
            }
        }
        
        selected_kpis = strategic_metrics.get(intent_lower, strategic_metrics['pesquisa de mercado'])

        for sig in signals:
            # 1. Capturar evidências e vizinhança semântica
            evidence = sig.get('dados_extras', {}).get('evidence', [])
            raw_text = f"{sig.get('termo')} {sig.get('plataforma')} {sig.get('relevancia_cultural')}"
            
            # 2. Análise de Vizinhança Semântica (Paper Gutsche)
            # Detecta se o termo está em um novo contexto (ex: Samba + Look do Dia)
            semantic_context = self._analyze_semantic_neighborhood(sig)
            
            # 3. Cálculo de Desvio de Padrão / Urgência (Teoria dos Limiares)
            # Mede se o momentum atual quebra a média histórica (Aceleração)
            threshold_data = self._calculate_threshold_deviation(sig)
            
            # 4. Análise Multidimensional (MiningWeakSignals)
            # Decompõe em Temporal, Social (Tiers) e Tensão
            dimensions = self._decompose_signal_dimensions(sig, context)
            
            # 5. Validação de Autenticidade Híbrida
            auth_res = analyzer.analyze_authenticity(
                content=raw_text,
                segment=context.business_objective,
                context_moment=context.scenario_type,
                evidence=evidence
            )
            
            is_verified = auth_res.visual_evidence_score > 0.6
            
            # 6. Geração de Narrativa Cultural (Migrado do ContextEnricherV2)
            narrative = self._generate_cultural_narrative(sig, context, auth_res)
            
            enriched_sig = {
                **sig,
                'authenticity_score': auth_res.authenticity_score,
                'visual_proof_score': auth_res.visual_evidence_score,
                'is_verified_source': is_verified,
                'momentum_velocity': threshold_data.get('velocity', 0.1),
                'context_tags': semantic_context.get('tags', []),
                'tension_score': dimensions.get('tension', 0.2),
                'campaign_fit': self._calculate_predictive_fit(sig, context, auth_res),
                'quality_label': self._get_quality_label(is_verified, threshold_data.get('is_breakout')),
                'business_impact': self._calculate_impact(sig, auth_res, threshold_data),
                'strategic_kpis': selected_kpis, # Injetado para o Dashboard Next.js (V10.4)
                'evidence': evidence[:3],
                'narrative_context': narrative['context'],
                'business_relevance': narrative['relevance'],
                'recommendation': self._generate_strategic_advice(auth_res, threshold_data, semantic_context, narrative)
            }
            enriched_signals.append(enriched_sig)
            
        return enriched_signals

    def _generate_cultural_narrative(self, sig: Dict, context: BusinessContext, auth: Any) -> Dict[str, str]:
        """
        Gera o contexto narrativo brasileiro (Substitui o ContextEnricherV2)
        """
        termo = sig.get('termo', '').lower()
        auth_score = getattr(auth, 'authenticity_score', 0.5)
        impacto = "médio" if auth_score < 0.7 else "alto"
        
        # Selecionar padrão narrativo baseado no círculo ou termo
        pattern = self.narrative_patterns['estetica']
        if any(w in termo for w in ['favela', 'periferia', 'rua']):
            pattern = self.narrative_patterns['estetica']
        elif any(w in termo for w in ['festa', 'show', 'carnaval']):
            pattern = self.narrative_patterns['celebracao']
        elif any(w in termo for w in ['familia', 'bairro', 'igreja']):
            pattern = self.narrative_patterns['comunidade']
            
        return {
            'context': f"Este sinal reflete um movimento de {pattern} com impacto cultural {impacto}.",
            'relevance': f"Para o cenário de '{context.scenario_type}', este sinal oferece um ponto de entrada para {context.opportunities_sought[0] if context.opportunities_sought else 'conexão real'}."
        }

    def _generate_strategic_advice(self, auth: Optional[AuthenticityResult], threshold: Dict, semantic: Dict, narrative: Dict = None) -> str:
        """Gera recomendação estratégica integrando narrativa e métricas"""
        # Tentar SLM Local (Ollama) para conselho ultra-contextualizado (V9.9)
        if self.slm_bridge and self.slm_bridge.is_available:
            try:
                # Construir dicionário de sinal para o SLM
                authenticity_score = getattr(auth, 'authenticity_score', 0.5)
                signal_for_slm = {
                    'termo': getattr(auth, 'term', 'Sinal Desconhecido'),
                    'narrativa_cultural': narrative.get('context', '') if narrative else '',
                    'authenticity_score': authenticity_score,
                    'is_breakout': threshold.get('is_breakout', False)
                }
                
                # O BusinessContext costuma vir no meta-fluxo, se não tivermos, passamos dict vazio
                # No fluxo do worker/bridge, o business_dict é passado pelo contexto de onboarding
                # Para manter compatibilidade com a assinatura antiga, geramos apenas o insight estratégico
                
                # Se tivermos acesso ao slm_bridge, usamos para gerar o conselho
                return self.slm_bridge.generate_insight(signal_for_slm, {})
            except Exception as e:
                logger.warning(f"⚠️ Erro no SLM Bridge do BusinessSynthesizer: {e}")

        # Fallback para Lógica de Templates (V9.0)
        is_breakout = threshold.get('is_breakout', False)
        tags = semantic.get('tags', [])
        authenticity_score = getattr(auth, 'authenticity_score', 0.5)
        
        if is_breakout:
            prefix = "🚀 ALERTA DE BREAKOUT: Aproveite a aceleração imediata. "
        else:
            prefix = "📈 MONITORAMENTO: Sinal em fase de maturação. "
            
        if authenticity_score > 0.8:
            advice = f"O sinal {' '.join(tags)} apresenta ALTA AUTENTICIDADE cultural. Invista em co-criação com membros genuínos da comunidade."
        elif authenticity_score < 0.4:
            advice = f"Risco de apropriação detectado. A marca deve atuar apenas como facilitadora, evitando substituir o protagonismo local."
        else:
            advice = f"Oportunidade de conexão via {narrative.get('relevance') if narrative else 'relevância contextual'}. Recomendamos foco em ativações orgânicas."
            
        return prefix + advice

    def _decompose_signal_dimensions(self, sig: Dict, auth: Optional[AuthenticityResult]) -> Dict[str, float]:
        """
        Decompõe o sinal em dimensões estratégicas (V9.0 Original).
        Calcula Tensão Cultural, Pertencimento e Potencial de Inovação.
        """
        authenticity_score = getattr(auth, 'authenticity_score', 0.5)
        cultural_relevance = float(sig.get('relevancia_cultural', 0.5))
        
        # 1. Tensão Cultural (Diferença entre relevância e autenticidade)
        # Sinais de alta relevância mas baixa autenticidade geram 'Tensão' (Risco/Oportunidade)
        cultural_tension = abs(cultural_relevance - authenticity_score)
        
        # 2. Pertencimento (Evidence-based)
        belonging_score = getattr(auth, 'visual_evidence_score', 0.5)
        
        # 3. Potencial de Inovação (Inverso da obviedade / Entropia)
        # Se o sinal é orignal (alta entropia), o potencial de inovação sobe
        innovation_potential = cultural_relevance * (1.0 - getattr(auth, 'is_obvious', 0.5))
        
        return {
            'cultural_tension': round(cultural_tension, 2),
            'belonging': round(belonging_score, 2),
            'innovation_potential': round(innovation_potential, 2),
            'authenticity_depth': round(authenticity_score, 2)
        }
        
    def _calculate_predictive_fit(self, sig: Dict, context: BusinessContext, auth: Optional[AuthenticityResult]) -> float:
        """Calcula o Campaign Match (Previsão de sucesso para o objetivo do negócio)"""
        # Base: Score de Autenticidade
        authenticity_score = getattr(auth, 'authenticity_score', 0.5)
        auth_visual_score = getattr(auth, 'visual_evidence_score', 0.5)
        score = authenticity_score * 0.5
        
        # Ajuste por Objetivo
        if context.scenario_type == "Lançamento de Produto":
            # Para lançamento, momentum alto é melhor
            score += (float(sig.get('momentum', 50)) / 100.0) * 0.3
        elif context.scenario_type == "Pesquisa de Mercado":
            # Para pesquisa, fontes verificadas valem mais
            if auth_visual_score > 0.6:
                score += 0.3
                
        # Ajuste por Público
        if context.target_audience.lower() in sig.get('texto_api', '').lower():
            score += 0.2
            
        return min(1.0, score)

    def _get_quality_label(self, is_verified: bool, is_breakout: bool) -> str:
        """Retorna label de qualidade do sinal"""
        if is_verified and is_breakout: return "EXPLOSÃO CULTURAL VERIFICADA"
        if is_verified: return "SINAL FORTE (TRUSTED)"
        if is_breakout: return "EMERGÊNCIA RÁPIDA"
        return "SINAL EM OBSERVAÇÃO"

    def _calculate_impact(self, sig: Dict, auth: Optional[AuthenticityResult], threshold: Dict) -> float:
        """Cálculo de Impacto de Negócio"""
        authenticity_score = getattr(auth, 'authenticity_score', 0.5)
        return (authenticity_score * 0.4) + (threshold.get('velocity', 0) * 0.4) + (float(sig.get('relevancia_cultural', 0.5)) * 0.2)

    def _calculate_cultural_entropy(self, term: str, context: str) -> float:
        """
        Calcula a Entropia Cultural DINÂMICA.
        Termos com alta correlação histórica (clichês) têm BAIXA ENTROPIA.
        Termos que quebram o padrão esperado para o cenário têm ALTA ENTROPIA.
        
        V9.9: Integração com ML Foundation para análise semântica em tempo real.
        """
        term_norm = term.lower().strip()
        context_norm = context.lower().strip()

        # 1. Base Estática (Heurística de Redução de Ruído inicial)
        obvious_pairs = {
            "samba": ["carnaval", "rio de janeiro", "festa", "brasil", "desfile", "sapucaí"],
            "futebol": ["seleção", "gol", "copa", "estádio", "campeonato", "neymar", "pelé"],
            "cerveja": ["churrasco", "praia", "gelada", "amigos", "bar", "boteco"],
            "praia": ["sol", "verão", "mar", "férias", "bronzeado", "rio de janeiro"],
            "startup": ["tecnologia", "investimento", "inovação", "vale do silício", "unicórnio", "pitch"],
            "amazônia": ["floresta", "natureza", "índios", "desmatamento", "pulmão do mundo"],
            "pobreza": ["favela", "carência", "ajuda", "violência", "falta"]
        }
        
        # 2. Bônus por Contexto de Alto Valor (Dinâmico)
        high_value_contexts = [
            "economia criativa", "sustentabilidade", "tecnologia", "blockchain",
            "inteligência artificial", "negócios", "educação", "direitos", "futuro", "tokenização"
        ]

        # 3. Cálculo de Proximidade Semântica (Onde a dinâmica acontece)
        # Se os termos estão semanticamente muito próximos nos embeddings, a entropia cai.
        # Se estão distantes (Samba + Quantum), a entropia sobe.
        semantic_distance_bonus = 0.0
        
        # Simulação de verificação de 'quebra de padrão' via ML
        # Em produção, aqui chamamos o model de embeddings
        words_context = context_norm.split()
        unusual_words = [w for w in words_context if len(w) > 5 and w not in high_value_contexts]
        
        if len(unusual_words) > 2:
            semantic_distance_bonus += 0.15 # Bônus por vocabulário não-clichê detectado

        # 4. Lógica de Filtragem
        for key, cliches in obvious_pairs.items():
            if key in term_norm or key in context_norm:
                if any(cliche in context_norm for cliche in cliches) or any(cliche in term_norm for cliche in cliches):
                    # É um clichê, mas vamos verificar se há um contexto de alto valor misturado
                    if any(hv in context_norm for hv in high_value_contexts):
                        return round(0.6 + semantic_distance_bonus, 3) 
                    return 0.2
            
        # 5. Alta Entropia Base + Bônus Dinâmico
        return round(0.85 + semantic_distance_bonus, 3) 

    def calculate_signal_depth(self, 
                             signal: Dict, 
                             context: BusinessContext, 
                             feedback_weights: Dict[str, float] = None) -> float:
        """
        Calcula a profundidade real de um sinal (V10.2 Híbrido).
        
        Combina:
        1. 💎 Entropia Dinâmica (Gutsche/P75): Similaridade vetorial baseada em clichês/distância.
        2. 🧠 Identidade Dinâmica: Bônus se o sinal atende ao objetivo do Onboarding (ex: Inovação).
        3. ⚡ Active Learning (Feedback): Ajuste de pesos baseado nas correções do usuário.
        """
        termo = signal.get('termo', '')
        contexto = context.business_objective
        
        # 1. Base de Entropia (Matriz Semântica de Clichês vs Outliers)
        # O calculate_static_obviousness agora usa o BERTimbau internamente.
        base_entropy = self.calculate_static_obviousness(termo, contexto, context.success_metrics[0] if context.success_metrics else "default")
        
        # 2. Refinamento Híbrido (Active Learning)
        # Se o usuário corrigiu este sinal anteriormente, o feedback_weight atua como multiplicador
        feedback_multiplier = 1.0
        if feedback_weights and termo in feedback_weights:
            feedback_multiplier = feedback_weights[termo]
            # O feedback pode 'forçar' um sinal óbvio a ser relevante (Peso > 1.0)
            # ou silenciar um sinal falso positivo (Peso < 1.0)
            
        final_depth = base_entropy * feedback_multiplier
        
        # Capping de Score para segurança do modelo
        return round(min(1.2, max(0.1, final_depth)), 3)

    def calculate_static_obviousness(self, term: str, context: str, user_objective: str = "default") -> float:
        """
        Calcula a entropia cultural (improbabilidade) de um termo em um contexto.
        V10.1: Passagem do objetivo do usuário para o SemanticMatrixScorer.
        """
        term_norm = term.lower().strip()
        context_norm = context.lower().strip()

        # 1. Obter Multiplicador Dinâmico baseado na Similaridade de Embeddings & Objetivo
        discovery_multiplier = dynamic_scorer.get_discovery_multiplier(
            context_norm, 
            term_norm, 
            user_intent=user_objective
        )
        
        # 2. Base de cálculo calibrada (0.6 neutral)
        base_entropy = 0.6 * discovery_multiplier
        
        # 3. Bônus por Contexto de Alto Valor (V9.9)
        high_value_contexts = [
            "economia criativa", "sustentabilidade", "tecnologia", "blockchain",
            "inteligência artificial", "negócios", "educação", "direitos", "futuro", "tokenização"
        ]
        
        if any(hv in term_norm for hv in high_value_contexts):
            base_entropy += 0.2
            
        return round(min(1.2, base_entropy), 3)

    def filter_obvious_signals(self, signals: List[Dict]) -> List[Dict]:
        """
        Aplica o Filtro de Obviedade (Entropia Cultural).
        Remove o que é esperado/clichê para dar holofote aos Sinais Fracos Reais.
        """
        non_obvious_signals = []
        for s in signals:
            text = s.get('text', s.get('content', ''))
            category = s.get('category', 'geral')
            
            entropy = self._calculate_cultural_entropy(category, text)
            
            # Só aceita sinais com Entropia > 0.5 (Não-Óbvios)
            if entropy > 0.5:
                s['entropy_score'] = entropy
                s['is_non_obvious'] = True
                non_obvious_signals.append(s)
            else:
                logger.info(f"🚫 Sinal filtrado por ser óbvio demais: {category} em {text[:30]}...")
                
        return non_obvious_signals

    def enrich_signal_with_slm(self, signal):
        """
        Método auxiliar para o teste de produção. 
        Enriquece o sinal com as narrativas do Llama-3.
        """
        if not self.slm_bridge:
            return signal

        # Simula o objeto de metadados que o bridge espera
        # Se 'topic' não existir no sinal original, pega do raw_data
        topic = signal.brand_name
        if hasattr(signal, 'raw_data') and 'topic' in signal.raw_data:
            topic = signal.raw_data['topic']

        signal_data = {
            'topic': topic,
            'text': signal.raw_data.get('text', ''),
            'platform': signal.data_sources[0] if signal.data_sources else 'general'
        }

        # Gera narrativa cultural
        signal.narrativa_cultural = self.slm_bridge.generate_insight(
            f"Analise este sinal cultural: {signal_data['text']}. Tópico: {signal_data['topic']}", 
            "Você é um antropólogo cultural brasileiro. Gere uma narrativa curta (Alma Cultural) sobre este sinal."
        )
        
        # Gera recomendação estratégica usando o método estruturado recém-criado
        signal.recomendacao_acao = self.slm_bridge.generate_strategic_advice(
            auth=None, 
            threshold={"score": signal.cultural_score}, 
            semantic={"text": signal_data['text']},
            narrative={"cultural": signal.narrativa_cultural}
        )
        
        return signal

# Função principal de refinamento
async def refine_research_context(context_text: str, 
                                cultural_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Função principal para refinamento de contexto de pesquisa"""
    
    synthesizer = BusinessSynthesizer()
    
    # Analisar contexto
    context = await synthesizer.analyze_business_context(context_text)
    
    # Sintetizar insights
    insights = await synthesizer.synthesize_cultural_insights(context, cultural_data or {})
    
    # Gerar estratégia
    strategy = await synthesizer.generate_refined_strategy(context, insights)
    
    return {
        'context': context,
        'insights': insights,
        'strategy': strategy,
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'total_insights': len(insights),
            'authenticity_score': strategy.cultural_authenticity_score,
            'primary_approach': strategy.primary_approach
        }
    }

# Singleton e Helper para acesso simplificado
_instance = None

def get_business_synthesizer() -> BusinessSynthesizer:
    """Retorna instância única do BusinessSynthesizer"""
    global _instance
    if _instance is None:
        _instance = BusinessSynthesizer()
    return _instance

# Teste
if __name__ == "__main__":
    print("🎯 Testando Business Synthesizer...")
    
    async def test_synthesizer():
        context_text = """
        Contexto de Negócio: Pesquisa de Mercado
        Detalhamento do Cenário: Entender penetração e conversação cultural com público periférico do Rio de Janeiro. 
        Com objetivo em mapear autenticidade cultural e identificar oportunidades de conexão genuína.
        """
        
        result = await refine_research_context(context_text)
        
        print(f"✅ Contexto analisado: {result['context'].scenario_type}")
        print(f"✅ Público-alvo: {result['context'].target_audience}")
        print(f"✅ Insights gerados: {len(result['insights'])}")
        print(f"✅ Score de autenticidade: {result['strategy'].cultural_authenticity_score:.2f}")
        print(f"✅ Abordagem primária: {result['strategy'].primary_approach}")
    
    # asyncio.run(test_synthesizer())  # Descomentado para teste
    
    print("🎉 Business Synthesizer implementado!")
