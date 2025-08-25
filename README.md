# 班表管理系統

一個使用 Flask 開發的企業級班表管理網站，支援CSV班表匯入、日曆檢視、排班查詢，以及ICS日曆匯出與Excel預覽功能。系統具備完整的使用者權限管理和群組管理功能。

## 功能特色

### 🚀 核心功能

1. **CSV 班表匯入** - 支援多種格式的.csv檔案或貼上資料匯入
2. **日曆檢視** - 使用 FullCalendar 顯示月班表，支援個人和群組檢視
3. **今日排班** - 首頁快速查看當天所有排班人員
4. **員工管理** - 完整的員工資料管理和群組分類
5. **排班查詢** - 可查詢特定日期的排班資訊
6. **個人班表** - 查看特定員工的完整班表紀錄

### 📅 匯出功能

7. **ICS日曆匯出** - 匯出個人班表為.ics檔案，可直接匯入Google Calendar、Outlook等日曆應用
8. **Excel預覽匯出** - 產生月曆式Excel預覽檔，含班別圖例和顏色區分
9. **班表統計報表** - 自動產生班別統計和工時分析

### 👥 權限管理

10. **使用者註冊與登入** - 完整的帳戶管理系統
11. **角色權限控制** - 支援admin、user等不同權限等級
12. **群組管理** - 支援演出人員、技術人員、燈光組等群組分類

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

## 🔄 匯出功能詳細說明

### ICS日曆匯出

系統支援將個人班表匯出為標準ICS日曆格式，可直接匯入各種日曆應用：

1. **支援的日曆應用**：
   - Google Calendar
   - Microsoft Outlook
   - Apple Calendar
   - 其他支援ICS格式的日曆軟體

2. **匯出特色**：
   - 符合Google Calendar匯入規範
   - 包含所有班別類型（含H0、H1休假日）
   - 事件標題顯示班別代碼（如：FC、P1c、H0）
   - 統一設定為09:00-09:05時段以避免匯入問題

3. **使用方式**：
   - 進入「班表匯出」頁面
   - 輸入員工姓名，選擇年月
   - 點擊「匯出ICS日曆」
   - 下載.ics檔案後匯入至個人日曆

### Excel預覽匯出

產生美觀的月曆式Excel檔案，方便列印或分享：

1. **預覽特色**：
   - 月曆格式顯示，直觀易讀
   - 班別顏色區分，視覺化呈現
   - 簡化圖例格式：「FC: FC」、「FX: FX」等
   - 每個班別配有專屬背景顏色

2. **圖例系統**：
   - FC班：藍色背景
   - P1系列：綠色背景
   - P3系列：橙色背景
   - P4系列：紅色背景
   - H0/H1休假：灰色背景

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

### 🏠 主要頁面
* `GET /` - 首頁，顯示今日排班
* `GET /calendar` - 日曆檢視
* `GET /employees` - 員工列表（僅顯示有排班紀錄者）
* `GET /employee/<id>/schedule` - 個人班表詳情
* `GET /query_shift?date=YYYY-MM-DD` - 查詢指定日期排班
* `GET /export_schedule` - 班表匯出頁面

### 📤 匯入功能
* `POST /upload_csv` - 上傳 CSV 班表
* `POST /upload_pasted` - 匯入貼上資料
* `POST /upload_new` - 新版匯入介面
* `POST /confirm_import` - 確認匯入資料

### 📅 匯出功能
* `GET /api/export_ics?query=<員工姓名>&year=<年>&month=<月>` - 匯出個人ICS日曆檔
* `GET /api/export_monthly_schedule?query=<員工姓名>&year=<年>&month=<月>` - 匯出Excel月曆預覽
* `GET /api/preview_schedule?query=<員工姓名>&year=<年>&month=<月>` - 預覽個人班表

### 🔧 系統API
* `GET /api/events` - 日曆事件 API（FullCalendar 用）
* `GET /api/employee-groups` - 取得員工群組資料
* `GET /api/date_range` - 取得資料庫中的日期範圍
* `GET /api/shift_types` - 取得所有班別類型

### 👤 使用者管理
* `GET /login` - 登入頁面
* `GET /register` - 註冊頁面
* `POST /api/auth/login` - 登入API
* `POST /api/auth/logout` - 登出API
* `GET /api/auth/status` - 檢查登入狀態

## 技術棧

* **後端**: Flask, SQLAlchemy, SQLite, Flask-Login
* **前端**: Bootstrap 5, FullCalendar, JavaScript, jQuery
* **資料處理**: Pandas, Python CSV 解析
* **匯出功能**: OpenPyXL (Excel), ICS格式生成
* **資料庫**: SQLite（可擴充為PostgreSQL、MySQL等）
* **部署**: Docker, Gunicorn, Zeabur雲平台支援

## 🔄 版本更新日誌

### v1.3 (最新版)
- ✅ 新增ICS日曆匯出功能，支援Google Calendar匯入
- ✅ 新增Excel月曆預覽匯出功能
- ✅ 優化圖例顯示格式，改為簡化版「FC: FC」樣式
- ✅ 修正H0、H1休假班別在ICS中的顯示問題
- ✅ 增強資料安全性，改善錯誤處理機制
- ✅ 支援Docker容器化部署
- 🔒 加強敏感資料保護，更新.gitignore規則

### v1.2
- 新增使用者權限管理系統
- 新增群組管理功能
- 改善匯入資料驗證邏輯
- 優化前端使用者介面

### v1.1
- 支援多種CSV格式匯入
- 新增班表預覽功能
- 改善日曆顯示效果

## 開發者說明

這套班表系統設計給管理者快速處理來自 Excel 或口頭交辦的班表，解決傳統 Excel 共用、無法即時查詢、格式難統一的問題。

支援直接複製貼上、上傳檔案、自訂班別代碼，讓團隊能夠快速完成每月班表資料匯入與查詢。新版本更加入ICS日曆匯出和Excel預覽功能，讓員工可以輕鬆將個人班表同步到手機或電腦的日曆應用中。

## 🤝 貢獻

歡迎提交Issue或Pull Request來改善這個專案。在提交前請確保：

1. 程式碼符合Python PEP8規範
2. 新功能包含適當的測試
3. 更新相關的文件說明
4. 不包含敏感的個人資料

## 📄 授權

本專案採用 MIT License 授權。