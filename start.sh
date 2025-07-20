#!/bin/bash

# 班表管理系統 - 生產環境啟動腳本

echo "正在啟動班表管理系統..."

# 初始化資料庫
echo "初始化資料庫..."
python -c "
from app import create_app
app = create_app()
with app.app_context():
    from app.models import db
    db.create_all()
    print('資料庫初始化完成')
"

# 啟動應用程式
echo "啟動應用程式..."
if [ "$FLASK_ENV" = "production" ]; then
    echo "生產環境模式 - 使用 Gunicorn"
    gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120 run:app
else
    echo "開發環境模式 - 使用 Flask 內建伺服器"
    python run.py
fi