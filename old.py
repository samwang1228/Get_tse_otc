import requests
import pandas as pd
from datetime import datetime, timedelta
import io
import time
import random
from tqdm import tqdm
import csv

def get_stock_data(date, session, type):
    if type == 'tse':
        url = f'https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date={date}&type=ALL'
    else:
        url = f'https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_download.php?l=zh-tw&d={date}&s=0,asc,0'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for attempt in range(3):  # 最多重試3次
        try:
            response = session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            if type == 'tse':
                lines = response.text.split('\n')
                header_row = next(i for i, line in enumerate(lines) if '證券代號' in line)
                df = pd.read_csv(io.StringIO('\n'.join(lines[header_row:])), 
                                 index_col='證券代號', 
                                 usecols=['證券代號', '證券名稱', '收盤價'], 
                                 dtype={'證券代號': str, '證券名稱': str, '收盤價': str})
                df['收盤價'] = df['收盤價'].str.replace(',', '').str.replace('--', 'NaN')
            else:  # OTC
                content = response.content.decode('big5', errors='ignore')
                reader = csv.reader(io.StringIO(content))
                data = list(reader)
                
                # 找到包含列名的行
                header_row = next(i for i, row in enumerate(data) if '代號' in row)
                headers = data[header_row]
                
                # 找到 '代號' 和 '收盤' 列的索引
                code_index = headers.index('代號')
                close_index = headers.index('收盤 ')  # 注意這裡的空格
                
                # 創建一個字典來存儲數據
                stock_data = {}
                for row in data[header_row+1:]:
                    if len(row) > max(code_index, close_index):
                        code = row[code_index].strip('"')
                        close = row[close_index].strip('"')
                        if code and close:
                            stock_data[code] = close
                
                df = pd.DataFrame.from_dict(stock_data, orient='index', columns=['收盤價'])
            
            df['收盤價'] = pd.to_numeric(df['收盤價'], errors='coerce')
            return df['收盤價']
        except Exception as e:
            print(f"嘗試 {attempt + 1} 獲取 {type} {date} 的數據時出錯：{str(e)}")
            if attempt == 2:  # 在最後一次嘗試時打印更多信息
                print(f"響應內容: {response.text[:500]}...")  # 打印前500個字符
            time.sleep(random.uniform(5, 10))  # 隨機等待5到10秒
    
    return pd.Series(dtype='float64', name=date)  # 如果所有嘗試都失敗，返回空的Series

def add_historical_prices(csv_file, start_date, end_date, add_to='end'):
    # 添加指定日期到原有的 CSV 文件
    df = pd.read_csv(csv_file, index_col=0)
    
    # 生成日期範圍
    date_range = pd.date_range(start=start_date, end=end_date, freq='B')  # 'B' 表示工作日
    
    # 獲取新的股價數據
    new_data = []
    with requests.Session() as session:
        for date in tqdm(date_range, desc="獲取歷史數據"):
            date_str = date.strftime('%Y%m%d')
            daily_data = get_stock_data(date_str, session,'otc')
            if not daily_data.empty:
                daily_data.name = date_str  # 設置 Series 的名稱為日期字符串
                new_data.append(daily_data)
                tqdm.write(f"成功獲取 {date_str} 的數據")
            else:
                tqdm.write(f"{date_str} 沒有數據（可能是非交易日）")
            time.sleep(random.uniform(3, 7))  # 隨機等待3到7秒
    
    # 將新數據合併成一個 DataFrame
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
def get_otc_stock_data(date, session):
    url = f'https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_download.php?l=zh-tw&d={date}&s=0,asc,0'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for attempt in range(3):  # 最多重試3次
        try:
            response = session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            df = pd.read_csv(io.StringIO(response.text), 
                             index_col='代號', 
                             usecols=['代號', '名稱', '收盤'], 
                             dtype={'代號': str, '名稱': str, '收盤': str})
            df['收盤'] = pd.to_numeric(df['收盤'], errors='coerce')
            return df['收���']
        except Exception as e:
            print(f"嘗試 {attempt + 1} 獲取上櫃股票 {date} 的數據時出錯：{str(e)}")
            time.sleep(random.uniform(5, 10))  # 隨機等待5到10秒
    
    return pd.Series(name=date)  # 如果所有嘗試都失敗，返回空的Series

def store_price(start_date, end_date,type,file_name):
    # otc 上櫃
    # tse 上市
    # 下載指定區間的股價
    # 生成日期範圍（2024年7月1日到8月31日，只包括工作日）
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    print(start_date,end_date)
    date_range = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5:  # 0-4 代表週一到週五
            date_range.append(current_date)
        current_date += timedelta(days=1)

    # 獲取所有交易日的數據
    all_data = []
    with requests.Session() as session:
        for date in tqdm(date_range, desc="處理進度"):
            date_str = date.strftime('%Y%m%d')
            if type == 'tse':
                daily_data = get_stock_data(date_str, session,'tse')
            else:
                daily_data = get_stock_data(date_str, session,'otc')
            if not daily_data.empty:
                all_data.append(daily_data)
                tqdm.write(f"成功獲取 {date_str} 的數據")
            else:
                tqdm.write(f"{date_str} 沒有數據（可能是假日）")
            time.sleep(random.uniform(3, 7))  # 隨機等待3到7秒

    # 將所有數據合併成一個 DataFrame
    result_df = pd.concat(all_data, axis=1)
    result_df.columns = [data.name for data in all_data]

    # 將結果保存為 CSV 文件
    result_df.to_csv('stock_prices_jul_aug_2024.csv', encoding='utf-8-sig')

    print("數據已保存到 stock_prices_jul_aug_2024.csv")

if __name__ == "__main__":
    csv_file = 'stock_prices_otc_jul_aug_2024.csv'
    start_date = '2024-07-01'  # 指定開始日期
    end_date = '2024-09-05'    # 指定結束日期
    
    # 讓用戶選擇添加位置
    '''
    add_position = input("請選擇將新數據添加到文件的位置 ('start' 為頭部，'end' 為尾部，默認為尾部): ").strip().lower()
    if add_position not in ['start', 'end']:
        add_position = 'end'
    
    add_historical_prices(csv_file, start_date, end_date, add_to=add_position)
    '''
    store_price(start_date, end_date,'otc',csv_file)