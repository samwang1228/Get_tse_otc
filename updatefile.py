from pathlib import Path
import os
from filter import filter_four_digit_stocks
from caculate import calculate_and_sort_gains
def read_date(file_name):
    try:
        with open(file_name, 'r') as f:
            return f.readline().strip()
    except FileNotFoundError:
        print(f"錯誤：找不到文件 {file_name}")
        return None

def update_date(old_date, new_date,day):
    base_name = 'stock_prices_20240701'
    for market in ['otc', 'tse']:
        input_file = Path(f'{market}/{base_name}_{new_date}.csv')
        old_file = Path(f'{market}/filtered_{base_name}_{old_date}.csv')
        new_file = Path(f'{market}/filtered_{base_name}_{new_date}.csv')
        rate_file=Path(f'{market}/stock_gains_5d_10d_20d_{day}_sorted.csv')
        try:
            if old_file.exists():
                old_file.rename(new_file)
                print(f"已重命名：{old_file} -> {new_file}")
            else:
                print(f"警告：舊文件 {old_file} 不存在，將直接處理新文件")
            
            if input_file.exists():
                filter_four_digit_stocks(str(input_file), str(new_file))
                calculate_and_sort_gains(new_file, rate_file, sort_period=f'{day}天')  # 可以改為 '5天' 或 '10天' 或 '20天' 或 '總'
                print(f"已過濾：{input_file} -> {new_file}")
            else:
                print(f"錯誤：輸入文件 {input_file} 不存在")
        except Exception as e:
            print(f"處理 {market} 市場文件時發生錯誤：{str(e)}")

 

if __name__ == "__main__":
    new_date = read_date('date.txt')
    old_date = read_date('olddate.txt')
    day=5
    if new_date and old_date:
        update_date(old_date, new_date,day)
    else:
        print("無法讀取日期，請檢查 date.txt 和 olddate.txt 文件")
        
        
    