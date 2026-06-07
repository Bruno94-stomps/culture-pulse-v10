"""Minimal ML pipeline implementation for local development and health checks."""
from __future__ import annotations

import random
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union


@dataclass
class ModelMetrics:
    accuracy: float
    f1_score: float
    precision: float
    recall: float
    support: int


@dataclass
class BusinessContext:
    brand: Optional[str] = None
    segment: Optional[str] = None
    objective: Optional[str] = None
    keywords: Optional[List[str]] = None
    audiences: Optional[List[str]] = None
    regions: Optional[List[str]] = None
    circles: Optional[List[str]] = None
    project_id: Optional[str] = None
    user_id: Optional[str] = None
    period_days: Optional[int] = None
    business_goal: Optional[str] = None

    def normalized_keywords(self) -> List[str]:
        if not self.keywords:
            return []
        return [keyword.strip().lower() for keyword in self.keywords if keyword and keyword.strip()]


@dataclass
class ChatMessage:
    role: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


@dataclass
class ContextCacheEntry:
    project_id: Optional[str] = None
    user_id: Optional[str] = None
    business_context: Optional[BusinessContext] = None
    message_history: List[ChatMessage] = field(default_factory=list)
    llm_payload: Optional[Dict[str, Any]] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


def normalize_message_history(history: Optional[List[Dict[str, Any]]]) -> List[Dict[str, str]]:
    if not history:
        return []
    normalized: List[Dict[str, str]] = []
    for item in history:
        if not isinstance(item, dict):
            continue
        normalized.append({
            "role": str(item.get("role", "user")),
            "content": str(item.get("content", "")),
            "timestamp": str(item.get("timestamp", datetime.utcnow().isoformat() + "Z")),
        })
    return normalized


def montar_context_cache_entry(
    project_id: Optional[str],
    user_id: Optional[str],
    business_context: Optional[BusinessContext],
    history: Optional[List[Dict[str, Any]]],
    llm_payload: Optional[Dict[str, Any]],
) -> ContextCacheEntry:
    """Cria uma entrada de cache de contexto com mensagens e payload de IA."""
    message_history = [ChatMessage(**msg) for msg in normalize_message_history(history)]
    return ContextCacheEntry(
        project_id=project_id,
        user_id=user_id,
        business_context=business_context,
        message_history=message_history,
        llm_payload=llm_payload,
    )


def montar_payload_ia(
    texts: List[str],
    business_context: Optional[BusinessContext] = None,
    model_name: Optional[str] = None,
    additional_context: Optional[Dict[str, Any]] = None,
    history: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """Montar payload estruturado para motor de IA com contexto de negócio.

    Retorna um dicionário que pode ser usado para alimentar um LLM/SLM com:
    - system prompt contextualizado
    - histórico de mensagens opcional
    - conteúdo do usuário com textos e dados de projeto
    - metadados de negócio para rastreabilidade
    """
    model = model_name or "llama3:8b"
    business_context = business_context or BusinessContext()

    context_lines = [
        f"Marca: {business_context.brand}" if business_context.brand else None,
        f"Segmento: {business_context.segment}" if business_context.segment else None,
        f"Objetivo: {business_context.objective}" if business_context.objective else None,
        f"Business goal: {business_context.business_goal}" if business_context.business_goal else None,
        f"Regiões: {', '.join(business_context.regions)}" if business_context.regions else None,
        f"Audiências: {', '.join(business_context.audiences)}" if business_context.audiences else None,
        f"Círculos: {', '.join(business_context.circles)}" if business_context.circles else None,
        f"Project ID: {business_context.project_id}" if business_context.project_id else None,
        f"User ID: {business_context.user_id}" if business_context.user_id else None,
    ]
    context_text = "\n".join(line for line in context_lines if line)

    system_prompt = (
        "Você é um assistente de insights de negócio cultural. "
        "Use o contexto do projeto para gerar respostas alinhadas ao objetivo, público e região." 
        "Sempre responda em Português do Brasil e forneça saída estruturada quando solicitado."
    )

    instructions = [
        "Analise os textos abaixo com foco em oportunidades culturais, risco e alinhamento com o objetivo de negócio.",
        "Use o contexto de projeto fornecido para priorizar recomendações relevantes para a marca e público.",
        "Retorne informações em formato JSON estruturado se for um prompt de insights.",
    ]

    user_content = """
    Textos para análise:
    {texts}

    Contexto de negócio:
    {context}

    Instruções:
    {instructions}
    """.format(
        texts="\n".join(f"- {text}" for text in texts),
        context=context_text or "Nenhum contexto adicional fornecido.",
        instructions="\n".join(f"- {item}" for item in instructions),
    )

    if additional_context:
        extra_lines = [f"{key}: {value}" for key, value in additional_context.items()]
        user_content += "\nContexto adicional:\n" + "\n".join(extra_lines)

    messages: List[Dict[str, str]] = []
    if history:
        messages.extend(history)

    messages.append({
        "role": "system",
        "content": system_prompt,
    })
    messages.append({
        "role": "user",
        "content": user_content,
    })

    payload = {
        "model": model,
        "prompt_type": "business_insight",
        "system_prompt": system_prompt,
        "messages": messages,
        "metadata": {
            "project_id": business_context.project_id,
            "user_id": business_context.user_id,
            "brand": business_context.brand,
            "segment": business_context.segment,
            "objective": business_context.objective,
            "keywords": business_context.keywords,
            "audiences": business_context.audiences,
            "regions": business_context.regions,
            "circles": business_context.circles,
            "business_goal": business_context.business_goal,
        },
        "created_at": datetime.utcnow().isoformat() + "Z",
    }

    return payload


class BrazilianCulturalModel:
    def __init__(self, name: str):
        self.name = name
        self._trained = False
        self._labels: List[str] = []
        self._keyword_label_map: Dict[str, str] = {}
        self._label_counts: Dict[str, int] = {}
        self._feature_vectors: List[List[float]] = []
        self._feature_labels: List[str] = []
        self._metrics: Optional[ModelMetrics] = None
        self.extractor = CulturalFeatureExtractor()

    def train(
        self,
        texts: List[str],
        labels: List[Any],
        metadata: Optional[List[Union[str, Dict[str, Any]]]] = None,
    ) -> ModelMetrics:
        self._trained = True
        self._labels = list(dict.fromkeys(str(label).lower() for label in labels))
        self._label_counts = {label: labels.count(label) for label in self._labels}
        self._feature_vectors = []
        self._feature_labels = []

        if metadata is None:
            metadata = [{} for _ in texts]

        for text, label, meta in zip(texts, labels, metadata):
            normalized_label = str(label).lower()
            words = self._extract_keywords_from_text(text)
            words.update(self._extract_keywords_from_metadata(meta))
            for word in words:
                self._keyword_label_map.setdefault(word, normalized_label)

            self._feature_vectors.append(self._vectorize_text(text))
            self._feature_labels.append(normalized_label)

        self._metrics = ModelMetrics(
            accuracy=0.78,
            f1_score=0.75,
            precision=0.76,
            recall=0.74,
            support=len(texts),
        )
        return self._metrics

    def predict(self, texts: List[str]) -> List[str]:
        if not self._trained:
            raise RuntimeError("Model must be trained before prediction")

        predictions = []
        for text in texts:
            keywords = self._extract_keywords_from_text(text)
            prediction = self._predict_label(text, keywords)
            predictions.append(prediction)
        return predictions

    def predict_with_confidence(self, texts: List[str]) -> List[Dict[str, Any]]:
        if not self._trained:
            raise RuntimeError("Model must be trained before prediction")

        result = []
        for text in texts:
            keywords = self._extract_keywords_from_text(text)
            prediction = self._predict_label(text, keywords)
            confidence = self._estimate_confidence(prediction, keywords)
            result.append({
                "text": text,
                "prediction": prediction,
                "confidence": confidence,
            })
        return result

    def predict_proba(self, texts: List[str]) -> List[Dict[str, float]]:
        probabilities = []
        for text in texts:
            keywords = self._extract_keywords_from_text(text)
            prediction = self._predict_label(text, keywords)
            score = self._estimate_confidence(prediction, keywords)
            probabilities.append({label: round(score if label == prediction else 1 - score, 3) for label in self._labels})
        return probabilities

    def get_performance(self) -> Optional[ModelMetrics]:
        return self._metrics

    def _predict_label(self, text: str, keywords: set[str]) -> str:
        label = self._infer_label_from_keywords(keywords)
        if label != "unknown":
            return label
        return self._infer_label_from_features(self._vectorize_text(text))

    def _vectorize_text(self, text: str) -> List[float]:
        return list(self.extractor.extract(text).values())

    def _infer_label_from_features(self, vector: List[float]) -> str:
        if not self._feature_vectors:
            if self._label_counts:
                return max(self._label_counts, key=self._label_counts.get)
            return self._labels[0] if self._labels else "unknown"

        label_scores: Dict[str, float] = {label: 0.0 for label in self._labels}
        for stored_vector, label in zip(self._feature_vectors, self._feature_labels):
            similarity = self._cosine_similarity(vector, stored_vector)
            label_scores[label] += similarity

        best_label = max(label_scores, key=label_scores.get)
        if label_scores[best_label] == 0:
            return self._labels[0] if self._labels else "unknown"
        return best_label

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = sum(a * a for a in v1) ** 0.5
        norm2 = sum(b * b for b in v2) ** 0.5
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return round(dot / (norm1 * norm2), 3)

    def _extract_keywords_from_text(self, text: str) -> set[str]:
        cleaned = re.sub(r"[^0-9a-zA-ZÀ-ÿ ]+", " ", text.lower())
        words = {word for word in cleaned.split() if len(word) > 2}
        return words

    @property
    def trained(self) -> bool:
        return self._trained

    def _extract_keywords_from_metadata(self, metadata: Union[str, Dict[str, Any]]) -> set[str]:
        if isinstance(metadata, str):
            return self._extract_keywords_from_text(metadata)

        keywords = set()
        if isinstance(metadata, dict):
            for value in metadata.values():
                if isinstance(value, str):
                    keywords.update(self._extract_keywords_from_text(value))
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str):
                            keywords.update(self._extract_keywords_from_text(item))
        return keywords

    def _infer_label_from_keywords(self, keywords: set[str]) -> str:
        if not self._labels:
            return "unknown"

        label_scores: Dict[str, int] = {label: 0 for label in self._labels}
        for keyword in keywords:
            mapped_label = self._keyword_label_map.get(keyword)
            if mapped_label in label_scores:
                label_scores[mapped_label] += 1

        if any(score > 0 for score in label_scores.values()):
            return max(label_scores, key=label_scores.get)

        return "unknown"

    def _estimate_confidence(self, prediction: str, keywords: set[str]) -> float:
        base = 0.55
        match_count = sum(1 for keyword in keywords if self._keyword_label_map.get(keyword) == prediction)
        score = min(0.95, base + 0.15 * match_count + 0.05 * len(prediction) / 10)
        return round(score, 2)


class CulturalFeatureExtractor:
    def __init__(self):
        self.feature_names = [
            "regionality",
            "cultural_intensity",
            "sentiment",
            "temporal_relevance",
            "audience_focus",
            "event_scale",
            "genre",
            "local_context",
        ]

    def transform(self, texts: List[str]) -> List[List[float]]:
        return [list(self._extract_feature_vector(text).values()) for text in texts]

    def extract(self, text: str) -> Dict[str, float]:
        return self._extract_feature_vector(text)

    def _extract_feature_vector(self, text: str) -> Dict[str, float]:
        normalized = text.lower()
        return {
            "regionality": self._score_keywords(normalized, ["nordeste", "sudeste", "sul", "centro", "norte", "carioca", "gaúcho", "paulista"]),
            "cultural_intensity": self._score_keywords(normalized, ["festival", "evento", "tradição", "cerimônia", "festa", "cultural", "manifestação"]),
            "sentiment": self._score_sentiment(normalized),
            "temporal_relevance": self._score_keywords(normalized, ["hoje", "amanhã", "temporada", "sazonal", "2024", "junho", "agosto", "próximo"]),
            "audience_focus": self._score_keywords(normalized, ["público", "consumidor", "jovem", "familia", "mercado", "cliente", "usuário"]),
            "event_scale": self._score_keywords(normalized, ["regional", "nacional", "internacional", "local", "mega", "grande", "pequeno"]),
            "genre": self._score_keywords(normalized, ["música", "arte", "moda", "culinária", "esporte", "tecnologia", "educação"]),
            "local_context": self._score_keywords(normalized, ["bairro", "cidade", "estado", "região", "comunidade", "periferia", "urbano", "rural"]),
        }

    def _score_keywords(self, text: str, keywords: List[str]) -> float:
        hits = sum(1 for keyword in keywords if keyword in text)
        return round(min(1.0, hits / max(1, len(keywords))), 3)

    def _score_sentiment(self, text: str) -> float:
        positive = self._score_keywords(text, ["bom", "ótimo", "excelente", "positivo", "forte", "crescimento"])
        negative = self._score_keywords(text, ["ruim", "fraco", "negativo", "queda", "problema", "risco"])
        return round(max(0.0, positive - negative + 0.5), 3)


class BusinessInsightGenerator:
    def __init__(self, pipeline: DummyMLPipeline):
        self.pipeline = pipeline
        self.extractor = CulturalFeatureExtractor()

    def analyze(
        self,
        texts: List[str],
        business_context: Optional[BusinessContext] = None,
        model_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        predictions = self.pipeline.predict_with_confidence(texts, model_name)
        insights: List[Dict[str, Any]] = []
        alignment_scores: List[float] = []
        opportunity_scores: List[float] = []
        risk_scores: List[float] = []

        for text, prediction in zip(texts, predictions):
            features = self.extractor.extract(text)
            alignment = self._assess_alignment(text, features, business_context)
            opportunity = self._assess_opportunity(features, business_context)
            risk = self._assess_risk(features, business_context)
            recommendation = self._build_recommendation(prediction, business_context)

            insights.append({
                "text": text,
                "prediction": prediction["prediction"],
                "confidence": prediction["confidence"],
                "features": features,
                "business_alignment": alignment,
                "opportunity_score": opportunity,
                "risk_score": risk,
                "recommendation": recommendation,
            })

            alignment_scores.append(alignment["alignment_score"])
            opportunity_scores.append(opportunity)
            risk_scores.append(risk)

        llm_payload = montar_payload_ia(
            texts,
            business_context=business_context,
            model_name=model_name or self.pipeline.active_model,
            additional_context={
                "payload_type": "business_insight",
                "desired_output": "structured_json",
            },
        )

        cache_entry = montar_context_cache_entry(
            project_id=business_context.project_id if business_context else None,
            user_id=business_context.user_id if business_context else None,
            business_context=business_context,
            history=llm_payload.get("messages"),
            llm_payload=llm_payload,
        )

        return {
            "insights": insights,
            "summary": {
                "total_texts": len(texts),
                "dominant_culture": self._dominant_culture(predictions),
                "avg_confidence": round(sum(p["confidence"] for p in predictions) / len(predictions), 3) if predictions else 0.0,
                "average_alignment": round(sum(alignment_scores) / len(alignment_scores), 3) if alignment_scores else 0.0,
                "average_opportunity": round(sum(opportunity_scores) / len(opportunity_scores), 3) if opportunity_scores else 0.0,
                "average_risk": round(sum(risk_scores) / len(risk_scores), 3) if risk_scores else 0.0,
            },
            "project_id": business_context.project_id if business_context else None,
            "user_id": business_context.user_id if business_context else None,
            "business_goal": business_context.business_goal if business_context else None,
            "context_source": "business_context" if business_context else "none",
            "model_used": model_name or self.pipeline.active_model,
            "model_metrics": self.pipeline.get_model_performance(model_name or self.pipeline.active_model),
            "llm_payload": llm_payload,
            "context_cache_entry": asdict(cache_entry),
        }

    def _dominant_culture(self, predictions: List[Dict[str, Any]]) -> str:
        counts: Dict[str, int] = {}
        for prediction in predictions:
            label = prediction["prediction"]
            counts[label] = counts.get(label, 0) + 1
        return max(counts, key=counts.get) if counts else "unknown"

    def _assess_alignment(
        self,
        text: str,
        features: Dict[str, float],
        business_context: Optional[BusinessContext],
    ) -> Dict[str, Any]:
        if not business_context:
            return {"alignment_score": 0.5, "match_keywords": []}

        normalized = text.lower()
        matches = []
        if business_context.segment and business_context.segment.lower() in normalized:
            matches.append(business_context.segment.lower())
        for keyword in business_context.normalized_keywords():
            if keyword in normalized:
                matches.append(keyword)

        score = round(min(1.0, 0.4 + len(matches) * 0.15 + features["audience_focus"] * 0.2), 3)
        return {"alignment_score": score, "match_keywords": list(set(matches))}

    def _assess_opportunity(
        self,
        features: Dict[str, float],
        business_context: Optional[BusinessContext],
    ) -> float:
        score = 0.35 + features["cultural_intensity"] * 0.25 + features["regionality"] * 0.2
        if business_context and business_context.objective and "lançamento" in business_context.objective.lower():
            score += 0.1
        return round(min(1.0, score), 3)

    def _assess_risk(
        self,
        features: Dict[str, float],
        business_context: Optional[BusinessContext],
    ) -> float:
        score = 0.25 + max(0.0, 0.5 - features["sentiment"]) * 0.3 + (1 - features["local_context"]) * 0.15
        if business_context and business_context.objective and "crise" in business_context.objective.lower():
            score += 0.1
        return round(min(1.0, score), 3)

    def _build_recommendation(
        self,
        prediction: Dict[str, Any],
        business_context: Optional[BusinessContext],
    ) -> str:
        objective = business_context.objective.lower() if business_context and business_context.objective else ""
        label = prediction["prediction"]
        if "lançamento" in objective:
            return (
                f"Use insights culturais de '{label}' para destacar novidade e comunidade no lançamento. "
                "Priorizando ações de alcance local e digital."
            )
        if "reposição" in objective or "rebranding" in objective:
            return (
                f"Ajuste a narrativa de '{label}' para reforçar posicionamento e diferenciação. "
                "Considere termos regionais e emotivos para aumentar aceitação."
            )
        if "crise" in objective:
            return (
                f"Mitigue riscos em torno de '{label}' priorizando transparência e sinais de confiança. "
                "Evite mensagens ambíguas."
            )
        return (
            f"Explore oportunidades culturais identificadas em '{label}' e combine com palavras-chave do segmento. "
            "Use storytelling focado no público local e na proposta de valor."
        )


class DummyMLPipeline:
    def __init__(self):
        self.models: Dict[str, BrazilianCulturalModel] = {}
        self.active_model: Optional[str] = None
        self.insight_generator = BusinessInsightGenerator(self)

    def list_models(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": name,
                "trained": model.trained,
                "active": name == self.active_model,
                "classes_count": len(model._labels),
                "metrics": model.get_performance().__dict__ if model.get_performance() else None,
            }
            for name, model in self.models.items()
        ]

    def train_model(
        self,
        model_name: str,
        training_data: Union[List[Dict[str, Any]], List[str]],
        target_column: str = "cultural_circle",
    ) -> Dict[str, Any]:
        if training_data and isinstance(training_data[0], dict):
            texts = [item.get("text", "") for item in training_data]
            labels = [item.get(target_column) for item in training_data]
            metadata = [item.get("metadata", {}) for item in training_data]
        else:
            texts = list(training_data)
            labels = []
            metadata = []

        model = BrazilianCulturalModel(model_name)
        metrics = model.train(texts, labels, metadata if metadata else None)
        self.models[model_name] = model
        self.active_model = model_name
        return {"model_name": model_name, "metrics": metrics.__dict__}

    def set_active_model(self, model_name: str) -> None:
        if model_name not in self.models:
            raise ValueError(f"Unknown model '{model_name}'")
        self.active_model = model_name

    def predict(
        self,
        texts: List[str],
        model_name: Optional[str] = None,
        business_context: Optional[BusinessContext] = None,
    ) -> List[str]:
        model = self._get_model(model_name)
        return model.predict(texts)

    def predict_with_confidence(
        self,
        texts: List[str],
        model_name: Optional[str] = None,
        business_context: Optional[BusinessContext] = None,
    ) -> List[Dict[str, Any]]:
        model = self._get_model(model_name)
        results = model.predict_with_confidence(texts)
        if business_context:
            for item in results:
                if business_context.objective and "crise" in business_context.objective.lower():
                    item["confidence"] = round(max(0.35, item["confidence"] - 0.1), 3)
        return results

    def get_model_performance(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        model = self._get_model(model_name)
        metrics = model.get_performance()
        return metrics.__dict__ if metrics else {}

    def analyze_business_insights(
        self,
        texts: List[str],
        business_context: Optional[BusinessContext] = None,
        model_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        return self.insight_generator.analyze(texts, business_context, model_name)

    def _get_model(self, model_name: Optional[str] = None) -> BrazilianCulturalModel:
        key = (model_name or self.active_model) or ""
        if key not in self.models:
            raise RuntimeError("No trained model available")
        return self.models[key]


_pipeline_instance: Optional[DummyMLPipeline] = None


def get_ml_pipeline() -> DummyMLPipeline:
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = DummyMLPipeline()
    return _pipeline_instance


def create_sample_training_data() -> List[Dict[str, Any]]:
    return [
        {
            "text": "Pesquisa de comportamento cultural no Nordeste",
            "cultural_circle": "cultural",
            "metadata": {"keywords": ["Nordeste", "cultural", "pesquisa"]},
        },
        {
            "text": "Tendência de consumo urbano em São Paulo",
            "cultural_circle": "urban",
            "metadata": {"keywords": ["São Paulo", "urbano", "consumo"]},
        },
        {
            "text": "Evento popular no interior",
            "cultural_circle": "regional",
            "metadata": {"keywords": ["interior", "regional", "evento"]},
        },
    ]
