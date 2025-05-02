"""
Script to recreate database tables according to the current models.
This will handle the missing password column issue.
WARNING: This will delete all existing data in the database.
"""

from app import app, db
import os

def recreate_database():
    print("Starting database recreation...")
    
    # Use app context to work with Flask-SQLAlchemy
    with app.app_context():
        try:
            # Check if db file exists first
            db_path = 'instance/db.sqlite3'
            if os.path.exists(db_path):
                print(f"Database found at: {os.path.abspath(db_path)}")
                
                # Drop all existing tables
                print("Dropping all existing tables...")
                db.drop_all()
                print("All tables dropped successfully.")
                
            # Create all tables according to current models
            print("Creating all tables from current models...")
            db.create_all()
            print("All tables created successfully!")
            
            print("Database recreation completed successfully.")
            return True
        
        except Exception as e:
            print(f"Error recreating database: {str(e)}")
            return False

if __name__ == "__main__":
    recreate_database()