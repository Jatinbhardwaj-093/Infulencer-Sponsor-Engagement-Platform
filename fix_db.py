#!/usr/bin/env python3
"""
Database Fix Tool for Influencer Engagement Platform

This script resolves common database connection issues by:
1. Ensuring the instance directory exists with proper permissions
2. Creating/fixing the database file with proper permissions
3. Verifying database connection
"""
import os
import sys
import sqlite3
import shutil
from pathlib import Path
import stat
import click
from datetime import datetime
from sqlalchemy.exc import OperationalError, ProgrammingError, IntegrityError
from werkzeug.security import generate_password_hash

from app import create_app, db
from models import Admin, Influencer, Sponsor, Campaign, InfluencerAdRequest, SponsorRequest, Img, Notification

def fix_database_permissions():
    """Fix database directory and file permissions"""
    print("Starting database connection fix...")
    
    # Get the base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define instance directory path
    instance_dir = os.path.join(base_dir, 'instance')
    print(f"Instance directory path: {instance_dir}")
    
    # Remove and recreate instance directory
    if os.path.exists(instance_dir):
        print(f"Removing existing instance directory at {instance_dir}")
        try:
            shutil.rmtree(instance_dir)
        except Exception as e:
            print(f"Error removing instance directory: {e}")
            print(f"Attempting to fix permissions on existing files...")
            
            # Try to fix permissions on existing files
            for root, dirs, files in os.walk(instance_dir):
                for d in dirs:
                    try:
                        os.chmod(os.path.join(root, d), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
                    except Exception as e:
                        print(f"Could not change permissions on directory {d}: {e}")
                
                for f in files:
                    try:
                        os.chmod(os.path.join(root, f), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
                    except Exception as e:
                        print(f"Could not change permissions on file {f}: {e}")
    
    # Create instance directory with permissive permissions
    try:
        os.makedirs(instance_dir, exist_ok=True)
        os.chmod(instance_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        print(f"Created instance directory with full permissions (777)")
    except Exception as e:
        print(f"Error creating instance directory: {e}")
        return False
    
    # Define database file path
    db_path = os.path.join(instance_dir, 'db.sqlite3')
    print(f"Database file path: {db_path}")
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Removed existing database file")
        except Exception as e:
            print(f"Error removing existing database file: {e}")
            return False
    
    # Create a new empty database file
    try:
        # Create empty database
        conn = sqlite3.connect(db_path)
        conn.close()
        print("Created new empty database file")
        
        # Set permissions to be as permissive as possible
        os.chmod(db_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)  # 0666
        print("Set database file permissions to 666 (readable/writable by all)")
        
        # Test database connection
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY)")
        conn.commit()
        conn.close()
        print("Successfully tested database connection")
        
        return True
    except Exception as e:
        print(f"Error creating database file: {e}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Current user: {os.getuid()}")
        return False

if __name__ == "__main__":
    success = fix_database_permissions()
    
    if success:
        print("\nDatabase permissions successfully fixed!")
        print("Next steps:")
        print("1. Run 'python rebuild_db.py' to initialize the database schema")
        print("2. Restart your Flask application")
    else:
        print("\nFailed to fix database permissions.")
        print("You may need to run this script with elevated permissions or check system file permissions.")

# Create Flask app with database connection
app = create_app()

@click.command()
@click.option('--check-only', is_flag=True, help='Only check for issues without fixing them')
@click.option('--verbose', is_flag=True, help='Show detailed information about fixes')
def fix_database(check_only, verbose):
    """Check and fix database issues."""
    click.echo("Analyzing database structure...")
    
    with app.app_context():
        issues_found = False
        
        # Use a connection to execute raw SQL when needed
        connection = db.engine.connect()
        
        # Check if tables exist
        tables_to_check = [
            'admin', 'influencer', 'sponsor', 'campaign', 
            'influencer_ad_request', 'sponsor_request', 
            'img', 'notification'
        ]
        
        missing_tables = []
        for table in tables_to_check:
            try:
                result = connection.execute(f"SELECT 1 FROM {table} LIMIT 1")
                if verbose:
                    click.echo(f"Table '{table}' exists.")
            except (OperationalError, ProgrammingError):
                missing_tables.append(table)
                issues_found = True
                click.echo(f"Table '{table}' is missing.")
        
        # Check for empty passwords in influencer table
        try:
            # Check if password column exists first
            try:
                connection.execute("SELECT password FROM influencer LIMIT 1")
                
                # Check for NULL or empty password
                result = connection.execute(
                    "SELECT influencer_id, username FROM influencer WHERE password IS NULL OR password = ''"
                )
                empty_passwords = result.fetchall()
                
                if empty_passwords:
                    issues_found = True
                    click.echo(f"Found {len(empty_passwords)} influencers with empty passwords.")
                    
                    if not check_only:
                        click.echo("Setting temporary passwords...")
                        for user_id, username in empty_passwords:
                            temp_password = generate_password_hash('password123')
                            connection.execute(
                                f"UPDATE influencer SET password = '{temp_password}' WHERE influencer_id = {user_id}"
                            )
                            if verbose:
                                click.echo(f"Set temporary password for {username}")
            
            except (OperationalError, ProgrammingError):
                issues_found = True
                click.echo("Password column is missing in the influencer table.")
                
                if not check_only:
                    click.echo("Adding password column...")
                    try:
                        connection.execute(
                            "ALTER TABLE influencer ADD COLUMN password VARCHAR(128) NOT NULL DEFAULT ''"
                        )
                        click.echo("Password column added.")
                        
                        # Set temporary passwords for all influencers
                        temp_password = generate_password_hash('password123')
                        connection.execute(
                            f"UPDATE influencer SET password = '{temp_password}'"
                        )
                        click.echo("Temporary passwords set for all influencers.")
                    except Exception as e:
                        click.echo(f"Error adding password column: {str(e)}")
        
        except Exception as e:
            click.echo(f"Error checking influencer passwords: {str(e)}")
        
        # Check for inconsistent foreign keys
        try:
            # Check influencer_ad_request table
            result = connection.execute("""
                SELECT iar.influencer_request_id, iar.influencer_id, iar.campaign_id
                FROM influencer_ad_request iar
                LEFT JOIN influencer i ON iar.influencer_id = i.influencer_id
                LEFT JOIN campaign c ON iar.campaign_id = c.campaign_id
                WHERE i.influencer_id IS NULL OR c.campaign_id IS NULL
            """)
            
            invalid_ad_requests = result.fetchall()
            if invalid_ad_requests:
                issues_found = True
                click.echo(f"Found {len(invalid_ad_requests)} invalid influencer ad requests with missing references.")
                
                if not check_only:
                    for request_id, inf_id, camp_id in invalid_ad_requests:
                        click.echo(f"Deleting invalid request ID {request_id} (influencer_id={inf_id}, campaign_id={camp_id})")
                        connection.execute(f"DELETE FROM influencer_ad_request WHERE influencer_request_id = {request_id}")
        
        except Exception as e:
            click.echo(f"Error checking influencer_ad_request references: {str(e)}")
        
        # Check for invalid sponsor requests
        try:
            result = connection.execute("""
                SELECT sr.sponsor_request_id, sr.sponsor_id, sr.influencer_id, sr.campaign_id
                FROM sponsor_request sr
                LEFT JOIN sponsor s ON sr.sponsor_id = s.sponsor_id
                LEFT JOIN influencer i ON sr.influencer_id = i.influencer_id
                LEFT JOIN campaign c ON sr.campaign_id = c.campaign_id
                WHERE s.sponsor_id IS NULL OR i.influencer_id IS NULL OR c.campaign_id IS NULL
            """)
            
            invalid_sponsor_requests = result.fetchall()
            if invalid_sponsor_requests:
                issues_found = True
                click.echo(f"Found {len(invalid_sponsor_requests)} invalid sponsor requests with missing references.")
                
                if not check_only:
                    for request_id, sponsor_id, inf_id, camp_id in invalid_sponsor_requests:
                        click.echo(f"Deleting invalid sponsor request ID {request_id}")
                        connection.execute(f"DELETE FROM sponsor_request WHERE sponsor_request_id = {request_id}")
        
        except Exception as e:
            click.echo(f"Error checking sponsor_request references: {str(e)}")
        
        # Check for orphaned images
        try:
            result = connection.execute("""
                SELECT i.id, i.filepath
                FROM img i
                LEFT JOIN influencer inf ON i.influencer_id = inf.influencer_id
                LEFT JOIN campaign c ON i.campaign_id = c.campaign_id
                WHERE (i.influencer_id IS NOT NULL AND inf.influencer_id IS NULL) OR
                      (i.campaign_id IS NOT NULL AND c.campaign_id IS NULL)
            """)
            
            orphaned_images = result.fetchall()
            if orphaned_images:
                issues_found = True
                click.echo(f"Found {len(orphaned_images)} orphaned image records.")
                
                if not check_only:
                    for img_id, filepath in orphaned_images:
                        click.echo(f"Deleting orphaned image ID {img_id} (file: {filepath})")
                        connection.execute(f"DELETE FROM img WHERE id = {img_id}")
                        
                        # Delete the actual file if it exists
                        full_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(filepath))
                        if os.path.exists(full_path):
                            os.remove(full_path)
                            if verbose:
                                click.echo(f"Deleted file: {full_path}")
        
        except Exception as e:
            click.echo(f"Error checking orphaned images: {str(e)}")
        
        # Check if missing tables need to be created
        if missing_tables and not check_only:
            click.echo("Creating missing tables...")
            db.create_all()
            click.echo("Tables created.")
            
            # Create admin user if admin table was missing
            if 'admin' in missing_tables:
                try:
                    admin = Admin(
                        username=app.config.get('ADMIN_USERNAME', 'admin'),
                        email=app.config.get('ADMIN_EMAIL', 'admin@example.com')
                    )
                    admin.set_password(app.config.get('ADMIN_PASSWORD', 'admin'))
                    db.session.add(admin)
                    db.session.commit()
                    click.echo("Created default admin user.")
                except Exception as e:
                    click.echo(f"Failed to create admin user: {str(e)}")
        
        # Final status report
        if issues_found:
            if check_only:
                click.echo("Issues were found. Run without --check-only to fix them.")
            else:
                click.echo("Issues were found and fixed.")
        else:
            click.echo("No issues found. Database is healthy.")

if __name__ == '__main__':
    fix_database()