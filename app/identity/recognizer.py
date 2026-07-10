"""Abstract interface for face or alternative identity recognition sources."""

from __future__ import annotations

from typing import Protocol

from app.identity.models import IdentityMatch


class IdentityRecognizer(Protocol):
    """Protocol for pluggable identity recognition implementations.

    Implementations may use face recognition or alternative identity sources,
    but should not expose backend-specific details to the rest of the
    application.
    """

    def identify(self, frame, detections) -> list[IdentityMatch]:
        """Identify participants visible in ``frame`` using candidate detections."""
