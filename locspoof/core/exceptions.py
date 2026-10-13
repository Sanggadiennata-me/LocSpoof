"""
Custom domain exceptions for locspoof.
Human-readable, structured exceptions with details and suggestions.
"""

from typing import Optional


class LocSpoofError(Exception):
    """Base exception for all locspoof errors."""

    def __init__(
        self,
        message: str,
        detail: Optional[str] = None,
        suggestion: Optional[str] = None,
        exit_code: int = 1,
    ):
        super().__init__(message)
        self.message = message
        self.detail = detail
        self.suggestion = suggestion
        self.exit_code = exit_code

    def __str__(self) -> str:
        res = [f"ERROR: {self.message}"]
        if self.detail:
            res.append(f"\nDETAIL:\n{self.detail}")
        if self.suggestion:
            res.append(f"\nSUGGESTION:\n{self.suggestion}")
        return "\n".join(res)


class ValidationError(LocSpoofError):
    """Coordinate or input validation error."""

    def __init__(self, message: str, detail: Optional[str] = None, suggestion: Optional[str] = None):
        super().__init__(message=message, detail=detail, suggestion=suggestion, exit_code=1)


class ConfigurationError(LocSpoofError):
    """Configuration loading or parsing error."""

    def __init__(self, message: str, detail: Optional[str] = None, suggestion: Optional[str] = None):
        super().__init__(message=message, detail=detail, suggestion=suggestion, exit_code=1)


class ProviderError(LocSpoofError):
    """Generic error raised by a provider."""

    def __init__(self, message: str, detail: Optional[str] = None, suggestion: Optional[str] = None, exit_code: int = 1):
        super().__init__(message=message, detail=detail, suggestion=suggestion, exit_code=exit_code)


class DependencyMissingError(LocSpoofError):
    """External dependency (e.g. adb, browser binary) missing."""

    def __init__(self, message: str, detail: Optional[str] = None, suggestion: Optional[str] = None):
        super().__init__(message=message, detail=detail, suggestion=suggestion, exit_code=3)


class DeviceNotFoundError(LocSpoofError):
    """Android or emulator device not found."""

    def __init__(self, message: str, detail: Optional[str] = None, suggestion: Optional[str] = None):
        super().__init__(message=message, detail=detail, suggestion=suggestion, exit_code=3)


class VerificationMismatchError(LocSpoofError):
    """Location consistency verification reported a severe mismatch."""

    def __init__(self, message: str, detail: Optional[str] = None, suggestion: Optional[str] = None):
        super().__init__(message=message, detail=detail, suggestion=suggestion, exit_code=2)
