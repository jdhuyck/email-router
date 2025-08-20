import asyncio

from app.core.config import get_settings
from app.services.classifier import classification_service
from app.services.gmail_client import EmailContents, gmail_service
from app.services.slack_notifier import slack_notifier

settings = get_settings


class EmailProcessor:
    """Service to process emails and handle routing logic."""

    def __init__(self):  # noqa:D107
        self.is_processing = False

    async def process_new_emails(self):
        """Check for and process new emails."""
        if self.is_processing:
            return

        self.is_processing = True
        try:
            emails = gmail_service.get_unread_emails(max_results=5)

            for email_data in emails:
                await self._process_single_email(email_data)
                await asyncio.sleep(1)  # Rate limiting

        finally:
            self.is_processing = False

    async def _process_single_email(self, email_data: EmailContents):
        """Process a single email through the classification pipeline."""
        try:
            # Classify the email
            classification = await classification_service.classify_email(
                email_data.body
            )

            primary_category = classification["labels"][0]
            confidence = classification["scores"][0]

            gmail_service.mark_as_processed(email_data["id"])

            message = (
                f"Email from {email_data['from']} classified as "
                f"*{primary_category}* with {confidence:.2%} confidence"
            )

            await slack_notifier.send_notification(message, email_data)

            print(f"Processed email: {email_data['subject']} -> {primary_category}")

        except Exception as e:
            error_msg = f"Error processing email '{email_data.subject}': {str(e)}"
            print(error_msg)
            await slack_notifier.send_notification(f"❌ {error_msg}")


# GLobal instance
email_processor = EmailProcessor()
