from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, comment='登入帳號')
    password_hash = db.Column(db.String(255), nullable=False, comment='加密密碼')
    name = db.Column(db.String(100), nullable=False, comment='真實姓名')
    role = db.Column(db.Enum('admin', 'user', name='user_role'), default='user', comment='用戶角色')
    status = db.Column(db.Enum('pending', 'approved', 'rejected', 'disabled', name='user_status'), 
                      default='pending', comment='帳號狀態')
    failed_attempts = db.Column(db.Integer, default=0, comment='登入失敗次數')
    locked_until = db.Column(db.DateTime, nullable=True, comment='鎖定到期時間')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯到員工表（如果用戶是員工）
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    employee = db.relationship('Employee', backref='user', uselist=False)
    
    # 關聯到會話表
    sessions = db.relationship('Session', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """設定密碼（加密）"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """檢查密碼"""
        return check_password_hash(self.password_hash, password)
    
    def is_locked(self):
        """檢查帳號是否被鎖定"""
        if self.locked_until:
            return datetime.utcnow() < self.locked_until
        return False
    
    def lock_account(self):
        """根據失敗次數鎖定帳號"""
        if self.failed_attempts >= 15:
            # 15次失敗：鎖定24小時
            self.locked_until = datetime.utcnow() + timedelta(hours=24)
        elif self.failed_attempts >= 10:
            # 10次失敗：鎖定1小時
            self.locked_until = datetime.utcnow() + timedelta(hours=1)
        elif self.failed_attempts >= 5:
            # 5次失敗：鎖定15分鐘
            self.locked_until = datetime.utcnow() + timedelta(minutes=15)
    
    def reset_failed_attempts(self):
        """重置登入失敗次數"""
        self.failed_attempts = 0
        self.locked_until = None
    
    def can_login(self):
        """檢查是否可以登入"""
        return (self.status == 'approved' and 
                not self.is_locked())
    
    def __repr__(self):
        return f'<User {self.username}>'

class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = db.Column(db.String(128), primary_key=True, comment='Session ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    def __init__(self, user_id):
        self.id = secrets.token_urlsafe(96)  # 生成安全的session ID
        self.user_id = user_id
        self.expires_at = datetime.utcnow() + timedelta(hours=8)  # 8小時過期
    
    def is_expired(self):
        """檢查session是否過期"""
        return datetime.utcnow() > self.expires_at
    
    def is_idle_timeout(self):
        """檢查是否閒置超時（2小時）"""
        return datetime.utcnow() > (self.last_activity + timedelta(hours=2))
    
    def update_activity(self):
        """更新活動時間"""
        self.last_activity = datetime.utcnow()
    
    def is_valid(self):
        """檢查session是否有效"""
        return not (self.is_expired() or self.is_idle_timeout())
    
    def __repr__(self):
        return f'<Session {self.id[:8]}... for User {self.user_id}>'

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    employee_code = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    schedules = db.relationship('Schedule', backref='employee', lazy=True)
    
    def __repr__(self):
        return f'<Employee {self.name}>'

class ShiftType(db.Model):
    __tablename__ = 'shift_types'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    color = db.Column(db.String(7), default='#007bff')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    schedules = db.relationship('Schedule', backref='shift_type', lazy=True)
    
    def __repr__(self):
        return f'<ShiftType {self.name}>'

class Schedule(db.Model):
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    shift_type_id = db.Column(db.Integer, db.ForeignKey('shift_types.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Schedule {self.date} - {self.employee.name} - {self.shift_type.name}>'

class ImportLog(db.Model):
    """匯入日誌記錄表"""
    __tablename__ = 'import_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    importer = db.Column(db.String(100), nullable=False, comment='匯入者')
    filename = db.Column(db.String(255), nullable=False, comment='檔名')
    import_time = db.Column(db.DateTime, default=datetime.utcnow, comment='匯入時間')
    data_version = db.Column(db.String(50), nullable=False, comment='選擇版本')
    target_group = db.Column(db.String(50), nullable=False, comment='匯入群組')
    validation_result = db.Column(db.Enum('OK', 'WARNING', 'ERROR', name='validation_result'), 
                                nullable=False, comment='驗證結果')
    force_import = db.Column(db.Boolean, default=False, comment='是否強制匯入')
    error_count = db.Column(db.Integer, default=0, comment='錯誤數量')
    warning_count = db.Column(db.Integer, default=0, comment='警告數量')
    records_imported = db.Column(db.Integer, default=0, comment='匯入記錄數')
    validation_errors = db.Column(db.Text, comment='驗證錯誤訊息(JSON格式)')
    
    def set_validation_errors(self, errors_list):
        """設置驗證錯誤列表"""
        self.validation_errors = json.dumps(errors_list, ensure_ascii=False)
    
    def get_validation_errors(self):
        """獲取驗證錯誤列表"""
        if self.validation_errors:
            return json.loads(self.validation_errors)
        return []
    
    def __repr__(self):
        return f'<ImportLog {self.filename} by {self.importer}>'