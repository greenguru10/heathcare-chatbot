import re
from typing import Dict, Any


def extract_metadata_from_text(text: str) -> Dict[str, Any]:
    """
    Extracts embedded metadata header if formatted with markdown key-value pairs.
    """
    metadata = {}
    lines = text.splitlines()
    for line in lines[:25]:
        match = re.match(r"\*\*(.*?)\*\*:\s*(.*)", line)
        if match:
            key = match.group(1).strip().lower().replace(" ", "_")
            val = match.group(2).strip()
            metadata[key] = val
    return metadata
