import json
import pandas as pd
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.executor import load_text_files, map_controls, run_kubescape, save_csv


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def diff_files(tmp_path):
    """Two diff TEXT files that contain real differences."""
    name_diff = tmp_path / "name_diff.txt"
    req_diff  = tmp_path / "req_diff.txt"
    name_diff.write_text(
        "Kubernetes Secrets,ABSENT-IN-cis-r2,PRESENT-IN-cis-r1,NA\n"
        "Network Policy,ABSENT-IN-cis-r1,PRESENT-IN-cis-r2,NA",
        encoding="utf-8",
    )
    req_diff.write_text(
        "kubelet,ABSENT-IN-cis-r2,PRESENT-IN-cis-r1,--read-only-port should be 0",
        encoding="utf-8",
    )
    return str(name_diff), str(req_diff)


@pytest.fixture
def no_diff_files(tmp_path):
    """Two diff TEXT files that report no differences."""
    name_diff = tmp_path / "name_diff.txt"
    req_diff  = tmp_path / "req_diff.txt"
    name_diff.write_text("NO DIFFERENCES IN REGARDS TO ELEMENT NAMES", encoding="utf-8")
    req_diff.write_text("NO DIFFERENCES IN REGARDS TO ELEMENT REQUIREMENTS", encoding="utf-8")
    return str(name_diff), str(req_diff)


# ---------------------------------------------------------------------------
# test_load_text_files
# ---------------------------------------------------------------------------

def test_load_text_files(diff_files):
    name_path, req_path = diff_files
    result = load_text_files(name_path, req_path)

    assert result["name_diff_file"] == name_path
    assert result["req_diff_file"]  == req_path
    assert "Kubernetes Secrets" in result["name_diff_content"]
    assert "kubelet"             in result["req_diff_content"]


# ---------------------------------------------------------------------------
# test_map_controls
# ---------------------------------------------------------------------------

def test_map_controls(diff_files, tmp_path):
    name_path, req_path = diff_files
    output_file = str(tmp_path / "controls.txt")

    map_controls(name_path, req_path, output_file)

    content = Path(output_file).read_text(encoding="utf-8")
    assert content != "NO DIFFERENCES FOUND"
    # Kubernetes Secrets → C-0015, Network Policy → C-0260/C-0030, kubelet → C-0041/C-0013
    assert "C-0015" in content
    assert "C-0260" in content
    assert "C-0041" in content


def test_map_controls_no_differences(no_diff_files, tmp_path):
    name_path, req_path = no_diff_files
    output_file = str(tmp_path / "controls.txt")

    map_controls(name_path, req_path, output_file)

    content = Path(output_file).read_text(encoding="utf-8")
    assert content == "NO DIFFERENCES FOUND"


# ---------------------------------------------------------------------------
# test_run_kubescape
# ---------------------------------------------------------------------------

def test_run_kubescape(tmp_path):
    controls_file = tmp_path / "controls.txt"
    controls_file.write_text("C-0015\nC-0035", encoding="utf-8")

    fake_json = {
        "summaryDetails": {
            "controls": {
                "C-0015": {
                    "name": "List Kubernetes secrets",
                    "severity": "High",
                    "complianceScore": 80.0,
                    "ResourceCounters": {"failedResources": 2, "passedResources": 8},
                },
                "C-0035": {
                    "name": "Administrative Roles",
                    "severity": "Medium",
                    "complianceScore": 100.0,
                    "ResourceCounters": {"failedResources": 0, "passedResources": 5},
                },
            }
        }
    }

    def fake_subprocess(cmd, check):
        # Write fake JSON to the --output path kubescape would have used
        out_path = cmd[cmd.index("--output") + 1]
        Path(out_path).write_text(json.dumps(fake_json), encoding="utf-8")

    with patch("src.executor.subprocess.run", side_effect=fake_subprocess):
        df = run_kubescape(str(controls_file), "YAMLfiles")

    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == [
        "FilePath", "Severity", "Control name",
        "Failed resources", "All Resources", "Compliance score",
    ]
    assert len(df) == 2
    assert "List Kubernetes secrets" in df["Control name"].values


# ---------------------------------------------------------------------------
# test_save_csv
# ---------------------------------------------------------------------------

def test_save_csv(tmp_path):
    df = pd.DataFrame([{
        "FilePath": "YAMLfiles",
        "Severity": "High",
        "Control name": "List Kubernetes secrets",
        "Failed resources": 2,
        "All Resources": 10,
        "Compliance score": 80.0,
    }])
    output_file = str(tmp_path / "results.csv")

    result_path = save_csv(df, output_file)

    assert Path(result_path).exists()
    loaded = pd.read_csv(result_path)
    assert list(loaded.columns) == [
        "FilePath", "Severity", "Control name",
        "Failed resources", "All Resources", "Compliance score",
    ]
    assert loaded.iloc[0]["Control name"] == "List Kubernetes secrets"
    assert loaded.iloc[0]["Compliance score"] == 80.0
