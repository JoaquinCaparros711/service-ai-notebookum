"""AI endpoints for chat and text summarization."""

from flask import Blueprint, current_app, jsonify, request


intelligence_bp = Blueprint("intelligence", __name__)


@intelligence_bp.post("/api/chat")
def chat():
    """Send a prompt to the configured language model."""

    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "message is required"}), 400

    response_text = current_app.ai_service.chat(message)
    return jsonify({"response": response_text}), 200


@intelligence_bp.post("/api/summarize")
def summarize():
    """Summarize structured or free-form text."""

    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "text is required"}), 400

    language = data.get("language")
    summary = current_app.ai_service.summarize_text(text, language=language)
    return jsonify({"summary": summary}), 200