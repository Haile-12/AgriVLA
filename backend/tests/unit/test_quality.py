"""
Unit tests for ImageQualityAssessor
"""
import pytest
from io import BytesIO
from PIL import Image
from app.perception.quality import QualityAssessor, QualityLevel

def make_image_bytes(width=512, height=512, color=(100, 150, 80)) -> bytes:
    img = Image.new("RGB", (width, height), color=color)
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

class TestQualityAssessor:
    def setup_method(self):
        self.assessor = QualityAssessor()

    def test_excellent_image(self):
        data = make_image_bytes()
        result = self.assessor.assess(data)
        assert result.quality_level == QualityLevel.EXCELLENT
        assert result.quality_score >= 0.8
        assert len(result.issues) == 0

    def test_too_small_image(self):
        data = make_image_bytes(width=100, height=100)
        result = self.assessor.assess(data)
        assert result.quality_level in [QualityLevel.POOR, QualityLevel.ACCEPTABLE]
        assert any("too small" in i for i in result.issues)

    def test_too_dark_image(self):
        data = make_image_bytes(color=(5, 5, 5))
        result = self.assessor.assess(data)
        assert any("dark" in i for i in result.issues)

    def test_overexposed_image(self):
        data = make_image_bytes(color=(250, 250, 250))
        result = self.assessor.assess(data)
        assert any("overexposed" in i for i in result.issues)

    def test_invalid_image(self):
        result = self.assessor.assess(b"not_an_image")
        assert result.quality_level == QualityLevel.POOR
        assert result.quality_score == 0.0
