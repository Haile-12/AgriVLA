import time
import json
import logging
from typing import Dict, Any

import httpx
import base64

from app.perception.interfaces import VisionPerceptionProvider
from app.domain.observations import PerceptionResult, ObservationQuality
from app.config.settings import settings

logger = logging.getLogger(__name__)

class GeminiProvider(VisionPerceptionProvider):
    """
    Integration with Google Gemini API for fast, state-of-the-art vision processing.
    """
    def __init__(self):
        self.model_name = settings.MODEL_NAME
        
        # Will automatically pick up GEMINI_API_KEY from environment/settings
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY is missing! Inference will fail.")
            
        self.api_key = settings.GEMINI_API_KEY

    async def observe(self, image_bytes: bytes) -> PerceptionResult:
        start_time = time.time()
        
        try:
            prompt_text = (
                "You are an expert agricultural vision system. Analyze this plant image.\n"
                "Provide a JSON response with the following keys exactly:\n"
                "- 'crop': name of the plant/crop\n"
                "- 'condition': disease name or 'healthy'\n"
                "- 'severity': float between 0.0 (healthy) and 1.0 (dead)\n"
                "- 'visible_damage': list of strings describing symptoms\n"
                "- 'confidence': float between 0.0 and 1.0 representing your confidence in this diagnosis\n"
                "- 'reasoning_summary': a short sentence explaining why you chose this condition\n"
            )

            # Pass image via base64 to REST API
            b64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt_text},
                            {
                                "inlineData": {
                                    "mimeType": "image/jpeg",
                                    "data": b64_image
                                }
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "temperature": 0.2
                }
            }
            
            headers = {"Content-Type": "application/json"}
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
            
            if resp.status_code != 200:
                raise RuntimeError(f"Gemini API returned {resp.status_code}: {resp.text}")
                
            resp_data = resp.json()
            response_text = resp_data["candidates"][0]["content"]["parts"][0]["text"]

            parsed_data = self._parse_json_output(response_text)
            inference_time = (time.time() - start_time) * 1000
            
            dummy_quality = ObservationQuality(quality_score=1.0, quality_level="EXCELLENT", issues=[])
            
            return PerceptionResult(
                crop=parsed_data.get("crop", "unknown"),
                condition=parsed_data.get("condition", "unknown"),
                severity=float(parsed_data.get("severity", 0.0)),
                visible_damage=parsed_data.get("visible_damage", []),
                confidence=float(parsed_data.get("confidence", 0.0)),
                observation_quality=dummy_quality,
                reasoning_summary=parsed_data.get("reasoning_summary", "No reasoning provided."),
                model_name=self.model_name,
                inference_time_ms=inference_time
            )
            
        except Exception as e:
            logger.error(f"Inference failed: {e}")
            dummy_quality = ObservationQuality(quality_score=0.0, quality_level="POOR", issues=["Inference crashed"])
            return PerceptionResult(
                crop="unknown",
                condition="unknown",
                severity=0.0,
                visible_damage=[],
                confidence=0.0,
                observation_quality=dummy_quality,
                reasoning_summary=f"Inference failed: {str(e)}",
                model_name=self.model_name,
                inference_time_ms=(time.time() - start_time) * 1000
            )

    def _parse_json_output(self, text: str) -> Dict[str, Any]:
        """Extracts JSON from the API response."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
            
        try:
            import re
            match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
        except (json.JSONDecodeError, AttributeError):
            pass
            
        return {}
