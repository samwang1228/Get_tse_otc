def convert_to_rocdate(date):
        # 將西元年日期轉換為民國年日期
        western_year = int(date[:4])
        roc_year = western_year - 1911
        return f"{roc_year}/{date[4:6]}/{date[6:9]}"
    
print(convert_to_rocdate('20240701'))