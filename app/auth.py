from flask import Blueprint, request, jsonify, make_response, render_template, redirect, url_for
from app.models import db, User, Session
from app.auth_middleware import optional_auth, get_current_user
from datetime import datetime
import re

auth = Blueprint('auth', __name__)

def validate_password(password):
    """驗證密碼強度"""
    if len(password) < 8:
        return False, "密碼至少需要8個字符"
    
    if not re.search(r'[A-Za-z]', password):
        return False, "密碼必須包含字母"
    
    if not re.search(r'\d', password):
        return False, "密碼必須包含數字"
    
    return True, ""

def validate_username(username):
    """驗證用戶名格式"""
    if len(username) < 3:
        return False, "用戶名至少需要3個字符"
    
    if len(username) > 50:
        return False, "用戶名不能超過50個字符"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "用戶名只能包含字母、數字和下劃線"
    
    return True, ""

@auth.route('/api/auth/register', methods=['POST'])
def register():
    """用戶註冊"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': '請提供註冊資料'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        
        # 驗證必填字段
        if not username or not password or not name:
            return jsonify({'success': False, 'message': '請填寫所有必填字段'}), 400
        
        # 驗證用戶名格式
        valid_username, username_error = validate_username(username)
        if not valid_username:
            return jsonify({'success': False, 'message': username_error}), 400
        
        # 驗證密碼強度
        valid_password, password_error = validate_password(password)
        if not valid_password:
            return jsonify({'success': False, 'message': password_error}), 400
        
        # 檢查用戶名是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': '用戶名已存在'}), 400
        
        # 創建新用戶
        user = User(
            username=username,
            name=name,
            role='user',
            status='pending'  # 需要管理員審核
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': '註冊申請已提交，等待管理員審核'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f'註冊錯誤: {e}')
        return jsonify({'success': False, 'message': '註冊失敗，請稍後再試'}), 500

@auth.route('/api/auth/login', methods=['POST'])
def login():
    """用戶登入"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': '請提供登入資料'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'success': False, 'message': '請填寫用戶名和密碼'}), 400
        
        # 查找用戶
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return jsonify({'success': False, 'message': '帳號或密碼錯誤'}), 401
        
        # 檢查帳號是否被鎖定
        if user.is_locked():
            return jsonify({
                'success': False, 
                'message': f'帳號已被鎖定，請稍後再試'
            }), 429
        
        # 檢查帳號狀態
        if user.status == 'pending':
            return jsonify({'success': False, 'message': '帳號等待審核中'}), 401
        elif user.status == 'rejected':
            return jsonify({'success': False, 'message': '帳號申請已被拒絕'}), 401
        elif user.status == 'disabled':
            return jsonify({'success': False, 'message': '帳號已被停用'}), 401
        
        # 驗證密碼
        if not user.check_password(password):
            # 增加失敗次數
            user.failed_attempts += 1
            user.lock_account()  # 根據失敗次數決定是否鎖定
            db.session.commit()
            
            return jsonify({'success': False, 'message': '帳號或密碼錯誤'}), 401
        
        # 檢查是否可以登入
        if not user.can_login():
            return jsonify({'success': False, 'message': '無法登入，請聯繫管理員'}), 401
        
        # 重置失敗次數
        user.reset_failed_attempts()
        
        # 創建新的session
        session = Session(user.id)
        db.session.add(session)
        db.session.commit()
        
        # 設置cookie
        response = make_response(jsonify({
            'success': True,
            'data': {
                'sessionId': session.id,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'name': user.name,
                    'role': user.role
                }
            }
        }))
        
        # 設置httpOnly cookie，提高安全性
        import os
        is_production = os.environ.get('FLASK_ENV') == 'production'
        
        response.set_cookie(
            'sessionId', 
            session.id, 
            max_age=8*60*60,  # 8小時
            httponly=True,
            secure=False,  # 暫時關閉secure要求，支援HTTP localhost
            samesite='Lax'
        )
        
        return response
        
    except Exception as e:
        db.session.rollback()
        print(f'登入錯誤: {e}')
        return jsonify({'success': False, 'message': '登入失敗，請稍後再試'}), 500

@auth.route('/api/auth/logout', methods=['POST'])
def logout():
    """用戶登出"""
    try:
        # 從cookie獲取session ID
        session_id = request.cookies.get('sessionId')
        
        if session_id:
            # 刪除session
            session = Session.query.get(session_id)
            if session:
                db.session.delete(session)
                db.session.commit()
        
        # 清除cookie
        response = make_response(jsonify({
            'success': True,
            'message': '已成功登出'
        }))
        response.set_cookie('sessionId', '', expires=0)
        
        return response
        
    except Exception as e:
        db.session.rollback()
        print(f'登出錯誤: {e}')
        return jsonify({'success': False, 'message': '登出失敗'}), 500

@auth.route('/api/auth/status', methods=['GET'])
def auth_status():
    """檢查當前登入狀態"""
    try:
        session_id = request.cookies.get('sessionId')
        
        if not session_id:
            return jsonify({'success': False, 'message': '未登入'}), 401
        
        session = Session.query.get(session_id)
        
        if not session or not session.is_valid():
            # 清除無效session
            if session:
                db.session.delete(session)
                db.session.commit()
            return jsonify({'success': False, 'message': 'Session已過期'}), 401
        
        # 更新活動時間
        session.update_activity()
        db.session.commit()
        
        user = session.user
        return jsonify({
            'success': True,
            'data': {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'name': user.name,
                    'role': user.role
                }
            }
        })
        
    except Exception as e:
        print(f'狀態檢查錯誤: {e}')
        return jsonify({'success': False, 'message': '檢查失敗'}), 500

# ===== 頁面路由 =====

@auth.route('/login')
@optional_auth
def login_page():
    """登入頁面"""
    # 如果已經登入，重定向到首頁
    if get_current_user():
        return redirect(url_for('main.index'))
    return render_template('login.html')

@auth.route('/register')
@optional_auth  
def register_page():
    """註冊頁面"""
    # 如果已經登入，重定向到首頁
    if get_current_user():
        return redirect(url_for('main.index'))
    return render_template('register.html')