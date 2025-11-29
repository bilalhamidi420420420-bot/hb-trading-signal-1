# okx_client.py - minimal signing not required for public market data
import os, time, requests, hmac, base64, hashlib, json

# For public market candles we don't need signed auth; only private endpoints need signature
OKX_BASE = os.environ.get("OKX_API_BASE","https://www.okx.com")
CANDLES = OKX_BASE + "/api/v5/market/candles"
