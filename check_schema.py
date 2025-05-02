import sqlite3
import os

def inspect_db():
    try:
        db_path = 'instance/db.sqlite3'
        print(f"Checking if database exists at: {os.path.abspath(db_path)}")
        if not os.path.exists(db_path):
            print(f"Database file not found at {db_path}")
            return
            
        print("Database file exists. Connecting...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        print("Querying tables...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("\nTables in the database:")
        for table in tables:
            print(f"- {table[0]}")
            
        # Check influencer table schema if it exists
        influencer_exists = False
        for table in tables:
            if table[0] == 'influencer':
                influencer_exists = True
                print("\nInfluencer Table Schema:")
                cursor.execute(f"PRAGMA table_info('{table[0]}');")
                columns = cursor.fetchall()
                for col in columns:
                    print(f"  {col[1]} ({col[2]})")
        
        if not influencer_exists:
            print("\nThe 'influencer' table does not exist in the database.")
        
        conn.close()
        
    except Exception as e:
        print(f"Error inspecting database: {str(e)}")

if __name__ == '__main__':
    inspect_db()