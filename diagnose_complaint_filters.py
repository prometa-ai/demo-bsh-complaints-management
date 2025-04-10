import psycopg2
import os
import logging
import sys
import getpass
from datetime import datetime
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
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
        conn.autocommit = True
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        sys.exit(1)

def execute_query_safe(cursor, query, params=None):
    """Execute a query safely with proper error handling."""
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        logger.error(f"Query: {query}")
        if params:
            logger.error(f"Params: {params}")
        logger.error(traceback.format_exc())
        return []

def diagnose_complaints_query():
    """Test different variations of the complaints query to identify the issue."""
    conn = connect_to_db()
    cursor = conn.cursor()
    
    # Check if we have any complaints at all
    result = execute_query_safe(cursor, "SELECT COUNT(*) FROM complaints")
    if result:
        total_complaints = result[0][0]
        logger.info(f"Total complaints in database: {total_complaints}")
    
    # Check if we have any technical notes
    result = execute_query_safe(cursor, "SELECT COUNT(*) FROM technical_notes")
    if result:
        total_notes = result[0][0]
        logger.info(f"Total technical notes in database: {total_notes}")
    
    # Check number of complaints with AI analysis
    result = execute_query_safe(cursor, """
        SELECT COUNT(DISTINCT complaint_id) 
        FROM technical_notes 
        WHERE data->'ai_analysis'->>'openai_category' IS NOT NULL
    """)
    if result:
        complaints_with_ai = result[0][0]
        logger.info(f"Complaints with AI analysis: {complaints_with_ai}")
    
    # Test different versions of the AI filter query
    
    # Version 1: Original latest_notes CTE with no extra filter
    result = execute_query_safe(cursor, """
        WITH latest_notes AS (
            SELECT DISTINCT ON (complaint_id)
                complaint_id,
                data->'ai_analysis'->>'openai_category' as ai_category
            FROM technical_notes
            WHERE data->'ai_analysis'->>'openai_category' IS NOT NULL
            AND data->'ai_analysis'->>'openai_category' != 'NO AI PREDICTION AVAILABLE'
            ORDER BY complaint_id, id DESC
        )
        SELECT COUNT(*) FROM latest_notes
    """)
    if result:
        v1_count = result[0][0]
        logger.info(f"Version 1 (no (NO OPENAI PREDICTION) filter): {v1_count} complaints")
    
    # Version 2: With the (NO OPENAI PREDICTION) filter
    result = execute_query_safe(cursor, """
        WITH latest_notes AS (
            SELECT DISTINCT ON (complaint_id)
                complaint_id,
                data->'ai_analysis'->>'openai_category' as ai_category
            FROM technical_notes
            WHERE data->'ai_analysis'->>'openai_category' IS NOT NULL
            AND data->'ai_analysis'->>'openai_category' != 'NO AI PREDICTION AVAILABLE'
            AND data->'ai_analysis'->>'openai_category' NOT LIKE '%(NO OPENAI PREDICTION)%'
            ORDER BY complaint_id, id DESC
        )
        SELECT COUNT(*) FROM latest_notes
    """)
    if result:
        v2_count = result[0][0]
        logger.info(f"Version 2 (with (NO OPENAI PREDICTION) filter): {v2_count} complaints")
    
    # Test the full filter query without any filter selections
    result = execute_query_safe(cursor, """
        WITH latest_notes AS (
            SELECT DISTINCT ON (complaint_id)
                complaint_id,
                data->'ai_analysis'->>'openai_category' as ai_category
            FROM technical_notes
            WHERE data->'ai_analysis'->>'openai_category' IS NOT NULL
            AND data->'ai_analysis'->>'openai_category' != 'NO AI PREDICTION AVAILABLE'
            AND data->'ai_analysis'->>'openai_category' NOT LIKE '%(NO OPENAI PREDICTION)%'
            ORDER BY complaint_id, id DESC
        )
        SELECT 
            COUNT(*)
        FROM complaints c
        LEFT JOIN latest_notes ln ON c.id = ln.complaint_id
        LEFT JOIN (
            SELECT DISTINCT ON (complaint_id) *
            FROM technical_notes
            ORDER BY complaint_id, id DESC
        ) tn ON c.id = tn.complaint_id
        WHERE 1=1
    """)
    if result:
        full_query_count = result[0][0]
        logger.info(f"Full query with LEFT JOIN (no filters): {full_query_count} complaints")
    
    # Check categories with the (NO OPENAI PREDICTION) string
    result = execute_query_safe(cursor, """
        SELECT DISTINCT data->'ai_analysis'->>'openai_category' as category
        FROM technical_notes
        WHERE data->'ai_analysis'->>'openai_category' LIKE '%(NO OPENAI PREDICTION)%'
        LIMIT 5
    """)
    if result:
        no_openai_categories = [row[0] for row in result]
        logger.info(f"Categories with (NO OPENAI PREDICTION): {no_openai_categories}")
    
    # Sample some filtered AI categories
    result = execute_query_safe(cursor, """
        SELECT DISTINCT data->'ai_analysis'->>'openai_category' as category
        FROM technical_notes
        WHERE data->'ai_analysis'->>'openai_category' IS NOT NULL
        AND data->'ai_analysis'->>'openai_category' != 'NO AI PREDICTION AVAILABLE'
        AND data->'ai_analysis'->>'openai_category' NOT LIKE '%(NO OPENAI PREDICTION)%'
        LIMIT 5
    """)
    if result:
        filtered_categories = [row[0] for row in result]
        logger.info(f"Sample filtered AI categories: {filtered_categories}")
    
        # Test with a specific AI category
        if filtered_categories:
            test_category = filtered_categories[0]
            result = execute_query_safe(cursor, """
                WITH latest_notes AS (
                    SELECT DISTINCT ON (complaint_id)
                        complaint_id,
                        data->'ai_analysis'->>'openai_category' as ai_category
                    FROM technical_notes
                    WHERE data->'ai_analysis'->>'openai_category' IS NOT NULL
                    AND data->'ai_analysis'->>'openai_category' != 'NO AI PREDICTION AVAILABLE'
                    AND data->'ai_analysis'->>'openai_category' NOT LIKE '%(NO OPENAI PREDICTION)%'
                    ORDER BY complaint_id, id DESC
                )
                SELECT 
                    COUNT(*)
                FROM complaints c
                JOIN latest_notes ln ON c.id = ln.complaint_id
                LEFT JOIN (
                    SELECT DISTINCT ON (complaint_id) *
                    FROM technical_notes
                    ORDER BY complaint_id, id DESC
                ) tn ON c.id = tn.complaint_id
                WHERE ln.ai_category = %s
            """, (test_category,))
            if result:
                specific_category_count = result[0][0]
                logger.info(f"Test with specific category '{test_category}': {specific_category_count} complaints")
    
    # Check issue with empty results by testing a simple query
    result = execute_query_safe(cursor, """
        SELECT count(*) FROM complaints
    """)
    if result:
        logger.info(f"Simple count query result: {result[0][0]}")
        
    cursor.close()
    conn.close()

if __name__ == "__main__":
    logger.info("Starting diagnosis of complaints query issues...")
    diagnose_complaints_query()
    logger.info("Diagnosis complete") 