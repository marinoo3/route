"""
Application configuration loaded from environment variables.

This module exposes a singleton `settings` instance that can be imported
throughout the project (e.g., from app.config import settings).
"""

from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    APP_NAME: str = "me.exe"
    APP_DESCRIPTION: str = "Personal chatbot API"
    APP_VERSION: str = "0.1.1"
    ENVIRONMENT: str = Field(default="production", validation_alias="ENV")

    DB_URL: str = Field(..., alias="db_url")
    DB_USERNAME: SecretStr = Field(..., alias="db_username")
    DB_PASSWORD: SecretStr = Field(..., alias="db_password")


settings = Settings() #type: ignore