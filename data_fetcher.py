import requests, pandas as pd, os
OKX_CANDLES_URL = os.environ.get("OKX_CANDLES_URL","https://www.okx.com/api/v5/market/candles")

TF_MAP = {"1m":"1m","3m":"3m","5m":"5m","15m":"15m","30m":"30m","1h":"1H","4h":"4H","1d":"1D"}

def fetch_klines(symbol='BTC-USDT-SWAP', interval='15m', limit=200):
    # Accept both BTCUSDT and BTC-USDT-SWAP forms
    inst = symbol
    if '-' not in symbol:
        # try to convert like BTCUSDT -> BTC-USDT-SWAP
        if symbol.endswith('USDT'):
            inst = symbol[:-4] + '-USDT-SWAP'
    bar = TF_MAP.get(interval.lower(), interval)
    params = {'instId': inst, 'bar': bar, 'limit': str(limit)}
    r = requests.get(OKX_CANDLES_URL, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    if data.get('code') not in (None, '0'):
        raise Exception('OKX error: %s' % str(data))
    items = data.get('data', [])
    rows=[]
    for it in items:
        ts=int(it[0]); o=float(it[1]); h=float(it[2]); l=float(it[3]); c=float(it[4]); v=float(it[5])
        rows.append([ts,o,h,l,c,v])
    rows.reverse()
    df=pd.DataFrame(rows, columns=['timestamp','open','high','low','close','volume'])
    df['timestamp']=pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df
