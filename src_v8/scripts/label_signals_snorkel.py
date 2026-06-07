#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S2.1 Snorkel Labeling Functions v2 (7 familias de heuristicas)

Arquitetura:
  FAMILIA A - Circulo canonico  (16 LFs) : slug match + dicionario tfidf_analyzer
  FAMILIA B - Alma Brasileira   ( 7 LFs) : keywords + expressoes alma_brasileira.py
  FAMILIA C - Tensao Cultural   ( 5 LFs) : 12 relationships + contexto/dor/emocao/mencoes
  FAMILIA D - Momentum Cultural ( 4 LFs) : score numerico + faixas + tendencia
  FAMILIA E - Plataforma*Circulo( 4 LFs) : afinidade plataforma->circulo
  FAMILIA F - Regional          ( 3 LFs) : expressoes regionais -> circulo provavel
  FAMILIA G - Qualidade / Guard ( 2 LFs) : filtros negativos (teste, lixo)
  TOTAL: 41 LFs

Uso:
    python scripts/label_signals_snorkel.py [--dry-run] [--min-confidence 0.6]
"""
from __future__ import annotations

import argparse
import json
import sys
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set

import numpy as np
import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://wsizqmnnicpgblopmxyv.supabase.co")
SUPABASE_KEY = os.getenv(
    "SUPABASE_SERVICE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndzaXpxbW5uaWNwZ2Jsb3BteHl2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MTQ0MDExNiwiZXhwIjoyMDg3MDE2MTE2fQ"
    ".ca8oGhfR1Ek7t5n9fmCS3O5UaaCBUhqRAIJtavc5QpE",
)
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ---------------------------------------------------------------------------
# LABEL SCHEMA
# ---------------------------------------------------------------------------
ABSTAIN = -1
LABEL_MAP = {
    0: "MUSICA", 1: "GASTRONOMIA", 2: "MODA", 3: "ESPORTE",
    4: "TECNOLOGIA", 5: "ARTE_CULTURA", 6: "RELIGIAO", 7: "POLITICA",
    8: "NATUREZA", 9: "JUVENTUDE", 10: "FAMILIA", 11: "TRABALHO",
    12: "SAUDE", 13: "EDUCACAO", 14: "SEXUALIDADE", 15: "DIVERSIDADE",
}
LABEL_NAMES = list(LABEL_MAP.values())
N_CLASSES = len(LABEL_MAP)
LABEL_FROM_NAME: Dict[str, int] = {v: k for k, v in LABEL_MAP.items()}

# ===========================================================================
# DICIONARIOS IMPORTADOS (proto-LFs do codebase)
# ===========================================================================

# -- core/tfidf_analyzer.py  cultural_terms --------------------------------
TFIDF_CULTURAL_TERMS: Dict[str, List[str]] = {
    "musica": [
        "samba", "forro", "axe", "frevo", "funk", "bossa nova", "mpb",
        "pagode", "reggae", "rap", "hip hop", "rock", "pop", "eletronica",
        "baiao", "xote", "mambo", "lambada", "zouk", "arrocha",
    ],
    "festas": [
        "carnaval", "festa junina", "reveillon", "micareta", "bloco",
        "trio eletrico", "marchinha", "quadrilha", "fogueira", "balao",
        "festa", "celebracao", "comemoracao", "folia", "farra",
    ],
    "culinaria": [
        "feijoada", "churrasco", "brigadeiro", "acai", "coxinha",
        "pastel", "caipirinha", "guarana", "mate", "cafezinho",
        "tapioca", "acaraje", "moqueca", "farofa", "picanha",
    ],
    "esportes": [
        "futebol", "pele", "copa do mundo", "maracana", "flamengo",
        "corinthians", "palmeiras", "santos", "vasco", "sao paulo",
        "surf", "volei", "capoeira", "jiu-jitsu", "futsal",
    ],
    "lugares": [
        "rio de janeiro", "sao paulo", "bahia", "nordeste", "amazonia",
        "pantanal", "cerrado", "mata atlantica", "copacabana", "ipanema",
        "cristo redentor", "pao de acucar", "iguacu", "fernando de noronha",
    ],
    "cultura_popular": [
        "jeitinho brasileiro", "malandragem", "cordialidade", "saudade",
        "ginga", "axe", "energia", "simpatia", "hospitalidade", "calor humano",
        "brasilidade", "tropicalismo", "miscigenacao", "diversidade",
    ],
}

# -- core/alma_brasileira.py  alma_values ----------------------------------
ALMA_VALUES: Dict[str, Dict[str, Any]] = {
    "caloroso_hospitaleiro": {
        "weight": 0.20,
        "keywords": [
            "acolhedor", "caloroso", "hospitaleiro", "receptivo", "amigavel",
            "carinhoso", "gentil", "cordial", "simpatico", "acolhimento",
            "abraco", "beijo", "carinho", "afeto", "amor",
        ],
        "expressions": [
            "seja bem-vindo", "fique a vontade", "como familia",
            "de bracos abertos", "casa aberta", "portas abertas",
        ],
    },
    "alegre_festivo": {
        "weight": 0.18,
        "keywords": [
            "alegre", "feliz", "festivo", "animado", "divertido",
            "festa", "celebracao", "comemoracao", "diversao", "alegria",
            "sorriso", "risada", "gargalhada", "brincadeira", "folia",
        ],
        "expressions": [
            "vamos celebrar", "que festa", "que alegria",
            "hora da festa", "vamos comemorar", "que diversao",
        ],
    },
    "criativo_improvisador": {
        "weight": 0.16,
        "keywords": [
            "criativo", "improvisador", "jeitinho", "gambiarra", "solucao",
            "criatividade", "improviso", "inovacao", "inventivo", "engenhoso",
            "desenrolar", "dar um jeito", "resolver", "adaptar",
        ],
        "expressions": [
            "jeitinho brasileiro", "dar um jeito", "quebrar o galho",
            "gambiarra", "improviso", "na criatividade",
        ],
    },
    "musical_ritmado": {
        "weight": 0.15,
        "keywords": [
            "musical", "ritmado", "dancante", "melodioso", "harmonioso",
            "musica", "ritmo", "danca", "som", "batida",
            "cantoria", "cantiga", "melodia", "harmonia", "compasso",
        ],
        "expressions": [
            "no ritmo", "na batida", "no compasso",
            "musica boa", "som massa", "ritmo gostoso",
        ],
    },
    "resiliente_esperancoso": {
        "weight": 0.14,
        "keywords": [
            "resiliente", "forte", "resistente", "persistente", "determinado",
            "esperanca", "fe", "coragem", "garra", "luta",
            "superar", "vencer", "conquistar", "perseverar", "insistir",
        ],
        "expressions": [
            "nao desistir", "seguir em frente", "ter fe",
            "dias melhores", "vai dar certo", "forca e fe",
        ],
    },
    "emotivo_expressivo": {
        "weight": 0.12,
        "keywords": [
            "emotivo", "expressivo", "sentimental", "apaixonado", "intenso",
            "emocao", "sentimento", "paixao", "coracao", "alma",
            "emocionar", "sentir", "vibrar", "arrepiar", "tocante",
        ],
        "expressions": [
            "do coracao", "com a alma", "de corpo e alma",
            "emocionante", "tocante", "arrepiante",
        ],
    },
    "solidario_comunitario": {
        "weight": 0.05,
        "keywords": [
            "solidario", "unido", "junto", "comunitario", "coletivo",
            "ajuda", "apoio", "uniao", "comunidade", "vizinhanca",
            "mutirao", "conjunto", "parceria", "colaboracao", "cooperacao",
        ],
        "expressions": [
            "juntos somos mais", "mao na massa", "todo mundo junto",
            "uniao faz a forca", "um por todos", "lado a lado",
        ],
    },
}

# -- core/alma_brasileira.py  regional_expressions -------------------------
REGIONAL_EXPRESSIONS: Dict[str, Dict[str, List[str]]] = {
    "Rio de Janeiro": {
        "expressions": ["cara", "vei", "massa", "maneiro", "legal", "show"],
        "cultural_markers": ["carioca", "zona sul", "zona norte", "tijuca", "barra"],
    },
    "Sao Paulo": {
        "expressions": ["mano", "cara", "meu", "bagulho", "parada", "trem"],
        "cultural_markers": ["paulista", "paulistano", "centro", "periferia", "quebrada"],
    },
    "Nordeste": {
        "expressions": ["oxe", "eita", "vixe", "arretado", "massa", "bom demais"],
        "cultural_markers": ["nordestino", "sertao", "litoral", "caatinga", "forro"],
    },
    "Sul": {
        "expressions": ["tche", "bah", "guri", "guria", "pia", "barbada"],
        "cultural_markers": ["gaucho", "catarinense", "paranaense", "sul", "pampa"],
    },
    "Minas Gerais": {
        "expressions": ["uai", "trem", "so", "ne nao", "sei la", "ta bom"],
        "cultural_markers": ["mineiro", "belo horizonte", "interior", "montanha"],
    },
}

# -- core/tension_analyzer.py  CULTURAL_RELATIONSHIPS (12) -----------------
CULTURAL_TENSIONS: List[Dict[str, Any]] = [
    {
        "circle_1": "Familia", "circle_2": "Gastronomia",
        "strength": 0.92, "type": "Sinergia Natural",
        "context": "Rituais familiares em torno da mesa",
        "pain": "Perda de tradicoes culinarias familiares",
        "emotion": "Nostalgia, pertencimento, conforto",
        "mentions_pattern": ["receita da vo", "almoco de domingo", "comida de mae", "tempero de casa"],
    },
    {
        "circle_1": "Tecnologia", "circle_2": "Relacionamentos",
        "strength": 0.73, "type": "Tensao Criativa",
        "context": "Dependencia digital vs presenca fisica",
        "pain": "Solidao digital - hiperconectados mas distantes",
        "emotion": "Ansiedade, FOMO, desejo de autenticidade",
        "mentions_pattern": ["tempo de tela", "vicio em celular", "detox digital", "presenca real"],
    },
    {
        "circle_1": "Sustentabilidade", "circle_2": "Status",
        "strength": 0.68, "type": "Conflito Ativo",
        "context": "Geracao Z quer sustentavel mas deseja luxo",
        "pain": "Culpa do consumo",
        "emotion": "Culpa, conflito interno",
        "mentions_pattern": ["consumo consciente", "fast fashion", "greenwashing", "sustentavel mas caro"],
    },
    {
        "circle_1": "Musica", "circle_2": "Comunidade",
        "strength": 0.87, "type": "Amplificacao Mutua",
        "context": "Baile funk, forro de rua, roda de samba",
        "pain": "Gentrificacao e criminalizacao de eventos perifericos",
        "emotion": "Orgulho, pertencimento, resistencia cultural",
        "mentions_pattern": ["baile da comunidade", "roda de samba", "forro pe de serra", "som na rua"],
    },
    {
        "circle_1": "Trabalho", "circle_2": "Diversidade",
        "strength": 0.61, "type": "Evolucao Necessaria",
        "context": "Cotas, lideranca diversa, equidade salarial",
        "pain": "Tokenismo - diversidade de fachada",
        "emotion": "Frustracao, esperanca, revolta contra hipocrisia",
        "mentions_pattern": ["vaga afirmativa", "teto de vidro", "salario igual", "lugar de fala"],
    },
    {
        "circle_1": "Saude", "circle_2": "Tecnologia",
        "strength": 0.75, "type": "Amplificacao Mutua",
        "context": "Apps de meditacao, fitness trackers, teleconsulta",
        "pain": "Excesso de telas prejudica saude mental",
        "emotion": "Empoderamento vs sobrecarga informacional",
        "mentions_pattern": ["saude mental", "burnout", "app de meditacao", "terapia online"],
    },
    {
        "circle_1": "Arte", "circle_2": "Tecnologia",
        "strength": 0.81, "type": "Amplificacao Mutua",
        "context": "IA generativa, NFTs, streaming - novos modelos",
        "pain": "IA ameaca empregos criativos",
        "emotion": "Excitacao, medo, incerteza",
        "mentions_pattern": ["ia generativa", "artista vs ia", "nft", "criacao digital"],
    },
    {
        "circle_1": "Educacao", "circle_2": "Tecnologia",
        "strength": 0.85, "type": "Amplificacao Mutua",
        "context": "EAD, EdTech, cursos online",
        "pain": "Exclusao digital",
        "emotion": "Esperanca, frustracao com desigualdade",
        "mentions_pattern": ["ead", "curso online", "exclusao digital", "educacao remota"],
    },
    {
        "circle_1": "Sustentabilidade", "circle_2": "Comunidade",
        "strength": 0.78, "type": "Tensao Criativa",
        "context": "Feiras organicas, cooperativas, produtores locais",
        "pain": "Grandes redes esmagam comercio local",
        "emotion": "Orgulho local, preocupacao com homogeneizacao",
        "mentions_pattern": ["compre local", "feira organica", "produtor local", "economia solidaria"],
    },
    {
        "circle_1": "Espiritualidade", "circle_2": "Saude",
        "strength": 0.72, "type": "Tensao Criativa",
        "context": "Mindfulness, yoga, meditacao",
        "pain": "Comercializacao esvazia sentido espiritual",
        "emotion": "Busca por proposito, cansaco do material",
        "mentions_pattern": ["mindfulness", "meditacao", "yoga", "proposito de vida"],
    },
    {
        "circle_1": "Ambicoes", "circle_2": "Trabalho",
        "strength": 0.89, "type": "Sinergia Natural",
        "context": "Empreendedorismo, side hustle, nomadismo digital",
        "pain": "Cultura do hustle - burnout disfarc. de ambicao",
        "emotion": "Motivacao, exaustao, medo de fracassar",
        "mentions_pattern": ["side hustle", "empreender", "sonho grande", "burnout"],
    },
    {
        "circle_1": "Diversidade", "circle_2": "Arte",
        "strength": 0.83, "type": "Amplificacao Mutua",
        "context": "Representatividade na arte, vozes marginalizadas",
        "pain": "Apropriacao cultural",
        "emotion": "Orgulho, indignacao, celebracao de identidade",
        "mentions_pattern": ["representatividade", "lugar de fala", "cultura periferica", "voz das minorias"],
    },
]

# -- core/tension_detection_engine.py  tension_keywords --------------------
TENSION_KEYWORDS: Dict[str, List[str]] = {
    "conflito_direto": [
        "contra", "versus", "briga", "discussao", "polemica", "controversia",
        "discordo", "absurdo", "ridiculo", "inaceitavel", "revoltante",
    ],
    "polarizacao": [
        "nos vs eles", "nosso vs deles", "verdadeiro vs falso",
        "certo vs errado", "tradicional vs moderno", "antigo vs novo",
    ],
    "exclusao_social": [
        "nao pertence", "nao e nosso", "invasor", "forasteiro",
        "nao entende", "nao e daqui", "cultura estranha",
    ],
    "resistencia_cultural": [
        "preservar tradicao", "manter costume", "resistir mudanca",
        "defender cultura", "proteger identidade", "nao perder raiz",
    ],
    "mudanca_forcada": [
        "imposto", "forcado", "obrigado", "sem escolha",
        "nao consultaram", "decisao de cima", "sem participacao",
    ],
}

# -- Emotion lexicon (para LFs de tensao) ----------------------------------
EMOTION_LEXICON: Dict[str, List[str]] = {
    "nostalgia": ["saudade", "nostalgia", "antigamente", "bons tempos", "como era antes", "lembro quando"],
    "ansiedade": ["ansiedade", "ansioso", "preocupado", "medo", "incerteza", "inseguranca", "angustia"],
    "revolta": ["revolta", "indignacao", "inaceitavel", "absurdo", "injusto", "raiva", "vergonha"],
    "esperanca": ["esperanca", "otimismo", "vai melhorar", "dias melhores", "futuro", "acredito"],
    "orgulho": ["orgulho", "orgulhoso", "representatividade", "nossa cultura", "identidade", "raiz"],
    "pertencimento": ["pertencer", "comunidade", "nosso", "juntos", "coletivo", "familia"],
    "culpa": ["culpa", "consciencia", "deveria", "errado", "impacto", "responsabilidade"],
    "empoderamento": ["empoderamento", "poder", "voz", "protagonismo", "autonomia", "liberdade"],
}

# -- Momentum bands (Paper B Muhlroth 2023) --------------------------------
MOMENTUM_BANDS = {
    "emergente": (0.0, 0.30),
    "crescente": (0.30, 0.55),
    "estabelecido": (0.55, 0.75),
    "dominante": (0.75, 0.90),
    "saturado": (0.90, 1.01),
}

# ===========================================================================
# HELPERS
# ===========================================================================
from snorkel.labeling import labeling_function


def _text_core(x):
    parts = [
        str(x.get("circulo", "")),
        str(x.get("termo", "")),
        str(x.get("tipo", "")),
    ]
    return " ".join(parts).lower()


def _text_full(x):
    raw = x.get("raw_data") or {}
    extra = []
    if isinstance(raw, dict):
        for key in ("title", "titulo", "description", "descricao",
                     "text", "texto", "snippet", "content", "name", "body"):
            val = raw.get(key, "")
            if val:
                extra.append(str(val))
    return (_text_core(x) + " " + " ".join(extra)).lower()


def _circulo(x):
    return str(x.get("circulo", "")).lower().strip()


def _plataforma(x):
    return str(x.get("plataforma", "")).lower().strip()


def _score(x):
    try:
        return float(x.get("score") or 0)
    except (ValueError, TypeError):
        return 0.0


def _kw_any(text, words):
    return any(w in text for w in words)


def _kw_count(text, words):
    return sum(1 for w in words if w in text)


def _expr_any(text, expressions):
    return any(expr in text for expr in expressions)


CIRCULO_SLUG_MAP = {
    "musica_ritmo": 0, "musica": 0,
    "gastronomia": 1, "gastronomia_sabor": 1,
    "moda": 2,
    "esporte": 3, "esportes": 3,
    "tecnologia": 4,
    "arte": 5, "arte_cultura": 5, "cultura": 5,
    "religiao": 6, "espiritualidade": 6,
    "politica": 7,
    "natureza": 8, "sustentabilidade": 8,
    "comportamento": 9, "juventude": 9,
    "familia": 10,
    "trabalho": 11, "economia": 11,
    "saude": 12, "bem-estar": 12,
    "educacao": 13,
    "sexualidade": 14,
    "diversidade": 15,
}


# ===========================================================================
# FAMILIA A  -  CIRCULO CANONICO (16 LFs)
# Heuristica: slug match + keywords do tfidf_analyzer.py
# ===========================================================================

@labeling_function()
def lf_a_musica(x):
    if _circulo(x) in ("musica_ritmo", "musica"):
        return 0
    t = _text_core(x)
    terms = TFIDF_CULTURAL_TERMS["musica"] + [
        "sertanejo", "trap", "mc ", "cantora", "playlist", "album",
        "clipe", "videoclipe", "show musical", "streaming musical",
    ]
    if _kw_any(t, terms):
        return 0
    return ABSTAIN


@labeling_function()
def lf_a_gastronomia(x):
    if _circulo(x) in ("gastronomia", "gastronomia_sabor"):
        return 1
    t = _text_core(x)
    terms = TFIDF_CULTURAL_TERMS["culinaria"] + [
        "receita", "restaurante", "chef", "comida", "delivery", "ifood",
        "gastronomia", "sabor", "tempero", "cozinha",
    ]
    if _kw_any(t, terms):
        return 1
    return ABSTAIN


@labeling_function()
def lf_a_moda(x):
    if _circulo(x) == "moda":
        return 2
    t = _text_core(x)
    if _kw_any(t, ["moda", "fashion", "streetwear", "roupa", "look", "outfit",
                    "grife", "estilo", "vestuario", "tenis", "sneaker",
                    "colecao", "desfile", "influencer moda"]):
        return 2
    return ABSTAIN


@labeling_function()
def lf_a_esporte(x):
    if _circulo(x) in ("esporte", "esportes"):
        return 3
    t = _text_core(x)
    terms = TFIDF_CULTURAL_TERMS["esportes"] + [
        "basquete", "beach tennis", "corrida", "maratona", "crossfit",
        "academia", "atleta", "campeonato", "olimpiadas", "libertadores", "brasileirao",
    ]
    if _kw_any(t, terms):
        return 3
    return ABSTAIN


@labeling_function()
def lf_a_tecnologia(x):
    if _circulo(x) == "tecnologia":
        return 4
    t = _text_core(x)
    if _kw_any(t, ["ia ", "inteligencia artificial", "chatgpt", "llm",
                    "machine learning", "startup", "app ", "software",
                    "tecnologia", "digital", "iphone", "android",
                    "tiktok", "algoritmo", "programacao", "github", "dados"]):
        return 4
    return ABSTAIN


@labeling_function()
def lf_a_arte_cultura(x):
    if _circulo(x) in ("arte", "cultura", "arte_cultura"):
        return 5
    t = _text_core(x)
    if _kw_any(t, TFIDF_CULTURAL_TERMS["cultura_popular"] + [
            "arte", "artista", "exposicao", "museu", "galeria", "cinema",
            "filme", "serie", "netflix", "literatura", "livro", "teatro",
            "danca", "fotografia", "grafite", "pintura"]):
        return 5
    return ABSTAIN


@labeling_function()
def lf_a_religiao(x):
    if _circulo(x) in ("religiao", "espiritualidade"):
        return 6
    t = _text_core(x)
    if _kw_any(t, ["religiao", "fe", "evangelico", "catolico", "umbanda",
                    "candomble", "pastor", "igreja", "culto", "deus", "biblia",
                    "espiritualidade", "orixa", "terreiro"]):
        return 6
    return ABSTAIN


@labeling_function()
def lf_a_politica(x):
    if _circulo(x) == "politica":
        return 7
    t = _text_core(x)
    if _kw_any(t, ["politica", "eleicao", "governo", "presidente", "senado",
                    "camara", "partido", "voto", "democracia", "manifestacao",
                    "protesto", "direitos", "congresso"]):
        return 7
    return ABSTAIN


@labeling_function()
def lf_a_natureza(x):
    if _circulo(x) in ("natureza", "sustentabilidade"):
        return 8
    t = _text_core(x)
    terms = TFIDF_CULTURAL_TERMS["lugares"]
    if _kw_any(t, terms + ["sustentabilidade", "meio ambiente", "clima",
                            "aquecimento global", "reciclagem", "organico",
                            "vegano", "biodiversidade", "desmatamento",
                            "energia solar", "renovavel"]):
        return 8
    return ABSTAIN


@labeling_function()
def lf_a_juventude(x):
    if _circulo(x) in ("juventude", "comportamento"):
        return 9
    t = _text_core(x)
    if _kw_any(t, ["gen z", "geracao z", "jovem", "adolescente", "escola",
                    "millennial", "skate", "trend", "viral", "influencer",
                    "hype", "cringe", "slay", "npc", "twitch"]):
        return 9
    return ABSTAIN


@labeling_function()
def lf_a_familia(x):
    if _circulo(x) == "familia":
        return 10
    t = _text_core(x)
    if _kw_any(t, ["familia", "pai", "mae", "filho", "casamento",
                    "crianca", "bebe", "gravidez", "maternidade",
                    "paternidade", "divorcio", "lar", "casa"]):
        return 10
    return ABSTAIN


@labeling_function()
def lf_a_trabalho(x):
    if _circulo(x) in ("trabalho", "economia"):
        return 11
    t = _text_core(x)
    if _kw_any(t, ["trabalho", "emprego", "salario", "carreira", "empresa",
                    "empreendedor", "home office", "freelance", "economia",
                    "inflacao", "pix", "financas", "investimento", "clt",
                    "uberizacao", "mercado de trabalho"]):
        return 11
    return ABSTAIN


@labeling_function()
def lf_a_saude(x):
    if _circulo(x) in ("saude", "bem-estar"):
        return 12
    t = _text_core(x)
    if _kw_any(t, ["saude", "saude mental", "bem-estar", "medicina", "hospital",
                    "terapia", "psicologo", "ansiedade", "depressao", "fitness",
                    "dieta", "nutricao", "pilates", "yoga", "autocuidado"]):
        return 12
    return ABSTAIN


@labeling_function()
def lf_a_educacao(x):
    if _circulo(x) == "educacao":
        return 13
    t = _text_core(x)
    if _kw_any(t, ["educacao", "universidade", "curso", "aprendizado", "ensino",
                    "professor", "enem", "vestibular", "faculdade", "mestrado",
                    "doutorado", "pesquisa", "ciencia", "capacitacao"]):
        return 13
    return ABSTAIN


@labeling_function()
def lf_a_sexualidade(x):
    if _circulo(x) == "sexualidade":
        return 14
    t = _text_core(x)
    if _kw_any(t, ["lgbtq", "lgbtqia", "gay", "lesbica", "bissexual",
                    "trans", "nao-binario", "queer", "sexualidade",
                    "identidade de genero", "pride", "parada", "feminismo"]):
        return 14
    return ABSTAIN


@labeling_function()
def lf_a_diversidade(x):
    if _circulo(x) in ("diversidade", "racial"):
        return 15
    t = _text_core(x)
    if _kw_any(t, ["diversidade", "racismo", "antirracismo", "negro",
                    "afro", "quilombola", "indigena", "representatividade",
                    "inclusao", "preconceito", "discriminacao", "equidade", "cotas"]):
        return 15
    return ABSTAIN


# ===========================================================================
# FAMILIA B  -  ALMA BRASILEIRA (7 LFs)
# Heuristica: keywords + expressoes multi-word do alma_brasileira.py
# ===========================================================================

ALMA_TO_CIRCLE = {
    "caloroso_hospitaleiro": 10,
    "alegre_festivo": 0,
    "criativo_improvisador": 5,
    "musical_ritmado": 0,
    "resiliente_esperancoso": 11,
    "emotivo_expressivo": 5,
    "solidario_comunitario": 15,
}


@labeling_function()
def lf_b_hospitalidade(x):
    t = _text_full(x)
    v = ALMA_VALUES["caloroso_hospitaleiro"]
    if _kw_count(t, v["keywords"]) >= 2 or _expr_any(t, v["expressions"]):
        return ALMA_TO_CIRCLE["caloroso_hospitaleiro"]
    return ABSTAIN


@labeling_function()
def lf_b_festividade(x):
    t = _text_full(x)
    v = ALMA_VALUES["alegre_festivo"]
    kw_hits = _kw_count(t, v["keywords"])
    festa_hits = _kw_count(t, TFIDF_CULTURAL_TERMS["festas"])
    if kw_hits >= 2 or _expr_any(t, v["expressions"]) or festa_hits >= 2:
        return ALMA_TO_CIRCLE["alegre_festivo"]
    return ABSTAIN


@labeling_function()
def lf_b_criatividade(x):
    t = _text_full(x)
    v = ALMA_VALUES["criativo_improvisador"]
    if _kw_count(t, v["keywords"]) >= 2 or _expr_any(t, v["expressions"]):
        return ALMA_TO_CIRCLE["criativo_improvisador"]
    return ABSTAIN


@labeling_function()
def lf_b_musicalidade(x):
    t = _text_full(x)
    v = ALMA_VALUES["musical_ritmado"]
    if _kw_count(t, v["keywords"]) >= 2 or _expr_any(t, v["expressions"]):
        return ALMA_TO_CIRCLE["musical_ritmado"]
    return ABSTAIN


@labeling_function()
def lf_b_resiliencia(x):
    t = _text_full(x)
    v = ALMA_VALUES["resiliente_esperancoso"]
    if _kw_count(t, v["keywords"]) >= 2 or _expr_any(t, v["expressions"]):
        return ALMA_TO_CIRCLE["resiliente_esperancoso"]
    return ABSTAIN


@labeling_function()
def lf_b_emotividade(x):
    t = _text_full(x)
    v = ALMA_VALUES["emotivo_expressivo"]
    if _kw_count(t, v["keywords"]) >= 2 or _expr_any(t, v["expressions"]):
        return ALMA_TO_CIRCLE["emotivo_expressivo"]
    return ABSTAIN


@labeling_function()
def lf_b_solidariedade(x):
    t = _text_full(x)
    v = ALMA_VALUES["solidario_comunitario"]
    if _kw_count(t, v["keywords"]) >= 2 or _expr_any(t, v["expressions"]):
        return ALMA_TO_CIRCLE["solidario_comunitario"]
    return ABSTAIN


# ===========================================================================
# FAMILIA C  -  TENSAO CULTURAL (5 LFs)
# Heuristica: relationships + contexto/dor/emocao/mencoes
# ===========================================================================

@labeling_function()
def lf_c_tensao_conflito(x):
    """Conflito cultural direto (polarizacao, exclusao).
    Contexto: discussao publica com posicoes opostas.
    Dor: divisao social, nao-pertencimento.
    Emocao: revolta, indignacao, medo.
    Mencoes: nos vs eles, nao pertence, invasor.
    """
    t = _text_full(x)
    conflict_kw = TENSION_KEYWORDS["conflito_direto"] + TENSION_KEYWORDS["polarizacao"]
    emotion_kw = EMOTION_LEXICON["revolta"] + EMOTION_LEXICON["ansiedade"]
    if _kw_count(t, conflict_kw) >= 2 or (_kw_count(t, conflict_kw) >= 1 and _kw_count(t, emotion_kw) >= 1):
        return 7  # POLITICA
    return ABSTAIN


@labeling_function()
def lf_c_tensao_identidade(x):
    """Tensao de identidade/resistencia cultural.
    Contexto: preservacao de tradicoes vs modernizacao.
    Dor: perda de raizes, descaracterizacao.
    Emocao: nostalgia, orgulho, medo de perda.
    Mencoes: preservar tradicao, defender cultura.
    """
    t = _text_full(x)
    resist_kw = TENSION_KEYWORDS["resistencia_cultural"]
    emotion_kw = EMOTION_LEXICON["nostalgia"] + EMOTION_LEXICON["orgulho"]
    if _kw_count(t, resist_kw) >= 1:
        return 5  # ARTE_CULTURA
    if _kw_count(t, emotion_kw) >= 2 and _kw_any(t, ["cultura", "tradicao", "raiz", "identidade"]):
        return 5
    return ABSTAIN


@labeling_function()
def lf_c_tensao_exclusao(x):
    """Tensao exclusao social / mudanca forcada.
    Contexto: gentrificacao, remocoes, politicas excludentes.
    Dor: invisibilidade, falta de voz.
    Emocao: revolta, frustracao.
    Mencoes: nao e nosso, forasteiro, sem participacao.
    """
    t = _text_full(x)
    exclusion_kw = TENSION_KEYWORDS["exclusao_social"] + TENSION_KEYWORDS["mudanca_forcada"]
    emotion_kw = EMOTION_LEXICON["revolta"] + EMOTION_LEXICON["culpa"]
    if _kw_count(t, exclusion_kw) >= 2 or (_kw_count(t, exclusion_kw) >= 1 and _kw_count(t, emotion_kw) >= 1):
        return 15  # DIVERSIDADE
    return ABSTAIN


@labeling_function()
def lf_c_tensao_consumo_sustentabilidade(x):
    """Tensao consumo x sustentabilidade (relationship #3).
    Contexto: Gen Z quer sustentavel mas deseja luxo.
    Dor: culpa do consumo.
    Emocao: culpa, conflito interno.
    Mencoes: consumo consciente, fast fashion, greenwashing.
    """
    t = _text_full(x)
    mentions = CULTURAL_TENSIONS[2]["mentions_pattern"]
    emotion_kw = EMOTION_LEXICON["culpa"]
    if _kw_count(t, mentions) >= 1:
        return 8  # NATUREZA
    if _kw_count(t, emotion_kw) >= 1 and _kw_any(t, ["consumo", "sustentavel", "comprar"]):
        return 8
    return ABSTAIN


@labeling_function()
def lf_c_tensao_digital_solidao(x):
    """Tensao tecnologia x solidao digital (relationship #2).
    Contexto: hiperconectados mas emocionalmente distantes.
    Dor: solidao digital, FOMO, vicio em tela.
    Emocao: ansiedade, desejo de autenticidade.
    Mencoes: tempo de tela, vicio celular, detox digital.
    """
    t = _text_full(x)
    mentions = CULTURAL_TENSIONS[1]["mentions_pattern"]
    emotion_kw = EMOTION_LEXICON["ansiedade"]
    if _kw_count(t, mentions) >= 1:
        return 12  # SAUDE
    if _kw_count(t, emotion_kw) >= 1 and _kw_any(t, ["digital", "tela", "celular", "rede social"]):
        return 12
    return ABSTAIN


# ===========================================================================
# FAMILIA D  -  MOMENTUM CULTURAL (4 LFs)
# Heuristica: score numerico (threshold) - Paper B (Muhlroth 2023)
# ===========================================================================

@labeling_function()
def lf_d_momentum_dominante(x):
    """Score dominante (>0.75): reforca label do slug."""
    if _score(x) < 0.75:
        return ABSTAIN
    return CIRCULO_SLUG_MAP.get(_circulo(x), ABSTAIN)


@labeling_function()
def lf_d_momentum_emergente(x):
    """Score emergente (<0.30): weak signal - ABSTAIN (incerteza)."""
    if 0 < _score(x) < 0.30:
        return ABSTAIN
    return ABSTAIN


@labeling_function()
def lf_d_score_alto_gastronomia(x):
    """Score alto + circulo gastronomico = label forte."""
    if _score(x) > 0.60 and _circulo(x) in ("gastronomia", "gastronomia_sabor"):
        return 1
    return ABSTAIN


@labeling_function()
def lf_d_score_alto_musica(x):
    """Score alto + circulo musical = label forte."""
    if _score(x) > 0.60 and _circulo(x) in ("musica_ritmo", "musica"):
        return 0
    return ABSTAIN


# ===========================================================================
# FAMILIA E  -  PLATAFORMA x CIRCULO (4 LFs)
# Heuristica: correlacao plataforma -> tipo de conteudo
# ===========================================================================

@labeling_function()
def lf_e_spotify(x):
    """Spotify -> MUSICA."""
    if _plataforma(x) == "spotify":
        t = _text_core(x)
        if _kw_any(t, ["receita", "saude", "politica"]):
            return ABSTAIN
        return 0
    return ABSTAIN


@labeling_function()
def lf_e_youtube_musica(x):
    """YouTube + termos musicais -> MUSICA."""
    if _plataforma(x) == "youtube":
        t = _text_full(x)
        if _kw_any(t, ["clipe", "videoclipe", "album", "lancamento musical",
                        "playlist", "feat", "remix", "cover"]):
            return 0
    return ABSTAIN


@labeling_function()
def lf_e_youtube_educacao(x):
    """YouTube + termos educacionais -> EDUCACAO."""
    if _plataforma(x) == "youtube":
        t = _text_full(x)
        if _kw_any(t, ["tutorial", "aula", "curso", "aprenda", "como fazer",
                        "explicacao", "documentario", "estudo"]):
            return 13
    return ABSTAIN


@labeling_function()
def lf_e_reddit(x):
    """Reddit + termos tech -> TECNOLOGIA."""
    if _plataforma(x) == "reddit":
        t = _text_full(x)
        if _kw_any(t, ["programming", "tech", "software", "ia ", "startup",
                        "python", "javascript", "code", "developer"]):
            return 4
    return ABSTAIN


# ===========================================================================
# FAMILIA F  -  REGIONAL (3 LFs)
# Heuristica: expressoes regionais + marcadores culturais
# ===========================================================================

@labeling_function()
def lf_f_nordeste_cultural(x):
    """Expressoes nordestinas + contexto musical -> MUSICA."""
    t = _text_full(x)
    ne = REGIONAL_EXPRESSIONS["Nordeste"]
    all_terms = ne["expressions"] + ne["cultural_markers"]
    if _kw_count(t, all_terms) >= 2:
        if _kw_any(t, TFIDF_CULTURAL_TERMS["musica"] + TFIDF_CULTURAL_TERMS["festas"]):
            return 0
    return ABSTAIN


@labeling_function()
def lf_f_periferia_arte(x):
    """Expressoes de periferia + contexto artistico -> ARTE_CULTURA."""
    t = _text_full(x)
    periferia_kw = ["periferia", "quebrada", "favela", "comunidade", "morro",
                    "vila", "rap ", "grafite", "slam", "sarau", "batalha de rima"]
    if _kw_count(t, periferia_kw) >= 2:
        return 5
    return ABSTAIN


@labeling_function()
def lf_f_regional_gastronomia(x):
    """Marcadores regionais + termos gastronomicos -> GASTRONOMIA."""
    t = _text_full(x)
    regional_all = []
    for region in REGIONAL_EXPRESSIONS.values():
        regional_all.extend(region["cultural_markers"])
    if _kw_count(t, regional_all) >= 1 and _kw_count(t, TFIDF_CULTURAL_TERMS["culinaria"]) >= 1:
        return 1
    return ABSTAIN


# ===========================================================================
# FAMILIA G  -  QUALIDADE / GUARD RAILS (2 LFs)
# ===========================================================================

@labeling_function()
def lf_g_teste_seed(x):
    """Sinais de teste/seed -> ABSTAIN."""
    tipo = str(x.get("tipo", "")).lower()
    if tipo in ("teste api", "seed", "test", "debug", "mock"):
        return ABSTAIN
    return ABSTAIN


@labeling_function()
def lf_g_vazio(x):
    """Sinal sem termo nem circulo -> ABSTAIN."""
    if not str(x.get("termo", "")).strip() and not str(x.get("circulo", "")).strip():
        return ABSTAIN
    return ABSTAIN


# ===========================================================================
# REGISTRO CENTRAL
# ===========================================================================

ALL_LFS = [
    # FAMILIA A (16)
    lf_a_musica, lf_a_gastronomia, lf_a_moda, lf_a_esporte,
    lf_a_tecnologia, lf_a_arte_cultura, lf_a_religiao, lf_a_politica,
    lf_a_natureza, lf_a_juventude, lf_a_familia, lf_a_trabalho,
    lf_a_saude, lf_a_educacao, lf_a_sexualidade, lf_a_diversidade,
    # FAMILIA B (7)
    lf_b_hospitalidade, lf_b_festividade, lf_b_criatividade,
    lf_b_musicalidade, lf_b_resiliencia, lf_b_emotividade,
    lf_b_solidariedade,
    # FAMILIA C (5)
    lf_c_tensao_conflito, lf_c_tensao_identidade, lf_c_tensao_exclusao,
    lf_c_tensao_consumo_sustentabilidade, lf_c_tensao_digital_solidao,
    # FAMILIA D (4)
    lf_d_momentum_dominante, lf_d_momentum_emergente,
    lf_d_score_alto_gastronomia, lf_d_score_alto_musica,
    # FAMILIA E (4)
    lf_e_spotify, lf_e_youtube_musica, lf_e_youtube_educacao, lf_e_reddit,
    # FAMILIA F (3)
    lf_f_nordeste_cultural, lf_f_periferia_arte, lf_f_regional_gastronomia,
    # FAMILIA G (2)
    lf_g_teste_seed, lf_g_vazio,
]

print(f"  Total LFs registradas: {len(ALL_LFS)}")
print(f"    A (Circulo):    16")
print(f"    B (Alma):       7")
print(f"    C (Tensao):     5")
print(f"    D (Momentum):   4")
print(f"    E (Plataforma): 4")
print(f"    F (Regional):   3")
print(f"    G (Guard):      2")


# ===========================================================================
# FETCH
# ===========================================================================
def fetch_all_signals():
    signals = []
    page, page_size = 0, 500
    while True:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/cultural_signals",
            headers={**HEADERS, "Range": f"{page * page_size}-{(page + 1) * page_size - 1}"},
            params={"select": "id,tipo,circulo,termo,score,regiao,plataforma,raw_data"},
        )
        batch = r.json()
        if not isinstance(batch, list) or not batch:
            break
        signals.extend(batch)
        if len(batch) < page_size:
            break
        page += 1
    return signals


# ===========================================================================
# LABELING
# ===========================================================================
def apply_labeling(signals):
    from snorkel.labeling import PandasLFApplier
    from snorkel.labeling.model import LabelModel
    import pandas as pd

    df = pd.DataFrame(signals)
    for col in ("tipo", "circulo", "termo", "score", "plataforma", "raw_data"):
        if col not in df.columns:
            df[col] = None

    print(f"\n  Aplicando {len(ALL_LFS)} LFs sobre {len(df)} sinais...", flush=True)
    applier = PandasLFApplier(lfs=ALL_LFS)
    L = applier.apply(df)

    lf_names = [lf.name for lf in ALL_LFS]
    print(f"  Matriz L shape: {L.shape}")

    # Cobertura
    print("\n  Cobertura por LF:")
    active_lfs = 0
    for i, name in enumerate(lf_names):
        cov = np.mean(L[:, i] != ABSTAIN) * 100
        if cov > 0:
            active_lfs += 1
            bar = "#" * int(cov / 5)
            print(f"    {name:<50} {cov:5.1f}% {bar}")
    print(f"  LFs ativas: {active_lfs}/{len(ALL_LFS)}")

    # Conflitos
    conflict_count = 0
    for i in range(L.shape[0]):
        votes = set(int(v) for v in L[i] if v != ABSTAIN)
        if len(votes) > 1:
            conflict_count += 1
    conflict_rate = conflict_count / len(signals) * 100
    print(f"\n  Sinais com conflito entre LFs: {conflict_count}/{len(signals)} ({conflict_rate:.1f}%)")
    if conflict_rate > 5:
        print(f"  -> Snorkel tera valor real (resolve disagreements)")
    else:
        print(f"  -> Poucos conflitos - Snorkel agindo como majority vote")

    # Cobertura por familia
    fam_ranges = {
        "A_Circulo": (0, 16), "B_Alma": (16, 23), "C_Tensao": (23, 28),
        "D_Momentum": (28, 32), "E_Plataforma": (32, 36),
        "F_Regional": (36, 39), "G_Guard": (39, 41),
    }
    print("\n  Cobertura por familia:")
    for fn, (s, e) in fam_ranges.items():
        fc = sum(np.mean(L[:, j] != ABSTAIN) * 100 for j in range(s, min(e, L.shape[1])))
        print(f"    {fn:<15} {fc:6.1f}%")

    # Estrategia
    active_classes = sorted(set(int(v) for row in L for v in row if v != ABSTAIN))
    avg_abstain = float(np.mean(L == ABSTAIN))
    use_majority = avg_abstain > 0.80 or len(signals) < 300

    print(f"\n  Classes ativas: {len(active_classes)}")
    print(f"  Taxa de abstain media: {avg_abstain:.2%}")
    print(f"  Estrategia: {'MajorityVote' if use_majority else 'LabelModel'}")

    if use_majority:
        from snorkel.labeling.model import MajorityLabelVoter
        label_model = MajorityLabelVoter(cardinality=N_CLASSES)
        probs = label_model.predict_proba(L)
    else:
        print("\n  Treinando LabelModel (500 epochs, lr=0.001)...", flush=True)
        label_model = LabelModel(cardinality=N_CLASSES, verbose=False)
        label_model.fit(L_train=L, n_epochs=500, lr=0.001, seed=42)
        probs = label_model.predict_proba(L)

    labels = np.argmax(probs, axis=1)
    confidences = np.max(probs, axis=1)
    abstain_rates = np.mean(L == ABSTAIN, axis=1)

    # Enrichment config: use AI layer only if ContextEnricher is available
    use_ai = True
    try:
        from core.context_enricher import ContextEnricher
        print("  ContextEnricher disponivel — AI enrichment ATIVO")
    except ImportError:
        use_ai = False
        print("  ContextEnricher nao disponivel — apenas enriquecimento por dicionario")

    results = []
    enrichment_stats = {"tension": 0, "emotion": 0, "alma": 0, "regional": 0, "narrative": 0}
    for i, row in enumerate(signals):
        label_int = int(labels[i])
        conf = float(confidences[i])
        ar = float(abstain_rates[i])

        lf_applied = [lf_names[j] for j in range(len(lf_names)) if L[i, j] != ABSTAIN]
        lf_votes = {
            lf_names[j]: LABEL_MAP.get(int(L[i, j]), "ABSTAIN")
            for j in range(len(lf_names)) if L[i, j] != ABSTAIN
        }

        tension_det = any(n.startswith("lf_c_") for n in lf_applied)
        alma_det = any(n.startswith("lf_b_") for n in lf_applied)
        momentum_band = _classify_momentum(_score(row))
        n_fam = _count_families(lf_applied)
        label_name = LABEL_MAP[label_int]

        # === ENRICHMENT LAYER ===
        enrichment = enrich_signal_full(row, label_name, use_ai=use_ai)

        # Track stats
        if enrichment["has_tension"]:
            enrichment_stats["tension"] += 1
        if enrichment["has_emotion"]:
            enrichment_stats["emotion"] += 1
        if enrichment["has_alma"]:
            enrichment_stats["alma"] += 1
        if enrichment["has_regional"]:
            enrichment_stats["regional"] += 1
        if use_ai and "narrative" in enrichment and "_error" not in enrichment.get("narrative", {}):
            enrichment_stats["narrative"] += 1

        results.append({
            "signal_id": row["id"],
            "label": label_name,
            "confidence": round(conf, 4),
            "lf_applied": lf_applied,
            "lf_votes": lf_votes,
            "abstain_rate": round(ar, 4),
            "tension_detected": tension_det,
            "alma_value_detected": alma_det,
            "momentum_band": momentum_band,
            "n_lfs_voted": len(lf_applied),
            "n_families_voted": n_fam,
            "enrichment_metadata": enrichment,
        })

    # Print enrichment summary
    total = len(signals)
    print(f"\n  === ENRICHMENT LAYER ===")
    print(f"  Sinais com tensao detalhada : {enrichment_stats['tension']:4d}/{total} ({100*enrichment_stats['tension']/total:.1f}%)")
    print(f"  Sinais com emocao detectada : {enrichment_stats['emotion']:4d}/{total} ({100*enrichment_stats['emotion']/total:.1f}%)")
    print(f"  Sinais com Alma Brasileira  : {enrichment_stats['alma']:4d}/{total} ({100*enrichment_stats['alma']/total:.1f}%)")
    print(f"  Sinais com marcador regional: {enrichment_stats['regional']:4d}/{total} ({100*enrichment_stats['regional']/total:.1f}%)")
    if use_ai:
        print(f"  Sinais com narrativa AI     : {enrichment_stats['narrative']:4d}/{total} ({100*enrichment_stats['narrative']/total:.1f}%)")
    avg_score = np.mean([r["enrichment_metadata"]["enrichment_score"] for r in results])
    print(f"  Enrichment score medio      : {avg_score:.4f}")

    return results


def _classify_momentum(score):
    for band, (lo, hi) in MOMENTUM_BANDS.items():
        if lo <= score < hi:
            return band
    return "desconhecido"


def _count_families(lf_names_voted):
    families = set()
    for name in lf_names_voted:
        parts = name.split("_")
        if len(parts) >= 2 and parts[1] in ("a", "b", "c", "d", "e", "f", "g"):
            families.add(parts[1])
    return len(families)


# ===========================================================================
# ENRICHMENT LAYER  (Post-Snorkel metadata extraction)
#
# Snorkel LFs only return an integer label. This layer re-scans each signal
# against ALL dictionaries to extract the DETAILED metadata that the LFs
# used internally but could not export:
#   - Which cultural tensions matched (with context/pain/emotion/mentions)
#   - Which emotions were detected and their intensity
#   - Which Alma Brasileira values were detected
#   - Which regional markers were found
#   - Optional: ContextEnricher narrative (AI layer)
# ===========================================================================

def enrich_tension_metadata(signal: dict) -> Dict[str, Any]:
    """Extract detailed tension metadata by re-scanning text against dictionaries.

    Returns dict with:
        tension_types       : List[str]   — matched TENSION_KEYWORDS categories
        tension_keywords_hit: List[str]   — specific keywords that matched
        relationships       : List[dict]  — matched CULTURAL_TENSIONS entries
                              each with circle_1, circle_2, type, context, pain,
                              emotion, mentions_hit
        emotions_detected   : Dict[str, List[str]] — emotion_category -> keywords hit
        emotion_intensity   : float       — 0..1 normalized by total lexicon size
    """
    text = _text_full(signal)
    result: Dict[str, Any] = {
        "tension_types": [],
        "tension_keywords_hit": [],
        "relationships": [],
        "emotions_detected": {},
        "emotion_intensity": 0.0,
    }

    # --- Tension keywords (5 categories) ---
    total_hits = 0
    for ttype, keywords in TENSION_KEYWORDS.items():
        hits = [kw for kw in keywords if kw in text]
        if hits:
            result["tension_types"].append(ttype)
            result["tension_keywords_hit"].extend(hits)
            total_hits += len(hits)

    # --- Cultural relationships (12 entries with context/pain/emotion/mentions) ---
    for rel in CULTURAL_TENSIONS:
        mentions = rel.get("mentions_pattern", [])
        mentions_hit = [m for m in mentions if m in text]
        # Also check if circle names appear in text
        c1 = rel["circle_1"].lower()
        c2 = rel["circle_2"].lower()
        circles_in_text = (c1 in text) or (c2 in text)
        if mentions_hit or (circles_in_text and total_hits > 0):
            result["relationships"].append({
                "circle_1": rel["circle_1"],
                "circle_2": rel["circle_2"],
                "type": rel["type"],
                "strength": rel["strength"],
                "context": rel["context"],
                "pain": rel["pain"],
                "emotion": rel["emotion"],
                "mentions_hit": mentions_hit,
            })

    # --- Emotion lexicon (8 categories) ---
    total_emotion_terms = 0
    emotion_hits_total = 0
    for emotion_cat, keywords in EMOTION_LEXICON.items():
        total_emotion_terms += len(keywords)
        hits = [kw for kw in keywords if kw in text]
        if hits:
            result["emotions_detected"][emotion_cat] = hits
            emotion_hits_total += len(hits)

    result["emotion_intensity"] = round(
        min(emotion_hits_total / max(total_emotion_terms, 1), 1.0), 4
    )

    return result


def enrich_alma_metadata(signal: dict) -> Dict[str, Any]:
    """Extract detailed Alma Brasileira metadata.

    Returns dict with:
        values_detected     : List[dict] — each with name, weight,
                              keywords_hit, expressions_hit
        total_weight        : float      — sum of weights of detected values
        dominant_value      : str|None   — highest-weight detected value
    """
    text = _text_full(signal)
    result: Dict[str, Any] = {
        "values_detected": [],
        "total_weight": 0.0,
        "dominant_value": None,
    }

    best_weight = 0.0
    for value_name, vdata in ALMA_VALUES.items():
        kw_hits = [kw for kw in vdata["keywords"] if kw in text]
        expr_hits = [ex for ex in vdata["expressions"] if ex in text]
        if kw_hits or expr_hits:
            w = vdata["weight"]
            result["values_detected"].append({
                "name": value_name,
                "weight": w,
                "keywords_hit": kw_hits,
                "expressions_hit": expr_hits,
            })
            result["total_weight"] += w
            if w > best_weight:
                best_weight = w
                result["dominant_value"] = value_name

    result["total_weight"] = round(result["total_weight"], 4)
    return result


def enrich_regional_metadata(signal: dict) -> Dict[str, Any]:
    """Extract regional markers from signal text.

    Returns dict with:
        regions_detected : List[dict] — each with region, expressions_hit,
                           markers_hit
        primary_region   : str|None   — region with most matches
    """
    text = _text_full(signal)
    result: Dict[str, Any] = {
        "regions_detected": [],
        "primary_region": None,
    }

    best_count = 0
    for region, rdata in REGIONAL_EXPRESSIONS.items():
        expr_hits = [e for e in rdata["expressions"] if e in text]
        marker_hits = [m for m in rdata["cultural_markers"] if m in text]
        total = len(expr_hits) + len(marker_hits)
        if total > 0:
            result["regions_detected"].append({
                "region": region,
                "expressions_hit": expr_hits,
                "markers_hit": marker_hits,
                "match_count": total,
            })
            if total > best_count:
                best_count = total
                result["primary_region"] = region

    return result


def enrich_with_context_enricher(signal: dict, label: str) -> Dict[str, Any]:
    """Optional AI enrichment via core/context_enricher.py.

    Uses TF-IDF similarity + knowledge base to add narrative context.
    Falls back gracefully if ContextEnricher is unavailable.

    Returns dict with:
        descricao, contexto_cultural, publico_alvo, tensoes_culturais,
        circulos_culturais, recomendacao_acao, ...
    """
    try:
        from core.context_enricher import ContextEnricher

        # Singleton: reuse enricher across calls
        if not hasattr(enrich_with_context_enricher, "_instance"):
            enrich_with_context_enricher._instance = ContextEnricher()
        enricher = enrich_with_context_enricher._instance

        termo = str(signal.get("termo", ""))
        texto = _text_full(signal)
        metricas = {"momentum": _score(signal)}

        ctx = enricher.enrich_signal(
            termo=termo,
            texto_api=texto,
            metricas=metricas,
            segmento=None,
            desafio=None,
        )
        # Keep only the most useful narrative fields
        return {
            "descricao": ctx.get("descricao", ""),
            "contexto_cultural": ctx.get("contexto_cultural", ""),
            "publico_alvo": ctx.get("publico_alvo", ""),
            "tensoes_culturais": ctx.get("tensoes_culturais", ""),
            "circulos_culturais": ctx.get("circulos_culturais", []),
            "recomendacao_acao": ctx.get("recomendacao_acao", ""),
        }
    except Exception as e:
        return {"_error": f"ContextEnricher unavailable: {e}"}


def enrich_signal_full(signal: dict, label: str, use_ai: bool = True) -> Dict[str, Any]:
    """Run ALL enrichment layers on a single signal.

    Combines dictionary-based extraction (always) with optional AI layer.

    Returns unified enrichment_metadata dict.
    """
    meta: Dict[str, Any] = {}

    # Layer 1: Dictionary-based (fast, deterministic)
    meta["tension"] = enrich_tension_metadata(signal)
    meta["alma"] = enrich_alma_metadata(signal)
    meta["regional"] = enrich_regional_metadata(signal)

    # Layer 2: AI narrative context (optional, slower)
    if use_ai:
        meta["narrative"] = enrich_with_context_enricher(signal, label)

    # Summary flags for quick filtering
    meta["has_tension"] = len(meta["tension"]["tension_types"]) > 0 or len(meta["tension"]["relationships"]) > 0
    meta["has_emotion"] = len(meta["tension"]["emotions_detected"]) > 0
    meta["has_alma"] = len(meta["alma"]["values_detected"]) > 0
    meta["has_regional"] = len(meta["regional"]["regions_detected"]) > 0
    meta["enrichment_score"] = round(
        sum([
            0.30 * min(len(meta["tension"]["relationships"]) / 3, 1.0),
            0.25 * meta["tension"]["emotion_intensity"],
            0.25 * min(meta["alma"]["total_weight"] / 0.50, 1.0),
            0.20 * min(len(meta["regional"]["regions_detected"]) / 2, 1.0),
        ]), 4
    )

    return meta


# ===========================================================================
# PERSIST
# ===========================================================================
def persist_labels(labels, min_confidence=0.0, dry_run=False):
    filtered = [l for l in labels if l["confidence"] >= min_confidence]
    print(f"\n  Labels com confidence >= {min_confidence}: {len(filtered)}/{len(labels)}")

    output_dir = ROOT / "scripts" / "output"
    output_dir.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    # Full enriched output (JSON with metadata)
    out_path = output_dir / f"signal_labels_v2_enriched_{ts}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)
    print(f"  Backup enriched: {out_path}")

    # Compact summary for quick inspection
    summary_path = output_dir / f"enrichment_summary_{ts}.json"
    summary = []
    for item in filtered:
        meta = item.get("enrichment_metadata", {})
        summary.append({
            "signal_id": item["signal_id"],
            "label": item["label"],
            "confidence": item["confidence"],
            "momentum_band": item.get("momentum_band"),
            "enrichment_score": meta.get("enrichment_score", 0),
            "tension_types": meta.get("tension", {}).get("tension_types", []),
            "emotions": list(meta.get("tension", {}).get("emotions_detected", {}).keys()),
            "alma_dominant": meta.get("alma", {}).get("dominant_value"),
            "primary_region": meta.get("regional", {}).get("primary_region"),
            "n_relationships": len(meta.get("tension", {}).get("relationships", [])),
        })
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"  Backup summary : {summary_path}")

    if dry_run:
        print("  [dry-run] Nao persistido no Supabase.")
        return {"saved": 0, "total_filtered": len(filtered), "backup": str(out_path)}

    payload = []
    for item in filtered:
        payload.append({
            "signal_id": item["signal_id"],
            "label": item["label"],
            "confidence": item["confidence"],
            "lf_applied": item["lf_applied"],
            "lf_votes": item["lf_votes"],
            "abstain_rate": item["abstain_rate"],
        })

    saved = 0
    errors = 0
    upsert_headers = {
        **HEADERS,
        "Prefer": "resolution=merge-duplicates,return=minimal",
    }
    for i in range(0, len(payload), 100):
        batch = payload[i:i + 100]
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/signal_labels",
            headers=upsert_headers,
            json=batch,
            params={"on_conflict": "signal_id"},
        )
        if r.status_code in (200, 201):
            saved += len(batch)
        else:
            errors += len(batch)
            print(f"  WARN Batch {i//100}: HTTP {r.status_code} - {r.text[:200]}")

    print(f"  Salvos: {saved} | Erros: {errors}")
    return {"saved": saved, "errors": errors, "total_filtered": len(filtered), "backup": str(out_path)}


# ===========================================================================
# REPORT
# ===========================================================================
def print_report(labels, min_confidence=0.0):
    from collections import Counter

    filtered = [l for l in labels if l["confidence"] >= min_confidence]
    if not filtered:
        print("  Sem labels apos filtro de confianca.")
        return

    confs = [l["confidence"] for l in filtered]
    n_lfs = [l.get("n_lfs_voted", 0) for l in filtered]
    n_fams = [l.get("n_families_voted", 0) for l in filtered]
    tension_ct = sum(1 for l in filtered if l.get("tension_detected"))
    alma_ct = sum(1 for l in filtered if l.get("alma_value_detected"))

    print(f"\n{'='*65}")
    print(f"  RELATORIO DE QUALIDADE v2 - {len(filtered)} labels")
    print(f"{'='*65}")

    print(f"\n  CONFIANCA")
    print(f"  Media  : {np.mean(confs):.3f}")
    print(f"  Mediana: {np.median(confs):.3f}")
    print(f"  >= 0.75: {sum(1 for c in confs if c >= 0.75)} ({100*sum(1 for c in confs if c >= 0.75)/len(confs):.1f}%)")
    print(f"  >= 0.60: {sum(1 for c in confs if c >= 0.60)} ({100*sum(1 for c in confs if c >= 0.60)/len(confs):.1f}%)")

    print(f"\n  DIVERSIDADE DE HEURISTICAS")
    print(f"  LFs votantes/sinal : {np.mean(n_lfs):.1f} (media)")
    print(f"  Familias/sinal     : {np.mean(n_fams):.1f} (media) - target >= 2")
    print(f"  Tensao detectada   : {tension_ct} ({100*tension_ct/len(filtered):.1f}%)")
    print(f"  Alma detectada     : {alma_ct} ({100*alma_ct/len(filtered):.1f}%)")

    mom_dist = Counter(l.get("momentum_band", "?") for l in filtered)
    print(f"\n  MOMENTUM CULTURAL (Paper B)")
    for band in ["emergente", "crescente", "estabelecido", "dominante", "saturado"]:
        ct = mom_dist.get(band, 0)
        pct = 100 * ct / len(filtered)
        bar = "#" * int(pct / 3)
        print(f"    {band:<15} {ct:4d} ({pct:5.1f}%) {bar}")

    label_dist = Counter(l["label"] for l in filtered)
    print(f"\n  DISTRIBUICAO POR CLASSE")
    for label, ct in label_dist.most_common():
        pct = 100 * ct / len(filtered)
        bar = "#" * int(pct / 3)
        print(f"    {label:<18} {ct:4d} ({pct:5.1f}%) {bar}")

    print(f"\n  Taxa de abstain media: {np.mean([l['abstain_rate'] for l in filtered]):.3f}")

    # --- Enrichment Layer Stats ---
    enriched = [l for l in filtered if l.get("enrichment_metadata")]
    if enriched:
        escores = [l["enrichment_metadata"].get("enrichment_score", 0) for l in enriched]
        has_t = sum(1 for l in enriched if l["enrichment_metadata"].get("has_tension"))
        has_e = sum(1 for l in enriched if l["enrichment_metadata"].get("has_emotion"))
        has_a = sum(1 for l in enriched if l["enrichment_metadata"].get("has_alma"))
        has_r = sum(1 for l in enriched if l["enrichment_metadata"].get("has_regional"))

        print(f"\n  ENRICHMENT METADATA")
        print(f"  Enrichment score : {np.mean(escores):.4f} (media) | {np.max(escores):.4f} (max)")
        print(f"  Com tensao       : {has_t:4d} ({100*has_t/len(enriched):.1f}%)")
        print(f"  Com emocao       : {has_e:4d} ({100*has_e/len(enriched):.1f}%)")
        print(f"  Com Alma         : {has_a:4d} ({100*has_a/len(enriched):.1f}%)")
        print(f"  Com regional     : {has_r:4d} ({100*has_r/len(enriched):.1f}%)")

        # Top tension types across all signals
        from collections import Counter as _Counter
        all_ttypes = []
        all_emotions = []
        all_alma = []
        for l in enriched:
            meta = l["enrichment_metadata"]
            all_ttypes.extend(meta.get("tension", {}).get("tension_types", []))
            all_emotions.extend(meta.get("tension", {}).get("emotions_detected", {}).keys())
            for v in meta.get("alma", {}).get("values_detected", []):
                all_alma.append(v["name"])

        if all_ttypes:
            print(f"\n  TOP TENSION TYPES")
            for tt, ct in _Counter(all_ttypes).most_common(5):
                print(f"    {tt:<25} {ct:4d}")
        if all_emotions:
            print(f"\n  TOP EMOTIONS")
            for em, ct in _Counter(all_emotions).most_common(5):
                print(f"    {em:<25} {ct:4d}")
        if all_alma:
            print(f"\n  TOP ALMA VALUES")
            for av, ct in _Counter(all_alma).most_common(5):
                print(f"    {av:<30} {ct:4d}")

    print(f"{'='*65}")


# ===========================================================================
# MAIN
# ===========================================================================
def main():
    parser = argparse.ArgumentParser(description="S2.1 Snorkel labeling v2")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--min-confidence", type=float, default=0.0)
    args = parser.parse_args()

    print("=" * 65)
    print("  S2.1 - Snorkel Labeling Functions v2 (7 familias)")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Arquitetura: {len(ALL_LFS)} LFs em 7 familias")
    print("=" * 65)

    print("\n[1/4] Buscando sinais do Supabase...")
    signals = fetch_all_signals()
    print(f"  {len(signals)} sinais carregados")
    if not signals:
        print("  Nenhum sinal encontrado.")
        sys.exit(1)

    print("\n[2/4] Aplicando Labeling Functions + LabelModel...")
    labels = apply_labeling(signals)

    print("\n[3/4] Relatorio de qualidade:")
    print_report(labels, min_confidence=args.min_confidence)

    print("\n[4/4] Persistindo pseudo-labels...")
    result = persist_labels(labels, min_confidence=args.min_confidence, dry_run=args.dry_run)

    print(f"\nS2.1 v2 Concluido: {result}")


if __name__ == "__main__":
    main()
