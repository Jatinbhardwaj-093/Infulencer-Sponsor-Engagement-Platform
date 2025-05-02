#!/usr/bin/env python3
"""
macOS-specific fix for SQLite 'unable to open database file' error
"""
import os
import subprocess
import sys

# Get the absolute path to the project directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the instance directory and database path
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
DB_PATH = os.path.join(INSTANCE_DIR, 'db.sqlite3')

print(f"Project directory: {BASE_DIR}")
print(f"Instance directory: {INSTANCE_DIR}")
print(f"Database path: {DB_PATH}")

# Step 1: Make sure the instance directory exists
if not os.path.exists(INSTANCE_DIR):
    print("Creating instance directory...")
    try:
        os.makedirs(INSTANCE_DIR)
        print("✅ Instance directory created successfully!")
    except Exception as e:
        print(f"❌ Error creating instance directory: {e}")
        sys.exit(1)
else:
    print("✅ Instance directory already exists")

# Step 2: Fix permissions for the current user (common macOS issue)
print("\nFixing directory permissions...")
try:
    # Get current user
    current_user = os.environ.get('USER', 'unknown')
    print(f"Current user: {current_user}")
    
    # Take ownership of the instance directory (macOS approach)
    subprocess.run(['sudo', 'chown', '-R', current_user, INSTANCE_DIR], check=True)
    print(f"✅ Changed ownership of {INSTANCE_DIR} to {current_user}")
    
    # Set permissive permissions
    subprocess.run(['sudo', 'chmod', '-R', '755', INSTANCE_DIR], check=True)
    print(f"✅ Set permissions on {INSTANCE_DIR} to 755")
except subprocess.SubprocessError as e:
    print(f"❌ Error fixing permissions: {e}")
    print("Warning: This script needs sudo permissions to fix ownership issues.")
    print("Try running it with sudo if you have administrator privileges.")
    
# Step 3: Test database creation
print("\nTesting database creation...")
import sqlite3
try:
    # Delete existing database if it exists to start fresh
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"✅ Removed existing database file")
    
    # Create new database file
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO test (name) VALUES ('Test successful')")
    conn.commit()
    
    # Verify it worked
    cursor.execute("SELECT name FROM test LIMIT 1")
    result = cursor.fetchone()
    if result and result[0] == 'Test successful':
        print("✅ Database creation and testing successful!")
    conn.close()
    
    # Fix database file permissions
    subprocess.run(['sudo', 'chmod', '666', DB_PATH], check=True)
    print(f"✅ Set database file permissions to 666 (readable/writable by all)")
except sqlite3.Error as e:
    print(f"❌ SQLite error: {e}")
    sys.exit(1)
except subprocess.SubprocessError as e:
    print(f"❌ Error setting permissions: {e}")
    print("Note: The database was created but permissions may not be optimal.")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)

print("\n✅ Database setup complete!")
print("You should now be able to run your Flask application without the 'unable to open database file' error.")
print("To initialize the application schema, run 'python rebuild_db.py'")