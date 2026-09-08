from pathlib import Path
from typing import Dict, Any, List
import yaml
from backend.app.core.config import settings


def load_medical_terms() -> Dict[str, Any]:
    terms_file = settings.CONFIGS_DIR / "medical_terms.yaml"
    if not terms_file.exists():
        return {
            "abbreviations": {
                "bp": {"expansion": "blood pressure"},
                "bmi": {"expansion": "body mass index"},
                "cpr": {"expansion": "cardiopulmonary resuscitation"},
                "uti": {"expansion": "urinary tract infection"},
                "htn": {"expansion": "hypertension"},
                "dm": {"expansion": "diabetes mellitus"}
            },
            "synonyms": {
                "high_blood_pressure": ["hypertension", "high bp"],
                "heart_attack": ["myocardial infarction"],
                "shortness_of_breath": ["breathlessness", "difficulty breathing"],
                "diabetes": ["diabetes mellitus", "high blood sugar"]
            }
        }
    with open(terms_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


MEDICAL_TERMS = load_medical_terms()
