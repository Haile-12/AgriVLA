from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Depends
from app.persistence.mongodb.connection import get_database
from app.persistence.mongodb.repositories.users import UserRepository
from app.persistence.mongodb.repositories.sessions import SessionRepository

async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    db = get_database()
    yield db

def get_user_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_session_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> SessionRepository:
    return SessionRepository(db)
