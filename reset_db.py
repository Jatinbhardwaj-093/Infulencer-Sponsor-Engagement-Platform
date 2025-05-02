#!/usr/bin/env python3
"""
Reset Database Script - Fixes SQLite 'unable to open database file' error
This script removes the existing database file and creates a new one with the proper schema.
"""
import os
import shutil
import sqlite3
from pathlib import Path
import sys
from werkzeug.security import generate_password_hash

def reset_database():
    """Reset the database by creating a fresh file with proper permissions"""
    # Get project directory path
    project_dir = os.path.abspath(os.path.dirname(__file__))
    instance_dir = os.path.join(project_dir, 'instance')
    db_path = os.path.join(instance_dir, 'db.sqlite3')
    
    print(f"Project directory: {project_dir}")
    print(f"Instance directory: {instance_dir}")
    print(f"Database path: {db_path}")
    
    # Step 1: Make sure instance directory exists with correct permissions
    try:
        print("\nChecking instance directory...")
        if os.path.exists(instance_dir):
            print(f"Instance directory exists, checking if writable...")
            if not os.access(instance_dir, os.W_OK):
                print(f"Instance directory not writable, fixing permissions...")
                try:
                    os.chmod(instance_dir, 0o755)
                    print("Set directory permissions to 755")
                except:
                    print("Could not set directory permissions, trying to recreate directory...")
                    shutil.rmtree(instance_dir)
                    os.makedirs(instance_dir, mode=0o755)
                    print("Recreated instance directory with 755 permissions")
        else:
            print(f"Instance directory does not exist, creating...")
            os.makedirs(instance_dir, mode=0o755)
            print(f"Created instance directory with 755 permissions")
    except Exception as e:
        print(f"Error managing instance directory: {e}")
        return False
        
    # Step 2: Delete existing database if it exists
    try:
        print("\nPreparing database file...")
        if os.path.exists(db_path):
            print(f"Removing existing database file...")
            try:
                os.remove(db_path)
                print("Existing database removed")
            except Exception as e:
                print(f"Error removing database: {e}")
                print("Trying to recover...")
                # Try to change permissions before removing
                try:
                    os.chmod(db_path, 0o666)
                    os.remove(db_path)
                    print("Recovery successful")
                except:
                    print("Recovery failed. Please try running this script with administrator privileges.")
                    return False
    except Exception as e:
        print(f"Error preparing database: {e}")
        return False
    
    # Step 3: Create a fresh database file
    try:
        print("\nCreating new database file...")
        # Create empty database file
        conn = sqlite3.connect(db_path)
        print("Created empty database file")
        
        # Set database file permissions
        os.chmod(db_path, 0o666)
        print("Set database file permissions to 666 (readable/writable by all)")
        
        # Create the basic schema for authentication
        print("Creating basic schema...")
        cursor = conn.cursor()
        
        # Admin table
        cursor.execute('''
        CREATE TABLE admin (
            admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Influencer table
        cursor.execute('''
        CREATE TABLE influencer (
            influencer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            genre TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            popularity TEXT NOT NULL,
            platform TEXT NOT NULL,
            bio TEXT,
            flag TEXT DEFAULT 'no',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
        ''')
        
        # Sponsor table
        cursor.execute('''
        CREATE TABLE sponsor (
            sponsor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            industry TEXT NOT NULL,
            company_name TEXT,
            website TEXT,
            email TEXT NOT NULL UNIQUE,
            flag TEXT DEFAULT 'no',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
        ''')
        
        # Create default admin user
        admin_password_hash = generate_password_hash('admin')
        cursor.execute('''
        INSERT INTO admin (username, password, email) VALUES (?, ?, ?)
        ''', ('admin', admin_password_hash, 'admin@example.com'))
        
        conn.commit()
        conn.close()
        print("Schema created and default admin user added!")
        
        # Test the database
        test_conn = sqlite3.connect(db_path)
        cursor = test_conn.cursor()
        cursor.execute("SELECT username FROM admin WHERE username = 'admin'")
        result = cursor.fetchone()
        if result and result[0] == 'admin':
            print("Database test successful!")
        else:
            print("Database test failed!")
        test_conn.close()
        
        return True
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

if __name__ == '__main__':
    print("Starting database reset process...\n")
    
    success = reset_database()
    
    if success:
        print("\n✅ Database has been successfully reset!")
        print("You should now be able to log in with the following credentials:")
        print("  Username: admin")
        print("  Password: admin")
        print("\nThe login/register functionality should now work correctly.")
    else:
        print("\n❌ Database reset failed.")
        print("Please check the error messages above and try again.")
        print("You might need to run this script with administrator privileges.")