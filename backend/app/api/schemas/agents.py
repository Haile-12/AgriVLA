from pydantic import BaseModel
from typing import Optional

class AgentSessionCreate(BaseModel):
    title: str
    goal: str
    scenario_id: Optional[str] = None

class AgentStepRequest(BaseModel):
    observation_ref: Optional[str] = None
    # In a real API, the image would be sent as multipart/form-data.
    # For this schema we accept an optional base64 encoded image or rely on form-data in the route.
    image_base64: Optional[str] = None 
