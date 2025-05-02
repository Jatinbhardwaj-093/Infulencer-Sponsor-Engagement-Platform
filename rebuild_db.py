#!/usr/bin/env python3
"""
Rebuild Database Script for Influencer Engagement Platform

This script completely rebuilds the database from scratch,
deleting the existing database file and creating a new one with the initial schema.
"""
import os
import sys
from flask import Flask
from db import db
import config

def rebuild_database():
    """Rebuild the database tables"""
    # Create a minimal Flask app
    app = Flask(__name__)
    app.config.from_object(config.active_config)
    
    # Initialize the database
    db.init_app(app)
    
    # Create the tables within app context
    with app.app_context():
        print("Dropping all existing tables...")
        db.drop_all()
        
        print("Creating new tables...")
        db.create_all()
        
        # Import models for initialization
        from models import Admin, Influencer, Sponsor
        
        # Create a default admin user
        admin = Admin(
            username=app.config.get('ADMIN_USERNAME', 'admin'),
            email=app.config.get('ADMIN_EMAIL', 'admin@example.com')
        )
        admin.set_password(app.config.get('ADMIN_PASSWORD', 'admin'))
        
        # Add admin to database
        db.session.add(admin)
        db.session.commit()
        
        print(f"Created default admin user: {admin.username}")
        print("Database rebuild completed successfully!")
        
        return True

if __name__ == '__main__':
    print("Starting database rebuild process...")
    
    # First fix database permissions
    from fix_database_permissions import fix_database
    if not fix_database():
        print("Failed to fix database permissions. Aborting.")
        sys.exit(1)
    
    # Then rebuild database
    if rebuild_database():
        print("Database has been successfully rebuilt with default admin user.")
        print("You should now be able to log in using the admin credentials.")
    else:
        print("Database rebuild failed.")