from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

class MongoDBClient:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

db_client = MongoDBClient()

async def connect_to_mongo():
    logger.info("Connecting to MongoDB...")
    db_client.client = AsyncIOMotorClient(settings.MONGODB_URI)
    db_client.db = db_client.client[settings.MONGODB_DATABASE]
    logger.info("Successfully connected to MongoDB.")

async def close_mongo_connection():
    logger.info("Closing MongoDB connection...")
    if db_client.client:
        db_client.client.close()
        logger.info("MongoDB connection closed.")

def get_database() -> AsyncIOMotorDatabase:
    """Dependency injection helper"""
    return db_client.db
