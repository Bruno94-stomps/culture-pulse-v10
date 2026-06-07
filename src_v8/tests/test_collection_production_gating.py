import os
import sys
import importlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
import src_v8.api.main as main


def test_production_blocks_simulated_sources(monkeypatch):
    monkeypatch.setenv('ENVIRONMENT', 'production')
    monkeypatch.setenv('ALLOW_DEMO_COLLECTION', 'false')

    import collectors.orchestrator as orchestrator
    orchestrator = importlib.reload(orchestrator)

    with pytest.raises(ValueError, match=r"Demo sources not allowed in production"):
        orchestrator._filter_sources_for_environment(['youtube', 'instagram'])

    assert orchestrator._filter_sources_for_environment(['youtube', 'news']) == ['youtube', 'news']


def test_production_allows_real_sources_only(monkeypatch):
    monkeypatch.setenv('ENVIRONMENT', 'production')
    monkeypatch.setenv('ALLOW_DEMO_COLLECTION', 'true')

    import collectors.orchestrator as orchestrator
    orchestrator = importlib.reload(orchestrator)

    assert orchestrator._filter_sources_for_environment(['youtube', 'instagram']) == ['youtube', 'instagram']


def test_collect_status_and_sources_endpoints_are_available(monkeypatch):
    monkeypatch.setenv('ENVIRONMENT', 'production')
    monkeypatch.setenv('ENABLE_DEMO_AUTH', 'true')

    import src_v8.api.middleware.auth as auth_module
    importlib.reload(auth_module)
    importlib.reload(main)

    client = TestClient(main.app, base_url="http://localhost")

    headers = {
        "host": "localhost",
        "Authorization": "Bearer cp_demo_2025_free_tier"
    }

    status_response = client.get('/api/v8/collect/status', headers=headers)
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data['api_info']['production_mode'] in (True, False)
    assert 'source_policy' in status_data['api_info']

    sources_response = client.get('/api/v8/collect/sources', headers=headers)
    assert sources_response.status_code == 200
    sources_data = sources_response.json()
    assert sources_data['allow_demo_collection'] in (True, False)
    assert 'instagram' in sources_data['sources']
    assert 'meetup' in sources_data['sources']
