from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.domain.agents import AgentSession, AgentSessionStatus
from app.persistence.mongodb.collections import Collections
from datetime import datetime
import uuid
import pymongo

class AgentSessionRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[Collections.AGENT_SESSIONS]

    async def create(self, user_id: str, title: str, goal: str, scenario_id: Optional[str] = None) -> AgentSession:
        session = AgentSession(
            _id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            goal=goal,
            scenario_id=scenario_id
        )
        await self.collection.insert_one(session.model_dump(by_alias=True))
        return session

    async def get_by_id(self, user_id: str, agent_session_id: str) -> Optional[AgentSession]:
        doc = await self.collection.find_one({"_id": agent_session_id, "user_id": user_id})
        if doc:
            return AgentSession(**doc)
        return None

    async def list_by_user(self, user_id: str, limit: int = 20) -> List[AgentSession]:
        cursor = self.collection.find({"user_id": user_id}).sort("created_at", pymongo.DESCENDING).limit(limit)
        sessions = []
        async for doc in cursor:
            sessions.append(AgentSession(**doc))
        return sessions

    async def update_status(self, user_id: str, agent_session_id: str, status: AgentSessionStatus, termination_reason: Optional[str] = None) -> None:
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        if status in [AgentSessionStatus.COMPLETED, AgentSessionStatus.ESCALATED, AgentSessionStatus.FAILED]:
            update_data["completed_at"] = datetime.utcnow()
            update_data["termination_reason"] = termination_reason
            
        await self.collection.update_one(
            {"_id": agent_session_id, "user_id": user_id},
            {"$set": update_data}
        )

    async def delete(self, user_id: str, agent_session_id: str) -> bool:
        result = await self.collection.delete_one({"_id": agent_session_id, "user_id": user_id})
        return result.deleted_count > 0
