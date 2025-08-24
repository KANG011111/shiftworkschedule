from flask import Flask
from app.models import db

def create_app():
    app = Flask(__name__)
    
    # 環境變數配置
    import os
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    
    # 資料庫配置 
    database_url = os.environ.get('DATABASE_URL')
    flask_env = os.environ.get('FLASK_ENV', '')
    
    print(f"🔍 FLASK_ENV 值: '{flask_env}'")
    print(f"🔍 當前工作目錄: {os.getcwd()}")
    print(f"🔍 工作目錄可寫: {os.access(os.getcwd(), os.W_OK)}")
    
    if database_url:
        print(f"🔗 使用環境變數資料庫: {database_url}")
    elif flask_env == 'production':
        # 只有明確設定為 production 時才使用記憶體資料庫
        database_url = 'sqlite:///:memory:'
        print("🏭 生產環境：使用記憶體 SQLite 資料庫")
    elif not os.access(os.getcwd(), os.W_OK):
        # 無寫入權限時使用記憶體資料庫
        database_url = 'sqlite:///:memory:'
        print("🔒 無寫入權限：使用記憶體 SQLite 資料庫")
    else:
        # 預設使用檔案資料庫（開發環境和本地測試）
        # 確保instance目錄存在
        instance_dir = os.path.join(os.getcwd(), 'instance')
        if not os.path.exists(instance_dir):
            os.makedirs(instance_dir)
            print(f"📁 創建instance目錄: {instance_dir}")
        
        # 使用絕對路徑避免路徑解析問題
        db_path = os.path.join(instance_dir, 'shift_schedule.db')
        database_url = f'sqlite:///{db_path}'
        print(f"🔧 本地環境：使用檔案 SQLite 資料庫 ({db_path})")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 生產環境安全設定（開發測試環境暫時放寬）
    if os.environ.get('FLASK_ENV') == 'production':
        # 暫時關閉SECURE要求，因為使用HTTP localhost測試
        app.config['SESSION_COOKIE_SECURE'] = False
        app.config['SESSION_COOKIE_HTTPONLY'] = True
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    db.init_app(app)
    
    from app.routes import main
    from app.auth import auth
    app.register_blueprint(main)
    app.register_blueprint(auth)
    
    # 初始化預設群組
    def init_default_groups():
        """初始化預設群組資料"""
        try:
            from app.models import GroupMembers
            
            default_groups = ['統籌組', '燈光組', '舞台組', '視聽組', '維護組']
            
            for group_name in default_groups:
                existing_group = GroupMembers.query.filter_by(group_name=group_name).first()
                if not existing_group:
                    new_group = GroupMembers(group_name=group_name)
                    new_group.set_members([])  # 空的群組
                    db.session.add(new_group)
            
            db.session.commit()
            print(f"✅ 初始化 {len(default_groups)} 個預設群組")
            
        except Exception as e:
            print(f"⚠️ 群組初始化錯誤: {e}")

    # 資料庫初始化函數
    def init_database():
        try:
            # 確保所有模型都被導入
            from app.models import User, Employee, ShiftType, Schedule, ImportLog, GroupMembers, Session
            
            db.create_all()
            print("✅ 資料庫表創建成功")
            
            # 初始化預設群組
            init_default_groups()
            
            # 確保有管理員帳號
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(
                    username='admin',
                    name='系統管理員',
                    role='admin',
                    status='approved'
                )
                # 預設管理員密碼，生產環境請務必修改
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                print('👑 管理員帳號已創建: admin/admin123')
            
            # 創建測試用戶帳號
            test_users = [
                ('user1', '測試用戶1', 'user'),
                ('user2', '測試用戶2', 'user'),
                ('lightuser', '燈光組員工', 'user')
            ]
            
            for username, name, role in test_users:
                existing_user = User.query.filter_by(username=username).first()
                if not existing_user:
                    test_user = User(
                        username=username,
                        name=name,
                        role=role,
                        status='approved'
                    )
                    test_user.set_password('123456')  # 簡單密碼方便測試
                    db.session.add(test_user)
                    print(f'👤 測試帳號已創建: {username}/123456 ({name})')
            
            db.session.commit()
            
            from app.models import ShiftType
            from datetime import time
            if not ShiftType.query.first():
                default_shifts = [
                    # 基本班別
                    ShiftType(code='A', name='早班', start_time=time(8, 0), end_time=time(16, 0), color='#28a745'),
                    ShiftType(code='B', name='中班', start_time=time(16, 0), end_time=time(0, 0), color='#ffc107'),
                    ShiftType(code='C', name='晚班', start_time=time(0, 0), end_time=time(8, 0), color='#dc3545'),
                    ShiftType(code='OFF', name='休假', start_time=time(0, 0), end_time=time(0, 0), color='#6c757d'),
                    
                    # 新規範班別代碼
                    ShiftType(code='C1', name='C1班', start_time=time(8, 0), end_time=time(16, 0), color='#28a745'),
                    ShiftType(code='C2', name='C2班', start_time=time(16, 0), end_time=time(0, 0), color='#ffc107'),
                    ShiftType(code='C3', name='C3班', start_time=time(0, 0), end_time=time(8, 0), color='#dc3545'),
                    ShiftType(code='CH/FC', name='CH/FC班', start_time=time(8, 0), end_time=time(17, 0), color='#fd7e14'),
                    ShiftType(code='CH/FC*', name='CH/FC*班', start_time=time(8, 0), end_time=time(17, 0), color='#fd7e14'),
                    ShiftType(code='E1', name='E1班', start_time=time(8, 0), end_time=time(16, 0), color='#17a2b8'),
                    ShiftType(code='FC', name='FC班', start_time=time(8, 0), end_time=time(17, 0), color='#fd7e14'),
                    ShiftType(code='FC/E1', name='FC/E1班', start_time=time(8, 0), end_time=time(17, 0), color='#fd7e14'),
                    ShiftType(code='FC/PM', name='FC/PM班', start_time=time(8, 0), end_time=time(17, 0), color='#fd7e14'),
                    ShiftType(code='FX', name='FX班', start_time=time(9, 0), end_time=time(17, 0), color='#17a2b8'),
                    ShiftType(code='H0', name='H0休假', start_time=time(0, 0), end_time=time(0, 0), color='#6c757d'),
                    ShiftType(code='H1', name='H1休假', start_time=time(0, 0), end_time=time(0, 0), color='#6f42c1'),
                    ShiftType(code='N1', name='N1夜班', start_time=time(0, 0), end_time=time(8, 0), color='#6610f2'),
                    ShiftType(code='N1/E1', name='N1/E1班', start_time=time(0, 0), end_time=time(8, 0), color='#6610f2'),
                    ShiftType(code='N2', name='N2夜班', start_time=time(22, 0), end_time=time(6, 0), color='#e83e8c'),
                    ShiftType(code='NT/FC', name='NT/FC班', start_time=time(22, 0), end_time=time(6, 0), color='#e83e8c'),
                    ShiftType(code='P1c', name='P1中班', start_time=time(14, 0), end_time=time(22, 0), color='#ffc107'),
                    ShiftType(code='P1c/P3p', name='P1c/P3p班', start_time=time(14, 0), end_time=time(22, 0), color='#ffc107'),
                    ShiftType(code='P1n', name='P1夜班', start_time=time(22, 0), end_time=time(6, 0), color='#dc3545'),
                    ShiftType(code='P1n/LED', name='P1n/LED班', start_time=time(22, 0), end_time=time(6, 0), color='#dc3545'),
                    ShiftType(code='P1p', name='P1晚班', start_time=time(22, 0), end_time=time(6, 0), color='#dc3545'),
                    ShiftType(code='P1p/Crew', name='P1p/Crew班', start_time=time(22, 0), end_time=time(6, 0), color='#dc3545'),
                    ShiftType(code='P1p/LED', name='P1p/LED班', start_time=time(22, 0), end_time=time(6, 0), color='#dc3545'),
                    ShiftType(code='P1p/ME', name='P1p/ME班', start_time=time(22, 0), end_time=time(6, 0), color='#dc3545'),
                    ShiftType(code='P1p/PM', name='P1p/PM班', start_time=time(22, 0), end_time=time(6, 0), color='#dc3545'),
                    ShiftType(code='P1s', name='P1早班', start_time=time(6, 0), end_time=time(14, 0), color='#28a745'),
                    ShiftType(code='P1s/Crew', name='P1s/Crew班', start_time=time(6, 0), end_time=time(14, 0), color='#28a745'),
                    ShiftType(code='P1s/PM', name='P1s/PM班', start_time=time(6, 0), end_time=time(14, 0), color='#28a745'),
                    ShiftType(code='P2c', name='P2中班', start_time=time(14, 0), end_time=time(22, 0), color='#ffc107'),
                    ShiftType(code='P2n', name='P2夜班', start_time=time(22, 0), end_time=time(6, 0), color='#dc3545'),
                    ShiftType(code='P2p', name='P2晚班', start_time=time(22, 0), end_time=time(6, 0), color='#dc3545'),
                    ShiftType(code='P2p/Crew', name='P2p/Crew班', start_time=time(22, 0), end_time=time(6, 0), color='#dc3545'),
                    ShiftType(code='P2p/LD', name='P2p/LD班', start_time=time(22, 0), end_time=time(6, 0), color='#dc3545'),
                    ShiftType(code='P2s', name='P2早班', start_time=time(6, 0), end_time=time(14, 0), color='#28a745'),
                    ShiftType(code='P2s/Crew', name='P2s/Crew班', start_time=time(6, 0), end_time=time(14, 0), color='#28a745'),
                    ShiftType(code='P2s/LD', name='P2s/LD班', start_time=time(6, 0), end_time=time(14, 0), color='#28a745'),
                    ShiftType(code='P3c', name='P3中班', start_time=time(14, 0), end_time=time(22, 0), color='#ffc107'),
                    ShiftType(code='P3n', name='P3夜班', start_time=time(22, 0), end_time=time(6, 0), color='#dc3545'),
                    ShiftType(code='P3p', name='P3晚班', start_time=time(20, 0), end_time=time(4, 0), color='#6f42c1'),
                    ShiftType(code='P4n', name='P4夜班', start_time=time(22, 0), end_time=time(6, 0), color='#dc3545'),
                    ShiftType(code='P4p', name='P4晚班', start_time=time(22, 0), end_time=time(6, 0), color='#dc3545'),
                    ShiftType(code='P5', name='P5班', start_time=time(8, 0), end_time=time(16, 0), color='#198754'),
                    ShiftType(code='P5/lobby', name='P5/lobby班', start_time=time(8, 0), end_time=time(16, 0), color='#198754')
                ]
                for shift in default_shifts:
                    db.session.add(shift)
                db.session.commit()
                print(f'✅ 初始化 {len(default_shifts)} 個班別類型')
        except Exception as e:
            print(f"⚠️ 資料庫初始化錯誤: {e}")
    
    # 初始化測試員工資料
    def init_test_employees():
        try:
            from app.models import Employee, Schedule, ShiftType
            from datetime import datetime, date
            
            # 員工工號對應
            employee_data = [
                ('賴 秉 宏', '8652'),
                ('李 惟 綱', '8312'), 
                ('李 家 瑋', '8512'),
                ('王 志 忠', '0450'),
                ('顧 育 禎', '8672'),
                ('胡 翊 潔', '8619'),
                ('朱 家 德', '8835')
            ]
            
            # 建立員工資料
            created_count = 0
            for name, code in employee_data:
                employee = Employee.query.filter_by(name=name).first()
                if not employee:
                    employee = Employee(name=name, employee_code=code)
                    db.session.add(employee)
                    created_count += 1
            
            db.session.commit()
            print(f'✅ 初始化 {len(employee_data)} 個測試員工 (新建 {created_count} 個)')
            
            # 清除現有排班資料避免重複
            existing_schedules = Schedule.query.count()
            if existing_schedules > 0:
                print(f'🗑️ 清除現有 {existing_schedules} 筆排班資料')
                Schedule.query.delete()
                db.session.commit()
                
            # 註釋掉自動建立測試排班資料，讓用戶可以進行乾淨測試
            # print('🔄 跳過自動建立測試排班資料，等待用戶匯入')
            
        except Exception as e:
            print(f"⚠️ 測試資料初始化錯誤: {e}")
            import traceback
            traceback.print_exc()
    
    # 在應用context中初始化資料庫
    with app.app_context():
        print("🚀 開始應用程式初始化...")
        init_database()
        print("🔄 開始初始化測試員工...")
        init_test_employees()
        print("✅ 應用程式初始化完成")
    
    return app