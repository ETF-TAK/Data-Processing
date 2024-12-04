import requests
from bs4 import BeautifulSoup
import mysql.connector
import logging

def load_symbols_from_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        symbols = [symbol.strip() for symbol in content.split(',')]
    return symbols

def fetch_invest_points(etf_num):
    
    url = f'https://www.k-etf.com/etf/{etf_num}'
    point = []

    res = requests.get(url)
    data = res.text

    soup = BeautifulSoup(data, 'html.parser')

    elements = soup.select("div.flex.flex-col.gap-1")
    for element in elements:
        title = element.find("span", class_="text-[13px] sm:text-[14px] font-semibold text-inherit")
        if title and title.get_text(strip=True) == "투자포인트":
            invest_point = element.find("span", class_="text-[12px] sm:text-[13px] font-normal text-inherit")
            if invest_point:
                processed_point = invest_point.get_text(strip=True).replace('\n', ' ')
                point.append(processed_point)
    
    return point

def save_to_mysql(etf_num, points):
    try:
        connection = mysql.connector.connect(
            host="tak-database.czgk4io0mrpg.ap-northeast-2.rds.amazonaws.com",
            user="admin",
            password="tak-etf2!",
            database="TAK"
        )

        cursor = connection.cursor()

        for point in points:
            query = """
            UPDATE etf
            SET invest_point = %s 
            WHERE etf_num = %s
            """
            cursor.execute(query, (point, etf_num))
        
        connection.commit()
        print(f"{etf_num}의 투자포인트를 저장했습니다.")
    
    except mysql.connector.Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    file_path = "./korea_etf.txt"
    symbols = load_symbols_from_file(file_path)
    
    for etf_num in symbols:
        etf_num = etf_num.removesuffix(".KS")
        print(f"Fetching data for ETF: {etf_num}")
        points = fetch_invest_points(etf_num)
        print(f"Points fetched: {points}")
        
        if points:
            save_to_mysql(etf_num, points)
        
