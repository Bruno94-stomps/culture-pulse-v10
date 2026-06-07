"""
SEMANTIC EXPANDER - DIMENSÃO 1
===============================

Expande relações semânticas usando BERTimbau embeddings.
Calcula cosine similarity para encontrar top-K conceitos relacionados.

Author: Culture Pulse V9
Date: 2026-02-03
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional
import logging
import numpy as np
from datetime import datetime

# Embeddings temporais (V9.1)
try:
    from core.engines.temporal_embedder import TemporalEmbedder
    HAS_TEMPORAL_EMBEDDER = True
except ImportError:
    HAS_TEMPORAL_EMBEDDER = False
    logging.warning("⚠️ TemporalEmbedder not available")

# S1.2 — pgvector cache (opcional; não bloqueia se Supabase indisponível)
try:
    from core.pgvector_cache import lookup as _pgvec_lookup, store as _pgvec_store
    _PGVECTOR_CACHE_AVAILABLE = True
except ImportError:
    _PGVECTOR_CACHE_AVAILABLE = False
    _pgvec_lookup = None
    _pgvec_store = None

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)


class SemanticExpander:
    """
    SEMANTIC EXPANDER - DIMENSÃO 1 DE CONTEXTUALIZAÇÃO
    
    Usa BERTimbau (BERT treinado em português brasileiro) para:
    - Gerar embeddings de 768 dimensões
    - Calcular cosine similarity entre termos
    - Retornar top-K conceitos semanticamente relacionados
    
    Features:
    - Cache de embeddings para performance
    - Fallback para relacionamentos hardcoded (desenvolvimento)
    - Support para batch processing
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa SemanticExpander
        
        Args:
            config: Configurações opcionais
                - use_bertimbau: bool (default True)
                - cache_embeddings: bool (default True)
                - min_similarity: float (default 0.5)
        """
        self.config = config or {}
        # FASE 3: BERTimbau ATIVADO POR PADRÃO (antes era False para fallback)
        self.use_bertimbau = self.config.get("use_bertimbau", True)  # ✅ MUDOU: False → True
        self.cache_enabled = self.config.get("cache_embeddings", True)
        self.min_similarity = self.config.get("min_similarity", 0.5)
        
        # Cache de embeddings
        self._embeddings_cache = {}
        
        # Modelo BERTimbau (lazy load)
        self._model = None
        self._tokenizer = None
        
        # Corpus de termos culturais brasileiros (para similaridade)
        self._cultural_corpus = self._load_cultural_corpus()
        
        # Temporal Embedder (V9.1) - Adiciona dimensões temporais (768d → 776d)
        self._temporal_embedder = None
        if HAS_TEMPORAL_EMBEDDER and self.config.get("use_temporal_embeddings", True):
            try:
                self._temporal_embedder = TemporalEmbedder()
                logger.info("✅ TemporalEmbedder integrado (768d → 776d)")
            except Exception as e:
                logger.warning(f"⚠️ TemporalEmbedder init failed: {e}")
        
        logger.info(f"✅ SemanticExpander inicializado (BERTimbau: {self.use_bertimbau})")
    
    def expand_relations(self, termo: str, top_k: int = 10) -> List[Dict]:
        """
        Expande relações semânticas do termo
        
        Args:
            termo: Termo para expandir
            top_k: Número de conceitos relacionados a retornar
        
        Returns:
            Lista de dicts: [{"termo": str, "similarity": float}, ...]
        """
        # Check cache primeiro
        cache_key = f"{termo.lower()}_{top_k}"
        if self.cache_enabled and cache_key in self._embeddings_cache:
            logger.debug(f"✅ Cache hit para '{termo}'")
            return self._embeddings_cache[cache_key]
        
        # Tenta usar BERTimbau
        if self.use_bertimbau:
            try:
                relations = self._expand_with_bertimbau(termo, top_k)
            except Exception as e:
                logger.warning(f"⚠️ BERTimbau falhou, usando fallback: {e}")
                relations = self._expand_with_fallback(termo, top_k)
        else:
            relations = self._expand_with_fallback(termo, top_k)
        
        # Cache resultado
        if self.cache_enabled:
            self._embeddings_cache[cache_key] = relations
        
        return relations
    
    def _expand_with_bertimbau(self, termo: str, top_k: int) -> List[Dict]:
        """
        Expansão usando BERTimbau real
        
        Args:
            termo: Termo para expandir
            top_k: Número de relacionamentos
        
        Returns:
            Lista de relacionamentos ordenada por similaridade
        """
        # Load modelo (lazy)
        if self._model is None:
            self._load_bertimbau_model()
        
        # Gera embedding do termo
        termo_embedding = self._get_embedding(termo)
        
        # Calcula similaridade com corpus
        similarities = []
        for corpus_term in self._cultural_corpus:
            if corpus_term.lower() == termo.lower():
                continue  # Skip próprio termo
            
            corpus_embedding = self._get_embedding(corpus_term)
            similarity = self._cosine_similarity(termo_embedding, corpus_embedding)
            
            if similarity >= self.min_similarity:
                similarities.append({
                    "termo": corpus_term,
                    "similarity": float(similarity)
                })
        
        # Ordena por similaridade e retorna top-K
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:top_k]
    
    def _load_bertimbau_model(self):
        """Carrega modelo BERTimbau (lazy loading)"""
        try:
            from transformers import AutoTokenizer, AutoModel
            import torch
            
            model_name = "neuralmind/bert-base-portuguese-cased"
            logger.info(f"🔄 Carregando BERTimbau: {model_name}...")
            
            self._tokenizer = AutoTokenizer.from_pretrained(model_name)
            self._model = AutoModel.from_pretrained(model_name)
            self._model.eval()  # Modo inference
            
            logger.info("✅ BERTimbau carregado com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar BERTimbau: {e}")
            raise
    
    def _get_embedding(self, text: str, timestamp: Optional[datetime] = None) -> np.ndarray:
        """
        Gera embedding usando BERTimbau (768d ou 776d com temporal).

        Pipeline S1.2:
          1. Consulta cache pgvector no Supabase  → cache HIT: retorna imediatamente
          2. Computa embedding via BERTimbau       → cache MISS: roda o modelo
          3. Persiste no pgvector para próxima vez
          4. Aplica componentes temporais (V9.1)   → +8d se timestamp fornecido

        Args:
            text:      Texto para embedar.
            timestamp: Data/hora para temporal embeddings (opcional).

        Returns:
            numpy array (768,) sem temporal ou (776,) com temporal.
        """
        import torch

        # ── S1.2: consultar pgvector cache ANTES de rodar o modelo ──────────
        if _PGVECTOR_CACHE_AVAILABLE and _pgvec_lookup is not None:
            cached_vec = _pgvec_lookup(text)
            if cached_vec is not None:
                # Aplica temporal se necessário e retorna
                if self._temporal_embedder and timestamp:
                    try:
                        return self._temporal_embedder.encode_with_time(
                            cached_vec, timestamp, include_events=True
                        )
                    except Exception:
                        pass
                return cached_vec

        # ── Computar embedding via BERTimbau ─────────────────────────────────
        # S1.4: dynamic padding — sem max_length fixo. Termos culturais têm
        # 3-9 tokens reais; padding fixo em 128 gerava ~93-98% de tokens
        # desnecessários. O(n²) de atenção → 202x menos operações para "funk".
        inputs = self._tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
        )

        with torch.no_grad():
            outputs = self._model(**inputs)

        # [CLS] token embedding — primeira posição, shape (768,)
        embedding = outputs.last_hidden_state[0, 0, :].numpy()

        # ── S1.2: persistir embedding no pgvector (best-effort) ──────────────
        if _PGVECTOR_CACHE_AVAILABLE and _pgvec_store is not None:
            try:
                _pgvec_store(text, embedding)
            except Exception as _pgvec_exc:
                logger.debug(f"pgvector store falhou (não crítico): {_pgvec_exc}")

        # ── V9.1: adicionar componentes temporais se disponível ───────────────
        if self._temporal_embedder and timestamp:
            try:
                embedding = self._temporal_embedder.encode_with_time(
                    embedding,
                    timestamp,
                    include_events=True
                )
                # Agora embedding tem 776 dimensões (768 + 8 temporal)
            except Exception as e:
                logger.warning(f"⚠️ Temporal encoding failed: {e}")

        return embedding
    
    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """
        Calcula cosine similarity entre dois vetores
        
        Args:
            a, b: Arrays numpy
        
        Returns:
            Similaridade (0-1)
        """
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def _expand_with_fallback(self, termo: str, top_k: int) -> List[Dict]:
        """
        Fallback: relacionamentos hardcoded para desenvolvimento
        
        Args:
            termo: Termo para expandir
            top_k: Número de relacionamentos
        
        Returns:
            Lista de relacionamentos mock
        """
        # Dicionário de relacionamentos culturais brasileiros
        fallback_relations = {
            "sustentabilidade afetiva": [
                ("economia do cuidado", 0.85),
                ("bem-estar coletivo", 0.82),
                ("comunidades afetivas", 0.78),
                ("consumo consciente", 0.76),
                ("relações regenerativas", 0.74),
                ("empatia ativa", 0.72),
                ("capital social", 0.70),
                ("vínculo comunitário", 0.68),
                ("solidariedade prática", 0.66),
                ("conexão autêntica", 0.64)
            ],
            "co-living": [
                ("moradia compartilhada", 0.88),
                ("economia colaborativa", 0.82),
                ("comunidades intencionais", 0.80),
                ("vida coletiva", 0.78),
                ("espaços comuns", 0.75),
                ("sharing economy", 0.73),
                ("housing cooperativo", 0.71),
                ("vizinhança ativa", 0.69),
                ("design social", 0.67),
                ("pertencimento local", 0.65)
            ],
            "ansiedade climática": [
                ("eco-ansiedade", 0.92),
                ("crise ambiental", 0.85),
                ("futuro sustentável", 0.80),
                ("consciência ecológica", 0.78),
                ("ativismo climático", 0.76),
                ("desespero existencial", 0.74),
                ("responsabilidade geracional", 0.72),
                ("colapso ecológico", 0.70),
                ("ação climática", 0.68),
                ("esperança ativa", 0.66)
            ],
            "música periférica": [
                ("funk carioca", 0.88),
                ("rap nacional", 0.86),
                ("cultura de favela", 0.84),
                ("movimento hip-hop", 0.82),
                ("batida periférica", 0.80),
                ("resistência cultural", 0.78),
                ("voz das quebradas", 0.76),
                ("autenticidade marginal", 0.74),
                ("música de protesto", 0.72),
                ("identidade favelada", 0.70)
            ],
            # Padrão genérico
            "default": [
                ("conceito relacionado A", 0.70),
                ("conceito relacionado B", 0.68),
                ("conceito relacionado C", 0.66),
                ("conceito relacionado D", 0.64),
                ("conceito relacionado E", 0.62),
                ("conceito relacionado F", 0.60),
                ("conceito relacionado G", 0.58),
                ("conceito relacionado H", 0.56),
                ("conceito relacionado I", 0.54),
                ("conceito relacionado J", 0.52)
            ]
        }
        
        # Busca relacionamentos
        relations_data = fallback_relations.get(termo.lower(), fallback_relations["default"])
        
        # Formata resultado
        relations = [
            {"termo": t, "similarity": sim}
            for t, sim in relations_data[:top_k]
        ]
        
        logger.debug(f"✅ Fallback gerou {len(relations)} relações para '{termo}'")
        return relations
    
    def _load_cultural_corpus(self) -> List[str]:
        """
        Carrega corpus de termos culturais brasileiros
        
        Returns:
            Lista de termos culturais
        """
        # Corpus inicial - pode ser expandido via arquivo externo
        corpus = [
            # Círculos culturais
            "família", "tradições", "comunidade", "vizinhança", "espiritualidade",
            "educação", "conhecimento", "música", "festivais", "esporte",
            "gastronomia", "arte", "criatividade", "trabalho", "prosperidade",
            "relacionamentos", "afeto", "status", "reconhecimento", "ambições",
            "sustentabilidade", "consumo", "tecnologia", "digital", "saúde",
            "bem-estar", "diversidade", "inclusão",
            
            # Tendências culturais
            "economia do cuidado", "co-living", "ansiedade climática",
            "música periférica", "sustentabilidade afetiva", "slow living",
            "desconexão digital", "autenticidade", "transparência radical",
            "economia circular", "consumo consciente", "minimalismo",
            
            # Comportamentos emergentes
            "compartilhamento", "colaboração", "empatia", "solidariedade",
            "pertencimento", "identidade", "expressão", "criação",
            "curadoria", "personalização", "conexão", "engajamento",
            
            # Valores brasileiros
            "brasilidade", "jeitinho brasileiro", "alegria", "otimismo",
            "resiliência", "improvisação", "criatividade", "diversidade",
            "miscigenação", "sincretismo", "hospitalidade", "calor humano"
        ]
        
        return corpus
    
    def batch_expand(self, termos: List[str], top_k: int = 10) -> Dict[str, List[Dict]]:
        """
        Expande múltiplos termos em batch
        
        Args:
            termos: Lista de termos
            top_k: Número de relacionamentos por termo
        
        Returns:
            Dict {termo: [relacionamentos]}
        """
        results = {}
        for termo in termos:
            results[termo] = self.expand_relations(termo, top_k)
        
        return results
    
    def get_cache_stats(self) -> Dict:
        """Retorna estatísticas do cache"""
        return {
            "cache_enabled": self.cache_enabled,
            "cached_terms": len(self._embeddings_cache),
            "corpus_size": len(self._cultural_corpus)
        }


# ========== STANDALONE TESTING ==========

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 Testando SemanticExpander...")
    
    # Teste com fallback (sem BERTimbau)
    expander = SemanticExpander(config={"use_bertimbau": False})
    
    test_terms = [
        "sustentabilidade afetiva",
        "co-living",
        "ansiedade climática"
    ]
    
    for term in test_terms:
        print(f"\n📍 Termo: {term}")
        relations = expander.expand_relations(term, top_k=5)
        
        for i, rel in enumerate(relations, 1):
            print(f"   {i}. {rel['termo']} (similaridade: {rel['similarity']:.2f})")
    
    # Stats
    stats = expander.get_cache_stats()
    print(f"\n📊 Cache stats: {stats}")
    
    # Batch test
    print("\n🔄 Testando batch processing...")
    batch_results = expander.batch_expand(["sustentabilidade afetiva", "música periférica"], top_k=3)
    print(f"   Processados {len(batch_results)} termos")
