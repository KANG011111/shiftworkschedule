# 班表管理系統

一個使用 Flask 開發的班表管理網站，可以匯入 Excel 班表、顯示日曆檢視、查詢排班資訊。

## 功能特色

### 主要功能
1. **Excel 班表匯入** - 支援 .xlsx/.xls 格式
2. **日曆檢視** - 使用 FullCalendar 顯示班表
3. **今日排班** - 首頁顯示當天所有排班人員
4. **員工管理** - 只顯示有班表記錄的員工
5. **排班查詢** - 查詢指定日期的所有排班
6. **個人班表** - 查看特定員工的完整班表記錄

### 班別設定
- **A班 (早班)**: 08:00-16:00 (綠色)
- **B班 (中班)**: 16:00-00:00 (黃色)
- **C班 (晚班)**: 00:00-08:00 (紅色)
- **OFF (休假)**: 休息日 (灰色)

## 安裝與使用

### 1. 環境設置
```bash
# 建立虛擬環境
python3 -m venv venv

# 啟動虛擬環境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 安裝套件
pip install -r requirements.txt
```

### 2. 運行應用
```bash
python run.py
```

應用將在 http://localhost:5001 啟動

### 3. Excel 格式要求

Excel 檔案需包含以下欄位：
- `姓名` 或 `員工姓名`
- `日期` (YYYY-MM-DD 格式或 Excel 日期)
- `班別` 或 `班次` (A/B/C/OFF)

範例格式：
| 姓名 | 日期 | 班別 |
|------|------|------|
| 張三 | 2024-01-15 | A |
| 李四 | 2024-01-15 | B |
| 王五 | 2024-01-15 | OFF |

### 4. 生成範例資料
```bash
python sample_schedule.py
```
這會建立 `sample_schedule.xlsx` 範例檔案供測試使用。

## 專案結構

```
shiftworkschedule/
├── app/
│   ├── __init__.py          # 應用初始化
│   ├── models.py            # 資料庫模型
│   ├── routes.py            # 路由處理
│   └── templates/           # HTML 模板
│       ├── base.html
│       ├── index.html       # 首頁
│       ├── calendar.html    # 日曆檢視
│       ├── employees.html   # 員工管理
│       ├── employee_schedule.html  # 個人班表
│       ├── query.html       # 排班查詢
│       └── upload.html      # Excel 上傳
├── venv/                    # 虛擬環境
├── run.py                   # 應用入口
├── requirements.txt         # Python 套件清單
├── sample_schedule.py       # 範例資料生成器
└── README.md               # 說明文件
```

## 資料庫設計

### 員工表 (employees)
- id: 主鍵
- name: 姓名
- employee_code: 員工代號
- created_at, updated_at: 時間戳記

### 班別表 (shift_types)
- id: 主鍵
- code: 班別代號 (A/B/C/OFF)
- name: 班別名稱
- start_time, end_time: 班別時間
- color: 顯示顏色

### 班表表 (schedules)
- id: 主鍵
- date: 排班日期
- employee_id: 員工 ID (外鍵)
- shift_type_id: 班別 ID (外鍵)
- created_at, updated_at: 時間戳記

## API 端點

- `GET /` - 首頁，顯示今日排班
- `GET /calendar` - 日曆檢視
- `GET /employees` - 員工列表 (僅顯示有班表的員工)
- `GET /employee/<id>/schedule` - 個人班表詳情
- `GET /query_shift?date=YYYY-MM-DD` - 查詢指定日期排班
- `POST /upload_excel` - 上傳 Excel 班表
- `GET /api/events` - 日曆事件 API (JSON)

## 技術棧

- **後端**: Flask, SQLAlchemy, SQLite
- **前端**: Bootstrap 5, FullCalendar
- **資料處理**: Pandas, OpenPyXL
- **資料庫**: SQLite

## 開發者

這個班表管理系統是為了解決每月 Excel 班表同步和查詢問題而開發的。可以快速查看今日排班、特定日期的同班同事，以及完整的班表日曆檢視。