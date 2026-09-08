from backend.app.generation.citation_validator import citation_validator


def test_valid_citations():
    evidence = [{"chunk": {"title": "Doc 1"}}, {"chunk": {"title": "Doc 2"}}]
    answer = "Hypertension refers to high blood pressure [S1]. Salt intake should be minimized [S2]."
    is_valid, errors, meta = citation_validator.validate_citations(answer, evidence)
    assert is_valid is True
    assert len(errors) == 0
    assert "S1" in meta["cited_markers"]
    assert "S2" in meta["cited_markers"]


def test_invalid_nonexistent_citation():
    evidence = [{"chunk": {"title": "Doc 1"}}]
    answer = "Hypertension is common [S1]. It requires emergency surgery immediately [S99]."
    is_valid, errors, meta = citation_validator.validate_citations(answer, evidence)
    assert is_valid is False
    assert any("S99" in err for err in errors)
