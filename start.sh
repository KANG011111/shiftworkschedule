#!/bin/bash

# 班表管理系統 - 生產環境啟動腳本

set -e  # 遇到錯誤立即退出

echo "🚀 正在啟動班表管理系統..."

# 檢查並創建資料庫目錄
echo "📂 檢查資料庫目錄..."
mkdir -p /app/instance
chmod 755 /app/instance

# 初始化資料庫
echo "🗄️ 初始化資料庫..."
python -c "
import os
print(f'工作目錄: {os.getcwd()}')
print(f'當前用戶: {os.getuid()}')
print(f'資料庫目錄權限: {oct(os.stat(\"/app/instance\").st_mode)[-3:]}')

from app import create_app
app = create_app()
print(f'資料庫 URI: {app.config[\"SQLALCHEMY_DATABASE_URI\"]}')

with app.app_context():
    from app.models import db
    try:
        db.create_all()
        print('✅ 資料庫初始化完成')
    except Exception as e:
        print(f'❌ 資料庫初始化失敗: {e}')
        raise
"

# 啟動應用程式
echo "🌐 啟動應用程式..."
if [ "$FLASK_ENV" = "production" ]; then
    echo "📦 生產環境模式 - 使用 Gunicorn"
    gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120 --access-logfile - --error-logfile - run:app
else
    echo "🔧 開發環境模式 - 使用 Flask 內建伺服器"
    python run.py
fi