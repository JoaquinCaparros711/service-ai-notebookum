"""Health and index endpoints for the AI microservice."""

from flask import Blueprint, jsonify


main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    """Return a simple readiness payload."""

    return jsonify({"message": "Service AI NotebookUm is running"}), 200


@main_bp.get("/health")
def health_check():
    """Return a health status payload."""

    return jsonify({"status": "ok", "service": "ai"}), 200