"""Identity domain models for participant matching results."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IdentityMatch:
    """A participant identity match produced by a recognition source.

    ``source`` identifies the matching backend, such as ``face_recognition`` or
    another future identity provider. The application can use ``confidence`` to
    decide whether a match is strong enough for downstream workflows.
    """

    participant_id: str
    confidence: float
    source: str
