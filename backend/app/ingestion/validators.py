import hashlib
from pathlib import Path
from backend.app.core.exceptions import DocumentIngestionException


def compute_sha256(file_path: Path) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def validate_document_file(file_path: Path, max_mb: int = 25):
    if not file_path.exists():
        raise DocumentIngestionException(f"File does not exist: {file_path}")

    size_mb = file_path.stat().st_size / (1024 * 1024)
    if size_mb > max_mb:
        raise DocumentIngestionException(f"File size {size_mb:.2f}MB exceeds limit of {max_mb}MB")

    allowed_exts = {".pdf", ".html", ".htm", ".txt", ".md"}
    if file_path.suffix.lower() not in allowed_exts:
        raise DocumentIngestionException(f"Unsupported file extension: {file_path.suffix}. Allowed: {allowed_exts}")
