from enum import Enum


class RiskLevel(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    ORANGE = "orange"
    RED = "red"
    BLOCKED = "blocked"


class SafetyRoute(str, Enum):
    ALLOWED = "allowed"
    EMERGENCY = "emergency"
    CRISIS = "crisis"
    BLOCKED_MEDICATION_ADVICE = "blocked_medication_advice"
    DIAGNOSIS_DEFERRAL = "diagnosis_deferral"
    HIGH_CAUTION = "high_caution"
    UNSUPPORTED = "unsupported"


class ResponseMode(str, Enum):
    GROUNDED_ANSWER = "grounded_answer"
    EMERGENCY = "emergency"
    SAFETY_REFUSAL = "safety_refusal"
    CLARIFICATION = "clarification"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class AuthorityTier(str, Enum):
    TIER_A = "A"
    TIER_B = "B"
    TIER_C = "C"
    TIER_D = "D"


class DocumentStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUPERSEDED = "superseded"
    FAILED = "failed"


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    REVIEWER = "reviewer"


class FeedbackRating(int, Enum):
    VERY_POOR = 1
    POOR = 2
    AVERAGE = 3
    GOOD = 4
    EXCELLENT = 5
