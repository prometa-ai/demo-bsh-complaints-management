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

# Initialize faker for each supported country
country_locales = {
    "Norway": "no_NO",
    "Spain": "es_ES",
    "Bulgaria": "bg_BG",
    "Italy": "it_IT",
    "Portugal": "pt_PT",
    "Romania": "ro_RO",
    "Turkey": "tr_TR",
    "Egypt": "ar_EG",
    "Kuwait": "ar_SA",  # Use Saudi Arabia locale for Kuwait
    "United Arab Emirates": "en_GB",  # Use UK locale for UAE
    "Germany": "de_DE",
    "United States": "en_US",
}

# Initialize faker instances for each locale
faker_instances = {}
for country, locale in country_locales.items():
    faker_instances[country] = Faker(locale)

# Default for countries not in our mapping
default_faker = Faker("en_US")

# Places of purchase for each country
purchase_places = {
    "Norway": ["Elkjøp", "Power", "Expert", "NetOnNet", "Skousen"],
    "Spain": ["MediaMarkt", "El Corte Inglés", "Worten", "FNAC", "Carrefour"],
    "Bulgaria": ["Technopolis", "Technomarket", "Zora", "Techmart", "Metro"],
    "Italy": ["MediaWorld", "Unieuro", "Euronics", "Expert", "Trony"],
    "Portugal": ["Worten", "MediaMarkt", "Rádio Popular", "Fnac", "El Corte Inglés"],
    "Romania": ["Altex", "Media Galaxy", "Flanco", "eMAG", "Carrefour"],
    "Turkey": ["Teknosa", "MediaMarkt", "Bimeks", "Vatan", "Arçelik"],
    "Egypt": ["Carrefour", "Raya", "B.Tech", "Radio Shack", "2B"],
    "Kuwait": ["X-cite", "Eureka", "Best Al-Yousifi", "Lulu Hypermarket", "Carrefour"],
    "United Arab Emirates": ["Sharaf DG", "Jumbo Electronics", "Emax", "Carrefour", "Lulu"],
    "Germany": ["MediaMarkt", "Saturn", "Expert", "Euronics", "Conrad"],
    "United States": ["Best Buy", "Home Depot", "Walmart", "Target", "Costco", "Lowe's"],
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

def generate_country_data(country):
    """Generate customer data appropriate for the given country."""
    # Get the right faker instance
    faker = faker_instances.get(country, default_faker)
    
    # Generate name
    name = faker.name()
    
    # Generate address
    address = faker.street_address()
    city = faker.city()
    postal_code = faker.postcode()
    
    # Generate contact info
    phone = faker.phone_number()
    
    # Generate email (using ASCII characters for compatibility)
    name_parts = ''.join(c for c in name.lower() if c.isalnum())[:10]
    email = f"{name_parts}{random.randint(1, 999)}@example.com"
    
    # Generate a place of purchase appropriate for the country
    place_of_purchase = random.choice(purchase_places.get(country, purchase_places["United States"]))
    
    # Create state/province only for countries that use them
    state_province = ""
    if country in ["United States"]:
        state_province = faker.state()
    
    return {
        "customer": {
            "fullName": name,
            "address": address,
            "city": city,
            "stateProvince": state_province,
            "postalCode": postal_code,
            "phoneNumber": phone,
            "emailAddress": email,
            "country": country
        },
        "purchase": {
            "placeOfPurchase": place_of_purchase
        }
    }

def update_customer_data():
    """Update all customer data to be consistent with their country."""
    conn = connect_to_db()
    if not conn:
        logger.error("Failed to connect to database")
        return
    
    cursor = conn.cursor()
    
    try:
        # Get all complaints
        cursor.execute("SELECT id, data FROM complaints")
        complaints = cursor.fetchall()
        logger.info(f"Found {len(complaints)} complaints to update")
        
        # Count by country before update
        cursor.execute("""
            SELECT 
                data->'customerInformation'->>'country' as country,
                COUNT(*) as count
            FROM complaints
            GROUP BY country
            ORDER BY count DESC
        """)
        country_counts = cursor.fetchall()
        logger.info("Country distribution before update:")
        for country, count in country_counts:
            logger.info(f"  {country or 'Unknown'}: {count} complaints")
        
        # Update each complaint
        update_count = 0
        for complaint_id, data in complaints:
            # Extract country or assign United States if not specified
            country = data.get('customerInformation', {}).get('country')
            if not country:
                # Randomly assign a country if none exists
                country = random.choice(list(country_locales.keys()))
                logger.debug(f"Complaint {complaint_id} has no country, assigning {country}")
            
            # Generate new data for this country
            country_specific_data = generate_country_data(country)
            
            # Update customer information
            if 'customerInformation' not in data:
                data['customerInformation'] = {}
            
            # Merge the new customer data
            customer_data = country_specific_data['customer']
            data['customerInformation'].update(customer_data)
            
            # Update place of purchase
            if 'productInformation' in data:
                data['productInformation']['placeOfPurchase'] = country_specific_data['purchase']['placeOfPurchase']
            
            # Update the record in the database
            cursor.execute(
                "UPDATE complaints SET data = %s WHERE id = %s",
                (json.dumps(data), complaint_id)
            )
            
            update_count += 1
            if update_count % 100 == 0:
                conn.commit()
                logger.info(f"Updated {update_count} complaints")
        
        # Final commit
        conn.commit()
        logger.info(f"Successfully updated {update_count} complaints with country-specific customer data")
        
        # Count by country after update to verify
        cursor.execute("""
            SELECT 
                data->'customerInformation'->>'country' as country,
                COUNT(*) as count
            FROM complaints
            GROUP BY country
            ORDER BY count DESC
        """)
        country_counts_after = cursor.fetchall()
        logger.info("Country distribution after update:")
        for country, count in country_counts_after:
            logger.info(f"  {country or 'Unknown'}: {count} complaints")
        
        # Print sample data for verification
        show_samples(cursor)
        
    except Exception as e:
        logger.error(f"Error updating customer data: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def show_samples(cursor):
    """Show sample data for each country after update."""
    logger.info("Sample customer data after update:")
    
    try:
        # Get distinct countries
        cursor.execute("""
            SELECT DISTINCT data->'customerInformation'->>'country' as country
            FROM complaints
            WHERE data->'customerInformation'->>'country' IS NOT NULL
            ORDER BY country
        """)
        
        countries = [row[0] for row in cursor.fetchall()]
        
        for country in countries:
            # Get one sample complaint for each country
            cursor.execute("""
                SELECT 
                    id,
                    data->'customerInformation'->>'fullName' as name,
                    data->'customerInformation'->>'city' as city,
                    data->'customerInformation'->>'postalCode' as postal,
                    data->'customerInformation'->>'phoneNumber' as phone,
                    data->'productInformation'->>'placeOfPurchase' as store
                FROM complaints
                WHERE data->'customerInformation'->>'country' = %s
                LIMIT 1
            """, (country,))
            
            sample = cursor.fetchone()
            if sample:
                logger.info(f"{country} sample: ID {sample[0]}, Name: {sample[1]}, City: {sample[2]}, " +
                           f"Postal: {sample[3]}, Phone: {sample[4]}, Store: {sample[5]}")
    
    except Exception as e:
        logger.error(f"Error showing samples: {e}")

if __name__ == "__main__":
    logger.info("Starting customer data update...")
    update_customer_data()
    logger.info("Customer data update completed.") 