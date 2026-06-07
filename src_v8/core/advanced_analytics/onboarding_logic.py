"""
ONBOARDING HELPER MODULE - Culture Pulse V9.0
Provides onboarding-related constants and profile utilities for backend integration.
"""

from __future__ import annotations
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

SEGMENTOS = [
    "Alimentação & Bebidas",
    "Entretenimento & Mídia",
    "Tecnologia & Inovação",
    "Moda & Beleza",
    "Educação & Cultura",
    "Esportes & Fitness",
    "Varejo & E-commerce",
    "Turismo & Hospitalidade",
    "Saúde & Bem-estar",
    "Finanças & Investimentos",
    "Imóveis & Construção",
    "Automotivo & Mobilidade",
    "Outro"
]

OBJETIVOS = [
    "Pesquisa de Mercado",
    "Lançamento de Produto",
    "Rebranding / Reposicionamento",
    "Análise de Concorrência",
    "Monitoramento de Crise",
    "Identificação de Tendências",
    "Expansão Geográfica",
    "Público-Alvo Emergente",
    "Outro"
]

AUDIENCIAS = [
    "Famílias (25-44 anos)",
    "Jovens Adultos (18-24 anos)",
    "Profissionais (30-50 anos)",
    "Idosos (60+ anos)",
    "Crianças & Adolescentes",
    "Classe A/B",
    "Classe C/D",
    "Zona Urbana",
    "Zona Rural",
    "LGBTQIA+",
    "Empreendedores",
    "Estudantes Universitários"
]

FONTES = [
    "YouTube",
    "Reddit",
    "Spotify",
    "NewsAPI",
    "Google Trends",
    "Instagram",
    "Meetup",
    "Eventbrite"
]

CIRCULOS_CULTURAIS = [
    "🎵 Música & Ritmos",
    "⚽ Esportes & Torcidas",
    "🍖 Gastronomia Regional",
    "🎭 Arte & Cultura Popular",
    "🎉 Festividades & Celebrações",
    "🌿 Natureza & Regionalismo",
    "📱 Digital & Inovação",
    "🏛️ História & Patrimônio",
    "🗣️ Dialetos & Linguagem",
    "👥 Movimentos Sociais",
    "🎓 Educação & Conhecimento",
    "💼 Trabalho & Empreendedorismo",
    "🏡 Família & Comunidade",
    "🎨 Moda & Estética",
    "🍃 Sustentabilidade",
    "⚡ Energia & Transformação"
]

KEYWORDS_TEMPLATES = {
    "Alimentação & Bebidas": ["street food", "churrasco", "vegano", "delivery", "food truck"],
    "Entretenimento & Mídia": ["streaming", "podcast", "série", "show", "festival"],
    "Tecnologia & Inovação": ["IA", "blockchain", "startup", "app", "fintech"],
    "Moda & Beleza": ["streetwear", "sustentável", "skincare", "make", "thrift"],
    "Esportes & Fitness": ["crossfit", "yoga", "corrida", "futebol", "bike"],
    "Educação & Cultura": ["edtech", "curso online", "livro", "literatura", "arte"],
    "Varejo & E-commerce": ["marketplace", "D2C", "omnichannel", "live commerce", "social commerce"],
    "Turismo & Hospitalidade": ["turismo sustentável", "ecoturismo", "Airbnb", "roteiro Brasil"],
    "Saúde & Bem-estar": ["telemedicina", "saúde mental", "fitoterapia", "autocuidado"],
    "Finanças & Investimentos": ["criptomoeda", "educação financeira", "open banking", "PIX"],
    "Imóveis & Construção": ["construção sustentável", "retrofit", "co-living", "smart city"],
    "Automotivo & Mobilidade": ["carro elétrico", "mobilidade urbana", "bicicleta", "carsharing"],
    "Outro": ["tendência", "inovação", "cultura brasileira", "comportamento"]
}


def get_user_keywords(profile: Optional[Dict[str, Any]] = None) -> List[str]:
    """Return a list of keywords for the profile or an empty list."""
    if not profile:
        return []
    keywords = profile.get('keywords', []) or []
    if not keywords and profile.get('brand_topic'):
        brand_words = [w.strip() for w in profile['brand_topic'].split() if len(w) > 3]
        keywords = brand_words
    return keywords


def get_user_sources(profile: Optional[Dict[str, Any]] = None) -> List[str]:
    """Return the configured data sources for a profile."""
    if not profile:
        return FONTES
    return profile.get('fontes', FONTES)


def get_analysis_period(profile: Optional[Dict[str, Any]] = None) -> int:
    """Return the analysis period in days for a profile."""
    if not profile:
        return 30
    return profile.get('periodo_dias', 30)


def export_profile_json(profile: Dict[str, Any]) -> str:
    """Export profile data as a JSON string."""
    return json.dumps(profile, indent=2, ensure_ascii=False)


def import_profile_json(json_string: str) -> Optional[dict]:
    """Import a profile JSON string and validate required fields."""
    try:
        profile = json.loads(json_string)
        required_fields = ['brand_topic', 'segmento', 'objetivo']
        if all(field in profile for field in required_fields):
            return profile
        return None
    except json.JSONDecodeError:
        return None
