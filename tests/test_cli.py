import pytest
import os

# Always clean up pre-commit hook before and after each test
@pytest.fixture(autouse=True)
def cleanup_precommit_hook():
    hook_path = os.path.join(".git", "hooks", "pre-commit")
    if os.path.exists(hook_path):
        os.remove(hook_path)
    yield
    if os.path.exists(hook_path):
        os.remove(hook_path)
import os
import tempfile
import shutil
import pytest
from typer.testing import CliRunner
from pysealer import cli
import pysealer

runner = CliRunner()

def test_version_callback():
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert "pysealer" in result.output

def test_init_success(monkeypatch, tmp_path):
    # Patch setup_keypair, generate_signature, verify_signature, is_git_repository, get_hook_status, install_hook
    monkeypatch.setattr(cli, "setup_keypair", lambda env: ("pub", "priv"))
    monkeypatch.setattr(cli, "generate_signature", lambda msg, key: "sig")
    monkeypatch.setattr(cli, "verify_signature", lambda msg, sig, pub: True)
    monkeypatch.setattr(cli, "is_git_repository", lambda: True)
    monkeypatch.setattr(cli, "get_hook_status", lambda: (False, None, None))
    monkeypatch.setattr(cli, "install_hook", lambda mode, target_pattern: (True, "hook installed"))
    result = runner.invoke(cli.app, ["init", str(tmp_path / ".env")])
    assert result.exit_code == 0
    assert "Successfully initialized pysealer" in result.output
    assert "Keypair generated" in result.output
    assert "hook installed" in result.output


def test_init_github_token(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "setup_keypair", lambda env: ("pub", "priv"))
    monkeypatch.setattr(cli, "generate_signature", lambda msg, key: "sig")
    monkeypatch.setattr(cli, "verify_signature", lambda msg, sig, pub: True)
    monkeypatch.setattr(cli, "is_git_repository", lambda: True)
    monkeypatch.setattr(cli, "get_hook_status", lambda: (False, None, None))
    monkeypatch.setattr(cli, "install_hook", lambda mode, target_pattern: (True, "hook installed"))
    class DummySecrets:
        @staticmethod
        def setup_github_secrets(pub, token):
            return True, "Successfully added"
    
def dummy_generate_keypair():
    # Return valid-length keys (private, public)
    priv = "privkey"
    pub = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmn1opq"  # 44 chars
    pub = pub[:44]  # Ensure exactly 44 chars
    return (priv, pub)
    monkeypatch.setitem(cli.__dict__, "github_secrets", DummySecrets)
    result = runner.invoke(cli.app, ["init", str(tmp_path / ".env"), "--github-token", "tok"])
    assert result.exit_code == 0
    assert "Successfully added" in result.output


def test_lock_file(monkeypatch, tmp_path):
    file = tmp_path / "f.py"
    file.write_text("def f():\n return 1\n")
    monkeypatch.setattr(cli, "add_decorators", lambda path: ("@pysealer._sig()\ndef f():\n return 1\n", True))
    result = runner.invoke(cli.app, ["lock", str(file)])
    assert result.exit_code == 0
    assert "Successfully added decorators" in result.output

def test_lock_folder(monkeypatch, tmp_path):
    d = tmp_path / "d"
    d.mkdir()
    (d / "a.py").write_text("def a():\n return 1\n")
    monkeypatch.setattr(cli, "add_decorators_to_folder", lambda path: [str(d / "a.py")])
    result = runner.invoke(cli.app, ["lock", str(d)])
    assert result.exit_code == 0
    assert "Successfully added decorators" in result.output

def test_check_file(monkeypatch, tmp_path):
    file = tmp_path / "f.py"
    file.write_text("@pysealer._sig()\ndef f():\n return 1\n")
    monkeypatch.setattr(cli, "check_decorators", lambda path: {"f": {"has_decorator": True, "valid": True}})
    result = runner.invoke(cli.app, ["check", str(file)])
    assert result.exit_code == 0
    assert "All decorator" in result.output or "All decorators" in result.output

def test_remove_file(monkeypatch, tmp_path):
    file = tmp_path / "f.py"
    file.write_text("@pysealer._sig()\ndef f():\n return 1\n")
    monkeypatch.setattr(cli, "remove_decorators", lambda path: ("def f():\n return 1\n", True))
    result = runner.invoke(cli.app, ["remove", str(file)])
    assert result.exit_code == 0
    assert "Successfully removed decorators" in result.output

def test_lock_file_not_found(tmp_path):
    result = runner.invoke(cli.app, ["lock", str(tmp_path / "nofile.py")])
    assert result.exit_code != 0
    assert "does not exist" in result.output

def test_lock_file_not_python(tmp_path):
    file = tmp_path / "f.txt"
    file.write_text("hi")
    result = runner.invoke(cli.app, ["lock", str(file)])
    assert result.exit_code != 0
    assert "not a Python file" in result.output

def test_check_file_not_found(tmp_path):
    result = runner.invoke(cli.app, ["check", str(tmp_path / "nofile.py")])
    assert result.exit_code != 0
    assert "does not exist" in result.output

def test_check_file_not_python(tmp_path):
    file = tmp_path / "f.txt"
    file.write_text("hi")
    result = runner.invoke(cli.app, ["check", str(file)])
    assert result.exit_code != 0
    assert "not a Python file" in result.output

def test_remove_file_not_found(tmp_path):
    result = runner.invoke(cli.app, ["remove", str(tmp_path / "nofile.py")])
    assert result.exit_code != 0
    assert "does not exist" in result.output

def test_remove_file_not_python(tmp_path):
    file = tmp_path / "f.txt"
    file.write_text("hi")
    result = runner.invoke(cli.app, ["remove", str(file)])
    assert result.exit_code != 0
    assert "not a Python file" in result.output

def test_init_keypair_error(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "setup_keypair", lambda env: (_ for _ in ()).throw(Exception("fail")))
    result = runner.invoke(cli.app, ["init", str(tmp_path / ".env")])
    assert result.exit_code != 0
    assert "Error during initialization" in result.output


def test_init_github_token_import_error(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "setup_keypair", lambda env: ("pub", "priv"))
    monkeypatch.setattr(cli, "generate_signature", lambda msg, key: "sig")
    monkeypatch.setattr(cli, "verify_signature", lambda msg, sig, pub: True)
    monkeypatch.setattr(cli, "is_git_repository", lambda: True)
    monkeypatch.setattr(cli, "get_hook_status", lambda: (False, None, None))
    monkeypatch.setattr(cli, "install_hook", lambda mode, target_pattern: (True, "hook installed"))
    import builtins
    real_import = builtins.__import__
    def fake_import(name, *a, **k):
        if name.endswith("github_secrets"):
            raise ImportError("fail")
        return real_import(name, *a, **k)
    monkeypatch.setattr(builtins, "__import__", fake_import)
    result = runner.invoke(cli.app, ["init", str(tmp_path / ".env"), "--github-token", "tok"])
    assert result.exit_code == 0
    assert "GitHub integration dependencies not installed" in result.output

