
import requests
import pandas as pd
import os

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.polygon.io"

def identify_signal_days(symbol, date, lookback_days=5):
    url = f"{BASE_URL}/v2/aggs/ticker/C:{symbol}/range/1/day/{date}/{date}?apiKey={API_KEY}"
    data = requests.get(url).json()
    if "results" not in data:
        return {"error": f"No results from Polygon for URL: {url}"}
    today = data["results"][0]
    end_ts = today["t"]
    start_ts = pd.to_datetime(end_ts, unit="ms") - pd.Timedelta(days=lookback_days)
    start_date = start_ts.strftime("%Y-%m-%d")
    history_url = f"{BASE_URL}/v2/aggs/ticker/C:{symbol}/range/1/day/{start_date}/{date}?apiKey={API_KEY}"
    res = requests.get(history_url).json()
    if "results" not in res:
        return {"error": f"No historical data from Polygon for URL: {history_url}"}
    df = pd.DataFrame([{
        "date": pd.to_datetime(d["t"], unit="ms").date(),
        "open": d["o"],
        "high": d["h"],
        "low": d["l"],
        "close": d["c"]
    } for d in res["results"]])
    signals = []
    for i in range(1, len(df)):
        today = df.iloc[i]
        yesterday = df.iloc[i - 1]
        if today["high"] < yesterday["high"] and today["low"] > yesterday["low"]:
            signals.append({"date": str(today["date"]), "type": "Inside Day"})
        elif today["high"] > yesterday["high"] and today["low"] < yesterday["low"]:
            signals.append({"date": str(today["date"]), "type": "Outside Day"})
        elif today["close"] > today["open"] and yesterday["close"] < yesterday["open"]:
            signals.append({"date": str(today["date"]), "type": "First Green Day"})
        elif today["close"] < today["open"] and yesterday["close"] > yesterday["open"]:
            signals.append({"date": str(today["date"]), "type": "First Red Day"})
    return signals[-1] if signals else {"date": date, "type": "Nessun segnale rilevato"}

def detect_time_window_setups(symbol, date, session_time="NewYork"):
    url = f"{BASE_URL}/v2/aggs/ticker/C:{symbol}/range/5/minute/{date}/{date}?adjusted=true&sort=asc&limit=1000&apiKey={API_KEY}"
    res = requests.get(url).json()
    if "results" not in res:
        return {"error": f"No intraday data from Polygon for URL: {url}"}
    df = pd.DataFrame([{
        "ts": pd.to_datetime(d["t"], unit="ms"),
        "open": d["o"], "high": d["h"], "low": d["l"], "close": d["c"]
    } for d in res["results"]])
    if session_time == "NewYork":
        df = df[(df["ts"].dt.hour >= 13) & (df["ts"].dt.hour <= 16)]
    elif session_time == "London":
        df = df[(df["ts"].dt.hour >= 7) & (df["ts"].dt.hour <= 10)]
    elif session_time == "Asia":
        df = df[(df["ts"].dt.hour >= 0) & (df["ts"].dt.hour <= 3)]
    if df.empty:
        return {"error": "Nessun dato nella sessione selezionata"}
    volatility = df["high"].max() - df["low"].min()
    return {
        "session": session_time,
        "high": df["high"].max(),
        "low": df["low"].min(),
        "volatility_range": round(volatility, 5)
    }

def detect_price_behavior_pattern(symbol, date, timeframe="M15"):
    tf_map = {"M5": 5, "M15": 15, "H1": 60, "H4": 240}
    tf = tf_map[timeframe]
    url = f"{BASE_URL}/v2/aggs/ticker/C:{symbol}/range/{tf}/minute/{date}/{date}?adjusted=true&sort=asc&limit=1000&apiKey={API_KEY}"
    res = requests.get(url).json()
    if "results" not in res:
        return {"error": f"No timeframe data from Polygon for URL: {url}"}
    df = pd.DataFrame([{
        "ts": pd.to_datetime(d["t"], unit="ms"),
        "open": d["o"], "high": d["h"], "low": d["l"], "close": d["c"]
    } for d in res["results"]])
    df["range"] = df["high"] - df["low"]
    max_range_idx = df["range"].idxmax()
    pattern = "Consolidation"
    if df["close"].iloc[max_range_idx] > df["open"].iloc[max_range_idx]:
        pattern = "Parabolic Move"
    return {
        "pattern": pattern,
        "max_range_candle": str(df.iloc[max_range_idx]["ts"]),
        "range": round(df["range"].max(), 5)
    }

def analyze_range_structure(symbol, date, box_size=100):
    url = f"{BASE_URL}/v2/aggs/ticker/C:{symbol}/range/1/day/{date}/{date}?adjusted=true&apiKey={API_KEY}"
    res = requests.get(url).json()
    if "results" not in res:
        return {"error": f"No daily range data from Polygon for URL: {url}"}
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

def evaluate_trade_quality(symbol, date, session_time):
    range_data = analyze_range_structure(symbol, date)
    if "error" in range_data:
        return range_data
    volatility = range_data["high"] - range_data["low"]
    quality = "Low"
    if volatility > 0.005:
        quality = "High"
    elif volatility > 0.002:
        quality = "Moderate"
    return {
        "session": session_time,
        "volatility": round(volatility, 5),
        "quality_rating": quality
    }

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
