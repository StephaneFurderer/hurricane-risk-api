"""Tests for health check endpoint"""
import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """Test client for FastAPI app."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint returns correct information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Hurricane Risk API"
    assert data["version"] == "1.0.0"
    assert "docs" in data


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "hurricane-risk-api"
    assert "timestamp" in data

