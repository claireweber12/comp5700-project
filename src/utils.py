from pypdf import PdfReader
from pathlib import Path

def extract_text(pdf_path:str) -> str:
    '''
    Helper function that reads a pdf document and returns file
    name and extracted text
    '''
    path = Path(pdf_path)
    reader = PdfReader(str(path))
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)
        full_text = "\n".join(text_parts).strip()

        if not full_text:
            raise ValueError(f"No text could be extracted from {pdf_path}")
        
        return path.stem, full_text