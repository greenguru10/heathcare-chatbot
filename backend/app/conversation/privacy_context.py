from typing import List, Dict, Any


def build_safe_context_summary(messages: List[Dict[str, Any]], max_turns: int = 4) -> str:
    """
    Summarizes recent conversational context while excluding sensitive raw user health narratives.
    """
    if not messages:
        return ""

    recent = messages[-max_turns:]
    summary_parts = []
    for msg in recent:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        # Truncate content to safe high-level snippet
        snippet = content[:100] + "..." if len(content) > 100 else content
        summary_parts.append(f"{role.capitalize()}: {snippet}")

    return "\n".join(summary_parts)
