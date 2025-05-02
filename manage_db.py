#!/usr/bin/env python3
"""
Comprehensive Database Management Script for Influencer Engagement Platform
This script provides various commands to manage your database:
- initialize: Create a fresh database with proper schema
- reset: Delete existing database and create a new one
- check: Verify database connectivity and structure
- fix-permissions: Correct database file and directory permissions
"""
import os
import sys
import shutil
import sqlite3
from pathlib import Path
import argparse
from werkzeug.security import generate_password_hash
from datetime import datetime

# Get project directory path
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(PROJECT_DIR, 'influencer_platform.db')

def setup_logging():
    """Configure basic logging"""
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(os.path.join(PROJECT_DIR, 'logs', f"{datetime.now().strftime('%Y-%m-%d')}_db.log"))
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

def check_permission(path, write=False):
    """Check if a path has read/write permissions"""
    if not os.path.exists(path):
        return False
    
    if write:
        return os.access(path, os.W_OK)
    else:
        return os.access(path, os.R_OK)

def fix_permissions():
    """Fix permissions on database file and surrounding directories"""
    logger.info("Fixing database permissions...")
    
    # Check and fix project directory permissions
    if os.path.exists(PROJECT_DIR):
        try:
            os.chmod(PROJECT_DIR, 0o755)
            logger.info(f"Set project directory permissions: {PROJECT_DIR}")
        except Exception as e:
            logger.error(f"Failed to set project directory permissions: {e}")
    
    # Check database file permissions
    if os.path.exists(DB_PATH):
        try:
            os.chmod(DB_PATH, 0o666)  # Read/write for everyone
            logger.info(f"Set database file permissions (666): {DB_PATH}")
        except Exception as e:
            logger.error(f"Failed to set database permissions: {e}")
    
    # Ensure logs directory exists and has proper permissions
    logs_dir = os.path.join(PROJECT_DIR, 'logs')
    if not os.path.exists(logs_dir):
        try:
            os.makedirs(logs_dir)
            logger.info(f"Created logs directory: {logs_dir}")
        except Exception as e:
            logger.error(f"Failed to create logs directory: {e}")
    
    try:
        os.chmod(logs_dir, 0o755)
        logger.info(f"Set logs directory permissions (755): {logs_dir}")
    except Exception as e:
        logger.error(f"Failed to set logs directory permissions: {e}")
    
    return True

def check_database():
    """Verify database connectivity and structure"""
    logger.info("Checking database connectivity...")
    
    if not os.path.exists(DB_PATH):
        logger.warning(f"Database file does not exist: {DB_PATH}")
        return False
    
    try:
        # Try connecting to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check for key tables
        tables_to_check = [
            'admin',
            'influencer',
            'sponsor',
            'campaign',
            'influencer_ad_request',
            'sponsor_request',
            'img',
            'notification'
        ]
        
        missing_tables = []
        for table in tables_to_check:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not cursor.fetchone():
                missing_tables.append(table)
        
        if missing_tables:
            logger.warning(f"Missing tables in database: {', '.join(missing_tables)}")
            return False
        
        # Check if admin table has at least one user
        cursor.execute("SELECT COUNT(*) FROM admin")
        admin_count = cursor.fetchone()[0]
        if admin_count == 0:
            logger.warning("No admin users found in database")
            return False
            
        logger.info("Database check successful!")
        conn.close()
        return True
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking database: {e}")
        return False

def initialize_database(force=False):
    """Create a fresh database with proper schema"""
    logger.info("Initializing database...")
    
    if os.path.exists(DB_PATH) and not force:
        logger.warning(f"Database already exists: {DB_PATH}")
        logger.warning("Use --force to overwrite the existing database")
        return False
    
    # Remove existing database if it exists and force is True
    if os.path.exists(DB_PATH) and force:
        try:
            os.remove(DB_PATH)
            logger.info("Removed existing database")
        except Exception as e:
            logger.error(f"Failed to remove existing database: {e}")
            return False
    
    # Create a fresh database
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create tables
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
        
        # Campaign table
        cursor.execute('''
        CREATE TABLE campaign (
            campaign_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sponsor_id INTEGER NOT NULL,
            influencer_id INTEGER,
            campaign_name TEXT NOT NULL,
            description TEXT NOT NULL,
            goals TEXT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            budget TEXT NOT NULL,
            visibility TEXT NOT NULL,
            finding_niche TEXT,
            flag TEXT DEFAULT 'no',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Active',
            FOREIGN KEY (sponsor_id) REFERENCES sponsor(sponsor_id),
            FOREIGN KEY (influencer_id) REFERENCES influencer(influencer_id)
        )
        ''')
        
        # InfluencerAdRequest table
        cursor.execute('''
        CREATE TABLE influencer_ad_request (
            influencer_request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER NOT NULL,
            influencer_id INTEGER NOT NULL,
            sponsor_id INTEGER NOT NULL,
            influencer_status TEXT DEFAULT 'Pending',
            message TEXT NOT NULL,
            amount INTEGER NOT NULL,
            sponsor_call TEXT,
            status_complete_influencer TEXT DEFAULT 'Pending',
            status_complete_sponsor TEXT DEFAULT 'Pending',
            payment_sponsor TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (campaign_id) REFERENCES campaign(campaign_id),
            FOREIGN KEY (influencer_id) REFERENCES influencer(influencer_id),
            FOREIGN KEY (sponsor_id) REFERENCES sponsor(sponsor_id)
        )
        ''')
        
        # SponsorRequest table
        cursor.execute('''
        CREATE TABLE sponsor_request (
            sponsor_request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER NOT NULL,
            influencer_id INTEGER NOT NULL,
            sponsor_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            amount INTEGER NOT NULL,
            influencer_call TEXT,
            sponsor_status TEXT DEFAULT 'Pending',
            status_complete_influencer TEXT DEFAULT 'Pending',
            status_complete_sponsor TEXT DEFAULT 'Pending',
            payment_sponsor TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (campaign_id) REFERENCES campaign(campaign_id),
            FOREIGN KEY (influencer_id) REFERENCES influencer(influencer_id),
            FOREIGN KEY (sponsor_id) REFERENCES sponsor(sponsor_id)
        )
        ''')
        
        # Img table
        cursor.execute('''
        CREATE TABLE img (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            filepath TEXT NOT NULL,
            mimetype TEXT NOT NULL,
            influencer_id INTEGER,
            campaign_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (influencer_id) REFERENCES influencer(influencer_id),
            FOREIGN KEY (campaign_id) REFERENCES campaign(campaign_id)
        )
        ''')
        
        # Notification table
        cursor.execute('''
        CREATE TABLE notification (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            notification_type TEXT NOT NULL,
            related_id INTEGER,
            date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_read TIMESTAMP,
            is_read BOOLEAN DEFAULT 0
        )
        ''')
        
        # Create default admin user
        admin_password_hash = generate_password_hash('admin')
        cursor.execute('''
        INSERT INTO admin (username, password, email) VALUES (?, ?, ?)
        ''', ('admin', admin_password_hash, 'admin@example.com'))
        
        conn.commit()
        conn.close()
        
        # Set proper permissions
        os.chmod(DB_PATH, 0o666)
        
        logger.info("Database initialized successfully with default admin user!")
        logger.info("You can log in with: username=admin, password=admin")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False

def reset_database():
    """Delete existing database and create a new one"""
    logger.info("Resetting database...")
    return initialize_database(force=True)

def main():
    parser = argparse.ArgumentParser(description='Influencer Platform Database Management')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Initialize command
    init_parser = subparsers.add_parser('initialize', help='Create a fresh database')
    init_parser.add_argument('--force', action='store_true', help='Overwrite existing database')
    
    # Reset command
    subparsers.add_parser('reset', help='Delete existing database and create a new one')
    
    # Check command
    subparsers.add_parser('check', help='Verify database connectivity and structure')
    
    # Fix permissions command
    subparsers.add_parser('fix-permissions', help='Correct database file permissions')
    
    args = parser.parse_args()
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.join(PROJECT_DIR, 'logs'), exist_ok=True)
    
    if args.command == 'initialize':
        success = initialize_database(args.force)
    elif args.command == 'reset':
        success = reset_database()
    elif args.command == 'check':
        success = check_database()
    elif args.command == 'fix-permissions':
        success = fix_permissions()
    else:
        parser.print_help()
        return
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()