from flask import Blueprint, render_template, request, jsonify, redirect, url_for, g
from app.models import db, Employee, ShiftType, Schedule, User
from app.auth_middleware import require_auth, require_admin, optional_auth, get_current_user
from datetime import datetime, date
import pandas as pd
import json

main = Blueprint('main', __name__)

@main.route('/')
@optional_auth
def index():
    # 檢查用戶是否已登入
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for('auth.login_page'))
    
    today = date.today()
    
    # 指定的員工名單
    target_employees = [
        '賴秉宏', '李惟綱', '李家瑋', '王志忠', '顧育禎', 
        '胡翊潔', '朱家德', '陳韋如', '葛禎', '井康羽', 
        '簡芳瑜', '梁弘岳', '李佩璇', '鄭栢玔', '王文怡'
    ]
    
    today_schedules = Schedule.query.join(Employee).filter(
        Schedule.date == today,
        Employee.name.in_(target_employees)
    ).all()
    
    return render_template('index.html', today_schedules=today_schedules, today=today)

# 移除員工管理功能，只保留個人班表查看
# @main.route('/employees')
# @main.route('/add_employee', methods=['POST'])

@main.route('/calendar')
def calendar():
    return render_template('calendar.html')

@main.route('/api/events')
def get_events():
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    # 如果沒有提供日期參數，使用預設範圍
    if not start_date or not end_date:
        start_date = '2024-07-01'
        end_date = '2024-07-31'
    
    # 指定的員工名單
    target_employees = [
        '賴秉宏', '李惟綱', '李家瑋', '王志忠', '顧育禎', 
        '胡翊潔', '朱家德', '陳韋如', '葛禎', '井康羽', 
        '簡芳瑜', '梁弘岳', '李佩璇', '鄭栢玔', '王文怡'
    ]
    
    try:
        schedules = Schedule.query.join(Employee).filter(
            Schedule.date >= datetime.strptime(start_date, '%Y-%m-%d').date(),
            Schedule.date <= datetime.strptime(end_date, '%Y-%m-%d').date(),
            Employee.name.in_(target_employees)
        ).all()
        
        events = []
        
        # 按日期分組事件，避免太多重疊
        from collections import defaultdict
        daily_events = defaultdict(list)
        
        for schedule in schedules:
            daily_events[schedule.date].append(schedule)
        
        # 為每一天創建事件
        for schedule_date, day_schedules in daily_events.items():
            if len(day_schedules) <= 3:
                # 如果當天排班人數少，顯示個別事件
                for schedule in day_schedules:
                    events.append({
                        'id': f"single_{schedule.id}",
                        'title': f"{schedule.employee.name}({schedule.shift_type.code})",
                        'start': schedule_date.isoformat(),
                        'backgroundColor': schedule.shift_type.color,
                        'borderColor': schedule.shift_type.color,
                        'textColor': '#fff',
                        'extendedProps': {
                            'employee': schedule.employee.name,
                            'shift': schedule.shift_type.name,
                            'shift_code': schedule.shift_type.code,
                            'type': 'single'
                        }
                    })
            else:
                # 如果當天排班人數多，顯示彙總事件
                shift_summary = {}
                for schedule in day_schedules:
                    shift_code = schedule.shift_type.code
                    if shift_code not in shift_summary:
                        shift_summary[shift_code] = {
                            'count': 0,
                            'color': schedule.shift_type.color,
                            'employees': []
                        }
                    shift_summary[shift_code]['count'] += 1
                    shift_summary[shift_code]['employees'].append(schedule.employee.name)
                
                # 為每個班別創建一個事件
                for shift_code, info in shift_summary.items():
                    events.append({
                        'id': f"summary_{schedule_date}_{shift_code}",
                        'title': f"{shift_code}班 ({info['count']}人)",
                        'start': schedule_date.isoformat(),
                        'backgroundColor': info['color'],
                        'borderColor': info['color'],
                        'textColor': '#fff',
                        'extendedProps': {
                            'employees': info['employees'],
                            'shift_code': shift_code,
                            'count': info['count'],
                            'type': 'summary',
                            'date': schedule_date.isoformat()
                        }
                    })
        
        return jsonify(events)
        
    except Exception as e:
        print(f"Events API 錯誤: {e}")
        return jsonify([]), 500

@main.route('/query_shift')
def query_shift():
    query_date = request.args.get('date')
    schedules = []
    
    # 指定的員工名單
    target_employees = [
        '賴秉宏', '李惟綱', '李家瑋', '王志忠', '顧育禎', 
        '胡翊潔', '朱家德', '陳韋如', '葛禎', '井康羽', 
        '簡芳瑜', '梁弘岳', '李佩璇', '鄭栢玔', '王文怡'
    ]
    
    if query_date:
        try:
            target_date = datetime.strptime(query_date, '%Y-%m-%d').date()
            schedules = Schedule.query.join(Employee).filter(
                Schedule.date == target_date,
                Employee.name.in_(target_employees)
            ).all()
        except ValueError:
            query_date = None
    
    return render_template('query.html', query_date=query_date, schedules=schedules)

@main.route('/api/query_shift')
def api_query_shift():
    query_date = request.args.get('date')
    
    # 指定的員工名單
    target_employees = [
        '賴秉宏', '李惟綱', '李家瑋', '王志忠', '顧育禎', 
        '胡翊潔', '朱家德', '陳韋如', '葛禎', '井康羽', 
        '簡芳瑜', '梁弘岳', '李佩璇', '鄭栢玔', '王文怡'
    ]
    
    if query_date:
        target_date = datetime.strptime(query_date, '%Y-%m-%d').date()
        schedules = Schedule.query.join(Employee).filter(
            Schedule.date == target_date,
            Employee.name.in_(target_employees)
        ).all()
        
        result = []
        for schedule in schedules:
            result.append({
                'employee': schedule.employee.name,
                'shift': schedule.shift_type.name,
                'shift_code': schedule.shift_type.code,
                'color': schedule.shift_type.color
            })
        
        return jsonify(result)
    
    return jsonify([])

@main.route('/search')
def search():
    # 如果 URL 中有員工參數，預填到搜尋框
    employee_param = request.args.get('employee', '')
    return render_template('search.html', default_employee=employee_param)

@main.route('/api/search')
def api_search():
    try:
        # 取得查詢參數
        employee_name = request.args.get('employee', '').strip()
        shift_code = request.args.get('shift', '').strip()
        start_date = request.args.get('start_date', '').strip()
        end_date = request.args.get('end_date', '').strip()
        
        # 指定的員工名單
        target_employees = [
            '賴秉宏', '李惟綱', '李家瑋', '王志忠', '顧育禎', 
            '胡翊潔', '朱家德', '陳韋如', '葛禎', '井康羽', 
            '簡芳瑜', '梁弘岳', '李佩璇', '鄭栢玔', '王文怡'
        ]
        
        # 建立基礎查詢，先篩選指定員工
        query = db.session.query(Schedule).join(Employee).join(ShiftType).filter(
            Employee.name.in_(target_employees)
        )
        
        # 員工姓名篩選
        if employee_name:
            query = query.filter(Employee.name.like(f'%{employee_name}%'))
        
        # 班別篩選
        if shift_code:
            query = query.filter(ShiftType.code.like(f'%{shift_code}%'))
        
        # 日期範圍篩選
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(Schedule.date >= start_dt)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(Schedule.date <= end_dt)
            except ValueError:
                pass
        
        # 如果沒有任何篩選條件，使用預設的時間範圍
        if not any([employee_name, shift_code, start_date, end_date]):
            # 預設顯示最近30天
            from datetime import timedelta
            today = date.today()
            month_ago = today - timedelta(days=30)
            query = query.filter(Schedule.date >= month_ago)
        
        # 執行查詢並限制結果數量
        schedules = query.order_by(Schedule.date.desc()).limit(500).all()
        
        result = []
        for schedule in schedules:
            result.append({
                'date': schedule.date.strftime('%Y-%m-%d'),
                'employee': schedule.employee.name,
                'employee_code': schedule.employee.employee_code,
                'shift': schedule.shift_type.name,
                'shift_code': schedule.shift_type.code,
                'start_time': schedule.shift_type.start_time.strftime('%H:%M'),
                'end_time': schedule.shift_type.end_time.strftime('%H:%M'),
                'color': schedule.shift_type.color
            })
        
        return jsonify(result)
    
    except Exception as e:
        print(f"搜尋錯誤: {e}")
        return jsonify({'error': str(e)}), 500

@main.route('/api/employees')
def api_employees():
    search_term = request.args.get('q', '').strip()
    
    # 指定的員工名單
    target_employees = [
        '賴秉宏', '李惟綱', '李家瑋', '王志忠', '顧育禎', 
        '胡翊潔', '朱家德', '陳韋如', '葛禎', '井康羽', 
        '簡芳瑜', '梁弘岳', '李佩璇', '鄭栢玔', '王文怡'
    ]
    
    query = Employee.query.join(Schedule).distinct().filter(
        Employee.name.in_(target_employees)
    )
    if search_term:
        query = query.filter(Employee.name.contains(search_term))
    
    employees = query.limit(20).all()
    
    result = [{'id': emp.id, 'name': emp.name, 'code': emp.employee_code} for emp in employees]
    return jsonify(result)

@main.route('/api/shift_types')
def api_shift_types():
    shift_types = ShiftType.query.all()
    result = [{'code': st.code, 'name': st.name, 'color': st.color} for st in shift_types]
    return jsonify(result)

@main.route('/api/date_range')
def api_date_range():
    """獲取資料庫中實際的日期範圍，支援多月份"""
    first_schedule = Schedule.query.order_by(Schedule.date.asc()).first()
    last_schedule = Schedule.query.order_by(Schedule.date.desc()).first()
    
    if first_schedule and last_schedule:
        # 獲取所有有資料的日期
        all_dates = [s.date.strftime('%Y-%m-%d') for s in Schedule.query.all()]
        unique_dates = sorted(list(set(all_dates)))
        
        # 統計各月份的資料
        month_stats = {}
        for schedule in Schedule.query.all():
            year_month = f'{schedule.date.year}-{schedule.date.month:02d}'
            if year_month not in month_stats:
                month_stats[year_month] = {
                    'count': 0,
                    'year': schedule.date.year,
                    'month': schedule.date.month,
                    'display': f'{schedule.date.year}年{schedule.date.month:02d}月'
                }
            month_stats[year_month]['count'] += 1
        
        # 如果跨月份，顯示範圍；如果同月份，顯示單月
        if first_schedule.date.month == last_schedule.date.month and first_schedule.date.year == last_schedule.date.year:
            month_display = first_schedule.date.strftime('%Y年%m月')
        else:
            month_display = f'{first_schedule.date.strftime("%Y年%m月")} 至 {last_schedule.date.strftime("%Y年%m月")}'
        
        return jsonify({
            'start_date': first_schedule.date.strftime('%Y-%m-%d'),
            'end_date': last_schedule.date.strftime('%Y-%m-%d'),
            'month_year': month_display,
            'year': first_schedule.date.year,
            'month': first_schedule.date.month,
            'available_dates': unique_dates,
            'available_months': month_stats
        })
    else:
        return jsonify({
            'start_date': '2025-07-01',
            'end_date': '2025-07-31',
            'month_year': '2025年07月',
            'year': 2025,
            'month': 7,
            'available_dates': [],
            'available_months': {}
        })

@main.route('/export_schedule')
def export_schedule():
    """一鍵匯出月度班表頁面"""
    return render_template('export.html')

@main.route('/api/preview_schedule')
def api_preview_schedule():
    """提供班表預覽資料給前端生成JPG"""
    try:
        # 取得查詢參數
        search_query = request.args.get('query', '').strip()
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        
        if not search_query:
            return jsonify({'error': '請輸入員工姓名或工號'}), 400
            
        if not year or not month:
            return jsonify({'error': '請選擇年月'}), 400
            
        # 指定的員工名單
        target_employees = [
            '賴秉宏', '李惟綱', '李家瑋', '王志忠', '顧育禎', 
            '胡翊潔', '朱家德', '陳韋如', '葛禎', '井康羽', 
            '簡芳瑜', '梁弘岳', '李佩璇', '鄭栢玔', '王文怡'
        ]
        
        # 搜尋員工（支援姓名或員工代碼），但限制在指定員工名單內
        employee = Employee.query.filter(
            ((Employee.name.like(f'%{search_query}%')) |
             (Employee.employee_code.like(f'%{search_query}%'))) &
            (Employee.name.in_(target_employees))
        ).first()
        
        if not employee:
            return jsonify({'error': f'找不到員工: {search_query}'}), 404
            
        # 取得該員工的月度排班資料
        from datetime import date
        import calendar
        
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
        
        schedules = Schedule.query.filter(
            Schedule.employee_id == employee.id,
            Schedule.date >= start_date,
            Schedule.date <= end_date
        ).order_by(Schedule.date.asc()).all()
        
        if not schedules:
            return jsonify({'error': f'{employee.name} 在 {year}年{month:02d}月 沒有排班資料'}), 404
            
        # 建立月曆結構
        cal = calendar.monthcalendar(year, month)
        
        # 準備排班資料
        schedule_data = []
        for schedule in schedules:
            schedule_data.append({
                'date': schedule.date.isoformat(),
                'shift_code': schedule.shift_type.code,
                'shift_name': schedule.shift_type.name
            })
        
        # 準備回傳資料
        response_data = {
            'employee': {
                'name': employee.name,
                'employee_code': employee.employee_code
            },
            'year': year,
            'month': month,
            'schedules': schedule_data,
            'calendar': cal
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f'預覽API錯誤: {e}')
        return jsonify({'error': str(e)}), 500

@main.route('/api/export_monthly_schedule')
def api_export_monthly_schedule():
    """匯出指定員工的月度班表為Excel"""
    try:
        # 取得查詢參數
        search_query = request.args.get('query', '').strip()
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        
        if not search_query:
            return jsonify({'error': '請輸入員工姓名或工號'}), 400
            
        if not year or not month:
            return jsonify({'error': '請選擇年月'}), 400
            
        # 搜尋員工（支援姓名或員工代碼）
        employee = Employee.query.filter(
            (Employee.name.like(f'%{search_query}%')) |
            (Employee.employee_code.like(f'%{search_query}%'))
        ).first()
        
        if not employee:
            return jsonify({'error': f'找不到員工: {search_query}'}), 404
            
        # 取得該員工的月度排班資料
        from datetime import date
        start_date = date(year, month, 1)
        
        # 計算月份的最後一天
        import calendar
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
        
        schedules = Schedule.query.filter(
            Schedule.employee_id == employee.id,
            Schedule.date >= start_date,
            Schedule.date <= end_date
        ).order_by(Schedule.date.asc()).all()
        
        if not schedules:
            return jsonify({'error': f'{employee.name} 在 {year}年{month:02d}月 沒有排班資料'}), 404
            
        # 建立月曆式Excel匯出
        import pandas as pd
        from io import BytesIO
        import calendar
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
        
        # 建立工作簿
        wb = Workbook()
        ws = wb.active
        ws.title = '月度班表'
        
        # 設定標題
        ws['A1'] = f'{employee.name} 個人班表'
        ws['A2'] = f'工號: {employee.employee_code}'
        ws['A3'] = f'{year}年{month:02d}月'
        
        # 合併標題儲存格
        ws.merge_cells('A1:H1')
        ws.merge_cells('A2:H2')
        ws.merge_cells('A3:H3')
        
        # 設定標題樣式
        title_font = Font(name='微軟正黑體', size=16, bold=True)
        subtitle_font = Font(name='微軟正黑體', size=12)
        ws['A1'].font = title_font
        ws['A2'].font = subtitle_font
        ws['A3'].font = subtitle_font
        ws['A1'].alignment = Alignment(horizontal='center')
        ws['A2'].alignment = Alignment(horizontal='center')
        ws['A3'].alignment = Alignment(horizontal='center')
        
        # 建立班表資料字典
        schedule_dict = {}
        for schedule in schedules:
            schedule_dict[schedule.date.day] = schedule.shift_type.code
        
        # 取得該月的日曆資訊
        cal = calendar.monthcalendar(year, month)
        weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
        
        # 從第5行開始建立日曆表格
        start_row = 5
        
        # 寫入星期標題
        for col, weekday in enumerate(weekdays, 1):
            cell = ws.cell(row=start_row, column=col, value=weekday)
            cell.font = Font(name='微軟正黑體', size=12, bold=True)
            cell.fill = PatternFill(start_color='D9E2F3', end_color='D9E2F3', fill_type='solid')
            cell.alignment = Alignment(horizontal='center')
            
        # 設定邊框樣式
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # 填入日期和班別
        for week_num, week in enumerate(cal):
            row = start_row + 1 + week_num
            for day_num, day in enumerate(week, 1):
                if day == 0:  # 空白日期
                    cell = ws.cell(row=row, column=day_num, value='')
                else:
                    # 日期
                    date_str = str(day)
                    # 班別（如果有的話）
                    shift_code = schedule_dict.get(day, '')
                    
                    if shift_code:
                        cell_value = f'{date_str}\n{shift_code}'
                        # 設定班別背景色
                        if 'H' in shift_code:  # 休假
                            fill_color = 'FFE6CC'  # 淺橙色
                        elif 'P1' in shift_code:  # P1班
                            fill_color = 'E2EFDA'  # 淺綠色
                        elif 'P2' in shift_code:  # P2班
                            fill_color = 'FFF2CC'  # 淺黃色
                        elif 'P3' in shift_code:  # P3班
                            fill_color = 'FCE4D6'  # 淺橙色
                        elif 'P4' in shift_code:  # P4班
                            fill_color = 'F4CCCC'  # 淺紅色
                        elif 'FC' in shift_code:  # FC班
                            fill_color = 'D0E0E3'  # 淺藍色
                        else:
                            fill_color = 'F2F2F2'  # 淺灰色
                        
                        cell = ws.cell(row=row, column=day_num, value=cell_value)
                        cell.fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type='solid')
                    else:
                        cell = ws.cell(row=row, column=day_num, value=date_str)
                        cell.fill = PatternFill(start_color='F8F9FA', end_color='F8F9FA', fill_type='solid')
                    
                    cell.font = Font(name='微軟正黑體', size=10)
                    cell.alignment = Alignment(horizontal='center', vertical='center')
                
                # 添加邊框
                ws.cell(row=row, column=day_num).border = thin_border
        
        # 為星期標題行也添加邊框
        for col in range(1, 8):
            ws.cell(row=start_row, column=col).border = thin_border
        
        # 設定欄位寬度
        for col in range(1, 8):
            ws.column_dimensions[chr(64 + col)].width = 12
        
        # 設定行高
        for row in range(start_row + 1, start_row + 1 + len(cal)):
            ws.row_dimensions[row].height = 40
        
        # 添加圖例說明
        legend_start_row = start_row + len(cal) + 2
        ws.cell(row=legend_start_row, column=1, value='班別說明:').font = Font(name='微軟正黑體', size=12, bold=True)
        
        # 取得該員工使用的班別類型
        used_shift_types = set()
        for schedule in schedules:
            used_shift_types.add((schedule.shift_type.code, schedule.shift_type.name))
        
        legend_row = legend_start_row + 1
        for i, (code, name) in enumerate(sorted(used_shift_types)):
            legend_cell = ws.cell(row=legend_row + i, column=1, value=f'{code}: {name}')
            legend_cell.font = Font(name='微軟正黑體', size=10)
        
        # 保存到BytesIO
        output = BytesIO()
        wb.save(output)
            
        output.seek(0)
        
        # 準備檔案名稱
        filename = f'{employee.name}_{year}年{month:02d}月_班表.xlsx'
        
        # 返回檔案下載
        from flask import send_file
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f'匯出錯誤: {e}')
        return jsonify({'error': str(e)}), 500

@main.route('/upload_excel', methods=['GET', 'POST'])
@require_admin
def upload_excel():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
            
            for _, row in df.iterrows():
                employee_name = row.get('姓名') or row.get('員工姓名')
                date_col = row.get('日期')
                shift_code = row.get('班別') or row.get('班次')
                
                if pd.isna(employee_name) or pd.isna(date_col) or pd.isna(shift_code):
                    continue
                
                employee = Employee.query.filter_by(name=employee_name).first()
                if not employee:
                    # 生成唯一的員工代碼
                    existing_count = Employee.query.count()
                    employee_code = f"EMP_{existing_count+1:03d}"
                    
                    # 確保代碼唯一性
                    while Employee.query.filter_by(employee_code=employee_code).first():
                        existing_count += 1
                        employee_code = f"EMP_{existing_count+1:03d}"
                    
                    employee = Employee(name=employee_name, employee_code=employee_code)
                    db.session.add(employee)
                    # 立即提交以避免重複代碼問題
                    try:
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        # 如果還是失敗，可能是姓名重複，使用現有員工
                        employee = Employee.query.filter_by(name=employee_name).first()
                        if not employee:
                            raise e
                
                shift_type = ShiftType.query.filter_by(code=shift_code).first()
                if not shift_type:
                    # 根據班別代碼設定預設時間和顏色
                    shift_name, start_time, end_time, color = get_shift_info(shift_code)
                    shift_type = ShiftType(
                        code=shift_code, 
                        name=shift_name, 
                        start_time=start_time, 
                        end_time=end_time,
                        color=color
                    )
                    db.session.add(shift_type)
                
                if isinstance(date_col, str):
                    schedule_date = datetime.strptime(date_col, '%Y-%m-%d').date()
                else:
                    schedule_date = date_col.date() if hasattr(date_col, 'date') else date_col
                
                existing_schedule = Schedule.query.filter_by(
                    date=schedule_date,
                    employee=employee
                ).first()
                
                if not existing_schedule:
                    schedule = Schedule(
                        date=schedule_date,
                        employee=employee,
                        shift_type=shift_type
                    )
                    db.session.add(schedule)
            
            db.session.commit()
            return redirect(url_for('main.calendar'))
    
    return render_template('upload.html')

def get_shift_info(shift_code):
    """根據班別代碼返回班別資訊"""
    from datetime import time
    
    # 休假相關
    if shift_code in ['H0', 'H1', 'H2']:
        return f'休假({shift_code})', time(0, 0), time(0, 0), '#6c757d'
    
    # 正常班別
    elif shift_code == 'FC':
        return 'FC班', time(9, 0), time(18, 0), '#007bff'
    
    # P班系列
    elif shift_code.startswith('P1'):
        return f'P1班({shift_code})', time(8, 0), time(17, 0), '#28a745'
    elif shift_code.startswith('P2'):
        return f'P2班({shift_code})', time(14, 0), time(23, 0), '#ffc107'
    elif shift_code.startswith('P3'):
        return f'P3班({shift_code})', time(17, 0), time(2, 0), '#fd7e14'
    elif shift_code.startswith('P4'):
        return f'P4班({shift_code})', time(20, 0), time(5, 0), '#dc3545'
    elif shift_code.startswith('P5'):
        return f'P5班({shift_code})', time(22, 0), time(7, 0), '#6f42c1'
    
    # 其他班別
    elif shift_code.startswith('N'):
        return f'N班({shift_code})', time(19, 0), time(4, 0), '#20c997'
    elif shift_code.startswith('E'):
        return f'E班({shift_code})', time(7, 0), time(16, 0), '#17a2b8'
    elif shift_code.startswith('C'):
        return f'C班({shift_code})', time(16, 0), time(1, 0), '#e83e8c'
    elif shift_code.startswith('R'):
        return f'R班({shift_code})', time(12, 0), time(21, 0), '#6610f2'
    elif shift_code in ['NT', 'CH']:
        return f'{shift_code}班', time(9, 0), time(18, 0), '#343a40'
    elif shift_code == 'FX':
        return 'FX班', time(10, 0), time(19, 0), '#495057'
    
    # 其他特殊班別
    else:
        return f'{shift_code}班', time(9, 0), time(18, 0), '#868e96'

@main.route('/employee/<int:employee_id>/schedule')
def employee_schedule(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    schedules = Schedule.query.filter_by(employee_id=employee_id).order_by(Schedule.date.desc()).all()
    today = date.today()
    
    return render_template('employee_schedule.html', employee=employee, schedules=schedules, today=today)

# ===== 管理員功能 =====

@main.route('/api/admin/pending-users')
@require_admin
def get_pending_users():
    """獲取待審核用戶列表"""
    try:
        pending_users = User.query.filter_by(status='pending').order_by(User.created_at.desc()).all()
        
        result = []
        for user in pending_users:
            result.append({
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'status': user.status,
                'created_at': user.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        print(f'獲取待審核用戶錯誤: {e}')
        return jsonify({'success': False, 'message': '獲取用戶列表失敗'}), 500

@main.route('/api/admin/approve-user', methods=['POST'])
@require_admin
def approve_user():
    """審核用戶"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': '請提供審核資料'}), 400
        
        user_id = data.get('userId')
        action = data.get('action')  # 'approve' or 'reject'
        
        if not user_id or action not in ['approve', 'reject']:
            return jsonify({'success': False, 'message': '無效的審核參數'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': '用戶不存在'}), 404
        
        if user.status != 'pending':
            return jsonify({'success': False, 'message': '用戶狀態不是待審核'}), 400
        
        # 更新用戶狀態
        if action == 'approve':
            user.status = 'approved'
            message = f'用戶 {user.name} 已審核通過'
        else:
            user.status = 'rejected'
            message = f'用戶 {user.name} 已被拒絕'
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        db.session.rollback()
        print(f'審核用戶錯誤: {e}')
        return jsonify({'success': False, 'message': '審核失敗'}), 500

@main.route('/api/admin/users')
@require_admin
def get_all_users():
    """獲取所有用戶列表"""
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        
        result = []
        for user in users:
            result.append({
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'role': user.role,
                'status': user.status,
                'failed_attempts': user.failed_attempts,
                'is_locked': user.is_locked(),
                'created_at': user.created_at.isoformat(),
                'updated_at': user.updated_at.isoformat() if user.updated_at else None
            })
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        print(f'獲取用戶列表錯誤: {e}')
        return jsonify({'success': False, 'message': '獲取用戶列表失敗'}), 500

@main.route('/api/admin/user/<int:user_id>/status', methods=['PUT'])
@require_admin
def update_user_status(user_id):
    """更新用戶狀態"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': '請提供狀態資料'}), 400
        
        new_status = data.get('status')
        
        if new_status not in ['pending', 'approved', 'rejected', 'disabled']:
            return jsonify({'success': False, 'message': '無效的狀態值'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': '用戶不存在'}), 404
        
        # 防止管理員修改自己的狀態
        current_user = get_current_user()
        if user.id == current_user.id:
            return jsonify({'success': False, 'message': '不能修改自己的狀態'}), 400
        
        user.status = new_status
        user.updated_at = datetime.utcnow()
        
        # 如果啟用用戶，重置失敗次數
        if new_status == 'approved':
            user.reset_failed_attempts()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'用戶狀態已更新為 {new_status}'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f'更新用戶狀態錯誤: {e}')
        return jsonify({'success': False, 'message': '更新失敗'}), 500

@main.route('/api/admin/user/<int:user_id>/unlock', methods=['POST'])
@require_admin
def unlock_user(user_id):
    """解鎖用戶帳號"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': '用戶不存在'}), 404
        
        user.reset_failed_attempts()
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'用戶 {user.name} 已解鎖'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f'解鎖用戶錯誤: {e}')
        return jsonify({'success': False, 'message': '解鎖失敗'}), 500

@main.route('/admin')
@require_admin
def admin_page():
    """管理員控制台頁面"""
    return render_template('admin.html')