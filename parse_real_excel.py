import pandas as pd
from datetime import datetime, date, time
import sys
import os

def parse_excel_schedule(excel_file):
    """解析真實的班表 Excel 檔案"""
    
    # 使用第二個工作表 "10407班表"
    df = pd.read_excel(excel_file, sheet_name='10407班表')
    
    schedule_data = []
    
    # 找到標題行 (包含 "年月", "組室別", "員工代碼", "姓名")
    header_row = None
    for i, row in df.iterrows():
        if '年月' in str(row.iloc[0]) and '姓名' in str(row.iloc[3]):
            header_row = i
            break
    
    if header_row is None:
        print("找不到標題行")
        return []
    
    print(f"找到標題行在第 {header_row} 行")
    
    # 獲取日期列的索引 (從第5列開始是日期)
    date_columns = []
    for col_idx in range(4, len(df.columns)):  # 從第5列開始
        col_value = df.iloc[header_row, col_idx]
        if pd.notna(col_value) and str(col_value).isdigit():
            date_columns.append((col_idx, int(col_value)))
    
    print(f"找到日期欄位: {date_columns[:10]}...")  # 只顯示前10個
    
    # 解析每個員工的班表
    for i in range(header_row + 1, len(df)):
        row = df.iloc[i]
        
        # 檢查是否為員工資料行
        year_month = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
        employee_name = str(row.iloc[3]) if pd.notna(row.iloc[3]) else ""
        
        if not year_month.startswith('114/') or not employee_name or '異動後' in employee_name:
            continue
            
        # 清理員工姓名 (移除空格)
        employee_name = employee_name.replace(' ', '')
        
        print(f"處理員工: {employee_name}")
        
        # 解析每一天的班別
        for col_idx, day in date_columns:
            if col_idx < len(row):
                shift_code = str(row.iloc[col_idx]) if pd.notna(row.iloc[col_idx]) else ""
                
                if shift_code and shift_code != 'nan':
                    # 建立日期 (假設是2024年7月)
                    try:
                        schedule_date = date(2024, 7, day)
                        
                        # 清理班別代碼
                        shift_code = shift_code.split('/')[0]  # 移除 /後面的內容
                        shift_code = shift_code.split('\n')[0]  # 移除換行後的內容
                        
                        schedule_data.append({
                            '姓名': employee_name,
                            '日期': schedule_date.strftime('%Y-%m-%d'),
                            '班別': shift_code
                        })
                    except ValueError:
                        continue
    
    return schedule_data

if __name__ == "__main__":
    excel_file = "11407演出部部門班表.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"檔案不存在: {excel_file}")
        sys.exit(1)
    
    schedule_data = parse_excel_schedule(excel_file)
    
    print(f"\n成功解析 {len(schedule_data)} 筆班表記錄")
    
    if schedule_data:
        # 顯示前10筆資料
        print("\n前10筆資料:")
        for i, record in enumerate(schedule_data[:10]):
            print(f"{i+1}. {record}")
        
        # 統計班別
        shift_counts = {}
        for record in schedule_data:
            shift = record['班別']
            shift_counts[shift] = shift_counts.get(shift, 0) + 1
        
        print(f"\n班別統計:")
        for shift, count in sorted(shift_counts.items()):
            print(f"  {shift}: {count} 次")
        
        # 儲存為新的 Excel 檔案
        df_output = pd.DataFrame(schedule_data)
        output_file = "parsed_schedule.xlsx"
        df_output.to_excel(output_file, index=False)
        print(f"\n已儲存解析結果至: {output_file}")
    else:
        print("沒有找到任何班表資料")