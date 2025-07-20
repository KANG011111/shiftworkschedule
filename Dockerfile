# 使用 Python 3.9 作為基礎映像
FROM python:3.9-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt 並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式代碼
COPY . .

# 創建應用用戶（非 root）
RUN useradd -m -u 1000 appuser

# 創建資料庫目錄並設定權限
RUN mkdir -p /app/instance && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app/instance

# 切換到應用用戶
USER appuser

# 設定環境變數
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 5000

# 創建啟動腳本
RUN echo '#!/bin/bash\n\
echo "正在初始化資料庫..."\n\
python -c "from app import create_app; app = create_app(); app.app_context().push(); from app.models import db; db.create_all(); print(\"資料庫初始化完成\")"\n\
echo "啟動應用程式..."\n\
python run.py\n\
' > start.sh && chmod +x start.sh

# 運行應用程式
CMD ["./start.sh"]