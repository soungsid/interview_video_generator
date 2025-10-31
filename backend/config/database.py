import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

_client = None
_database = None


def get_database() -> AsyncIOMotorDatabase:
    """Get MongoDB database instance"""
    global _client, _database
    
    if _database is None:
        mongo_url = os.environ['MONGO_URL']
        db_name = os.environ['DB_NAME']
        _client = AsyncIOMotorClient(mongo_url)
        _database = _client[db_name]
    
    return _database


def close_database():
    """Close MongoDB connection"""
    global _client
    if _client:
        _client.close()
