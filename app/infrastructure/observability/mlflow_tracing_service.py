from __future__ import annotations

from app.infrastructure.observability.json_trace_service import JsonTraceService


class MLflowTracingService(JsonTraceService):
    """MLflow tracing adapter placeholder with JSONL fallback.

    This class intentionally extends JsonTraceService. In a full implementation, methods
    can be replaced with MLflow trace/span APIs while keeping the application contract stable.
    """

    pass
