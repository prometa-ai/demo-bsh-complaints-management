import psycopg2
import getpass

def connect_to_db():
    """Connect to the PostgreSQL database."""
    username = getpass.getuser()
    try:
        conn = psycopg2.connect(
            host="localhost",
            user=username,
            database="bsh_turkish_complaints",
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
    print("\n=== BSH Buzdolabı Şikayetleri Örnekleri ===\n")
    
    try:
        samples = get_sample_complaints()
        for id, data in samples:
            print(f"Şikayet ID: {id}")
            print(f"Müşteri: {data['customerInformation']['fullName']}")
            print(f"Ürün: {data['productInformation']['modelNumber']}")
            print(f"Sorunlar: {', '.join(data['complaintDetails']['natureOfProblem'])}")
            print("\nDetaylı Açıklama:")
            print(data['complaintDetails']['detailedDescription'])
            print("\nServis Temsilcisinin İlk Değerlendirmesi:")
            print(data['serviceRepresentativeNotes']['initialAssessment'])
            print("\nÖneriler:")
            print(data['serviceRepresentativeNotes']['recommendations'])
            print("\n" + "="*80 + "\n")
    except Exception as e:
        print(f"Şikayet örneklerini alma hatası: {e}")

if __name__ == "__main__":
    main() 