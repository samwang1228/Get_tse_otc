import pandas as pd
import os
from pathlib import Path
def filter_four_digit_stocks(input_file, output_file):
    # 讀取 CSV 文件
    df = pd.read_csv(input_file, index_col=0)
    
    # 過濾出索引（股票代碼）為四個字元的行
    filtered_df = df[df.index.str.len() == 4]
    
    # 保存過濾後的數據到新的 CSV 文件
    filtered_df.to_csv(output_file, encoding='utf-8-sig')
    
    print(f"處理完成。原始文件有 {len(df)} 個股票，過濾後有 {len(filtered_df)} 個股票。")
    print(f"結果已保存到 {output_file}")
 
# 使用示例
 

if __name__ == "__main__":
    input_file = 'stock_prices_20240701_20240905.csv'
    otc_file = os.path.join('otc', input_file)
    tse_file = os.path.join('tse', input_file)
    otc_output_file = os.path.join('otc', f'filtered_{input_file}')
    tse_output_file = os.path.join('tse', f'filtered_{input_file}')
    filter_four_digit_stocks(otc_file, otc_output_file)
    filter_four_digit_stocks(tse_file, tse_output_file)
