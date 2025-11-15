"""Pytest configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


@pytest.fixture
def sample_issue_data():
    """Sample issue data for testing."""
    return {
        "lat": 40.7128,
        "lng": -74.0060,
        "issue_type": "pothole",
        "description": "Large pothole on Main Street"
    }


@pytest.fixture
def sample_route_request():
    """Sample route request for testing."""
    return {
        "origin_lat": 40.7128,
        "origin_lng": -74.0060,
        "destination_lat": 40.7580,
        "destination_lng": -73.9855,
        "route_type": "drive"
    }
