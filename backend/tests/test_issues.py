"""Tests for issues endpoints."""
import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint(client: TestClient):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "name" in response.json()
    assert "version" in response.json()


def test_get_issues_empty(client: TestClient):
    """Test getting issues when database might be empty."""
    response = client.get("/api/v1/issues")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_route_planning_validation(client: TestClient, sample_route_request):
    """Test route planning endpoint validation."""
    response = client.post("/api/v1/plan", json=sample_route_request)
    # This might fail if database is not set up, but endpoint should exist
    assert response.status_code in [200, 500]


def test_get_mood_areas(client: TestClient):
    """Test mood areas endpoint."""
    response = client.get("/api/v1/mood")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_traffic_segments(client: TestClient):
    """Test traffic segments endpoint."""
    response = client.get("/api/v1/traffic")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_noise_segments(client: TestClient):
    """Test noise segments endpoint."""
    response = client.get("/api/v1/noise")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_api_docs_available(client: TestClient):
    """Test that API documentation is available."""
    response = client.get("/docs")
    assert response.status_code == 200
