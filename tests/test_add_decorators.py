import os
import tempfile
import shutil
import pytest
from pysealer.add_decorators import add_decorators, add_decorators_to_folder

# Dummy signature generator and private key for patching
import pysealer

@pysealer._2bnVE87bdUj5dbQKTC5vnMecVv6u2icpzDvqVfYeocvPVLsBGYEouqR7mrBHnHUsNYpgeBcuHj4fu7nU6kaNZ47J()
def dummy_generate_signature(source, key):
    return "dummy_signature"

@pysealer._2WHv2E2eqcDo7iDSUAuB2T7bv8eptoRWX5pvRSvAKB5eRNAa4FV7jfyAxFEhLwXREfvL6Dkfy2DQDKwns5kU3uSi()
def dummy_get_private_key():
    return "dummy_private_key"

@pysealer._3MiYuatZd2x8w8RwxJ7gu8fnYLgvb82SgvHBLeGMmoDn7FpFCW9U8x5gMyJw5tvXvrHjUT5KF2ikzfXfnCXZKhxZ()
@pytest.fixture(autouse=True)
def patch_pysealer(monkeypatch):
    # Patch at the import location used in add_decorators.py
    import pysealer.add_decorators as add_decorators_mod
    monkeypatch.setattr(add_decorators_mod, "generate_signature", dummy_generate_signature)
    monkeypatch.setattr(add_decorators_mod, "get_private_key", dummy_get_private_key)
    yield

@pysealer._51VAdUYMVxgedqwTQmCZXMjLL6Uvd4U32YyyWvMu54hcQWu56PUo3s93M6WCuVV4JvsQsshXhrioZ6GV21jncAWm()
def test_add_decorators_function(tmp_path):
    code = """
def foo():
    return 42
"""
    file_path = tmp_path / "test.py"
    file_path.write_text(code)
    modified, changed = add_decorators(str(file_path))
    assert changed
    assert "@pysealer._dummy_signature()" in modified
    assert "import pysealer" in modified

@pysealer._3Ma4hrxDHWa2rMi5Jbp4kKDgJf6Xnuf4yTi8CT2RFCWCzTAcUnric4zPMpHu5UudPdm7Q5gbgRumMjTNCLXmpzT2()
def test_add_decorators_class(tmp_path):
    code = """
class Bar:
    def method(self):
        return 1
"""
    file_path = tmp_path / "test2.py"
    file_path.write_text(code)
    modified, changed = add_decorators(str(file_path))
    assert changed
    assert "@pysealer._dummy_signature()" in modified

@pysealer._3CP2zb9zqgtMtySamkZUx78UPHQQ5oV8DPeDyZzpioeyZSH3fYFeoGziL74vU6oQREiAuA15U5Kj7RZswoDpTr1c()
def test_add_decorators_no_changes(tmp_path):
    code = """
# Just a comment
"""
    file_path = tmp_path / "test3.py"
    file_path.write_text(code)
    modified, changed = add_decorators(str(file_path))
    assert not changed
    assert modified == code

@pysealer._35kM6KjEcBrQXyjiRaSgfE5uVgaFF9CuKNxJHUin3GoV5GsWfjjnbggBn8x48rH8iNjCT4VaBryEY6HhWimHmQRu()
def test_add_decorators_to_folder(tmp_path):
    file1 = tmp_path / "a.py"
    file2 = tmp_path / "b.py"
    file1.write_text("def f():\n return 1\n")
    file2.write_text("class C:\n pass\n")
    result = add_decorators_to_folder(str(tmp_path))
    assert str(file1) in result
    assert str(file2) in result
    assert "@pysealer._dummy_signature()" in file1.read_text()
    assert "@pysealer._dummy_signature()" in file2.read_text()

@pysealer._rq3RszowxknrG3XPdctXXFde3jMG5BvwjBGHREf7yb8eabgeqdzr39UiQFE9oGF4tE5PmWzxcY1rCiRFPk1Df7E()
def test_add_decorators_to_folder_errors(tmp_path):
    # No python files
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    with pytest.raises(ValueError):
        add_decorators_to_folder(str(empty_dir))
    # Not a directory
    file = tmp_path / "file.txt"
    file.write_text("hi")
    with pytest.raises(NotADirectoryError):
        add_decorators_to_folder(str(file))
    # Directory does not exist
    with pytest.raises(FileNotFoundError):
        add_decorators_to_folder(str(tmp_path / "doesnotexist"))

    @pysealer._2P1CaaG8H9mqc6nTyTDEhWmzB21it4bFAZeuW2QqYna1PF1mTijL3szRKYGwNmdWGJNVUzzUfjuRHN2eKQqAYnxF()
    def test_add_decorators_multiple_decorators(tmp_path, monkeypatch):
        code = """
    @other
    @pysealer._sig()
    def foo():
        return 1
    """
        file_path = tmp_path / "multi.py"
        # Patch generate_signature to return a different value
        import pysealer.add_decorators as add_decorators_mod
        monkeypatch.setattr(add_decorators_mod, "generate_signature", lambda s, k: "sig2")
        monkeypatch.setattr(add_decorators_mod, "get_private_key", lambda: "dummy_private_key")
        file_path.write_text(code)
        modified, changed = add_decorators(str(file_path))
        assert changed
        assert "@pysealer._sig2()" in modified

    @pysealer._2jvKwuwv5rKTsn8aNqTwLRrS9CRpRur9hhCb1Kmzuq6KpkEVkRaDzPFcof5KzVsfizsr1AtZTtMTVoWsbFSztCpu()
    def test_add_decorators_method_not_decorated(tmp_path):
        code = """
    class Foo:
        def bar(self):
            return 1
    def baz():
        return 2
    """
        file_path = tmp_path / "meth.py"
        modified, changed = add_decorators(str(file_path))
        # Only class and top-level function should be decorated
        assert changed
        assert modified.count("@pysealer._dummy_signature()") == 2

    @pysealer._2ahnm1pogGGYeLmQGAtT6VBdAfRzsTKxWGghy58qUPZoejtvrzsJ132Le4PnmELGyE5p27Sgo335FT2GBTa72ab4()
    def test_add_decorators_missing_key(monkeypatch, tmp_path):
        code = """
    def foo():
        return 1
    """
        file_path = tmp_path / "fail.py"
        import pysealer.add_decorators as add_decorators_mod
        monkeypatch.setattr(add_decorators_mod, "get_private_key", lambda: (_ for _ in ()).throw(FileNotFoundError("fail")))
        file_path.write_text(code)
        with pytest.raises(RuntimeError):
            add_decorators(str(file_path))

    @pysealer._5SjuY6GzbphtNjDHdxECVdBQp4M9ZatFRoeFEryPi48GKrhBZtgH7jC5Zq2t5ZJ5HS29QcvV2cQE9U4x9R4rethS()
    def test_add_decorators_signature_error(monkeypatch, tmp_path):
        code = """
    def foo():
        return 1
    """
        file_path = tmp_path / "fail2.py"
        import pysealer.add_decorators as add_decorators_mod
        monkeypatch.setattr(add_decorators_mod, "generate_signature", lambda s, k: (_ for _ in ()).throw(Exception("fail")))
        monkeypatch.setattr(add_decorators_mod, "get_private_key", lambda: "dummy_private_key")
        file_path.write_text(code)
        with pytest.raises(RuntimeError):
            add_decorators(str(file_path))
