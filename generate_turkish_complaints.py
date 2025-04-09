#!/usr/bin/env python3

import psycopg2
import json
import random
import logging
import getpass
from faker import Faker
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Turkish faker
turkish_faker = Faker("tr_TR")

# Common refrigerator problems in Turkish
refrigerator_problems_tr = [
    "Sıcaklık Sorunları",
    "Soğutma Sorunları",
    "Dondurma Sorunları",
    "Buz Yapıcı Sorunları",
    "Su Pınarı Sorunları",
    "Gürültü Sorunları",
    "Buz Çözme Sorunları",
    "Kapı Contası Sorunları",
    "Koku Sorunları",
    "Ekran Sorunları",
    "Kompresör Sorunları",
    "Tahliye Sorunları",
    "Aydınlatma Sorunları"
]

# Components in Turkish
component_mapping_tr = {
    "Sıcaklık Sorunları": ["Termostat", "Sensör", "Kontrol Kartı"],
    "Soğutma Sorunları": ["Kompresör", "Soğutucu Akışkan", "Kondansatör"],
    "Dondurma Sorunları": ["Dondurucu Fanı", "Termostat", "Buz Çözme Isıtıcısı"],
    "Buz Yapıcı Sorunları": ["Buz Yapıcı Motor", "Su Vanası", "Doldurma Kolu"],
    "Su Pınarı Sorunları": ["Su Filtresi", "Su Hattı", "Dağıtım Valfi"],
    "Gürültü Sorunları": ["Kompresör", "Fan Motor", "Buz Yapıcı"],
    "Buz Çözme Sorunları": ["Buz Çözme Zamanlayıcısı", "Buz Çözme Isıtıcısı", "Termostat"],
    "Kapı Contası Sorunları": ["Kapı Contası", "Kapı Menteşesi", "Kapı Hizalaması"],
    "Koku Sorunları": ["Hava Filtresi", "Tahliye Hattı", "Yoğuşma Tepsisi"],
    "Ekran Sorunları": ["Kontrol Kartı", "Ekran Paneli", "Güç Kaynağı"],
    "Kompresör Sorunları": ["Kompresör", "Başlatıcı Röle", "Termal Koruyucu"],
    "Tahliye Sorunları": ["Tahliye Hattı", "Yoğuşma Tepsisi", "Buz Çözme Sistemi"],
    "Aydınlatma Sorunları": ["Lamba", "Kapı Anahtarı", "Güç Kaynağı"]
}

# Issues in Turkish
issue_mapping_tr = {
    "Sıcaklık Sorunları": ["aşınma", "arıza", "bozulma", "kalibrasyon hatası"],
    "Soğutma Sorunları": ["gaz kaçağı", "tıkanma", "aşınma", "yetersiz basınç"],
    "Dondurma Sorunları": ["sensör arızası", "fan arızası", "ısıtıcı arızası"],
    "Buz Yapıcı Sorunları": ["tıkanma", "motor arızası", "kontrol arızası"],
    "Su Pınarı Sorunları": ["tıkanma", "valf arızası", "basınç düşüklüğü"],
    "Gürültü Sorunları": ["dengesizlik", "aşınma", "gevşek parçalar"],
    "Buz Çözme Sorunları": ["zamanlayıcı arızası", "ısıtıcı arızası", "sensör arızası"],
    "Kapı Contası Sorunları": ["aşınma", "bozulma", "hizalama sorunu"],
    "Koku Sorunları": ["bakteri oluşumu", "tıkanma", "filtre kirliliği"],
    "Ekran Sorunları": ["yazılım hatası", "donanım arızası", "bağlantı sorunu"],
    "Kompresör Sorunları": ["aşınma", "elektrik arızası", "soğutucu akışkan sorunu"],
    "Tahliye Sorunları": ["tıkanma", "buz oluşumu", "yanlış montaj"],
    "Aydınlatma Sorunları": ["ampul arızası", "bağlantı sorunu", "güç kaynağı arızası"]
}

# Detailed problem descriptions in Turkish
problem_descriptions_tr = {
    "Sıcaklık Sorunları": "Buzdolabım düzgün soğutmuyor. İçerideki sıcaklık çok yüksek ve yiyeceklerim hızla bozuluyor.",
    "Soğutma Sorunları": "Buzdolabının soğutması yeterli değil. Yiyecekler oda sıcaklığına yakın kalıyor.",
    "Dondurma Sorunları": "Dondurucu bölmesi yeterince soğuk değil. Dondurulmuş yiyeceklerim çözülüyor.",
    "Buz Yapıcı Sorunları": "Buz yapıcı düzgün çalışmıyor. Ya hiç buz üretmiyor ya da çok az üretiyor.",
    "Su Pınarı Sorunları": "Su pınarından su gelmiyor veya çok az geliyor. Filtre değiştirmeme rağmen sorun devam ediyor.",
    "Gürültü Sorunları": "Buzdolabı çok fazla gürültü yapıyor. Özellikle geceleri rahatsız edici bir seviyede.",
    "Buz Çözme Sorunları": "Buzdolabım otomatik buz çözme yapmıyor. İçeride çok fazla buz birikiyor.",
    "Kapı Contası Sorunları": "Kapı contası düzgün kapanmıyor. Kapıyı kapatmama rağmen aralık kalıyor ve içerisi soğumuyor.",
    "Koku Sorunları": "Buzdolabımda kötü koku var. Temizlememe rağmen geçmiyor.",
    "Ekran Sorunları": "Kontrol paneli ekranı düzgün çalışmıyor. Bazen yanıt vermiyor veya yanlış bilgiler gösteriyor.",
    "Kompresör Sorunları": "Kompresör düzgün çalışmıyor. Buzdolabı çalışmaya başladığında anormal sesler çıkarıyor ve sonra duruyor.",
    "Tahliye Sorunları": "Buzdolabından su sızıntısı var. Zemine su birikmeye başladı.",
    "Aydınlatma Sorunları": "İç aydınlatma çalışmıyor. Ampulleri değiştirmeme rağmen sorun devam ediyor."
}

# Other options in Turkish
frequency_options_tr = ["Sürekli", "Aralıklı", "Ara sıra", "Günlük", "Haftalık"]
ventilation_options_tr = ["İyi", "Ortalama", "Kötü", "Engellenmiş", "Bilinmiyor"]
environmental_changes_tr = [
    "Buzdolabını yakın zamanda yeni bir konuma taşıdım", 
    "Yakın zamanda değişiklik yok", 
    "Yakın zamanda elektrik kesintisi yaşandı", 
    "Oda sıcaklığı ayarlarını değiştirdim", 
    "Mutfak yenilendi"
]
preferred_resolution_options_tr = ["Tamir", "Değişim", "İade", "Servis Ziyareti", "Teknik Yardım"]
additional_comments_tr = [
    "Bu sorunun en kısa sürede çözülmesini istiyorum", 
    "Sabah randevularını tercih ederim", 
    "Ziyaretten önce lütfen arayın", 
    "Daha önceki tamir girişimlerinde kötü deneyim yaşadım", 
    ""
]
repair_details_tr = [
    "Cihazı sıfırlamayı denedim. Bu sorunu çözmedi.", 
    "Bobinleri temizlemeyi denedim. Bu sorunu çözmedi.", 
    "Sıcaklık ayarlarını değiştirmeyi denedim. Bu sorunu çözmedi.", 
    "Manuel buz çözmeyi denedim. Bu sorunu çözmedi.", 
    "Gevşek bağlantıları kontrol etmeyi denedim. Bu sorunu çözmedi."
]

# Turkish cities with their postal code prefixes
turkish_cities = {
    "İstanbul": "34",
    "Ankara": "06",
    "İzmir": "35",
    "Antalya": "07",
    "Bursa": "16",
    "Adana": "01",
    "Konya": "42",
    "Gaziantep": "27",
    "Şanlıurfa": "63",
    "Mersin": "33",
    "Kayseri": "38",
    "Samsun": "55",
    "Denizli": "20",
    "Eskişehir": "26",
    "Trabzon": "61"
}

# Places of purchase in Turkey
purchase_places_tr = ["Teknosa", "MediaMarkt", "Bimeks", "Vatan", "Arçelik"]

# Technical assessment templates in Turkish
initial_assessment_templates_tr = [
    "İlk incelemede, {problem_type} doğrulandı. {component} üzerinde {issue} belirtileri görüldü.",
    "İlk kontrol sonucunda, bildirilen {problem_type} teyit edildi. {component}'deki {issue} muhtemelen bildirilen soruna neden oluyor.",
    "Buzdolabının ilk incelemesinde, {problem_type} gözlemlendi. {component} parçasındaki {issue} tespit edildi.",
    "Ön değerlendirmemizde, {problem_type} sorunu doğrulandı. {component} parçasında {issue} tespit edildi."
]

immediate_actions_templates_tr = [
    "Kondansatör bobinlerini temizledim ve soğutucu akışkan basıncını kontrol ettim. Buz tıkanıklıklarını temizlemek için manuel bir buz çözme döngüsü gerçekleştirdim.",
    "Termostat ve sensörlerin kalibrasyonunu kontrol ettim. Tüm elektrik bağlantılarını sıktım ve fan motorlarını temizledim.",
    "Sistemin tüm parçalarını kontrol ettim ve test ettim. Küçük ayarlamalar yaptım ve genel bir sistem temizliği gerçekleştirdim.",
    "Donanım düzgün çalışıyor mu diye teşhis testi yaptım. Gerekli ayarlamaları yaptım ve sistemin ana parçalarını temizledim."
]

recommendations_templates_tr = [
    "{component} aşınma belirtileri gösteriyor ve yakında değiştirilmesi gerekecek. {problem_type} sorununun tamamen çözülmesi için bu bakımın önümüzdeki 30 gün içinde planlanmasını öneriyorum.",
    "{component} düzgün çalışmıyor ve değiştirilmesi gerekiyor. Bu, {problem_type} sorununu çözecektir. Ek olarak, gelecekteki sorunları önlemek için genel bir bakım öneriyorum.",
    "Teşhis, {component}'nin değiştirilmesi gerektiğini gösteriyor. Bu {problem_type} sorununun ana nedenidir. Ayrıca, sistemin daha iyi çalışması için genel bir bakım öneriyorum.",
    "{component} ciddi {problem_type} belirtileri gösteriyor. Bu parçanın değiştirilmesini ve sistemin çalışmasını optimize etmek için tam bir bakım yapılmasını öneriyorum."
]

def random_date(start_date, end_date):
    """Generate a random date between start_date and end_date."""
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)

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
        logger.error(f"Database connection error: {e}")
        return None

def generate_turkish_address():
    """Generate a realistic Turkish address."""
    
    # Choose a city and get its postal code prefix
    city = random.choice(list(turkish_cities.keys()))
    postal_prefix = turkish_cities[city]
    
    # Common Turkish street name formats
    street_types = ["Caddesi", "Sokak", "Bulvarı"]
    street_type = random.choice(street_types)
    
    # Common street names
    street_names = ["Atatürk", "Cumhuriyet", "İstiklal", "Fatih", "Mevlana", 
                   "Gazi", "Barış", "Çiçek", "İnönü", "Fevzi Çakmak"]
    street_name = random.choice(street_names)
    
    # Generate address
    building_no = random.randint(1, 150)
    apt_no = random.randint(1, 30)
    
    # Create address string
    address = f"{street_name} {street_type} No: {building_no}, Daire: {apt_no}"
    
    # Generate postal code (5 digits in Turkey, starting with city prefix)
    postal_code = f"{postal_prefix}{random.randint(100, 999)}"
    
    # Generate phone (starts with 0 and country code is +90)
    area_code = random.choice(["532", "535", "542", "544", "505", "506", "555"])
    phone = f"+90 {area_code} {random.randint(100, 999)} {random.randint(1000, 9999)}"
    
    return {
        "address": address,
        "city": city,
        "postalCode": postal_code,
        "phoneNumber": phone
    }

def generate_turkish_customer():
    """Generate a Turkish customer details."""
    
    # Generate Turkish name
    name = turkish_faker.name()
    
    # Generate Turkish address
    turkish_address = generate_turkish_address()
    
    # Generate email (using ASCII characters for compatibility)
    name_parts = ''.join(c for c in name.lower() if c.isalnum())[:10]
    email = f"{name_parts}{random.randint(1, 999)}@example.com"
    
    return {
        "fullName": name,
        "address": turkish_address["address"],
        "city": turkish_address["city"],
        "stateProvince": "",
        "postalCode": turkish_address["postalCode"],
        "phoneNumber": turkish_address["phoneNumber"],
        "emailAddress": email,
        "country": "Turkey"
    }

def generate_turkish_complaint():
    """Generate a random complaint in Turkish."""
    
    # Generate dates
    current_date = datetime.now()
    purchase_date = random_date(current_date - timedelta(days=1825), current_date - timedelta(days=30))
    warranty_expiration_date = purchase_date + timedelta(days=730)  # 2-year warranty
    problem_first_date = random_date(purchase_date, current_date)
    complaint_date = random_date(problem_first_date, current_date)
    
    # Randomly select 1-3 problems
    num_problems = random.randint(1, 3)
    selected_problems = random.sample(refrigerator_problems_tr, num_problems)
    
    # Get the main problem type (first in the list)
    main_problem_type = selected_problems[0]
    
    # Get detailed description for the main problem
    detailed_description = problem_descriptions_tr.get(main_problem_type, turkish_faker.paragraph(nb_sentences=3))
    
    # Randomly determine if a repair was attempted
    repair_attempted = random.choice([True, False])
    repair_details = random.choice(repair_details_tr) if repair_attempted else ""
    
    # Determine warranty status based on dates
    if current_date < warranty_expiration_date:
        warranty_status = "Aktif"
    else:
        warranty_status = random.choice(["Süresi Dolmuş", "Geçersiz"])
    
    # Get components relevant to the main problem
    component = random.choice(component_mapping_tr.get(main_problem_type, ["Kompresör", "Termostat", "Kontrol Kartı"]))
    issue = random.choice(issue_mapping_tr.get(main_problem_type, ["aşınma", "arıza", "bozulma"]))
    
    # Generate service representative notes using templates
    initial_assessment = random.choice(initial_assessment_templates_tr).format(
        problem_type=main_problem_type.lower(),
        component=component.lower(),
        issue=issue
    )
    
    immediate_actions_taken = random.choice(immediate_actions_templates_tr)
    
    recommendations = random.choice(recommendations_templates_tr).format(
        component=component.lower(),
        problem_type=main_problem_type.lower()
    )
    
    # Generate availability days (3-5 random weekdays)
    weekdays = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
    availability_days = random.sample(weekdays, random.randint(3, 5))
    
    # Create the complaint data structure
    complaint = {
        "customerInformation": generate_turkish_customer(),
        "productInformation": {
            "modelNumber": f"BSH-R{random.randint(1000, 9999)}",
            "serialNumber": turkish_faker.uuid4().upper()[:12],
            "dateOfPurchase": purchase_date.isoformat(),
            "placeOfPurchase": random.choice(purchase_places_tr)
        },
        "warrantyInformation": {
            "warrantyStatus": warranty_status,
            "warrantyExpirationDate": warranty_expiration_date.isoformat()
        },
        "complaintDetails": {
            "dateOfComplaint": complaint_date.isoformat(),
            "natureOfProblem": selected_problems,
            "detailedDescription": detailed_description,
            "problemFirstOccurrence": problem_first_date.isoformat(),
            "frequency": random.choice(frequency_options_tr),
            "repairAttempted": repair_attempted,
            "repairDetails": repair_details
        },
        "environmentalConditions": {
            "roomTemperature": f"{random.randint(18, 30)}°C",
            "ventilation": random.choice(ventilation_options_tr),
            "recentEnvironmentalChanges": random.choice(environmental_changes_tr)
        },
        "customerAcknowledgment": {
            "preferredResolution": random.choice(preferred_resolution_options_tr),
            "availabilityForServiceVisit": availability_days,
            "additionalComments": random.choice(additional_comments_tr)
        },
        "serviceRepresentativeNotes": {
            "initialAssessment": initial_assessment,
            "immediateActionsTaken": immediate_actions_taken,
            "recommendations": recommendations
        },
        "signatures": {
            "customerSignature": turkish_faker.name(),
            "customerSignatureDate": complaint_date.isoformat(),
            "serviceRepresentativeSignature": turkish_faker.name(),
            "serviceRepresentativeSignatureDate": complaint_date.isoformat()
        }
    }
    
    return complaint, main_problem_type, component, issue

def generate_turkish_technical_note(complaint_data, main_problem_type, main_component, main_issue):
    """Generate a technical note in Turkish that's consistent with the complaint."""
    
    # Extract problem details
    problems = complaint_data.get('complaintDetails', {}).get('natureOfProblem', [main_problem_type])
    
    # Get components based on the main problem type
    relevant_components = component_mapping_tr.get(main_problem_type, ["Kompresör", "Termostat", "Kontrol Kartı"])
    
    # Ensure the main component is included
    if main_component not in relevant_components:
        relevant_components.append(main_component)
    
    # Get a few more components to inspect (1-3 additional)
    additional_components = random.sample(
        [c for c in set(sum(component_mapping_tr.values(), [])) if c != main_component],
        k=min(3, random.randint(1, 3))
    )
    inspected_components = [main_component] + additional_components
    
    # Get issues related to the main problem
    relevant_issues = issue_mapping_tr.get(main_problem_type, ["aşınma", "arıza", "bozulma"])
    
    # Ensure the main issue is included
    if main_issue not in relevant_issues:
        relevant_issues.append(main_issue)
    
    # Random cause
    causes = [
        "normal aşınma", "üretim hatası", "yanlış kullanım", "uygun olmayan çevre koşulları",
        "elektrik dalgalanmaları", "nakliye hasarı", "yetersiz temizlik", "normal kullanım ömrünün sona ermesi",
        "önceki hatalı tamir", "uyumsuz parça kullanımı", "aşırı yükleme", "nem ve rutubet"
    ]
    cause = random.choice(causes)
    
    # Repair actions
    repair_actions = [
        "temizleme", "değiştirme", "kalibrasyon", "yeniden programlama",
        "lehimleme", "sıkıştırma", "kaynak yapma", "yalıtımı güçlendirme"
    ]
    repair_action = random.choice(repair_actions)
    
    # Generate visit date
    complaint_date = datetime.fromisoformat(complaint_data.get('complaintDetails', {}).get('dateOfComplaint', datetime.now().isoformat()))
    visit_date = random_date(complaint_date, datetime.now())
    
    # Decide if parts were replaced
    parts_replaced = []
    if random.random() < 0.7:  # 70% chance to replace parts
        parts_replaced.append(main_component)
        
        # Small chance to replace additional components
        if random.random() < 0.3:
            parts_replaced.extend(random.sample(additional_components, k=random.randint(
                0, min(2, len(additional_components))
            )))
    
    # Create diagnosis text in Turkish
    fault_diagnosis = f"Müşteri tarafından bildirilen {main_problem_type.lower()} sorunu incelendi. {main_component} üzerinde yapılan testlerde {main_issue} tespit edildi. Ölçüm değerleri normal aralığın %{random.randint(15, 50)} dışında."
    
    # Create root cause text in Turkish
    root_cause = f"Sorunun temel nedeni, {main_component}'ın {main_issue} nedeniyle verimli çalışmamasıdır. Bu muhtemelen {cause} nedeniyle oluşmuştur."
    
    # Create solution text in Turkish
    solution_proposed = f"{main_component} ünitesinin tamamen değiştirilmesi gerekiyor. Ayrıca, {random.choice(repair_actions)} yapılması önerilir."
    
    # Create repair details text in Turkish
    repair_details = ""
    if parts_replaced:
        repair_details = f"{main_component} üzerinde {repair_action} uygulandı. Eski parça tamamen sökülüp, yeni parça takıldı ve test edildi."
    
    # Decide if follow-up is required
    follow_up_required = random.random() < 0.4
    
    # Create follow-up notes if required
    follow_up_notes = ""
    if follow_up_required:
        follow_up_notes = f"{random.randint(15, 90)} gün içinde {random.choice(['parçanın durumunu kontrol etmek', 'sistemi tekrar gözden geçirmek', 'kalibrasyonu doğrulamak', 'müşteri memnuniyetini kontrol etmek'])} için takip ziyareti gerekiyor."
    
    # Generate customer satisfaction score
    customer_satisfaction = random.randint(1, 5)
    
    # Create the technical note structure
    technical_note = {
        "technicianName": turkish_faker.name(),
        "visitDate": visit_date.isoformat(),
        "technicalAssessment": {
            "componentInspected": inspected_components,
            "faultDiagnosis": fault_diagnosis,
            "rootCause": root_cause,
            "solutionProposed": solution_proposed
        },
        "partsReplaced": parts_replaced,
        "repairDetails": repair_details if parts_replaced else "Sadece teşhis yapıldı. Herhangi bir parça değiştirilmedi.",
        "followUpRequired": follow_up_required,
        "followUpNotes": follow_up_notes if follow_up_required else "",
        "customerSatisfaction": customer_satisfaction
    }
    
    return technical_note

def generate_turkish_complaints(num_complaints=50):
    """Generate Turkish complaints and add them to the database."""
    conn = connect_to_db()
    if not conn:
        logger.error("Failed to connect to database")
        return
    
    cursor = conn.cursor()
    
    try:
        inserted_count = 0
        for i in range(num_complaints):
            # Generate a Turkish complaint
            complaint, problem_type, component, issue = generate_turkish_complaint()
            
            # Insert the complaint
            cursor.execute(
                "INSERT INTO complaints (data) VALUES (%s) RETURNING id",
                (json.dumps(complaint),)
            )
            complaint_id = cursor.fetchone()[0]
            
            # Add a technical note for about 70% of complaints
            if random.random() < 0.7:
                tech_note = generate_turkish_technical_note(complaint, problem_type, component, issue)
                cursor.execute(
                    "INSERT INTO technical_notes (complaint_id, data) VALUES (%s, %s)",
                    (complaint_id, json.dumps(tech_note))
                )
            
            inserted_count += 1
            if inserted_count % 10 == 0:
                conn.commit()
                logger.info(f"Generated {inserted_count} Turkish complaints...")
        
        # Final commit
        conn.commit()
        logger.info(f"Successfully generated {inserted_count} Turkish complaints with Turkish text")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error generating Turkish complaints: {e}")
        if conn:
            conn.close()

if __name__ == "__main__":
    logger.info("Starting Turkish complaint generation...")
    generate_turkish_complaints(50)  # Generate 50 Turkish complaints by default
    logger.info("Turkish complaint generation completed.") 