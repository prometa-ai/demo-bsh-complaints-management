#!/usr/bin/env python3

import psycopg2
import json
import random
import datetime
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

def update_resolution_dates():
    """Add resolution dates to resolved complaints."""
    conn = connect_to_db()
    if not conn:
        logger.error("Failed to connect to database")
        return
    
    cursor = conn.cursor()
    
    try:
        # Get all resolved complaints without resolution dates
        cursor.execute("""
            SELECT id, data 
            FROM complaints 
            WHERE data->'complaintDetails'->>'resolutionStatus' = 'Resolved'
        """)
        
        resolved_complaints = cursor.fetchall()
        logger.info(f"Found {len(resolved_complaints)} resolved complaints")
        
        # Define typical resolution time ranges (in days) for different brands
        # These are just examples - adjust as needed
        brand_resolution_times = {
            "Bosch": (3, 12),      # 3-12 days
            "Profilo": (5, 15),    # 5-15 days
            "Siemens": (4, 10),    # 4-10 days
            "Gaggenau": (2, 7),    # 2-7 days (premium brand, faster service)
            "Neff": (4, 14)        # 4-14 days
        }
        
        # Default for unknown brands
        default_time_range = (5, 20)
        
        update_count = 0
        for complaint_id, data in resolved_complaints:
            # Get the complaint date
            complaint_date_str = data.get('complaintDetails', {}).get('dateOfComplaint')
            
            if not complaint_date_str:
                logger.warning(f"Complaint {complaint_id} has no complaint date, skipping")
                continue
            
            try:
                # Parse the complaint date
                complaint_date = datetime.datetime.fromisoformat(complaint_date_str.replace('Z', '+00:00'))
                
                # Get the brand
                brand = data.get('productInformation', {}).get('brand', 'Unknown')
                
                # Get appropriate time range for the brand
                min_days, max_days = brand_resolution_times.get(brand, default_time_range)
                
                # Generate a random resolution time
                resolution_days = random.randint(min_days, max_days)
                
                # Calculate resolution date
                resolution_date = complaint_date + datetime.timedelta(days=resolution_days)
                
                # Format resolution date as ISO 8601 string
                resolution_date_str = resolution_date.isoformat()
                
                # Update the complaint data with resolution date
                if 'complaintDetails' not in data:
                    data['complaintDetails'] = {}
                
                data['complaintDetails']['resolutionDate'] = resolution_date_str
                
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
            
            except Exception as e:
                logger.error(f"Error updating complaint {complaint_id}: {e}")
                continue
        
        # Final commit
        conn.commit()
        logger.info(f"Updated resolution dates for {update_count} complaints")
        
        # Verify update - get average resolution time for each brand
        cursor.execute("""
            SELECT 
                COALESCE(data->'productInformation'->>'brand', 'Unknown') as brand,
                ROUND(AVG(
                    EXTRACT(EPOCH FROM 
                        (data->'complaintDetails'->>'resolutionDate')::timestamp - 
                        (data->'complaintDetails'->>'dateOfComplaint')::timestamp
                    ) / 86400
                )::numeric, 1) as avg_days,
                COUNT(*) as count
            FROM complaints
            WHERE data->'complaintDetails'->>'resolutionStatus' = 'Resolved'
            AND data->'complaintDetails'->>'resolutionDate' IS NOT NULL
            GROUP BY brand
            ORDER BY count DESC;
        """)
        
        results = cursor.fetchall()
        logger.info("Brand resolution time statistics:")
        for brand, avg_days, count in results:
            logger.info(f"  {brand}: {avg_days} days (average) for {count} complaints")
            
    except Exception as e:
        logger.error(f"Error updating resolution dates: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    logger.info("Starting resolution date update...")
    update_resolution_dates()
    logger.info("Resolution date update completed.") 