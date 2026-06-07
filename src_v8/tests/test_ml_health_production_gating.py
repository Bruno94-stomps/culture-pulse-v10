import os
import sys
import importlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
import src_v8.api.main as main


def test_ml_health_production_reports_demo_gate(monkeypatch):
    monkeypatch.setenv('ENVIRONMENT', 'production')
    monkeypatch.setenv('ALLOW_DEMO_COLLECTION', 'false')
    monkeypatch.setenv('ENABLE_DEMO_AUTH', 'true')

    # Re-import the ML endpoint module so the runtime env values are consistent.
    import src_v8.api.endpoints.ml as ml_module
    import src_v8.api.middleware.auth as auth_module
    importlib.reload(auth_module)
    importlib.reload(ml_module)
    importlib.reload(main)

    client = TestClient(main.app, base_url="http://localhost")
    response = client.get(
        '/api/v8/ml/health',
        headers={
            "host": "localhost",
            "Authorization": "Bearer cp_demo_2025_free_tier"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'
    assert data['production_mode'] is True
    assert data['allow_demo_collection'] is False
    assert data['source_policy'] == 'real-only'


def test_ml_health_demo_override_allowed(monkeypatch):
    monkeypatch.setenv('ENVIRONMENT', 'production')
    monkeypatch.setenv('ALLOW_DEMO_COLLECTION', 'true')
    monkeypatch.setenv('ENABLE_DEMO_AUTH', 'true')

    import src_v8.api.endpoints.ml as ml_module
    import src_v8.api.middleware.auth as auth_module
    importlib.reload(auth_module)
    importlib.reload(ml_module)
    importlib.reload(main)

    client = TestClient(main.app, base_url="http://localhost")
    response = client.get(
        '/api/v8/ml/health',
        headers={
            "host": "localhost",
            "Authorization": "Bearer cp_demo_2025_free_tier"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data['production_mode'] is True
    assert data['allow_demo_collection'] is True
    assert data['source_policy'] == 'real-plus-demo-allowed'


def test_global_health_exposes_source_policy(monkeypatch):
    monkeypatch.setenv('ENVIRONMENT', 'production')
    monkeypatch.setenv('ALLOW_DEMO_COLLECTION', 'false')

    client = TestClient(main.app, base_url="http://localhost")
    response = client.get('/api/v8/health', headers={"host": "localhost"})

    assert response.status_code == 200
    data = response.json()
    assert data['production_mode'] is True
    assert data['allow_demo_collection'] is False
    assert data['source_policy'] == 'real-only'
