"""Tests for pysealer initialization behavior."""

import os
import subprocess
import tempfile
import pytest

def test_pysealer_init_creates_env_file():
    """Test that 'pysealer init' creates a new .env file containing valid PRIVATE_KEY and PUBLIC_KEY entries."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = os.path.join(tmpdir, ".env")
        result = subprocess.run([
            "pysealer", "init", env_path
        ], capture_output=True, text=True)
        assert result.returncode == 0, f"pysealer init failed: {result.stderr}"
        assert os.path.exists(env_path), ".env file was not created"
        with open(env_path) as f:
            content = f.read()
        assert "PRIVATE_KEY" in content and "PUBLIC_KEY" in content, "Keys not found in .env file"


def test_pysealer_init_does_not_overwrite_existing_env():
    """Test that re-running 'pysealer init' does not overwrite an existing .env file without explicit confirmation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = os.path.join(tmpdir, ".env")
        # First init
        subprocess.run(["pysealer", "init", env_path], capture_output=True, text=True)
        with open(env_path) as f:
            original_content = f.read()
        # Second init (simulate no confirmation)
        result = subprocess.run(["pysealer", "init", env_path], capture_output=True, text=True)
        with open(env_path) as f:
            new_content = f.read()
        assert original_content == new_content, ".env file was overwritten without confirmation"
    assert ("Keys already exist" in result.stderr or "Cannot overwrite" in result.stderr), "No warning about existing .env file"
