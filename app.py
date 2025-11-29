from flask import Flask, request, jsonify
import os
from data_fetcher import fetch_klines

app = Flask(__name__)

# Simple demo user (replace with real user system for production)
TEST_USER = {"email":"test@example.com","password":"1234","token":"demo-token-123"}

@app.route("/")
def home():
    return jsonify({"service":"HB Trading Signal API","status":"ok"})

@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    email = data.get("email","")
    password = data.get("password","")
    if email == TEST_USER["email"] and password == TEST_USER["password"]:
        return jsonify({"status":"ok","token":TEST_USER["token"]})
    return jsonify({"status":"error","message":"invalid_credentials"}), 401

@app.route("/analyze", methods=["GET","POST"])
def analyze():
    params = request.args if request.method == 'GET' else request.get_json(silent=True) or {}
    symbol = params.get("symbol","BTCUSDT")
    timeframe = params.get("timeframe","15m")
    limit = int(params.get("limit",200))
    auth = request.headers.get("Authorization","").strip()
    token = auth.split(" ",1)[1] if auth.startswith("Bearer ") else auth
    if token != TEST_USER["token"]:
        return jsonify({"status":"error","message":"unauthorized"}), 401
    try:
        df = fetch_klines(symbol=symbol, interval=timeframe, limit=limit)
    except Exception as e:
        return jsonify({"error":"fetch_failed","detail":str(e)}), 502
    try:
        import pandas as pd
        df['sma7'] = df['close'].rolling(7).mean()
        df['sma21'] = df['close'].rolling(21).mean()
        last = df.iloc[-1]
        signal = "neutral"
        if pd.notna(last['sma7']) and pd.notna(last['sma21']):
            if last['sma7'] > last['sma21']:
                signal = "LONG"
            elif last['sma7'] < last['sma21']:
                signal = "SHORT"
        resp = {"status":"ok","symbol":symbol,"timeframe":timeframe,"signal":signal,
                "indicators":{"sma7": None if pd.isna(last['sma7']) else float(last['sma7']),
                              "sma21": None if pd.isna(last['sma21']) else float(last['sma21']),
                              "close": float(last['close'])}}
        return jsonify(resp)
    except Exception as e:
        return jsonify({"error":"indicator_failed","detail":str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
