from src.extractor import load_documents
from src.extractor import build_zero_shot_prompt, build_few_shot_prompt, build_cot_prompt


def test_load_documents():
    docs = load_documents("inputs/cis-r1.pdf", "inputs/cis-r2.pdf")
    assert "doc1_text" in docs
    assert len(docs["doc1_text"]) > 0

def test_build_zero_shot_prompt():
    text= "Passwords must be encrypted."
    prompt = build_zero_shot_prompt(text)
    assert "Passwords must be encrypted." in prompt
    assert "valid JSON" in prompt

def test_build_few_shot_prompt():
    text = "Passwords must be encrypted."
    prompt = build_few_shot_prompt(text)
    assert "Passwords must be encrypted." in prompt
    assert "valid JSON" in prompt

def test_build_cot_prompt():
    text = "Passwords must be encrypted."
    prompt = build_cot_prompt(text)
    assert "Passwords must be encrypted." in prompt
    assert "valid JSON" in prompt