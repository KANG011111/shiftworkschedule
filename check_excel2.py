import pandas as pd
import numpy as np

excel_file = "11407演出部部門班表.xlsx"

# 檢查第二個工作表 "10407班表"
try:
    df = pd.read_excel(excel_file, sheet_name='10407班表')
    print(f"工作表 '10407班表' 資料形狀: {df.shape}")
    print(f"欄位名稱: {list(df.columns)}")
    print(f"\n前 10 行資料:")
    print(df.head(10))
    
    # 查找包含姓名的欄位
    print("\n尋找可能的姓名欄位...")
    for col in df.columns:
        sample_values = df[col].dropna().head(5).tolist()
        if any(isinstance(val, str) and len(val) >= 2 and len(val) <= 5 for val in sample_values):
            print(f"欄位 '{col}' 可能包含姓名: {sample_values}")
    
    # 檢查是否有日期相關的資料
    print("\n檢查日期資料...")
    for i, row in df.iterrows():
        if i > 20:  # 只檢查前20行
            break
        non_null_values = [val for val in row if pd.notna(val)]
        if non_null_values:
            print(f"第{i}行: {non_null_values[:10]}")  # 只顯示前10個非空值
            
except Exception as e:
    print(f"讀取錯誤: {e}")

# 也檢查第一個工作表的詳細結構
try:
    print("\n" + "="*50)
    print("檢查第一個工作表...")
    df1 = pd.read_excel(excel_file, sheet_name=0)
    
    # 找出有意義的行
    for i, row in df1.iterrows():
        if i > 50:  # 只檢查前50行
            break
        non_null_values = [val for val in row if pd.notna(val)]
        if len(non_null_values) > 3:  # 如果這行有超過3個非空值
            print(f"第{i}行: {non_null_values}")
            
except Exception as e:
    print(f"讀取錯誤: {e}")