from pathlib import Path
from src.utils import extract_text
import yaml
import json
from typing import Dict, Any


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
    return f"""
    Given the following security requirements document, identify the key data elements
    For each key data element list:
    1. The name of the key data element
    2. The requirements associated with that element
    Return your answer in valid JSON using this format:
    {{
        "element1": {{
            "name": "name of key data element",
            "requirements": [
                "requirement 1",
                "requirement 2"
            ]
        }}
    }}
    Document:{document_text}
    """.strip()

def build_few_shot_prompt(document_text:str) -> str:
    return f"""
    Given the following security requirements document, identify the key data elements
    For each key data element list:
    1. The name of the key data element
    2. The requirements associated with that element
    Return your answer in valid JSON using this format:
    {{
        "element1": {{
            "name": "name of key data element",
            "requirements": [
                "requirement 1",
                "requirement 2"
            ]
        }}
    }}
    For Example:
    Document snippet: "The system shall encrypt passwords and maintain audit logs for login attempts."
    Output:
    {{
        "element1": {{
            "name": "password data",
            "requirements": [
                "passwords shall be encrypted",
            ]
        }}
        "element2":{{
            "name": "audit log data",
            "requirements": [
                "audit logs shall be maintained for login attempts"
            ]
        }}
    }}
    Document:{document_text}
    """.strip()

def build_cot_prompt(document_text:str) -> str:
    return f"""
    Carefully analyze the security requirements document step by step:
    1. Read the document
    2. Identify nouns or noun phrases that represent key data elements
    3. Determine which requirements refer to each entity
    4. Group related requirements under the correct key data element 

    Then, return only the final answer in valid JSON using this format:
    {{
        "element1": {{
            "name": "name of key data element",
            "requirements": [
                "requirement 1",
                "requirement 2"
            ]
        }}
    }}
    Document: {document_text}
    """.strip()


def extract_gemma(document_text:str, prompt:str, promopt_type:str) -> dict:
    mock_output = {
        "element1": {
            "name": "authentication data",
            "requirements":[
                "authentication data must be protected",
                "authentication data must be validated"
            ]
        },
        "element2":{
            "name": "audit log data",
            "requirements":[
                "audit log data must be retained"
            ]
        }
    }
    return mock_output

def save_yaml(kde_dict: dict, original_pdf_name: str, output_dir: str) -> str:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    yaml_file = output_path / f"{original_pdf_name}-kdes.yaml"

    with open(yaml_file, "w", encoding="utf-8") as file:
        yaml.dump(kde_dict, file)
    return yaml_file

def save_llm_output_log(llm_name: str, prompt_used :str, prompt_type: str, llm_output:str, output_file: str) -> None:
    ...
