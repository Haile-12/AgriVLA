from pydantic import BaseModel
from typing import Optional

class EnvironmentState(BaseModel):
    """Hidden ground truth of the environment."""
    crop: str
    health: float = 1.0  # 1.0 is perfectly healthy, 0.0 is dead
    disease: Optional[str] = None
    disease_severity: float = 0.0
    water_level: float = 0.5  # 0.0 to 1.0
    environmental_stress: float = 0.0
    treatment_status: Optional[str] = None
    timestep: int = 0
