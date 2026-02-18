import pytest
from pysealer.check_decorators import check_decorators, check_decorators_in_folder

# Dummy signature verification and public key for patching
import pysealer

def dummy_verify_signature(source, signature, key):
    # Accept 'validsig', reject others
    return signature == "validsig"

def dummy_get_public_key():
    return "dummy_public_key"

def dummy_is_git_available():
    return False

def dummy_get_function_diff(*args, **kwargs):
    return [("-", "old", 1), ("+", "new", 2)]

@pytest.fixture(autouse=True)
def patch_pysealer(monkeypatch):
    import pysealer.check_decorators as check_decorators_mod
    monkeypatch.setattr(check_decorators_mod, "verify_signature", dummy_verify_signature)
    monkeypatch.setattr(check_decorators_mod, "get_public_key", dummy_get_public_key)
    monkeypatch.setattr(check_decorators_mod, "is_git_available", dummy_is_git_available)
    monkeypatch.setattr(check_decorators_mod, "get_function_diff", dummy_get_function_diff)
    yield

def test_check_decorators_valid(tmp_path):
    code = """
@pysealer._validsig()
def foo():
    return 1
"""
    file_path = tmp_path / "test.py"
    file_path.write_text(code)
    results = check_decorators(str(file_path))
    assert "foo" in results
    assert results["foo"]["valid"]
    assert results["foo"]["has_decorator"]
    assert "validsig" == results["foo"]["signature"]
    assert "✓" in results["foo"]["message"]

def test_check_decorators_invalid(tmp_path):
    code = """
@pysealer._wrongsig()
def bar():
    return 2
"""
    file_path = tmp_path / "test2.py"
    file_path.write_text(code)
    results = check_decorators(str(file_path))
    assert "bar" in results
    assert not results["bar"]["valid"]
    assert results["bar"]["has_decorator"]
    assert results["bar"]["signature"] == "wrongsig"
    assert "✗" in results["bar"]["message"]

def test_check_decorators_no_decorator(tmp_path):
    code = """
def baz():
    return 3
"""
    file_path = tmp_path / "test3.py"
    file_path.write_text(code)
    results = check_decorators(str(file_path))
    assert "baz" in results
    assert not results["baz"]["has_decorator"]
    assert "No pysealer decorator" in results["baz"]["message"]

def test_check_decorators_in_folder(tmp_path):
    file1 = tmp_path / "a.py"
    file2 = tmp_path / "b.py"
    file1.write_text("@pysealer._validsig()\ndef f():\n return 1\n")
    file2.write_text("def g():\n return 2\n")
    results = check_decorators_in_folder(str(tmp_path))
    assert str(file1) in results
    assert str(file2) in results
    assert results[str(file1)]["f"]["valid"]
    assert not results[str(file2)]["g"]["has_decorator"]

def test_check_decorators_in_folder_errors(tmp_path):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    with pytest.raises(ValueError):
        check_decorators_in_folder(str(empty_dir))
    file = tmp_path / "file.txt"
    file.write_text("hi")
    with pytest.raises(NotADirectoryError):
        check_decorators_in_folder(str(file))
    with pytest.raises(FileNotFoundError):
        check_decorators_in_folder(str(tmp_path / "doesnotexist"))
