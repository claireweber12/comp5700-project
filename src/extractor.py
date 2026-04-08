from pathlib import Path
from src.utils import extract_text


def load_documents(pdf_path1: str, pdf_path2: str) -> dict:
    Path1 = Path(pdf_path1)
    Path2 = Path(pdf_path2)
    Paths = [Path1, Path2]
    for p in Paths:
        if not p.exists():
            raise FileNotFoundError(f"File not found {p}")
        if p.suffix.lower() != ".pdf":
            raise ValueError(f"Invalid file type for {p}. Expected a PDF")
    
    doc1_name, doc1_text = extract_text(pdf_path1)
    doc2_name, doc2_text = extract_text(pdf_path2)
    return {
        "doc1_name": doc1_name,
        "doc1_text":doc1_text,
        "doc2_name":doc2_name,
        "doc2_text":doc2_text
    }

def build_zero_shot_prompt(document_text: str) -> str:
    ...

def build_few_shot_prompt(document_text:str) -> str:
    ...

def build_cot_prompt(document_text:str) -> str:
    ...

# put prompts in PROMPT.md


def extract_gemma(document_text:str, prompt:str, promopt_type:str) -> dict:
    ...

def save_yaml(kde_dict: dict, original_pdf_name: str, output_dir: str) -> str:
    ...

def save_llm_output_log(llm_name: str, prompt_used :str, prompt_type: str, llm_output:str, output_file: str) -> None:
    ...
