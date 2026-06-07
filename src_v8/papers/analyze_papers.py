"""
Análise dos Papers Acadêmicos sobre Weak Signals e Trends
Extrai conceitos-chave para validar implementação do Futurumã
"""

import PyPDF2
from pathlib import Path

def extract_paper_content(paper_path, max_pages=5):
    """Extrai conteúdo textual de um paper PDF"""
    try:
        with open(paper_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            total_pages = len(reader.pages)
            
            content = {
                'title': paper_path.name,
                'total_pages': total_pages,
                'text': ''
            }
            
            # Ler primeiras páginas (abstract, intro, methodology)
            for i in range(min(max_pages, total_pages)):
                page_text = reader.pages[i].extract_text()
                content['text'] += page_text + '\n\n'
            
            return content
    except Exception as e:
        return {'title': paper_path.name, 'error': str(e)}

def analyze_papers():
    """Analisa todos os papers na pasta"""
    papers_dir = Path('papers')
    papers = list(papers_dir.glob('*.pdf'))
    
    print("=" * 80)
    print("📚 ANÁLISE DE PAPERS ACADÊMICOS SOBRE WEAK SIGNALS")
    print("=" * 80)
    print(f"\nTotal de papers encontrados: {len(papers)}\n")
    
    for paper_path in papers:
        print("\n" + "=" * 80)
        print(f"📄 {paper_path.name}")
        print("=" * 80)
        
        content = extract_paper_content(paper_path, max_pages=5)
        
        if 'error' in content:
            print(f"❌ Erro: {content['error']}")
            continue
        
        print(f"Páginas totais: {content['total_pages']}")
        print(f"Texto extraído: {len(content['text'])} caracteres")
        print("\n--- PRIMEIROS 3000 CARACTERES ---")
        print(content['text'][:3000])
        print("\n...")
        
        # Buscar conceitos-chave
        print("\n🔍 CONCEITOS-CHAVE DETECTADOS:")
        key_concepts = [
            'weak signal', 'trend', 'foresight', 'emergence', 
            'momentum', 'velocity', 'acceleration', 'clustering',
            'detection', 'prediction', 'forecast', 'scenario',
            'cultural', 'social', 'innovation', 'disruption',
            'machine learning', 'NLP', 'embedding', 'classification'
        ]
        
        text_lower = content['text'].lower()
        found_concepts = []
        for concept in key_concepts:
            count = text_lower.count(concept.lower())
            if count > 0:
                found_concepts.append((concept, count))
        
        found_concepts.sort(key=lambda x: x[1], reverse=True)
        for concept, count in found_concepts[:10]:
            print(f"   • {concept:20s}: {count:3d} menções")

if __name__ == '__main__':
    analyze_papers()
