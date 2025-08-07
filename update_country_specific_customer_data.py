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

# Set up Faker instances for different locales
faker_instances = {
    "Norway": Faker('no_NO'),
    "Spain": Faker('es_ES'),
    "Bulgaria": Faker('bg_BG'),
    "Italy": Faker('it_IT'),
    "Portugal": Faker('pt_PT'),
    "Romania": Faker('ro_RO'),
    "Turkey": Faker('tr_TR'),
    "Egypt": Faker('ar_EG'),
    "Kuwait": Faker('ar_KW'),
    "United Arab Emirates": Faker('ar_AE'),
    "United States": Faker('en_US'),  # Default for any other countries
    "Germany": Faker('de_DE')
}

# Default locale
default_faker = Faker('en_US')

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

def get_country_faker(country):
    """Get the appropriate faker instance for a given country."""
    return faker_instances.get(country, default_faker)

def generate_country_specific_data(country):
    """Generate customer data specific to a country."""
    faker = get_country_faker(country)
    
    # Generate a name format appropriate for the country
    name = faker.name()
    
    # Generate address information
    address = faker.street_address()
    city = faker.city()
    
    # Generate postal code
    postal_code = faker.postcode()
    
    # Generate phone number
    phone = faker.phone_number()
    
    # Generate email (with ASCII-only domain)
    name_part = ''.join(c for c in name.lower() if c.isalnum())[:8]
    email = f"{name_part}{random.randint(1, 999)}@example.com"
    
    return {
        "fullName": name,
        "address": address,
        "city": city,
        "stateProvince": faker.state() if country in ["United States"] else "",
        "postalCode": postal_code,
        "phoneNumber": phone,
        "emailAddress": email
    }

def update_customer_data():
    """Update customer data to match their countries."""
    conn = connect_to_db()
    if not conn:
        logger.error("Failed to connect to database")
        return
    
    cursor = conn.cursor()
    
    try:
        # Get all complaints with their country information
        cursor.execute("""
            SELECT id, data 
            FROM complaints
            ORDER BY id
        """)
        
        all_complaints = cursor.fetchall()
        logger.info(f"Found {len(all_complaints)} complaints to update")
        
        update_count = 0
        for complaint_id, data in all_complaints:
            try:
                # Get the country from the data
                country = data.get('customerInformation', {}).get('country', 'United States')
                
                # Generate new customer data specific to that country
                new_customer_data = generate_country_specific_data(country)
                
                # Update the customer data while preserving the country
                if 'customerInformation' in data:
                    data['customerInformation'].update(new_customer_data)
                    # Make sure to preserve the country field
                    data['customerInformation']['country'] = country
                else:
                    new_customer_data['country'] = country
                    data['customerInformation'] = new_customer_data
                
                # Update the record in the database
                cursor.execute(
                    "UPDATE complaints SET data = ? WHERE id = ?",
                    (json.dumps(data), complaint_id)
                )
                
                update_count += 1
                if update_count % 100 == 0:
                    conn.commit()
                    logger.info(f"Updated {update_count} complaints")
                
            except Exception as e:
                logger.error(f"Error updating complaint {complaint_id}: {e}")
                continue
        
        # Final commit
        conn.commit()
        logger.info(f"Successfully updated {update_count} complaints with country-specific customer data")
        
        # Verify the update with a sample
        verify_update(cursor)
        
    except Exception as e:
        logger.error(f"Error in updating customer data: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def verify_update(cursor):
    """Verify the update with a sample of complaints from each country."""
    try:
        # Get counts by country
        cursor.execute("""
            SELECT 
                data->'customerInformation'->>'country' as country,
                COUNT(*) as count
            FROM complaints
            GROUP BY country
            ORDER BY count DESC
        """)
        
        country_counts = cursor.fetchall()
        logger.info("Country distribution after update:")
        for country, count in country_counts:
            logger.info(f"  {country}: {count} complaints")
        
        # For each country, get a sample complaint to verify
        for country, _ in country_counts:
            cursor.execute("""
                SELECT 
                    id, 
                    data->'customerInformation'->>'fullName' as name,
                    data->'customerInformation'->>'address' as address,
                    data->'customerInformation'->>'city' as city,
                    data->'customerInformation'->>'postalCode' as postal_code,
                    data->'customerInformation'->>'phoneNumber' as phone
                FROM complaints
                WHERE data->'customerInformation'->>'country' = %s
                LIMIT 1
            """, (country,))
            
            sample = cursor.fetchone()
            if sample:
                logger.info(f"Sample for {country}: ID: {sample[0]}, Name: {sample[1]}, Address: {sample[2]}, City: {sample[3]}, Postal: {sample[4]}, Phone: {sample[5]}")
            
    except Exception as e:
        logger.error(f"Error verifying update: {e}")

if __name__ == "__main__":
    logger.info("Starting customer data update...")
    update_customer_data()
    logger.info("Customer data update completed.") 