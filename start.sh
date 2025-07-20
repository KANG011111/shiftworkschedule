#!/bin/bash

# 班表管理系統 - 生產環境啟動腳本

set -e  # 遇到錯誤立即退出

echo "🚀 正在啟動班表管理系統..."

# 創建必要目錄
mkdir -p instance

# 初始化資料庫
echo "🗄️ 初始化資料庫..."
python -c "
import os
print(f'🔧 工作目錄: {os.getcwd()}')
print(f'👤 當前用戶 UID: {os.getuid()}')
print(f'🌍 FLASK_ENV: {os.environ.get(\"FLASK_ENV\", \"未設定\")}')

from app import create_app
app = create_app()
print(f'🗄️ 資料庫 URI: {app.config[\"SQLALCHEMY_DATABASE_URI\"]}')

with app.app_context():
    from app.models import db
    try:
        # 創建所有表
        db.create_all()
        print('✅ 資料庫表創建完成')
        
        # 創建預設管理員（如果不存在）
        from app.models import User
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                name='系統管理員',
                role='admin',
                status='approved'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print('👑 初始管理員帳號已創建: admin / admin123')
        else:
            print('👑 管理員帳號已存在')
            
        print('🎉 資料庫初始化完全完成!')
        
    except Exception as e:
        print(f'❌ 資料庫初始化失敗: {e}')
        import traceback
        traceback.print_exc()
        raise
"

# 啟動應用程式
echo "🌐 啟動應用程式..."
if [ "$FLASK_ENV" = "production" ]; then
    echo "📦 生產環境模式 - 使用 Gunicorn"
    # Zeabur 通常使用 $PORT 環境變數，預設 8080
    DEPLOY_PORT=${PORT:-8080}
    echo "🔌 使用 Port: $DEPLOY_PORT"
    gunicorn --bind 0.0.0.0:$DEPLOY_PORT --workers 2 --timeout 120 --access-logfile - --error-logfile - run:app
else
    echo "🔧 開發環境模式 - 使用 Flask 內建伺服器"
    python run.py
fi