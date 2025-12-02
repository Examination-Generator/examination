# cPanel Backend Setup Instructions

## ⚠️ CRITICAL: Application Root Path

**You MUST use `public_html/api` as the Application Root** - NOT just `api`

If you use just `api`, cPanel will create the app in `/home/zbhxqeap/api` instead of `/home/zbhxqeap/public_html/api`, and the deployed code won't work.

---

## Setup Python App via cPanel

### Step 1: Create Python Application

1. **Login to cPanel** at https://speedstarexams.co.ke:2083
2. **Navigate to**: Software → **Setup Python App**
3. **Click "CREATE APPLICATION"**
4. **Configure with EXACT values:**
   ```
   Python Version:           3.12.x (recommended) or 3.11.x
   Application Root:         public_html/api
   Application URL:          speedstarexams.co.ke/api
   Application Startup File: passenger_wsgi.py
   Application Entry Point:  application
   ```

⚠️ **Important**: 
- Application Root must be `public_html/api` (full path)
- This matches where GitHub deployment pushes the code

5. **After creating**, the app will provide you with:
   - Virtual environment path (usually `public_html/api/venv`)
   - Command to activate the venv

6. **Click "Terminal" button** in the Python App interface and run:
   ```bash
   source /home/zbhxqeap/public_html/api/venv/bin/activate
   pip install -r /home/zbhxqeap/public_html/api/requirements.txt
   ```

7. **Create `.env` file** in `/home/zbhxqeap/public_html/api/`:
   ```bash
   cd /home/zbhxqeap/public_html/api
   cat > .env << 'EOF'
   SECRET_KEY=your-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=speedstarexams.co.ke,51.91.24.182
   DATABASE_URL=postgresql://zbhxqeap_editor:TesterK&700@localhost:5432/zbhxqeap_exam
   CORS_ALLOWED_ORIGINS=https://speedstarexams.co.ke
   EOF
   ```

8. **Run migrations**:
   ```bash
   cd /home/zbhxqeap/public_html/api
   source venv/bin/activate
   python manage.py migrate --settings=examination_system.settings_production
   python manage.py collectstatic --noinput --settings=examination_system.settings_production
   ```

9. **Restart the application** in the Python App interface

### Option 2: Manual .htaccess Configuration

If cPanel doesn't have Python App interface, the `.htaccess` file is already configured. Just ensure:

1. **Passenger is enabled** (contact hosting support if needed)
2. **Python version is set** to 3.11 or higher
3. **Virtual environment exists** at `public_html/api/venv/`
4. **Dependencies are installed** in the venv

### Verify Backend is Working

After setup, test:
```bash
curl https://speedstarexams.co.ke/api/
```

Should return Django API response, not the React frontend.

### Troubleshooting

**If you still see React frontend:**
- Passenger might not be loading `passenger_wsgi.py`
- Check cPanel Error Logs (Metrics → Errors)
- Ensure `passenger_wsgi.py` has correct permissions (755)
- Contact hosting support about Passenger Python configuration

**Database connection errors:**
- Verify PostgreSQL credentials in `.env`
- Test connection: `psql -U zbhxqeap_editor -d zbhxqeap_exam -h localhost`
- Check if PostgreSQL allows local connections

**Module import errors:**
- Activate venv and reinstall: `pip install -r requirements.txt`
- Check Python version matches requirements
