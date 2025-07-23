# 安全配置說明

## ⚠️ 生產環境重要安全提醒

### 1. 修改預設密碼
- **預設管理員帳號**: `admin`  
- **預設密碼**: `admin123`
- **⚠️ 請務必在生產環境中修改預設密碼**

### 2. 環境變數配置
在生產環境中設置以下環境變數：

```bash
# 設置安全的密鑰
export SECRET_KEY="your-very-secure-random-secret-key-here"

# 設置生產環境
export FLASK_ENV="production"
```

### 3. 資料庫安全
- 目前使用記憶體SQLite資料庫，重啟後數據會丟失
- 生產環境建議使用持久化數據庫（PostgreSQL/MySQL）
- 定期備份重要數據

### 4. Docker安全
- 確保Docker容器運行在安全的網絡環境中
- 考慮使用HTTPS證書
- 限制容器的資源使用

### 5. 用戶管理
- 定期檢查待審核用戶
- 及時處理不當的註冊申請
- 監控系統使用情況

## 🔒 建議的生產環境配置

### docker-compose.production.yml
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "80:5000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
    restart: unless-stopped
```

### 啟動命令
```bash
# 設置環境變數
export SECRET_KEY="$(openssl rand -base64 32)"
docker-compose -f docker-compose.production.yml up -d
```