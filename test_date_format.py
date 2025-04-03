import psycopg2
import getpass
import json

def connect_to_db():
    """Connect to the PostgreSQL database."""
    username = getpass.getuser()
    try:
        conn = psycopg2.connect(
            host="localhost",
            user=username,
            database="bsh_english_complaints",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

def check_complaint_dates():
    """Check the date format in complaint records."""
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        
        # Fetch a few complaint records
        cursor.execute("SELECT id, data FROM complaints LIMIT 5")
        complaints = cursor.fetchall()
        
        print(f"Found {len(complaints)} complaints")
        
        for complaint_id, data in complaints:
            date_of_complaint = data.get('complaintDetails', {}).get('dateOfComplaint', 'N/A')
            print(f"Complaint ID: {complaint_id}")
            print(f"Date of Complaint: {date_of_complaint}")
            print(f"Date Type: {type(date_of_complaint)}")
            print("-" * 50)
        
        # Test the time period filter
        cursor.execute("""
            SELECT COUNT(*) 
            FROM complaints 
            WHERE (data->'complaintDetails'->>'dateOfComplaint')::timestamp >= NOW() - INTERVAL '30 days'
        """)
        count_result = cursor.fetchone()
        print(f"Complaints in last 30 days: {count_result[0]}")
        
        # Print example of date format as it appears in the database
        cursor.execute("""
            SELECT data->'complaintDetails'->>'dateOfComplaint' as date_format
            FROM complaints
            LIMIT 5
        """)
        date_formats = cursor.fetchall()
        print("Example date formats from database:")
        for date_format in date_formats:
            print(date_format[0])
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error checking complaint dates: {e}")

if __name__ == "__main__":
    check_complaint_dates() 