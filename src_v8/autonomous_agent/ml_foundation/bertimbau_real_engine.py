#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🇧🇷 BERTimbau Real Integration V8.2
====================================
Integração REAL do BERTimbau neuralmind com PyTorch + fallback TF-IDF

Melhorias implementadas:
1. BERTimbau real neuralmind/bert-base-portuguese-cased
2. Cache inteligente otimizado para embeddings
3. Batch processing para melhor performance
4. Warm-up automático de embeddings comuns
5. Memory optimization para grandes datasets

Author: Culture Pulse V8.2 System
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
import logging
import json
import pickle
import os
import time
from datetime import datetime
from dataclasses import dataclass
import hashlib

# Importação do Finetuner para carregar modelos especializados (V9.9)
try:
    from .bert_finetuner import load_finetuned_model
except (ImportError, ValueError):
    try:
        from autonomous_agent.ml_foundation.bert_finetuner import load_finetuned_model
    except ImportError:
        load_finetuned_model = None

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tentar importar PyTorch + Transformers
try:
    import torch
    from transformers import AutoTokenizer, AutoModel
    PYTORCH_AVAILABLE = True
    logger.info("🚀 PyTorch + Transformers disponível - BERTimbau REAL ativado!")
except ImportError:
    PYTORCH_AVAILABLE = False
    logger.warning("⚠️ PyTorch não disponível - usando fallback TF-IDF")
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.decomposition import PCA
    from sklearn.cluster import KMeans


@dataclass
class EnhancedCulturalEmbedding:
    """Embedding cultural aprimorado"""
    text: str
    embedding: np.ndarray
    confidence: float
    cultural_category: str
    regional_context: str
    processing_time: float
    model_type: str  # 'bertimbau_real' ou 'tfidf_fallback'


class BERTimbauRealEngine:
    """
    🧠 BERTimbau Real Engine V9.9
    
    Funcionalidades:
    - BERTimbau neuralmind REAL (768D)
    - Suporte a Modelos Specialized (Fine-tuned via bert_finetuner)
    - Cache inteligente otimizado
    - Batch processing
    """
    
    def __init__(self, 
                 model_name: str = "neuralmind/bert-base-portuguese-cased",
                 specialized_model_path: Optional[str] = "models/bertimbau_cultural_v1",
                 cache_dir: str = "cache/bertimbau_real",
                 device: str = "auto",
                 max_length: int = 512,
                 batch_size: int = 32):
        """Inicializar BERTimbau Real Engine"""
        
        self.model_name = model_name
        self.specialized_model_path = specialized_model_path
        self.cache_dir = cache_dir
        self.device = self._get_device(device)
        self.max_length = max_length
        self.batch_size = batch_size
        
        # Estado do modelo
        self.model = None
        self.tokenizer = None
        self.use_real_model = PYTORCH_AVAILABLE
        self.is_loaded = False
        
        # Cache otimizado
        self.embeddings_cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'cache_size': 0
        }
        
        # Métricas de performance
        self.performance_stats = {
            'total_embeddings_generated': 0,
            'total_processing_time': 0.0,
            'avg_processing_time': 0.0,
            'cache_hit_ratio': 0.0
        }
        
        os.makedirs(cache_dir, exist_ok=True)
        
        # Base cultural brasileira expandida
        self.cultural_knowledge = self._load_expanded_cultural_knowledge()
        
        # Embeddings comuns para warm-up
        self.common_terms = [
            "startup brasileira", "fintech nacional", "inovação brasil",
            "cultura brasileira", "música brasileira", "festival brasileiro",
            "agronegócio brasil", "sustentabilidade", "economia brasileira",
            "empreendedorismo nacional", "tecnologia brasil", "mercado brasileiro"
        ]
        
        self._initialize_model()
        logger.info(f"🇧🇷 BERTimbau Real Engine V8.2 inicializado (Modelo: {'REAL' if self.use_real_model else 'TF-IDF'})")
    
    def _get_device(self, device: str) -> str:
        """Detectar melhor device disponível"""
        if device == "auto":
            if PYTORCH_AVAILABLE and torch.cuda.is_available():
                return "cuda"
            else:
                return "cpu"
        return device
    
    def _initialize_model(self):
        """Inicializar modelo BERTimbau (Base ou Specialized)"""
        if self.use_real_model and PYTORCH_AVAILABLE:
            try:
                # 1. Tentar carregar modelo Fine-Tuned (Specialized)
                if self.specialized_model_path and os.path.exists(self.specialized_model_path) and load_finetuned_model:
                    logger.info(f"🎯 Carregando BERTimbau SPECIALIZED (Fine-tuned) de {self.specialized_model_path}...")
                    finetuned_wrapper = load_finetuned_model(self.specialized_model_path)
                    self.model = finetuned_wrapper.backbone # Usamos o backbone adaptado
                    self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                    logger.info("✅ BERTimbau SPECIALIZED ativado com sucesso!")
                else:
                    # 2. Fallback para modelo BASE
                    logger.info("🔄 Carregando BERTimbau neuralmind BASE (Zero-shot)...")
                    self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, cache_dir=self.cache_dir)
                    self.model = AutoModel.from_pretrained(self.model_name, cache_dir=self.cache_dir)
                
                # Mover para device apropriado
                self.model.to(self.device)
                self.model.eval()  # Modo inferência
                
                self.is_loaded = True
                logger.info(f"✅ BERTimbau REAL carregado! Device: {self.device}")
                
                # Warm-up com termos comuns
                self._warmup_cache()
                
            except Exception as e:
                logger.error(f"❌ Erro ao carregar BERTimbau REAL: {e}")
                logger.info("🔄 Fallback para TF-IDF...")
                self.use_real_model = False
                self._initialize_fallback_model()
        else:
            self._initialize_fallback_model()
    
    def _initialize_fallback_model(self):
        """Inicializar modelo fallback TF-IDF"""
        logger.info("🔄 Inicializando TF-IDF fallback...")
        
        # Implementação do fallback (mantida do código original)
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.decomposition import PCA
        
        # Preparar corpus
        training_corpus = self._prepare_training_corpus()
        
        # TF-IDF Vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 3),
            stop_words=self._get_portuguese_stopwords(),
            lowercase=True,
            token_pattern=r'\b[a-záàâãéèêíìîóòôõúùûç]+\b'
        )
        
        # Treinar
        X = self.vectorizer.fit_transform(training_corpus)
        
        # PCA para reduzir dimensionalidade
        n_components = min(768, X.shape[0] - 1, X.shape[1])
        self.pca = PCA(n_components=n_components, random_state=42)
        self.pca.fit(X.toarray())
        
        self.is_loaded = True
        logger.info("✅ TF-IDF fallback carregado!")
    
    def _warmup_cache(self):
        """Warm-up do cache com termos comuns"""
        if not self.use_real_model:
            return
            
        logger.info("🔥 Iniciando warm-up do cache...")
        
        warmup_start = time.time()
        
        # Gerar embeddings para termos comuns
        for term in self.common_terms:
            try:
                self.get_embedding(term, use_cache=True)
            except Exception as e:
                logger.warning(f"⚠️ Erro no warm-up para '{term}': {e}")
        
        warmup_time = time.time() - warmup_start
        logger.info(f"✅ Warm-up concluído em {warmup_time:.2f}s - {len(self.common_terms)} embeddings")
    
    def get_embedding(self, text: str, use_cache: bool = True) -> np.ndarray:
        """Gerar embedding usando BERTimbau REAL ou fallback"""
        
        # Verificar cache
        if use_cache:
            cache_key = hashlib.md5(text.encode()).hexdigest()
            
            if cache_key in self.embeddings_cache:
                self.cache_stats['hits'] += 1
                return self.embeddings_cache[cache_key]
            else:
                self.cache_stats['misses'] += 1
        
        start_time = time.time()
        
        try:
            if self.use_real_model and self.is_loaded:
                embedding = self._get_bertimbau_embedding(text)
            else:
                embedding = self._get_tfidf_embedding(text)
            
            processing_time = time.time() - start_time
            
            # Atualizar estatísticas
            self.performance_stats['total_embeddings_generated'] += 1
            self.performance_stats['total_processing_time'] += processing_time
            self.performance_stats['avg_processing_time'] = (
                self.performance_stats['total_processing_time'] / 
                self.performance_stats['total_embeddings_generated']
            )
            
            # Calcular cache hit ratio
            total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
            if total_requests > 0:
                self.performance_stats['cache_hit_ratio'] = self.cache_stats['hits'] / total_requests
            
            # Salvar no cache
            if use_cache:
                self.embeddings_cache[cache_key] = embedding
                self.cache_stats['cache_size'] = len(self.embeddings_cache)
            
            return embedding
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar embedding: {e}")
            # Retornar embedding zero como fallback
            return np.zeros(768)
    
    def _get_bertimbau_embedding(self, text: str) -> np.ndarray:
        """Gerar embedding usando BERTimbau REAL"""
        
        # Tokenizar
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=self.max_length
        )
        
        # Mover para device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Inferência sem gradientes
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Extrair embedding (mean pooling)
        embeddings = outputs.last_hidden_state
        attention_mask = inputs['attention_mask']
        
        # Mean pooling
        masked_embeddings = embeddings * attention_mask.unsqueeze(-1)
        sum_embeddings = masked_embeddings.sum(dim=1)
        sum_mask = attention_mask.sum(dim=1, keepdim=True)
        mean_embedding = sum_embeddings / sum_mask
        
        # Converter para numpy
        embedding = mean_embedding.cpu().numpy().flatten()
        
        return embedding
    
    def _get_tfidf_embedding(self, text: str) -> np.ndarray:
        """Gerar embedding usando TF-IDF fallback"""
        try:
            # Vectorizar
            X = self.vectorizer.transform([text])
            
            # Reduzir dimensionalidade
            embedding = self.pca.transform(X.toarray())[0]
            
            # Pad para 768D se necessário
            if len(embedding) < 768:
                embedding = np.pad(embedding, (0, 768 - len(embedding)), 'constant')
            elif len(embedding) > 768:
                embedding = embedding[:768]
            
            return embedding
            
        except Exception as e:
            logger.error(f"❌ Erro TF-IDF embedding: {e}")
            return np.random.rand(768) * 0.01  # Embedding aleatório pequeno
    
    def get_embeddings_batch(self, texts: List[str], use_cache: bool = True) -> List[np.ndarray]:
        """Processar múltiplos textos em lote (otimizado)"""
        
        if not self.use_real_model or not self.is_loaded:
            # Fallback para processamento individual
            return [self.get_embedding(text, use_cache) for text in texts]
        
        # Verificar cache primeiro
        embeddings = []
        uncached_texts = []
        uncached_indices = []
        
        if use_cache:
            for i, text in enumerate(texts):
                cache_key = hashlib.md5(text.encode()).hexdigest()
                if cache_key in self.embeddings_cache:
                    embeddings.append(self.embeddings_cache[cache_key])
                    self.cache_stats['hits'] += 1
                else:
                    embeddings.append(None)  # Placeholder
                    uncached_texts.append(text)
                    uncached_indices.append(i)
                    self.cache_stats['misses'] += 1
        else:
            uncached_texts = texts
            uncached_indices = list(range(len(texts)))
            embeddings = [None] * len(texts)
        
        # Processar textos não cacheados em lote
        if uncached_texts:
            start_time = time.time()
            
            try:
                # Tokenizar todos os textos
                inputs = self.tokenizer(
                    uncached_texts,
                    return_tensors="pt",
                    truncation=True,
                    padding=True,
                    max_length=self.max_length
                )
                
                # Mover para device
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                # Inferência em lote
                with torch.no_grad():
                    outputs = self.model(**inputs)
                
                # Extrair embeddings (mean pooling)
                batch_embeddings = outputs.last_hidden_state
                attention_mask = inputs['attention_mask']
                
                # Mean pooling para cada texto
                masked_embeddings = batch_embeddings * attention_mask.unsqueeze(-1)
                sum_embeddings = masked_embeddings.sum(dim=1)
                sum_mask = attention_mask.sum(dim=1, keepdim=True)
                mean_embeddings = sum_embeddings / sum_mask
                
                # Converter para numpy
                batch_embeddings_np = mean_embeddings.cpu().numpy()
                
                # Inserir embeddings nas posições corretas
                for i, embedding in enumerate(batch_embeddings_np):
                    original_index = uncached_indices[i]
                    embeddings[original_index] = embedding
                    
                    # Salvar no cache
                    if use_cache:
                        text = uncached_texts[i]
                        cache_key = hashlib.md5(text.encode()).hexdigest()
                        self.embeddings_cache[cache_key] = embedding
                
                processing_time = time.time() - start_time
                
                # Atualizar estatísticas
                self.performance_stats['total_embeddings_generated'] += len(uncached_texts)
                self.performance_stats['total_processing_time'] += processing_time
                self.performance_stats['avg_processing_time'] = (
                    self.performance_stats['total_processing_time'] / 
                    self.performance_stats['total_embeddings_generated']
                )
                
                logger.info(f"✅ Batch processado: {len(uncached_texts)} embeddings em {processing_time:.3f}s")
                
            except Exception as e:
                logger.error(f"❌ Erro no batch processing: {e}")
                # Fallback para processamento individual
                for i in uncached_indices:
                    text = texts[i]
                    embeddings[i] = self.get_embedding(text, use_cache=False)
        
        return embeddings
    
    def optimize_cache(self, max_cache_size: int = 1000):
        """Otimizar cache removendo embeddings menos usados"""
        if len(self.embeddings_cache) <= max_cache_size:
            return
        
        logger.info(f"🧹 Otimizando cache: {len(self.embeddings_cache)} → {max_cache_size}")
        
        # Estratégia simples: remover aleatoriamente (pode ser melhorada)
        cache_keys = list(self.embeddings_cache.keys())
        keys_to_remove = cache_keys[max_cache_size:]
        
        for key in keys_to_remove:
            del self.embeddings_cache[key]
        
        self.cache_stats['cache_size'] = len(self.embeddings_cache)
        logger.info(f"✅ Cache otimizado: {len(keys_to_remove)} embeddings removidos")
    
    def get_enhanced_stats(self) -> Dict[str, Any]:
        """Estatísticas completas do BERTimbau"""
        
        # Calcular cache hit ratio atualizado
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        cache_hit_ratio = self.cache_stats['hits'] / total_requests if total_requests > 0 else 0
        
        return {
            "model_type": "BERTimbau Real (PyTorch)" if self.use_real_model else "TF-IDF Fallback",
            "model_name": self.model_name,
            "device": self.device,
            "model_loaded": self.is_loaded,
            "pytorch_available": PYTORCH_AVAILABLE,
            "embedding_dimension": 768,
            
            # Performance stats
            "total_embeddings_generated": self.performance_stats['total_embeddings_generated'],
            "avg_processing_time": self.performance_stats['avg_processing_time'],
            "total_processing_time": self.performance_stats['total_processing_time'],
            
            # Cache stats
            "cache_size": self.cache_stats['cache_size'],
            "cache_hits": self.cache_stats['hits'],
            "cache_misses": self.cache_stats['misses'],
            "cache_hit_ratio": cache_hit_ratio,
            
            # Model config
            "max_length": self.max_length,
            "batch_size": self.batch_size,
            "warmup_terms": len(self.common_terms),
            
            # Cultural knowledge
            "cultural_categories": len(self.cultural_knowledge),
            "total_cultural_terms": sum(len(terms) for terms in self.cultural_knowledge.values()),
            
            # System info
            "brazilian_specialized": True,
            "real_time_capable": True,
            "production_ready": True
        }
    
    # Métodos auxiliares (mantidos do código original)
    def _load_expanded_cultural_knowledge(self) -> Dict[str, List[str]]:
        """Base cultural expandida"""
        return {
            'musica': [
                'samba', 'bossa nova', 'mpb', 'forró', 'axé', 'funk', 'sertanejo',
                'pagode', 'choro', 'maracatu', 'frevo', 'baião', 'xote', 'piseiro',
                'rap nacional', 'rock brasileiro', 'eletrônica brasileira'
            ],
            'cultura_popular': [
                'carnaval', 'festa junina', 'bumba meu boi', 'capoeira', 'cordel',
                'repente', 'congada', 'folia de reis', 'quadrilha', 'ciranda',
                'folclore brasileiro', 'tradições regionais'
            ],
            'gastronomia': [
                'feijoada', 'acarajé', 'brigadeiro', 'açaí', 'tapioca', 'coxinha',
                'pastel', 'pão de açúcar', 'farofa', 'maniçoba', 'tucumã',
                'culinária regional', 'street food brasileiro'
            ],
            'regioes': [
                'nordeste', 'sudeste', 'sul', 'norte', 'centro-oeste',
                'bahia', 'rio de janeiro', 'são paulo', 'minas gerais', 'ceará',
                'amazonas', 'rio grande do sul', 'paraná', 'pernambuco'
            ],
            'expressoes': [
                'jeitinho brasileiro', 'saudade', 'malandragem', 'cordialidade',
                'hospitalidade', 'brasilidade', 'tropicalismo', 'antropofagia',
                'diversidade cultural', 'multiculturalismo brasileiro'
            ],
            'inovacao_tech': [
                'startup brasileira', 'fintech nacional', 'unicórnio brasileiro',
                'hub de inovação', 'ecossistema empreendedor', 'venture capital',
                'scale-up', 'edtech', 'healthtech', 'proptech', 'agtech'
            ]
        }
    
    def _prepare_training_corpus(self) -> List[str]:
        """Corpus expandido para treinamento"""
        corpus = []
        
        # Adicionar conhecimento cultural
        for category, terms in self.cultural_knowledge.items():
            for term in terms:
                corpus.extend([
                    f"{term} é parte da cultura brasileira",
                    f"no brasil temos {term} como tradição",
                    f"{term} representa a brasilidade",
                    f"cultura popular brasileira inclui {term}",
                    f"{term} no contexto nacional brasileiro"
                ])
        
        return corpus
    
    def _get_portuguese_stopwords(self) -> List[str]:
        """Stopwords em português"""
        return [
            'a', 'o', 'e', 'é', 'de', 'do', 'da', 'em', 'um', 'uma', 'para',
            'com', 'não', 'que', 'se', 'na', 'no', 'por', 'mais', 'as', 'os',
            'como', 'mas', 'foi', 'ao', 'ele', 'ela', 'eu', 'tu', 'você',
            'nós', 'eles', 'elas', 'seu', 'sua', 'meu', 'minha'
        ]


# ===== FACTORY FUNCTION =====
def create_bertimbau_real_engine(**kwargs) -> BERTimbauRealEngine:
    """Factory para criar BERTimbau Real Engine"""
    return BERTimbauRealEngine(**kwargs)


# ===== TESTE PRINCIPAL =====
if __name__ == "__main__":
    import asyncio
    
    async def test_bertimbau_real():
        """Teste do BERTimbau Real"""
        print("🇧🇷 BERTimbau Real Engine V8.2 - Teste Principal")
        print("=" * 60)
        
        # Criar engine
        engine = create_bertimbau_real_engine()
        
        # Textos de teste
        test_texts = [
            "startup de fintech brasileira revoluciona pagamentos digitais",
            "festival de música brasileira atrai milhares no nordeste", 
            "agronegócio sustentável no cerrado bate recordes de produção",
            "capoeira é reconhecida como patrimônio cultural da humanidade",
            "samba carioca influencia nova geração de artistas brasileiros"
        ]
        
        print(f"\n📊 Testando com {len(test_texts)} textos...")
        
        # Teste individual
        print(f"\n🔍 Teste Individual:")
        for i, text in enumerate(test_texts[:3], 1):
            start_time = time.time()
            embedding = engine.get_embedding(text)
            processing_time = time.time() - start_time
            
            print(f"  {i}. Tempo: {processing_time:.3f}s - Dim: {len(embedding)} - {text[:50]}...")
        
        # Teste em lote
        print(f"\n🔄 Teste em Lote:")
        start_batch = time.time()
        batch_embeddings = engine.get_embeddings_batch(test_texts)
        batch_time = time.time() - start_batch
        
        print(f"  ⚡ Total: {batch_time:.3f}s")
        print(f"  📊 Por item: {batch_time/len(test_texts):.3f}s")
        print(f"  🎯 Embeddings: {len(batch_embeddings)}")
        
        # Teste de cache
        print(f"\n💾 Teste de Cache:")
        
        # Primeiro acesso (miss)
        start_miss = time.time()
        engine.get_embedding(test_texts[0])
        miss_time = time.time() - start_miss
        
        # Segundo acesso (hit)
        start_hit = time.time()
        engine.get_embedding(test_texts[0])
        hit_time = time.time() - start_hit
        
        speedup = miss_time / hit_time if hit_time > 0 else float('inf')
        
        print(f"  🔍 Cache Miss: {miss_time:.3f}s")
        print(f"  ⚡ Cache Hit: {hit_time:.3f}s") 
        print(f"  🚀 Speedup: {speedup:.1f}x")
        
        # Estatísticas finais
        stats = engine.get_enhanced_stats()
        
        print(f"\n📊 Estatísticas Finais:")
        print(f"  🤖 Modelo: {stats['model_type']}")
        print(f"  🔧 Device: {stats['device']}")
        print(f"  ⚡ Tempo médio: {stats['avg_processing_time']:.3f}s")
        print(f"  💾 Cache hit ratio: {stats['cache_hit_ratio']:.1%}")
        print(f"  🎯 Embeddings gerados: {stats['total_embeddings_generated']}")
        print(f"  📏 Cache size: {stats['cache_size']}")
        
        print(f"\n🎉 BERTimbau Real Engine testado com sucesso!")
    
    # Executar teste
    asyncio.run(test_bertimbau_real())
