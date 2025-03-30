import random
import json
import psycopg2
from faker import Faker
from datetime import datetime, timedelta
import time
import getpass

# Create a Turkish faker instance
fake = Faker('tr_TR')

# Function to generate a single Turkish complaint document
def generate_complaint():
    # Random dates within reasonable ranges
    purchase_date = fake.date_between(start_date='-5y', end_date='-1m')
    warranty_years = random.choice([1, 2, 3, 5])
    warranty_expiration = purchase_date + timedelta(days=365 * warranty_years)
    complaint_date = fake.date_between(start_date=purchase_date, end_date='today')
    problem_first_date = fake.date_between(start_date=purchase_date, end_date=complaint_date)
    
    # Determine warranty status based on dates
    warranty_status = "Aktif" if warranty_expiration > datetime.now().date() else "Süresi Dolmuş"
    
    # Common refrigerator problems in Turkish
    problem_types = [
        "Soğutma Problemi", "Aşırı Ses", "Su Sızıntısı", "Kapı Contası Sorunu", 
        "Buz Yapıcı Arızası", "Sıcaklık Dalgalanması", "Buzlanma Birikimleri", 
        "Kompresör Sorunları", "Kontrol Paneli Hataları", "Çalışmama Sorunu", 
        "Kötü Koku", "Dondurucu Dondurmama Sorunu", "Lamba Çalışmıyor"
    ]
    
    # BSH refrigerator model numbers (realistic prefixes)
    model_prefixes = ["B36", "B46", "B20", "KGN", "KGE", "GSN", "KSV", "KIR", "GIN"]
    model_number = random.choice(model_prefixes) + str(random.randint(1000, 9999))
    
    # Common places of purchase in Turkish
    purchase_places = [
        "MediaMarkt", "Teknosa", "Vatan Bilgisayar", "BSH Mağazası", "Arçelik Bayi", 
        "Bimeks", "Amazon Türkiye", "Hepsiburada", "Trendyol", "Elektro World",
        "BSH Yetkili Satıcı", "Koçtaş", "Bauhaus"
    ]
    
    repair_attempted = random.choice([True, False])
    
    # Turkish refrigerator problem descriptions
    refrigerator_descriptions = [
        f"Buzdolabımız {random.choice(['sürekli', 'ara sıra', 'gece', 'sıcak havalarda'])} çok fazla ses çıkarıyor. {random.choice(['Uykumuz bölünüyor', 'Rahatsız edici bir gürültü', 'Motor sesi çok yüksek'])}.",
        f"Buzdolabının alt kısmında {random.choice(['her gün', 'iki günde bir', 'sürekli'])} su birikmesi oluyor. {random.choice(['Yerler ıslanıyor', 'Mutfak zemini zarar görüyor', 'Temizlemekten bıktım'])}.",
        f"Buzdolabı {random.choice(['yeterince', 'hiç'])} soğutmuyor. {random.choice(['Yiyeceklerimiz bozuluyor', 'İçindeki sıcaklık çok yüksek', 'Termostat sorunu olabilir'])}.",
        f"Kapı contası {random.choice(['deforme olmuş', 'yıpranmış', 'sızdırıyor'])}. {random.choice(['Soğuk hava kaçıyor', 'Dışarıdan sıcak hava giriyor', 'Enerji tüketimi arttı'])}.",
        f"Dondurucu bölmesi {random.choice(['düzgün çalışmıyor', 'dondurmada yetersiz kalıyor', 'çok fazla buz yapıyor'])}. {random.choice(['Yiyecekler donmuyor', 'Çok fazla buzlanma oluyor', 'Sıcaklık ayarı değişmiyor'])}.",
        f"Buzdolabının {random.choice(['içinde', 'sebzelik kısmında', 'et bölmesinde'])} kötü koku var. {random.choice(['Temizlik yaptığım halde geçmiyor', 'Yiyeceklere koku siniyor', 'Filtre sorunu olabilir'])}.",
        f"İç aydınlatma {random.choice(['hiç çalışmıyor', 'sürekli yanıp sönüyor', 'çok zayıf'])}. {random.choice(['Ampul değiştirdim düzelmedi', 'İçini görmek zorlaşıyor', 'Elektronik kart sorunu olabilir'])}.",
        f"Buz makinesi {random.choice(['buz üretmiyor', 'sürekli tıkanıyor', 'su damlatıyor'])}. {random.choice(['Su filtresi değiştirdim düzelmedi', 'Su bağlantısında sorun var', 'Tamir edilmesi gerekiyor'])}.",
        f"Buzdolabı {random.choice(['aniden', 'yavaş yavaş', 'dün gece', 'birkaç gündür'])} çalışmayı durdurdu. {random.choice(['Elektrik bağlantısında sorun yok', 'Sigortayı kontrol ettim', 'Kompresör arızası olabilir'])}.",
        f"Sıcaklık {random.choice(['sürekli değişiyor', 'sabit kalmıyor', 'çok yükseliyor'])}. {random.choice(['Ayarlarda değişiklik yapmadım', 'Termostat sorunu olabilir', 'Elektronik kartta arıza olabilir'])}."
    ]
    
    # Turkish customer complaint text
    def generate_turkish_complaint_text():
        intro = random.choice([
            f"{random.randint(1, 30)} {random.choice(['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'])} {random.choice(['2022', '2023'])} tarihinde satın aldığım buzdolabı ile ilgili sorun yaşıyorum.",
            f"Yaklaşık {random.choice(['bir', 'iki', 'üç', 'altı'])} {random.choice(['gündür', 'haftadır', 'aydır'])} buzdolabımla ilgili problem yaşıyorum.",
            f"Buzdolabını {random.choice(['yeni aldım', 'iki yıldır kullanıyorum', 'geçen sene aldım'])} ve şu sorunla karşılaştım."
        ])
        
        problem_desc = random.choice(refrigerator_descriptions)
        
        outro = random.choice([
            "Bu sorunun bir an önce çözülmesini istiyorum.",
            "Garanti kapsamında onarılmasını talep ediyorum.",
            "Ürünün değiştirilmesini istiyorum.",
            "Servis ekibinin en kısa sürede gelmesini rica ediyorum.",
            "Mağduriyetimin giderilmesini bekliyorum."
        ])
        
        return f"{intro} {problem_desc} {outro}"
    
    # Turkish service representative assessment
    def generate_service_assessment():
        assessments = [
            f"Müşterinin şikayeti kontrol edildi. {random.choice(['Soğutma sistemi', 'Kapı contası', 'Termostat', 'Kompresör', 'Elektronik kart'])} ile ilgili sorun tespit edildi.",
            f"Yapılan incelemede {random.choice(['gaz kaçağı', 'motor arızası', 'sensör hatası', 'fan sorunu'])} tespit edildi.",
            f"Ürün incelendi ve {random.choice(['yazılım güncellemesi', 'parça değişimi', 'ayar sorunu'])} gerektiği belirlendi.",
            f"Yerinde inceleme sonucunda {random.choice(['kullanıcı hatasından kaynaklı', 'fabrikasyon hatası', 'normal aşınma'])} olduğu gözlemlendi."
        ]
        return random.choice(assessments)
    
    # Turkish service recommendations
    def generate_recommendations():
        recommendations = [
            f"{random.choice(['Kompresör', 'Termostat', 'Kapı contası', 'Fan motoru', 'Anakart'])} değişimi yapılması önerilir.",
            f"Cihazın {random.choice(['tamir edilmesi', 'yazılım güncellemesi', 'farklı bir konuma taşınması'])} tavsiye edilir.",
            f"Garanti kapsamında {random.choice(['ücretsiz onarım', 'parça değişimi', 'yenisiyle değişim'])} işleminin yapılması uygun görülmüştür.",
            f"Servis ekibinin {random.choice(['önümüzdeki hafta', 'en kısa sürede', '3 iş günü içinde'])} ziyaret gerçekleştirmesi planlanmıştır."
        ]
        return random.choice(recommendations)
    
    return {
        "customerInformation": {
            "fullName": fake.name(),
            "address": fake.address(),
            "city": fake.city(),
            "stateProvince": fake.administrative_unit(),
            "postalCode": fake.postcode(),
            "phoneNumber": fake.phone_number(),
            "emailAddress": fake.email()
        },
        "productInformation": {
            "modelNumber": model_number,
            "serialNumber": fake.bothify(text='SN########'),
            "dateOfPurchase": purchase_date.isoformat(),
            "placeOfPurchase": random.choice(purchase_places)
        },
        "warrantyInformation": {
            "warrantyStatus": warranty_status,
            "warrantyExpirationDate": warranty_expiration.isoformat()
        },
        "complaintDetails": {
            "dateOfComplaint": complaint_date.isoformat(),
            "natureOfProblem": random.sample(problem_types, k=random.randint(1, 3)),
            "detailedDescription": generate_turkish_complaint_text(),
            "problemFirstOccurrence": problem_first_date.isoformat(),
            "frequency": random.choice(["Sürekli", "Aralıklı", "Ara sıra", "Rastgele", "Sadece..."]),
            "repairAttempted": repair_attempted,
            "repairDetails": fake.paragraph(nb_sentences=2) if repair_attempted else ""
        },
        "environmentalConditions": {
            "roomTemperature": f"{random.randint(15, 32)}°C",
            "ventilation": random.choice(["Yeterli", "Yetersiz", "Kısmen Engelli"]),
            "recentEnvironmentalChanges": random.choice([
                "Yok", "Elektrik Dalgalanması", "Tadilat", "Taşınma", "Hava Değişimi", 
                "Yakınına Yeni Cihaz Yerleştirilmesi", "Oda Değişikliği"
            ])
        },
        "customerAcknowledgment": {
            "preferredResolution": random.choice([
                "Tamir", "Değişim", "İade", "Kısmi İade", 
                "Garanti Uzatma", "Teknik Destek"
            ]),
            "availabilityForServiceVisit": random.sample([
                "Hafta İçi", "Hafta Sonu", "Sabah", "Öğleden Sonra", "Akşam"
            ], k=random.randint(1, 3)),
            "additionalComments": fake.paragraph(nb_sentences=1)
        },
        "serviceRepresentativeNotes": {
            "initialAssessment": generate_service_assessment(),
            "immediateActionsTaken": fake.paragraph(nb_sentences=1),
            "recommendations": generate_recommendations()
        },
        "signatures": {
            "customerSignature": "Dijital İmza",
            "customerSignatureDate": complaint_date.isoformat(),
            "serviceRepresentativeSignature": "Dijital İmza",
            "serviceRepresentativeSignatureDate": complaint_date.isoformat()
        }
    }

# Create the database and table structure for PostgreSQL
def setup_database():
    # Get current username as the default user for PostgreSQL on macOS
    username = getpass.getuser()
    
    # Connect to PostgreSQL (default database)
    try:
        # Connect to default 'postgres' database first
        conn = psycopg2.connect(
            host="localhost",
            user=username,
            database="postgres",
            port="5432"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create a new database
        try:
            cursor.execute("CREATE DATABASE bsh_turkish_complaints")
            print("Database 'bsh_turkish_complaints' created successfully")
        except psycopg2.errors.DuplicateDatabase:
            print("Database 'bsh_turkish_complaints' already exists")
        
        cursor.close()
        conn.close()
        
        # Connect to the new database
        conn = psycopg2.connect(
            host="localhost",
            user=username,
            database="bsh_turkish_complaints",
            port="5432"
        )
        cursor = conn.cursor()
        
        # Create table for complaints
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id SERIAL PRIMARY KEY,
            data JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        print("Table 'complaints' created successfully")
        conn.commit()
        
        return conn, cursor
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

# Generate complaints and store them in PostgreSQL
def generate_and_store_complaints(num_complaints=10000, batch_size=100):
    conn, cursor = setup_database()
    
    start_time = time.time()
    generated_count = 0
    
    for batch in range(0, num_complaints, batch_size):
        complaints_batch = []
        end_index = min(batch + batch_size, num_complaints)
        
        # Generate a batch of complaints
        for _ in range(batch, end_index):
            complaint = generate_complaint()
            complaints_batch.append(json.dumps(complaint))
            generated_count += 1
        
        # Insert the batch into the database
        args = [(complaint,) for complaint in complaints_batch]
        cursor.executemany("INSERT INTO complaints (data) VALUES (%s)", args)
        conn.commit()
        
        # Print progress
        elapsed_time = time.time() - start_time
        print(f"Generated and stored {generated_count}/{num_complaints} complaints ({generated_count/num_complaints*100:.1f}%) - Time elapsed: {elapsed_time:.2f}s")
    
    cursor.close()
    conn.close()
    
    print(f"Successfully generated and stored {num_complaints} complaints in {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    print("Starting to generate and store Turkish refrigerator complaints...")
    # Generate 1000 complaints for demonstration
    generate_and_store_complaints(1000) 