"""Identity recognition interfaces and models."""

from app.identity.models import IdentityMatch
from app.identity.recognizer import IdentityRecognizer

__all__ = ["IdentityMatch", "IdentityRecognizer"]
