# 班表管理系統 - Zeabur 部署指南

## 🚀 部署方式選擇

### 推薦：Docker 部署 (最穩定)
```bash
# 1. 確認文件都已準備好
ls Dockerfile docker-compose.yml

# 2. 本地測試 Docker 構建
docker build -t shift-schedule .
docker run -p 5000:5000 shift-schedule
```

### 替代：Git 部署
直接連接 GitHub/GitLab 倉庫進行自動部署

## 📋 部署前準備

### 1. 設定環境變數
在 Zeabur 控制台設定以下環境變數：

```bash
FLASK_ENV=production
SECRET_KEY=your-super-secret-production-key-at-least-32-chars
PORT=5000
DATABASE_URL=sqlite:///instance/shift_schedule.db
```

### 2. 可選：使用 PostgreSQL 資料庫
```bash
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

## 🔧 Zeabur 部署步驟

### Docker 部署步驟：

1. **上傳到 Git 倉庫**
   ```bash
   git add .
   git commit -m "準備 Zeabur 部署"
   git push origin main
   ```

2. **在 Zeabur 建立新專案**
   - 登入 [Zeabur](https://zeabur.com)
   - 點擊 "New Project"
   - 選擇 "Deploy from Git"

3. **連接 Git 倉庫**
   - 選擇你的 GitHub/GitLab 倉庫
   - 選擇 `main` 分支

4. **配置服務**
   - Zeabur 會自動檢測到 `Dockerfile`
   - 設定環境變數（見上方）
   - 點擊 "Deploy"

5. **設定域名**
   - 部署完成後，點擊 "Domain"
   - 添加自定義域名或使用 Zeabur 提供的域名

### Git 部署步驟（替代方案）：

1. **準備 zeabur.json**
   - 已經為你準備好 `zeabur.json` 文件
   - 確認設定正確

2. **其餘步驟與 Docker 部署相同**

## 🔐 安全設定

### 必須更改的預設值：

1. **SECRET_KEY**
   ```bash
   # 生成強密碼
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **管理員密碼**
   - 部署後立即登入 `/login`
   - 使用預設帳號：`admin / admin123`
   - **立即更改密碼！**

3. **HTTPS 設定**
   - Zeabur 自動提供 HTTPS
   - 確認環境變數 `FLASK_ENV=production`

## 📊 資料庫管理

### SQLite (預設)
- 資料存儲在 `/app/instance/shift_schedule.db`
- 自動創建和初始化
- 適合中小型團隊使用

### PostgreSQL (建議大型使用)
1. 在 Zeabur 添加 PostgreSQL 服務
2. 更新 `DATABASE_URL` 環境變數
3. 重新部署

## 🔍 部署後檢查

### 1. 功能測試
- [ ] 訪問首頁是否正常
- [ ] 管理員登入：`admin / admin123`
- [ ] 用戶註冊流程
- [ ] Excel 匯入功能
- [ ] JPG 匯出功能

### 2. 安全檢查
- [ ] 更改管理員預設密碼
- [ ] 確認 HTTPS 已啟用
- [ ] 測試用戶權限隔離

### 3. 效能監控
- [ ] 檢查服務啟動時間
- [ ] 測試並發用戶訪問
- [ ] 監控記憶體使用

## 🐛 常見問題

### 部署失敗
```bash
# 檢查 logs
zeabur logs

# 常見原因：
1. requirements.txt 依賴問題
2. 環境變數未設定
3. 資料庫連接問題
```

### 資料庫問題
```bash
# 重新初始化資料庫
1. 刪除現有資料庫文件
2. 重新部署
3. 系統會自動創建初始管理員帳號
```

### 權限問題
```bash
# 確認文件權限
chmod +x start.sh
```

## 📞 技術支援

如遇到部署問題：
1. 檢查 Zeabur 控制台 logs
2. 確認環境變數設定
3. 驗證 Docker 本地構建
4. 查看此文件的故障排除部分

## 🔄 更新部署

```bash
# 代碼更新流程
git add .
git commit -m "更新功能"
git push origin main

# Zeabur 會自動重新部署
```

---

**重要提醒：**
- ✅ 部署後立即更改管理員密碼
- ✅ 設定強密碼的 SECRET_KEY
- ✅ 定期備份資料庫
- ✅ 監控系統性能和安全性