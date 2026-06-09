"""AI endpoints for chat and text summarization."""

import json
import logging
import os

from flask import Blueprint, current_app, jsonify, request

logger = logging.getLogger(__name__)

intelligence_bp = Blueprint("intelligence", __name__)


@intelligence_bp.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "message is required"}), 400

    response_text = current_app.ai_service.chat(message)
    return jsonify({"response": response_text}), 200


@intelligence_bp.post("/api/summarize")
@intelligence_bp.post("/api/v1/summaries")
def summarize():
    """Summarize free-form text received directly in the request body."""
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "text is required"}), 400

    language = data.get("language")
    summary = current_app.ai_service.summarize_text(text, language=language)
    response = {"summary": summary}
    document_id = data.get("document_id")
    if document_id:
        response["document_id"] = document_id
    return jsonify(response), 200


@intelligence_bp.post("/api/v1/summaries/document")
def summarize_from_extraction():
    """Read extracted text from Redis by document_id and return a summary.

    The Controller is responsible for saving the result to persistence.
    """
    data = request.get_json(silent=True) or {}
    document_id = (data.get("document_id") or "").strip()
    if not document_id:
        return jsonify({"error": "document_id is required"}), 400

    try:
        import redis as redis_lib
        r = redis_lib.Redis(
            host=os.environ.get("REDIS_HOST", "redis"),
            port=int(os.environ.get("REDIS_PORT", 6379)),
            password=os.environ.get("REDIS_PASSWORD") or None,
            decode_responses=True,
        )
        raw = r.get(f"extraction:{document_id}")
    except Exception as exc:
        logger.error("Redis connection failed: %s", exc)
        return jsonify({"error": "could not connect to extraction store"}), 503

    if raw is None:
        return jsonify({"error": "no extraction found for document_id"}), 404

    try:
        extraction = json.loads(raw)
    except Exception:
        return jsonify({"error": "malformed extraction data in store"}), 500

    text = (extraction.get("text") or "").strip()
    if not text:
        return jsonify({"error": "extraction contains no text"}), 422

    language = (data.get("language") or "").strip() or None
    summary = current_app.ai_service.summarize_text(text, language=language)
    model_used = current_app.ai_service.settings.summary_model

    return jsonify({
        "document_id": document_id,
        "filename": extraction.get("filename"),
        "job_id": extraction.get("job_id"),
        "summary": summary,
        "model_used": model_used,
    }), 200