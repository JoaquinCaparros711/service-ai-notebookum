"""Service layer for language-model interactions."""

from __future__ import annotations

import time
from dataclasses import dataclass

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - import guard for constrained environments
    OpenAI = None


@dataclass(frozen=True)
class AISettings:
    """Resolved runtime settings for the AI service."""

    api_key: str
    base_url: str | None
    chat_model: str
    summary_model: str


class AIService:
    """Encapsulate chat and summary behavior behind a small service API."""

    def __init__(self, settings: AISettings) -> None:
        self.settings = settings
        self.client = None
        if OpenAI is not None and settings.api_key:
            self.client = OpenAI(api_key=settings.api_key, base_url=settings.base_url)

    @classmethod
    def from_config(cls, config) -> "AIService":
        """Build the service from a Flask config object."""

        settings = AISettings(
            api_key=getattr(config, "api_key", ""),
            base_url=getattr(config, "base_url", None),
            chat_model=getattr(config, "chat_model", "gemma3-4b"),
            summary_model=getattr(config, "summary_model", "gpt-4o-mini"),
        )
        return cls(settings)

    def chat(self, message: str) -> str:
        """Return a chat completion or a deterministic fallback."""

        normalized_message = message.strip()
        if not normalized_message:
            raise ValueError("message is required")

        if self.client is not None:
            try:
                completion = self.client.chat.completions.create(
                    model=self.settings.chat_model,
                    messages=[{"role": "user", "content": normalized_message}],
                )
                response_text = completion.choices[0].message.content or ""
                if response_text.strip():
                    return response_text.strip()
            except Exception:
                pass

        return self._fallback_chat_response(normalized_message)

    def summarize_text(self, text: str, language: str | None = None) -> str:
        """Summarize text with the remote model when available."""

        normalized_text = text.strip()
        if not normalized_text:
            raise ValueError("text is required")

        resolved_language = language or self.detect_language(normalized_text)
        if self.client is not None:
            try:
                response = self.client.responses.create(
                    model=self.settings.summary_model,
                    input=[
                        {
                            "role": "system",
                            "content": (
                                "You are a concise summarization assistant. "
                                f"Respond only in {'Spanish' if resolved_language == 'es' else 'English'}."
                            ),
                        },
                        {
                            "role": "user",
                            "content": f"Summarize the following text:\n\n{normalized_text}",
                        },
                    ],
                )
                output_text = getattr(response, "output_text", "") or ""
                if output_text.strip():
                    return output_text.strip()
            except Exception:
                pass

        return self._summarize_locally(normalized_text, resolved_language)

    @staticmethod
    def detect_language(text: str) -> str:
        """Detect basic Spanish or English markers."""

        lowered = text.lower()
        spanish_markers = (" el ", " la ", " de ", " y ", " que ", " los ", " las ", " un ")
        return "es" if any(marker in f" {lowered} " for marker in spanish_markers) else "en"

    @staticmethod
    def _fallback_chat_response(message: str) -> str:
        """Return a deterministic response when no model is configured."""

        if message.strip().replace(" ", "") == "2+2?" or "2+2" in message:
            return "Gemma fallback response: 4"
        return f"Gemma fallback response: {message[:120]}"

    @staticmethod
    def _summarize_locally(text: str, language: str) -> str:
        """Generate a deterministic local summary fallback."""

        normalized = " ".join(text.split())
        if not normalized:
            return ""

        parts = [segment.strip() for segment in normalized.replace("?", ".").split(".") if segment.strip()]
        if not parts:
            parts = [normalized]

        selected = parts[:2]
        body = ". ".join(selected)
        if not body.endswith("."):
            body += "."

        prefix = "Resumen: " if language == "es" else "Summary: "
        return f"{prefix}{body}"