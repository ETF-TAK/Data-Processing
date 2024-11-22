import pandas as pd
import yfinance as yf
import datetime
import requests
import json

etf_mapping = {
    "KODEX": "삼성자산운용",
    "TIGER": "미래에셋자산운용",
    "RISE": "KB자산운용",
    "ACE": "한국투자신탁운용",
    "SOL": "신한자산운용",
    "ARIRANG": "한화자산운용",
    "HANARO": "NH-Amundi자산운용",
    "KOSEF": "키움자산운용"
}

def safe_get(data, key, default=None):
    value = data.get(key, default)
    if value == "N/A" or value is None:
        return default
    return value

# ETF 심볼 리스트
symbols = [ "SHOC", "SPY", "UMDD", "MSTU", "HIDV", "NVDY", "GLD", "IAU", "462330.KS", "484880.KS" ]

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
    #nation = nation_mapping[1 if etf_num == "N/A" else 0]
    
    # ticker 매핑, 한국 ETF data
    ticker_type = safe_get(etf.info, "symbol")
    if ticker_type.endswith(".KS"):
        nation = nation_mapping[0]
        ticker = None
        etf_num = ticker_type.removesuffix(".KS")
        
        url = 'https://finance.naver.com/api/sise/etfItemList.nhn'
        json_data = json.loads(requests.get(url).text)
        df = pd.json_normalize(json_data['result']['etfItemList'])
        etf_nav = df.loc[df['itemcode'] == etf_num, 'nav']
        etf_aum = df.loc[df['itemcode'] == etf_num, 'marketSum']
        etf_company = df.loc[df['itemcode'] == etf_num, 'itemname']
        nav = etf_nav.values[0]
        netWorth = int(etf_aum.values[0])
        company_etf = etf_company.values[0]
        company_name = company_etf.split(" ")[0]
        company = etf_mapping.get(company_name, "Unknown")
    else:
        nation = nation_mapping[1]
        ticker = ticker_type
        etf_num = None
        nav = safe_get(etf.info, "navPrice", 0.0)
        netWorth = safe_get(etf.info, "totalAssets", 0)
        company = safe_get(etf.info, "fundFamily", "N/A")

    
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
        "company": company,
        "listingDate": listing_date,
        "equity": safe_get(etf.info, "0", 0),
        "netWorth": netWorth,
        "dividendRate": etf.info.get("yield", 0),
        "sector": safe_get(etf.info, "sector", "N/A"),
        "category": category,
        "fee": safe_get(etf.info, "expenseRatio", 0),
        "price": safe_get(etf.info, "regularMarketOpen", 0),
        "previousClose": safe_get(etf.info, "regularMarketPreviousClose", 0),
        "ticker": ticker,
        "etfNum": etf_num,
        "iNav": nav,
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