import re
from typing import Tuple, List


class OutputSafetyValidator:
    def __init__(self):
        self.diagnosis_patterns = [
            r"\byou have\b",
            r"\byou are suffering from\b",
            r"\bthis is definitely\b",
            r"\bi diagnose you with\b",
            r"\byour condition is\b"
        ]
        self.prescription_patterns = [
            r"\btake \d+\s*(?:mg|ml|tablets|pills)\b",
            r"\bincrease your dose\b",
            r"\bstop taking your\b",
            r"\bswitch to\b",
            r"\bi prescribe\b"
        ]

    def validate_output(self, text: str) -> Tuple[bool, List[str]]:
        errors = []
        text_lower = text.lower()

        for pat in self.diagnosis_patterns:
            if re.search(pat, text_lower):
                errors.append(f"Output contains prohibited diagnosis claim: {pat}")

        for pat in self.prescription_patterns:
            if re.search(pat, text_lower):
                errors.append(f"Output contains prohibited prescription or dosage advice: {pat}")

        is_safe = len(errors) == 0
        return is_safe, errors


output_safety_validator = OutputSafetyValidator()
