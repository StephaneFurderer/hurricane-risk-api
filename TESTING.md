# Testing Guide for Hurricane Risk API

## Overview

This test suite provides comprehensive testing for the Hurricane Risk API endpoints using pytest and mocked dependencies.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures and configuration
├── test_health.py      # Health check endpoint tests
└── test_risk.py        # Risk analysis endpoint tests
```

## Running Tests

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_health.py -v
pytest tests/test_risk.py -v
```

### Run Specific Test

```bash
pytest tests/test_health.py::test_root_endpoint -v
```

### Run with Coverage

```bash
pip install pytest-cov
pytest tests/ --cov=. --cov-report=html
```

## Test Coverage

### Health Check Tests (`test_health.py`)

- ✅ Root endpoint (`/`)
- ✅ Health check endpoint (`/api/v1/health`)

### Risk Analysis Tests (`test_risk.py`)

- ✅ Analyze risk endpoint (`/api/v1/analyze`)
  - Single date analysis with mocked dependencies
  - Validates response structure and data

- ✅ Analyze risk range endpoint (`/api/v1/analyze-range`)
  - Date range analysis with mocked dependencies
  - Validates response structure and data

- ✅ Input validation tests
  - Invalid date format
  - Invalid days (out of range > 30)
  - Missing required fields
  - Negative days

## Test Fixtures

### `client`
FastAPI TestClient instance for making HTTP requests

### `mock_hurricane_data_range`
Mock hurricane data structure for date range testing

### `mock_risk_profile_result`
Mock risk profile calculation result

## Mocking Strategy

Tests use dependency injection to mock external services:

1. **WeatherLabClient**: Mocked using `app.dependency_overrides` to avoid actual API calls
2. **RiskCalculator**: Mocked using `unittest.mock.patch` to control calculation results

This allows tests to:
- Run without external dependencies
- Be fast and deterministic
- Test error handling scenarios
- Validate API response structures

## Example Test Output

```
tests/test_health.py::test_root_endpoint PASSED
tests/test_health.py::test_health_endpoint PASSED
tests/test_risk.py::test_analyze_risk_endpoint PASSED
tests/test_risk.py::test_analyze_risk_range_endpoint PASSED
tests/test_risk.py::test_analyze_risk_invalid_date_format PASSED
tests/test_risk.py::test_analyze_risk_range_invalid_days PASSED
tests/test_risk.py::test_analyze_risk_missing_fields PASSED
tests/test_risk.py::test_analyze_risk_negative_days PASSED

8 passed in 0.35s
```

