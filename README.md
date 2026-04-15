# comp5700-project
### Claire Weber - cmw0165@auburn.edu
This project is a security tool that identifies differences in two security documents and executes a static analysis tool based on the identified differences. 

Pipeline:

1.   Extractor — Loads two CIS benchmark PDFs and uses the Gemma-3-1B-IT LLM with zero-shot, few-shot, and chain-of-thought prompting to extract Key Data Elements (KDEs) and their security requirements. Outputs YAML files per document.
   
2.   Comparator — Compares the two YAML files to identify differences in KDE names and requirements. Outputs two TEXT files summarizing the differences.
   
3.   Executor — Maps differences to relevant Kubescape controls, runs Kubescape against the provided Kubernetes YAML files, and outputs a CSV with scan results.

**LLM Used**: google/gemma-3-1b-it

#### How to run:

**Run all 9 input combinations (PDFs must be in inputs/)**

./dist/pipeline

**Run a specific pair**

./dist/pipeline inputs/cis-r1.pdf inputs/cis-r2.pdf

**Specify a different YAML scan target**

./dist/pipeline inputs/cis-r1.pdf inputs/cis-r2.pdf --scan-target path/to/YAMLfiles


