import logging
from typing import Optional
from app.perception.interfaces import VisionPerceptionProvider
from app.perception.quality import QualityAssessor, QualityLevel
from app.domain.observations import PerceptionResult
from app.config.settings import settings

logger = logging.getLogger(__name__)

class PerceptionEngine:
    """
    Coordinates image quality assessment and delegates to the configured VLM provider.
    """
    def __init__(self, provider: VisionPerceptionProvider):
        self.provider = provider
        self.quality_assessor = QualityAssessor()
        self.high_conf_thresh = settings.HIGH_CONFIDENCE_THRESHOLD
        self.med_conf_thresh = settings.MEDIUM_CONFIDENCE_THRESHOLD

    async def observe(self, image_bytes: bytes) -> PerceptionResult:
        """
        1. Evaluates image quality.
        2. If quality is completely unacceptable, returns early with low confidence.
        3. Otherwise, delegates to the VLM provider.
        4. Injects the quality assessment into the PerceptionResult.
        5. Adjusts confidence based on image quality.
        """
        logger.info("Assessing image quality...")
        quality = self.quality_assessor.assess(image_bytes)
        
        # If image is completely broken or too small to evaluate
        if quality.quality_level == QualityLevel.POOR and quality.quality_score < 0.2:
            logger.warning("Image quality too poor to attempt inference.")
            return PerceptionResult(
                crop="unknown",
                condition="unknown",
                severity=0.0,
                visible_damage=[],
                confidence=0.0,
                observation_quality=quality,
                reasoning_summary="Image quality is too poor to evaluate.",
                model_name="N/A",
                inference_time_ms=0.0
            )
            
        logger.info(f"Image quality acceptable ({quality.quality_score}). Delegating to model...")
        
        # Run inference
        result = await self.provider.observe(image_bytes)
        
        # Override the dummy quality injected by the provider with the real assessment
        result.observation_quality = quality
        
        # Heuristic: Cap the model's self-reported confidence based on objective image quality
        # e.g., if the image is blurry, the model shouldn't be 99% confident
        max_allowed_confidence = min(1.0, quality.quality_score + 0.2)
        if result.confidence > max_allowed_confidence:
            logger.info(f"Capping model confidence from {result.confidence} to {max_allowed_confidence} due to image quality.")
            result.confidence = max_allowed_confidence
            
        return result
