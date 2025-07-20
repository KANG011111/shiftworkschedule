from functools import wraps
from flask import request, jsonify, g, redirect, url_for
from app.models import Session
from datetime import datetime

def require_auth(f):
    """要求用戶登入的裝飾器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = request.cookies.get('sessionId')
        
        if not session_id:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'success': False, 'message': '需要登入'}), 401
            return redirect(url_for('auth.login_page'))
        
        session = Session.query.get(session_id)
        
        if not session or not session.is_valid():
            # 清除無效session
            if session:
                from app.models import db
                db.session.delete(session)
                db.session.commit()
            
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'success': False, 'message': 'Session已過期'}), 401
            return redirect(url_for('auth.login_page'))
        
        # 更新活動時間
        session.update_activity()
        from app.models import db
        db.session.commit()
        
        # 將用戶信息存儲在g中供視圖使用
        g.current_user = session.user
        g.current_session = session
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_admin(f):
    """要求管理員權限的裝飾器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 先檢查是否登入
        auth_result = require_auth(lambda: None)()
        if auth_result is not None:  # 有返回值表示認證失敗
            return auth_result
        
        # 檢查是否為管理員
        if g.current_user.role != 'admin':
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'success': False, 'message': '需要管理員權限'}), 403
            return redirect(url_for('main.index'))  # 重定向到首頁
        
        return f(*args, **kwargs)
    
    return decorated_function

def optional_auth(f):
    """可選登入的裝飾器（不強制登入但會設置用戶信息）"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = request.cookies.get('sessionId')
        g.current_user = None
        g.current_session = None
        
        if session_id:
            session = Session.query.get(session_id)
            
            if session and session.is_valid():
                # 更新活動時間
                session.update_activity()
                from app.models import db
                db.session.commit()
                
                g.current_user = session.user
                g.current_session = session
        
        return f(*args, **kwargs)
    
    return decorated_function

def get_current_user():
    """獲取當前登入用戶"""
    return getattr(g, 'current_user', None)

def is_logged_in():
    """檢查是否已登入"""
    return get_current_user() is not None

def is_admin():
    """檢查是否為管理員"""
    user = get_current_user()
    return user and user.role == 'admin'

def cleanup_expired_sessions():
    """清理過期的session（可以設定為定期任務）"""
    try:
        from app.models import db
        from datetime import timedelta
        expired_sessions = Session.query.filter(
            (Session.expires_at < datetime.utcnow()) |
            (Session.last_activity < datetime.utcnow() - timedelta(hours=2))
        ).all()
        
        for session in expired_sessions:
            db.session.delete(session)
        
        db.session.commit()
        return len(expired_sessions)
    except Exception as e:
        print(f'清理過期session錯誤: {e}')
        return 0