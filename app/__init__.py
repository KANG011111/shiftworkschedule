from flask import Flask
from app.models import db

def create_app():
    app = Flask(__name__)
    
    # 環境變數配置
    import os
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///instance/shift_schedule.db')
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
        
        # 創建初始管理員帳號
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
            print('初始管理員帳號已創建: admin / admin123')
        
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