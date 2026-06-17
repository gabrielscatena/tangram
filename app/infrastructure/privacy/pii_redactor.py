from __future__ import annotations

import re


class PIIRedactor:
    """Simple PII redactor for Portuguese demo text."""

    EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
    CPF_RE = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
    PHONE_RE = re.compile(r"\b(?:\+55\s?)?(?:\(?\d{2}\)?\s?)?9?\d{4}[-\s]?\d{4}\b")

    def redact(self, text: str) -> str:
        """Mask common PII patterns.

        Args:
            text: Raw text.

        Returns:
            Text with common PII replaced by placeholders.
        """
        redacted = self.EMAIL_RE.sub("[EMAIL]", text)
        redacted = self.CPF_RE.sub("[CPF]", redacted)
        redacted = self.PHONE_RE.sub("[TELEFONE]", redacted)
        return redacted
