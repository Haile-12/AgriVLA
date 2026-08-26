from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.domain.trajectories import TrajectoryStep
from app.domain.states import AgentState
from app.persistence.mongodb.collections import Collections
import uuid
import pymongo

class TrajectoryRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.trajectory_col = db[Collections.TRAJECTORIES]
        self.state_col = db[Collections.AGENT_STATES]

    async def save_step(self, step: TrajectoryStep) -> TrajectoryStep:
        """Saves a complete auditable trajectory step."""
        if not getattr(step, 'step_id', None) or step.step_id == "":
             step.step_id = str(uuid.uuid4())
             
        await self.trajectory_col.insert_one(step.model_dump(by_alias=True))
        return step

    async def get_trajectory(self, user_id: str, agent_session_id: str) -> List[TrajectoryStep]:
        """Retrieves the full trajectory for a session, verifying ownership."""
        cursor = self.trajectory_col.find(
            {"user_id": user_id, "agent_session_id": agent_session_id}
        ).sort("step_number", pymongo.ASCENDING)
        
        steps = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            steps.append(TrajectoryStep(**doc))
        return steps

    async def save_latest_state(self, user_id: str, agent_session_id: str, state: AgentState) -> None:
        """Persists the most recent AgentState separately for quick access."""
        state_dict = state.model_dump()
        state_dict["user_id"] = user_id
        state_dict["agent_session_id"] = agent_session_id
        
        await self.state_col.update_one(
            {"agent_session_id": agent_session_id, "user_id": user_id},
            {"$set": state_dict},
            upsert=True
        )

    async def get_latest_state(self, user_id: str, agent_session_id: str) -> Optional[AgentState]:
        """Retrieves the most recent AgentState, verifying ownership."""
        doc = await self.state_col.find_one({"agent_session_id": agent_session_id, "user_id": user_id})
        if doc:
            # Remove persistence metadata not in the model
            doc.pop("user_id", None)
            doc.pop("agent_session_id", None)
            doc.pop("_id", None)
            return AgentState(**doc)
        return None
