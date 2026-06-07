# cultural_embedding_analyzer.py
"""
Cultural Embedding Analyzer

Este módulo implementa análise de embeddings culturais para detecção de padrões, similaridades e polaridades culturais em dados textuais ou contextuais.
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class CulturalEmbeddingAnalyzer:
    def __init__(self, embedding_model):
        """
        embedding_model: objeto com método .encode(text) -> np.ndarray
        """
        self.embedding_model = embedding_model

    def get_embedding(self, text):
        """Gera embedding para um texto."""
        return self.embedding_model.encode(text)

    def similarity(self, text1, text2):
        """Calcula similaridade de cosseno entre dois textos."""
        emb1 = self.get_embedding(text1).reshape(1, -1)
        emb2 = self.get_embedding(text2).reshape(1, -1)
        return float(cosine_similarity(emb1, emb2)[0][0])

    def batch_similarity(self, texts):
        """Matriz de similaridade entre múltiplos textos."""
        embeddings = [self.get_embedding(t) for t in texts]
        return cosine_similarity(embeddings)

    def detect_polarity(self, text, reference_texts):
        """
        Mede a polaridade cultural de um texto em relação a referências.
        Retorna score médio de similaridade.
        """
        emb = self.get_embedding(text).reshape(1, -1)
        ref_embs = [self.get_embedding(ref).reshape(1, -1) for ref in reference_texts]
        scores = [float(cosine_similarity(emb, ref)[0][0]) for ref in ref_embs]
        return float(np.mean(scores))

    def find_most_similar(self, text, candidates):
        """
        Retorna o texto mais similar dentre os candidatos.
        """
        emb = self.get_embedding(text).reshape(1, -1)
        candidate_embs = [self.get_embedding(c).reshape(1, -1) for c in candidates]
        sims = [float(cosine_similarity(emb, c)[0][0]) for c in candidate_embs]
        idx = int(np.argmax(sims))
        return candidates[idx], sims[idx]
