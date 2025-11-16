"""
Clean database reset script.
This will:
1. Delete the SQLite database file
2. Delete all migration files (except __init__.py)
3. Create fresh migrations
4. Run migrations
"""
import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def delete_migration_files():
    """Delete all migration files except __init__.py"""
    apps = [
        'authentification',
        'profiles',
        'ProfileCategory',
        'ProfileDomain',
        'ProfileItem',
        'goals',
        'notes',
        'strategies',
        'termdecondition',
    ]
    
    deleted_count = 0
    for app in apps:
        migrations_dir = BASE_DIR / app / 'migrations'
        if migrations_dir.exists():
            for file in migrations_dir.iterdir():
                if file.is_file() and file.name != '__init__.py' and file.suffix == '.py':
                    file.unlink()
                    deleted_count += 1
                    print(f"  Deleted: {file}")
    
    return deleted_count

def main():
    print("=== Database Reset Script ===\n")
    
    # Step 1: Delete database
    db_file = BASE_DIR / 'db.sqlite3'
    if db_file.exists():
        print(f"1. Deleting database file: {db_file}")
        db_file.unlink()
        print("   ✓ Database deleted\n")
    else:
        print("1. Database file not found (already deleted?)\n")
    
    # Step 2: Delete migration files
    print("2. Deleting migration files...")
    deleted = delete_migration_files()
    print(f"   ✓ Deleted {deleted} migration files\n")
    
    print("=== Next Steps ===")
    print("Run these commands:")
    print("  python manage.py makemigrations")
    print("  python manage.py migrate")
    print("\nThis will create fresh migrations and set up the database.")

if __name__ == '__main__':
    response = input("This will DELETE your database and all migration files. Continue? (yes/no): ")
    if response.lower() == 'yes':
        main()
    else:
        print("Cancelled.")

