import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["name"] == "MIKASA"
    assert "version" in data
    assert "brain_ready" in data

def test_core_info_endpoint():
    response = client.get("/api/core")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "MIKASA"
    assert data["mode"] == "local"
