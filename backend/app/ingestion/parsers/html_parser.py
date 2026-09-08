from pathlib import Path
from typing import Dict, Any, List
from bs4 import BeautifulSoup
from backend.app.ingestion.parsers.base import BaseDocumentParser


class HTMLParser(BaseDocumentParser):
    def parse(self, file_path: Path) -> Dict[str, Any]:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, "html.parser")
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        title_tag = soup.find("title") or soup.find("h1")
        doc_title = title_tag.get_text().strip() if title_tag else file_path.stem.replace("_", " ").title()

        sections: List[Dict[str, Any]] = []
        headings = soup.find_all(["h1", "h2", "h3"])
        if headings:
            for h in headings:
                section_title = h.get_text().strip()
                content = []
                sibling = h.find_next_sibling()
                while sibling and sibling.name not in ["h1", "h2", "h3"]:
                    text = sibling.get_text().strip()
                    if text:
                        content.append(text)
                    sibling = sibling.find_next_sibling()
                if content:
                    sections.append({
                        "title": section_title,
                        "content": "\n".join(content),
                        "page_start": 1,
                        "page_end": 1
                    })

        if not sections:
            full_text = soup.get_text(separator="\n", strip=True)
            sections.append({
                "title": "Main Content",
                "content": full_text,
                "page_start": 1,
                "page_end": 1
            })

        return {
            "title": doc_title,
            "raw_text": soup.get_text(separator="\n", strip=True),
            "sections": sections,
            "metadata": {"format": "html"}
        }


class TXTParser(BaseDocumentParser):
    def parse(self, file_path: Path) -> Dict[str, Any]:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()

        doc_title = file_path.stem.replace("_", " ").title()
        return {
            "title": doc_title,
            "raw_text": text,
            "sections": [{
                "title": "Main Content",
                "content": text,
                "page_start": 1,
                "page_end": 1
            }],
            "metadata": {"format": "txt"}
        }
