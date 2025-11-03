"""
Risk calculation API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta
from typing import Dict, Any

from models.requests import RiskAnalysisRequest, RiskAnalysisRangeRequest, RiskAnalysisWithDataRequest
from models.responses import RiskAnalysisResponse, DailyRiskProfile, AirportRisk
from services.data_client import WeatherLabClient
from services.risk_calculator import RiskCalculator
from core.config import settings

router = APIRouter()


async def get_weather_client() -> WeatherLabClient:
    """Dependency to get WeatherLab client."""
    client = WeatherLabClient(settings.WEATHER_LAB_API_URL)
    try:
        yield client
    finally:
        await client.close()


@router.get("/health")
async def health() -> Dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "hurricane-risk-api",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@router.post("/analyze", response_model=RiskAnalysisResponse)
async def analyze_risk(
    request: RiskAnalysisRequest,
    client: WeatherLabClient = Depends(get_weather_client)
) -> RiskAnalysisResponse:
    """
    Analyze risk for a single date.
    
    Args:
        request: Risk analysis request with date and days
        client: WeatherLab client dependency
        
    Returns:
        Risk analysis response with daily risk profiles
    """
    try:
        # Fetch hurricane data
        hurricane_data = await client.get_hurricane_data_range(
            request.date, 
            request.days
        )
        
        # Calculate risk profile
        calculator = RiskCalculator()
        result = calculator.calculate_risk_profile(
            hurricane_data,
            request.date,
            request.days
        )
        
        # Build response
        end_date = (datetime.strptime(request.date, '%Y-%m-%d') + 
                   timedelta(days=request.days-1)).strftime('%Y-%m-%d')
        
        response = RiskAnalysisResponse(
            meta={
                'start_date': request.date,
                'end_date': end_date,
                'total_days': request.days,
                'analysis_timestamp': datetime.utcnow().isoformat() + 'Z'
            },
            daily_risk=[
                DailyRiskProfile(**profile) for profile in result['daily_risk']
            ]
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-range", response_model=RiskAnalysisResponse)
async def analyze_risk_range(
    request: RiskAnalysisRangeRequest,
    client: WeatherLabClient = Depends(get_weather_client)
) -> RiskAnalysisResponse:
    """
    Analyze risk for a date range (forecast).
    
    Args:
        request: Risk analysis range request
        client: WeatherLab client dependency
        
    Returns:
        Risk analysis response with daily risk profiles
    """
    try:
        # Fetch hurricane data
        hurricane_data = await client.get_hurricane_data_range(
            request.start_date,
            request.days
        )
        
        # Calculate risk profile
        calculator = RiskCalculator()
        result = calculator.calculate_risk_profile(
            hurricane_data,
            request.start_date,
            request.days
        )
        
        # Build response
        end_date = (datetime.strptime(request.start_date, '%Y-%m-%d') + 
                   timedelta(days=request.days-1)).strftime('%Y-%m-%d')
        
        response = RiskAnalysisResponse(
            meta={
                'start_date': request.start_date,
                'end_date': end_date,
                'total_days': request.days,
                'analysis_timestamp': datetime.utcnow().isoformat() + 'Z'
            },
            daily_risk=[
                DailyRiskProfile(**profile) for profile in result['daily_risk']
            ]
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-records", response_model=RiskAnalysisResponse)
async def analyze_risk_with_data(
    request: RiskAnalysisWithDataRequest
) -> RiskAnalysisResponse:
    """
    Analyze risk using provided weather data (no external API calls).
    
    This endpoint accepts weather data directly and calculates risk exposure.
    Perfect for n8n workflows where you've already fetched weather data.
    
    Args:
        request: Risk analysis request with weather data included
        
    Returns:
        Risk analysis response with daily risk profiles
        
    Example request body:
    {
        "start_date": "2024-10-23",
        "days": 3,
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
                "records": []
            }
        }
    }
    """
    try:
        # Build hurricane data structure expected by calculator
        hurricane_data = {
            'data': request.data
        }
        
        # Calculate risk profile using provided data
        calculator = RiskCalculator()
        result = calculator.calculate_risk_profile(
            hurricane_data,
            request.start_date,
            request.days
        )
        
        # Build response
        end_date = (datetime.strptime(request.start_date, '%Y-%m-%d') + 
                   timedelta(days=request.days-1)).strftime('%Y-%m-%d')
        
        response = RiskAnalysisResponse(
            meta={
                'start_date': request.start_date,
                'end_date': end_date,
                'total_days': request.days,
                'analysis_timestamp': datetime.utcnow().isoformat() + 'Z',
                'data_source': 'provided'
            },
            daily_risk=[
                DailyRiskProfile(**profile) for profile in result['daily_risk']
            ]
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

