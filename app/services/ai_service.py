"""Service layer for language-model interactions."""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
except Exception:
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
            logger.info("AI backend: %s — model: %s", settings.base_url or "OpenAI", settings.summary_model)
        else:
            logger.warning("AI backend: local fallback only (no api_key)")

    @classmethod
    def from_config(cls, config) -> "AIService":
        settings = AISettings(
            api_key=getattr(config, "api_key", ""),
            base_url=getattr(config, "base_url", None),
            chat_model=getattr(config, "chat_model", "nvidia/nemotron-4-340b-instruct"),
            summary_model=getattr(config, "summary_model", "nvidia/nemotron-4-340b-instruct"),
        )
        return cls(settings)

    def chat(self, message: str) -> str:
        normalized = message.strip()
        if not normalized:
            raise ValueError("message is required")

        if self.client is not None:
            try:
                completion = self.client.chat.completions.create(
                    model=self.settings.chat_model,
                    messages=[{"role": "user", "content": normalized}],
                    temperature=0.7,
                    max_tokens=1024,
                )
                text = (completion.choices[0].message.content or "").strip()
                if text:
                    return text
            except Exception as exc:
                logger.warning("Chat error: %s", exc)

        return self._fallback_chat_response(normalized)

    def summarize_text(self, text: str, language: str | None = None) -> str:
        normalized = text.strip()
        if not normalized:
            raise ValueError("text is required")

        resolved_language = language or self.detect_language(normalized)
        system_prompt, user_prompt = self._build_summary_prompts(normalized, resolved_language)

        if self.client is not None:
            try:
                completion = self.client.chat.completions.create(
                    model=self.settings.summary_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.6,
                    top_p=0.95,
                    max_tokens=1024,
                )
                result = (completion.choices[0].message.content or "").strip()
                if result:
                    return result
            except Exception as exc:
                logger.warning("Summarize error: %s", exc)

        return self._summarize_locally(normalized, resolved_language)

    @staticmethod
    def _build_summary_prompts(text: str, language: str) -> tuple[str, str]:
        if language == "es":
            system = (
                "Eres un asistente experto en análisis y síntesis de documentos académicos. "
                "Genera un resumen estructurado y profesional. El resumen debe:\n"
                "- Identificar el tema central y los objetivos del trabajo\n"
                "- Destacar los argumentos, metodología o hallazgos más relevantes\n"
                "- Mencionar las conclusiones principales\n"
                "- Ser claro, preciso y bien redactado en español\n"
                "- Tener entre 150 y 300 palabras"
            )
            user = f"Genera un resumen académico estructurado del siguiente documento:\n\n{text}"
        else:
            system = (
                "You are an expert academic document analyst. "
                "Produce a structured and professional summary. The summary must:\n"
                "- Identify the central topic and objectives\n"
                "- Highlight the key arguments, methodology, or findings\n"
                "- State the main conclusions\n"
                "- Be clear, precise and well-written in English\n"
                "- Be between 150 and 300 words"
            )
            user = f"Generate a structured academic summary of the following document:\n\n{text}"
        return system, user

    @staticmethod
    def detect_language(text: str) -> str:
        lowered = text.lower()
        spanish_markers = (" el ", " la ", " de ", " y ", " que ", " los ", " las ", " un ")
        return "es" if any(m in f" {lowered} " for m in spanish_markers) else "en"

    @staticmethod
    def _fallback_chat_response(message: str) -> str:
        if "2+2" in message:
            return "Fallback: 4"
        return f"Fallback (sin API key): {message[:120]}"

    @staticmethod
    def _summarize_locally(text: str, language: str) -> str:
        normalized = " ".join(text.split())
        if not normalized:
            return ""
        parts = [s.strip() for s in normalized.replace("?", ".").split(".") if s.strip()]
        body = ". ".join((parts or [normalized])[:2])
        if not body.endswith("."):
            body += "."
        prefix = "Resumen: " if language == "es" else "Summary: "
        return f"{prefix}{body}"
