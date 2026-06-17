from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Iterator

logger = logging.getLogger(__name__)


class MLflowTrackingService:
    """Optional MLflow Tracking wrapper.

    If MLflow is unavailable, calls degrade to no-ops. This keeps the mock testable in
    minimal environments while preserving the intended integration points.
    """

    def __init__(self, tracking_uri: str | None = None, experiment_name: str = "tangram-ai-feedback-lab") -> None:
        self._tracking_uri = tracking_uri
        self._experiment_name = experiment_name
        self._mlflow = self._try_import_mlflow()
        if self._mlflow is not None:
            if tracking_uri:
                self._mlflow.set_tracking_uri(tracking_uri)
            self._mlflow.set_experiment(experiment_name)

    @contextmanager
    def run(self, run_name: str) -> Iterator[None]:
        """Start an MLflow run when MLflow is available."""
        if self._mlflow is None:
            yield None
            return
        with self._mlflow.start_run(run_name=run_name):
            yield None

    def log_params(self, params: dict[str, object]) -> None:
        """Log parameters."""
        if self._mlflow is None:
            return
        self._mlflow.log_params(params)

    def log_metrics(self, metrics: dict[str, float]) -> None:
        """Log metrics."""
        if self._mlflow is None:
            return
        self._mlflow.log_metrics(metrics)

    @staticmethod
    def _try_import_mlflow():
        try:
            import mlflow
        except ImportError:
            logger.info("mlflow_not_installed_tracking_disabled")
            return None
        return mlflow
