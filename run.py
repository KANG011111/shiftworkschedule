from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # 檢查環境模式
    flask_env = os.environ.get('FLASK_ENV', 'production')
    
    if flask_env == 'development':
        # 開發模式：啟用熱重載和調試
        print("🔧 開發模式：啟用熱重載和調試")
        app.run(
            debug=True, 
            host='0.0.0.0', 
            port=5000,
            use_reloader=True,
            use_debugger=True
        )
    else:
        # 生產環境設定
        debug_mode = flask_env != 'production'
        port = int(os.environ.get('PORT', 8080))
        app.run(debug=debug_mode, host='0.0.0.0', port=port)