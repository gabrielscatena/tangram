from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path

from app.domain.entities import TraceStep


class JsonTraceService:
    """Local JSONL tracing service with MLflow-compatible semantics.

    This service keeps traces in memory for the running Flask process and also
    appends them to a JSONL file so they can be inspected after a restart.
    """

    def __init__(self, trace_path: str | None = None) -> None:
        self._trace_path = Path(trace_path) if trace_path else None
        self._steps: list[TraceStep] = []
        if self._trace_path:
            self._trace_path.parent.mkdir(parents=True, exist_ok=True)
            self._load_existing_steps()

    def start_trace(self, name: str, metadata: dict[str, object]) -> str:
        """Start a local trace."""
        trace_id = f"trc_{uuid.uuid4().hex[:12]}"
        self._write_jsonl(
            {
                "event": "trace_started",
                "trace_id": trace_id,
                "name": name,
                "metadata": metadata,
            }
        )
        return trace_id

    def log_step(
        self,
        trace_id: str,
        response_id: str,
        step_name: str,
        payload: dict[str, object],
        latency_ms: int = 0,
    ) -> None:
        """Log one trace step."""
        step = TraceStep(
            trace_id=trace_id,
            response_id=response_id,
            step_name=step_name,
            payload=payload,
            latency_ms=latency_ms,
        )
        self._steps.append(step)
        self._write_jsonl(
            {
                "event": "trace_step",
                "trace_id": trace_id,
                "response_id": response_id,
                "step_name": step_name,
                "payload": payload,
                "latency_ms": latency_ms,
                "created_at": step.created_at.isoformat(),
            }
        )

    def end_trace(self, trace_id: str, output: dict[str, object]) -> None:
        """Finish a local trace."""
        self._write_jsonl({"event": "trace_ended", "trace_id": trace_id, "output": output})

    def list_steps(self) -> list[TraceStep]:
        """Return trace steps."""
        return list(self._steps)

    def list_trace_ids(self) -> list[str]:
        """Return trace ids ordered from newest to oldest."""
        seen: set[str] = set()
        trace_ids: list[str] = []
        for step in reversed(self._steps):
            if step.trace_id not in seen:
                seen.add(step.trace_id)
                trace_ids.append(step.trace_id)
        return trace_ids

    def get_trace_steps(self, trace_id: str) -> list[TraceStep]:
        """Return all steps for one trace id."""
        return [step for step in self._steps if step.trace_id == trace_id]

    def _write_jsonl(self, item: dict[str, object]) -> None:
        if self._trace_path is None:
            return
        with self._trace_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(item, ensure_ascii=False, default=str) + "\n")

    def _load_existing_steps(self) -> None:
        """Load previously persisted trace steps from JSONL, if available."""
        if self._trace_path is None or not self._trace_path.exists():
            return

        for line in self._trace_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue

            if item.get("event") != "trace_step":
                continue

            created_at_raw = item.get("created_at")
            created_at = None
            if isinstance(created_at_raw, str):
                try:
                    created_at = datetime.fromisoformat(created_at_raw)
                except ValueError:
                    created_at = None

            kwargs = {
                "trace_id": str(item.get("trace_id", "")),
                "response_id": str(item.get("response_id", "")),
                "step_name": str(item.get("step_name", "unknown_step")),
                "payload": item.get("payload", {}) if isinstance(item.get("payload", {}), dict) else {},
                "latency_ms": int(item.get("latency_ms", 0)),
            }
            if created_at is not None:
                kwargs["created_at"] = created_at
            self._steps.append(TraceStep(**kwargs))
