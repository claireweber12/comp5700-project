import pdfplumber
from pathlib import Path
from typing import List

def extract_text(pdf_path: str):

    path = Path(pdf_path)
    full_text = []
    target_header = "Recommendations"
    start_extracting = False

    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            header_area = page.crop((0,0,page.width, 100))
            header_text = header_area.extract_text() or ""
            if target_header.lower() in header_text.lower():
                start_extracting = True 

            if "appendix" in header_text.lower():
                break
            if start_extracting:
                text = page.extract_text()
                if text:
                    full_text.append(f"\n--- Page {i+1} ---\n{text}")

    
    return path.stem, "\n".join(full_text)
    

def chunk_text(text:str, chunk_size: int, overlap: int) -> List[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if overlap < 0:
        raise ValueError("overlap cannnot be negative")
    if overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk_size")
    
    chunks=[]
    step = chunk_size - overlap

    for start in range(0, len(text), step):
        end = start + chunk_size
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk)
        if end >= len(text):
            break
    return chunks 

def make_batches(chunks: List[str], batch_size: int) -> List[List[str]]:
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than 0")
    
    return [chunks[i:i+ batch_size] for i in range(0, len(chunks), batch_size)]

def build_batch_text(chunk_batch: list[str]) -> str:
    return "\n\n".join(
        [f"Chunk {i+1}:\n{chunk}" for i, chunk in enumerate(chunk_batch)]
    )

def merge_kde_results(batch_results: list) -> dict:
    merged = {}
    element_counter = 1

    for batch in batch_results:
        output = batch.get("output", {})

        if not isinstance(output, dict):
            continue

        for _, value in output.items():
            if not isinstance(value, dict):
                continue
            name = value.get("name")
            requirements = value.get("requirements", [])
            if not name:
                continue

            existing_key = None
            for key, existing_value in merged.items():
                if existing_value["name"].lower() == name.lower():
                    existing_key = key
                    break

            existing_reqs = merged[existing_key]["requirements"] if existing_key else {}
            new_reqs = requirements if isinstance(requirements, dict) else {}

            if existing_key:
                existing_vals = set(existing_reqs.values())
                next_idx = len(existing_reqs) + 1
                for req_text in new_reqs.values():
                    if req_text not in existing_vals:
                        existing_reqs[f"req{next_idx}"] = req_text
                        next_idx += 1
            else:
                merged[f"element{element_counter}"] = {
                "name": name,
                "requirements": dict(new_reqs)
                }
                element_counter += 1
    return merged                                   