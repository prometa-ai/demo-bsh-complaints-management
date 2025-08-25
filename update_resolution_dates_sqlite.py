#!/usr/bin/env python3
"""
Update resolution dates for resolved complaints in SQLite database
"""

import os
import sqlite3
import json
import random
import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def connect_to_db():
    """Connect to the SQLite database using the same logic as the app (Cloud Storage aware)."""
    # Try using Cloud Storage DB helper if available
    try:
        from cloud_storage_db import cloud_db
        conn = cloud_db.connect()
        if conn:
            return conn
        logger.warning("cloud_db.connect() returned None, falling back to DB_PATH/local path")
    except Exception as e:
        logger.info(f"Cloud Storage DB not available or failed ({e}), falling back to DB_PATH/local path")

    # Fallback: use DB_PATH or default local file
    try:
        db_path = os.getenv('DB_PATH', 'bsh_complaints.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
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
            WHERE json_extract(data, '$.complaintDetails.resolutionStatus') = 'Resolved'
              AND json_extract(data, '$.complaintDetails.resolutionDate') IS NULL
        """)
        
        resolved_complaints = cursor.fetchall()
        logger.info(f"Found {len(resolved_complaints)} resolved complaints missing resolutionDate")
        
        # Define typical resolution time ranges (in days) for different brands
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
            # Parse JSON data if it's a string
            if isinstance(data, str):
                data = json.loads(data)
            
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
                    "UPDATE complaints SET data = ? WHERE id = ?",
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
                COALESCE(json_extract(data, '$.productInformation.brand'), 'Unknown') as brand,
                ROUND(AVG(
                    CAST(
                        (julianday(json_extract(data, '$.complaintDetails.resolutionDate')) - 
                         julianday(json_extract(data, '$.complaintDetails.dateOfComplaint'))) AS REAL
                    ), 1
                ) as avg_days,
                COUNT(*) as count
            FROM complaints
            WHERE json_extract(data, '$.complaintDetails.resolutionStatus') = 'Resolved'
            AND json_extract(data, '$.complaintDetails.resolutionDate') IS NOT NULL
            GROUP BY brand
            ORDER BY avg_days ASC
        """)
        
        results = cursor.fetchall()
        logger.info("Brand resolution time statistics:")
        for brand, avg_days, count in results:
            if avg_days is not None:
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
