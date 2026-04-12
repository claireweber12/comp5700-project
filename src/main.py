
from extractor import(
    load_documents,
    extract_gemma_batches,
    save_yaml
)
from utils import merge_kde_results
from comparator import compare_names, compare_requirements
from pathlib import Path


INPUT_COMBINATIONS = [
    ("inputs/cis-r1.pdf", "inputs/cis-r1.pdf"),
    ("inputs/cis-r1.pdf", "inputs/cis-r2.pdf"),
    ("inputs/cis-r1.pdf", "inputs/cis-r3.pdf"),
    ("inputs/cis-r1.pdf", "inputs/cis-r4.pdf"),
    ("inputs/cis-r2.pdf", "inputs/cis-r2.pdf"),
    ("inputs/cis-r2.pdf", "inputs/cis-r3.pdf"),
    ("inputs/cis-r2.pdf", "inputs/cis-r4.pdf"),
    ("inputs/cis-r3.pdf", "inputs/cis-r3.pdf"),
    ("inputs/cis-r3.pdf", "inputs/cis-r4.pdf"),
]

PROMPT_TYPES = ["zero_shot", "few_shot", "cot"]

def main():
    processed_docs = {}

    for i, (path1, path2) in enumerate(INPUT_COMBINATIONS, start=1):
        print(f"\nInput-{i}: {path1} + {path2}")

        docs = load_documents(path1, path2)
        yaml_paths = []

        for name_key, text_key in [("doc1_name", "doc1_text"), ("doc2_name", "doc2_text")]:
            doc_name = docs[name_key]
            doc_text = docs[text_key]

            if doc_name in processed_docs:
                print(f" Skipping {doc_name} already processed")
                yaml_paths.append(processed_docs[doc_name])
                continue

            print(f"    Processing {doc_name}...")
            all_results = []
            for prompt_type in PROMPT_TYPES:
                print(f"    Running {prompt_type}")
                results=extract_gemma_batches(doc_text, prompt_type)
                all_results.extend(results)
            
            kdes = merge_kde_results(all_results)
            yaml_path = save_yaml(kdes, doc_name, "outputs/yaml")
            processed_docs[doc_name] = yaml_path
            yaml_paths.append(yaml_path)

        yaml1, yaml2 = yaml_paths
        stem1 = Path(yaml1).stem.replace("-kdes", "")
        stem2 = Path(yaml2).stem.replace("-kdes", "")

        print(f"    Comparing {stem1} and {stem2}")
        compare_names(yaml1, yaml2, f"outputs/text/{stem1}_{stem2}_name_differences.txt")
        compare_requirements(yaml1, yaml2, f"outputs/text/{stem1}_{stem2}_req_differences.txt")





if __name__ == "__main__":
    main()

