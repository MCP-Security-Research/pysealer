import pytest
from pysealer.remove_decorators import remove_decorators, remove_decorators_from_folder

@pysealer._3vVSKo7ZtzmuEzLQw5vNC6ARUFPEUPKwXiuiXtURkqchQU8Fk6SwceCk4cEr42ifKfnUbctqSb5wSpYZfwRbj8Sn()
def test_remove_decorators_function(tmp_path):
    code = """
@pysealer._sig()
def foo():
    return 1
"""
    file_path = tmp_path / "test.py"
    file_path.write_text(code)
    modified, found = remove_decorators(str(file_path))
    assert found
    assert "@pysealer" not in modified
    assert "def foo()" in modified

@pysealer._4PvGMQtAWjDGGZ7qgcU8Uj3MszLDCUe7q4R9xA5GHjwC8Yb4LgchcHYh8uA9rgDA2vutovSGbjvJtiMmvg9h9FEd()
def test_remove_decorators_class(tmp_path):
    code = """
@pysealer._sig()
class Bar:
    pass
"""
    file_path = tmp_path / "test2.py"
    file_path.write_text(code)
    modified, found = remove_decorators(str(file_path))
    assert found
    assert "@pysealer" not in modified
    assert "class Bar" in modified

@pysealer._haWrqtoRvYMxmKDD74XbbGhbsEreX9y4jkms7c6YVYYwsE7cKV4mAcDZJjZFgqp4mwqphq4t4XguKy4kQu9KC2s()
def test_remove_decorators_no_decorator(tmp_path):
    code = """
def baz():
    return 2
"""
    file_path = tmp_path / "test3.py"
    file_path.write_text(code)
    modified, found = remove_decorators(str(file_path))
    assert not found
    assert modified == code

@pysealer._4McxbGqY7c47ofKjRZHnUqXQExBdK6JA5d1VZTMw37d78EJjjPLXk2oZ4bijbQrXPgLjhdG8CFqy5hLE2huutoLH()
def test_remove_decorators_from_folder(tmp_path):
    file1 = tmp_path / "a.py"
    file2 = tmp_path / "b.py"
    file1.write_text("@pysealer._sig()\ndef f():\n return 1\n")
    file2.write_text("def g():\n return 2\n")
    result = remove_decorators_from_folder(str(tmp_path))
    assert str(file1) in result
    assert str(file2) not in result
    assert "@pysealer" not in file1.read_text()
    assert "def g()" in file2.read_text()

@pysealer._3AcjHc76B6iJX7DHTLugy4qz24u9N9pRLF9iE4Wcg4z2afDUgpcLZVeVRtTtMXFfLCd7KSvGpXvWgbQ2amSH138A()
def test_remove_decorators_from_folder_errors(tmp_path):
    file = tmp_path / "file.txt"
    file.write_text("hi")
    with pytest.raises(NotADirectoryError):
        remove_decorators_from_folder(str(file))
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    with pytest.raises(FileNotFoundError):
        remove_decorators_from_folder(str(empty_dir))
