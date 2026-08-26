import asyncio
import logging
from app.config.settings import settings
from app.persistence.mongodb.connection import connect_to_mongo, close_mongo_connection, get_database
from app.persistence.mongodb.indexes import create_indexes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def initialize_database():
    """Initializes the database connections and creates required indexes."""
    logger.info("Starting database initialization...")
    try:
        await connect_to_mongo()
        db = get_database()
        
        # Verify connectivity by running a simple command
        await db.command("ping")
        logger.info("Database connectivity verified.")
        
        # Create indexes
        await create_indexes(db)
        
        logger.info("Database initialization completed successfully.")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(initialize_database())
