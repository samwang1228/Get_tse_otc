from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import pandas as pd
import time

class InstitutionalInvestors:
    def __init__(self):
        self.url = "https://www.twse.com.tw/zh/trading/foreign/t86.html"
        self.driver = webdriver.Chrome()

    def get_institutional_investors_data(self, date):
        self.driver.get(self.url)
        
        # 解析日期
        year, month, day = date.split('/')
        
        # 轉換民國年為西元年
        year = str(int(year) + 1911)
        
        # 選擇年份
        Select(self.driver.find_element(By.NAME, "yy")).select_by_value(year)
        
        # 選擇月份
        Select(self.driver.find_element(By.NAME, "mm")).select_by_value(month)
        
        # 選擇日期
        Select(self.driver.find_element(By.NAME, "dd")).select_by_value(day)
        
        # 點擊查詢按鈕
        self.driver.find_element(By.CSS_SELECTOR, "button.button.search").click()
        
        # 等待表格加載
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.table"))
        )
        
        # 獲取表格數據
        table = self.driver.find_element(By.CSS_SELECTOR, "table.table")
        html = table.get_attribute('outerHTML')
        
        # 使用 pd.read_html() 解析表格，並處理可能的異常
        try:
            df = pd.read_html(html)[0]
            # 檢查 DataFrame 是否為空或列名是否正確
            if df.empty or '證券代號' not in df.columns:
                print("表格數據為空或格式不正確")
                return pd.DataFrame()
            return df
        except Exception as e:
            print(f"解析表格時發生錯誤：{str(e)}")
            return pd.DataFrame()

    def search_institutional_buying(self, date, min_foreign=0, min_investment_trust=0):
        df = self.get_institutional_investors_data(date)
        
        if df.empty:
            print(f"{date} 沒有可用的三大法人買賣超資料")
            return pd.DataFrame()

        # 處理數據，篩選符合條件的股票
        try:
            df['外資買超張數'] = pd.to_numeric(df['外陸資買賣超股數(不含外資自營商)'].str.replace(',', ''), errors='coerce') / 1000
            df['投信買超張數'] = pd.to_numeric(df['投信買賣超股數'].str.replace(',', ''), errors='coerce') / 1000

            result = df[(df['外資買超張數'] >= min_foreign) & (df['投信買超張數'] >= min_investment_trust)]
            return result[['證券代號', '證券名稱', '外資買超張數', '投信買超張數']]
        except Exception as e:
            print(f"處理數據時發生錯誤：{str(e)}")
            return pd.DataFrame()

    def __del__(self):
        if hasattr(self, 'driver'):
            self.driver.quit()

# 使用示例
if __name__ == "__main__":
    fetcher = InstitutionalInvestors()
    date = '113/09/04'  # 使用您截圖中的日期
    min_foreign = 100
    min_investment_trust = 50

    try:
        result = fetcher.search_institutional_buying(date, min_foreign, min_investment_trust)
        if not result.empty:
            print(result)
        else:
            print("沒有找到符合條件的股票。")
    except Exception as e:
        print(f"發生錯誤：{str(e)}")
    finally:
        fetcher.__del__()