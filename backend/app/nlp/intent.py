import re
from typing import Tuple


class HealthcareIntentClassifier:
    def classify(self, query: str) -> Tuple[str, float]:
        """
        Classifies query intent into approved health topic categories.
        Returns (intent, confidence).
        """
        q = query.lower()

        # Definitions
        if re.search(r"\b(what is|define|meaning of|what does .* mean|definition of)\b", q):
            return "definition", 0.95

        # Prevention
        if re.search(r"\b(prevent|reduce risk|prevention|avoid getting|protect against)\b", q):
            return "prevention", 0.92

        # Symptoms
        if re.search(r"\b(symptoms|signs of|feel like|how do i know if)\b", q):
            return "symptom_information", 0.90

        # When to seek care
        if re.search(r"\b(when to see a doctor|when to go to hospital|is it serious|should i see a doctor|when to seek)\b", q):
            return "when_to_seek_care", 0.92

        # Vaccines
        if re.search(r"\b(vaccine|vaccination|immunization|shot|booster)\b", q):
            return "vaccination_information", 0.94

        # Nutrition & Diet
        if re.search(r"\b(diet|food|eat|nutrition|calories|vitamins|salt|sugar)\b", q):
            return "nutrition", 0.90

        # Mental health
        if re.search(r"\b(anxiety|depression|mental health|stress|panic|depressed)\b", q):
            return "mental_health_education", 0.90

        # Maternal / Child
        if re.search(r"\b(pregnant|pregnancy|baby|infant|breastfeeding|child nutrition|maternal)\b", q):
            return "maternal_child_health", 0.90

        # General explanation
        if re.search(r"\b(how does|why does|explain|how do)\b", q):
            return "explanation", 0.85

        return "common_health_concepts", 0.75


intent_classifier = HealthcareIntentClassifier()
