import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.server_api import ServerApi
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

_client = None
_database = None


def get_database() -> AsyncIOMotorDatabase:
    """Get MongoDB database instance with Atlas support"""
    global _client, _database
    
    if _database is None:
        db_name = os.environ['DB_NAME']
        
        # Check if using MongoDB Atlas (via separate credentials)
        mongo_username = os.environ.get('MONGO_USERNAME')
        mongo_password = os.environ.get('MONGO_PASSWORD')
        mongo_cluster = os.environ.get('MONGO_CLUSTER')
        mongo_app_name = os.environ.get('MONGO_APP_NAME', 'Cluster0')
        
        # Support for MongoDB Atlas with SRV and ServerAPI
        try:
            if mongo_username and mongo_password and mongo_cluster:
                # MongoDB Atlas connection with credentials from env variables
                # URL-encode username and password to handle special characters
                username_encoded = quote_plus(mongo_username)
                password_encoded = quote_plus(mongo_password)
                
                mongo_url = f"mongodb+srv://{username_encoded}:{password_encoded}@{mongo_cluster}/?appName={mongo_app_name}"
                
                _client = AsyncIOMotorClient(
                    mongo_url,
                    server_api=ServerApi('1'),
                    serverSelectionTimeoutMS=5000
                )
                logger.info(f"Connected to MongoDB Atlas: {mongo_cluster}")
            else:
                # Fallback to MONGO_URL for local or custom connections
                mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
                _client = AsyncIOMotorClient(mongo_url)
                logger.info("Connected to MongoDB using MONGO_URL")
            
            _database = _client[db_name]
            logger.info(f"Database '{db_name}' initialized")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    return _database


def close_database():
    """Close MongoDB connection"""
    global _client
    if _client:
        _client.close()
