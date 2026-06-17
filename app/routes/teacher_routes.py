from __future__ import annotations

from app.routes._helpers import get_container

try:
    from flask import Blueprint, render_template
except ImportError:  # pragma: no cover
    Blueprint = None  # type: ignore[assignment]

if Blueprint is not None:
    teacher_bp = Blueprint("teacher", __name__)

    @teacher_bp.route("/teacher/review", methods=["GET"])
    def teacher_review():
        """Render teacher review queue."""
        container = get_container()
        pending = container.response_repository.list_pending_review()
        return render_template("teacher_review.html", pending=pending)
else:  # pragma: no cover
    teacher_bp = None
