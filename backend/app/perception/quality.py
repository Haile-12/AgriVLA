from io import BytesIO
from PIL import Image, ImageStat
from app.domain.observations import ObservationQuality, QualityLevel

class QualityAssessor:
    """Evaluates image quality deterministically (blur, brightness, size)."""
    
    MIN_DIMENSION = 224
    
    def assess(self, image_bytes: bytes) -> ObservationQuality:
        issues = []
        score = 1.0
        
        try:
            image = Image.open(BytesIO(image_bytes))
            image.load()
        except Exception:
            return ObservationQuality(
                quality_score=0.0,
                quality_level=QualityLevel.POOR,
                issues=["Invalid image format"]
            )
            
        width, height = image.size
        
        # Check resolution
        if width < self.MIN_DIMENSION or height < self.MIN_DIMENSION:
            issues.append(f"Image too small ({width}x{height})")
            score -= 0.4
            
        # Check brightness (basic heuristic)
        if image.mode in ("RGB", "L"):
            stat = ImageStat.Stat(image.convert("L"))
            mean_brightness = stat.mean[0]
            if mean_brightness < 30:
                issues.append("Image is too dark")
                score -= 0.3
            elif mean_brightness > 230:
                issues.append("Image is overexposed")
                score -= 0.3
                
        score = max(0.0, min(1.0, score))
        
        if score >= 0.8:
            level = QualityLevel.EXCELLENT
        elif score >= 0.5:
            level = QualityLevel.ACCEPTABLE
        else:
            level = QualityLevel.POOR
            
        return ObservationQuality(
            quality_score=score,
            quality_level=level,
            issues=issues
        )
