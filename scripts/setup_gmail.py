#!/usr/bin/env python3
# Script to perform initial Gmail OAuth authentication.
# Run this once to generate token.json.
from app.services.gmail_client import GmailService


def main():  # noqa:D103
    print("Setting up Gmail authentication...")
    print("This will open a browser window for you to authenticate.")

    # This will trigger authentication and create token.json
    service = GmailService()
    print("Authentication successful! token.json has been created.")

    # Test that it works
    emails = service.get_unread_emails(max_results=1)
    if emails:
        print(f"Found {len(emails)} unread emails")
    else:
        print("No unread emails found (this is normal)")


if __name__ == "__main__":
    main()
