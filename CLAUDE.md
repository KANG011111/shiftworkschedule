# Claude Code Configuration

## Project Overview
Flask-based shift work schedule application with features for creating, managing, and exporting work schedules to JPG/ICS formats.

## Docker Commands
- `docker-compose up -d` - Start application in background
- `docker-compose down` - Stop application
- `docker-compose build` - Build application image
- `docker-compose restart` - Restart application
- `docker-compose logs -f` - View application logs

## Python Commands
- `python run.py` - Start development server locally
- `pip install -r requirements.txt` - Install dependencies

## Key Directories
- `app/` - Flask application source code
- `app/templates/` - HTML templates
- `app/models.py` - Database models
- `app/routes.py` - Application routes and API endpoints
- `static/` - Static assets (CSS, JS, images)
- `testcsv/` - Test data files
- `shiftpreview/` - JPG output directory
- `instance/` - SQLite database directory

## Database
- SQLite database: `instance/shift_schedule.db`
- Models: Employee, Schedule, ShiftType, Group
- Auto-initialization with test data

## API Endpoints
- `/api/preview_schedule` - Get schedule preview data for JPG export
- `/api/preview_schedule_by_id` - Get schedule by employee ID
- `/api/export_ics` - Export schedule to ICS calendar format
- `/upload_excel` - Upload Excel schedule files
- `/upload_new` - New version Excel upload with validation

## Test Environment
- **System URL:** http://localhost:5001/
- **Admin Login:** admin / admin123
- **Test Data:** 321 records for September 2025 (民國114年9月)
- **Test Employees:** 賴秉宏(8652), 李惟綱(8312), 李家瑋(8512), 王志忠(0450), 胡翊潔(8619), 朱家德(8835)

## Recent Updates (2025-09-08)

### JPG Export Calendar Format Fix
**Problem:** Date alignment in JPG exports was incorrect - September 1st (Monday) was showing under Sunday column.

**Solution:** Implemented traditional calendar format (Sunday-first):
- **Backend:** Modified `app/routes.py` to use `calendar.SUNDAY` mode in all `calendar.monthcalendar()` calls
- **Frontend:** Updated `app/templates/export.html` weekdays array to `['日', '一', '二', '三', '四', '五', '六']`

**Files Modified:**
- `app/routes.py` (3 locations): Added `calendar.setfirstweekday(calendar.SUNDAY)` before calendar generation
- `app/templates/export.html` (line 405): Fixed weekdays array order

**Verification:** 
- ✅ September 1, 2025 (Monday) now correctly displays in Monday column with Sunday column blank
- ✅ All months 2025-2027 tested and working correctly
- ✅ Cross-year functionality fully supported

## Testing Instructions
1. Access system at http://localhost:5001/
2. Login with admin/admin123
3. Navigate to "一鍵匯出月大表" (JPG Export)
4. Test with employee "李惟綱" or "8312" for 2025年9月
5. Verify September 1st appears in Monday column
6. Download JPG and confirm calendar alignment

## Notes
- Follow existing Flask patterns and conventions
- Ensure proper error handling in all routes
- All calendar operations use Sunday-first format for consistency
- Test data automatically loads on application startup
- Docker container includes all dependencies and configurations