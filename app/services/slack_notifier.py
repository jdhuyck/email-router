import httpx
from app.core.config import get_settings
from typing import Optional


settings = get_settings()


class SlackNotifier:
    """Service for sending notifications to Slack."""

    def __init__(self):  # noqa:D107
        self.webhook_url = settings.slack_webhook_url

    async def send_notification(
        self, message: str, email_data: Optional[dict] = None
    ) -> bool:
        """Send a notification to Slack."""
        if not self.webhook_url:
            print("Slack webhook URL not configured")
            return False

        payload = self._build_payload(message, email_data)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url, json=payload, timeout=10.0
                )
                response.raise_for_status()
                return True
        except Exception as e:
            print(f"Failed to send Slack notification: {e}")
            return False

    def _build_payload(self, message: str, email_data: Optional[dict] = None) -> dict:
        """Build the Slack message payload."""
        if email_data:
            # Rich notification with email details
            return {
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"📩 *Email Processed*\n{message}",
                        },
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*From:*\n{email_data.get('from', 'Unknown')}",
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Subject:*\n{email_data.get('subject', 'No Subject')}",  # noqa:E501
                            },
                        ],
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Snippet:*\n{email_data.get('snippet', '')[:100]}...",  # noqa:E501
                        },
                    },
                ]
            }
        else:
            return {"text": message}


slack_notifier = SlackNotifier()
