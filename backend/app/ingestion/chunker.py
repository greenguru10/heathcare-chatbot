import re
from typing import List, Dict, Any


class MedicalChunker:
    def __init__(self, target_tokens: int = 350, max_tokens: int = 500, min_tokens: int = 50):
        self.target_tokens = target_tokens
        self.max_tokens = max_tokens
        self.min_tokens = min_tokens

    def _estimate_token_count(self, text: str) -> int:
        return len(text.split())

    def _split_into_sentences(self, text: str) -> List[str]:
        # Split on sentence boundaries while keeping abbreviations like e.g. or i.e. intact
        sentence_end = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")
        sentences = sentence_end.split(text.strip())
        return [s.strip() for s in sentences if s.strip()]

    def chunk_document(self, doc_title: str, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chunks: List[Dict[str, Any]] = []
        sequence = 1

        for sec in sections:
            sec_title = sec.get("title", "General")
            content = sec.get("content", "").strip()
            if not content:
                continue

            page_start = sec.get("page_start", 1)
            page_end = sec.get("page_end", 1)

            # Check if content fits in one chunk
            est_tokens = self._estimate_token_count(content)
            if est_tokens <= self.max_tokens:
                chunks.append({
                    "chunk_sequence": sequence,
                    "title": doc_title,
                    "section": sec_title,
                    "subsection": None,
                    "page_start": page_start,
                    "page_end": page_end,
                    "raw_text": content,
                    "normalized_text": content.lower(),
                    "token_count": est_tokens,
                    "topic_tags": [],
                    "population_tags": [],
                    "risk_tags": []
                })
                sequence += 1
            else:
                # Break down large section by paragraphs / sentences while preserving warnings together
                paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
                current_chunk_paragraphs = []
                current_tokens = 0

                for para in paragraphs:
                    para_tokens = self._estimate_token_count(para)
                    if current_tokens + para_tokens > self.max_tokens and current_chunk_paragraphs:
                        chunk_text = "\n\n".join(current_chunk_paragraphs)
                        chunks.append({
                            "chunk_sequence": sequence,
                            "title": doc_title,
                            "section": sec_title,
                            "subsection": None,
                            "page_start": page_start,
                            "page_end": page_end,
                            "raw_text": chunk_text,
                            "normalized_text": chunk_text.lower(),
                            "token_count": self._estimate_token_count(chunk_text),
                            "topic_tags": [],
                            "population_tags": [],
                            "risk_tags": []
                        })
                        sequence += 1
                        current_chunk_paragraphs = [para]
                        current_tokens = para_tokens
                    else:
                        current_chunk_paragraphs.append(para)
                        current_tokens += para_tokens

                if current_chunk_paragraphs:
                    chunk_text = "\n\n".join(current_chunk_paragraphs)
                    chunks.append({
                        "chunk_sequence": sequence,
                        "title": doc_title,
                        "section": sec_title,
                        "subsection": None,
                        "page_start": page_start,
                        "page_end": page_end,
                        "raw_text": chunk_text,
                        "normalized_text": chunk_text.lower(),
                        "token_count": self._estimate_token_count(chunk_text),
                        "topic_tags": [],
                        "population_tags": [],
                        "risk_tags": []
                    })
                    sequence += 1

        return chunks


chunker = MedicalChunker()
