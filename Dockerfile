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

# 創建應用用戶（非 root，提高安全性）
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# 切換到應用用戶
USER appuser

# 設定環境變數
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 5000

# 設置啟動腳本權限
RUN chmod +x start.sh

# 運行應用程式
CMD ["./start.sh"]