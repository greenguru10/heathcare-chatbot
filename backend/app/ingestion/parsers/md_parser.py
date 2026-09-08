import re
from pathlib import Path
from typing import Dict, Any, List
from backend.app.ingestion.parsers.base import BaseDocumentParser


class MarkdownParser(BaseDocumentParser):
    def parse(self, file_path: Path) -> Dict[str, Any]:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        lines = content.splitlines()
        sections: List[Dict[str, Any]] = []
        doc_title = file_path.stem.replace("_", " ").title()
        current_section = "Overview"
        current_lines = []

        for line in lines:
            if line.startswith("# "):
                doc_title = line[2:].strip()
            elif line.startswith("## "):
                if current_lines:
                    sections.append({
                        "title": current_section,
                        "content": "\n".join(current_lines).strip(),
                        "page_start": 1,
                        "page_end": 1
                    })
                    current_lines = []
                current_section = line[3:].strip()
            else:
                current_lines.append(line)

        if current_lines:
            sections.append({
                "title": current_section,
                "content": "\n".join(current_lines).strip(),
                "page_start": 1,
                "page_end": 1
            })

        return {
            "title": doc_title,
            "raw_text": content,
            "sections": sections,
            "metadata": {"format": "markdown"}
        }
