import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Check key tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [t[0] for t in cursor.fetchall()]

print("=== Database State Check ===\n")
print(f"Total tables: {len(tables)}\n")

# Check for auth_user
has_auth_user = 'auth_user' in tables
has_customuser = 'authentification_customuser' in tables

print(f"auth_user table: {'✓ EXISTS' if has_auth_user else '✗ MISSING'}")
print(f"authentification_customuser table: {'✓ EXISTS' if has_customuser else '✗ MISSING'}")

if has_auth_user:
    cursor.execute("SELECT COUNT(*) FROM auth_user")
    count = cursor.fetchone()[0]
    print(f"  - Records in auth_user: {count}")

# Check migration state
cursor.execute("SELECT app, name FROM django_migrations WHERE app='authentification'")
auth_migrations = cursor.fetchall()
print(f"\nAuthentification migrations in database: {len(auth_migrations)}")
for app, name in auth_migrations:
    print(f"  - {app}.{name}")

conn.close()

