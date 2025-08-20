import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict
import email
from email import policy
from app.core.config import get_settings


settings = get_settings()


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class GmailService:
    """Service for interacting with Gmail API."""

    def __init__(self):  # noqa:D107
        self.creds = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate and create Gmail service."""
        if os.path.exists(settings.gmail_token_path):
            self.creds = Credentials.from_authorized_user_file(
                settings.gmail.token_path, SCOPES
            )

        if not self.creds or not self.creds.valid:
            if not self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    settings.gmail_credentials_path, SCOPES
                )
                self.creds = flow.run_local_server(port=0)

            with open(settings.gmail_token_path, "w") as token:
                token.write(self.creds.to_json())

        self.service = build("gmail", "v1", credentials=self.creds)

    def get_unread_emails(self, max_results: int = 10) -> List[Dict]:
        """Fetch unread emails from Gmail."""
        try:
            results = (
                self.service.users()
                .messages()
                .list(userId="me", labelIds=["INBOX", "UNREAD"], maxResults=max_results)
                .execute()
            )

            messages = results.get("messages", [])
            email_details = []

            for message in messages:
                msg = (
                    self.service.users()
                    .messages()
                    .get(userId="me", id=message["id"], format="raw")
                    .execute()
                )

                email_data = self._parse_email(msg)
                email_data["id"] = message["id"]
                email_details.append(email_data)

            return email_details

        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

    def _parse_email(self, msg: Dict) -> Dict:
        """Parse raw email message into structured data."""
        msg_str = base64.urlsafe_b64decode(msg["raw"].encode("ASCII"))
        mime_msg = email.message_from_bytes(msg_str, policy=policy.default)

        subject = mime_msg["subject"] or "No Subject"
        sender = mime_msg["from"] or "Unknown Sender"
        date = mime_msg["date"] or "Unknown Date"

        # Extract email body
        body = ""
        if mime_msg.is_multipart():
            for part in mime_msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = mime_msg.get_payload(decode=True).decode()

        return {
            "subject": subject,
            "from": sender,
            "date": date,
            "body": body,
            "snippet": msg.get("snippet", ""),
        }

    def mark_as_processed(self, message_id: str):
        """Mark an email as read and add processed label."""
        try:
            # Remove UNREAD label
            self.service.users().messages().modify(
                userId="me", id=message_id, body={"removeLabelIds": ["UNREAD"]}
            ).execute()

            # !!! Implement label creation and application
            print(f"Marked email {message_id} as processed")

        except HttpError as error:
            print(f"Error marking email as processed: {error}")


# Global instance
gmail_service = GmailService()
