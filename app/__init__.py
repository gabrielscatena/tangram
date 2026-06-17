from __future__ import annotations

from app.bootstrap import build_demo_container


def create_app():
    """Create the Flask application.

    Returns:
        A configured Flask app instance.

    Raises:
        RuntimeError: If Flask is not installed in the active environment.
    """
    try:
        from flask import Flask
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "Flask is required to run the web app. Install the Conda environment first."
        ) from exc

    from app.routes.annotation_routes import annotation_bp
    from app.routes.api_routes import api_bp
    from app.routes.observability_routes import observability_bp
    from app.routes.rubric_routes import rubric_bp
    from app.routes.student_routes import student_bp
    from app.routes.teacher_routes import teacher_bp

    app = Flask(__name__)
    app.config.from_object("app.config.LocalConfig")

    container = build_demo_container()
    app.extensions["tangram_container"] = container

    app.register_blueprint(student_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(annotation_bp)
    app.register_blueprint(rubric_bp)
    app.register_blueprint(observability_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    return app
