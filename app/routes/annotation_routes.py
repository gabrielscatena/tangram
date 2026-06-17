from __future__ import annotations

from app.domain.value_objects import ReviewRequest
from app.routes._helpers import get_container

try:
    from flask import Blueprint, redirect, render_template, request, url_for
except ImportError:  # pragma: no cover
    Blueprint = None  # type: ignore[assignment]

if Blueprint is not None:
    annotation_bp = Blueprint("annotation", __name__)

    @annotation_bp.route("/annotation", methods=["GET", "POST"])
    def annotation_studio():
        """Render annotation studio and accept simple reviews."""
        container = get_container()
        if request.method == "POST":
            container.annotate_response.execute(
                ReviewRequest(
                    response_id=request.form["response_id"],
                    reviewer_role=request.form.get("reviewer_role", "pedagogia"),
                    corrected_label=request.form.get("corrected_label", "partially_correct"),
                    edited_feedback=request.form.get("edited_feedback", ""),
                    decision=request.form.get("decision", "approved"),
                )
            )
            return redirect(url_for("annotation.annotation_studio"))
        candidates = container.active_learning.list_candidates()
        return render_template("annotation_studio.html", candidates=candidates)
else:  # pragma: no cover
    annotation_bp = None
