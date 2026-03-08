from src.app import get_github_repo

def test_get_github_repo_standard():
    url = "https://github.com/dsheehan/qrchive"
    assert get_github_repo(url) == "dsheehan/qrchive"

def test_get_github_repo_trailing_slash():
    url = "https://github.com/dsheehan/qrchive/"
    assert get_github_repo(url) == "dsheehan/qrchive"

def test_get_github_repo_extra_path():
    url = "https://github.com/dsheehan/qrchive/tree/main"
    assert get_github_repo(url) == "dsheehan/qrchive"

def test_get_github_repo_no_protocol():
    url = "github.com/dsheehan/qrchive"
    assert get_github_repo(url) == "dsheehan/qrchive"

def test_get_github_repo_fallback():
    url = "https://gitlab.com/dsheehan/qrchive"
    assert get_github_repo(url) == "dsheehan/qrchive"  # Our current fallback
