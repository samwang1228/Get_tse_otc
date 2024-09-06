import pandas as pd
import numpy as np

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

    # 打印一些調試信息
    print("前五行數據：")
    print(df.head())
    print("\n第一天和最後一天的價格：")
    print(df.iloc[:, [0, -1]].head())

    # 計算漲幅
    gains_5d = (df.iloc[:, min(4, num_days-1)] - df.iloc[:, 0]) / df.iloc[:, 0] if num_days >= 5 else pd.Series(np.nan, index=df.index)
    gains_20d = (df.iloc[:, min(19, num_days-1)] - df.iloc[:, 0]) / df.iloc[:, 0] if num_days >= 20 else pd.Series(np.nan, index=df.index)
    gains_total = (df.iloc[:, -1] - df.iloc[:, 0]) / df.iloc[:, 0]

    # 打印總漲幅的一些統計信息
    print("\n總漲幅統計：")
    print(gains_total.describe())

    # 創建結果DataFrame
    result_df = pd.DataFrame({
        '股票代碼': df.index,
        '5天漲幅': gains_5d.apply(lambda x: f'{x:.2%}' if pd.notnull(x) else 'N/A'),
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
input_file = 'filtered_stock_prices_otc_jul_aug_2024.csv'
output_file = 'stock_gains_5d_20d_total_otc_sorted.csv'
calculate_and_sort_gains(input_file, output_file, sort_period='總')  # 可以改為 '5天' 或 '20天' 或 '總'
