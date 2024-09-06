import pandas as pd
import io
import time
import random
import requests
import csv
from datetime import datetime, timedelta
from tqdm import tqdm
import os

class StockDataFetcher:
    def __init__(self,start_date=None, end_date=None, stock_type=None):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.start_date = pd.to_datetime(start_date) if start_date else None
        self.end_date = pd.to_datetime(end_date) if end_date else None
        self.stock_type = stock_type

    def set_date_range(self, start_date, end_date):
        """設置日期範圍。"""
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)

    def set_stock_type(self, stock_type):
        """設置股票類型。"""
        self.stock_type = stock_type
        
    def get_stock_data(self, date, type):
        """獲取指定日期的股票數據。"""
        if type == 'tse':
            url = f'https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date={date}&type=ALL'
        else:
            url = f'https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_download.php?l=zh-tw&d={date}&s=0,asc,0'

        for attempt in range(3):  # 最多重試3次
            try:
                response = self.session.get(url, headers=self.headers, timeout=30)
                response.raise_for_status()
                
                if type == 'tse':
                    return self._process_tse_data(response.text)
                else:  # OTC
                    return self._process_otc_data(response.content)
            except Exception as e:
                print(f"嘗試 {attempt + 1} 獲取 {type} {date} 的數據時出錯：{str(e)}")
                if attempt == 2:  # 在最後一次嘗試時打印更多信息
                    print(f"響應內容: {response.text[:500]}...")  # 打印前500個字符
                time.sleep(random.uniform(5, 10))  # 隨機等待5到10秒
        
        return pd.Series(dtype='float64', name=date)  # 如果所有嘗試都失敗，返回空的Series

    def _process_tse_data(self, text):
        lines = text.split('\n')
        header_row = next(i for i, line in enumerate(lines) if '證券代號' in line)
        df = pd.read_csv(io.StringIO('\n'.join(lines[header_row:])), 
                         index_col='證券代號', 
                         usecols=['證券代號', '證券名稱', '收盤價'], 
                         dtype={'證券代號': str, '證券名稱': str, '收盤價': str})
        df['收盤價'] = df['收盤價'].str.replace(',', '').str.replace('--', 'NaN')
        df['收盤價'] = pd.to_numeric(df['收盤價'], errors='coerce')
        return df['收盤價']

    def _process_otc_data(self, content):
        content = content.decode('big5', errors='ignore')
        reader = csv.reader(io.StringIO(content))
        data = list(reader)
        
        header_row = next(i for i, row in enumerate(data) if '代號' in row)
        headers = data[header_row]
        
        code_index = headers.index('代號')
        close_index = headers.index('收盤 ')  # 注意這裡的空格
        
        stock_data = {}
        for row in data[header_row+1:]:
            if len(row) > max(code_index, close_index):
                code = row[code_index].strip('"')
                close = row[close_index].strip('"')
                if code and close:
                    stock_data[code] = close
        
        df = pd.DataFrame.from_dict(stock_data, orient='index', columns=['收盤價'])
        df.index.name = '股票代號'
        df['收盤價'] = pd.to_numeric(df['收盤價'], errors='coerce')
        return df['收盤價']
    
    def fetch_stock_data_range(self):
        """獲取指定日期範圍內的股票數據。"""
        if not all([self.start_date, self.end_date, self.stock_type]):
            raise ValueError("請先設置開始日期、結束日期和股票類型")

        date_range = pd.date_range(start=self.start_date, end=self.end_date, freq='B')  # 'B' 表示工作日

        all_data = []
        for date in tqdm(date_range, desc="處理進度"):
            date_str = date.strftime('%Y%m%d')
            
            if self.stock_type == 'otc':
                date_str = self._convert_to_rocdate(date_str)
            
            daily_data = self.get_stock_data(date_str, self.stock_type)
            if not daily_data.empty:
                daily_data.name = date_str  # 設置 Series 的名稱為日期字符串
                all_data.append(daily_data)
                tqdm.write(f"成功獲取 {date_str} 的數據")
            else:
                tqdm.write(f"{date_str} 沒有數據（可能是假日）")
            time.sleep(random.uniform(3, 7))  # 隨機等待3到7秒

        return all_data  
    
    def store_price(self):
        """將獲取的股票數據存儲到 CSV 文件中。"""
        all_data = self.fetch_stock_data_range()
        
        result_df = pd.concat(all_data, axis=1)
        result_df.columns = [data.name for data in all_data]

        file_name = os.path.join(self.stock_type, f'stock_prices_{self.start_date.strftime("%Y%m%d")}_{self.end_date.strftime("%Y%m%d")}.csv')
        result_df.to_csv(file_name, encoding='utf-8-sig')
        print(f"數據已保存到 {file_name}")

    def add_historical_prices(self, csv_file, add_to='end'):
        """將新的股票數據添加到現有的 CSV 文件中。"""
        # 讀取原有的 CSV 文件
        df = pd.read_csv(csv_file, index_col=0)
        
        # 獲取新的股價數據
        new_data = self.fetch_stock_data_range()
        
        if new_data:
            new_df = pd.concat(new_data, axis=1)
            
            # 根據用戶選擇將新數據添加到頭部或尾部
            if add_to.lower() == 'start':
                combined_df = pd.concat([new_df, df], axis=1)
                print(f"歷史數據已添加到文件頭部")
            else:  # 默認添加到尾部
                combined_df = pd.concat([df, new_df], axis=1)
                print(f"歷史數據已添加到文件尾部")
            
            # 保存合併後的數據
            combined_df.to_csv(csv_file, encoding='utf-8-sig')
            
            print(f"數據已保存到 {csv_file}")
        else:
            print("沒有獲取到新的數據")
    def _convert_to_rocdate(self, date):
        # 將西元年日期轉換為民國年日期
        western_year = int(date[:4])
        roc_year = western_year - 1911
        return f"{roc_year}/{date[4:6]}/{date[6:9]}"
    

if __name__ == "__main__":
    fetcher = StockDataFetcher()
    type = 'tse'
    # 設置日期範圍和股票類型
    start_date = '2024-07-01'
    end_date = '2024-09-05'
    fetcher.set_date_range(start_date, end_date)
    fetcher.set_stock_type(type)
    # 存儲新的價格數據
    fetcher.store_price()
     
    
     