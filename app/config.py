"""Application configuration for the AI microservice."""

import os
from dataclasses import dataclass

# Import consul_kv first — seeds os.environ with all KV-sourced values so that
# any downstream code using os.environ.get() transparently gets Consul values.
from app.utils.consul_kv import get as kv


@dataclass(frozen=True)
class LLMConfig:
    """Configuration for the language model client."""

    api_key: str
    base_url: str | None
    chat_model: str
    summary_model: str


class BaseConfig:
    """Shared configuration values."""

    SECRET_KEY = "dev-secret-key"
    DEBUG = False
    TESTING = False
    LLM = LLMConfig(
        api_key=kv("nvidia_api_key", os.environ.get("NVIDIA_API_KEY", "")),
        base_url=kv("ai_base_url", "https://integrate.api.nvidia.com/v1"),
        chat_model=kv("chat_model", "nvidia/nemotron-3-ultra-550b-a55b"),
        summary_model=kv("summary_model", "nvidia/nemotron-3-ultra-550b-a55b"),
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
        chat_model="nvidia/nemotron-3-ultra-550b-a55b",
        summary_model="nvidia/nemotron-3-ultra-550b-a55b",
    )


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
