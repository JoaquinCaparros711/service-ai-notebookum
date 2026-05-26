"""Application configuration for the AI microservice."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class LLMConfig:
    """Configuration for the language model client."""

    api_key: str
    base_url: str | None
    chat_model: str
    summary_model: str


class BaseConfig:
    """Shared configuration values."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    DEBUG = False
    TESTING = False
    LLM = LLMConfig(
        api_key=os.environ.get("OPENAI_API_KEY") or os.environ.get("GEMMA_API_KEY", ""),
        base_url=os.environ.get("GEMMA_API_URL"),
        chat_model=os.environ.get("GEMMA_MODEL", "gemma3-4b"),
        summary_model=os.environ.get("SUMMARY_MODEL", "gpt-4o-mini"),
    )


class DevelopmentConfig(BaseConfig):
    """Development settings."""

    DEBUG = True


class ProductionConfig(BaseConfig):
    """Production settings."""

    DEBUG = False


class TestingConfig(BaseConfig):
    """Testing settings."""

    TESTING = True
    DEBUG = True
    LLM = LLMConfig(
        api_key="",
        base_url=None,
        chat_model="gemma3-4b",
        summary_model="gpt-4o-mini",
    )


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
