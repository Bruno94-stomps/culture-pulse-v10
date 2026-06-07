import pytest

from autonomous_agent.ml_foundation.back.ml_pipeline import (
    CulturalFeatureExtractor,
    BusinessContext,
    create_sample_training_data,
    get_ml_pipeline,
)


def test_ml_pipeline_train_predict():
    pipeline = get_ml_pipeline()
    pipeline.models.clear()
    pipeline.active_model = None

    sample_data = create_sample_training_data()
    train_response = pipeline.train_model("cultural-model", sample_data)

    assert train_response["model_name"] == "cultural-model"
    assert train_response["metrics"]["support"] == len(sample_data)
    assert pipeline.active_model == "cultural-model"
    assert pipeline.models["cultural-model"].trained is True

    predictions = pipeline.predict(["Lançamento de marca no Nordeste"], model_name="cultural-model")
    assert isinstance(predictions, list)
    assert len(predictions) == 1

    confidence_results = pipeline.predict_with_confidence(
        ["Lançamento de marca no Nordeste"],
        model_name="cultural-model"
    )
    assert isinstance(confidence_results, list)
    assert len(confidence_results) == 1
    assert confidence_results[0]["prediction"] in [item["cultural_circle"] for item in sample_data]
    assert 0.5 <= confidence_results[0]["confidence"] <= 1.0


def test_business_insight_analysis():
    pipeline = get_ml_pipeline()
    pipeline.models.clear()
    pipeline.active_model = None

    sample_data = create_sample_training_data()
    pipeline.train_model("business-model", sample_data)

    context = BusinessContext(
        brand="Marca Teste",
        segment="consumo urbano",
        objective="lançamento",
        keywords=["São Paulo", "consumo", "lançamento"],
        audiences=["jovem adultas"],
        regions=["São Paulo"],
        circles=["moda", "tecnologia"],
        project_id="proj-123",
        user_id="user-abc",
        business_goal="Lançar nova linha de lifestyle",
    )

    analysis = pipeline.analyze_business_insights(
        ["Campanha de lançamento cultural no centro de São Paulo"],
        business_context=context,
        model_name="business-model",
    )

    assert "insights" in analysis
    assert "summary" in analysis
    assert analysis["summary"]["total_texts"] == 1
    assert len(analysis["insights"]) == 1
    assert analysis["insights"][0]["confidence"] >= 0.5
    assert analysis["project_id"] == "proj-123"
    assert analysis["user_id"] == "user-abc"
    assert analysis["business_goal"] == "Lançar nova linha de lifestyle"
    assert analysis["context_source"] == "business_context"
    assert analysis["model_used"] == "business-model"
    assert "model_metrics" in analysis
    assert set(analysis["model_metrics"].keys()) == {"accuracy", "f1_score", "precision", "recall", "support"}
    assert analysis["model_metrics"]["support"] == len(sample_data)
    assert "llm_payload" in analysis
    assert analysis["llm_payload"]["model"] == "business-model"
    assert analysis["llm_payload"]["prompt_type"] == "business_insight"
    assert isinstance(analysis["llm_payload"]["messages"], list)
    assert analysis["llm_payload"]["metadata"]["project_id"] == "proj-123"
    assert "context_cache_entry" in analysis
    assert analysis["context_cache_entry"]["project_id"] == "proj-123"
    assert analysis["context_cache_entry"]["user_id"] == "user-abc"
    assert isinstance(analysis["context_cache_entry"]["message_history"], list)
    assert analysis["context_cache_entry"]["llm_payload"]["model"] == "business-model"


def test_cultural_feature_extractor_transform_and_extract():
    extractor = CulturalFeatureExtractor()

    transformed = extractor.transform(["Texto 1", "Texto 2"])
    assert len(transformed) == 2
    assert all(len(row) == len(extractor.feature_names) for row in transformed)

    extracted = extractor.extract("Texto de exemplo")
    assert set(extracted.keys()) == set(extractor.feature_names)
    assert all(0.0 <= value <= 1.0 for value in extracted.values())
