
from extractor import(
    load_documents,
    extract_gemma_batches,
    save_yaml
)
from utils import merge_kde_results


INPUT_COMBINATIONS = [
    ("inputs/cis-r1.pdf", "inputs/cis-r1.pdf"),
    ("inputs/cis-r1.pdf", "inputs/cis-r2.pdf"),
    ("inputs/cis-r1.pdf", "inputs/cis-r3.pdf"),
    ("inputs/cis-r1.pdf", "inputs/cis-r4.pdf"),
    ("inputs/cis-r2.pdf", "inputs/cis-r2.pdf"),
    ("inputs/cis-r2.pdf", "inputs/cis-r3.pdf"),
    ("inputs/cis-r2.pdf", "inputs/cis-r4.pdf"),
    ("inputs/cis-r3.pdf", "inputs/cis-r3.pdf"),
    ("inputs/cis-r1.pdf", "inputs/cis-r4.pdf"),
]

PROMPT_TYPES = ["zero_shot", "few_shot", "cot"]

def main():
    processed_docs = {}

    for i, (path1, path2) in enumerate(INPUT_COMBINATIONS, start=1):
        print(f"\nInput-{i}: {path1} + {path2}")

        docs = load_documents(path1, path2)

        for name_key, text_key in [("doc1_name", "doc1_text"), ("doc2_name", "doc2_text")]:
            doc_name = docs[name_key]
            doc_text = docs[text_key]

            if doc_name in processed_docs:
                print(f" Skipping {doc_name} already processed")
                continue

            print(f"    Processing {doc_name}...")
            all_results = []
            for prompt_type in PROMPT_TYPES:
                print(f"    Running {prompt_type}")
                results=extract_gemma_batches(doc_text, prompt_type)
                all_results.extend(results)
            
            kdes = merge_kde_results(all_results)
            save_yaml(kdes, doc_name, "outputs/yaml")
            processed_docs[doc_name] = True 




if __name__ == "__main__":
    main()

