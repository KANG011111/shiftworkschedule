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
    elif 'production' in flask_env or not os.access(os.getcwd(), os.W_OK):
        # 生產環境或無寫入權限時使用記憶體資料庫
        database_url = 'sqlite:///:memory:'
        print("🏭 強制使用記憶體 SQLite 資料庫（生產環境或無寫入權限）")
    else:
        # 開發環境使用檔案資料庫
        database_url = 'sqlite:///instance/shift_schedule.db'
        print("🔧 開發環境：使用檔案 SQLite 資料庫")
    
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
    
    # 資料庫初始化函數
    def init_database():
        try:
            db.create_all()
            print("✅ 資料庫表創建成功")
            
            # 確保有管理員帳號
            from app.models import User
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
                db.session.commit()
                print('👑 管理員帳號已創建: admin/admin123')
            
            from app.models import ShiftType
            from datetime import time
            if not ShiftType.query.first():
                default_shifts = [
                    # 基本班別
                    ShiftType(code='A', name='早班', start_time=time(8, 0), end_time=time(16, 0), color='#28a745'),
                    ShiftType(code='B', name='中班', start_time=time(16, 0), end_time=time(0, 0), color='#ffc107'),
                    ShiftType(code='C', name='晚班', start_time=time(0, 0), end_time=time(8, 0), color='#dc3545'),
                    ShiftType(code='OFF', name='休假', start_time=time(0, 0), end_time=time(0, 0), color='#6c757d'),
                    
                    # FC系列
                    ShiftType(code='FC', name='消防班', start_time=time(8, 0), end_time=time(17, 0), color='#fd7e14'),
                    ShiftType(code='FC/工程', name='FC工程班', start_time=time(8, 0), end_time=time(17, 0), color='#fd7e14'),
                    ShiftType(code='FC/急救課', name='FC急救課', start_time=time(8, 0), end_time=time(17, 0), color='#fd7e14'),
                    ShiftType(code='FX', name='固定班', start_time=time(9, 0), end_time=time(17, 0), color='#17a2b8'),
                    
                    # P1系列
                    ShiftType(code='P1s', name='P1早班', start_time=time(6, 0), end_time=time(14, 0), color='#28a745'),
                    ShiftType(code='P1s2', name='P1早班2', start_time=time(7, 0), end_time=time(15, 0), color='#198754'),
                    ShiftType(code='P1c', name='P1中班', start_time=time(14, 0), end_time=time(22, 0), color='#ffc107'),
                    ShiftType(code='P1c2', name='P1中班2', start_time=time(7, 0), end_time=time(15, 0), color='#20c997'),
                    ShiftType(code='P1n', name='P1夜班', start_time=time(19, 0), end_time=time(7, 0), color='#e83e8c'),
                    ShiftType(code='P1n/夜超', name='P1夜超班', start_time=time(19, 0), end_time=time(7, 0), color='#dc3545'),
                    ShiftType(code='P1p', name='P1晚班', start_time=time(22, 0), end_time=time(6, 0), color='#dc3545'),
                    ShiftType(code='P1p2', name='P1晚班2', start_time=time(20, 0), end_time=time(4, 0), color='#6f42c1'),
                    ShiftType(code='P1p/ME', name='P1晚班/ME', start_time=time(22, 0), end_time=time(6, 0), color='#dc3545'),
                    
                    # P2系列
                    ShiftType(code='P2s', name='P2早班', start_time=time(6, 0), end_time=time(14, 0), color='#198754'),
                    ShiftType(code='P2c', name='P2中班', start_time=time(14, 0), end_time=time(22, 0), color='#fd7e14'),
                    ShiftType(code='P2n', name='P2夜班', start_time=time(22, 0), end_time=time(6, 0), color='#6610f2'),
                    ShiftType(code='P2p', name='P2晚班', start_time=time(22, 0), end_time=time(6, 0), color='#0dcaf0'),
                    ShiftType(code='P2p/LD', name='P2晚班/LD', start_time=time(22, 0), end_time=time(6, 0), color='#0dcaf0'),
                    
                    # P3系列
                    ShiftType(code='P3c', name='P3中班', start_time=time(14, 0), end_time=time(22, 0), color='#fd7e14'),
                    ShiftType(code='P3n', name='P3夜班', start_time=time(22, 0), end_time=time(6, 0), color='#e83e8c'),
                    ShiftType(code='P3n/夜超', name='P3夜超班', start_time=time(22, 0), end_time=time(6, 0), color='#e83e8c'),
                    ShiftType(code='P3p', name='P3晚班', start_time=time(20, 0), end_time=time(4, 0), color='#6f42c1'),
                    
                    # P4系列
                    ShiftType(code='P4c', name='P4中班', start_time=time(14, 0), end_time=time(22, 0), color='#fd7e14'),
                    ShiftType(code='P4n', name='P4夜班', start_time=time(20, 0), end_time=time(8, 0), color='#6610f2'),
                    ShiftType(code='P4p', name='P4晚班', start_time=time(22, 0), end_time=time(6, 0), color='#dc3545'),
                    
                    # 其他P系列
                    ShiftType(code='P5', name='P5班', start_time=time(8, 0), end_time=time(16, 0), color='#198754'),
                    ShiftType(code='P6', name='P6班', start_time=time(16, 0), end_time=time(0, 0), color='#0dcaf0'),
                    
                    # C系列
                    ShiftType(code='C1', name='C1班', start_time=time(8, 0), end_time=time(16, 0), color='#28a745'),
                    ShiftType(code='C3', name='C3班', start_time=time(16, 0), end_time=time(0, 0), color='#dc3545'),
                    
                    # N系列
                    ShiftType(code='N1', name='N1夜班', start_time=time(0, 0), end_time=time(8, 0), color='#6610f2'),
                    ShiftType(code='N2', name='N2夜班', start_time=time(22, 0), end_time=time(6, 0), color='#e83e8c'),
                    
                    # E和R系列
                    ShiftType(code='E1', name='E1班', start_time=time(8, 0), end_time=time(16, 0), color='#fd7e14'),
                    ShiftType(code='R1', name='R1班', start_time=time(9, 0), end_time=time(17, 0), color='#17a2b8'),
                    
                    # 休假系列
                    ShiftType(code='H0', name='休假-週末', start_time=time(0, 0), end_time=time(0, 0), color='#6c757d'),
                    ShiftType(code='H1', name='休假-平日', start_time=time(0, 0), end_time=time(0, 0), color='#6f42c1'),
                    
                    # 其他
                    ShiftType(code='舞台', name='舞台班', start_time=time(8, 0), end_time=time(17, 0), color='#6c757d')
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
                
            # 建立完整31天測試班表資料
            import random
            from datetime import datetime, date
            
            # 設定隨機種子確保可重現結果  
            random.seed(42)
            
            shift_codes = ['FC', 'FX', 'P1c', 'P1n', 'P1p', 'P1s', 'P2c', 'P2n', 'P2p', 'P2s', 
                          'P3c', 'P3n', 'P3p', 'P4c', 'P4n', 'P4p', 'H0', 'H1']
            
            # 獲取所有班別類型
            shift_types = {st.code: st for st in ShiftType.query.all()}
            print(f'🔍 可用班別代碼: {len(shift_types)} 個')
            
            schedule_count = 0
            total_expected = 31 * len(employee_data)  # 31天 × 7員工 = 217筆
            
            # 為每個員工建立完整31天排班
            for name, _ in employee_data:
                employee = Employee.query.filter_by(name=name).first()
                if not employee:
                    print(f'⚠️ 找不到員工: {name}')
                    continue
                    
                employee_schedules = 0
                for day in range(1, 32):  # 1-31天
                    schedule_date = date(2025, 7, day)
                    
                    # 隨機選擇班別代碼
                    shift_code = random.choice(shift_codes)
                    shift_type = shift_types.get(shift_code)
                    
                    if shift_type:
                        schedule = Schedule(
                            employee_id=employee.id,
                            shift_type_id=shift_type.id,
                            date=schedule_date
                        )
                        db.session.add(schedule)
                        schedule_count += 1
                        employee_schedules += 1
                    else:
                        print(f'⚠️ 找不到班別類型: {shift_code}')
                
                print(f'📅 {name}: 建立 {employee_schedules} 天排班')
            
            db.session.commit()
            print(f'✅ 初始化 {schedule_count}/{total_expected} 筆測試班表資料')
            
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