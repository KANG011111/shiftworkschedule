import pandas as pd
from datetime import datetime, timedelta

# 建立範例班表數據
data = []
employees = ['張三', '李四', '王五', '趙六', '錢七']
shifts = ['A', 'B', 'C', 'OFF']

# 生成一個月的班表
start_date = datetime(2024, 1, 1)
for i in range(31):  # 一月份
    current_date = start_date + timedelta(days=i)
    for j, employee in enumerate(employees):
        # 簡單的排班邏輯
        shift_index = (i + j) % len(shifts)
        shift = shifts[shift_index]
        
        data.append({
            '姓名': employee,
            '日期': current_date.strftime('%Y-%m-%d'),
            '班別': shift
        })

# 建立 DataFrame 並儲存為 Excel
df = pd.DataFrame(data)
df.to_excel('sample_schedule.xlsx', index=False, sheet_name='班表')

print("範例班表檔案 'sample_schedule.xlsx' 已建立")
print(f"包含 {len(data)} 筆記錄")
print("\n前 10 筆資料:")
print(df.head(10))