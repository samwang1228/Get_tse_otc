import pandas as pd

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
input_file = 'stock_prices_jul_aug_2024.csv'
output_file = 'filtered_stock_prices_otc_jul_aug_2024.csv'
filter_four_digit_stocks(input_file, output_file)
