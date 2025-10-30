"""
TTS Exceptions

Custom exceptions for TTS operations.
"""


class TTSException(Exception):
    """Custom exception for TTS errors."""
    pass


class EngineNotAvailableError(TTSException):
    """Raised when a TTS engine is not available."""

    pass


class ValidationError(TTSException):
    """Raised when input validation fails."""

    pass