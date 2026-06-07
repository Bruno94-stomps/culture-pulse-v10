#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TF-IDF Cultural Analyzer - Culture Pulse V8.0
Analisador TF-IDF especializado em cultura brasileira

🎯 RESPONSABILIDADES:
- Análise TF-IDF cultural avançada
- Detecção de termos culturais relevantes
- Análise de tendências linguísticas
- Score de relevância cultural
"""

from typing import Dict, List, Any, Tuple, Optional
import numpy as np
import re
from collections import Counter, defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

class TFIDFCulturalAnalyzer:
    """
    Analisador TF-IDF especializado em cultura brasileira
    Integra com os círculos culturais para análise semântica
    """
    
    def __init__(self):
        """Inicializa o analisador TF-IDF cultural"""
        
        # Termos culturais brasileiros categorizados
        self.cultural_terms = {
            'musica': [
                'samba', 'forró', 'axé', 'frevo', 'funk', 'bossa nova', 'mpb',
                'pagode', 'reggae', 'rap', 'hip hop', 'rock', 'pop', 'eletrônica',
                'baião', 'xote', 'mambo', 'lambada', 'zouk', 'arrocha'
            ],
            'festas': [
                'carnaval', 'festa junina', 'reveillon', 'micareta', 'bloco',
                'trio elétrico', 'marchinha', 'quadrilha', 'fogueira', 'balão',
                'festa', 'celebração', 'comemoração', 'folia', 'farra'
            ],
            'culinaria': [
                'feijoada', 'churrasco', 'pão de açúcar', 'brigadeiro', 'açaí',
                'coxinha', 'pastel', 'caipirinha', 'guaraná', 'mate', 'cafezinho',
                'tapioca', 'acarajé', 'moqueca', 'farofa', 'picanha'
            ],
            'esportes': [
                'futebol', 'pelé', 'copa do mundo', 'maracanã', 'flamengo',
                'corinthians', 'palmeiras', 'santos', 'vasco', 'são paulo',
                'surf', 'vôlei', 'capoeira', 'jiu-jitsu', 'futsal'
            ],
            'lugares': [
                'rio de janeiro', 'são paulo', 'bahia', 'nordeste', 'amazônia',
                'pantanal', 'cerrado', 'mata atlântica', 'copacabana', 'ipanema',
                'cristo redentor', 'pão de açúcar', 'iguaçu', 'fernando de noronha'
            ],
            'cultura_popular': [
                'jeitinho brasileiro', 'malandragem', 'cordialidade', 'saudade',
                'ginga', 'axé', 'energia', 'simpatia', 'hospitalidade', 'calor humano',
                'brasilidade', 'tropicalismo', 'miscigenação', 'diversidade'
            ]
        }
        
        # Stopwords brasileiras específicas
        self.cultural_stopwords = {
            'é', 'do', 'da', 'de', 'para', 'com', 'em', 'no', 'na', 'um', 'uma',
            'esse', 'essa', 'isso', 'aquele', 'aquela', 'muito', 'mais', 'bem',
            'já', 'ainda', 'só', 'também', 'mas', 'porque', 'quando', 'onde'
        }
        
        # Configurar TF-IDF
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words=list(self.cultural_stopwords),
            ngram_range=(1, 2),
            lowercase=True,
            strip_accents='unicode'
        )
        
        # Cache para performance
        self._analysis_cache = {}
        
        logger.info("📊 TF-IDF Cultural Analyzer inicializado")
    
    def analyze_cultural_relevance(
        self,
        raw_data: Dict[str, Any],
        circles_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Análise de relevância cultural usando TF-IDF
        
        Args:
            raw_data: Dados brutos das plataformas
            circles_analysis: Resultado da análise dos círculos
            
        Returns:
            Dict com análise TF-IDF completa
        """
        logger.info("📊 Iniciando análise TF-IDF cultural")
        
        try:
            # 1. Extrair textos de todas as plataformas
            documents = self._extract_documents(raw_data)
            
            if not documents:
                return self._empty_tfidf_result()
            
            # 2. Aplicar TF-IDF
            tfidf_results = self._apply_tfidf_analysis(documents)
            
            # 3. Identificar termos culturais relevantes
            cultural_terms = self._identify_cultural_terms(tfidf_results)
            
            # 4. Calcular relevância cultural
            cultural_relevance = self._calculate_cultural_relevance(
                cultural_terms, circles_analysis
            )
            
            # 5. Detectar tendências
            trends_analysis = self._detect_cultural_trends(cultural_terms)
            
            # 6. Análise semântica
            semantic_analysis = self._analyze_semantic_patterns(tfidf_results, cultural_terms)
            
            result = {
                'relevance_score': cultural_relevance['overall_score'],
                'cultural_terms': cultural_terms,
                'trends': trends_analysis['emerging_trends'],
                'semantic_patterns': semantic_analysis,
                'tfidf_scores': tfidf_results['top_terms'],
                'cultural_categories': cultural_relevance['category_scores'],
                'processing_metadata': {
                    'documents_analyzed': len(documents),
                    'terms_extracted': len(tfidf_results['top_terms']),
                    'cultural_terms_found': len(cultural_terms)
                }
            }
            
            logger.info(f"✅ TF-IDF concluído - Relevância: {cultural_relevance['overall_score']:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro na análise TF-IDF: {e}")
            return self._empty_tfidf_result()
    
    def _extract_documents(self, raw_data: Dict[str, Any]) -> List[str]:
        """Extrai documentos de texto de todas as plataformas"""
        documents = []
        
        for platform, data in raw_data.items():
            if not isinstance(data, dict):
                continue
                
            platform_texts = []
            
            if platform == 'youtube':
                # Comentários do YouTube
                for comment in data.get('comments', []):
                    text = comment.get('text', '').strip()
                    if text and len(text) > 10:  # Filtrar comentários muito curtos
                        platform_texts.append(text)
            
            elif platform == 'reddit':
                # Posts e comentários do Reddit
                for post in data.get('posts', []):
                    title = post.get('title', '').strip()
                    content = post.get('content', '').strip()
                    combined = f"{title} {content}".strip()
                    if combined and len(combined) > 10:
                        platform_texts.append(combined)
            
            elif platform == 'news':
                # Artigos de notícias
                for article in data.get('articles', []):
                    title = article.get('title', '').strip()
                    content = article.get('content', '').strip()
                    combined = f"{title} {content}".strip()
                    if combined and len(combined) > 20:
                        platform_texts.append(combined)
            
            elif platform == 'spotify':
                # Nomes de músicas e playlists
                for track in data.get('tracks', []):
                    name = track.get('name', '').strip()
                    if name:
                        platform_texts.append(name)
            
            # Adicionar textos da plataforma aos documentos
            if platform_texts:
                # Combinar textos por plataforma para manter contexto
                combined_platform_text = ' '.join(platform_texts)
                documents.append(combined_platform_text)
        
        return documents
    
    def _apply_tfidf_analysis(self, documents: List[str]) -> Dict[str, Any]:
        """Aplica análise TF-IDF aos documentos"""
        
        # Ajustar TF-IDF se poucos documentos
        if len(documents) < 2:
            # Para um documento apenas, usar análise de frequência simples
            return self._simple_frequency_analysis(documents[0] if documents else "")
        
        # Aplicar TF-IDF normal
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
        feature_names = self.tfidf_vectorizer.get_feature_names_out()
        
        # Calcular scores médios por termo
        mean_scores = tfidf_matrix.mean(axis=0).A1
        
        # Top termos com scores
        top_indices = mean_scores.argsort()[-50:][::-1]  # Top 50
        top_terms = [
            {
                'term': feature_names[i],
                'score': mean_scores[i],
                'frequency': np.sum(tfidf_matrix[:, i] > 0)
            }
            for i in top_indices if mean_scores[i] > 0.01  # Filtrar scores muito baixos
        ]
        
        return {
            'top_terms': top_terms,
            'tfidf_matrix': tfidf_matrix,
            'feature_names': feature_names,
            'documents_count': len(documents)
        }

    def apply_topic_modeling(self, documents: List[str], n_topics: int = 8, max_features: int = 1000) -> Dict[str, Any]:
        """Apply LDA topic modeling on a list of documents.

        This method complements TF-IDF by producing topic distributions
        which are useful for hierarchical grouping, dashboards and
        temporal topic tracking.

        Returns a dict with 'topics' (list of terms per topic) and
        'doc_topic_matrix' (documents x topics distribution).
        """
        if not documents:
            return {'topics': [], 'doc_topic_matrix': None}

        # Use CountVectorizer as LDA input
        vectorizer = CountVectorizer(max_features=max_features, stop_words=list(self.cultural_stopwords))
        X = vectorizer.fit_transform(documents)

        lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
        doc_topic = lda.fit_transform(X)

        feature_names = vectorizer.get_feature_names_out()
        topics = []
        for topic_idx, topic in enumerate(lda.components_):
            top_indices = topic.argsort()[-10:][::-1]
            topics.append({
                'topic_id': topic_idx,
                'terms': [feature_names[i] for i in top_indices]
            })

        return {
            'topics': topics,
            'doc_topic_matrix': doc_topic,
            'n_topics': n_topics
        }
    
    def _simple_frequency_analysis(self, text: str) -> Dict[str, Any]:
        """Análise de frequência simples para poucos documentos"""
        
        # Limpar e tokenizar texto
        clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = [word for word in clean_text.split() if len(word) > 2 and word not in self.cultural_stopwords]
        
        # Contar frequências
        word_freq = Counter(words)
        total_words = len(words)
        
        # Criar lista de termos com scores normalizados
        top_terms = [
            {
                'term': word,
                'score': count / total_words,
                'frequency': count
            }
            for word, count in word_freq.most_common(50)
        ]
        
        return {
            'top_terms': top_terms,
            'tfidf_matrix': None,
            'feature_names': [],
            'documents_count': 1
        }
    
    def _identify_cultural_terms(self, tfidf_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identifica termos culturais relevantes nos resultados TF-IDF"""
        
        cultural_terms_found = []
        top_terms = tfidf_results['top_terms']
        
        for term_data in top_terms:
            term = term_data['term'].lower()
            
            # Verificar se o termo está nas categorias culturais
            for category, terms_list in self.cultural_terms.items():
                for cultural_term in terms_list:
                    if cultural_term.lower() in term or term in cultural_term.lower():
                        cultural_terms_found.append({
                            'term': term,
                            'cultural_category': category,
                            'tfidf_score': term_data['score'],
                            'frequency': term_data['frequency'],
                            'cultural_match': cultural_term
                        })
                        break
        
        # Remover duplicatas e ordenar por score
        unique_terms = {}
        for term_data in cultural_terms_found:
            key = term_data['term']
            if key not in unique_terms or term_data['tfidf_score'] > unique_terms[key]['tfidf_score']:
                unique_terms[key] = term_data
        
        return sorted(unique_terms.values(), key=lambda x: x['tfidf_score'], reverse=True)
    
    def _calculate_cultural_relevance(
        self,
        cultural_terms: List[Dict[str, Any]],
        circles_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calcula relevância cultural baseada nos termos e círculos"""
        
        if not cultural_terms:
            return {'overall_score': 0.0, 'category_scores': {}}
        
        # Scores por categoria cultural
        category_scores = defaultdict(float)
        category_counts = defaultdict(int)
        
        for term_data in cultural_terms:
            category = term_data['cultural_category']
            score = term_data['tfidf_score']
            
            category_scores[category] += score
            category_counts[category] += 1
        
        # Normalizar scores por categoria
        normalized_category_scores = {
            category: score / category_counts[category]
            for category, score in category_scores.items()
        }
        
        # Score cultural geral (média ponderada)
        total_score = sum(normalized_category_scores.values())
        num_categories = len(normalized_category_scores)
        overall_score = total_score / num_categories if num_categories > 0 else 0.0
        
        # Bonus se alinhado com círculos dominantes
        circles_bonus = self._calculate_circles_alignment_bonus(
            normalized_category_scores, circles_analysis
        )
        
        final_score = min(overall_score + circles_bonus, 1.0)
        
        return {
            'overall_score': final_score,
            'category_scores': dict(normalized_category_scores),
            'circles_alignment_bonus': circles_bonus
        }
    
    def _calculate_circles_alignment_bonus(
        self,
        category_scores: Dict[str, float],
        circles_analysis: Dict[str, Any]
    ) -> float:
        """Calcula bônus de alinhamento com círculos culturais"""
        
        # Mapear categorias TF-IDF para círculos culturais
        category_to_circles = {
            'musica': ['musicalidade_expressao', 'alegria_celebracao'],
            'festas': ['alegria_celebracao', 'sociocultural'],
            'culinaria': ['afeto_hospitalidade', 'sociocultural'],
            'esportes': ['emocional_comportamental', 'sociocultural'],
            'cultura_popular': ['sincretismo_cultural', 'diversidade_contradicao']
        }
        
        bonus = 0.0
        circles_scores = circles_analysis.get('circles_scores', {})
        
        for category, score in category_scores.items():
            if category in category_to_circles:
                related_circles = category_to_circles[category]
                
                # Calcular média dos círculos relacionados
                circle_avg = np.mean([
                    circles_scores.get(circle, {}).get('score', 0.0)
                    for circle in related_circles
                ])
                
                # Adicionar bônus proporcional
                bonus += score * circle_avg * 0.1  # Máximo 10% de bônus
        
        return min(bonus, 0.2)  # Máximo 20% de bônus total
    
    def _detect_cultural_trends(self, cultural_terms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detecta tendências culturais baseadas nos termos"""
        
        # Agrupar por categoria
        trends_by_category = defaultdict(list)
        for term_data in cultural_terms:
            category = term_data['cultural_category']
            trends_by_category[category].append(term_data)
        
        # Identificar tendências emergentes (alta frequência + alto score)
        emerging_trends = []
        for category, terms in trends_by_category.items():
            if len(terms) >= 2:  # Categoria com pelo menos 2 termos
                avg_score = np.mean([t['tfidf_score'] for t in terms])
                if avg_score > 0.1:  # Threshold para tendência emergente
                    emerging_trends.append({
                        'category': category,
                        'strength': avg_score,
                        'terms': [t['term'] for t in terms[:3]]  # Top 3 termos
                    })
        
        # Ordenar por força
        emerging_trends.sort(key=lambda x: x['strength'], reverse=True)
        
        return {
            'emerging_trends': emerging_trends,
            'total_categories': len(trends_by_category),
            'strongest_trend': emerging_trends[0] if emerging_trends else None
        }
    
    def _analyze_semantic_patterns(
        self,
        tfidf_results: Dict[str, Any],
        cultural_terms: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analisa padrões semânticos nos textos"""
        
        # Padrões linguísticos brasileiros
        brazilian_patterns = {
            'positive_expressions': ['legal', 'massa', 'show', 'top', 'demais', 'bacana'],
            'intensifiers': ['muito', 'super', 'mega', 'hiper', 'ultra', 'demais'],
            'colloquialisms': ['né', 'cara', 'mano', 'véi', 'galera', 'pessoal']
        }
        
        pattern_scores = {}
        top_terms = [t['term'] for t in tfidf_results['top_terms']]
        
        for pattern_type, pattern_words in brazilian_patterns.items():
            matches = [word for word in pattern_words if any(word in term for term in top_terms)]
            pattern_scores[pattern_type] = len(matches) / len(pattern_words)
        
        # Score de brasilidade linguística
        brasilidade_score = np.mean(list(pattern_scores.values()))
        
        return {
            'pattern_scores': pattern_scores,
            'brasilidade_linguistica': brasilidade_score,
            'linguistic_authenticity': 'alta' if brasilidade_score > 0.3 else 'média' if brasilidade_score > 0.1 else 'baixa'
        }
    
    def _empty_tfidf_result(self) -> Dict[str, Any]:
        """Retorna resultado vazio em caso de erro"""
        return {
            'relevance_score': 0.0,
            'cultural_terms': [],
            'trends': [],
            'semantic_patterns': {},
            'tfidf_scores': [],
            'cultural_categories': {},
            'processing_metadata': {'error': True}
        }


# Factory function
def create_tfidf_analyzer() -> TFIDFCulturalAnalyzer:
    """Cria instância do analisador TF-IDF"""
    return TFIDFCulturalAnalyzer()


# Para testes diretos
if __name__ == "__main__":
    analyzer = create_tfidf_analyzer()
    
    # Teste com dados simulados
    test_data = {
        'youtube': {
            'comments': [
                {'text': 'Que samba maravilhoso! Show de bola, cara!'},
                {'text': 'Forró é massa demais, né não? Alegria pura!'},
                {'text': 'Carnaval no Rio é o máximo! Festa linda!'}
            ]
        },
        'reddit': {
            'posts': [
                {'title': 'Feijoada de domingo', 'content': 'Tradição brasileira que nunca sai de moda'},
                {'title': 'Futebol brasileiro', 'content': 'A ginga que o mundo admira'}
            ]
        }
    }
    
    # Análise dos círculos simulada
    circles_analysis = {
        'circles_scores': {
            'musicalidade_expressao': {'score': 0.8},
            'alegria_celebracao': {'score': 0.9}
        }
    }
    
    result = analyzer.analyze_cultural_relevance(test_data, circles_analysis)
    
    print(f"📊 Relevância Cultural: {result['relevance_score']:.2f}")
    print(f"🎯 Termos Culturais: {len(result['cultural_terms'])}")
    print(f"📈 Tendências: {len(result['trends'])}")
    print("✅ TF-IDF Analyzer funcionando!")
