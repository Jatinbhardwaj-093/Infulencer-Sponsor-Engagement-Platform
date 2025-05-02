import sqlite3
import os

def add_password_column():
    try:
        # Connect to the SQLite database
        db_path = 'instance/db.sqlite3'
        print(f"Connecting to database at: {os.path.abspath(db_path)}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if influencer table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='influencer';")
        if not cursor.fetchone():
            print("The 'influencer' table doesn't exist. Please make sure the database is properly initialized.")
            conn.close()
            return False
        
        # Check if the password column already exists
        cursor.execute("PRAGMA table_info(influencer);")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'password' in columns:
            print("The 'password' column already exists in the 'influencer' table.")
        else:
            # Add the password column to the influencer table
            print("Adding 'password' column to the 'influencer' table...")
            cursor.execute("ALTER TABLE influencer ADD COLUMN password VARCHAR(128) NOT NULL DEFAULT '';")
            conn.commit()
            print("Column added successfully!")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(influencer);")
        columns = cursor.fetchall()
        print("\nUpdated influencer table schema:")
        for col in columns:
            print(f"  {col[1]} ({col[2]}){' (PRIMARY KEY)' if col[5] else ''}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    add_password_column()