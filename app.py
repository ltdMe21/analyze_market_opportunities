
from fastapi import FastAPI, Query
from polygon_trading_analysis import analyze_market_opportunities

app = FastAPI()

@app.get("/analyze")
def analyze(symbol: str, date: str, session_time: str, timeframe: str = "M15", lookback_days: int = 5):
    result = analyze_market_opportunities(symbol, date, session_time, timeframe, lookback_days)
    return result
