import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "src_v8"))

from fastapi.testclient import TestClient
from api.main import app
from api.middleware.auth import create_access_token
from autonomous_agent.ml_foundation.back.ml_pipeline import (
    get_ml_pipeline,
    create_sample_training_data,
)


def test_business_insights_endpoint_flow():
    client = TestClient(app)
    token = create_access_token("client_demo")
    headers = {
        "Authorization": f"Bearer {token}",
        "Host": "localhost",
    }

    pipeline = get_ml_pipeline()
    pipeline.models.clear()
    pipeline.active_model = None

    sample_data = create_sample_training_data()
    pipeline.train_model("business-model", sample_data)

    payload = {
        "texts": ["Campanha cultural de lançamento em São Paulo"],
        "model_name": "business-model",
        "business_context": {
            "brand": "Marca Teste",
            "segment": "moda",
            "objective": "lançamento",
            "keywords": ["São Paulo", "jovem", "moda"],
            "audiences": ["jovem"],
            "regions": ["São Paulo"],
            "circles": ["moda", "tecnologia"],
            "project_id": "proj-123",
            "user_id": "user-abc",
            "business_goal": "Lançar nova coleção urbana",
        },
    }

    response = client.post("/api/v8/ml/analyze/business-insights", json=payload, headers=headers)

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["project_id"] == "proj-123"
    assert data["user_id"] == "user-abc"
    assert data["business_goal"] == "Lançar nova coleção urbana"
    assert data["context_source"] == "business_context"
    assert data["model_used"] == "business-model"
    assert "insights" in data
    assert isinstance(data["insights"], list)
    assert len(data["insights"]) == 1
    assert "llm_payload" in data
    assert data["llm_payload"]["model"] == "business-model"
    assert data["llm_payload"]["metadata"]["project_id"] == "proj-123"
