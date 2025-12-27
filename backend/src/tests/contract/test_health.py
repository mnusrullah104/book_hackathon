import pytest
from fastapi.testclient import TestClient
from ...main import app

client = TestClient(app)

def test_health_check_returns_200():
    response = client.get("/health")
    assert response.status_code == 200

def test_health_check_returns_correct_structure():
    response = client.get("/health")
    assert "status" in response.json()
    assert response.json()["status"] == "healthy"
    assert "timestamp" in response.json()
