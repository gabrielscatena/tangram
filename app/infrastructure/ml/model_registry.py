from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelDescriptor:
    """Minimal model descriptor for the mock registry."""

    name: str
    version: str
    purpose: str
    runtime: str


class InMemoryModelRegistry:
    """Tiny model registry used by the observability dashboard."""

    def __init__(self) -> None:
        self._models = [
            ModelDescriptor(
                name="rule_based_financial_literacy",
                version="v0.1",
                purpose="baseline classification",
                runtime="cpu",
            ),
            ModelDescriptor(
                name="template_feedback_generator",
                version="v0.1",
                purpose="controlled formative feedback",
                runtime="cpu",
            ),
        ]

    def list_models(self) -> list[ModelDescriptor]:
        """Return registered demo models."""
        return list(self._models)
