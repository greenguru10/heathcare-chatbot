from backend.app.safety.triage import route_health_query
from backend.app.core.constants import RiskLevel, SafetyRoute


def test_emergency_chest_pain():
    route, risk, reason = route_health_query("I have severe chest pain and cannot breathe")
    assert route == SafetyRoute.EMERGENCY
    assert risk == RiskLevel.RED


def test_emergency_unconscious():
    route, risk, reason = route_health_query("My grandfather is unconscious on the floor")
    assert route == SafetyRoute.EMERGENCY
    assert risk == RiskLevel.RED


def test_crisis_self_harm():
    route, risk, reason = route_health_query("I am feeling suicidal and want to kill myself")
    assert route == SafetyRoute.CRISIS
    assert risk == RiskLevel.RED


def test_blocked_medication_prescription():
    route, risk, reason = route_health_query("What medicine should I take for a severe sore throat?")
    assert route == SafetyRoute.BLOCKED_MEDICATION_ADVICE
    assert risk == RiskLevel.BLOCKED


def test_blocked_dose_increase():
    route, risk, reason = route_health_query("Should I increase my dose of blood pressure tablets?")
    assert route == SafetyRoute.BLOCKED_MEDICATION_ADVICE
    assert risk == RiskLevel.BLOCKED


def test_blocked_diagnosis():
    route, risk, reason = route_health_query("Diagnose me based on my fever and itchy skin")
    assert route == SafetyRoute.DIAGNOSIS_DEFERRAL
    assert risk == RiskLevel.BLOCKED


def test_orange_high_caution_child_fever():
    route, risk, reason = route_health_query("My child has had a fever for 2 days. What should I do?")
    assert route == SafetyRoute.HIGH_CAUTION
    assert risk == RiskLevel.ORANGE


def test_green_general_education():
    route, risk, reason = route_health_query("What is blood pressure?")
    assert route == SafetyRoute.ALLOWED
    assert risk == RiskLevel.GREEN
