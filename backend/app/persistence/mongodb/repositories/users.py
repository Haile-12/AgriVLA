from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.domain.users import UserInDB, UserCreate
from app.persistence.mongodb.collections import Collections
from datetime import datetime
import uuid

class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[Collections.USERS]

    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        user_doc = await self.collection.find_one({"email": email.lower()})
        if user_doc:
            return UserInDB(**user_doc)
        return None

    async def get_by_id(self, user_id: str) -> Optional[UserInDB]:
        user_doc = await self.collection.find_one({"_id": user_id})
        if user_doc:
            return UserInDB(**user_doc)
        return None

    async def create(self, user: UserCreate, password_hash: str) -> UserInDB:
        user_in_db = UserInDB(
            _id=str(uuid.uuid4()),
            email=user.email.lower(),
            display_name=user.display_name,
            password_hash=password_hash,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        await self.collection.insert_one(user_in_db.model_dump(by_alias=True))
        return user_in_db

    async def update_last_login(self, user_id: str) -> None:
        await self.collection.update_one(
            {"_id": user_id},
            {"$set": {"last_login_at": datetime.utcnow(), "updated_at": datetime.utcnow()}}
        )
