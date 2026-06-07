"""
🔮 Weak Signals Detector V9.0 - ML Foundation Integrated
Sistema de detecção de sinais fracos para análise preditiva cultural
Identifica tendências emergentes antes que se tornem mainstream

NOVA INTEGRAÇÃO:
- ML Foundation para embeddings semânticos
- GitHub Models para análise contextual
- BERTimbau para análise cultural brasileira
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional, Set
from datetime import datetime, timedelta
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from collections import defaultdict, Counter
from dataclasses import dataclass
import json
import re
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WeakSignal:
    """Estrutura de dados para um sinal fraco detectado"""
    id: str
    term: str
    source: str
    strength: float  # 0.0 a 1.0
    confidence: float  # 0.0 a 1.0
    urgency: float  # 0.0 a 1.0
    cultural_context: str
    emergence_date: datetime
    geographic_region: str
    audience_segment: str
    signal_type: str  # "preditiva", "exploratoria", "normativa"
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o sinal para dicionário"""
        return {
            'id': self.id,
            'term': self.term,
            'source': self.source,
            'strength': self.strength,
            'confidence': self.confidence,
            'urgency': self.urgency,
            'cultural_context': self.cultural_context,
            'emergence_date': self.emergence_date.isoformat(),
            'geographic_region': self.geographic_region,
            'audience_segment': self.audience_segment,
            'signal_type': self.signal_type,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WeakSignal':
        """Cria um WeakSignal a partir de dicionário"""
        data['emergence_date'] = datetime.fromisoformat(data['emergence_date'])
        return cls(**data)

class WeakSignalsDetector:
    """
    Detector de sinais fracos para identificação precoce de tendências
    
    METODOLOGIA:
    1. PREDITIVA: Identifica padrões emergentes nos dados
    2. EXPLORATÓRIA: Descobre conexões não óbvias
    3. NORMATIVA: Sugere ações baseadas nos sinais
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.clustering = DBSCAN(eps=0.3, min_samples=2)
        
        # Configurações de detecção
        self.weak_signal_threshold = 0.05  # 5% de crescimento mínimo
        self.emergence_window = 7  # Dias para considerar "emergente"
        self.cultural_contexts = self._load_cultural_contexts()
        
        # Cache de sinais detectados
        self.detected_signals = []
        self.signal_patterns = defaultdict(list)
        
        # Integração ML Foundation
        self.ml_foundation = None
        self.cultural_embeddings = None
        self.github_models = None
        self.nlp_processor = None
        
        self._initialize_ml_foundation()
        
        logger.info("🔮 Weak Signals Detector V9.0 inicializado com ML Foundation!")
    
    def _initialize_ml_foundation(self):
        """Inicializar integração com ML Foundation"""
        try:
            from autonomous_agent.ml_foundation.ml_integrator_simple import MLIntegratorSimple
            
            self.ml_foundation = MLIntegratorSimple()
            
            # Verificar se está inicializado
            if not self.ml_foundation.is_initialized:
                logger.info("🔄 Inicializando componentes ML Foundation para Weak Signals...")
                self.ml_foundation._initialize_components()
            
            # Obter componentes individuais
            self.cultural_embeddings = getattr(self.ml_foundation, 'cultural_embeddings', None)
            self.github_models = getattr(self.ml_foundation, 'github_models', None)
            self.nlp_processor = getattr(self.ml_foundation, 'nlp_processor', None)
            
            # Log dos componentes disponíveis
            components_status = {
                'cultural_embeddings': bool(self.cultural_embeddings),
                'github_models': bool(self.github_models),
                'nlp_processor': bool(self.nlp_processor)
            }
            
            active_components = sum(components_status.values())
            logger.info(f"🔗 ML Foundation integrado: {active_components}/3 componentes ativos")
            
            if active_components > 0:
                logger.info("✅ Weak Signals com ML Foundation habilitado")
            else:
                logger.warning("⚠️ Weak Signals funcionará em modo básico")
                
        except Exception as e:
            logger.warning(f"⚠️ Erro ao integrar ML Foundation: {e}")
            logger.info("🔄 Weak Signals funcionará em modo básico")
        
    def _load_cultural_contexts(self) -> Dict[str, List[str]]:
        """Contextos culturais brasileiros para análise de sinais"""
        return {
            "tecnologia_emergente": [
                "web3", "blockchain", "nft", "metaverso", "realidade virtual",
                "inteligencia artificial", "machine learning", "deep learning",
                "iot", "5g", "quantum computing", "edge computing"
            ],
            "comportamento_digital": [
                "live commerce", "social commerce", "creators economy",
                "influencer marketing", "micro influencers", "ugc",
                "short form video", "audio social", "podcasting"
            ],
            "sustentabilidade": [
                "economia circular", "upcycling", "zero waste",
                "carbon neutral", "esg", "green tech", "clean energy",
                "sustainable fashion", "conscious consumption"
            ],
            "financas_digitais": [
                "defi", "open banking", "embedded finance", "bnpl",
                "super app", "neobank", "regtech", "insurtech",
                "wealth tech", "robo advisor"
            ],
            "cultura_brasileira": [
                "afrofuturismo", "periferias criativas", "funk evolution",
                "trap brasileiro", "sertanejo eletrônico", "brega funk",
                "cultura gamer", "e-sports brasileiro"
            ],
            "saude_wellness": [
                "telemedicine", "mental health tech", "wellness apps",
                "biohacking", "personalized nutrition", "sleep tech",
                "meditation tech", "fitness gamification"
            ]
        }
        
    def detect_weak_signals(self, data_points: List[Dict[str, Any]], 
                          timeframe: int = 30,
                          user_intent: str = "Pesquisa de Mercado") -> Dict[str, Any]:
        """
        Detecta sinais fracos nos dados coletados, filtrados pelo Intent do Usuário (Onboarding)
        
        Args:
            data_points: Dados de diferentes fontes (APIs)
            timeframe: Janela de tempo em dias
            user_intent: "Pesquisa de Mercado", "Lançamento de Produto" ou "Crise de Reputação"
            
        Returns:
            Dict com sinais fracos detectados
        """
        print(f"🔍 Analisando {len(data_points)} pontos de dados para Intent: {user_intent}...")
        
        # 1. ANÁLISE TEMPORAL - Detectar crescimento emergente
        temporal_signals = self._analyze_temporal_patterns(data_points, timeframe)
        
        # 2. ANÁLISE SEMÂNTICA - Detectar novos termos e conceitos
        semantic_signals = self._analyze_semantic_emergence(data_points)
        
        # 3. ANÁLISE DE CLUSTERING - Detectar agrupamentos anômalos
        cluster_signals = self._analyze_clustering_patterns(data_points)
        
        # 4. ANÁLISE CULTURAL - Detectar mudanças em contextos brasileiros
        cultural_signals = self._analyze_cultural_shifts(data_points)
        
        # 5. SÍNTESE DOS SINAIS (Injetando Intent no Sintetizador)
        weak_signals = self._synthesize_signals(
            temporal_signals, semantic_signals, 
            cluster_signals, cultural_signals,
            user_intent=user_intent
        )
        
        # 6. CLASSIFICAÇÃO POR FORÇA E RELEVÂNCIA
        classified_signals = self._classify_signal_strength(weak_signals)
        
        return {
            "detected_at": datetime.now().isoformat(),
            "timeframe_days": timeframe,
            "total_signals": len(classified_signals),
            "signals_by_strength": classified_signals,
            "recommendations": self._generate_recommendations(classified_signals),
            "cultural_context": self._map_to_cultural_circles(classified_signals)
        }
        
    def _analyze_temporal_patterns(self, data_points: List[Dict], 
                                 timeframe: int) -> List[Dict[str, Any]]:
        """Detecta padrões temporais emergentes"""
        temporal_signals = []
        
        # Agrupar dados por período
        time_series = defaultdict(lambda: defaultdict(int))
        
        for point in data_points:
            timestamp = point.get('timestamp', datetime.now())
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                
            day_key = timestamp.strftime('%Y-%m-%d')
            content = point.get('content', '') + ' ' + point.get('title', '')
            
            # Extrair termos relevantes
            terms = self._extract_relevant_terms(content.lower())
            
            for term in terms:
                time_series[day_key][term] += 1
                
        # Detectar crescimento acelerado
        for term in self._get_all_terms(time_series):
            growth_pattern = self._calculate_growth_pattern(time_series, term)
            
            if growth_pattern['is_emerging']:
                temporal_signals.append({
                    "type": "temporal_emergence",
                    "term": term,
                    "growth_rate": growth_pattern['growth_rate'],
                    "confidence": growth_pattern['confidence'],
                    "days_emerging": growth_pattern['days_active']
                })
                
        return temporal_signals
        
    def _analyze_semantic_emergence(self, data_points: List[Dict]) -> List[Dict[str, Any]]:
        """Detecta emergência semântica de novos conceitos"""
        semantic_signals = []
        
        # Extrair todos os textos
        all_texts = []
        for point in data_points:
            content = point.get('content', '') + ' ' + point.get('title', '')
            all_texts.append(content.lower())
            
        # Detectar termos novos ou com co-ocorrência inusual
        term_cooccurrence = self._analyze_term_cooccurrence(all_texts)
        
        for term_pair, stats in term_cooccurrence.items():
            if stats['novelty_score'] > 0.7:  # Alto score de novidade
                semantic_signals.append({
                    "type": "semantic_emergence",
                    "term_pair": term_pair,
                    "novelty_score": stats['novelty_score'],
                    "frequency": stats['frequency'],
                    "contexts": stats['contexts'][:3]  # Top 3 contextos
                })
                
        return semantic_signals
        
    def _analyze_clustering_patterns(self, data_points: List[Dict]) -> List[Dict[str, Any]]:
        """Detecta padrões de clustering anômalos"""
        cluster_signals = []
        
        if len(data_points) < 5:
            return cluster_signals
            
        # Preparar features para clustering
        features_matrix = self._prepare_clustering_features(data_points)
        
        if features_matrix.size > 0:
            # Aplicar clustering
            clusters = self.clustering.fit_predict(features_matrix)
            
            # Detectar clusters anômalos (pequenos mas distintos)
            cluster_stats = Counter(clusters)
            
            for cluster_id, count in cluster_stats.items():
                if cluster_id != -1 and count >= 2 and count <= 5:  # Clusters pequenos
                    cluster_points = [data_points[i] for i, c in enumerate(clusters) if c == cluster_id]
                    
                    cluster_signals.append({
                        "type": "anomalous_cluster",
                        "cluster_id": cluster_id,
                        "size": count,
                        "representative_content": self._get_cluster_representative(cluster_points),
                        "anomaly_score": 1.0 - (count / len(data_points))
                    })
                    
        return cluster_signals
        
    def _analyze_cultural_shifts(self, data_points: List[Dict]) -> List[Dict[str, Any]]:
        """
        Detecta mudanças culturais profundas usando BERTimbau e GitHub Models.
        Foca em sair do óbvio através de análise semântica avançada.
        """
        cultural_signals = []
        
        # 1. Agrupar textos para análise de subtexto (Sair do Óbvio)
        texts = [p.get('text', p.get('content', p.get('title', ''))) for p in data_points]
        if not texts:
            return cultural_signals

        try:
            # 2. Uso do BERTimbau (via ml_foundation) para entender NUANCES brasileiras
            # O BERTimbau detecta se o termo está sendo usado em um contexto "estranho" ou novo
            if self.ml_foundation and hasattr(self.ml_foundation, 'cultural_embeddings'):
                for text in texts[:20]: # Analisa amostra profunda
                    # O motor de análise cultural já herda o conhecimento do BERTimbau REAL
                    analysis = self.ml_foundation.process_cultural_analysis(text, [])
                    if analysis.get('analysis', {}).get('cultural_similarities', {}).get('is_anomaly', False):
                        cultural_signals.append({
                            "type": "cultural_anomaly_detected",
                            "context": text[:150],
                            "engine": "BERTimbau_Neural",
                            "confidence": 0.88,
                            "is_non_obvious": True
                        })

            # 3. Uso do GitHub Models (GPT-4o mini) para Capturar o "Espírito do Tempo" (Zeitgeist)
            if self.ml_foundation and hasattr(self.ml_foundation, 'github_models'):
                import asyncio
                try:
                    # Rodar análise contextual da IA para encontrar padrões que o código não vê
                    loop = asyncio.get_event_loop()
                    # Pedimos explicitamente para a IA sair do óbvio
                    ai_context = loop.run_until_complete(
                        self.ml_foundation.github_models.analyze_context(
                            " ".join(texts[:10]), 
                            analysis_type="weak_signals_non_obvious"
                        )
                    )
                    
                    if ai_context and not ai_context.get('fallback'):
                        cultural_signals.append({
                            "type": "latent_trend_detected",
                            "content": ai_context.get('cultural_context', 'Subtexto emergente'),
                            "engine": "GitHub_Models_GPT4o",
                            "is_non_obvious": True,
                            "potential_impact": "high"
                        })
                except Exception as e:
                    logger.warning(f"⚠️ GitHub Models bypass no detector: {e}")

        except Exception as e:
            logger.error(f"❌ Erro na análise cultural avançada (ML Foundation): {e}")

        # Mantém o mapeamento clássico como fallback para volume
        context_mentions = defaultdict(int)
        context_evolution = defaultdict(list)
        
        for point in data_points:
            content = point.get('content', '') + ' ' + point.get('title', '')
            content_lower = content.lower()
            
            timestamp = point.get('timestamp', datetime.now())
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                
            for context_name, terms in self.cultural_contexts.items():
                mentions = sum(1 for term in terms if term in content_lower)
                if mentions > 0:
                    context_mentions[context_name] += mentions
                    context_evolution[context_name].append({
                        'timestamp': timestamp,
                        'mentions': mentions,
                        'content_sample': content[:100]
                    })
                    
        # Detectar contextos em ascensão
        for context_name, total_mentions in context_mentions.items():
            if total_mentions >= 3:
                evolution = context_evolution[context_name]
                if len(evolution) >= 2:
                    recent_mentions = sum(e['mentions'] for e in evolution[-3:])
                    early_mentions = sum(e['mentions'] for e in evolution[:3])
                    
                    if recent_mentions > early_mentions * 1.5:
                        cultural_signals.append({
                            "type": "cultural_shift",
                            "context": context_name,
                            "total_mentions": total_mentions,
                            "growth_acceleration": recent_mentions / max(early_mentions, 1),
                            "sample_content": [e['content_sample'] for e in evolution[-2:]]
                        })
                        
        return cultural_signals
        
    def _extract_relevant_terms(self, text: str) -> List[str]:
        """Extrai termos relevantes do texto"""
        # Remove pontuação e divide em palavras
        words = re.findall(r'\b[a-záàâãéèêíìîóòôõúùûç]{3,}\b', text)
        
        # Filtra palavras muito comuns
        stopwords = {'que', 'para', 'com', 'uma', 'por', 'não', 'mais', 'como', 'ser', 'ter'}
        relevant_terms = [w for w in words if w not in stopwords and len(w) > 3]
        
        return relevant_terms
        
    def _get_all_terms(self, time_series: Dict) -> Set[str]:
        """Obtém todos os termos únicos da série temporal"""
        all_terms = set()
        for day_data in time_series.values():
            all_terms.update(day_data.keys())
        return all_terms
        
    def _calculate_growth_pattern(self, time_series: Dict, term: str) -> Dict[str, Any]:
        """Calcula padrão de crescimento de um termo"""
        daily_counts = []
        active_days = 0
        
        for day in sorted(time_series.keys()):
            count = time_series[day].get(term, 0)
            daily_counts.append(count)
            if count > 0:
                active_days += 1
                
        if len(daily_counts) < 3 or active_days < 2:
            return {"is_emerging": False, "growth_rate": 0, "confidence": 0, "days_active": active_days}
            
        # Calcular crescimento
        recent_avg = np.mean(daily_counts[-3:]) if len(daily_counts) >= 3 else daily_counts[-1]
        early_avg = np.mean(daily_counts[:3]) if len(daily_counts) >= 3 else daily_counts[0]
        
        growth_rate = (recent_avg - early_avg) / max(early_avg, 1)
        
        # Determinar se é emergente
        is_emerging = (
            growth_rate > self.weak_signal_threshold and
            active_days >= 2 and
            recent_avg > 0
        )
        
        confidence = min(growth_rate, 1.0) * (active_days / len(daily_counts))
        
        return {
            "is_emerging": is_emerging,
            "growth_rate": growth_rate,
            "confidence": confidence,
            "days_active": active_days
        }
        
    def _analyze_term_cooccurrence(self, texts: List[str]) -> Dict[Tuple[str, str], Dict[str, Any]]:
        """Analisa co-ocorrência de termos para detectar novidade"""
        cooccurrence = defaultdict(lambda: {"frequency": 0, "contexts": []})
        
        for text in texts:
            terms = self._extract_relevant_terms(text)
            
            # Gerar pares de termos
            for i, term1 in enumerate(terms):
                for term2 in terms[i+1:]:
                    if term1 != term2:
                        pair = tuple(sorted([term1, term2]))
                        cooccurrence[pair]["frequency"] += 1
                        cooccurrence[pair]["contexts"].append(text[:100])
                        
        # Calcular scores de novidade
        result = {}
        for pair, data in cooccurrence.items():
            if data["frequency"] >= 2:  # Mínimo de co-ocorrências
                # Score de novidade baseado em raridade + frequência relativa
                novelty_score = min(1.0, data["frequency"] / 10)  # Normalizar
                
                result[pair] = {
                    **data,
                    "novelty_score": novelty_score
                }
                
        return result
        
    def _prepare_clustering_features(self, data_points: List[Dict]) -> np.ndarray:
        """Prepara matriz de features para clustering"""
        features = []
        
        for point in data_points:
            content = point.get('content', '') + ' ' + point.get('title', '')
            
            # Features simples: comprimento, número de palavras, etc.
            feature_vector = [
                len(content),
                len(content.split()),
                content.lower().count('brasil'),
                content.lower().count('tech'),
                content.lower().count('digital')
            ]
            
            features.append(feature_vector)
            
        if features:
            return self.scaler.fit_transform(np.array(features))
        else:
            return np.array([])
            
    def _get_cluster_representative(self, cluster_points: List[Dict]) -> str:
        """Obtém conteúdo representativo do cluster"""
        if not cluster_points:
            return ""
            
        # Pegar o ponto com mais conteúdo
        representative = max(cluster_points, 
                           key=lambda p: len(p.get('content', '') + p.get('title', '')))
        
        content = representative.get('content', '') + ' ' + representative.get('title', '')
        return content[:200] + "..." if len(content) > 200 else content
        
    def _synthesize_signals(self, *signal_lists, user_intent: str = "Pesquisa de Mercado") -> List[Dict[str, Any]]:
        """
        Sintetiza todos os tipos de sinais e aplica o FILTRO DE OBVIEDADE.
        Usa o BusinessSynthesizer para garantir Entropia Cultural alta e alinhar com o Intent.
        """
        all_signals = []
        for s_list in signal_lists:
            if isinstance(s_list, list):
                all_signals.extend(s_list)
        
        # 1. Integração com Filtro de Entropia Cultural
        from core.intelligence.business_synthesizer import BusinessSynthesizer, BusinessContext
        synthesizer = BusinessSynthesizer()
        
        # 2. Criar contexto de negócio baseado no Intent do Onboarding
        # Isso garante que a filtragem de entropia considere o que o usuário busca
        context = BusinessContext(
            scenario_type=user_intent,
            target_audience="público geral brasileiro",
            business_objective=f"Detectar sinais fracos para {user_intent}",
            opportunities_sought=["descoberta não-óbvia", "antecipação de tendências"]
        )
        
        # Filtra clichês (Ex: Samba/Carnaval) para focar em Sinais Fracos Não-Óbvios
        print(f"🧩 Aplicando Filtro de Entropia Cultural para {user_intent} em {len(all_signals)} sinais...")
        refined_signals = synthesizer.filter_obvious_signals(all_signals)
        
        # 3. Enriquecer sinais com recomendações baseadas no Intent
        for sig in refined_signals:
            sig['user_intent_context'] = user_intent
            if user_intent == "Crise de Reputação":
                sig['urgency'] = min(1.0, sig.get('urgency', 0.5) + 0.2)
        
        print(f"✨ {len(refined_signals)} sinais sobreviventes: Baixa Probabilidade / Alta Oportunidade.")
        return refined_signals
        
    def _classify_signal_strength(self, signals: List[Dict]) -> Dict[str, List[Dict]]:
        """Classifica sinais por força (forte, médio, fraco)"""
        classified = {
            "strong_signals": [],
            "medium_signals": [],
            "weak_signals": []
        }
        
        for signal in signals:
            strength_score = self._calculate_signal_strength(signal)
            
            if strength_score >= 0.7:
                classified["strong_signals"].append({**signal, "strength": strength_score})
            elif strength_score >= 0.4:
                classified["medium_signals"].append({**signal, "strength": strength_score})
            else:
                classified["weak_signals"].append({**signal, "strength": strength_score})
                
        return classified
        
    def _calculate_signal_strength(self, signal: Dict[str, Any]) -> float:
        """Calcula força do sinal baseado em fatores de ML e Entropia Cultural V9.8"""
        base_strength = 0.5
        signal_type = signal.get("type", "")
        
        # Bônus de Entropia (Sair do Óbvio)
        # Sinais que sobreviveram ao filtro de obviedade ganham relevância estratégica
        entropy_bonus = 0.3 if signal.get('is_non_obvious') else 0.0
        
        if signal_type == "temporal_emergence":
            base_strength = min(1.0, signal.get("growth_rate", 0) * signal.get("confidence", 0))
            
        elif signal_type == "semantic_emergence":
            base_strength = signal.get("novelty_score", 0)
            
        elif signal_type == "anomalous_cluster":
            base_strength = signal.get("anomaly_score", 0)
            
        elif signal_type == "cultural_shift":
            base_strength = min(1.0, signal.get("growth_acceleration", 1) / 3)
            
        elif signal_type == "cultural_anomaly_detected": # BERTimbau
            base_strength = signal.get("confidence", 0.8)
            
        elif signal_type == "latent_trend_detected": # GitHub Models
            base_strength = 0.85
            
        # O score final é a união da detecção técnica com a validação de entropia
        return min(1.0, base_strength + entropy_bonus)
        
    def _generate_recommendations(self, classified_signals: Dict) -> List[Dict[str, str]]:
        """Gera recomendações baseadas nos sinais detectados"""
        recommendations = []
        
        # Recomendações para sinais fortes
        for signal in classified_signals.get("strong_signals", []):
            if signal["type"] == "temporal_emergence":
                recommendations.append({
                    "priority": "HIGH",
                    "action": f"Investigar imediatamente a tendência '{signal['term']}'",
                    "rationale": f"Crescimento de {signal['growth_rate']:.1%} detectado",
                    "timeline": "1-2 semanas"
                })
                
            elif signal["type"] == "cultural_shift":
                recommendations.append({
                    "priority": "HIGH", 
                    "action": f"Adaptar estratégia para o contexto '{signal['context']}'",
                    "rationale": f"Aceleração cultural de {signal['growth_acceleration']:.1f}x",
                    "timeline": "2-4 semanas"
                })
                
        # Recomendações para sinais médios
        for signal in classified_signals.get("medium_signals", []):
            recommendations.append({
                "priority": "MEDIUM",
                "action": f"Monitorar evolução do sinal {signal['type']}",
                "rationale": f"Força moderada: {signal['strength']:.2f}",
                "timeline": "4-8 semanas"
            })
            
        return recommendations
        
    def _map_to_cultural_circles(self, classified_signals: Dict) -> Dict[str, float]:
        """Mapeia sinais para círculos culturais brasileiros"""
        circle_relevance = defaultdict(float)
        
        # Mapeamento simplificado
        cultural_mapping = {
            "tecnologia_emergente": "criatividade_improvisacao",
            "comportamento_digital": "adaptacao_flexibilidade", 
            "sustentabilidade": "conexao_natureza_coletivo",
            "financas_digitais": "desejo_ascensao_oportunidades",
            "cultura_brasileira": "diversidade_geografica_cultural",
            "saude_wellness": "resiliencia_fe"
        }
        
        for signal_type, signals in classified_signals.items():
            for signal in signals:
                if signal.get("context") in cultural_mapping:
                    circle = cultural_mapping[signal["context"]]
                    circle_relevance[circle] += signal.get("strength", 0.5)
                    
        return dict(circle_relevance)

def create_weak_signals_detector() -> WeakSignalsDetector:
    """Factory function para criar detector de sinais fracos"""
    return WeakSignalsDetector()

# Teste básico
if __name__ == "__main__":
    print("🧪 Testando Weak Signals Detector...")
    
    # Criar detector
    detector = create_weak_signals_detector()
    
    # Dados de teste simulados
    test_data = [
        {
            "timestamp": datetime.now() - timedelta(days=1),
            "title": "Nova startup brasileira cria solução de pix para delivery",
            "content": "Empresa paulista desenvolve tecnologia que integra pix com apps de delivery usando blockchain"
        },
        {
            "timestamp": datetime.now() - timedelta(days=2),
            "title": "Crescimento do web3 no Brasil",
            "content": "Desenvolvedores brasileiros lideram adoção de tecnologias web3 na América Latina"
        },
        {
            "timestamp": datetime.now() - timedelta(days=3),
            "title": "Influencers focam em sustentabilidade",
            "content": "Creators brasileiros aderem massivamente a conteúdo sobre economia circular e upcycling"
        }
    ]
    
    # Detectar sinais fracos
    signals = detector.detect_weak_signals(test_data)
    
    print(f"✅ Sinais detectados: {signals['total_signals']}")
    print(f"✅ Recomendações: {len(signals['recommendations'])}")
    print(f"✅ Contexto cultural: {len(signals['cultural_context'])}")
    
    print("🎉 Weak Signals Detector funcionando!")
