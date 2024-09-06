import pandas as pd
import numpy as np
import os

def calculate_and_sort_gains(input_file, output_file, sort_period='5天'):
    # 讀取CSV文件
    df = pd.read_csv(input_file, index_col=0)
    
    # 確保日期列是按照時間順序排列的
    df = df.sort_index(axis=1)
    
    # 檢查數據列數
    num_days = df.shape[1]
    print(f"數據包含 {num_days} 天的價格信息")

    # 將所有價格數據轉換為浮點數
    df = df.astype(float)

    # 計算漲幅
    gains_5d = (df.iloc[:, -1] - df.iloc[:, -min(5, num_days)]) / df.iloc[:, -min(5, num_days)] if num_days >= 5 else pd.Series(np.nan, index=df.index)
    gains_10d = (df.iloc[:, -1] - df.iloc[:, -min(10, num_days)]) / df.iloc[:, -min(10, num_days)] if num_days >= 10 else pd.Series(np.nan, index=df.index)
    gains_20d = (df.iloc[:, -1] - df.iloc[:, -min(20, num_days)]) / df.iloc[:, -min(20, num_days)] if num_days >= 20 else pd.Series(np.nan, index=df.index)
    gains_total = (df.iloc[:, -1] - df.iloc[:, 0]) / df.iloc[:, 0]

    # 打印一些調試信息
    print("\n總漲幅統計：")
    print(gains_total.describe())

    # 創建結果DataFrame
    result_df = pd.DataFrame({
        '股票代碼': df.index,
        '5天漲幅': gains_5d.apply(lambda x: f'{x:.2%}' if pd.notnull(x) else 'N/A'),
        '10天漲幅': gains_10d.apply(lambda x: f'{x:.2%}' if pd.notnull(x) else 'N/A'),
        '20天漲幅': gains_20d.apply(lambda x: f'{x:.2%}' if pd.notnull(x) else 'N/A'),
        '總漲幅': gains_total.apply(lambda x: f'{x:.2%}' if pd.notnull(x) else 'N/A')
    })
    
    # 根據指定的天數進行排序
    sort_column = f'{sort_period}漲幅'
    if sort_column in result_df.columns:
        result_df[sort_column] = result_df[sort_column].apply(lambda x: float(x.rstrip('%'))/100 if x != 'N/A' else np.nan)
        result_df = result_df.sort_values(by=sort_column, ascending=False)
        result_df[sort_column] = result_df[sort_column].apply(lambda x: f'{x:.2%}' if pd.notnull(x) else 'N/A')
    else:
        print(f"警告：無法找到 '{sort_column}' 列進行排序。")
    
    # 保存結果到CSV文件
    result_df.to_csv(output_file, encoding='utf-8-sig', index=False)
    
    print(f"漲幅計算和排序完成，結果已保存到 {output_file}")

# 使用示例
if __name__ == "__main__":
    input_file = 'filtered_stock_prices_20240701_20240905.csv'
    otc_file = os.path.join('otc', input_file)
    tse_file = os.path.join('tse', input_file)
    day=5
    output_file = f'stock_gains_5d_10d_20d_{day}_sorted.csv'
    otc_output_file = os.path.join('otc', output_file)
    tse_output_file = os.path.join('tse', output_file)
    calculate_and_sort_gains(otc_file, otc_output_file, sort_period=f'{day}天')  # 可以改為 '5天' 或 '10天' 或 '20天' 或 '總'
    calculate_and_sort_gains(tse_file, tse_output_file, sort_period=f'{day}天')  # 可以改為 '5天' 或 '10天' 或 '20天' 或 '總'
