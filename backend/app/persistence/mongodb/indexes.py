from motor.motor_asyncio import AsyncIOMotorDatabase
from app.persistence.mongodb.collections import Collections
import pymongo
import logging

logger = logging.getLogger(__name__)

async def create_indexes(db: AsyncIOMotorDatabase):
    """Creates required MongoDB indexes if they don't exist."""
    logger.info("Creating MongoDB indexes...")
    
    try:
        # Users indexes
        await db[Collections.USERS].create_index(
            [("email", pymongo.ASCENDING)], unique=True
        )

        # Sessions indexes
        await db[Collections.SESSIONS].create_index([("user_id", pymongo.ASCENDING)])
        await db[Collections.SESSIONS].create_index([("token_id", pymongo.ASCENDING)], unique=True)
        await db[Collections.SESSIONS].create_index([("expires_at", pymongo.ASCENDING)])

        # Agent sessions indexes
        await db[Collections.AGENT_SESSIONS].create_index([
            ("user_id", pymongo.ASCENDING),
            ("created_at", pymongo.DESCENDING)
        ])
        await db[Collections.AGENT_SESSIONS].create_index([
            ("user_id", pymongo.ASCENDING),
            ("status", pymongo.ASCENDING)
        ])

        # Agent states indexes
        await db[Collections.AGENT_STATES].create_index([
            ("agent_session_id", pymongo.ASCENDING),
            ("step_number", pymongo.ASCENDING)
        ])

        # Trajectories indexes
        await db[Collections.TRAJECTORIES].create_index([
            ("user_id", pymongo.ASCENDING),
            ("created_at", pymongo.DESCENDING)
        ])

        logger.info("Successfully created MongoDB indexes.")
    except Exception as e:
        logger.error(f"Failed to create MongoDB indexes: {e}")
        raise
