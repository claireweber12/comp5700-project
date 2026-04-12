import pytest
from pathlib import Path
import yaml
from src.comparator import load_yamls, compare_names, compare_requirements

@pytest.fixture
def sample_yamls(tmp_path):
    doc1 = {
        "element1": {"name": "kubelet", "requirements": {"req1": "kubelet must be configured"}},
        "element2": {"name": "Anonymous Auth", "requirements": {"req1": "Anonymous Auth must be disabled"}},
        "element3": {"name": "kubeconfig file", "requirements": {"req1": "permissions must be 644"}},
    }
    doc2 = {
        "element1": {"name": "kubelet", "requirements": {"req1": "kubelet must be configured"}},
        "element2": {"name": "Anonymous Auth", "requirements": {"req1": "Anonymous Auth must be disabled", "req2": "webhook must be enabled"}},
        "element3": {"name": "readOnlyPort", "requirements": {"req1": "readOnlyPort must be set to 0"}},
    }

    path1 = tmp_path / "cis-r1-kdes.yaml"
    path2 = tmp_path / "cis-r2-kdes.yaml"

    path1.write_text(yaml.dump(doc1))
    path2.write_text(yaml.dump(doc2))

    return str(path1), str(path2)


def test_load_yamls(sample_yamls):
    path1, path2 = sample_yamls
    data = load_yamls(path1, path2)

    assert "cis-r1" in data
    assert "cis-r2" in data
    assert "kubelet" in data["cis-r1"]
    assert data["cis-r1"]["kubelet"] == {"req1": "kubelet must be configured"}


def test_compare_names(sample_yamls, tmp_path):
    path1, path2 = sample_yamls
    output_file = str(tmp_path / "name_differences.txt")

    compare_names(path1, path2, output_file)

    content = Path(output_file).read_text()
    assert "kubeconfig file,ABSENT-IN-cis-r2,PRESENT-IN-cis-r1,NA" in content
    assert "readOnlyPort,ABSENT-IN-cis-r1,PRESENT-IN-cis-r2,NA" in content


def test_compare_requirements(sample_yamls, tmp_path):
    path1, path2 = sample_yamls
    output_file = str(tmp_path / "req_differences.txt")

    compare_requirements(path1, path2, output_file)

    content = Path(output_file).read_text()
    # name absent in one file
    assert "kubeconfig file,ABSENT-IN-cis-r2,PRESENT-IN-cis-r1,NA" in content
    assert "readOnlyPort,ABSENT-IN-cis-r1,PRESENT-IN-cis-r2,NA" in content
    # requirement present in one but not the other
    assert "Anonymous Auth,ABSENT-IN-cis-r1,PRESENT-IN-cis-r2,webhook must be enabled" in content