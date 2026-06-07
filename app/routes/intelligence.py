"""AI endpoints for chat, text summarization, and PDF uploads."""

import json
import logging
import os
from uuid import uuid4

import requests as http_requests
from flask import Blueprint, current_app, jsonify, request

from ..services.pdf_service import extract_text_from_pdf, is_pdf_upload

logger = logging.getLogger(__name__)


def _save_to_persistence(document_payload: dict, summary_content: str, model_used: str) -> dict | None:
    """Save document + summary to persistence service. Returns dict with document_id on success."""
    base_url = os.environ.get("PERSISTENCE_URL", "").rstrip("/")
    if not base_url:
        logger.warning("PERSISTENCE_URL not set — skipping persistence save")
        return None
    try:
        doc_resp = http_requests.post(
            f"{base_url}/api/v1/documents",
            json=document_payload,
            timeout=10,
        )
        doc_resp.raise_for_status()
        doc_data = doc_resp.json()
        doc_id = doc_data.get("id")
        if not doc_id:
            logger.warning("Persistence returned no document id: %s", doc_data)
            return None

        summary_resp = http_requests.post(
            f"{base_url}/api/v1/summaries",
            json={"documentId": doc_id, "content": summary_content, "modelUsed": model_used},
            timeout=10,
        )
        summary_resp.raise_for_status()
        return {"document_id": doc_id, "summary": summary_resp.json()}
    except Exception as exc:
        logger.warning("Failed to save to persistence: %s", exc)
        return None


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
@intelligence_bp.post("/api/v1/summaries")
def summarize():
    """Summarize structured or free-form text."""

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
    """Read extracted text from Redis by document_id and generate a summary."""

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
    user_id = data.get("user_id") or 1
    summary = current_app.ai_service.summarize_text(text, language=language)
    model_used = current_app.ai_service.settings.summary_model

    document_payload = {
        "userId": user_id,
        "filename": extraction.get("filename") or f"{document_id}.pdf",
        "filePath": f"/extractions/{document_id}",
        "jobId": extraction.get("job_id"),
        "status": "COMPLETED",
        "extractedText": text,
    }
    _save_to_persistence(document_payload, summary, model_used)

    return jsonify({
        "document_id": document_id,
        "filename": extraction.get("filename"),
        "job_id": extraction.get("job_id"),
        "summary": summary,
    }), 200


@intelligence_bp.post("/api/upload")
@intelligence_bp.post("/api/v1/documento/upload")
def upload_document():
    """Accept a PDF, extract its text, and summarize it with the configured model."""

    uploaded_file = request.files.get("file")
    if uploaded_file is None or not uploaded_file.filename:
        return jsonify({"error": "file is required"}), 400

    if not is_pdf_upload(uploaded_file):
        return jsonify({"error": "only PDF files are supported"}), 400

    try:
        extracted_text = extract_text_from_pdf(uploaded_file)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    if not extracted_text.strip():
        return jsonify({"error": "could not extract text from the uploaded PDF"}), 400

    language = (request.form.get("language") or request.args.get("language") or "").strip() or None
    summary = current_app.ai_service.summarize_text(extracted_text, language=language)
    document_id = str(uuid4())

    return (
        jsonify(
            {
                "document_id": document_id,
                "file_name": uploaded_file.filename,
                "summary": summary,
                "extracted_text": extracted_text,
            }
        ),
        200,
    )