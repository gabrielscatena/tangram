from __future__ import annotations

from app.routes._helpers import get_container

try:
    from flask import Blueprint, render_template
except ImportError:  # pragma: no cover
    Blueprint = None  # type: ignore[assignment]

if Blueprint is not None:
    rubric_bp = Blueprint("rubric", __name__)

    @rubric_bp.route("/rubrics", methods=["GET"])
    def rubric_manager():
        """Render rubrics."""
        container = get_container()
        rubrics = container.rubric_repository.list_rubrics()
        return render_template("rubric_manager.html", rubrics=rubrics)
else:  # pragma: no cover
    rubric_bp = None
