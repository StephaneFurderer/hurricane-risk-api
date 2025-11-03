"""Test fixtures and configuration"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any

from main import app


@pytest.fixture
def client():
    """Test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_hurricane_data_single():
    """Mock hurricane data for a single date."""
    return {
        "meta": {
            "date": "2024-10-23",
            "total_records": 2
        },
        "records": [
            {
                "track_id": "AL182024",
                "valid_time": "2024-10-23T00:00:00Z",
                "lat": 25.5,
                "lon": -80.3,
                "maximum_sustained_wind_speed_knots": 85
            },
            {
                "track_id": "AL182024",
                "valid_time": "2024-10-23T12:00:00Z",
                "lat": 26.0,
                "lon": -81.0,
                "maximum_sustained_wind_speed_knots": 90
            }
        ]
    }


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
def mock_weather_client(mock_hurricane_data_single, mock_hurricane_data_range):
    """Mock WeatherLabClient."""
    async def mock_get_hurricane_data(date: str) -> Dict[str, Any]:
        return mock_hurricane_data_single
    
    async def mock_get_hurricane_data_range(start_date: str, days: int) -> Dict[str, Any]:
        return mock_hurricane_data_range
    
    async def mock_close():
        pass
    
    mock_client = AsyncMock()
    mock_client.get_hurricane_data = mock_get_hurricane_data
    mock_client.get_hurricane_data_range = mock_get_hurricane_data_range
    mock_client.close = mock_close
    
    return mock_client


@pytest.fixture
def mock_risk_calculator():
    """Mock RiskCalculator."""
    mock_calc = MagicMock()
    mock_calc.calculate_risk_profile.return_value = {
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
    return mock_calc

