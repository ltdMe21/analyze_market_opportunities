
# Polygon Trading Analysis API

This project exposes an API to analyze trading opportunities based on real-time data from Polygon.io.

## Endpoints

### GET /analyze

Query Parameters:
- symbol: Forex pair (e.g. EURUSD)
- date: YYYY-MM-DD
- session_time: "NewYork", "London", "Asia"
- timeframe: "M5", "M15", "H1", "H4"
- lookback_days: integer (default 5)

Example:
```
/analyze?symbol=EURUSD&date=2025-06-14&session_time=NewYork&timeframe=M15
```

## Deployment

Deploy on Render using a FastAPI-compatible environment.

## Requirements

Install dependencies with:
```
pip install -r requirements.txt
```
# analyze_market_opportunities
