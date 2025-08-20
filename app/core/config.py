from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "AI Email Router API"
    model_name: str = "facebook/bart-large-mnli"  # Zero-shot model

    class Config:
        """Defines path for config source."""

        env_file = ".env"


@lru_cache()
def get_settings():
    """Returns settings for environment variable config."""
    return Settings()
