from transformers import pipeline

from app.core.config import get_settings

settings = get_settings()


class ClassificationService:
    """Service for handling email text classification."""

    def __init__(self):
        # Initialize the zero-shot classification pipeline
        # Downloads model on first run
        self.classifier = pipeline(
            "zero-shot-classification",
            model=settings.model_name
        )
        # Define the candidate labels for routing
        self.candidate_labels = [
            "customer support",
            "sales inquiry",
            "billing issue",
            "complaint",
            "feedback"
        ]

    async def classify_email(self, email_text: str) -> dict:
        """
        Classify the given email text into one of the predefined categories.

        Args:
            email_text (str): The body of the email to classify.

        Returns:
            dict: The result from the classifier,
                  including scores for each label.
        """
        # Runs synchronously to avoid blocking event loop.
        # FastAPI handles this using run_in_executor.
        # Run directly for now - to scale offload this to a worker process.
        if not email_text.strip():
            raise ValueError("Email text cannot be empty.")

        result = self.classifier(
            email_text,
            candidate_labels=self.candidate_labels,
            multi_label=False
        )
        return result


# Global instance to be importer and used
# Model only loads once on application start
classification_service = ClassificationService()
