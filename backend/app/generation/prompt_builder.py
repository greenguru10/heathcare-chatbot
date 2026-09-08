from typing import List, Dict, Any
from pathlib import Path
from backend.app.core.config import settings


class PromptBuilder:
    def __init__(self):
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        prompt_file = settings.CONFIGS_DIR / "prompts" / "grounded_answer_v1.txt"
        if prompt_file.exists():
            with open(prompt_file, "r", encoding="utf-8") as f:
                return f.read()
        return (
            "You are HealthEvidence Assistant, an educational healthcare-information system.\n"
            "Answer ONLY from the approved evidence supplied below using [S1], [S2] citation markers. "
            "Do not diagnose or prescribe. Output valid JSON."
        )

    def build_user_prompt(self, user_question: str, evidence_chunks: List[Dict[str, Any]], safe_context_summary: str = None) -> str:
        evidence_text_parts = []
        for i, item in enumerate(evidence_chunks):
            chunk = item["chunk"]
            citation_key = f"S{i+1}"
            part = (
                f"[{citation_key}]\n"
                f"Title: {chunk.get('title', 'Medical Resource')}\n"
                f"Authority: {chunk.get('source_name', 'Authoritative Source')}\n"
                f"Section: {chunk.get('section', 'General')}\n"
                f"Date: {chunk.get('last_updated') or chunk.get('publication_date') or 'Current'}\n"
                f"Text: {chunk.get('raw_text', '')}\n"
            )
            evidence_text_parts.append(part)

        evidence_formatted = "\n".join(evidence_text_parts) if evidence_text_parts else "No evidence found."

        context_str = f"Conversation context:\n{safe_context_summary}\n\n" if safe_context_summary else ""

        user_prompt = (
            f"User question:\n{user_question}\n\n"
            f"{context_str}"
            f"Approved evidence:\n{evidence_formatted}\n\n"
            "INSTRUCTIONS:\n"
            "Write a factual, educational answer derived ONLY from the approved evidence above.\n"
            "Add [S#] citations after every factual sentence.\n"
            "Do not diagnose conditions or prescribe treatments.\n"
            "Return the answer in the required JSON format."
        )
        return user_prompt


prompt_builder = PromptBuilder()
