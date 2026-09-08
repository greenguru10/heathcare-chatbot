import re
from backend.app.nlp.medical_terms import MEDICAL_TERMS
from backend.app.core.privacy import redact_sensitive_content


def normalize_query(query: str, expand_abbreviations: bool = True) -> str:
    """
    Cleans, normalizes, minimizes sensitive PII, and expands medical abbreviations for retrieval.
    """
    if not query:
        return ""

    # 1. PII Redaction
    text = redact_sensitive_content(query.strip())

    # 2. Lowercase and whitespace normalization
    text = re.sub(r"\s+", " ", text).strip()

    if expand_abbreviations:
        abbreviations = MEDICAL_TERMS.get("abbreviations", {})
        words = re.findall(r"\b[\w-]+\b|[^\w\s]", text)
        expanded_words = []
        for word in words:
            w_lower = word.lower()
            if w_lower in abbreviations:
                expansion = abbreviations[w_lower].get("expansion", word)
                expanded_words.append(f"{word} ({expansion})")
            else:
                expanded_words.append(word)
        text = " ".join(expanded_words)
        # Clean up punctuation spacing
        text = re.sub(r"\s+([?.!,;])", r"\1", text)

    return text
