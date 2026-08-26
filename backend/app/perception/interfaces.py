from abc import ABC, abstractmethod
from typing import BinaryIO
from app.domain.observations import PerceptionResult

class VisionPerceptionProvider(ABC):
    """
    Base interface for all Vision-Language Models.
    Ensures that any model (Gemini, Claude, GPT) adheres to the same contract.
    """
    
    @abstractmethod
    async def observe(self, image_bytes: bytes) -> PerceptionResult:
        """
        Takes raw image bytes, runs inference, and returns a structured PerceptionResult.
        """
        pass
