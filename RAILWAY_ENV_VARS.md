# Railway Environment Variables

## Required Variables
- `PORT` - Automatically set by Railway (DO NOT set this manually)

## Optional Variables (with defaults)

| Variable | Default Value | Description |
|----------|--------------|-------------|
| `WEATHER_LAB_API_URL` | `https://weather-lab-data-api-production.up.railway.app` | URL of the weather-lab-data-api service |
| `RISK_RADIUS_KM` | `160.9` | Risk radius in kilometers (100 miles) |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

## Setting Variables on Railway

### Via Railway CLI
```bash
railway variables set WEATHER_LAB_API_URL=https://your-weather-api-url.com
railway variables set RISK_RADIUS_KM=160.9
railway variables set LOG_LEVEL=INFO
```

### Via Railway Dashboard
1. Navigate to your Railway project
2. Select the `hurricane-risk-api` service
3. Click on the **Variables** tab
4. Click **+ New Variable** for each variable
5. Enter the variable name and value
6. Click **Add**

## Notes
- All variables are optional and have sensible defaults
- Only set `WEATHER_LAB_API_URL` if your weather API is at a different URL
- `RISK_RADIUS_KM` can be adjusted based on your risk tolerance (default is 100 miles)
- `LOG_LEVEL` can be set to `DEBUG` for more verbose logging during troubleshooting

