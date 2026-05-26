"""Flask application factory for the AI microservice."""

import os

from flask import Flask

from .config import config
from .services.ai_service import AIService


def create_app(config_name: str | None = None) -> Flask:
    """Create and configure the Flask application."""

    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "default")

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.ai_service = AIService.from_config(app.config["LLM"])

    register_blueprints(app)
    return app


def register_blueprints(app: Flask) -> None:
    """Register API blueprints."""

    from .routes.intelligence import intelligence_bp
    from .routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(intelligence_bp)
