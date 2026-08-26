from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.domain.sessions import UserSession, SessionStatus
from app.persistence.mongodb.collections import Collections
from datetime import datetime
import uuid

class SessionRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[Collections.SESSIONS]

    async def create(self, user_id: str, token_id: str, expires_at: datetime, user_agent: Optional[str] = None, ip_address_hash: Optional[str] = None) -> UserSession:
        session = UserSession(
            _id=str(uuid.uuid4()),
            user_id=user_id,
            token_id=token_id,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address_hash=ip_address_hash
        )
        
        await self.collection.insert_one(session.model_dump(by_alias=True))
        return session

    async def get_by_token_id(self, token_id: str) -> Optional[UserSession]:
        session_doc = await self.collection.find_one({"token_id": token_id})
        if session_doc:
            return UserSession(**session_doc)
        return None

    async def revoke_session(self, token_id: str) -> None:
        await self.collection.update_one(
            {"token_id": token_id},
            {
                "$set": {
                    "status": SessionStatus.REVOKED,
                    "revoked_at": datetime.utcnow()
                }
            }
        )

    async def update_activity(self, token_id: str) -> None:
        await self.collection.update_one(
            {"token_id": token_id},
            {"$set": {"last_activity_at": datetime.utcnow()}}
        )
