"""Tests for the 'pysealer lock' CLI command."""

import os
import subprocess
import tempfile

SAMPLE_CODE = """
def foo():
    return 42

class Bar:
    def baz(self):
        return 'baz'
"""

EMPTY_CODE = """
# No functions or classes here
x = 123
"""

def test_decorate_injects_decorators():
    """Test that 'pysealer lock' injects decorators into all functions and classes in a file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "sample.py")
        with open(file_path, "w") as f:
            f.write(SAMPLE_CODE)
        # Initialize pysealer in the temp directory
        subprocess.run(["pysealer", "init"], cwd=tmpdir, capture_output=True, text=True, input="n\n")
        result = subprocess.run(["pysealer", "lock", file_path], capture_output=True, text=True)
        assert result.returncode == 0, f"pysealer lock failed: {result.stderr}"
        with open(file_path) as f:
            content = f.read()
        assert any(line.strip().startswith("@pysealer._") for line in content.splitlines()), "Decorator not injected into file"

def test_decorate_idempotency():
    """Test that running 'pysealer lock' twice does not duplicate decorators."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "sample.py")
        with open(file_path, "w") as f:
            f.write(SAMPLE_CODE)
        # Initialize pysealer in the temp directory
        subprocess.run(["pysealer", "init"], cwd=tmpdir, capture_output=True, text=True, input="n\n")
        subprocess.run(["pysealer", "lock", file_path], capture_output=True, text=True)
        # Run again
        result = subprocess.run(["pysealer", "lock", file_path], capture_output=True, text=True)
        assert result.returncode == 0, f"Second pysealer lock failed: {result.stderr}"
        with open(file_path) as f:
            content = f.read()
        # Should only have one decorator per function/class
        decorator_lines = [line for line in content.splitlines() if line.strip().startswith("@pysealer._")]
        assert len(decorator_lines) == 2, "Duplicate or missing decorators found"

def test_decorate_handles_empty_file():
    """Test that 'pysealer lock' handles files with no functions/classes gracefully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "empty.py")
        with open(file_path, "w") as f:
            f.write(EMPTY_CODE)
        # Initialize pysealer in the temp directory
        subprocess.run(["pysealer", "init"], cwd=tmpdir, capture_output=True, text=True, input="n\n")
        result = subprocess.run(["pysealer", "lock", file_path], capture_output=True, text=True)
        assert result.returncode == 0, f"pysealer lock failed on empty file: {result.stderr}"
        with open(file_path) as f:
            content = f.read()
        assert "@pysealer_decorator" not in content, "Decorator should not be injected into empty file"
