import os
import tempfile
import pytest
import pysealer.git_diff as gd

import pysealer

def test_extract_function_from_source():
    code = """
def foo():
    x = 1
    return x
class Bar:
    def method(self):
        pass
"""
    func, start = gd.extract_function_from_source(code, "foo")
    assert "def foo()" in func
    assert start == 2
    cls, start = gd.extract_function_from_source(code, "Bar")
    assert "class Bar" in cls
    assert start == 5
    assert gd.extract_function_from_source(code, "notfound") is None

def test_generate_function_diff():
    old = "def f():\n    return 1\n"
    new = "def f():\n    return 2\n"
    diff = gd.generate_function_diff(old, new, "f", 1, 1)
    assert any(t[0] == '-' for t in diff)
    assert any(t[0] == '+' for t in diff)

def test_get_candidate_git_refs_env(monkeypatch):
    monkeypatch.setenv("PYSEALER_GIT_REF", "myref")
    refs = gd.get_candidate_git_refs()
    assert "myref" in refs

def test_is_git_available(tmp_path):
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        assert not gd.is_git_available()
        (tmp_path / ".git").mkdir()
        assert gd.is_git_available()
    finally:
        os.chdir(cwd)

def test_get_file_from_git_handles_errors(tmp_path):
    # Should return None if not in a git repo
    file = tmp_path / "f.py"
    file.write_text("def f(): pass\n")
    assert gd.get_file_from_git(str(file)) is None

def test_get_function_diff_handles_missing(tmp_path):
    # Should return None if no git history
    file = tmp_path / "f.py"
    file.write_text("def f(): pass\n")
    assert gd.get_function_diff(str(file), "f", "def f(): pass\n", 1) is None
