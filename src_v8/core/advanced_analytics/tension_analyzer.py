"""
TENSION ANALYZER - DIMENSÃO 3
==============================

Analisa tensões culturais contextualizadas aos sinais.
Conecta círculos culturais em conflito ou sinergia.

Baseado na análise de relacionamentos culturais do dashboard v11.

Author: Culture Pulse V9
Date: 2026-02-03
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional
import logging

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import direto do dataclass
import importlib.util
models_path = PROJECT_ROOT / "core" / "models" / "enriched_signal.py"
spec = importlib.util.spec_from_file_location("enriched_signal", models_path)
enriched_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(enriched_module)
ContextualizedTension = enriched_module.ContextualizedTension

logger = logging.getLogger(__name__)


class TensionAnalyzer:
    """
    TENSION ANALYZER - DIMENSÃO 3 DE CONTEXTUALIZAÇÃO
    
    Analisa tensões culturais entre os 16 círculos culturais:
    
    TIPOS DE TENSÃO:
    1. Sinergia Natural: Círculos que se reforçam mutuamente (>0.8)
    2. Amplificação Mútua: Círculos que se potencializam (0.7-0.8)
    3. Tensão Criativa: Conflito produtivo que gera inovação (0.6-0.7)
    4. Conflito Ativo: Tensão forte que requer resolução (0.5-0.6)
    5. Evolução Necessária: Mudança estrutural em curso (<0.5)
    """
    
    # Relacionamentos culturais pré-mapeados (expandível)
    CULTURAL_RELATIONSHIPS = [
        {
            "circle_1": "Família & Tradições",
            "circle_2": "Gastronomia & Sabores",
            "strength": 0.92,
            "type": "Sinergia Natural",
            "description": "Forte conexão entre valores familiares e tradições gastronômicas brasileiras",
            "opportunity": "Campanhas que conectam sabores com memórias familiares têm alto potencial emocional",
            "risk": None
        },
        {
            "circle_1": "Tecnologia & Digital",
            "circle_2": "Relacionamentos & Afeto",
            "strength": 0.73,
            "type": "Tensão Criativa",
            "description": "Tecnologia facilita conexões mas também pode distanciar pessoas fisicamente",
            "opportunity": "Tecnologias que aproximam pessoas fisicamente podem resolver essa tensão",
            "risk": "Dependência excessiva de digital pode alienar públicos mais tradicionais"
        },
        {
            "circle_1": "Sustentabilidade & Consumo",
            "circle_2": "Status & Reconhecimento",
            "strength": 0.68,
            "type": "Conflito Ativo",
            "description": "Tensão entre consumo consciente e desejo de status através de bens materiais",
            "opportunity": "Status através de sustentabilidade pode resolver esse conflito",
            "risk": "Marcas de luxo podem ser rejeitadas por não serem sustentáveis"
        },
        {
            "circle_1": "Música & Festivais",
            "circle_2": "Comunidade & Vizinhança",
            "strength": 0.87,
            "type": "Amplificação Mútua",
            "description": "Música e festivais fortalecem senso de comunidade e identidade local",
            "opportunity": "Eventos musicais comunitários podem fortalecer laços locais e com a marca",
            "risk": None
        },
        {
            "circle_1": "Trabalho & Prosperidade",
            "circle_2": "Diversidade & Inclusão",
            "strength": 0.61,
            "type": "Evolução Necessária",
            "description": "Crescente consciência de que prosperidade deve incluir diversidade",
            "opportunity": "Liderança em diversidade no trabalho pode atrair talentos e consumidores conscientes",
            "risk": "Falta de diversidade pode limitar crescimento em mercados jovens"
        },
        {
            "circle_1": "Saúde & Bem-estar",
            "circle_2": "Tecnologia & Digital",
            "strength": 0.75,
            "type": "Amplificação Mútua",
            "description": "Tecnologia amplifica práticas de saúde (apps fitness, telemedicina)",
            "opportunity": "Soluções digitais de bem-estar têm alta aceitação",
            "risk": "Excesso de telas pode prejudicar saúde mental"
        },
        {
            "circle_1": "Arte & Criatividade",
            "circle_2": "Tecnologia & Digital",
            "strength": 0.81,
            "type": "Amplificação Mútua",
            "description": "Tecnologia democratiza criação e distribuição artística",
            "opportunity": "Plataformas digitais criam novos modelos de monetização para artistas",
            "risk": "IA generativa pode ameaçar artistas tradicionais"
        },
        {
            "circle_1": "Educação & Conhecimento",
            "circle_2": "Tecnologia & Digital",
            "strength": 0.85,
            "type": "Amplificação Mútua",
            "description": "Tecnologia transforma acesso e metodologias educacionais",
            "opportunity": "EdTech tem potencial disruptivo no Brasil",
            "risk": "Exclusão digital limita acesso à educação de qualidade"
        },
        {
            "circle_1": "Sustentabilidade & Consumo",
            "circle_2": "Comunidade & Vizinhança",
            "strength": 0.78,
            "type": "Tensão Criativa",
            "description": "Consumo local e economia circular fortalecem comunidades",
            "opportunity": "Marcas que conectam sustentabilidade com impacto local ganham relevância",
            "risk": None
        },
        {
            "circle_1": "Espiritualidade & Fé",
            "circle_2": "Saúde & Bem-estar",
            "strength": 0.72,
            "type": "Tensão Criativa",
            "description": "Práticas espirituais integradas com bem-estar holístico",
            "opportunity": "Mindfulness e meditação conectam os dois círculos",
            "risk": "Comercialização excessiva pode esvaziar sentido espiritual"
        },
        {
            "circle_1": "Ambições & Sonhos",
            "circle_2": "Trabalho & Prosperidade",
            "strength": 0.89,
            "type": "Sinergia Natural",
            "description": "Ambições pessoais impulsionam trabalho e construção de prosperidade",
            "opportunity": "Narrativas de realização profissional têm forte apelo",
            "risk": None
        },
        {
            "circle_1": "Diversidade & Inclusão",
            "circle_2": "Arte & Criatividade",
            "strength": 0.83,
            "type": "Amplificação Mútua",
            "description": "Diversidade enriquece expressão artística e criatividade",
            "opportunity": "Representatividade na arte gera conexão emocional forte",
            "risk": None
        }
    ]
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa TensionAnalyzer
        
        Args:
            config: Configurações opcionais
        """
        self.config = config or {}
        self.relationships = self.CULTURAL_RELATIONSHIPS.copy()
        self.logger = logging.getLogger(__name__)
        
        logger.info(f"✅ TensionAnalyzer inicializado - {len(self.relationships)} relacionamentos mapeados")
    
    def get_contextualized_tensions(
        self,
        termo: str,
        dominant_circle: Optional[str] = None,
        top_k: int = 3
    ) -> List[ContextualizedTension]:
        """
        Retorna tensões contextualizadas ao termo/círculo
        
        Args:
            termo: Termo do sinal cultural
            dominant_circle: Círculo cultural dominante
            top_k: Número de tensões a retornar
        
        Returns:
            Lista de ContextualizedTension
        """
        if not dominant_circle:
            # Sem círculo, retorna tensões gerais mais fortes
            return self._get_top_tensions(top_k)
        
        # Busca tensões relacionadas ao círculo dominante
        related_tensions = []
        
        for rel in self.relationships:
            if rel["circle_1"] == dominant_circle or rel["circle_2"] == dominant_circle:
                tension = ContextualizedTension(
                    circle_1=rel["circle_1"],
                    circle_2=rel["circle_2"],
                    strength=rel["strength"],
                    type=rel["type"],
                    description=rel["description"],
                    opportunity=rel.get("opportunity"),
                    risk=rel.get("risk")
                )
                related_tensions.append(tension)
        
        # Ordena por força e retorna top-K
        related_tensions.sort(key=lambda t: t.strength, reverse=True)
        return related_tensions[:top_k]
    
    def _get_top_tensions(self, top_k: int) -> List[ContextualizedTension]:
        """
        Retorna top tensões gerais (sem contexto específico)
        
        Args:
            top_k: Número de tensões
        
        Returns:
            Lista de ContextualizedTension
        """
        # Ordena por força
        sorted_rels = sorted(self.relationships, key=lambda r: r["strength"], reverse=True)
        
        tensions = []
        for rel in sorted_rels[:top_k]:
            tension = ContextualizedTension(
                circle_1=rel["circle_1"],
                circle_2=rel["circle_2"],
                strength=rel["strength"],
                type=rel["type"],
                description=rel["description"],
                opportunity=rel.get("opportunity"),
                risk=rel.get("risk")
            )
            tensions.append(tension)
        
        return tensions
    
    def get_tensions_by_type(self, tension_type: str) -> List[ContextualizedTension]:
        """
        Filtra tensões por tipo
        
        Args:
            tension_type: "Sinergia Natural", "Tensão Criativa", etc.
        
        Returns:
            Lista de tensões do tipo especificado
        """
        filtered = [
            ContextualizedTension(
                circle_1=rel["circle_1"],
                circle_2=rel["circle_2"],
                strength=rel["strength"],
                type=rel["type"],
                description=rel["description"],
                opportunity=rel.get("opportunity"),
                risk=rel.get("risk")
            )
            for rel in self.relationships
            if rel["type"] == tension_type
        ]
        
        return filtered
    
    def add_custom_relationship(self, relationship: Dict):
        """
        Adiciona relacionamento customizado
        
        Args:
            relationship: Dict com circle_1, circle_2, strength, type, description
        """
        self.relationships.append(relationship)
        self.logger.info(f"➕ Adicionado relacionamento: {relationship['circle_1']} <-> {relationship['circle_2']}")
    
    def analyze_circle_ecosystem(self, circle: str) -> Dict:
        """
        Analisa ecossistema completo de um círculo
        
        Args:
            circle: Nome do círculo cultural
        
        Returns:
            Dict com análise de relacionamentos
        """
        synergies = []
        conflicts = []
        creative_tensions = []
        
        for rel in self.relationships:
            if rel["circle_1"] == circle or rel["circle_2"] == circle:
                other_circle = rel["circle_2"] if rel["circle_1"] == circle else rel["circle_1"]
                
                if rel["strength"] >= 0.8:
                    synergies.append((other_circle, rel["strength"]))
                elif rel["strength"] >= 0.7:
                    creative_tensions.append((other_circle, rel["strength"]))
                else:
                    conflicts.append((other_circle, rel["strength"]))
        
        return {
            "circle": circle,
            "synergies": sorted(synergies, key=lambda x: x[1], reverse=True),
            "creative_tensions": sorted(creative_tensions, key=lambda x: x[1], reverse=True),
            "conflicts": sorted(conflicts, key=lambda x: x[1], reverse=True),
            "total_connections": len(synergies) + len(creative_tensions) + len(conflicts)
        }


# ========== STANDALONE TESTING ==========

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 Testando TensionAnalyzer...")
    
    analyzer = TensionAnalyzer()
    
    # Teste 1: Tensões contextualizadas
    print("\n📍 Tensões para 'Sustentabilidade & Consumo':")
    tensions = analyzer.get_contextualized_tensions(
        termo="sustentabilidade afetiva",
        dominant_circle="Sustentabilidade & Consumo",
        top_k=3
    )
    
    for i, tension in enumerate(tensions, 1):
        print(f"\n   {i}. {tension.circle_1} <-> {tension.circle_2}")
        print(f"      Tipo: {tension.type} (força: {tension.strength:.2f})")
        print(f"      {tension.description[:80]}...")
        if tension.opportunity:
            print(f"      💡 Oportunidade: {tension.opportunity[:60]}...")
    
    # Teste 2: Tensões por tipo
    print("\n📍 Todas as 'Sinergias Naturais':")
    synergies = analyzer.get_tensions_by_type("Sinergia Natural")
    for syn in synergies:
        print(f"   - {syn.circle_1} + {syn.circle_2} ({syn.strength:.2f})")
    
    # Teste 3: Ecossistema de um círculo
    print("\n📍 Ecossistema de 'Tecnologia & Digital':")
    ecosystem = analyzer.analyze_circle_ecosystem("Tecnologia & Digital")
    print(f"   Sinergias: {len(ecosystem['synergies'])}")
    print(f"   Tensões Criativas: {len(ecosystem['creative_tensions'])}")
    print(f"   Conflitos: {len(ecosystem['conflicts'])}")
    print(f"   Total conexões: {ecosystem['total_connections']}")
