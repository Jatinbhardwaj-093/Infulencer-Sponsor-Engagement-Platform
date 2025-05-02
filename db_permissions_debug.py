#!/usr/bin/env python3
"""
Database permissions diagnostic tool for macOS
"""
import os
import sys
import pwd
import grp
import stat
import sqlite3
import subprocess

def debug_permissions():
    """Print detailed information about database file and directory permissions"""
    print("=== Database Permissions Debug Tool ===\n")
    
    # Get the current user info
    current_uid = os.getuid()
    current_user = pwd.getpwuid(current_uid).pw_name
    print(f"Current user: {current_user} (UID: {current_uid})")
    
    # Get project path info
    project_dir = os.path.abspath(os.path.dirname(__file__))
    instance_dir = os.path.join(project_dir, 'instance')
    db_path = os.path.join(instance_dir, 'db.sqlite3')
    
    print(f"\nProject directory: {project_dir}")
    print(f"Instance directory: {instance_dir}")
    print(f"Database path: {db_path}")
    
    # Check if instance directory exists
    if not os.path.exists(instance_dir):
        print("\nInstance directory does not exist!")
        try:
            os.makedirs(instance_dir, mode=0o777)
            print(f"Created instance directory with full permissions (777)")
        except Exception as e:
            print(f"Failed to create instance directory: {e}")
            return False
    
    # Get instance directory permissions
    try:
        instance_stat = os.stat(instance_dir)
        instance_mode = instance_stat.st_mode
        instance_owner_id = instance_stat.st_uid
        instance_group_id = instance_stat.st_gid
        
        instance_owner = pwd.getpwuid(instance_owner_id).pw_name
        instance_group = grp.getgrgid(instance_group_id).gr_name
        
        print(f"\nInstance directory owner: {instance_owner} (UID: {instance_owner_id})")
        print(f"Instance directory group: {instance_group} (GID: {instance_group_id})")
        print(f"Instance directory permissions: {stat.filemode(instance_mode)} " +
              f"({oct(instance_mode & 0o777)[2:]})")
        
        # Check if current user has write access to instance directory
        if instance_owner_id == current_uid:
            print(f"✓ Current user owns the instance directory")
        elif (instance_mode & 0o002) != 0:  # Check if world-writable
            print(f"✓ Instance directory is world-writable")
        elif (instance_mode & 0o020) != 0 and current_user in grp.getgrnam(instance_group).gr_mem:
            print(f"✓ Current user is in the directory's group and has write permission")
        else:
            print(f"✗ Current user does not have write permission to the instance directory")
    except Exception as e:
        print(f"Error getting instance directory info: {e}")
    
    # Check database file
    if os.path.exists(db_path):
        try:
            db_stat = os.stat(db_path)
            db_mode = db_stat.st_mode
            db_owner_id = db_stat.st_uid
            db_group_id = db_stat.st_gid
            
            db_owner = pwd.getpwuid(db_owner_id).pw_name
            db_group = grp.getgrgid(db_group_id).gr_name
            
            print(f"\nDatabase file owner: {db_owner} (UID: {db_owner_id})")
            print(f"Database file group: {db_group} (GID: {db_group_id})")
            print(f"Database file permissions: {stat.filemode(db_mode)} " +
                  f"({oct(db_mode & 0o777)[2:]})")
            
            # Check if current user has write access to database file
            if db_owner_id == current_uid:
                print(f"✓ Current user owns the database file")
            elif (db_mode & 0o002) != 0:  # Check if world-writable
                print(f"✓ Database file is world-writable")
            elif (db_mode & 0o020) != 0 and current_user in grp.getgrnam(db_group).gr_mem:
                print(f"✓ Current user is in the file's group and has write permission")
            else:
                print(f"✗ Current user does not have write permission to the database file")
        except Exception as e:
            print(f"Error getting database file info: {e}")
    else:
        print(f"\nDatabase file does not exist!")
    
    # Test database connection
    print("\nAttempting to create a test database connection...")
    try:
        if os.path.exists(db_path):
            os.chmod(db_path, 0o666)  # Try to make it writable by everyone
            print(f"Updated database permissions to 666")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS test_connection (id INTEGER PRIMARY KEY)")
        cursor.execute("INSERT INTO test_connection (id) VALUES (1)")
        conn.commit()
        
        print("✅ Successfully connected to the database and created a test table!")
        conn.close()
    except sqlite3.OperationalError as e:
        print(f"❌ SQLite operational error: {e}")
    except Exception as e:
        print(f"❌ Error testing database connection: {e}")
    
    # Suggest fix based on findings
    print("\n=== Recommended Fix ===")
    print("Based on the diagnostics, try running the following commands:")
    print(f"sudo mkdir -p {instance_dir}")
    print(f"sudo chmod -R 777 {instance_dir}")
    print(f"sudo touch {db_path}")
    print(f"sudo chmod 666 {db_path}")
    print(f"sudo chown {current_user}:{grp.getgrgid(os.getgid()).gr_name} {db_path}")
    
    return True

if __name__ == "__main__":
    debug_permissions()