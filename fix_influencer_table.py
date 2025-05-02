#!/usr/bin/env python3
"""
Comprehensive fix script for the influencer table.
This script will:
1. Back up your database first
2. Check the schema of the influencer table
3. Fix the missing password column if needed
4. Validate the fix
"""

import sqlite3
import os
import shutil
import sys
from datetime import datetime

DB_PATH = 'instance/db.sqlite3'

def backup_database():
    """Create a backup of the database before making changes"""
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}")
        return False
        
    # Create backups directory if it doesn't exist
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Create backup with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{backup_dir}/db_backup_{timestamp}.sqlite3"
    
    try:
        shutil.copy2(DB_PATH, backup_path)
        print(f"Database backed up successfully to {backup_path}")
        return True
    except Exception as e:
        print(f"Failed to create backup: {e}")
        return False

def check_table_schema(table_name):
    """Check the schema of a specific table"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if not cursor.fetchone():
            print(f"Table '{table_name}' does not exist in the database")
            conn.close()
            return False, []
            
        # Get schema
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print(f"\nSchema for table '{table_name}':")
        for col in columns:
            col_id, name, type_name, not_null, default_val, pk = col
            print(f"  Column {col_id}: {name} ({type_name}){' NOT NULL' if not_null else ''}{' PRIMARY KEY' if pk else ''}{f' DEFAULT {default_val}' if default_val is not None else ''}")
        
        column_names = [col[1] for col in columns]
        conn.close()
        return True, column_names
    except Exception as e:
        print(f"Error checking table schema: {e}")
        return False, []

def fix_missing_password_column():
    """Add the missing password column to the influencer table"""
    # First backup the database
    if not backup_database():
        print("Aborting operation due to failed backup")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if influencer table exists
        table_exists, columns = check_table_schema("influencer")
        if not table_exists:
            print("Cannot fix table: influencer table does not exist")
            conn.close()
            return False
            
        # Check if password column already exists
        if 'password' in columns:
            print("The password column already exists in the influencer table. No changes needed.")
            conn.close()
            return True
            
        # Add the missing column
        print("\nAdding 'password' column to the influencer table...")
        try:
            cursor.execute("ALTER TABLE influencer ADD COLUMN password VARCHAR(128) DEFAULT ''")
            conn.commit()
            print("Password column added successfully!")
        except sqlite3.OperationalError as e:
            print(f"SQLite error while adding column: {e}")
            conn.close()
            return False
        
        # Verify the changes were made
        _, updated_columns = check_table_schema("influencer")
        if 'password' in updated_columns:
            print("Verification successful: password column was added to the influencer table")
            conn.close()
            return True
        else:
            print("Verification failed: password column was not added successfully")
            conn.close()
            return False
    except Exception as e:
        print(f"Error during fix operation: {e}")
        return False

def recreate_influencer_table_if_needed():
    """Last resort option: recreate the entire influencer table with the correct schema"""
    # This is a more drastic approach and should be used only if the above method fails
    # Implementation would go here
    pass

if __name__ == "__main__":
    print("=" * 80)
    print("INFLUENCER TABLE FIX UTILITY")
    print("=" * 80)
    print("This script will fix the missing password column in the influencer table")
    print("A backup will be created before making any changes")
    
    print("\nChecking database...")
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}")
        sys.exit(1)
        
    try:
        result = fix_missing_password_column()
        
        if result:
            print("\nOperation completed successfully. The influencer table now has a password column.")
            print("You can now restart your application and it should work correctly.")
            sys.exit(0)
        else:
            print("\nOperation failed. Please check the error messages above.")
            sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)