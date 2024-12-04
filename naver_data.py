import requests
import json
import pandas as pd

url = 'https://finance.naver.com/api/sise/etfItemList.nhn'
json_data = json.loads(requests.get(url).text)

df = pd.json_normalize(json_data['result']['etfItemList'])

# print(df.columns)
print(df.shape)
# print(df.head())
# itemcodes = [code + '.KS' for code in df['itemcode'].tolist()]

# print(','.join(itemcodes))

print(df)
print(df.dtypes)