class SafetyPolicy:
    MAX_QUERY_LENGTH = 1500
    MIN_QUERY_LENGTH = 2
    STRICT_FAIL_CLOSED = True
    ALLOW_AUTONOMOUS_AGENTS = False
    REQUIRE_CITATIONS = True
    ALLOW_PATIENT_RECORDS = False


policy = SafetyPolicy()
