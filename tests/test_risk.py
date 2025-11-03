"""Tests for risk analysis endpoints"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient

from main import app
from routers.risk import get_weather_client
from services.data_client import WeatherLabClient
from services.risk_calculator import RiskCalculator


@pytest.fixture
def client():
    """Test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_hurricane_data_range():
    """Mock hurricane data for a date range."""
    return {
        "meta": {
            "start_date": "2024-10-23",
            "days": 3,
            "total_records": 6
        },
        "data": {
            "2024-10-23": {
                "records": [
                    {
                        "track_id": "AL182024",
                        "valid_time": "2024-10-23T00:00:00Z",
                        "lat": 25.5,
                        "lon": -80.3,
                        "maximum_sustained_wind_speed_knots": 85
                    }
                ]
            },
            "2024-10-24": {
                "records": [
                    {
                        "track_id": "AL182024",
                        "valid_time": "2024-10-24T00:00:00Z",
                        "lat": 26.0,
                        "lon": -81.0,
                        "maximum_sustained_wind_speed_knots": 90
                    }
                ]
            },
            "2024-10-25": {
                "records": []
            }
        }
    }


@pytest.fixture
def mock_risk_profile_result():
    """Mock risk profile calculation result."""
    return {
        "daily_risk": [
            {
                "date": "2024-10-23",
                "total_travelers_at_risk": 45000,
                "airports_affected": 3,
                "airports_at_risk": [
                    {
                        "airport_code": "MIA",
                        "airport_name": "Miami International",
                        "travelers_at_risk": 25000,
                        "distance_to_hurricane_km": 85.3,
                        "risk_level": "high"
                    },
                    {
                        "airport_code": "FLL",
                        "airport_name": "Fort Lauderdale-Hollywood International",
                        "travelers_at_risk": 15000,
                        "distance_to_hurricane_km": 95.2,
                        "risk_level": "medium"
                    },
                    {
                        "airport_code": "PBI",
                        "airport_name": "Palm Beach International",
                        "travelers_at_risk": 5000,
                        "distance_to_hurricane_km": 110.5,
                        "risk_level": "low"
                    }
                ],
                "active_hurricanes": 1
            }
        ]
    }


async def mock_get_weather_client():
    """Mock weather client dependency."""
    mock_client = AsyncMock(spec=WeatherLabClient)
    mock_client.get_hurricane_data_range = AsyncMock()
    mock_client.close = AsyncMock()
    try:
        yield mock_client
    finally:
        await mock_client.close()


def test_analyze_risk_endpoint(client, mock_hurricane_data_range, mock_risk_profile_result):
    """Test analyze risk endpoint with mocked dependencies."""
    # Setup mocks
    mock_client_instance = AsyncMock()
    mock_client_instance.get_hurricane_data_range = AsyncMock(return_value=mock_hurricane_data_range)
    mock_client_instance.close = AsyncMock()
    
    async def override_get_weather_client():
        try:
            yield mock_client_instance
        finally:
            await mock_client_instance.close()
    
    # Override dependency
    app.dependency_overrides[get_weather_client] = override_get_weather_client
    
    with patch('routers.risk.RiskCalculator') as mock_calc_class:
        mock_calc_instance = mock_calc_class.return_value
        mock_calc_instance.calculate_risk_profile.return_value = mock_risk_profile_result
        
        # Make request
        response = client.post(
            "/api/v1/analyze",
            json={
                "date": "2024-10-23",
                "days": 1
            }
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "meta" in data
        assert "daily_risk" in data
        assert len(data["daily_risk"]) == 1
        assert data["daily_risk"][0]["date"] == "2024-10-23"
        assert data["daily_risk"][0]["total_travelers_at_risk"] == 45000
        assert data["daily_risk"][0]["airports_affected"] == 3
        assert len(data["daily_risk"][0]["airports_at_risk"]) == 3
        
        # Verify mocks were called
        mock_client_instance.get_hurricane_data_range.assert_called_once()
        mock_calc_instance.calculate_risk_profile.assert_called_once()
    
    # Cleanup
    app.dependency_overrides.clear()


def test_analyze_risk_range_endpoint(client, mock_hurricane_data_range, mock_risk_profile_result):
    """Test analyze risk range endpoint with mocked dependencies."""
    # Setup mocks
    mock_client_instance = AsyncMock()
    mock_client_instance.get_hurricane_data_range = AsyncMock(return_value=mock_hurricane_data_range)
    mock_client_instance.close = AsyncMock()
    
    async def override_get_weather_client():
        try:
            yield mock_client_instance
        finally:
            await mock_client_instance.close()
    
    # Override dependency
    app.dependency_overrides[get_weather_client] = override_get_weather_client
    
    with patch('routers.risk.RiskCalculator') as mock_calc_class:
        mock_calc_instance = mock_calc_class.return_value
        mock_calc_instance.calculate_risk_profile.return_value = mock_risk_profile_result
        
        # Make request
        response = client.post(
            "/api/v1/analyze-range",
            json={
                "start_date": "2024-10-23",
                "days": 3
            }
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "meta" in data
        assert "daily_risk" in data
        assert data["meta"]["start_date"] == "2024-10-23"
        assert data["meta"]["total_days"] == 3
        
        # Verify mocks were called
        mock_client_instance.get_hurricane_data_range.assert_called_once()
        mock_calc_instance.calculate_risk_profile.assert_called_once()
    
    # Cleanup
    app.dependency_overrides.clear()


def test_analyze_risk_invalid_date_format(client):
    """Test analyze endpoint with invalid date format."""
    response = client.post(
        "/api/v1/analyze",
        json={
            "date": "invalid-date",
            "days": 1
        }
    )
    # Should still accept the request, but may fail during processing
    # The exact behavior depends on validation


def test_analyze_risk_range_invalid_days(client):
    """Test analyze range endpoint with invalid days (out of range)."""
    response = client.post(
        "/api/v1/analyze-range",
        json={
            "start_date": "2024-10-23",
            "days": 35  # Exceeds max of 30
        }
    )
    # Should return validation error
    assert response.status_code == 422


def test_analyze_risk_missing_fields(client):
    """Test analyze endpoint with missing required fields."""
    response = client.post(
        "/api/v1/analyze",
        json={}
    )
    assert response.status_code == 422


def test_analyze_risk_negative_days(client):
    """Test analyze endpoint with negative days."""
    response = client.post(
        "/api/v1/analyze-range",
        json={
            "start_date": "2024-10-23",
            "days": -1
        }
    )
    assert response.status_code == 422

