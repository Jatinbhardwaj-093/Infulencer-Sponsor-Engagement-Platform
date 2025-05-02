#!/usr/bin/env python3

"""
Simple standalone script to add the missing password column to the influencer table.
This script uses only SQLite operations and doesn't depend on Flask or SQLAlchemy.
"""

import sqlite3
import os
import sys

def fix_password_column():
    db_path = 'instance/db.sqlite3'
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the influencer table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='influencer'")
        if not cursor.fetchone():
            print("Error: The 'influencer' table doesn't exist in the database")
            conn.close()
            return False
        
        # Get current columns in the influencer table
        cursor.execute("PRAGMA table_info(influencer)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Check if password column already exists
        if 'password' in columns:
            print("The password column already exists in the influencer table")
            conn.close()
            return True
        
        # Add the missing password column
        print("Adding missing 'password' column to influencer table...")
        cursor.execute("ALTER TABLE influencer ADD COLUMN password VARCHAR(128) DEFAULT ''")
        conn.commit()
        
        # Verify the column was added successfully
        cursor.execute("PRAGMA table_info(influencer)")
        new_columns = [col[1] for col in cursor.fetchall()]
        
        if 'password' in new_columns:
            print("Success! Password column added to the influencer table.")
            conn.close()
            return True
        else:
            print("Error: Failed to verify the password column was added")
            conn.close()
            return False
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    try:
        result = fix_password_column()
        if result:
            print("Database fix completed successfully")
            sys.exit(0)
        else:
            print("Database fix failed")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)