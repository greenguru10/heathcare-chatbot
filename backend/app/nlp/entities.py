import re
from typing import Dict, List, Any


class MedicalEntityExtractor:
    def __init__(self):
        self.symptom_patterns = [
            "fever", "chest pain", "shortness of breath", "cough", "headache", "dizziness",
            "rash", "nausea", "vomiting", "fatigue", "thirst", "blurred vision", "sweating",
            "trembling", "palpitations", "dry mouth", "seizure", "bleeding", "swelling"
        ]
        self.population_patterns = [
            "infant", "baby", "child", "children", "toddler", "pregnant", "pregnancy",
            "breastfeeding", "elderly", "older adult", "adolescent", "teenager"
        ]
        self.duration_patterns = [
            r"\b\d+\s*(?:day|days|week|weeks|month|months|hour|hours|year|years)\b",
            r"\bsince\s+(?:morning|yesterday|last week|childhood)\b",
            r"\bfor\s+\d+\s*(?:days|weeks|months|hours)\b"
        ]

    def extract_entities(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        extracted_symptoms = [s for s in self.symptom_patterns if re.search(r"\b" + re.escape(s) + r"\b", text_lower)]
        extracted_populations = [p for p in self.population_patterns if re.search(r"\b" + re.escape(p) + r"\b", text_lower)]
        
        durations = []
        for pat in self.duration_patterns:
            matches = re.findall(pat, text_lower)
            durations.extend(matches)

        return {
            "symptoms": extracted_symptoms,
            "populations": extracted_populations,
            "durations": durations,
            "has_vulnerable_population": len(extracted_populations) > 0,
            "has_acute_symptoms": len(extracted_symptoms) > 0
        }


entity_extractor = MedicalEntityExtractor()
