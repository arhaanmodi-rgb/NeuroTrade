"""Integration tests for FastAPI endpoints."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest

try:
    from fastapi.testclient import TestClient
    from api.main import app
    client = TestClient(app)
    API_AVAILABLE = True
except Exception:
    API_AVAILABLE = False


@pytest.mark.skipif(not API_AVAILABLE, reason='FastAPI not available')
def test_root():
    response = client.get('/')
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'NeuroTrade API'


@pytest.mark.skipif(not API_AVAILABLE, reason='FastAPI not available')
def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    data = response.json()
    assert 'status' in data
    assert 'models_loaded' in data
    assert isinstance(data['models_loaded'], list)


@pytest.mark.skipif(not API_AVAILABLE, reason='FastAPI not available')
def test_stocks_list():
    response = client.get('/stocks')
    assert response.status_code == 200
    data = response.json()
    assert 'stocks' in data
    assert isinstance(data['stocks'], list)


@pytest.mark.skipif(not API_AVAILABLE, reason='FastAPI not available')
def test_portfolio():
    response = client.get('/portfolio')
    assert response.status_code == 200
    data = response.json()
    assert 'total_value' in data
    assert 'positions' in data


@pytest.mark.skipif(not API_AVAILABLE, reason='FastAPI not available')
def test_trades():
    response = client.get('/trades')
    assert response.status_code == 200
    data = response.json()
    assert 'trades' in data
    assert isinstance(data['trades'], list)


@pytest.mark.skipif(not API_AVAILABLE, reason='FastAPI not available')
def test_invalid_stock_signal():
    response = client.get('/signal/INVALID_STOCK_XYZ')
    assert response.status_code == 404
