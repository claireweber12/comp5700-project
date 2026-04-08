from src.extractor import(
    load_documents,
    build_zero_shot_prompt,
    build_few_shot_prompt,
    build_cot_prompt,
    extract_gemma,
    save_yaml,
    save_llm_output_log,
)

def main():
    docs = load_documents("inputs/cis-r1.pdf", "inputs/cis-r2.pdf")
    prompt = build_zero_shot_prompt()
    kde_output = extract_gemma(docs["doc1_text"], prompt, "zero-shot")

    yaml_path = save_yaml(kde_output, docs["doc1_name"], "outputs/yaml")
    log_path = save_llm_output_log(
        llm_name = "google/gemma-3-1b-it", 
        prompt_used = prompt,
        prompt_type = "zero-shot",
        llm_output = kde_output,
        output_file = "outputs/text/doc1_zero_shot_log.txt",
    )

    print("YAML saved to: ", yaml_path)
    print("Log saved to: ", log_path)



if __name__ == "__main__":
    main()