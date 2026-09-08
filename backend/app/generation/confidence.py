from typing import List, Dict, Any, Tuple


def calculate_confidence(
    retrieval_evidence: List[Dict[str, Any]],
    grounding_score: float,
    intent_confidence: float = 0.90,
    contradiction_risk: float = 0.0
) -> Tuple[float, str, str]:
    """
    Calculates deterministic multi-factor confidence score according to Section 16 of Technical Spec.
    Returns (score, label, explanation).
    """
    if not retrieval_evidence:
        return 0.0, "insufficient", "No approved evidence could be retrieved for this inquiry."

    # R: Retrieval relevance
    r_scores = [item.get("final_score", 0.7) for item in retrieval_evidence]
    r = sum(r_scores) / len(r_scores)

    # G: Grounding score
    g = grounding_score

    # A: Authority score
    a_scores = [float(item["chunk"].get("authority_score", 1.0)) for item in retrieval_evidence]
    a = sum(a_scores) / len(a_scores)

    # C: Corroboration (distinct sources)
    unique_sources = len({item["chunk"].get("source_name") for item in retrieval_evidence})
    c = min(unique_sources / 2.0, 1.0)

    # I: Intent confidence
    i = intent_confidence

    # X: Contradiction risk
    x = contradiction_risk

    confidence_val = (
        0.28 * r
        + 0.22 * g
        + 0.16 * a
        + 0.12 * c
        + 0.12 * i
        + 0.10 * (1.0 - x)
    )
    confidence_val = max(0.0, min(1.0, round(confidence_val, 2)))

    if confidence_val >= 0.82:
        label = "high"
        explanation = "The response is strongly grounded in current, authoritative health guidance."
    elif confidence_val >= 0.68:
        label = "medium"
        explanation = "The answer is supported by authoritative guidance, but evidence may not cover all individual contexts."
    elif confidence_val >= 0.50:
        label = "low"
        explanation = "Limited supporting evidence found in the approved corpus."
    else:
        label = "insufficient"
        explanation = "Evidence is insufficient to safely answer this health question."

    return confidence_val, label, explanation
