# 班表管理系統

一個使用 Flask 開發的班表管理網站，可以匯入 CSV 班表、顯示日曆檢視、查詢排班資訊，並支援貼上 Excel 班表資料進行即時預覽與匯入。

## 功能特色

### 主要功能

1. **CSV 班表匯入** - 支援 .csv 檔案或貼上資料匯入
2. **日曆檢視** - 使用 FullCalendar 顯示月班表
3. **今日排班** - 首頁快速查看當天所有排班人員
4. **員工管理** - 僅顯示有班表記錄的員工
5. **排班查詢** - 可查詢特定日期的排班資訊
6. **個人班表** - 查看特定員工的完整班表紀錄
7. **JPG匯出** - 一鍵匯出月度個人班表為JPG圖片 (2025.09.08 新增)
8. **ICS日曆匯出** - 匯出為標準日曆格式，可導入Google日曆、Outlook等

### 班別設定

系統內建以下常用班別代碼，匯入 CSV 或貼上資料時會自動識別：

```
C1, C2, C3, CH/FC, CH/FC*, E1, FC, FC/E1, FC/PM, FX,
H0, H1, N1, N1/E1, N2, NT/FC,
P1c, P1c/P3p, P1n, P1n/LED, P1p, P1p/Crew, P1p/LED, P1p/ME, P1p/PM,
P1s, P1s/Crew, P1s/PM,
P2c, P2n, P2p, P2p/Crew, P2p/LD, P2s, P2s/Crew, P2s/LD,
P3c, P3n, P3p,
P4n, P4p,
P5, P5/lobby
```

若匯入班表時遇到系統未定義的班別代碼，系統會列為「待補登」狀態，
管理者可進入「新增班別」介面補上代號、時間、名稱與顏色，新增後立即可用。

自訂班別支援任意字串代碼，例如：「休假日班」、「支援A區」、「技術排班」等，供不同部門彈性使用。

* **預設班別**：

  * A班（早班）
  * B班（中班）
  * C班（晚班）
  * OFF（休假）
* **支援自訂班別**：管理者可手動新增班別代碼（如 D 班、外勤、特休等），可設定：班別代碼、名稱、時間、顏色。

## 匯入班表格式規範（支援 CSV 與 Excel 貼上）

### 班表預覽與管理功能（匯入前）

* 系統在上傳或貼上資料後，會即時分析班表的「年月分佈」

  * 例如：7 月、8 月、或跨月班表（7～9 月）
* 管理者可在預覽介面中：

  * 查看即將匯入的月份範圍與筆數
  * 勾選特定月份進行「刪除」、「修改」或「更換檔案」
  * 若內容錯誤，可直接取消匯入或重新貼上/上傳

系統支援兩種方式匯入班表資料：

### 方法一：上傳直式 CSV 檔案

* 檔案格式：`.csv`（UTF-8 編碼）
* 必須包含以下欄位（順序不限）：

| 姓名 | 員工代碼 | 年月      | 日期 | 班別 |
| -- | ---- | ------- | -- | -- |
| 張三 | A001 | 2024-07 | 1  | A  |

* 系統會自動將「年月」與「日期」組合為完整日期（如 `2024-07-01`）
* 未知班別代碼會提示需補登
* 空白班別視為未排班

### 方法二：貼上班表資料（前端輸入區）

* 可從 Excel 或 Google Sheet 複製貼上資料
* 需為 CSV 結構（逗號分隔，直式格式），例如：

```
姓名,員工代碼,年月,日期,班別
張三,A001,2024-07,1,A
張三,A001,2024-07,2,B
張三,A001,2024-07,3,OFF
```

* 貼上後會即時預覽轉成表格
* 若資料有誤（格式錯誤、缺漏、班別未定義）會即時提示
* 可點選送出進行匯入

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

### 2. 執行應用

```bash
python run.py
```

應用將在 [http://localhost:5001](http://localhost:5001) 啟動

### 3. 生成範例資料

```bash
python sample_schedule.py
```

這會建立 `sample_schedule.csv` 範例檔案供測試使用。

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
│       └── upload.html      # 匯入區（上傳/貼上）
├── venv/                    # 虛擬環境
├── run.py                   # 應用入口
├── requirements.txt         # Python 套件清單
├── sample_schedule.py       # 範例資料生成器
└── README.md               # 說明文件
```

## 資料庫設計

### 員工表 (employees)

* id: 主鍵
* name: 姓名
* employee\_code: 员工代號
* created\_at, updated\_at: 時間戳記

### 班別表 (shift\_types)

* id: 主鍵
* code: 班別代號 (如 A/B/C/OFF)
* name: 班別名稱
* start\_time, end\_time: 班別時間
* color: 顯示顏色

### 班表表 (schedules)

* id: 主鍵
* date: 排班日期
* employee\_id: 員工 ID (外鍵)
* shift\_type\_id: 班別 ID (外鍵)
* created\_at, updated\_at: 時間戳記

## API 端點

* `GET /` - 首頁，顯示今日排班
* `GET /calendar` - 日曆檢視
* `GET /employees` - 員工列表（僅顯示有排班紀錄者）
* `GET /employee/<id>/schedule` - 個人班表詳情
* `GET /query_shift?date=YYYY-MM-DD` - 查詢指定日期排班
* `POST /upload_csv` - 上傳 CSV 班表
* `POST /upload_pasted` - 匯入貼上資料
* `GET /api/events` - 日曆事件 API（FullCalendar 用）

## 技術棧

* **後端**: Flask, SQLAlchemy, SQLite
* **前端**: Bootstrap 5, FullCalendar, JavaScript
* **資料處理**: Pandas, Python CSV 解析
* **資料庫**: SQLite（可擴充為其他）

## Docker 部署

系統已容器化，可使用 Docker 快速部署：

```bash
# 啟動系統
docker-compose up -d

# 查看狀態
docker-compose ps

# 查看日誌
docker-compose logs -f

# 停止系統
docker-compose down

# 重建並啟動
docker-compose build && docker-compose up -d
```

**系統訪問：** http://localhost:5001/  
**管理員帳號：** admin / admin123

## 最新更新 (2025.09.08)

### JPG匯出星期對齊修正

**問題：** JPG班表匯出時，日期與星期對齊不正確，例如9月1日(星期一)錯誤顯示在星期日欄位。

**解決方案：**
- 實現傳統日曆格式（星期日開始）
- 修正後端 `calendar.monthcalendar()` 使用 `calendar.SUNDAY` 模式
- 調整前端 weekdays 陣列順序為 `['日', '一', '二', '三', '四', '五', '六']`

**修正效果：**
- ✅ 9月1日(星期一)現在正確顯示在星期一欄位，星期日欄位空白
- ✅ 完全支援2025-2027年跨年使用
- ✅ 所有月份的星期對齊都正確

**測試驗證：**
- 測試員工：李惟綱(8312)、賴秉宏(8652)等
- 測試月份：2025年9月(含321筆實際排班記錄)
- 跨年測試：2026、2027年各月份

## 開發者說明

這套班表系統設計給管理者快速處理來自 Excel 或口頭交辦的班表，解決傳統 Excel 共用、無法即時查詢、格式難統一的問題。

支援直接複製貼上、上傳檔案、自訂班別代碼、JPG圖片匯出等功能，讓團隊能夠快速完成每月班表資料匯入、查詢與分享。

### 核心特色
- 🐳 **Docker 容器化** - 一鍵部署，環境一致
- 📊 **智能匯入** - 自動識別 Excel/CSV 格式
- 📅 **多格式匯出** - JPG圖片 + ICS日曆
- 🌍 **跨年支援** - 長期使用無憂
- 📱 **響應式設計** - 桌面/手機都好用