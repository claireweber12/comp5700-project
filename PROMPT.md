# Prompts

## System Prompt

Used in `extract_gemma` for all prompt types:

```
You are a cybersecurity expert that finds security requirements in documents and returns answers in JSON.
```

---

## Zero-Shot Prompt

Function: `build_zero_shot_prompt` ([extractor.py:29](src/extractor.py#L29))

```
You are a cybersecurity expert. Identify nouns or noun phrases in the given document
Read the following security doument and identify all Key Data Elements (KDEs). A KDE is a distinct entity
(e.g. a file, configuration flag, API, network port ,role, secret, etc.) mentioned in the document that has
one or more security requirements.

Return only valid JSON (no explanation, no markdown)
BEGINNING OF DOCUMENT:

Document: {document_text}
```

---

## Few-Shot Prompt

Function: `build_few_shot_prompt` ([extractor.py:42](src/extractor.py#L42))

```
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
{
    "element1": {
        "name": "example configuration",
        "requirements": {
            "req1": "example configuration should be clear",
            "req2": "examples directly from the text are prohibited",
        },
    },
}
Find as many KDEs as you can.
BEGINNING OF DOCUMENT:
Document:{document_text}
```

---

## Chain-of-Thought (CoT) Prompt

Function: `build_cot_prompt` ([extractor.py:69](src/extractor.py#L69))

```
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
```
