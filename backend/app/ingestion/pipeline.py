from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from backend.app.ingestion.validators import validate_document_file, compute_sha256
from backend.app.ingestion.parsers.pdf_parser import PDFParser
from backend.app.ingestion.parsers.html_parser import HTMLParser, TXTParser
from backend.app.ingestion.parsers.md_parser import MarkdownParser
from backend.app.ingestion.cleaner import clean_medical_text
from backend.app.ingestion.chunker import MedicalChunker
from backend.app.ingestion.metadata import extract_metadata_from_text
from backend.app.core.exceptions import DocumentIngestionException


class IngestionPipeline:
    def __init__(self):
        self.chunker = MedicalChunker()
        self.md_parser = MarkdownParser()
        self.html_parser = HTMLParser()
        self.txt_parser = TXTParser()
        self.pdf_parser = PDFParser()

    def _get_parser(self, file_path: Path):
        suffix = file_path.suffix.lower()
        if suffix in [".md", ".markdown"]:
            return self.md_parser
        elif suffix in [".html", ".htm"]:
            return self.html_parser
        elif suffix in [".txt"]:
            return self.txt_parser
        elif suffix in [".pdf"]:
            return self.pdf_parser
        else:
            raise DocumentIngestionException(f"Unsupported file format: {suffix}")

    def process_file(
        self,
        file_path: Path,
        source_id: str,
        category_id: int,
        title_override: Optional[str] = None,
        source_url_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Parses, cleans, and chunks an approved document file.
        Returns document dict and list of chunk dicts ready for DB storage.
        """
        validate_document_file(file_path)
        content_hash = compute_sha256(file_path)

        parser = self._get_parser(file_path)
        parsed_result = parser.parse(file_path)

        title = title_override or parsed_result.get("title", file_path.stem)
        raw_text = parsed_result.get("raw_text", "")
        cleaned_text = clean_medical_text(raw_text)

        if len(cleaned_text.strip()) < 100:
            raise DocumentIngestionException("Extracted document content is too short (< 100 characters).")

        sections = parsed_result.get("sections", [])
        chunks = self.chunker.chunk_document(title, sections)

        embedded_meta = extract_metadata_from_text(raw_text)
        source_url = source_url_override or embedded_meta.get("url")

        pub_date = None
        if "publication_date" in embedded_meta:
            try:
                pub_date = date.fromisoformat(embedded_meta["publication_date"])
            except ValueError:
                pass

        last_updated_date = None
        if "last_updated" in embedded_meta:
            try:
                last_updated_date = date.fromisoformat(embedded_meta["last_updated"])
            except ValueError:
                pass

        doc_data = {
            "source_id": source_id,
            "category_id": category_id,
            "title": title,
            "document_type": embedded_meta.get("document_type", "fact_sheet"),
            "source_url": source_url,
            "local_path": str(file_path),
            "content_hash": content_hash,
            "language": "en",
            "publication_date": pub_date,
            "last_updated": last_updated_date,
            "status": "active",
            "extracted_text": cleaned_text,
            "extraction_quality": 1.0,
        }

        return {
            "document": doc_data,
            "chunks": chunks
        }


ingestion_pipeline = IngestionPipeline()
