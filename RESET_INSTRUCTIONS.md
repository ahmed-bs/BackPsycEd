# Database Reset Instructions

## Option 1: Quick Reset (Recommended if you have no important data)

1. **Delete the database:**
   ```powershell
   Remove-Item db.sqlite3
   ```

2. **Delete all migration files** (except `__init__.py`):
   ```powershell
   # Run the reset script
   python reset_database.py
   ```
   Or manually delete migration files in each app's `migrations/` folder (keep `__init__.py`)

3. **Create fresh migrations:**
   ```powershell
   python manage.py makemigrations
   ```

4. **Run migrations:**
   ```powershell
   python manage.py migrate
   ```

5. **Create a superuser (optional):**
   ```powershell
   python manage.py createsuperuser
   ```

## Option 2: Keep Data, Fix Migrations

If you have important data and want to keep it:

1. **Backup your database:**
   ```powershell
   Copy-Item db.sqlite3 db.sqlite3.backup
   ```

2. **Check current state:**
   ```powershell
   python manage.py showmigrations
   python check_db_state.py
   ```

3. **Try to fix without reset:**
   - The `auth_user` table already exists and works
   - Test if the server works: `python manage.py runserver`
   - If errors persist, then do Option 1

## Current Status

- ✓ Database file exists
- ✓ `auth_user` table exists (6 users)
- ✓ All migrations show as applied
- ✓ CustomUser model works

If the server still shows errors, the issue might be elsewhere (not the database).

