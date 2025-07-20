#!/usr/bin/env python3
"""重設資料庫腳本"""

from app import create_app
from app.models import db

# 建立應用實例
app = create_app()

with app.app_context():
    # 刪除所有表格
    db.drop_all()
    print("已刪除所有資料表")
    
    # 重新建立所有表格
    db.create_all()
    print("已重新建立所有資料表")
    
    print("資料庫重設完成！")