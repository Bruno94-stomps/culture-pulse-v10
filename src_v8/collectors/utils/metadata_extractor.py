#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visual Evidence Extractor V1.0 (V9.9)
=====================================
Extrai thumbnails e imagens de metadados (OG, Twitter Cards) para sinais RSS/News.
Essencial para alimentar o visual_evidence_score e o selo [VERIFICADO].
"""

import requests
import re
import logging
from typing import Optional, Dict
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class VisualEvidenceExtractor:
    """Extrai evidências visuais de URLs para comprovação cultural"""
    
    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def extract_image_from_url(self, url: str) -> Optional[str]:
        """
        Tenta extrair a imagem principal (Thumbnail/OG) de uma URL
        """
        if not url or not url.startswith('http'):
            return None
            
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. Tentar Open Graph (Meta tags de imagem)
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                return urljoin(url, og_image['content'])
                
            # 2. Tentar Twitter Card Image
            twitter_image = soup.find('meta', name='twitter:image')
            if twitter_image and twitter_image.get('content'):
                return urljoin(url, twitter_image['content'])
            
            # 3. Tentar imagem principal (Ex: Classe article-thumb, destaque, etc)
            # Como fallback, pegamos a primeira imagem grande se disponível
            images = soup.find_all('img', src=True)
            for img in images:
                src = img['src']
                # Evitar icones pequenos e trackers
                if any(x in src.lower() for x in ['logo', 'icon', 'ads', 'tracker']):
                    continue
                return urljoin(url, src)

            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao extrair evidência visual de {url}: {e}")
            return None

    def enrich_signal_with_media(self, signal: Dict) -> Dict:
        """Enriquece um sinal individual com evidência visual extraída"""
        link = signal.get('link') or signal.get('url')
        
        # Se já tem imagem ou não tem link, não fazemos nada
        if signal.get('image') or signal.get('thumbnail') or not link:
            return signal
            
        # Tenta extrair
        media_url = self.extract_image_from_url(link)
        if media_url:
            signal['image'] = media_url
            signal['thumbnail'] = media_url
            signal['visual_evidence_type'] = "extracted_og_source"
            logger.info(f"📸 Evidência visual extraída para: {signal.get('title', 'Sinal')}")
            
        return signal
