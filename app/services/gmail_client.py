import base64
import datetime
import email
import os
from email import policy
from typing import Dict, List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.config import get_settings

settings = get_settings()


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class EmailContents:
    """Represents the contents of an email."""

    def __init__(  # noqa:D107
        self,
        email_id: str,
        subject: str,
        sender: str,
        body: str,
        date: datetime.datetime,
        snippet: str,
    ):
        self.email_id = email_id
        self.subject = subject
        self.sender = sender
        self.body = body
        self.date = date
        self.snippet = snippet

    def __repr__(self):  # noqa:D105
        return f"EmailContents(subject={self.subject!r}," f"sender={self.sender!r})"

    def __str__(self):  # noqa:D105
        lines = [
            f"Subject: {self.subject}",
            f"From: {self.sender}",
            "Text:",
            self._format_body_text(),
        ]

        return "\n".join(lines)

    def _format_body_text(self, max_line_length: int = 100) -> str:
        """
        Format body text based on inputted max line length.

        Args:
            max_line_length (int): Maximum number of characters on one line
        """
        if not self.body:
            return "[No Text]"

        cleaned_body_text = "\n".join(
            line.strip() for line in self.body.splitlines() if line.strip()
        )

        wrapped = []
        for line in cleaned_body_text.splitlines():
            if len(line) > max_line_length:
                wrapped.extend(
                    line[i : i + max_line_length]  # noqa:E203
                    for i in range(0, len(line), max_line_length)
                )
            else:
                wrapped.append(line)

        return "\n".join(wrapped)

    def display(self, verbose: bool = False):
        """
        Display method with formatting options.

        Args:
            verbose: If True, shows full body with original formatting
        """
        print(f"\n{'='*50}")
        print(f"Subject: {self.subject}")
        print(f"From: {self.sender}")

        print("\nBody Text")
        print(self.body if verbose else self._format_body_text())

    @property
    def text_summary(self) -> str:
        """Give a short summary of the email content."""
        body_preview = (self.body[:100] + "...") if self.body else "[No body]"
        return (
            f"Subject: {self.subject}\n"
            f"From: {self.sender}\n"
            f"Preview: {body_preview}"
        )


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
                settings.gmail_token_path, SCOPES
            )

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(settings.gmail_credentials_path):
                    raise FileNotFoundError(
                        f"Gmail credentials file not found at: {settings.gmail_credentials_path}"  # noqa:E501
                    )
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
                email_data.email_id = message["id"]
                email_details.append(email_data)

            return email_details

        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

    def _parse_email(self, msg: Dict) -> EmailContents:
        """Parse raw email message into structured data."""
        msg_str = base64.urlsafe_b64decode(msg["raw"].encode("ASCII"))
        mime_msg = email.message_from_bytes(msg_str, policy=policy.default)

        subject = mime_msg["subject"]
        sender = mime_msg["from"]
        date = mime_msg["date"]

        # Extract email body
        body = ""
        if mime_msg.is_multipart():
            for part in mime_msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = mime_msg.get_payload(decode=True).decode()

        return EmailContents(
            email_id=msg["id"],
            subject=subject,
            sender=sender,
            date=date,
            body=body,
            snippet=msg.get("snippet", ""),
        )

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
