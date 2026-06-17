from __future__ import annotations

import json

from app.routes._helpers import get_container

try:
    from flask import Blueprint, abort, jsonify, render_template
except ImportError:  # pragma: no cover
    Blueprint = None  # type: ignore[assignment]

if Blueprint is not None:
    observability_bp = Blueprint("observability", __name__)

    @observability_bp.route("/observability", methods=["GET"])
    def observability_dashboard():
        """Render observability dashboard."""
        container = get_container()
        steps = container.trace_service.list_steps()
        models = container.model_registry.list_models()
        trace_ids = container.trace_service.list_trace_ids()
        return render_template(
            "observability_dashboard.html",
            steps=steps,
            models=models,
            trace_ids=trace_ids,
        )

    @observability_bp.route("/observability/traces/<trace_id>", methods=["GET"])
    def trace_detail(trace_id: str):
        """Render detailed steps for one trace."""
        container = get_container()
        steps = container.trace_service.get_trace_steps(trace_id)
        if not steps:
            abort(404)
        rendered_steps = [
            {
                "trace_id": step.trace_id,
                "response_id": step.response_id,
                "step_name": step.step_name,
                "latency_ms": step.latency_ms,
                "created_at": step.created_at,
                "payload_pretty": json.dumps(step.payload, ensure_ascii=False, indent=2, default=str),
            }
            for step in steps
        ]
        return render_template("trace_detail.html", trace_id=trace_id, steps=rendered_steps)

    @observability_bp.route("/api/traces/<trace_id>", methods=["GET"])
    def trace_detail_api(trace_id: str):
        """Return trace steps as JSON for API inspection."""
        container = get_container()
        steps = container.trace_service.get_trace_steps(trace_id)
        if not steps:
            abort(404)
        return jsonify(
            {
                "trace_id": trace_id,
                "steps": [
                    {
                        "response_id": step.response_id,
                        "step_name": step.step_name,
                        "payload": step.payload,
                        "latency_ms": step.latency_ms,
                        "created_at": step.created_at.isoformat(),
                    }
                    for step in steps
                ],
            }
        )
else:  # pragma: no cover
    observability_bp = None
