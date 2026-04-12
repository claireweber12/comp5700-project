import yaml 
from pathlib import Path

def load_yamls(doc1:str, doc2:str):
    results = {}

    for doc_path in [doc1, doc2]:
        p = Path(doc_path)
        stem = p.stem.replace("-kdes", "")

        with open(p, 'r') as file:
            raw = yaml.safe_load(file)
        
        transformed = {}
        for element in raw.values():
            name = element.get("name")
            requirements = element.get("requirements", {})
            transformed[name] = requirements
        
        results[stem] = transformed
    return results

def compare_names(doc1:str, doc2:str, output_file:str):
    data = load_yamls(doc1, doc2)

    stems = list(data.keys())
    stem1, stem2 = stems[0], stems[1]

    names1 = set(data[stem1].keys())
    names2 = set(data[stem2].keys())

    only_in_1 = names1 - names2
    only_in_2 = names2 - names1

    lines = []
    for name in only_in_1:
        lines.append(f"{name},ABSENT-IN-{stem2},PRESENT-IN-{stem1},NA")
    for name in only_in_2:
        lines.append(f"{name},ABSENT-IN-{stem1},PRESENT-IN-{stem2},NA")
    
    with open(output_file, 'w') as file:
        if not lines:
            file.write("NO DIFFERENCES IN REGARDS TO ELEMENT NAMES")
        else:
            file.write("\n".join(lines))


def compare_requirements(doc1:str, doc2: str, output_file:str):
    data = load_yamls(doc1, doc2)
    
    stems = list(data.keys())
    stem1, stem2 = stems[0], stems[1]

    names1 = set(data[stem1].keys())
    names2 = set(data[stem2].keys())

    only_in_1 = names1 - names2
    only_in_2 = names2 - names1
    in_both = names1 & names2

    lines = []

    for name in only_in_1:
        lines.append(f"{name},ABSENT-IN-{stem2},PRESENT-IN-{stem1},NA")
    
    for name in only_in_2:
        lines.append(f"{name},ABSENT-IN-{stem1},PRESENT-IN-{stem2},NA")

    for name in in_both:
        reqs1 = set((data[stem1][name] or {}).values())
        reqs2 = set((data[stem2][name] or {}).values())
        
        only_req_in_1 = reqs1 - reqs2
        only_req_in_2 = reqs2 - reqs1
        
        for req in only_req_in_1:
            lines.append(f"{name},ABSENT-IN-{stem2},PRESENT-IN-{stem1},{req}")
        for req in only_req_in_2:
            lines.append(f"{name},ABSENT-IN-{stem1},PRESENT-IN-{stem2},{req}")

    with open (output_file, 'w') as file:
        if not lines:
            file.write("NO DIFFERENCES IN REGARDS TO ELEMENT REQUIREMENTS")
        else:
            file.write("\n".join(lines))

    

