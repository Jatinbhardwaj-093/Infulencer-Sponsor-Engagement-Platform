#!/usr/bin/env python3
from flask import Flask
from models import Admin
from db import db, bcrypt
import config

# Create a minimal Flask app to leverage the db context
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.get_db_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def create_admin_user():
    with app.app_context():
        # Check if admin already exists
        admin = Admin.query.filter_by(username='admin').first()
        
        if admin:
            print("Admin user already exists!")
            return
            
        # Create a new admin user
        new_admin = Admin(
            username='admin',
            email='admin@example.com'
        )
        new_admin.set_password('admin')
        
        # Save to database
        db.session.add(new_admin)
        db.session.commit()
        
        print("Admin user created successfully!")
        print("Username: admin")
        print("Password: admin")

if __name__ == '__main__':
    create_admin_user()