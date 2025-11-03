"""Request models for Hurricane Risk API"""
from pydantic import BaseModel, Field
from typing import Dict, List, Any


class RiskAnalysisRequest(BaseModel):
    """Request for single date risk analysis."""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    days: int = Field(default=1, description="Number of days to analyze")


class RiskAnalysisRangeRequest(BaseModel):
    """Request for date range risk analysis."""
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    days: int = Field(..., ge=1, le=30, description="Number of days to forecast (1-30)")


class RiskAnalysisWithDataRequest(BaseModel):
    """Request for risk analysis with provided weather data."""
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    days: int = Field(..., ge=1, le=30, description="Number of days to analyze (1-30)")
    data: Dict[str, Dict[str, List[Dict[str, Any]]]] = Field(
        ..., 
        description="Weather data structure: {date: {records: [...]}, ...}"
    )
