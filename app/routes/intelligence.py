"""AI endpoints for chat, text summarization, and PDF uploads."""

from uuid import uuid4

from flask import Blueprint, current_app, jsonify, request

from ..services.pdf_service import extract_text_from_pdf, is_pdf_upload


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