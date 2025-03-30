import random
import json
import psycopg2
from faker import Faker
from datetime import datetime, timedelta
import time
import getpass

# Set Faker to use Turkish locale
fake = Faker('tr_TR')

# Türkçe doldurma metinleri
tr_phrases = [
    "Buzdolabında sorun yaşıyorum.", "Ürünün çalışmasından memnun değilim.", "Servis desteği talep ediyorum.",
    "Sürekli ses yapıyor.", "Motor çok gürültülü çalışıyor.", "Kapak tam kapanmıyor.",
    "İçindeki yiyecekler çabuk bozuluyor.", "Yeterince soğutmuyor.", "Enerji tüketimi çok yüksek.",
    "Buzluğa buz tuttu.", "Çalışma sesi rahatsız edici.", "Kapı contası aşınmış.",
    "Dijital ekranda arıza var.", "Isı ayarı düzgün çalışmıyor.", "Enerji tüketimi beklenenden fazla.",
    "Kompresör sık sık duruyor.", "Arka tarafta su birikiyor.", "İç aydınlatma çalışmıyor.",
    "Sebzelik kırıldı.", "Rafları sağlam değil.", "Servise ulaşamıyorum.",
    "Garanti kapsamında değil dediler.", "Parça değişimi gerekiyor.", "Teknik servis yardımcı olmadı.",
    "Termostat doğru çalışmıyor.", "İç kısımda koku oluşuyor.", "Sürekli buz yapıyor.",
    "Motor aşırı ısınıyor.", "Sürekli kendini kapatıyor.", "Yetkili servise ulaşamadım."
]

# Türkçe kullanıcı yorumları
tr_comments = [
    "Acilen çözüm bekliyorum.", "Ürün tamamen değiştirilsin istiyorum.", "Paramın iadesini talep ediyorum.",
    "Garanti süresi içinde bu sorunun çözülmesini bekliyorum.", "İkinci kez aynı arıza ile karşılaşıyorum.",
    "Teknisyen randevusu talep ediyorum.", "Telefonda verilen bilgilendirme yetersizdi.",
    "Mağduriyetimin giderilmesini talep ediyorum.", "Ürünün kalitesinden hiç memnun değilim.",
    "Aynı modeli kullanan tanıdıklarım da benzer sorunlar yaşıyor.", "Marka güvenimi kaybetti.",
    "Daha önce de benzer sorunlar yaşadım.", "Yetkili servisi aradım ama yardımcı olmadılar.",
    "Servisin randevu tarihi çok geç.", "Bu marka bir daha tercih etmeyeceğim."
]

# Türkçe servis notları
tr_service_notes = [
    "Müşteriye dönüş yapıldı.", "Servis randevusu oluşturuldu.", "Garanti kapsamında değerlendirildi.",
    "Parça değişimi için sipariş verildi.", "Teknik inceleme yapıldı.", "Kullanım hatası tespit edildi.",
    "Ürün inceleme için servise alındı.", "Uzaktan destek sağlandı.", "Müşteri tekrar aranacak.",
    "Fotoğraf istendi.", "Evde onarım yapılacak.", "Merkeze taşıma gerekiyor.",
    "Fabrika ile görüşüldü.", "Benzer şikayetler incelendi.", "Kullanım kılavuzu gönderildi."
]

# Türkçe paragraf oluşturmak için fonksiyon
def generate_turkish_paragraph(n_sentences=5):
    sentences = random.sample(tr_phrases, min(n_sentences, len(tr_phrases)))
    return " ".join(sentences)

# Türkçe yorum oluşturmak için fonksiyon
def generate_turkish_comment(n_sentences=2):
    sentences = random.sample(tr_comments, min(n_sentences, len(tr_comments)))
    return " ".join(sentences)

# Türkçe servis notu oluşturmak için fonksiyon
def generate_turkish_service_note(n_sentences=2):
    sentences = random.sample(tr_service_notes, min(n_sentences, len(tr_service_notes)))
    return " ".join(sentences)

# Function to generate a single complaint document
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
        "Soğutma Sorunları", "Aşırı Gürültü", "Su Sızıntısı", "Kapı Contası Sorunu", 
        "Buz Yapıcı Arızası", "Sıcaklık Dalgalanması", "Buzlanma Oluşumu", 
        "Kompresör Sorunları", "Kontrol Paneli Hataları", "Çalışmama Sorunu", 
        "Kötü Koku", "Dondurucu Dondurmuyor", "Işık Çalışmıyor"
    ]
    
    # BSH refrigerator model numbers (realistic prefixes)
    model_prefixes = ["B36", "B46", "B20", "KGN", "KGE", "GSN", "KSV", "KIR", "GIN"]
    model_number = random.choice(model_prefixes) + str(random.randint(1000, 9999))
    
    # Common places of purchase in Turkish
    purchase_places = [
        "MediaMarkt", "Teknosa", "Vatan Bilgisayar", "BSH Mağazası", 
        "Arçelik", "Bimeks", "Amazon Türkiye", "Hepsiburada", "n11",
        "Trendyol", "E-mağaza", "Elektro World", "Koçtaş"
    ]
    
    repair_attempted = random.choice([True, False])
    
    return {
        "customerInformation": {
            "fullName": fake.name(),
            "address": fake.street_address(),
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
            "detailedDescription": generate_turkish_paragraph(5),
            "problemFirstOccurrence": problem_first_date.isoformat(),
            "frequency": random.choice(["Sürekli", "Aralıklı", "Ara Sıra", "Rastgele", "Sadece ..."]),
            "repairAttempted": repair_attempted,
            "repairDetails": generate_turkish_paragraph(3) if repair_attempted else ""
        },
        "environmentalConditions": {
            "roomTemperature": f"{random.randint(15, 32)}°C",
            "ventilation": random.choice(["Yeterli", "Yetersiz", "Kısmen Engellenmiş"]),
            "recentEnvironmentalChanges": random.choice([
                "Yok", "Elektrik Dalgalanması", "Yenileme Çalışması", "Yer Değiştirme", 
                "Hava Değişimi", "Yakında Yeni Cihazlar", "Oda Değişimi"
            ])
        },
        "customerAcknowledgment": {
            "preferredResolution": random.choice([
                "Tamir", "Değişim", "İade", "Kısmi İade", 
                "Uzatılmış Garanti", "Teknik Destek"
            ]),
            "availabilityForServiceVisit": random.sample([
                "Hafta İçi", "Hafta Sonu", "Sabah", "Öğleden Sonra", "Akşam"
            ], k=random.randint(1, 3)),
            "additionalComments": generate_turkish_comment(2)
        },
        "serviceRepresentativeNotes": {
            "initialAssessment": generate_turkish_service_note(2),
            "immediateActionsTaken": generate_turkish_service_note(2),
            "recommendations": generate_turkish_service_note(2)
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
        print(f"Oluşturuldu ve depolandı: {generated_count}/{num_complaints} şikayet (%{generated_count/num_complaints*100:.1f}) - Geçen süre: {elapsed_time:.2f}s")
    
    cursor.close()
    conn.close()
    
    print(f"Başarıyla {num_complaints} şikayet {time.time() - start_time:.2f} saniyede oluşturuldu ve kaydedildi")

if __name__ == "__main__":
    print("10.000 şikayet oluşturma ve kaydetme işlemi başlatılıyor...")
    generate_and_store_complaints(10000) 