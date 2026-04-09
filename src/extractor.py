from pathlib import Path
from src.utils import extract_text
import yaml
import json


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
    Use the table of contents to determine the key data elements listed in the document and their associated requirements. Sections are numbered on 
    the table of contents with KDEs numbered underneath them as subsections. The KDE's associated requirements are numbered under the KDE as subsections.
    One KDE can map to multiple requirements. Ignore section headers which are numbered as whole numbers. 
    Generate a nested dictonary with the following fields: 
    - element1:
        - name:
        - requirements: 
            - req1
            - req2 
            - req3 
    """.strip()

def build_few_shot_prompt(document_text:str) -> str:
    return f"""
    Use the table of contents to determine the key data elements listed in the document and their associated requirements. Sections are numbered on 
    the table of contents with KDEs numbered underneath them as subsections. The KDE's associated requirements are numbered under the KDE as subsections.
    One KDE can map to multiple requirements. Ignore section headers which are numbered as whole numbers. 
    Generate a nested dictonary with the following fields: 
    - element1:
        - name:
        - requirements: 
            - req1
            - req2 
            - req3 
    
    For Example:
    Document snippet: 
    1. Authentication
        1.1 Password data
            1.1.1 passwords shall be encrypted
        1.2 Audit log data 
            1.2.1 Audit logs shall be maintained for login attempts 
    Output:
    {{
        "element1": {{
            "name": "Password data",
            "requirements": [
                "Passwords shall be encrypted",
            ]
        }}
        "element2":{{
            "name": "Audit log data",
            "requirements": [
                "Audit logs shall be maintained for login attempts"
            ]
        }}
    }}
    Document:{document_text}
    """.strip()

def build_cot_prompt(document_text:str) -> str:
    return f"""
    Use the table of contents to determine the key data elements listed in the document and their associated requirements. Sections are numbered on 
    the table of contents with KDEs numbered underneath them as subsections. The KDE's associated requirements are numbered under the KDE as subsections.
    One KDE can map to multiple requirements. Ignore section headers which are numbered as whole numbers. 
    Think through it step by step. 
    Generate a nested dictonary with the following fields: 
    - element1:
        - name:
        - requirements: 
            - req1
            - req2 
            - req3 

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
    return str(yaml_file)

def save_llm_output_log(llm_name: str, prompt_used :str, prompt_type: str, llm_output:str, output_file: str) -> None:
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok = True)

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(f"LLM Name\n{llm_name}\n\n")
        file.write(f"Prompt Used\n{prompt_used}\n\n")
        file.write(f"Prompt Type\n{prompt_type}\n\n")
        file.write(f"LLM Output\n{json.dumps(llm_output, indent=2)}\n")

    return str(output_path)       
