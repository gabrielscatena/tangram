from __future__ import annotations

import hashlib


class Pseudonymizer:
    """Deterministic pseudonymizer for demo identifiers.

    This is not a full anonymization strategy. It is a mock to demonstrate privacy by design.
    """

    def __init__(self, salt: str) -> None:
        self._salt = salt

    def pseudonymize(self, identifier: str) -> str:
        """Return a stable pseudonymous id.

        Args:
            identifier: Raw student identifier.

        Returns:
            Pseudonymous identifier prefixed with ``stu_``.
        """
        digest = hashlib.sha256(f"{self._salt}:{identifier}".encode("utf-8")).hexdigest()
        return f"stu_{digest[:16]}"
