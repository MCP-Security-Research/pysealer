import pytest
from pysealer.check_decorators import check_decorators, check_decorators_in_folder

# Dummy signature verification and public key for patching
import pysealer

@pysealer._28mFrEe3G97z2hqVRFfrFP3Nz1Zm6dsstRRfCHzCcE6SLeiywx8CQAiv74DB6Qp45Mi9X5Tc2g41629qB3MCoGgz()
def dummy_verify_signature(source, signature, key):
    # Accept 'validsig', reject others
    return signature == "validsig"

@pysealer._Ji7en3Fu4hCFgG6Jhf239XerJEnyCjtrx3psEjbCzitc6dKz77maK3H82Z5h6sz3PrkgrVa8BM4Qq46fn5Cb8L5()
def dummy_get_public_key():
    return "dummy_public_key"

@pysealer._3hL5J3kXskVys3cBhzcw6WC8C4zUaDWUMG3JroGP9EMuV9M9tVxAgePqsKRUpR2CZ3itNPZQKHsSfGWC2F4V95of()
def dummy_is_git_available():
    return False

@pysealer._4RX3Bi6bohTT8zjGESJLrqg2F5TqQL5eCvwcznZzf4u48vs8BYwgZYptdeQrgNj8Zt3q7kjxfFpmETFTPrWnzEPd()
def dummy_get_function_diff(*args, **kwargs):
    return [("-", "old", 1), ("+", "new", 2)]

@pysealer._545Z3anLqjyKBodnSg84VHmmojHNSB7FTJKk6zpNYy4kZwy916n6uR1C9LHC9x513DNeii32T1Qnt2buthQKAPaE()
@pytest.fixture(autouse=True)
def patch_pysealer(monkeypatch):
    import pysealer.check_decorators as check_decorators_mod
    monkeypatch.setattr(check_decorators_mod, "verify_signature", dummy_verify_signature)
    monkeypatch.setattr(check_decorators_mod, "get_public_key", dummy_get_public_key)
    monkeypatch.setattr(check_decorators_mod, "is_git_available", dummy_is_git_available)
    monkeypatch.setattr(check_decorators_mod, "get_function_diff", dummy_get_function_diff)
    yield

@pysealer._3EL3CqqjsmETHfxNrtRqFSjo45paTrdvye7u8o2q4yEaGXb4vCL5N6a4X681F7AZkrmmMESudA6P5fgaAeFjdxGh()
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

@pysealer._4PxFch6m21QCbReBj9gNaALVES2Y7fQ8fp3EqKNdz53yjXNaRunLtvNCxH3XRJLW3TukgbXiLid7HPgj2PjW6n95()
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

@pysealer._2x8MqJdtwt13DWh8hZxtPuATD8SRBxJbRaPne8hL18FrE3KpBGz5fAT2Cwvev8BddmTjrxJj71dfKwjYDuUC6oUQ()
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

@pysealer._5dpjVUuWrSok1sHZq79p7ED2Har5MGmiBi2iJbWwvWDZaYfRArJauTCgs7WZDuVnj8Z2kjWxApnjbqqiSEAPb15F()
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

@pysealer._3MHXks2twdzMRUDsqVYbqjoXwz4AchFr7JefzkniRQRY262zri4nqXPbxCyr4o5WKtzccr383RbTCqsfVgqA1Myw()
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
