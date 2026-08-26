from typing import List, Optional
from pydantic import BaseModel
from enum import Enum

class QualityLevel(str, Enum):
    POOR = "POOR"
    ACCEPTABLE = "ACCEPTABLE"
    EXCELLENT = "EXCELLENT"

class ObservationQuality(BaseModel):
    quality_score: float
    quality_level: QualityLevel
    issues: List[str]

class PerceptionResult(BaseModel):
    crop: str
    condition: str
    severity: float
    visible_damage: List[str]
    confidence: float
    observation_quality: ObservationQuality
    detected_regions: List[str] = []
    visual_evidence: List[str] = []
    reasoning_summary: str
    model_name: str
    inference_time_ms: float
