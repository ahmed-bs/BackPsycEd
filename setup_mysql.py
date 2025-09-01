#!/usr/bin/env python3
"""
MySQL Database Setup Script for PsychoEducatif

This script helps you set up the MySQL database for your Django project.
Run this script after installing MySQL and before running Django migrations.
"""

import mysql.connector
from mysql.connector import Error

def create_database():
    """Create the MySQL database and user for the project."""
    
    # MySQL root connection (you'll need to provide the root password)
    root_password = input("Enter MySQL root password (or press Enter if none): ").strip()
    
    try:
        # Connect to MySQL server
        if root_password:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password=root_password
            )
        else:
            connection = mysql.connector.connect(
                host="localhost",
                user="root"
            )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database
            cursor.execute("CREATE DATABASE IF NOT EXISTS PsychoEducatif CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("✅ Database 'PsychoEducatif' created successfully!")
            
            # Create user (optional - you can use root if preferred)
            create_user = input("Do you want to create a dedicated user? (y/n): ").lower().strip()
            
            if create_user == 'y':
                username = input("Enter username (default: psycho_user): ").strip() or "psycho_user"
                password = input("Enter password (default: admin123): ").strip() or "admin123"
                
                cursor.execute(f"CREATE USER IF NOT EXISTS '{username}'@'localhost' IDENTIFIED BY '{password}'")
                cursor.execute(f"GRANT ALL PRIVILEGES ON PsychoEducatif.* TO '{username}'@'localhost'")
                cursor.execute("FLUSH PRIVILEGES")
                print(f"✅ User '{username}' created and granted privileges!")
                
                # Update settings.py with new credentials
                print("\n📝 Update your backend/settings.py with these credentials:")
                print(f"USER: '{username}'")
                print(f"PASSWORD: '{password}'")
            
            print("\n🎉 MySQL database setup completed!")
            print("\nNext steps:")
            print("1. Install the new requirements: pip install -r requirements.txt")
            print("2. Run Django migrations: python manage.py migrate")
            print("3. Create a superuser: python manage.py createsuperuser")
            
    except Error as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("- Make sure MySQL is running")
        print("- Check if the root password is correct")
        print("- Ensure MySQL server is accessible on localhost:3306")
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("🚀 MySQL Database Setup for PsychoEducatif")
    print("=" * 50)
    create_database() 