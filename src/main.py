
from extractor import(
    load_documents,
    extract_gemma_batches,
    save_yaml
)
from utils import merge_kde_results
from pypdf import PdfReader



def main():
    
    docs = load_documents("inputs/cis-r1.pdf", "inputs/cis-r2.pdf")
    doc1_results = extract_gemma_batches(docs["doc1_text"], "few_shot")
    doc1_kdes = merge_kde_results(doc1_results)
    save_yaml(doc1_kdes, "cis-r1", "outputs/yaml")

    doc2_results = extract_gemma_batches(docs["doc2_text"], "few_shot")
    doc2_kdes = merge_kde_results(doc2_results)
    save_yaml(doc2_kdes, docs["doc2_name"], "outputs/yaml")





if __name__ == "__main__":
    main()

