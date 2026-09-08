from pathlib import Path
from typing import Dict, Any, List
from backend.app.ingestion.parsers.base import BaseDocumentParser

try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None


class PDFParser(BaseDocumentParser):
    def parse(self, file_path: Path) -> Dict[str, Any]:
        if not fitz:
            raise RuntimeError("PyMuPDF (fitz) is not installed.")

        doc = fitz.open(file_path)
        sections: List[Dict[str, Any]] = []
        full_text_list = []
        doc_title = file_path.stem.replace("_", " ").title()

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").strip()
            if text:
                full_text_list.append(text)
                sections.append({
                    "title": f"Page {page_num + 1}",
                    "content": text,
                    "page_start": page_num + 1,
                    "page_end": page_num + 1
                })

        doc.close()
        return {
            "title": doc_title,
            "raw_text": "\n\n".join(full_text_list),
            "sections": sections,
            "metadata": {"format": "pdf", "page_count": len(sections)}
        }
