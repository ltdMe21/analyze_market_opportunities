
import requests
import pandas as pd
import os

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.polygon.io"

def resolve_symbol(symbol):
    fx = ["EURUSD", "USDCAD", "GBPUSD"]
    crypto = ["BTCUSD", "ETHUSD"]
    if symbol.upper() in fx:
        return f"C:{symbol.upper()}"
    elif symbol.upper() in crypto:
        return f"X:{symbol.upper()}"
    return symbol.upper()

# Tutte le funzioni precedenti identiche tranne questa:

def analyze_range_structure(symbol, date, box_size=100):
    symbol = resolve_symbol(symbol)

    url_date = f"{BASE_URL}/v2/aggs/ticker/{symbol}/range/1/day/{date}/{date}?adjusted=true&apiKey={API_KEY}"
    res = requests.get(url_date).json()

    if "results" not in res or not res["results"]:
        url_prev = f"{BASE_URL}/v2/aggs/ticker/{symbol}/prev?adjusted=true&apiKey={API_KEY}"
        res = requests.get(url_prev).json()
        if "results" not in res or not res["results"]:
            return {"error": "No daily range data from Polygon (date and fallback failed)"}

    d = res["results"][0]
    high = d["h"]
    low = d["l"]
    close = d["c"]
    box_top = (int(high * 10000 / box_size) + 1) * (box_size / 10000)
    box_bottom = (int(low * 10000 / box_size)) * (box_size / 10000)
    return {
        "high": high,
        "low": low,
        "close": close,
        "box_levels": [round(box_bottom, 4), round(box_top, 4)]
    }

# Le altre funzioni restano identiche: ident_signal_days, detect_time_window_setups, etc.

# Wrapper
def analyze_market_opportunities(symbol, date, session_time, timeframe="M15", lookback_days=5):
    try:
        signal = identify_signal_days(symbol, date, lookback_days)
        time_setup = detect_time_window_setups(symbol, date, session_time)
        price_pattern = detect_price_behavior_pattern(symbol, date, timeframe)
        range_info = analyze_range_structure(symbol, date)
        trade_eval = evaluate_trade_quality(symbol, date, session_time)
        return {
            "signal_day": signal,
            "time_window_setup": time_setup,
            "price_behavior_pattern": price_pattern,
            "range_structure": range_info,
            "trade_quality": trade_eval
        }
    except Exception as e:
        return {"error": str(e)}
