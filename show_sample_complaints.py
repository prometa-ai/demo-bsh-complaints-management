import psycopg2
import getpass

def connect_to_db():
    """Connect to the PostgreSQL database."""
    username = getpass.getuser()
    try:
        conn = psycopg2.connect(
            host="localhost",
            user=username,
            database="bsh_complaints",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

def get_sample_complaints(limit=10):
    """Get a sample of complaints."""
    conn = connect_to_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, data FROM complaints ORDER BY id LIMIT %s", (limit,))
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return results

def main():
    print("\n=== Sample BSH Customer Complaints ===\n")
    
    try:
        samples = get_sample_complaints()
        for id, data in samples:
            print(f"Complaint ID: {id}")
            print(f"Customer: {data['customerInformation']['fullName']}")
            print(f"Product: {data['productInformation']['modelNumber']}")
            print(f"Problems: {', '.join(data['complaintDetails']['natureOfProblem'])}")
            print("\nDetailed Description:")
            print(data['complaintDetails']['detailedDescription'])
            print("\nService Representative's Initial Assessment:")
            print(data['serviceRepresentativeNotes']['initialAssessment'])
            print("\nRecommendations:")
            print(data['serviceRepresentativeNotes']['recommendations'])
            print("\n" + "="*80 + "\n")
    except Exception as e:
        print(f"Error retrieving sample complaints: {e}")

if __name__ == "__main__":
    main() 