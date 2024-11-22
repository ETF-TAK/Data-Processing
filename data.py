import pandas as pd
import yfinance as yf
import datetime
import requests
import json

def safe_get(data, key, default=None):
    value = data.get(key, default)
    if value == "N/A" or value is None:
        return default
    return value

# ETF 심볼 리스트
symbols = ["SHOC", "SPY", "SMCX", "MSTU", "YMAX", "IQQQ", "GLD", "IAU"]

results = []

for symbol in symbols:
    etf = yf.Ticker(symbol)
    
    # 상장일 처리
    fund_inception_date = etf.info.get("fundInceptionDate", None)
    if fund_inception_date and isinstance(fund_inception_date, (int, float)):
        listing_date = datetime.datetime.utcfromtimestamp(fund_inception_date).isoformat()
    else:
        listing_date = None
    
    # Nation 매핑
    etf_num = etf.info.get("", "N/A")
    nation_mapping = {1: "US", 0: "KOREA"}
    nation = nation_mapping[1 if etf_num == "N/A" else 0]

    # Category 매핑
    category_mapping = {
        "GROWTH": "GROWTH",
        "LEVERAGE": "LEVERAGE",
        "DIVIDEND": "DIVIDEND",
        "GOLD": "GOLD"
    }
    category = category_mapping.get("GOLD", "GOLD")

    # 데이터 구성
    data = {
        "name": safe_get(etf.info, "shortName", "N/A"),
        "type": safe_get(etf.info, "quoteType", "N/A"),
        "company": safe_get(etf.info, "fundFamily", "N/A"),
        "listingDate": listing_date,
        "equity": safe_get(etf.info, "0", 0),
        "netWorth": safe_get(etf.info, "totalAssets", 0),
        "dividendRate": safe_get(etf.info, "trailingAnnualDividendRate", 0.0),
        "sector": safe_get(etf.info, "sector", "N/A"),
        "category": category,
        "fee": safe_get(etf.info, "expenseRatio", 0),
        "price": safe_get(etf.info, "regularMarketOpen", 0),
        "previousClose": safe_get(etf.info, "regularMarketPreviousClose", 0),
        "ticker": symbol,
        "etfNum": etf_num,
        "iNav": safe_get(etf.info, "navPrice", 0.0),
        "investPoint": safe_get(etf.info, "longBusinessSummary", "N/A"),
        "nation": nation
    }
    results.append(data)

# 결과 출력
for result in results:
    print("\n=== ETF 데이터 ===")
    for key, value in result.items():
        print(f"{key}: {value}")

# 서버로 데이터 전송
url = "http://localhost:8080/save"

for result in results:
    print("전송 데이터:", json.dumps(result, indent=2))
    response = requests.post(url, json=result)
    if response.status_code == 200:
        try:
            print("전송 성공:", response.json())
        except requests.exceptions.JSONDecodeError:
            print("JSON 디코딩 실패. 응답 내용:", response.text)
    else:
        print("전송 실패:", response.status_code, response.text)
