from backend.app.ingestion.chunker import MedicalChunker


def test_medical_chunker_preserves_sections():
    chunker = MedicalChunker(target_tokens=350, max_tokens=500)
    sections = [
        {"title": "Section 1", "content": "Short text about blood pressure.", "page_start": 1, "page_end": 1},
        {"title": "Section 2", "content": "Another short paragraph describing healthy dietary habits.", "page_start": 2, "page_end": 2}
    ]
    chunks = chunker.chunk_document("Test Guide", sections)
    assert len(chunks) == 2
    assert chunks[0]["title"] == "Test Guide"
    assert chunks[0]["section"] == "Section 1"
    assert chunks[1]["section"] == "Section 2"
    assert chunks[0]["token_count"] > 0
