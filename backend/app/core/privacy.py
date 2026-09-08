import re
from typing import Dict, Any


# Regular expressions for identifying common PII/PHI patterns
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_REGEX = re.compile(r"(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}")
SSN_AADHAAR_REGEX = re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b|\b\d{3}-\d{2}-\d{4}\b")
MRN_REGEX = re.compile(r"\b(MRN|mrn|Patient ID|patient id)[\s:#]*\w+\b", re.IGNORECASE)


def redact_sensitive_content(text: str) -> str:
    """
    Minimizes PII/PHI from user queries before logging, storage, or external LLM transmission.
    """
    if not text:
        return text
    
    redacted = EMAIL_REGEX.sub("[REDACTED_EMAIL]", text)
    redacted = PHONE_REGEX.sub("[REDACTED_PHONE]", redacted)
    redacted = SSN_AADHAAR_REGEX.sub("[REDACTED_ID]", redacted)
    redacted = MRN_REGEX.sub("[REDACTED_MRN]", redacted)
    return redacted


def sanitize_audit_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Filters out sensitive parameters and secrets from audit log dictionaries.
    """
    sensitive_keys = {"password", "api_key", "token", "authorization", "secret", "jwt"}
    sanitized = {}
    for k, v in metadata.items():
        if any(s_key in k.lower() for s_key in sensitive_keys):
            sanitized[k] = "[REDACTED]"
        elif isinstance(v, str):
            sanitized[k] = redact_sensitive_content(v)
        else:
            sanitized[k] = v
    return sanitized
