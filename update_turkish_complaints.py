#!/usr/bin/env python3

import psycopg2
import json
import random
import logging
import getpass
from faker import Faker

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Turkish faker
turkish_faker = Faker("tr_TR")

# Turkish translations for common refrigerator problems
refrigerator_problems_tr = {
    "Temperature Issues": "Sıcaklık Sorunları",
    "Cooling Issues": "Soğutma Sorunları",
    "Freezing Issues": "Dondurma Sorunları",
    "Ice Maker Issues": "Buz Yapıcı Sorunları",
    "Water Dispenser Issues": "Su Pınarı Sorunları",
    "Noise Issues": "Gürültü Sorunları",
    "Defrosting Issues": "Buz Çözme Sorunları",
    "Door Seal Issues": "Kapı Contası Sorunları",
    "Odor Issues": "Koku Sorunları",
    "Display Issues": "Ekran Sorunları",
    "Compressor Issues": "Kompresör Sorunları",
    "Drainage Issues": "Tahliye Sorunları",
    "Lighting Issues": "Aydınlatma Sorunları"
}

# Turkish translations for frequencies
frequency_tr = {
    "Constant": "Sürekli",
    "Intermittent": "Aralıklı",
    "Occasional": "Ara sıra",
    "Daily": "Günlük",
    "Weekly": "Haftalık"
}

# Turkish translations for ventilation
ventilation_tr = {
    "Good": "İyi",
    "Average": "Ortalama",
    "Poor": "Kötü",
    "Blocked": "Engellenmiş",
    "Unknown": "Bilinmiyor"
}

# Turkish translations for environmental changes
environmental_changes_tr = {
    "Recently moved the refrigerator to a new location": "Buzdolabını yakın zamanda yeni bir konuma taşıdım",
    "No recent changes": "Yakın zamanda değişiklik yok",
    "Recent power outage": "Yakın zamanda elektrik kesintisi yaşandı",
    "Changed room temperature settings": "Oda sıcaklığı ayarlarını değiştirdim",
    "Remodeled kitchen": "Mutfak yenilendi"
}

# Turkish translations for preferred resolution
preferred_resolution_tr = {
    "Repair": "Tamir",
    "Replacement": "Değişim",
    "Refund": "İade",
    "Service Visit": "Servis Ziyareti",
    "Technical Assistance": "Teknik Yardım"
}

# Turkish translations for additional comments
additional_comments_tr = {
    "Need this fixed as soon as possible": "Bu sorunun en kısa sürede çözülmesini istiyorum",
    "Prefer morning appointments": "Sabah randevularını tercih ederim",
    "Please call before visiting": "Ziyaretten önce lütfen arayın",
    "Already had a bad experience with previous repair attempts": "Daha önceki tamir girişimlerinde kötü deneyim yaşadım",
    "": ""
}

# Turkish translations for repair attempts
repair_details_tr = {
    "I tried to reset the unit": "Cihazı sıfırlamayı denedim",
    "I tried to clean the coils": "Bobinleri temizlemeyi denedim",
    "I tried to adjust the temperature settings": "Sıcaklık ayarlarını değiştirmeyi denedim",
    "I tried to defrost manually": "Manuel buz çözmeyi denedim",
    "I tried to check for loose connections": "Gevşek bağlantıları kontrol etmeyi denedim"
}

# Turkish detailed descriptions for refrigerator problems
problem_descriptions_tr = {
    "Temperature Issues": "Buzdolabım düzgün soğutmuyor. İçerideki sıcaklık çok yüksek ve yiyeceklerim hızla bozuluyor.",
    "Cooling Issues": "Buzdolabının soğutması yeterli değil. Yiyecekler oda sıcaklığına yakın kalıyor.",
    "Freezing Issues": "Dondurucu bölmesi yeterince soğuk değil. Dondurulmuş yiyeceklerim çözülüyor.",
    "Ice Maker Issues": "Buz yapıcı düzgün çalışmıyor. Ya hiç buz üretmiyor ya da çok az üretiyor.",
    "Water Dispenser Issues": "Su pınarından su gelmiyor veya çok az geliyor. Filtre değiştirmeme rağmen sorun devam ediyor.",
    "Noise Issues": "Buzdolabı çok fazla gürültü yapıyor. Özellikle geceleri rahatsız edici bir seviyede.",
    "Defrosting Issues": "Buzdolabım otomatik buz çözme yapmıyor. İçeride çok fazla buz birikiyor.",
    "Door Seal Issues": "Kapı contası düzgün kapanmıyor. Kapıyı kapatmama rağmen aralık kalıyor ve içerisi soğumuyor.",
    "Odor Issues": "Buzdolabımda kötü koku var. Temizlememe rağmen geçmiyor.",
    "Display Issues": "Kontrol paneli ekranı düzgün çalışmıyor. Bazen yanıt vermiyor veya yanlış bilgiler gösteriyor.",
    "Compressor Issues": "Kompresör düzgün çalışmıyor. Buzdolabı çalışmaya başladığında anormal sesler çıkarıyor ve sonra duruyor.",
    "Drainage Issues": "Buzdolabından su sızıntısı var. Zemine su birikmeye başladı.",
    "Lighting Issues": "İç aydınlatma çalışmıyor. Ampulleri değiştirmeme rağmen sorun devam ediyor."
}

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

def generate_turkish_complaint_details(original_complaint):
    """Generate Turkish versions of the complaint details for Turkish customers."""
    
    # Extract original complaint details
    complaint_details = original_complaint.get('complaintDetails', {})
    environmental_conditions = original_complaint.get('environmentalConditions', {})
    customer_acknowledgment = original_complaint.get('customerAcknowledgment', {})
    
    # Convert nature of problem to Turkish
    original_problems = complaint_details.get('natureOfProblem', [])
    turkish_problems = []
    
    if isinstance(original_problems, list):
        for problem in original_problems:
            turkish_problems.append(refrigerator_problems_tr.get(problem, problem))
    else:
        # Handle case where natureOfProblem might be a string
        turkish_problems = [refrigerator_problems_tr.get(original_problems, original_problems)]
    
    # Get detailed description in Turkish based on first problem
    main_problem = original_problems[0] if isinstance(original_problems, list) and original_problems else ""
    detailed_description = problem_descriptions_tr.get(main_problem, turkish_faker.paragraph(nb_sentences=3))
    
    # Convert frequency to Turkish
    original_frequency = complaint_details.get('frequency', 'Constant')
    turkish_frequency = frequency_tr.get(original_frequency, original_frequency)
    
    # Convert repair details to Turkish if attempted
    repair_attempted = complaint_details.get('repairAttempted', False)
    repair_details = ""
    if repair_attempted:
        original_repair = complaint_details.get('repairDetails', "")
        # Try to match with known English phrases
        for eng, tr in repair_details_tr.items():
            if eng in original_repair:
                repair_details = tr + ". Bu sorunu çözmedi."
                break
        
        # If no match found, generate a generic Turkish repair attempt description
        if not repair_details:
            repair_details = random.choice(list(repair_details_tr.values())) + ". Bu sorunu çözmedi."
    
    # Convert environmental conditions to Turkish
    original_temp = environmental_conditions.get('roomTemperature', "")
    original_ventilation = environmental_conditions.get('ventilation', "")
    original_changes = environmental_conditions.get('recentEnvironmentalChanges', "")
    
    # Convert room temperature to Celsius if it contains Fahrenheit
    room_temperature = original_temp
    if "°F" in original_temp:
        try:
            fahrenheit = int(original_temp.replace('°F', '').strip())
            celsius = round((fahrenheit - 32) * 5/9)
            room_temperature = f"{celsius}°C"
        except:
            room_temperature = original_temp
    
    turkish_ventilation = ventilation_tr.get(original_ventilation, original_ventilation)
    turkish_changes = environmental_changes_tr.get(original_changes, original_changes)
    
    # Convert customer acknowledgment to Turkish
    original_resolution = customer_acknowledgment.get('preferredResolution', "")
    original_comments = customer_acknowledgment.get('additionalComments', "")
    
    turkish_resolution = preferred_resolution_tr.get(original_resolution, original_resolution)
    turkish_comments = additional_comments_tr.get(original_comments, original_comments)
    
    # Create Turkish versions of the complaint sections
    turkish_complaint_details = {
        'dateOfComplaint': complaint_details.get('dateOfComplaint', ''),
        'natureOfProblem': turkish_problems,
        'detailedDescription': detailed_description,
        'problemFirstOccurrence': complaint_details.get('problemFirstOccurrence', ''),
        'frequency': turkish_frequency,
        'repairAttempted': repair_attempted,
        'repairDetails': repair_details if repair_attempted else "",
        'resolutionStatus': complaint_details.get('resolutionStatus', ''),
        'resolutionDate': complaint_details.get('resolutionDate', '')
    }
    
    turkish_environmental_conditions = {
        'roomTemperature': room_temperature,
        'ventilation': turkish_ventilation,
        'recentEnvironmentalChanges': turkish_changes
    }
    
    turkish_customer_acknowledgment = {
        'preferredResolution': turkish_resolution,
        'availabilityForServiceVisit': customer_acknowledgment.get('availabilityForServiceVisit', []),
        'additionalComments': turkish_comments
    }
    
    return turkish_complaint_details, turkish_environmental_conditions, turkish_customer_acknowledgment

def update_turkish_complaints():
    """Update complaints from Turkey to have Turkish text."""
    conn = connect_to_db()
    if not conn:
        logger.error("Failed to connect to database")
        return
    
    cursor = conn.cursor()
    
    try:
        # Get all complaints from Turkey
        cursor.execute("""
            SELECT id, data 
            FROM complaints 
            WHERE data->'customerInformation'->>'country' = 'Turkey'
        """)
        
        turkish_complaints = cursor.fetchall()
        
        if not turkish_complaints:
            logger.info("No Turkish complaints found in the database")
            cursor.close()
            conn.close()
            return
            
        logger.info(f"Found {len(turkish_complaints)} Turkish complaints to update")
        
        # Update each Turkish complaint with Turkish text
        update_count = 0
        for complaint_id, data in turkish_complaints:
            # Convert complaint data to Python dict
            complaint_data = data
            
            # Generate Turkish versions of the relevant sections
            turkish_complaint_details, turkish_environmental_conditions, turkish_customer_acknowledgment = generate_turkish_complaint_details(complaint_data)
            
            # Update the sections in the complaint data
            complaint_data['complaintDetails'] = turkish_complaint_details
            complaint_data['environmentalConditions'] = turkish_environmental_conditions
            complaint_data['customerAcknowledgment'] = turkish_customer_acknowledgment
            
            # Update the record in the database
            cursor.execute(
                "UPDATE complaints SET data = %s WHERE id = %s",
                (json.dumps(complaint_data), complaint_id)
            )
            
            update_count += 1
            if update_count % 10 == 0:
                conn.commit()
                logger.info(f"Updated {update_count} Turkish complaints")
        
        # Final commit
        conn.commit()
        logger.info(f"Successfully updated {update_count} Turkish complaints with Turkish text")
        
        # Show a sample of updated complaints
        show_samples(cursor)
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error updating Turkish complaints: {e}")
        if conn:
            conn.close()

def show_samples(cursor):
    """Show some samples of updated Turkish complaints."""
    cursor.execute("""
        SELECT id, data->'customerInformation'->>'fullName', 
               data->'complaintDetails'->>'detailedDescription'
        FROM complaints
        WHERE data->'customerInformation'->>'country' = 'Turkey'
        LIMIT 5
    """)
    samples = cursor.fetchall()
    
    logger.info("Sample updated Turkish complaints:")
    for sample_id, name, description in samples:
        logger.info(f"ID: {sample_id}, Customer: {name}")
        logger.info(f"Description: {description[:100]}...")
        logger.info("-" * 50)

if __name__ == "__main__":
    logger.info("Starting Turkish complaint update...")
    update_turkish_complaints()
    logger.info("Turkish complaint update completed.") 