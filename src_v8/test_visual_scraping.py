#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test: Visual Metadata Extraction (Scraping)
===========================================
Valida se o extrator consegue pegar imagens de URLs reais (ex: G1, CNN).
"""

import sys
import os
import asyncio

# Setup de paths
ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_PATH)

async def test_scraping():
    print("\n🚀 TESTANDO EXTRAÇÃO DE METADADOS VISUAIS (SCRAPING)")
    print("-" * 60)

    try:
        from collectors.utils.metadata_extractor import VisualEvidenceExtractor
        extractor = VisualEvidenceExtractor()
        
        # URL de teste (notícia real brasileira para testar OG tags)
        test_url = "https://g1.globo.com/"
        print(f"🔗 Analisando URL: {test_url}")
        
        image = extractor.extract_image_from_url(test_url)
        
        if image:
            print(f"✅ SUCESSO! Imagem encontrada: {image}")
        else:
            print("⚠️ Nenhuma imagem encontrada (verifique conexão ou se o site bloqueou o bot).")

        # Simular sinal News
        signal = {
            'title': 'Notícia de Teste',
            'link': 'https://www.cnnbrasil.com.br/',
            'source': 'news'
        }
        
        print(f"\n📦 Enriquecendo sinal simulado...")
        enriched = extractor.enrich_signal_with_media(signal)
        
        if enriched.get('image'):
            print(f"✅ SINAL ENRIQUECIDO: {enriched['image']}")
        else:
            print("❌ Falha no enriquecimento do sinal.")

    except Exception as e:
        print(f"❌ Erro no teste: {e}")

if __name__ == "__main__":
    asyncio.run(test_scraping())
