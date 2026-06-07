import os
import pytest

from api.endpoints.emerging_profiles import EmergingProfile, EmergingProfilesResponse


try:
    from api.main import app
    from fastapi.testclient import TestClient
except Exception:
    app = None
    TestClient = None


def test_emerging_profile_model_accepts_derived_data():
    profile = EmergingProfile(
        name="Entusiastas de Música",
        category="Musical",
        emergence_score=0.78,
        growth_velocity=12.5,
        uniqueness_index=0.42,
        stability_score=0.61,
        summary="Grupo com alto engajamento e tendências de crescimento." 
    )
    assert profile.name == "Entusiastas de Música"
    assert profile.emergence_score > 0


def test_emerging_profiles_response_model():
    response = EmergingProfilesResponse(
        status="success",
        data=[
            EmergingProfile(
                name="Curadores de Cultura",
                category="Cultural",
                emergence_score=0.55,
                growth_velocity=8.2,
                uniqueness_index=0.33,
                stability_score=0.72,
                summary="Perfil emergente ligado a cultura digital."
            )
        ],
        count=1,
        plan="pro",
        top_n=6,
    )
    assert response.count == 1
    assert response.data[0].category == "Cultural"


@pytest.mark.skipif(app is None or TestClient is None, reason="FastAPI app not available")
def test_emerging_profiles_endpoint_returns_data():
    client = TestClient(app, base_url="http://localhost")
    response = client.get("/api/v8/dashboard/emerging-profiles?plan=free&top_n=1")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] in ("success", "refreshed")
    assert "data" in json_response
    assert isinstance(json_response["data"], list)
    assert json_response["count"] == len(json_response["data"])


def get_real_smoke_token():
    auth_token = os.getenv("SMOKE_TEST_AUTH_TOKEN")
    if not auth_token:
        pytest.skip("SMOKE_TEST_AUTH_TOKEN is not configured; skipping real backend smoke test.")

    if not os.getenv("SUPABASE_URL") or not (os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")):
        pytest.skip("Supabase environment variables not configured for real Supabase auth.")

    return auth_token


@pytest.mark.skipif(app is None or TestClient is None, reason="FastAPI app not available")
def test_emerging_profiles_status_endpoint_smoke_test():
    auth_token = get_real_smoke_token()
    client = TestClient(app, base_url="http://localhost")
    response = client.get(
        "/api/v8/dashboard/emerging-profiles/status",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "ready"
    assert json_response.get("available") is True
    assert "supabase_health" in json_response
    assert "supabase_dns" in json_response
    assert "redis_health" in json_response
    assert "message" in json_response
