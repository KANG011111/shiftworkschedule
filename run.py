from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # 生產環境設定
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)