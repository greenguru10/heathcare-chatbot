from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path


class BaseDocumentParser(ABC):
    @abstractmethod
    def parse(self, file_path: Path) -> Dict[str, Any]:
        """
        Parses document file and returns:
        {
            "raw_text": str,
            "sections": [{"title": str, "content": str, "page_start": int, "page_end": int}],
            "metadata": dict
        }
        """
        pass
