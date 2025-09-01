# MySQL Migration Guide for PsychoEducatif

This guide will help you migrate your Django project from PostgreSQL to MySQL.

## Prerequisites

1. **Install MySQL Server**
   - Download and install MySQL Server from [mysql.com](https://dev.mysql.com/downloads/mysql/)
   - Or use XAMPP/WAMP for Windows
   - Ensure MySQL service is running

2. **Install MySQL Connector for Python**
   ```bash
   pip install mysqlclient PyMySQL
   ```

## Step-by-Step Migration

### 1. Install New Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up MySQL Database
Run the setup script:
```bash
python setup_mysql.py
```

This script will:
- Create the `PsychoEducatif` database
- Optionally create a dedicated user
- Set proper character encoding (utf8mb4)

### 3. Update Database Credentials (if needed)
If you created a custom user, update `backend/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'PsychoEducatif',
        'USER': 'your_username',  # Update this
        'PASSWORD': 'your_password',  # Update this
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}
```

### 4. Backup Existing Data (if needed)
If you have important data in your current database:
```bash
# Export data from current database
python manage.py dumpdata > backup_data.json
```

### 5. Remove Old Database Files
```bash
# Remove SQLite database (if using SQLite)
rm db.sqlite3

# Remove PostgreSQL database (if using PostgreSQL)
# Use pgAdmin or psql to drop the database
```

### 6. Run Django Migrations
```bash
# Create new migration files
python manage.py makemigrations

# Apply migrations to MySQL
python manage.py migrate
```

### 7. Create Superuser
```bash
python manage.py createsuperuser
```

### 8. Restore Data (if needed)
If you backed up data:
```bash
python manage.py loaddata backup_data.json
```

## Configuration Details

### Database Settings
The new MySQL configuration includes:
- **Engine**: `django.db.backends.mysql`
- **Character Set**: `utf8mb4` (supports full Unicode including emojis)
- **SQL Mode**: `STRICT_TRANS_TABLES` (ensures data integrity)

### PyMySQL Configuration
The settings file now includes:
```python
import pymysql
pymysql.install_as_MySQLdb()
```

This ensures compatibility between PyMySQL and Django's MySQL backend.

## Troubleshooting

### Common Issues

1. **Connection Error**
   - Ensure MySQL service is running
   - Check host/port settings
   - Verify username/password

2. **Character Encoding Issues**
   - Database is configured with `utf8mb4`
   - Tables will inherit this encoding

3. **Migration Errors**
   - Check MySQL version compatibility
   - Ensure proper permissions for the database user

4. **PyMySQL Installation Issues**
   - On Windows, you might need Visual C++ build tools
   - Alternative: Use `mysqlclient` instead

### Alternative MySQL Client
If you encounter issues with `mysqlclient`, you can use `PyMySQL`:
```python
# In settings.py, replace the ENGINE line with:
'ENGINE': 'django.db.backends.mysql',
```

## Testing the Migration

1. **Start Django Server**
   ```bash
   python manage.py runserver
   ```

2. **Check Admin Interface**
   - Visit `http://localhost:8000/admin/`
   - Login with your superuser credentials

3. **Verify Data**
   - Check if your models are working
   - Test CRUD operations

## Performance Considerations

- MySQL performs well with Django
- Consider adding database indexes for frequently queried fields
- Monitor query performance using Django Debug Toolbar

## Rollback Plan

If you need to revert to PostgreSQL:
1. Restore the original `settings.py`
2. Reinstall `psycopg2`
3. Restore your PostgreSQL database
4. Run migrations again

## Support

For MySQL-specific issues:
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Django MySQL Documentation](https://docs.djangoproject.com/en/stable/ref/databases/#mysql-notes)
- [PyMySQL Documentation](https://pymysql.readthedocs.io/)

---

**Note**: This migration will create a fresh database. Make sure to backup any important data before proceeding. 