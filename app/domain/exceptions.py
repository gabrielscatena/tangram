from __future__ import annotations


class TangramLabError(Exception):
    """Base exception for the mock package."""


class FeedbackGenerationError(TangramLabError):
    """Raised when feedback generation fails."""


class InvalidStudentResponseError(TangramLabError):
    """Raised when a submitted response is invalid."""
