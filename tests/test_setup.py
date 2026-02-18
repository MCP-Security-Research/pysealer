import os
import tempfile
import pytest
from pathlib import Path
from pysealer.setup import setup_keypair, get_public_key, get_private_key, _find_env_file

import pysealer

def dummy_generate_keypair():
    return ("privkey", "pubkey")

def test_setup_keypair_creates_env(monkeypatch, tmp_path):
    monkeypatch.setattr("pysealer.setup.generate_keypair", dummy_generate_keypair)
    env_path = tmp_path / ".env"
    pub, priv = setup_keypair(env_path)
    assert pub == "pubkey"
    assert priv == "privkey"
    content = env_path.read_text()
    assert "PYSEALER_PRIVATE_KEY" in content
    assert "PYSEALER_PUBLIC_KEY" in content

def test_setup_keypair_existing_keys(monkeypatch, tmp_path):
    env_path = tmp_path / ".env"
    env_path.write_text("PYSEALER_PRIVATE_KEY=abc\nPYSEALER_PUBLIC_KEY=def\n")
    with pytest.raises(ValueError):
        setup_keypair(env_path)

def test_get_public_key_env(monkeypatch):
    monkeypatch.setenv("PYSEALER_PUBLIC_KEY", "envkey")
    assert get_public_key() == "envkey"

def test_get_public_key_env_file(tmp_path, monkeypatch):
    env_path = tmp_path / ".env"
    env_path.write_text("PYSEALER_PUBLIC_KEY=abc\n")
    monkeypatch.delenv("PYSEALER_PUBLIC_KEY", raising=False)
    assert get_public_key(env_path, prefer_environment=False) == "abc"

def test_get_public_key_missing(tmp_path, monkeypatch):
    env_path = tmp_path / ".env"
    env_path.write_text("")
    monkeypatch.delenv("PYSEALER_PUBLIC_KEY", raising=False)
    with pytest.raises(ValueError):
        get_public_key(env_path, prefer_environment=False)

def test_get_private_key(tmp_path):
    env_path = tmp_path / ".env"
    env_path.write_text("PYSEALER_PRIVATE_KEY=priv\n")
    assert get_private_key(env_path) == "priv"

def test_get_private_key_missing(tmp_path):
    env_path = tmp_path / ".env"
    env_path.write_text("")
    with pytest.raises(ValueError):
        get_private_key(env_path)

def test_find_env_file(tmp_path, monkeypatch):
    env_path = tmp_path / ".env"
    env_path.write_text("PYSEALER_PRIVATE_KEY=priv\n")
    monkeypatch.chdir(tmp_path)
    assert _find_env_file() == env_path
