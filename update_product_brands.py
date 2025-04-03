#!/usr/bin/env python3

import psycopg2
import json
import random
import sys
import logging
import getpass

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

def update_product_brands():
    """Update product brands in the complaints database."""
    conn = connect_to_db()
    if not conn:
        logger.error("Failed to connect to database")
        return
    
    cursor = conn.cursor()
    
    try:
        # First, let's check how many complaints we have
        cursor.execute("SELECT COUNT(*) FROM complaints")
        total_complaints = cursor.fetchone()[0]
        logger.info(f"Total complaints in database: {total_complaints}")
        
        # Define the brands we want to use with their distribution percentages
        brands = {
            "Bosch": 45,  # 45% of complaints
            "Profilo": 30,  # 30% of complaints
            "Siemens": 15,  # 15% of complaints
            "Gaggenau": 5,   # 5% of complaints
            "Neff": 5        # 5% of complaints
        }
        
        # Get all complaints
        cursor.execute("SELECT id, data FROM complaints")
        all_complaints = cursor.fetchall()
        
        # Calculate how many complaints should be assigned to each brand
        brand_counts = {brand: int(total_complaints * percentage / 100) for brand, percentage in brands.items()}
        
        # Make sure all complaints are accounted for (adjust for rounding)
        remaining = total_complaints - sum(brand_counts.values())
        if remaining > 0:
            # Add remaining to the first brand
            brand_counts["Bosch"] += remaining
        
        # Create a list of brands based on their distribution
        brand_list = []
        for brand, count in brand_counts.items():
            brand_list.extend([brand] * count)
        
        # Shuffle the brand list to randomize assignment
        random.shuffle(brand_list)
        
        # Update each complaint with a brand
        update_count = 0
        for (complaint_id, data), brand in zip(all_complaints, brand_list):
            # Make sure productInformation exists
            if 'productInformation' not in data:
                data['productInformation'] = {}
            
            # Update the brand
            data['productInformation']['brand'] = brand
            
            # Update the record in the database
            cursor.execute(
                "UPDATE complaints SET data = %s WHERE id = %s",
                (json.dumps(data), complaint_id)
            )
            update_count += 1
            
            # Commit every 100 updates to avoid transaction timeout
            if update_count % 100 == 0:
                conn.commit()
                logger.info(f"Updated {update_count} complaints")
        
        # Final commit
        conn.commit()
        logger.info(f"Updated all {update_count} complaints with brand information")
        
        # Verify the update
        verify_brands(cursor)
        
    except Exception as e:
        logger.error(f"Error updating product brands: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def verify_brands(cursor):
    """Verify the distribution of brands in the database."""
    try:
        cursor.execute("""
            SELECT 
                data->'productInformation'->>'brand' as brand,
                COUNT(*) as count
            FROM complaints
            GROUP BY brand
            ORDER BY count DESC
        """)
        
        results = cursor.fetchall()
        logger.info("Brand distribution after update:")
        total = sum(count for _, count in results)
        for brand, count in results:
            percentage = round(count * 100 / total, 2)
            logger.info(f"  {brand}: {count} complaints ({percentage}%)")
            
    except Exception as e:
        logger.error(f"Error verifying brand distribution: {e}")

if __name__ == "__main__":
    logger.info("Starting product brand update...")
    update_product_brands()
    logger.info("Product brand update completed.") 