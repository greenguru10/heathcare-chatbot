import re
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class HealthcareConversationState(BaseModel):
    session_id: str
    previous_intent: Optional[str] = None
    previous_topics: List[str] = Field(default_factory=list)
    previous_entities: List[str] = Field(default_factory=list)
    previous_source_ids: List[str] = Field(default_factory=list)
    previous_risk_level: Optional[str] = None
    pending_clarification: Optional[str] = None
    safe_context_summary: Optional[str] = None


class FollowUpResolver:
    def resolve_follow_up(self, current_query: str, state: HealthcareConversationState) -> str:
        """
        Resolves ambiguous follow-up pronouns and subjectless contextual queries
        (e.g., 'What foods should I avoid with it?', 'What are the symptoms?', 'What about pregnant women?')
        using recent conversational topics.
        """
        q = current_query.strip()
        if not state.previous_topics:
            return q

        last_topic = state.previous_topics[-1]
        
        # Clean topic if it has prefixes like "WHO Fact Sheet: "
        clean_topic = re.sub(r"^(WHO Fact Sheet:\s*|MedlinePlus:\s*|CDC:\s*|ICMR Guidelines:\s*)", "", last_topic, flags=re.IGNORECASE).strip()
        if not clean_topic:
            clean_topic = last_topic

        # 1. Pronoun replacement
        pronoun_pattern = r"\b(it|this|that|these|those|the disease|the condition|the illness|the problem)\b"
        if re.search(pronoun_pattern, q, re.IGNORECASE):
            resolved = re.sub(pronoun_pattern, clean_topic, q, flags=re.IGNORECASE)
            return resolved

        # 2. Elliptical / Subjectless follow-up questions
        # e.g., "What are the symptoms?", "How to prevent?", "What foods to avoid?", "What about pregnant women?"
        subjectless_patterns = [
            r"^(what\s+are\s+(the\s+)?(symptoms|signs|causes|risk\s+factors|complications|treatments|prevention\s+methods|side\s+effects)\??)$",
            r"^(how\s+(can\s+I|to|is\s+it)\s+(prevent|treat|manage|diagnose|cure|check)(\s+it)?\??)$",
            r"^(what\s+(foods|diet|exercises|lifestyle\s+changes)\s+(should\s+I\s+avoid|help|are\s+recommended)\??)$",
            r"^(what\s+about\s+(children|adults|elderly|infants|pregnant\s+women|pregnancy)\??)$",
            r"^(can\s+you\s+explain\s+(more|in\s+simpler\s+terms|further)\??)$",
            r"^(is\s+it\s+(curable|preventable|dangerous|fatal|contagious)\??)$",
            r"^(when\s+should\s+I\s+see\s+a\s+doctor\??)$"
        ]

        for pattern in subjectless_patterns:
            if re.search(pattern, q, re.IGNORECASE):
                # Append context
                q_clean = q.rstrip("?").strip()
                return f"{q_clean} for {clean_topic}?"

        return q


resolver = FollowUpResolver()
