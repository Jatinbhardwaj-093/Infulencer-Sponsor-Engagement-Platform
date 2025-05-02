#!/usr/bin/env python3
"""
Simple database fix script that addresses the 'unable to open database file' error.
This creates the instance directory, sets proper permissions, and creates a fresh database file.
"""
import os
import sqlite3
import sys
import stat

def fix_db():
    print("Starting simple database fix...")
    
    # Get the root directory
    root_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Project directory: {root_dir}")
    
    # Create instance directory with permissive permissions
    instance_dir = os.path.join(root_dir, 'instance')
    print(f"Instance directory path: {instance_dir}")
    
    try:
        # Create directory if not exists
        if not os.path.exists(instance_dir):
            os.makedirs(instance_dir)
            print(f"Created instance directory: {instance_dir}")
        
        # Set permissions that allow everyone to read/write
        os.chmod(instance_dir, 0o777)  # Full permissions for everyone
        print(f"Set instance directory permissions to 777")
    except Exception as e:
        print(f"Error managing instance directory: {e}")
        return False

    # Database file path
    db_path = os.path.join(instance_dir, 'db.sqlite3')
    print(f"Database file path: {db_path}")
    
    # Create or reset database file
    try:
        # Create a new database connection (creates file if not exists)
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Create a test table to verify write access
        conn.execute("CREATE TABLE IF NOT EXISTS test_connection (id INTEGER PRIMARY KEY)")
        conn.execute("INSERT INTO test_connection (id) VALUES (1)")
        conn.commit()
        
        # Test reading
        result = conn.execute("SELECT id FROM test_connection WHERE id = 1").fetchone()
        if result and result[0] == 1:
            print("Database connection test successful!")
        
        conn.close()
        
        # Set permissive permissions on database file
        os.chmod(db_path, 0o666)  # Read/write for all users
        print("Set database file permissions to 666")
        
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False

if __name__ == "__main__":
    success = fix_db()
    if success:
        print("\nDatabase connection issue has been fixed!")
        print("Try logging in again, or run 'python rebuild_db.py' to rebuild tables.")
    else:
        print("\nFailed to fix database issue.")
        print("Troubleshooting tips:")
        print("1. Check if you have permissions to write to the directory")
        print("2. Make sure no other process is using the database file")
        print("3. Try running the script with sudo if on macOS/Linux")