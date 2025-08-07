import os
import sqlite3
import tempfile
import shutil
from google.cloud import storage
import logging

logger = logging.getLogger(__name__)

class CloudStorageDB:
    """
    SQLite database with Google Cloud Storage persistence.
    Downloads DB from GCS on startup, uploads on changes.
    """
    
    def __init__(self, bucket_name=None, db_filename='bsh_complaints.db'):
        self.bucket_name = bucket_name or os.getenv('GCS_BUCKET_NAME')
        self.db_filename = db_filename
        self.local_db_path = f'/tmp/{db_filename}'
        self.client = None
        self.bucket = None
        
        # Initialize GCS client if in production
        if self._is_production():
            if not self.bucket_name:
                logger.error("GCS_BUCKET_NAME environment variable not set, falling back to local SQLite")
                return
                
            try:
                self.client = storage.Client()
                self.bucket = self.client.bucket(self.bucket_name)
                # Test the connection
                self.bucket.exists()
                logger.info(f"Initialized Cloud Storage client for bucket: {self.bucket_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Cloud Storage: {e}")
                logger.info("Falling back to local SQLite")
                self.client = None
                self.bucket = None
        else:
            logger.info("Development mode: Using local SQLite")
    
    def _is_production(self):
        """Check if running in production environment"""
        return (
            os.getenv('FLASK_ENV') == 'production' or 
            os.getenv('ENVIRONMENT') == 'production' or
            os.getenv('GAE_ENV') or  # Google App Engine
            os.getenv('K_SERVICE')   # Cloud Run
        )
    
    def get_db_path(self):
        """Get the path to the SQLite database file"""
        if self._is_production() and self.client:
            return self.local_db_path
        else:
            # Development mode - use local file
            return os.getenv('DB_PATH', 'bsh_complaints.db')
    
    def download_db_from_gcs(self):
        """Download database from Google Cloud Storage"""
        if not self.client or not self.bucket:
            logger.info("No Cloud Storage client, skipping download")
            return False
            
        try:
            blob = self.bucket.blob(self.db_filename)
            
            # Check if database exists in GCS
            if not blob.exists():
                logger.info(f"Database {self.db_filename} not found in GCS, will create new one")
                return False
            
            # Download to local temp file
            blob.download_to_filename(self.local_db_path)
            logger.info(f"Downloaded database from GCS to {self.local_db_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download database from GCS: {e}")
            return False
    
    def upload_db_to_gcs(self):
        """Upload database to Google Cloud Storage"""
        if not self.client or not self.bucket:
            logger.info("No Cloud Storage client, skipping upload")
            return False
            
        if not os.path.exists(self.local_db_path):
            logger.warning(f"Local database {self.local_db_path} not found, nothing to upload")
            return False
            
        try:
            blob = self.bucket.blob(self.db_filename)
            blob.upload_from_filename(self.local_db_path)
            logger.info(f"Uploaded database to GCS: {self.db_filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload database to GCS: {e}")
            return False
    
    def connect(self):
        """Get a connection to the SQLite database"""
        db_path = self.get_db_path()
        
        # In production, ensure we have the latest DB from GCS
        if self._is_production() and self.client:
            # Only download if local file doesn't exist
            if not os.path.exists(self.local_db_path):
                success = self.download_db_from_gcs()
                if not success:
                    logger.info("Failed to download from GCS, creating new local database")
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            
            logger.debug(f"Connected to SQLite database at {db_path}")
            return conn
            
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            # In production, if database fails, try to create a minimal one
            if self._is_production():
                try:
                    # Create a basic database in memory as last resort
                    conn = sqlite3.connect(':memory:')
                    conn.row_factory = sqlite3.Row
                    logger.warning("Using in-memory database as fallback")
                    return conn
                except:
                    pass
            return None
    
    def backup_to_gcs(self):
        """Manual backup to GCS (called after significant changes)"""
        if self._is_production() and self.client:
            return self.upload_db_to_gcs()
        return True
    
    def initialize_db_if_needed(self):
        """Initialize database and download from GCS if available"""
        if self._is_production() and self.client:
            # Try to download existing DB from GCS
            if not self.download_db_from_gcs():
                logger.info("No existing database in GCS, will create new one")
                
                # Create local DB path directory if needed
                os.makedirs(os.path.dirname(self.local_db_path), exist_ok=True)
        
        return True

# Global instance
cloud_db = CloudStorageDB()
