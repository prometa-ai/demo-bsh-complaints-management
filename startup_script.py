#!/usr/bin/env python3
"""
Startup script for BSH Complaints Management System.
This script ensures the database is properly initialized before the Flask app starts.
"""

import os
import sys
import time
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_startup_checks():
    """Run all necessary startup checks and initializations."""
    logger.info("Starting BSH Complaints Management System initialization...")
    
    # Check if we're in production
    is_production = (
        os.getenv('FLASK_ENV') == 'production' or 
        os.getenv('ENVIRONMENT') == 'production' or
        os.getenv('GAE_ENV') or  # Google App Engine
        os.getenv('K_SERVICE')   # Cloud Run
    )
    
    logger.info(f"Environment: {'Production' if is_production else 'Development'}")
    
    # Attempt to load secrets from Secret Manager before checking env vars
    try:
        from secrets_manager import load_secrets_to_env
        load_secrets_to_env()
    except Exception as e:
        logger.info(f"Skipping Secret Manager preload: {e}")

    # Check required environment variables
    required_vars = ['OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"Missing environment variables: {missing_vars}")
        logger.warning("Some features may not work properly")
    
    # Initialize database
    try:
        logger.info("Initializing database...")
        
        # Import and run database setup
        from setup_database import setup_database
        if setup_database():
            logger.info("Database setup completed successfully")
        else:
            logger.error("Database setup failed")
            return False
        
        # Check if database has data
        import sqlite3
        db_path = os.getenv('DB_PATH', 'bsh_complaints.db')
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM complaints")
            complaint_count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            logger.info(f"Database contains {complaint_count} complaints")
            
            # If database is empty, generate sample data
            if complaint_count == 0:
                logger.info("Database is empty. Generating sample data...")
                from regenerate_consistent_data import regenerate_database
                
                if regenerate_database():
                    logger.info("Sample data generated successfully")
                    
                    # Backup to GCS if available
                    try:
                        from cloud_storage_db import cloud_db
                        cloud_db.backup_to_gcs()
                        logger.info("Database backed up to Cloud Storage")
                    except ImportError:
                        logger.info("Cloud Storage not available, skipping backup")
                else:
                    logger.error("Failed to generate sample data")
                    return False
            else:
                logger.info("Database already contains data, skipping data generation")
                
        except Exception as e:
            logger.error(f"Error checking database: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        return False
    
    # Test OpenAI connection
    try:
        logger.info("Testing OpenAI connection...")
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != 'your-openai-api-key-here':
            client = OpenAI()
            models = client.models.list()
            logger.info(f"OpenAI connection successful: Found {len(models.data)} models")
        else:
            logger.warning("OpenAI API key not configured, AI features will be disabled")
            
    except Exception as e:
        logger.warning(f"OpenAI connection test failed: {e}")
        logger.warning("AI features may not work properly")
    
    # Test Cloud Storage connection if in production
    if is_production:
        try:
            logger.info("Testing Cloud Storage connection...")
            from cloud_storage_db import cloud_db
            
            if cloud_db.client:
                logger.info("Cloud Storage connection successful")
            else:
                logger.warning("Cloud Storage not available")
                
        except Exception as e:
            logger.warning(f"Cloud Storage connection test failed: {e}")
    
    logger.info("Startup checks completed successfully")
    return True

def main():
    """Main startup function."""
    logger.info("=" * 50)
    logger.info("BSH Complaints Management System Startup")
    logger.info("=" * 50)
    
    # Run startup checks
    if not run_startup_checks():
        logger.error("Startup checks failed. Exiting...")
        sys.exit(1)
    
    logger.info("Startup completed successfully!")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()
