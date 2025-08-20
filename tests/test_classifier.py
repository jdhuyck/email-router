import pytest
from app.services.classifier import ClassificationService


@pytest.mark.asyncio
class TestClassificationService:
    """Test suite for ClassificationService."""

    @pytest.fixture
    def service(self):
        """Fixture to provide a service instance for tests."""
        return ClassificationService()

    async def test_classify_email_valid_text(self, service):
        """Test classification with valid email text."""
        test_text = "My product is broken and I need help getting a refund."

        result = await service.classify_email(test_text)

        assert "sequence" in result
        assert "labels" in result
        assert "scores" in result
        assert len(result["labels"]) == len(result["scores"])
        assert result["labels"][0] in ["customer support", "complaint", "billing issue"]

    async def test_classify_email_empty_text_raises_error(self, service):
        """Test that empty test raises a ValueError."""
        test_text = "    "

        with pytest.raises(ValueError, match="Email text cannot be empty."):
            await service.classify_email(test_text)

    async def test_classify_email_very_short_text(self, service):
        """Test classification with very short text."""
        # Tests model doesn't crash on minimal input
        test_text = "Hello"
        result = await service.classify_email(test_text)
        assert result is not None
