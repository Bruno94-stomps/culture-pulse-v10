#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧹 Brazilian Text Preprocessor
Preprocessing especializado para texto em português brasileiro

Features:
- Expansão de contrações PT-BR (tá → está, vc → você)
- Normalização de gírias regionais (massa → legal, dahora → legal)
- Correção de typos comuns
- Lematização com spaCy PT-BR
- Extração de emojis (não remove, analisa separadamente)

Autor: Culture Pulse V9.1
Data: Fevereiro 2026
"""

import re
import unicodedata
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class BrazilianTextPreprocessor:
    """
    Preprocessador especializado para textos culturais brasileiros
    
    Níveis de preprocessing:
    - 'light': Limpeza básica (URLs, whitespace)
    - 'medium': + contrações + typos comuns
    - 'full': + gírias + lematização
    """
    
    def __init__(self):
        # Dicionário de contrações PT-BR (mais de 50 entradas)
        self.contractions = {
            # Comuns
            'tá': 'está',
            'tô': 'estou',
            'tava': 'estava',
            'tão': 'estão',
            'cê': 'você',
            'ocê': 'você',
            'pra': 'para',
            'pro': 'para o',
            'pruma': 'para uma',
            'né': 'não é',
            'vc': 'você',
            'vcs': 'vocês',
            'tbm': 'também',
            'tb': 'também',
            'tmb': 'também',
            'mt': 'muito',
            'mto': 'muito',
            'msm': 'mesmo',
            'mm': 'mesmo',
            'hj': 'hoje',
            'ontem': 'ontem',
            'q': 'que',
            'oq': 'o que',
            'pq': 'porque',
            'pprt': 'papo reto',
            'cmg': 'comigo',
            'ctg': 'contigo',
            'sla': 'sei lá',
            'tlgd': 'tá ligado',
            'vlw': 'valeu',
            'flw': 'falou',
            'blz': 'beleza',
            'fds': 'fim de semana',
            'sdds': 'saudades',
            'dps': 'depois',
            'dp': 'depois',
            'aq': 'aqui',
            'td': 'tudo',
            'tds': 'todos',
            'ngm': 'ninguém',
            'tbm': 'também',
            'dnv': 'de novo',
            'dnovo': 'de novo',
            'agr': 'agora',
            'hr': 'hora',
            'min': 'minuto',
            'seg': 'segundo',
            
            # Regionais
            'véi': 'velho',  # SP
            'mano': 'irmão',  # SP
            'parça': 'parceiro',  # SP
            'truta': 'parceiro',  # SP
            'quebrada': 'bairro',  # SP
            'rolê': 'passeio',  # SP
            'mina': 'garota',  # SP
            'cara': 'pessoa',  # SP/RJ
            'maluco': 'pessoa',  # SP/RJ
            'brother': 'irmão',  # RJ
            'pow': 'nossa',  # RJ
            'massa': 'legal',  # NE
            'oxe': 'opa',  # NE
            'oxente': 'nossa',  # NE
            'aff': 'nossa',  # NE
            'arretado': 'legal',  # NE
            'da hora': 'legal',  # NE
            'maneiro': 'legal',  # NE/RJ
            'tri': 'muito',  # RS
            'bah': 'nossa',  # RS
            'tchê': 'cara',  # RS
            'guri': 'garoto',  # RS
            'piá': 'garoto',  # PR/SC
            'sô': 'senhor',  # MG
            'uai': 'nossa',  # MG
            'trem': 'coisa',  # MG
        }
        
        # Gírias → normalização semântica
        self.slang_mapping = {
            'dahora': 'legal',
            'da hora': 'legal',
            'maneiro': 'legal',
            'bacana': 'legal',
            'top': 'legal',
            'massa': 'legal',
            'show': 'legal',
            'firmeza': 'certo',
            'beleza': 'certo',
            'tranquilo': 'certo',
            'sussa': 'tranquilo',
            'de boa': 'tranquilo',
            'na moral': 'sério',
            'sério': 'sério',
            'papo reto': 'sério',
            'papo furado': 'mentira',
            'mó': 'muito',
            'demais': 'muito',
            'pra caralho': 'muito',
            'pra caramba': 'muito',
            'pra cacete': 'muito',
            'puta': 'muito',
            'irado': 'legal',
            'sinistro': 'legal',
            'brabo': 'legal',
            'foda': 'legal',
            'lacrou': 'arrasou',
            'mitou': 'arrasou',
            'arrasou': 'arrasou',
            'mandou bem': 'arrasou',
            'bagulho': 'coisa',
            'parada': 'coisa',
            'lance': 'coisa',
            'trem': 'coisa',
            'troço': 'coisa',
        }
        
        # Typos comuns (especialmente em termos culturais)
        self.common_typos = {
            'sustentabilidae': 'sustentabilidade',
            'inteligençia': 'inteligência',
            'artifical': 'artificial',
            'Nike Tec Flis': 'Nike Tech Fleece',
            'Nike Tec Flece': 'Nike Tech Fleece',
            'Nike Tech Flice': 'Nike Tech Fleece',
            'Madurro': 'Maduro',
            'Wuhan': 'Wuhan',  # preserva (não é typo)
            'autenticidae': 'autenticidade',
            'cultuiral': 'cultural',
            'brasilerio': 'brasileiro',
            'brasiliero': 'brasileiro',
            'tecnológia': 'tecnologia',
            'inovaçao': 'inovação',
            'consumo conscente': 'consumo consciente',
            'moda sustentavel': 'moda sustentável',
        }
        
        # Lazy load spaCy (só carrega se full preprocessing)
        self.nlp = None
    
    def _load_spacy(self):
        """Lazy loading do spaCy"""
        if self.nlp is None:
            try:
                import spacy
                self.nlp = spacy.load('pt_core_news_lg')
                logger.info("✅ spaCy PT-BR loaded")
            except Exception as e:
                logger.warning(f"⚠️ spaCy not available: {e}")
                self.nlp = False
        return self.nlp
    
    def preprocess(self, text: str, level: str = 'medium') -> str:
        """
        Preprocessa texto em português brasileiro
        
        Args:
            text: Texto para processar
            level: 'light', 'medium', 'full'
        
        Returns:
            Texto processado
        """
        if not text:
            return ""
        
        # 1. LIGHT: Limpeza básica
        text = self._clean_basic(text)
        if level == 'light':
            return text
        
        # 2. MEDIUM: + contrações + typos
        text = self._expand_contractions(text)
        text = self._fix_typos(text)
        if level == 'medium':
            return text
        
        # 3. FULL: + gírias + lematização
        text = self._normalize_slang(text)
        text = self._lemmatize(text)
        
        return text
    
    def _clean_basic(self, text: str) -> str:
        """Limpeza básica (URLs, mentions, whitespace)"""
        # Preservar emojis (não remover, serão analisados separadamente)
        
        # URLs
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'www\.\S+', '', text)
        
        # Mentions (mas preservar conteúdo)
        text = re.sub(r'@(\w+)', r'\1', text)  # @nike → nike
        
        # Hashtags (preservar conteúdo)
        text = re.sub(r'#(\w+)', r'\1', text)  # #sustentabilidade → sustentabilidade
        
        # Números isolados (preservar contexto)
        # NÃO remover números, pois "Nike 2024" é relevante
        
        # Whitespace múltiplo
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Normalizar unicode (acentos corretos)
        text = unicodedata.normalize('NFKC', text)
        
        # Lowercase (preservar case em nomes próprios é complexo, então lowercase)
        text = text.lower()
        
        return text
    
    def _expand_contractions(self, text: str) -> str:
        """Expandir contrações PT-BR"""
        words = text.split()
        expanded = []
        
        for word in words:
            # Tentar match exato
            if word.lower() in self.contractions:
                expanded.append(self.contractions[word.lower()])
            else:
                expanded.append(word)
        
        return ' '.join(expanded)
    
    def _fix_typos(self, text: str) -> str:
        """Corrigir typos comuns"""
        for typo, correct in self.common_typos.items():
            # Case-insensitive replacement
            text = re.sub(r'\b' + re.escape(typo) + r'\b', correct, text, flags=re.IGNORECASE)
        
        return text
    
    def _normalize_slang(self, text: str) -> str:
        """Normalizar gírias para termos padrão"""
        words = text.split()
        normalized = []
        
        for word in words:
            if word.lower() in self.slang_mapping:
                normalized.append(self.slang_mapping[word.lower()])
            else:
                normalized.append(word)
        
        return ' '.join(normalized)
    
    def _lemmatize(self, text: str) -> str:
        """Lematização com spaCy (opcionalmente remove stopwords)"""
        nlp = self._load_spacy()
        
        if not nlp:
            # Fallback: retorna texto sem lematização
            return text
        
        doc = nlp(text)
        
        # Lematizar mas PRESERVAR stopwords (contexto importa)
        # Exemplo: "não é legal" → remover "não" mudaria sentido!
        lemmas = [token.lemma_ for token in doc]
        
        return ' '.join(lemmas)
    
    def extract_emojis(self, text: str) -> List[str]:
        """
        Extrair emojis (não remove do texto original)
        
        Emojis são importantes para sentiment analysis!
        """
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"  # dingbats
            "\U000024C2-\U0001F251"  # enclosed characters
            "]+", flags=re.UNICODE
        )
        
        return emoji_pattern.findall(text)
    
    def analyze_text_quality(self, text: str) -> Dict:
        """
        Analisa qualidade do texto (útil para filtrar spam/bots)
        
        Returns:
            Dict com métricas de qualidade
        """
        if not text:
            return {'quality_score': 0.0, 'issues': ['empty_text']}
        
        issues = []
        
        # 1. Uppercase excessivo (GRITARIA = spam?)
        uppercase_ratio = sum(1 for c in text if c.isupper()) / len(text)
        if uppercase_ratio > 0.5:
            issues.append('excessive_uppercase')
        
        # 2. Exclamação excessiva (!!!!! = spam?)
        exclamation_count = text.count('!')
        if exclamation_count > 5:
            issues.append('excessive_exclamation')
        
        # 3. Caracteres repetidos (aaaaaaaa = bot?)
        if re.search(r'(.)\1{5,}', text):
            issues.append('repeated_characters')
        
        # 4. URLs demais (link spam?)
        url_count = len(re.findall(r'http\S+', text))
        if url_count > 3:
            issues.append('excessive_urls')
        
        # 5. Emojis demais (🔥🔥🔥🔥🔥🔥 = fake engagement?)
        emoji_count = len(self.extract_emojis(text))
        if emoji_count > 10:
            issues.append('excessive_emojis')
        
        # 6. Texto muito curto (< 10 chars = spam?)
        if len(text.strip()) < 10:
            issues.append('too_short')
        
        # 7. Texto muito longo (> 5000 chars = copy-paste?)
        if len(text) > 5000:
            issues.append('too_long')
        
        # Calcular score (0-1)
        quality_score = max(0.0, 1.0 - (len(issues) * 0.15))
        
        return {
            'quality_score': quality_score,
            'issues': issues,
            'is_spam_likely': quality_score < 0.5,
            'is_bot_likely': 'repeated_characters' in issues or 'excessive_urls' in issues,
            'uppercase_ratio': uppercase_ratio,
            'emoji_count': emoji_count,
            'url_count': url_count,
            'text_length': len(text)
        }
    
    def batch_preprocess(self, texts: List[str], level: str = 'medium') -> List[Tuple[str, Dict]]:
        """
        Preprocessa múltiplos textos em batch
        
        Returns:
            Lista de (texto_processado, quality_metrics)
        """
        results = []
        
        for text in texts:
            processed = self.preprocess(text, level=level)
            quality = self.analyze_text_quality(text)
            results.append((processed, quality))
        
        logger.info(f"✅ Preprocessed {len(texts)} texts (level: {level})")
        
        return results


# Exemplo de uso
if __name__ == "__main__":
    preprocessor = BrazilianTextPreprocessor()
    
    # Teste 1: Contrações
    text1 = "Tá dahora esse Nike Tech Fleece q o Maduro tava usando, né? Vc viu?"
    print("ORIGINAL:", text1)
    print("LIGHT:", preprocessor.preprocess(text1, level='light'))
    print("MEDIUM:", preprocessor.preprocess(text1, level='medium'))
    print("FULL:", preprocessor.preprocess(text1, level='full'))
    print()
    
    # Teste 2: Gírias regionais
    text2 = "Massa demais, mano! Essa parada tá tri irada, véi!"
    print("ORIGINAL:", text2)
    print("FULL:", preprocessor.preprocess(text2, level='full'))
    print()
    
    # Teste 3: Qualidade
    text3 = "COMPRE AGORA!!!! http://spam.com http://fake.com 🔥🔥🔥🔥🔥🔥"
    quality = preprocessor.analyze_text_quality(text3)
    print("SPAM TEST:", text3)
    print("QUALITY:", quality)
