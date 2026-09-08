from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class HealthcareAppException(Exception):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class SafetyViolationException(HealthcareAppException):
    """Raised when a prompt or output critically violates medical safety constraints."""
    pass


class DocumentIngestionException(HealthcareAppException):
    """Raised when document parsing, validation, or chunking fails."""
    pass


class RetrievalException(HealthcareAppException):
    """Raised when retrieval index access or vector search fails."""
    pass


class LLMGatewayException(HealthcareAppException):
    """Raised when the LLM provider fails, times out, or returns invalid structure."""
    pass


class EntityNotFoundException(HealthcareAppException):
    """Raised when a requested resource is missing."""
    pass
