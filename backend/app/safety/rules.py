from pathlib import Path
from typing import Dict, Any, List
import yaml
from backend.app.core.config import settings


def load_safety_rules() -> Dict[str, Any]:
    rules_file = settings.CONFIGS_DIR / "safety_rules.yaml"
    if not rules_file.exists():
        return {
            "red_flag_patterns": ["chest pain", "cannot breathe", "unconscious", "seizure", "severe bleeding", "overdose", "poisoning", "anaphylaxis"],
            "self_harm_patterns": ["suicidal", "kill myself", "want to die", "self harm"],
            "blocked_patterns": ["what medicine should i take", "should i stop taking", "increase my dose", "prescribe", "diagnose me"],
            "caution_patterns": ["symptoms", "fever", "pregnant", "rash"],
            "emergency_contact_by_region": {
                "DEFAULT": {"phone": "112 / 911 / 999", "service_name": "Emergency Medical Services"}
            }
        }
    with open(rules_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


SAFETY_CONFIG = load_safety_rules()
