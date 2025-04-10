import psycopg2
import psycopg2.extras
import logging
import os
from dotenv import load_dotenv
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def connect_to_db():
    """Connect to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME", "complaints_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432")
        )
        conn.autocommit = True
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        sys.exit(1)

def get_all_complaints(page=1, items_per_page=20, search=None, time_period=None, has_notes=False, start_date=None, end_date=None, country=None, status=None, warranty=None, ai_category=None, brand=None):
    """Get all complaints with pagination and filtering."""
    try:
        conn = connect_to_db()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Base query with CTE for latest technical notes
        query = """
        WITH latest_notes AS (
            SELECT DISTINCT ON (complaint_id)
                complaint_id,
                data->'ai_analysis'->>'openai_category' as ai_category
            FROM technical_notes
            WHERE data->'ai_analysis'->>'openai_category' IS NOT NULL
            AND data->'ai_analysis'->>'openai_category' != 'NO AI PREDICTION AVAILABLE'
            ORDER BY complaint_id, id DESC
        )
        """
        
        # If AI Category filter is applied, use JOIN instead of LEFT JOIN
        if ai_category:
            query += """
            SELECT 
                c.id,
                c.data,
                tn.data as technical_notes
            FROM complaints c
            JOIN latest_notes ln ON c.id = ln.complaint_id
            LEFT JOIN (
                SELECT DISTINCT ON (complaint_id) *
                FROM technical_notes
                ORDER BY complaint_id, id DESC
            ) tn ON c.id = tn.complaint_id
            WHERE ln.ai_category = %s
            """
            params = [ai_category]
        else:
            query += """
            SELECT 
                c.id,
                c.data,
                tn.data as technical_notes
            FROM complaints c
            LEFT JOIN latest_notes ln ON c.id = ln.complaint_id
            LEFT JOIN (
                SELECT DISTINCT ON (complaint_id) *
                FROM technical_notes
                ORDER BY complaint_id, id DESC
            ) tn ON c.id = tn.complaint_id
            WHERE 1=1
            """
            params = []
        
        # Add search filter
        if search:
            search_pattern = f"%{search}%"
            query += """
            AND (
                c.data->'customerInformation'->>'fullName' ILIKE %s
                OR c.data->'productInformation'->>'modelNumber' ILIKE %s
                OR c.data->'complaintDetails'->>'detailedDescription' ILIKE %s
            )
            """
            params.extend([search_pattern, search_pattern, search_pattern])
        
        # Add time period filter
        if time_period:
            logger.info(f"Applying time period filter: {time_period}")
            
            if time_period == '24h':
                query += " AND (c.data->'complaintDetails'->>'dateOfComplaint')::timestamp >= NOW() - INTERVAL '24 hours'"
            elif time_period == '1w':
                query += " AND (c.data->'complaintDetails'->>'dateOfComplaint')::timestamp >= NOW() - INTERVAL '1 week'"
            elif time_period == '30d':
                query += " AND (c.data->'complaintDetails'->>'dateOfComplaint')::timestamp >= NOW() - INTERVAL '30 days'"
            elif time_period == '3m':
                query += " AND (c.data->'complaintDetails'->>'dateOfComplaint')::timestamp >= NOW() - INTERVAL '3 months'"
            elif time_period == '6m':
                query += " AND (c.data->'complaintDetails'->>'dateOfComplaint')::timestamp >= NOW() - INTERVAL '6 months'"
            elif time_period == '1y':
                query += " AND (c.data->'complaintDetails'->>'dateOfComplaint')::timestamp >= NOW() - INTERVAL '1 year'"
            elif time_period.startswith('custom:'):
                start_date, end_date = time_period.split(':')[1:]
                query += " AND (c.data->'complaintDetails'->>'dateOfComplaint')::timestamp BETWEEN %s::timestamp AND %s::timestamp"
                params.extend([start_date, end_date])
        
        # Add country filter
        if country:
            query += " AND c.data->'customerInformation'->>'country' = %s"
            params.append(country)
        
        # Add status filter
        if status:
            query += " AND c.data->'complaintDetails'->>'resolutionStatus' = %s"
            params.append(status)
        
        # Add warranty filter
        if warranty:
            query += " AND c.data->'warrantyInformation'->>'warrantyStatus' = %s"
            params.append(warranty)
        
        # Add brand filter
        if brand:
            query += " AND c.data->'productInformation'->>'brand' = %s"
            params.append(brand)
        
        # Add has_notes filter
        if has_notes:
            query += " AND tn.id IS NOT NULL"
        
        # Get total count
        count_query = f"""
            SELECT COUNT(*)
            FROM ({query}) AS filtered_complaints
        """
        
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        # Add pagination
        query += " ORDER BY (c.data->'complaintDetails'->>'dateOfComplaint')::timestamp DESC"
        query += " LIMIT %s OFFSET %s"
        params.extend([items_per_page, (page - 1) * items_per_page])
        
        logger.info(f"Executing query: {query}")
        logger.info(f"With parameters: {params}")
        
        cursor.execute(query, params)
        complaints = cursor.fetchall()
        
        logger.info(f"Query executed with {len(complaints)} results")
        if complaints:
            logger.info(f"First complaint ID: {complaints[0]['id']}")
        
        return complaints, total_count
        
    except Exception as e:
        logger.error(f"Error in get_all_complaints: {e}")
        return [], 0
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

def get_ai_categories():
    """Get all distinct AI categories from the database."""
    conn = connect_to_db()
    cursor = conn.cursor()
    
    query = """
    SELECT DISTINCT data->'ai_analysis'->>'openai_category' as ai_category
    FROM technical_notes
    WHERE data->'ai_analysis'->>'openai_category' IS NOT NULL
    AND data->'ai_analysis'->>'openai_category' != 'NO AI PREDICTION AVAILABLE'
    """
    
    cursor.execute(query)
    categories = [row[0] for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return categories

def test_ai_category_filter():
    """Test the AI category filter function."""
    # Get all distinct AI categories
    categories = get_ai_categories()
    logger.info(f"Found {len(categories)} distinct AI categories")
    
    for category in categories:
        logger.info(f"Testing AI category: {category}")
        complaints, count = get_all_complaints(ai_category=category, items_per_page=5)
        logger.info(f"Category '{category}' has {count} complaints")
        
        if complaints:
            for complaint in complaints:
                if isinstance(complaint, dict):
                    complaint_id = complaint['id']
                else:
                    complaint_id = complaint[0]
                logger.info(f" - Complaint ID: {complaint_id}")
        else:
            logger.info(f" - No complaints found for category '{category}'")
        
        logger.info("---")

if __name__ == "__main__":
    logger.info("Starting AI category filter test")
    test_ai_category_filter()
    logger.info("AI category filter test completed") 