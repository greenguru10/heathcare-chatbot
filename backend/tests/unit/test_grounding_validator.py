from backend.app.generation.grounding_validator import grounding_validator
from backend.app.generation.confidence import calculate_confidence


def test_grounding_validation_supported():
    evidence = [{
        "chunk": {
            "normalized_text": "hypertension high blood pressure occurs when arterial force is elevated. eating less salt helps lower blood pressure."
        }
    }]
    answer = "High blood pressure occurs when arterial force is elevated. Eating less salt helps lower blood pressure."
    is_grounded, score, unsupp = grounding_validator.validate_grounding(answer, evidence)
    assert is_grounded is True
    assert score >= 0.70
    assert len(unsupp) == 0


def test_confidence_scorer():
    evidence = [
        {"final_score": 0.85, "chunk": {"source_name": "WHO", "authority_score": 1.0}},
        {"final_score": 0.80, "chunk": {"source_name": "CDC", "authority_score": 1.0}}
    ]
    score, label, exp = calculate_confidence(evidence, grounding_score=0.90, intent_confidence=0.95)
    assert score >= 0.80
    assert label in ["high", "medium"]
    assert "authoritative" in exp.lower()
