from backend.services.ingest import chunk_text, _normalise_record


def test_chunk_text_returns_content():
    chunks = chunk_text("DIEMS admission information. " * 100, chunk_size=100, overlap=10)
    assert chunks
    assert all(chunk.strip() for chunk in chunks)


def test_faq_record_normalisation():
    record = _normalise_record({"question": "What is the fee?", "answer": "See official notice", "category": "Fees"}, "x", "faq.csv")
    assert record["text"] == "Question: What is the fee? Answer: See official notice"
    assert record["metadata"]["category"] == "Fees"
