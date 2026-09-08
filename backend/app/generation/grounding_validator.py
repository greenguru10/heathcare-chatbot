import re
from typing import List, Dict, Any, Tuple


class GroundingValidator:
    def _extract_factual_sentences(self, text: str) -> List[str]:
        # Split into sentences
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
        # Filter out short disclaimers
        factual = [s for s in sentences if len(s.split()) >= 4 and not s.lower().startswith("this is general educational")]
        return factual

    def validate_grounding(
        self,
        answer_text: str,
        provided_evidence: List[Dict[str, Any]]
    ) -> Tuple[bool, float, List[str]]:
        """
        Decomposes answer into sentences and computes lexical/semantic support against evidence.
        Returns (is_supported, grounding_score, unsupported_sentences).
        """
        sentences = self._extract_factual_sentences(answer_text)
        if not sentences:
            return True, 1.0, []

        if not provided_evidence:
            return False, 0.0, sentences

        # Combine all evidence raw text
        all_evidence_text = " ".join([item["chunk"]["normalized_text"] for item in provided_evidence])
        evidence_words = set(re.findall(r"\b\w{3,}\b", all_evidence_text.lower()))

        supported_count = 0
        unsupported = []

        for sent in sentences:
            sent_words = set(re.findall(r"\b\w{3,}\b", sent.lower()))
            if not sent_words:
                supported_count += 1
                continue

            overlap = len(sent_words.intersection(evidence_words)) / len(sent_words)
            # A sentence is considered supported if >= 40% of substantive words appear in the evidence
            if overlap >= 0.35:
                supported_count += 1
            else:
                unsupported.append(sent)

        grounding_score = supported_count / len(sentences) if sentences else 1.0
        is_supported = grounding_score >= 0.65

        return is_supported, grounding_score, unsupported


grounding_validator = GroundingValidator()
