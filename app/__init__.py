from flask import Flask
from app.models import db

def create_app():
    app = Flask(__name__)
    
    # 環境變數配置
    import os
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    
    # 資料庫配置 - 雲端環境強制使用記憶體資料庫
    if os.environ.get('FLASK_ENV') == 'production':
        # 生產環境強制使用記憶體資料庫（忽略 DATABASE_URL）
        database_url = 'sqlite:///:memory:'
        print("🏭 生產環境：強制使用記憶體 SQLite 資料庫")
    else:
        # 開發環境使用檔案資料庫
        database_url = 'sqlite:///instance/shift_schedule.db'
        print("🔧 開發環境：使用檔案 SQLite 資料庫")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 生產環境安全設定
    if os.environ.get('FLASK_ENV') == 'production':
        app.config['SESSION_COOKIE_SECURE'] = True
        app.config['SESSION_COOKIE_HTTPONLY'] = True
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    db.init_app(app)
    
    from app.routes import main
    from app.auth import auth
    app.register_blueprint(main)
    app.register_blueprint(auth)
    
    with app.app_context():
        db.create_all()
        
        # 注意：初始管理員在啟動腳本中創建，避免重複創建
        
        from app.models import ShiftType
        from datetime import time
        if not ShiftType.query.first():
            default_shifts = [
                ShiftType(code='A', name='早班', start_time=time(8, 0), end_time=time(16, 0), color='#28a745'),
                ShiftType(code='B', name='中班', start_time=time(16, 0), end_time=time(0, 0), color='#ffc107'),
                ShiftType(code='C', name='晚班', start_time=time(0, 0), end_time=time(8, 0), color='#dc3545'),
                ShiftType(code='OFF', name='休假', start_time=time(0, 0), end_time=time(0, 0), color='#6c757d')
            ]
            for shift in default_shifts:
                db.session.add(shift)
            db.session.commit()
    
    return app