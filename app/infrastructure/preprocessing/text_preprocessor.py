from __future__ import annotations

import re
import unicodedata


class TextPreprocessor:
    """Text preprocessor for student answers."""

    CONTROL_RE = re.compile(r"[\x00-\x1F\x7F]")
    SPACE_RE = re.compile(r"\s+")

    def clean(self, text: str) -> str:
        """Normalize whitespace and unicode without removing semantic content.

        Args:
            text: Input text.

        Returns:
            Cleaned text preserving accents and student wording.
        """
        normalized = unicodedata.normalize("NFC", text)
        without_controls = self.CONTROL_RE.sub(" ", normalized)
        collapsed = self.SPACE_RE.sub(" ", without_controls).strip()
        return collapsed

    def tokenize_for_rules(self, text: str) -> list[str]:
        """Return simple lowercase tokens for deterministic rules.

        Args:
            text: Cleaned text.

        Returns:
            Lowercase word tokens.
        """
        return re.findall(r"[\wÀ-ÿ]+", text.lower())
