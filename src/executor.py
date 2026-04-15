from pathlib import Path
import subprocess
import tempfile
import json
import pandas as pd

# Maps keywords found in KDE names/requirements to Kubescape control IDs.
# Built from the KDE names extracted by Gemma and the controls present in the scan.
KEYWORD_CONTROL_MAP = {
    "kubelet":                      ["C-0041", "C-0013"],
    "read-only-port":               ["C-0041"],
    "streamingConnectionIdleTimeout": ["C-0041"],
    "protect-kernel-defaults":      ["C-0013"],
    "RotateCertificate":            ["C-0262"],
    "RotateKubeletServerCertificate": ["C-0262"],
    "client certificate":           ["C-0262"],
    "anonymous":                    ["C-0262"],
    "kubeconfig":                   ["C-0262"],
    "Kubernetes Secrets":           ["C-0015"],
    "Service Account":              ["C-0053", "C-0034"],
    "service account":              ["C-0053", "C-0034"],
    "Kubernetes Roles":             ["C-0035"],
    "ClusterRole":                  ["C-0035"],
    "system:masters":               ["C-0035"],
    "Administrative":               ["C-0035"],
    "dedicated administrator":      ["C-0035"],
    "AWS IAM":                      ["C-0035"],
    "IAM roles":                    ["C-0035"],
    "Network Policy":               ["C-0260", "C-0030"],
    "CNI plugin":                   ["C-0260"],
    "Security Context":             ["C-0013", "C-0057"],
    "PodSecurityPolicy":            ["C-0057", "C-0013"],
    "eks.privileged":               ["C-0057"],
    "privileged":                   ["C-0057"],
    "hostPath":                     ["C-0048"],
    "HostPath":                     ["C-0048"],
    "hostNetwork":                  ["C-0041"],
    "HostNetwork":                  ["C-0041"],
    "hostPID":                      ["C-0038"],
    "hostIPC":                      ["C-0038"],
    "Image Scanning":               ["C-0013"],
    "Container-optimized OS":       ["C-0013"],
    "Kubernetes Namespaces":        ["C-0041"],
    "Amazon EKS":                   ["C-0035"],
}

NO_NAME_DIFF = "NO DIFFERENCES IN REGARDS TO ELEMENT NAMES"
NO_REQ_DIFF  = "NO DIFFERENCES IN REGARDS TO ELEMENT REQUIREMENTS"


def map_controls(name_diff_file: str, req_diff_file: str, output_file: str) -> None:
    data = load_text_files(name_diff_file, req_diff_file)
    name_content = data["name_diff_content"].strip()
    req_content  = data["req_diff_content"].strip()

    if NO_NAME_DIFF in name_content and NO_REQ_DIFF in req_content:
        Path(output_file).write_text("NO DIFFERENCES FOUND", encoding="utf-8")
        return

    # Collect all KDE names and requirement text from both diff files
    diff_tokens = []
    for line in (name_content + "\n" + req_content).splitlines():
        if line and "NO DIFFERENCES" not in line:
            diff_tokens.append(line.split(",")[0])   # KDE name is first field
            diff_tokens.append(line)                  # also search full line

    # Map tokens to control IDs
    matched = set()
    for token in diff_tokens:
        for keyword, control_ids in KEYWORD_CONTROL_MAP.items():
            if keyword.lower() in token.lower():
                matched.update(control_ids)

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if matched:
        output_path.write_text("\n".join(sorted(matched)), encoding="utf-8")
    else:
        output_path.write_text("NO DIFFERENCES FOUND", encoding="utf-8")


def run_kubescape(controls_file: str, scan_target: str) -> pd.DataFrame:
    controls_content = Path(controls_file).read_text(encoding="utf-8").strip()

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        tmp_path = tmp.name

    if controls_content == "NO DIFFERENCES FOUND":
        cmd = ["kubescape", "scan", scan_target, "--format", "json", "--output", tmp_path]
    else:
        control_ids = ",".join(controls_content.splitlines())
        cmd = ["kubescape", "scan", "control", control_ids, scan_target,
               "--format", "json", "--output", tmp_path]

    subprocess.run(cmd, check=True)

    with open(tmp_path, encoding="utf-8") as f:
        data = json.load(f)
    Path(tmp_path).unlink(missing_ok=True)

    controls = data["summaryDetails"]["controls"]
    rows = []
    for ctrl in controls.values():
        counters = ctrl.get("ResourceCounters", {})
        failed   = counters.get("failedResources", 0)
        passed   = counters.get("passedResources", 0)
        rows.append({
            "FilePath":         scan_target,
            "Severity":         ctrl.get("severity", ""),
            "Control name":     ctrl.get("name", ""),
            "Failed resources": failed,
            "All Resources":    failed + passed,
            "Compliance score": ctrl.get("complianceScore", 0.0),
        })

    return pd.DataFrame(rows)


def save_csv(df: pd.DataFrame, output_file: str) -> str:
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return str(output_path)


def load_text_files(name_diff: str, req_diff: str) -> dict:
    for doc_path in [name_diff, req_diff]:
        p = Path(doc_path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {p}")

    return {
        "name_diff_file": name_diff,
        "name_diff_content": Path(name_diff).read_text(encoding="utf-8"),
        "req_diff_file": req_diff,
        "req_diff_content": Path(req_diff).read_text(encoding="utf-8"),
    }

