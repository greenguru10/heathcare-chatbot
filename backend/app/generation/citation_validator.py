import re
from typing import List, Dict, Any, Tuple, Set


class CitationValidator:
    def validate_citations(
        self,
        answer_text: str,
        provided_evidence: List[Dict[str, Any]],
        parsed_source_ids: List[str] = None
    ) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Validates citation markers [S1], [S2] in generated answer.
        Returns (is_valid, list_of_errors, validation_metadata).
        """
        valid_keys: Set[str] = {f"S{i+1}" for i in range(len(provided_evidence))}
        cited_markers = set(re.findall(r"\[(S\d+)\]", answer_text))
        
        errors = []
        # Check for citations pointing to non-existent sources
        invalid_markers = cited_markers - valid_keys
        if invalid_markers:
            errors.append(f"Answer cites nonexistent source markers: {list(invalid_markers)}")

        if not cited_markers and len(provided_evidence) > 0 and len(answer_text.strip()) > 30:
            errors.append("Answer contains no citation markers [S#] for factual claims.")

        is_valid = len(errors) == 0
        meta = {
            "valid_source_keys": list(valid_keys),
            "cited_markers": list(cited_markers),
            "invalid_markers": list(invalid_markers),
            "citation_count": len(cited_markers)
        }
        return is_valid, errors, meta


citation_validator = CitationValidator()
