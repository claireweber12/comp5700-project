from pathlib import Path
from utils import extract_text, chunk_text, make_batches, build_batch_text
import yaml
import json
import torch
from transformers import pipeline 
import re


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
    You are a cybersecurity expert. Identify nouns or noun phrases in the given document
    Read the following security doument and identify all Key Data Elements (KDEs). A KDE is a distinct entity
    (e.g. a file, configuration flag, API, network port ,role, secret, etc.) mentioned in the document that has
    one or more security requirements.

    Return only valid JSON (no explanation, no markdown)
    BEGINNING OF DOCUMENT:

    Document: {document_text}
    """.strip()

def build_few_shot_prompt(document_text:str) -> str:
    return f"""
    You are a cybersecurity expert. Identify nouns or noun phrases in the given document
    Read the following security doument and identify all Key Data Elements (KDEs). A KDE is a distinct entity
    (e.g. a file, configuration flag, API, network port ,role, secret, etc.) mentioned in the document that has
    one or more security requirements.
    Then return only the final answer in valid JSON format. Do not include any explanation or markdown — output raw JSON only.

    For Example (do not include example in your output):
    Example Document snippet: 
    "1.2.3 example configuration should be clear"
    "examples directly from the text are prohibited"
    Output:
    {{
        "element1": {{
            "name": "example configuration",
            "requirements": {{
                "req1": "example configuration should be clear",
                "req2": "examples directly from the text are prohibited",
            }},
        }},
    }}
    Find as many KDEs as you can.
    BEGINNING OF DOCUMENT:
    Document:{document_text}
    """.strip()

def build_cot_prompt(document_text:str) -> str:
    return f"""
    You are a cybersecurity expert. Your taask is to extract Key Data Elements (KDEs)
    and their security requirements from the document below.

    Follow these reasoning steps:
    1. Read the document carefilly and list every concerete entity (file path, configuration flag, role, port, secret, network
    component, API, etc.)
    2. For each entity, collect every requirement, constraint, ot instruction
    3. Merge duplicate entries - one KDE may have multiple requirements
    4. Output ONLY the final JSON. No text prose before or after. 

    DOCUMENT:
        {document_text}
 
        (Begin with your step-by-step reasoning inside <!-- --> comments, then
        output the JSON after the closing comment.)
 
        <!--
        Step 1 – Entities found:
        Step 2 – Requirements per entity:
        Step 3 – Merged list:
        -->
        JSON:
    """.strip()


def build_prompt(document_text:str, prompt_type:str) -> str:
    """ 
    Wrapper to build prompts using a single function 
    """
    if prompt_type == "zero_shot":
        return build_zero_shot_prompt(document_text)
    elif prompt_type == "few_shot":
        return build_few_shot_prompt(document_text)
    elif prompt_type == "cot":
        return build_cot_prompt(document_text)
    else:
        raise ValueError(f"Unknown prompt type: {prompt_type}")
    
def extract_gemma_batches(document_text:str, prompt_type:str) -> list:
    chunks = chunk_text(document_text, chunk_size=800, overlap=50)
    batches = make_batches(chunks, batch_size = 4)

    all_outputs = []
    print(f"Total chunks:{len(chunks)}")
    print(f"Total batches: {len(batches)}")
    for i, batch in enumerate(batches, start=1):
        print(f"Processing batch {i}/{len(batches)}")
        batch_text = build_batch_text(batch)
        prompt = build_prompt(batch_text, prompt_type)
        output = extract_gemma(batch_text, prompt, prompt_type)

        all_outputs.append({
            "batch_number": i,
            "chunks_in_batch": len(batch),
            "output":output
        })
    return all_outputs 


pipe = pipeline("text-generation", model="google/gemma-3-1b-it", device="cpu", dtype=torch.float16)

def extract_gemma(document_text:str, prompt:str, prompt_type:str) -> dict:
    messages = [
        
        {
            "role": "system",
            "content": [{"type":"text", "text":"You analyze documents to find security requirements and return answers in JSON format."}, ]
        },
        {
            "role":"user",
            "content":[{"type":"text", "text": prompt}]
        },
        
    ]

    output = pipe(messages, return_full_text=False, max_new_tokens=5000)
    save_llm_output_log("google/gemma-3-1b-it", prompt, prompt_type, output, "outputs/text/gemma_log.txt")
    return parse_gemma_output(output)

def save_yaml(kde_dict: dict, original_pdf_name: str, output_dir: str) -> str:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    yaml_file = output_path / f"{original_pdf_name}-kdes.yaml"

    with open(yaml_file, "w", encoding="utf-8") as file:
        yaml.dump(kde_dict, file)
    return str(yaml_file)

def save_llm_output_log(llm_name: str, prompt_used :str, prompt_type: str, llm_output:str, output_file: str) -> str:
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok = True)

    with open(output_path, "a", encoding="utf-8") as file:
        file.write(f"LLM Name\n{llm_name}\n\n")
        file.write(f"Prompt Used\n{prompt_used}\n\n")
        file.write(f"Prompt Type\n{prompt_type}\n\n")
        file.write(f"LLM Output\n{json.dumps(llm_output, indent=2, default=str)}\n")

    return str(output_path)       

def parse_gemma_output(output) -> dict:
    try:
        generated_text = output[0]["generated_text"]
    except (KeyError, IndexError, TypeError):
        return {
            "error": "Could not extract generated text from model output",
            "raw_output": output
        }

    # Strip markdown code fences if present
    text = generated_text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL).strip()
    if "JSON:" in text:
        text = text.split("JSON:", 1)[1].strip()
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting the first complete JSON object from the text
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end+1])
        except json.JSONDecodeError:
            pass

    return {"raw_output": generated_text}