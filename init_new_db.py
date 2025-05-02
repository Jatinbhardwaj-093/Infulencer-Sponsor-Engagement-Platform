#!/usr/bin/env python3
"""
Initialize a new database at the root directory location
"""
import os
import sqlite3
from werkzeug.security import generate_password_hash

# Get project directory path
project_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(project_dir, 'influencer_platform.db')

print(f"Setting up new database at: {db_path}")

# Remove existing database if it exists
if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print(f"Removed existing database file")
    except Exception as e:
        print(f"Error removing existing database: {e}")

# Create a fresh database file
try:
    # Create empty database file
    conn = sqlite3.connect(db_path)
    print("Created empty database file")
    
    # Set database file permissions
    os.chmod(db_path, 0o666)  # Read/write permissions for everyone
    print("Set database file permissions to 666")
    
    # Create the basic schema
    cursor = conn.cursor()
    
    # Create admin table
    cursor.execute('''
    CREATE TABLE admin (
        admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create influencer table
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
    
    # Create sponsor table
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
    
    # Create default admin user
    admin_password_hash = generate_password_hash('admin')
    cursor.execute('''
    INSERT INTO admin (username, password, email) VALUES (?, ?, ?)
    ''', ('admin', admin_password_hash, 'admin@example.com'))
    
    # Create campaign table
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
    
    # Create influencer_ad_request table
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
    
    # Create sponsor_request table
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
    
    # Create img table
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
    
    # Create notification table
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
    
    conn.commit()
    print("Schema created successfully with default admin user!")
    conn.close()
    
    print("\n✅ Database initialization complete!")
    print("You can now start your Flask application.")
    print("Login with:")
    print("  Username: admin")
    print("  Password: admin")
    
except Exception as e:
    print(f"Error initializing database: {e}")
    print("Database initialization failed.")