import yfinance as yf
import json

# yfinance에서 가져올 수 있는 Ticker 정보 확인
etf = yf.Ticker("SPY")

print(json.dumps(etf.info, indent=4, ensure_ascii=False))