import os
import getpass
import json
import sqlite3
from dotenv import load_dotenv

def setup_database():
    """Create the database and necessary tables if they don't exist."""
    print("Setting up SQLite database...")
    
    # Load environment variables
    load_dotenv()
    
    # Determine database path consistently with app's Cloud Storage helper
    try:
        from cloud_storage_db import cloud_db
        db_path = cloud_db.get_db_path()
    except Exception:
        db_path = os.getenv("DB_PATH", "bsh_complaints.db")
    
    try:
        print(f"Connecting to SQLite database at {db_path}...")
        
        # Ensure directory exists (only if path has a directory component)
        db_dir = os.path.dirname(db_path)
        if db_dir:  # Only create directory if there's a directory path
            os.makedirs(db_dir, exist_ok=True)
        
        # Connect to SQLite database (creates file if it doesn't exist)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Create complaints table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Create index on complaint details for better query performance
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_complaint_details 
        ON complaints (json_extract(data, '$.complaintDetails.natureOfProblem'))
        """)
        
        # Create technical_notes table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS technical_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id INTEGER REFERENCES complaints(id),
            data TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Create index on technical notes for better query performance
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_technical_notes_complaint_id 
        ON technical_notes (complaint_id)
        """)
        
        # Commit changes and close connection
        conn.commit()
        cursor.close()
        conn.close()
        
        print("SQLite database setup complete!")
        return True
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    setup_database() 
