import pandas as pd
import sys

# 檢查 Excel 檔案結構
excel_file = "11407演出部部門班表.xlsx"

try:
    # 讀取 Excel 檔案
    xl = pd.ExcelFile(excel_file)
    print(f"工作表列表: {xl.sheet_names}")
    
    # 讀取第一個工作表
    df = pd.read_excel(excel_file, sheet_name=0)
    
    print(f"\n資料形狀: {df.shape}")
    print(f"欄位名稱: {list(df.columns)}")
    print(f"\n前 5 行資料:")
    print(df.head())
    
    print(f"\n資料型態:")
    print(df.dtypes)
    
    # 檢查是否有空值
    print(f"\n空值統計:")
    print(df.isnull().sum())
    
except Exception as e:
    print(f"讀取錯誤: {e}")