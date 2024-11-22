import pandas as pd
import yfinance as yf
import datetime
import requests

def safe_get(data, key, default=None):
    value = data.get(key, default)
    if value == "N/A" or value is None:
        return default
    return value

symbols = ["SHOC", "SPY", "UMDD", "MSTU", "HIDV", "NVDY", "GLD", "IAU"]   # 성장 레버리지 배당 금 미국

results = []

for symbol in symbols:
    etf = yf.Ticker(symbol)
    
    fund_inception_date = etf.info.get("fundInceptionDate")
    listing_date = datetime.datetime.utcfromtimestamp(fund_inception_date).isoformat() if fund_inception_date else None
    
    data = {
        "name": etf.info.get("shortName", "N/A"),  # ETF 종목이름
        "type": etf.info.get("quoteType", "N/A"),  # ETF 타입
        "company": etf.info.get("fundFamily", "N/A"),  # 운용사
        "listingDate": listing_date,  # 상장일 (ISO 8601 형식)
        "equity": etf.info.get("0", 0),  # 기초 자산 (숫자값이 필요하면 수정 필요)
        "netWorth": etf.info.get("totalAssets", 0),  # 순자산
        "dividendRate": etf.info.get("yield", 0),  # 배당률
        "sector": etf.info.get("sector", "N/A"),  # 섹터
        "category": etf.info.get("", "GOLD"),  # 카테고리
        "fee": (etf.info.get("expenseRatio", 0)),  # 수수료
        "price": etf.info.get("regularMarketOpen", 0),  # 현재가
        "previousClose": etf.info.get("regularMarketPreviousClose", 0),  # 전일 종가
        "ticker": symbol,  # 미국 ETF 심볼 (티커)
        "etfNum": etf.info.get("", "N/A"),  # 한국 ETF 심볼
        "iNav": etf.info.get("navPrice", 0.0),  # iNav
        "investPoint": etf.info.get("longBusinessSummary", "N/A")  # 투자 포인트
    }
    results.append(data)

for result in results:
    print("\n=== ETF 데이터 ===")
    for key, value in result.items():
        print(f"{key}: {value}")

url = "http://localhost:8080/save"

for result in results:
    response = requests.post(url, json=result)
    if response.status_code == 200:
        try:
            print("전송 성공:", response.json())
        except requests.exceptions.JSONDecodeError:
            print("JSON 디코딩 실패. 응답 내용:", response.text)
    else:
        print("전송 실패:", response.status_code, response.text)