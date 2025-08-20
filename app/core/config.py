from functools import lru_cache

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "AI Email Router API"
    model_name: str = "facebook/bart-large-mnli"  # Zero-shot model

    # Gmail API Configuration
    gmail_credentials_path: str = Field(
        "credentials.json", description="Path to Gmail OAuth credentials"
    )
    gmail_token_path: str = Field(
        "token.json", description="Path to store Gmail OAuth token"
    )
    gmail_poll_interval: int = Field(
        300, description="Email polling interval in seconds"
    )

    # Slack Configuration
    slack_webhook_url: str = Field(
        "", description="Slack incoming webhook URL for notifications"
    )

    # Email Processing
    processed_label: str = Field(
        "AI-Processed", description="Gmail label for processed emails"
    )

    class Config:
        """Defines path for config source."""

        env_file = ".env"


@lru_cache()
def get_settings():
    """Returns settings for environment variable config."""
    return Settings()
