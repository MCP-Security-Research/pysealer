import os
import tempfile
import shutil
import pytest
from pathlib import Path
import pysealer.git_pre_commit as gpc

import pysealer

def test_is_git_repository(tmp_path):
    assert not gpc.is_git_repository(tmp_path)
    (tmp_path / ".git").mkdir()
    assert gpc.is_git_repository(tmp_path)

def test_get_git_root(tmp_path, monkeypatch):
    # Not a git repo
    assert gpc.get_git_root(tmp_path) is None
    # Simulate git command
    def fake_run(*a, **kw):
        class R: stdout = str(tmp_path); returncode = 0
        return R()
    monkeypatch.setattr("subprocess.run", fake_run)
    assert Path(gpc.get_git_root(tmp_path)) == tmp_path

def test_create_hook_script():
    script = gpc.create_hook_script("mandatory", "src/*.py")
    assert "MANDATORY" in script
    assert "src/*.py" in script
    assert "pysealer" in script

def test_install_hook_and_uninstall(tmp_path):
    # Setup fake git repo
    git_dir = tmp_path / ".git"
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(parents=True)
    # Patch get_git_root
    def fake_get_git_root(_=None): return tmp_path
    gpc.get_git_root = fake_get_git_root
    # Install
    ok, msg = gpc.install_hook("mandatory", "*.py", tmp_path)
    assert ok
    assert "Pre-commit hook installed" in msg
    # Install again (should detect already installed)
    ok, msg = gpc.install_hook("mandatory", "*.py", tmp_path)
    assert not ok
    assert "already installed" in msg or "already exists" in msg
    # Uninstall
    ok, msg = gpc.uninstall_hook(tmp_path)
    assert ok
    assert "uninstalled" in msg
    # Uninstall again (should not find hook)
    ok, msg = gpc.uninstall_hook(tmp_path)
    assert not ok
    assert "No pre-commit hook found" in msg

def test_get_hook_status(tmp_path):
    git_dir = tmp_path / ".git"
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(parents=True)
    hook_path = hooks_dir / "pre-commit"
    hook_path.write_text("""#!/usr/bin/env python3\n"""
        """Pysealer pre-commit hook - MANDATORY mode\nTarget pattern: **/*.py\n""")
    def fake_get_git_root(_=None): return tmp_path
    gpc.get_git_root = fake_get_git_root
    is_installed, mode, pattern = gpc.get_hook_status(tmp_path)
    assert is_installed
    assert mode == "mandatory"
    assert pattern == "**/*.py"
    # Not our hook
    hook_path.write_text("not our hook")
    is_installed, mode, pattern = gpc.get_hook_status(tmp_path)
    assert not is_installed
