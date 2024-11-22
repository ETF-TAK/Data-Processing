import requests
import json
import pandas as pd

url = 'https://finance.naver.com/api/sise/etfItemList.nhn'
json_data = json.loads(requests.get(url).text)

df = pd.json_normalize(json_data['result']['etfItemList'])

print(df.columns)