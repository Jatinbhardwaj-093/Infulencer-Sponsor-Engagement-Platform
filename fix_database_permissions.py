#!/usr/bin/env python3
"""
Fix database permissions and initialize the database
"""
import os
import logging
import sqlite3
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_database():
    """Ensure the database path exists with proper permissions and initialize the database"""
    # Get the root directory
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create instance directory if not exists
    instance_dir = os.path.join(root_dir, 'instance')
    Path(instance_dir).mkdir(parents=True, exist_ok=True)
    logger.info(f"Ensured instance directory exists at: {instance_dir}")
    
    # Set permissions on instance directory
    try:
        os.chmod(instance_dir, 0o755)
        logger.info("Set permissions on instance directory to 755")
    except Exception as e:
        logger.error(f"Failed to set permissions on instance directory: {e}")
    
    # Database file path
    db_path = os.path.join(instance_dir, 'db.sqlite3')
    
    # Check if database exists
    if not os.path.exists(db_path):
        logger.info(f"Creating new database at: {db_path}")
        
        # Create an empty database file
        try:
            # Create the database file
            conn = sqlite3.connect(db_path)
            conn.close()
            logger.info("Created empty database file")
            
            # Set permissions on the database file
            os.chmod(db_path, 0o666)  # Read/write for all users
            logger.info("Set permissions on database file to 666")
        except Exception as e:
            logger.error(f"Failed to create database file: {e}")
            return False
    else:
        logger.info(f"Database file already exists at: {db_path}")
        
        # Check if we can access the database
        try:
            conn = sqlite3.connect(db_path)
            conn.close()
            logger.info("Successfully connected to the database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            
            # Attempt to fix permissions
            try:
                os.chmod(db_path, 0o666)  # Read/write for all users
                logger.info("Reset permissions on database file to 666")
            except Exception as perm_err:
                logger.error(f"Failed to update database file permissions: {perm_err}")
                return False
    
    logger.info("Database permission check and initialization completed successfully")
    return True

if __name__ == "__main__":
    success = fix_database()
    if success:
        print("Database permissions fixed successfully. You should be able to login now.")
    else:
        print("Failed to fix database permissions. Please check the logs for more information.")