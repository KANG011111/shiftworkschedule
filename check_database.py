#!/usr/bin/env python3
"""
檢查資料庫中的員工和排班記錄
"""

import os
import sys
sys.path.insert(0, '/app')

# 設置環境變數，模擬Docker環境
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['FLASK_ENV'] = 'development'

from datetime import date
from app import create_app
from app.models import db, Employee, Schedule, ShiftType

def check_database():
    app = create_app()
    
    with app.app_context():
        print("🔍 資料庫檢查報告")
        print("=" * 50)
        
        # 檢查員工記錄
        employees = Employee.query.all()
        print(f"👥 員工總數: {len(employees)}")
        
        if employees:
            print("\n前10個員工:")
            for i, emp in enumerate(employees[:10]):
                print(f"  {i+1}. {emp.name} (代碼: {emp.employee_code})")
        
        # 檢查排班記錄
        schedules = Schedule.query.all()
        print(f"\n📅 排班記錄總數: {len(schedules)}")
        
        if schedules:
            # 按日期分組統計
            dates = {}
            for schedule in schedules:
                date_str = schedule.date.strftime('%Y-%m-%d')
                dates[date_str] = dates.get(date_str, 0) + 1
            
            print("\n排班日期分布:")
            for date_str in sorted(dates.keys()):
                print(f"  {date_str}: {dates[date_str]}筆記錄")
        
        # 檢查今日排班
        today = date.today()
        today_schedules = Schedule.query.filter(Schedule.date == today).all()
        print(f"\n🗓️ 今日 ({today}) 排班: {len(today_schedules)}筆")
        
        # 檢查最近的排班記錄
        if schedules:
            latest_schedules = Schedule.query.order_by(Schedule.date.desc()).limit(5).all()
            print("\n最新的5筆排班記錄:")
            for schedule in latest_schedules:
                print(f"  {schedule.date} - {schedule.employee.name} - {schedule.shift_type.code}")

if __name__ == "__main__":
    check_database()