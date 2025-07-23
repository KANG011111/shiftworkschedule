#!/bin/bash

# 班表管理系統 - 生產環境啟動腳本

set -e  # 遇到錯誤立即退出

echo "🚀 正在啟動班表管理系統 v2..."

# 創建必要目錄
mkdir -p instance

# 顯示環境信息
echo "🗄️ 環境信息..."
echo "🔧 工作目錄: $(pwd)"
echo "👤 當前用戶 UID: $(id -u)"
echo "🌍 FLASK_ENV: $FLASK_ENV"

# 啟動應用程式
echo "🌐 啟動應用程式..."
echo "🔍 FLASK_ENV 值檢查: '$FLASK_ENV'"
if [ "$FLASK_ENV" = "production" ] || [ "$FLASK_ENV" = "FLASK_ENV=production" ]; then
    echo "📦 生產環境模式 - 使用 Gunicorn"
    echo "🔍 調試所有環境變數:"
    env | grep -i port || echo "❌ 沒有找到任何 PORT 相關環境變數"
    
    # 使用環境變數 PORT 或預設 8080
    DEPLOY_PORT=${PORT:-8080}
    echo "🐳 使用端口: $DEPLOY_PORT (來源: ${PORT:+環境變數}${PORT:-預設值})"
    
    echo "🔌 最終使用 Port: $DEPLOY_PORT"
    # 記憶體資料庫使用單worker確保數據一致性，但優化其他參數提升性能
    gunicorn --bind 0.0.0.0:$DEPLOY_PORT --workers 1 --timeout 120 --max-requests 1000 --access-logfile - --error-logfile - run:app
else
    echo "🔧 開發環境模式 - 使用 Flask 內建伺服器"
    python run.py
fi