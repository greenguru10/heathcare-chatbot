import re


def clean_medical_text(text: str) -> str:
    """
    Cleans boilerplate, excess whitespace, web navigation artifacts, and unwanted noise.
    """
    if not text:
        return ""

    # Normalize line breaks
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove repeated hyphens or equals lines
    text = re.sub(r"[-=_]{3,}", " ", text)

    # Collapse multi-spaces except single line breaks
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    
    # Remove empty lines excess
    cleaned_lines = []
    empty_count = 0
    for line in lines:
        if not line:
            empty_count += 1
            if empty_count <= 1:
                cleaned_lines.append("")
        else:
            empty_count = 0
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()
