from src.extractor import load_documents

def test_load_documents():
    docs = load_documents("inputs/cis-r1.pdf", "inputs/cis-r2.pdf")
    assert "doc1_text" in docs
    assert len(docs["doc1_text"]) > 0