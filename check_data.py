from app import create_app
from app.models import db, Employee, ShiftType, Schedule

app = create_app()

with app.app_context():
    print(f"員工數量: {Employee.query.count()}")
    print(f"班別數量: {ShiftType.query.count()}")
    print(f"班表數量: {Schedule.query.count()}")
    
    if Schedule.query.count() > 0:
        print("\n前5筆班表記錄:")
        for schedule in Schedule.query.limit(5).all():
            print(f"  {schedule.date} - {schedule.employee.name} - {schedule.shift_type.code}")