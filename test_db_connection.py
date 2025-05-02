#!/usr/bin/env python3
"""
Database Connection Test Script

This script tests the database connection and verifies that the admin user exists.
"""
import os
import sys
from flask import Flask
from dotenv import load_dotenv
from db import db

# Load environment variables from .env file
load_dotenv()

# Print current working directory and database path
print(f"Current working directory: {os.getcwd()}")
db_uri = os.environ.get('DATABASE_URI') 
if db_uri:
    print(f"Database URI from .env: {db_uri}")
else:
    print("No DATABASE_URI found in .env file")

# Create a minimal Flask app for testing
app = Flask(__name__)

# Configure SQLAlchemy with the database URI from .env
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri or f'sqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), "influencer_platform.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with the app
db.init_app(app)

# Test database connection
with app.app_context():
    try:
        # Import the models
        from models import Admin, Influencer, Sponsor
        
        # Try to execute a query
        print("\nTesting database connection...")
        admin_count = db.session.query(Admin).count()
        print(f"Found {admin_count} admin users in the database")
        
        if admin_count > 0:
            admin = db.session.query(Admin).first()
            print(f"Admin username: {admin.username}")
            print("Database connection successful!")
        else:
            print("No admin users found. Database may not be properly initialized.")
            
        # Check other tables too
        influencer_count = db.session.query(Influencer).count()
        sponsor_count = db.session.query(Sponsor).count()
        
        print(f"Found {influencer_count} influencers and {sponsor_count} sponsors in the database")
        
        print("\nDatabase connection test completed successfully!")
        sys.exit(0)
    except Exception as e:
        print(f"\nError connecting to database: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure the DATABASE_URI in .env file is correct")
        print("2. Check file permissions on the database file")
        print("3. Run the reset_db.py script to initialize the database")
        print("4. Check if the database file exists")
        
        # Check if database file exists
        if not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "influencer_platform.db")):
            print("\nThe database file does not exist. Try running this command:")
            print("python manage_db.py reset")
            
        sys.exit(1)