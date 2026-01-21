"""Tests for the 'pysealer check' CLI command."""

import os
import subprocess
import tempfile
import pytest

SAMPLE_CODE = """
def foo():
    return 42

class Bar:
    def baz(self):
        return 'baz'
"""

def test_check_valid_decorated_file():
    """Test that 'pysealer check' passes for a properly decorated file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "sample.py")
        with open(file_path, "w") as f:
            f.write(SAMPLE_CODE)
        subprocess.run(["pysealer", "decorate", file_path], capture_output=True, text=True)
        result = subprocess.run(["pysealer", "check", file_path], capture_output=True, text=True)
        assert result.returncode == 0, f"pysealer check failed: {result.stderr}"
        # Accept the actual output string
        assert ("all decorators are valid" in result.stdout.lower() or
            "all decorators are valid" in result.stderr.lower()), "Check did not verify file"

def test_check_fails_on_tampered_file():
    """Test that 'pysealer check' fails if the decorated file is tampered with."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "sample.py")
        with open(file_path, "w") as f:
            f.write(SAMPLE_CODE)
        subprocess.run(["pysealer", "decorate", file_path], capture_output=True, text=True)
            # Tamper with the function body (change a line inside the function)
        with open(file_path, "r") as f:
            lines = f.readlines()
        # Find the first non-def line and modify it
        for i, line in enumerate(lines):
            if line.strip().startswith("def "):
                # Next line should be inside the function
                if i + 1 < len(lines):
                    lines[i + 1] = "    x = 123  # tampered\n"
                break
        with open(file_path, "w") as f:
            f.writelines(lines)
        result = subprocess.run(["pysealer", "check", file_path], capture_output=True, text=True)
        # Accept either a non-zero return code or a warning in output
        tampered_detected = (result.returncode != 0 or
                            "invalid" in result.stdout.lower() or
                            "invalid" in result.stderr.lower() or
                            "tampered" in result.stdout.lower() or
                            "tampered" in result.stderr.lower())
        assert tampered_detected, f"pysealer check should fail or warn on tampered file, got: {result.stdout} {result.stderr}"
        assert ("failed" in result.stdout.lower() or "failed" in result.stderr.lower() or
                "invalid" in result.stdout.lower() or "invalid" in result.stderr.lower()), "Check did not report failure"

def test_check_on_undecorated_file():
    """Test that 'pysealer check' handles undecorated files gracefully (should not crash)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "plain.py")
        with open(file_path, "w") as f:
            f.write(SAMPLE_CODE)
        result = subprocess.run(["pysealer", "check", file_path], capture_output=True, text=True)
        # Accept either a warning or a pass, but should not crash
        assert result.returncode == 0 or result.returncode == 1, "pysealer check crashed on undecorated file"
        undecorated_detected = (
            "undecorated" in result.stdout.lower() or "undecorated" in result.stderr.lower() or
            "no decorators" in result.stdout.lower() or "no decorators" in result.stderr.lower() or
            "not protected" in result.stdout.lower() or "not protected" in result.stderr.lower() or
            "no pysealer decorators found" in result.stdout.lower() or "no pysealer decorators found" in result.stderr.lower()
        )
        assert undecorated_detected, f"Check did not report undecorated file, got: {result.stdout} {result.stderr}"
