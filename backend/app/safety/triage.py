import re
from typing import Tuple
from backend.app.core.constants import RiskLevel, SafetyRoute
from backend.app.safety.rules import SAFETY_CONFIG


class SafetyTriage:
    def __init__(self):
        self._load_patterns()

    def _load_patterns(self):
        from backend.app.safety.rules import load_safety_rules
        cfg = load_safety_rules()
        self.red_flag_patterns = [re.compile(re.escape(p), re.IGNORECASE) for p in cfg.get("red_flag_patterns", [])]
        self.self_harm_patterns = [re.compile(re.escape(p), re.IGNORECASE) for p in cfg.get("self_harm_patterns", [])]
        self.blocked_patterns = [re.compile(re.escape(p), re.IGNORECASE) for p in cfg.get("blocked_patterns", [])]
        self.caution_patterns = [re.compile(re.escape(p), re.IGNORECASE) for p in cfg.get("caution_patterns", [])]

    def assess_risk(self, query: str) -> Tuple[SafetyRoute, RiskLevel, str]:
        """
        Assesses health query risk level deterministically prior to retrieval and LLM inference.
        Returns (SafetyRoute, RiskLevel, explanation).
        """
        self._load_patterns()
        cleaned = query.strip().lower()

        # 1. Crisis / Self-Harm
        for pat in self.self_harm_patterns:
            if pat.search(cleaned):
                return SafetyRoute.CRISIS, RiskLevel.RED, f"Matched self-harm pattern: {pat.pattern}"

        # 2. Emergency Red Flags
        for pat in self.red_flag_patterns:
            if pat.search(cleaned):
                return SafetyRoute.EMERGENCY, RiskLevel.RED, f"Matched emergency red flag: {pat.pattern}"

        # 3. Diagnosis Deferral
        if any(diag in cleaned for diag in ["diagnose me", "confirm my diagnosis", "do i have cancer", "what disease do i have"]):
            return SafetyRoute.DIAGNOSIS_DEFERRAL, RiskLevel.BLOCKED, "Requested personal medical diagnosis."

        # 4. Check generic blocked patterns (medications, dose changes, illegal drugs)
        for pat in self.blocked_patterns:
            if pat.search(cleaned):
                return SafetyRoute.BLOCKED_MEDICATION_ADVICE, RiskLevel.BLOCKED, f"Matched blocked pattern: {pat.pattern}"

        # 5. High Caution / Orange
        if any(c in cleaned for c in ["pregnant and", "infant fever", "child has had a fever", "child fever", "new rash while taking", "fever for 2 days"]):
            return SafetyRoute.HIGH_CAUTION, RiskLevel.ORANGE, "Matched vulnerable population or acute symptom pattern."

        # 6. Yellow Caution (Symptom information, mental health concerns)
        if any(c in cleaned for c in ["symptoms of", "feeling depressed", "anxiety for weeks", "signs of"]):
            return SafetyRoute.ALLOWED, RiskLevel.YELLOW, "Symptom or distress inquiry; allowed with caution guidance."

        # 7. Green (Educational definitions and prevention)
        return SafetyRoute.ALLOWED, RiskLevel.GREEN, "General health literacy or prevention inquiry."


triage_engine = SafetyTriage()


def route_health_query(query: str) -> Tuple[SafetyRoute, RiskLevel, str]:
    return triage_engine.assess_risk(query)
