import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.server_api import ServerApi

logger = logging.getLogger(__name__)

_client = None
_database = None


def get_database() -> AsyncIOMotorDatabase:
    """Get MongoDB database instance with Atlas support"""
    global _client, _database
    
    if _database is None:
        mongo_url = os.environ['MONGO_URL']
        db_name = os.environ['DB_NAME']
        
        # Support for MongoDB Atlas with SRV and ServerAPI
        try:
            if 'mongodb+srv://' in mongo_url:
                # MongoDB Atlas connection
                _client = AsyncIOMotorClient(
                    mongo_url,
                    server_api=ServerApi('1'),
                    serverSelectionTimeoutMS=5000
                )
                logger.info("Connected to MongoDB Atlas with SRV")
            else:
                # Local MongoDB connection
                _client = AsyncIOMotorClient(mongo_url)
                logger.info("Connected to local MongoDB")
            
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
