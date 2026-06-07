"""Flask application factory for the AI microservice."""

import os

from flask import Flask
from flask_cors import CORS
from werkzeug.exceptions import RequestEntityTooLarge

from .config import config
from .services.ai_service import AIService

_CORS_ORIGINS = [
    "https://api.universidad.localhost",
    "http://localhost",
    r"http://localhost:\d+",
    "null",  # file:// pages
]


def create_app(config_name: str | None = None) -> Flask:
    """Create and configure the Flask application."""

    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "default")

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.ai_service = AIService.from_config(app.config["LLM"])
    app.config.setdefault("MAX_CONTENT_LENGTH", 25 * 1024 * 1024)

    CORS(app, origins=_CORS_ORIGINS, supports_credentials=True)

    register_error_handlers(app)

    register_blueprints(app)
    return app


def register_blueprints(app: Flask) -> None:
    """Register API blueprints."""

    from .routes.intelligence import intelligence_bp
    from .routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(intelligence_bp)


def register_error_handlers(app: Flask) -> None:
    """Register JSON error handlers used by file uploads."""

    @app.errorhandler(RequestEntityTooLarge)
    def handle_request_entity_too_large(_error):
        return (
            {
                "type": "about:blank",
                "title": "Payload too large",
                "status": 400,
                "detail": "El archivo excede el límite máximo de 25 MB.",
            },
            400,
        )
