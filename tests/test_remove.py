"""Tests for the 'pysealer remove' CLI command."""

import os
import tempfile
import textwrap
from pysealer.remove_decorators import remove_decorators

SAMPLE_DECORATED_CODE = textwrap.dedent('''
@pysealer._abcdef123456()
def foo():
	return 42

@pysealer._deadbeef()
class Bar:
	pass
''')

SAMPLE_UNDECORATED_CODE = textwrap.dedent('''
def foo():
	return 42

class Bar:
	pass
''')

def test_remove_decorators_removes_all():
	"""Test that remove_decorators removes all pysealer decorators from functions and classes."""
	with tempfile.TemporaryDirectory() as tmpdir:
		file_path = os.path.join(tmpdir, "decorated.py")
		with open(file_path, "w") as f:
			f.write(SAMPLE_DECORATED_CODE)
		modified_code, found = remove_decorators(file_path)
		assert found, "Should find pysealer decorators to remove"
		assert "@pysealer" not in modified_code, "Decorators were not fully removed"
		# Should match undecorated code
		assert modified_code.strip() == SAMPLE_UNDECORATED_CODE.strip()

def test_remove_decorators_handles_no_decorators():
	"""Test that remove_decorators does nothing if no pysealer decorators are present."""
	with tempfile.TemporaryDirectory() as tmpdir:
		file_path = os.path.join(tmpdir, "plain.py")
		with open(file_path, "w") as f:
			f.write(SAMPLE_UNDECORATED_CODE)
		modified_code, found = remove_decorators(file_path)
		assert not found, "Should not find any pysealer decorators"
		assert modified_code.strip() == SAMPLE_UNDECORATED_CODE.strip(), "Code should remain unchanged"

def test_remove_decorators_mixed_decorators():
	"""Test that remove_decorators only removes pysealer decorators and leaves others."""
	mixed_code = textwrap.dedent('''
@other_decorator
@pysealer._abcdef123456()
def foo():
	return 42
''')
	expected_code = textwrap.dedent('''
@other_decorator
def foo():
	return 42
''')
	with tempfile.TemporaryDirectory() as tmpdir:
		file_path = os.path.join(tmpdir, "mixed.py")
		with open(file_path, "w") as f:
			f.write(mixed_code)
		modified_code, found = remove_decorators(file_path)
		assert found, "Should find pysealer decorator to remove"
		assert "@pysealer" not in modified_code, "Pysealer decorator was not removed"
		assert "@other_decorator" in modified_code, "Other decorator should remain"
		assert modified_code.strip() == expected_code.strip(), "Code should match expected output"
