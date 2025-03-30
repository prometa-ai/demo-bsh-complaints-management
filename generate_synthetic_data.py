import random
import json
from faker import Faker

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
            "modelNumber": fake.bothify(text='??-#####'),
            "serialNumber": fake.bothify(text='SN-########'),
            "dateOfPurchase": fake.date_this_decade().isoformat(),
            "placeOfPurchase": fake.company()
        },
        "warrantyInformation": {
            "warrantyStatus": random.choice(["Aktif", "Süresi Dolmuş"]),
            "warrantyExpirationDate": fake.date_this_decade().isoformat()
        },
        "complaintDetails": {
            "dateOfComplaint": fake.date_this_year().isoformat(),
            "natureOfProblem": random.sample([
                "Soğutma Sorunları", "Aşırı Gürültü", "Su Sızıntısı",
                "Kapı Contası Sorunu", "Buz Yapıcı Arızası"
            ], k=random.randint(1, 3)),
            "detailedDescription": generate_turkish_paragraph(5),
            "problemFirstOccurrence": fake.date_this_year().isoformat(),
            "frequency": random.choice(["Sürekli", "Aralıklı"]),
            "repairAttempted": random.choice([True, False]),
            "repairDetails": generate_turkish_paragraph(3) if random.choice([True, False]) else ""
        },
        "environmentalConditions": {
            "roomTemperature": f"{random.randint(15, 30)}°C",
            "ventilation": random.choice(["Yeterli", "Yetersiz"]),
            "recentEnvironmentalChanges": random.choice([
                "Yok", "Elektrik Dalgalanması", "Yenileme Çalışması"
            ])
        },
        "customerAcknowledgment": {
            "preferredResolution": random.choice(["Tamir", "Değişim", "İade"]),
            "availabilityForServiceVisit": random.sample([
                "Hafta İçi", "Hafta Sonu", "Sabah", "Öğleden Sonra"
            ], k=random.randint(1, 2)),
            "additionalComments": generate_turkish_comment(2)
        },
        "serviceRepresentativeNotes": {
            "initialAssessment": generate_turkish_service_note(2),
            "immediateActionsTaken": generate_turkish_service_note(2),
            "recommendations": generate_turkish_service_note(2)
        },
        "signatures": {
            "customerSignature": fake.name(),
            "customerSignatureDate": fake.date_this_year().isoformat(),
            "serviceRepresentativeSignature": fake.name(),
            "serviceRepresentativeSignatureDate": fake.date_this_year().isoformat()
        }
    }

# Generate 10,000 complaints
def generate_complaints_data(num_complaints=10000):
    return [generate_complaint() for _ in range(num_complaints)]

# Save the data to a JSON file
def save_to_json(data, filename='complaints_data.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    complaints_data = generate_complaints_data()
    save_to_json(complaints_data)
    print(f"Generated {len(complaints_data)} complaints and saved to complaints_data.json") 