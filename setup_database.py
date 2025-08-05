import os
import getpass
import json
import psycopg2
from dotenv import load_dotenv

def setup_database():
    """Create the database and necessary tables if they don't exist."""
    print("Setting up database...")
    
    # Load environment variables
    load_dotenv()
    
    # Get username for database connection
    username = getpass.getuser()
    
    # Get database parameters from environment or use defaults
    db_name = os.getenv("DB_NAME", "bsh_english_complaints")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_password = os.getenv("DB_PASSWORD", "admin")
    
    try:
        # Connect to PostgreSQL
        print(f"Connecting to PostgreSQL as user {username}...")
        
        # First connect to default postgres database to create our database if needed
        conn = psycopg2.connect(
            host=db_host,
            user=username,
            database="postgres",
            port=db_port,
            password=db_password
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists, create if not
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        if not cursor.fetchone():
            print(f"Creating database '{db_name}'...")
            cursor.execute(f"CREATE DATABASE {db_name}")
        else:
            print(f"Database '{db_name}' already exists.")
        
        cursor.close()
        conn.close()
        
        # Connect to the complaints database
        conn = psycopg2.connect(
            host=db_host,
            user=username,
            database=db_name,
            port=db_port,
            password=db_password
        )
        cursor = conn.cursor()
        
        # Create complaints table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id SERIAL PRIMARY KEY,
            data JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Create index on complaint details for better query performance
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_complaint_details ON complaints USING GIN ((data->'complaintDetails'->'natureOfProblem'))
        """)
        
        # Create technical_notes table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS technical_notes (
            id SERIAL PRIMARY KEY,
            complaint_id INTEGER REFERENCES complaints(id),
            data JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Commit changes and close connection
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Database setup complete!")
        return True
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        return False

if __name__ == "__main__":
    setup_database() 