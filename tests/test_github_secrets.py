import pytest
import pysealer.github_secrets as gs

import pysealer

def test_validate_public_key_valid():
    # 44-char base58, valid length
    key = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmn1opq"[:44]  # 44 chars
    assert len(key) == 44
    assert gs._validate_public_key(key) == key

def test_validate_public_key_invalid():
    with pytest.raises(ValueError):
        gs._validate_public_key(None)
    with pytest.raises(ValueError):
        gs._validate_public_key("")
    with pytest.raises(ValueError):
        gs._validate_public_key("\nabc")
    with pytest.raises(ValueError):
        gs._validate_public_key("_abc")
    with pytest.raises(ValueError):
        gs._validate_public_key("-----BEGIN PUBLIC KEY-----")
    with pytest.raises(ValueError):
        gs._validate_public_key("{abc}")
    with pytest.raises(ValueError):
        gs._validate_public_key("notbase58!@#")
    with pytest.raises(ValueError):
        gs._validate_public_key("short")
    with pytest.raises(ValueError):
        gs._validate_public_key("1"*50)
    # Test lower and upper boundary for length
    with pytest.raises(ValueError):
        gs._validate_public_key("1"*42)
    with pytest.raises(ValueError):
        gs._validate_public_key("1"*45)

def test_add_secret_to_github_errors(monkeypatch):
    class DummyRepo:
        def create_secret(self, *a, **k):
            raise gs.GithubException(401, data={})
    class DummyGithub:
        def __init__(self, token): pass
        def get_user(self):
            class U: login = "x"
            return U()
        def get_repo(self, name): return DummyRepo()
    monkeypatch.setattr(gs, "Github", DummyGithub)
    # Auth error
    with pytest.raises(Exception) as e:
        gs.add_secret_to_github("tok", "owner", "repo", "NAME", "VAL")
    assert "Authentication failed" in str(e.value)
    # Permission error
    class DummyRepo2:
        def create_secret(self, *a, **k):
            raise gs.GithubException(403, data={})
    class DummyGithub2(DummyGithub):
        def get_repo(self, name): return DummyRepo2()
    monkeypatch.setattr(gs, "Github", DummyGithub2)
    with pytest.raises(Exception) as e:
        gs.add_secret_to_github("tok", "owner", "repo", "NAME", "VAL")
    assert "Permission denied" in str(e.value)
    # Not found error
    class DummyRepo3:
        def create_secret(self, *a, **k):
            raise gs.GithubException(404, data={})
    class DummyGithub3(DummyGithub):
        def get_repo(self, name): return DummyRepo3()
    monkeypatch.setattr(gs, "Github", DummyGithub3)
    with pytest.raises(Exception) as e:
        gs.add_secret_to_github("tok", "owner", "repo", "NAME", "VAL")
    assert "not found" in str(e.value)
    # Other error
    class DummyRepo4:
        def create_secret(self, *a, **k):
            raise gs.GithubException(500, data={"message": "fail"})
    class DummyGithub4(DummyGithub):
        def get_repo(self, name): return DummyRepo4()
    monkeypatch.setattr(gs, "Github", DummyGithub4)
    with pytest.raises(Exception) as e:
        gs.add_secret_to_github("tok", "owner", "repo", "NAME", "VAL")
    assert "GitHub API error" in str(e.value)

def test_get_repo_info(monkeypatch):
    class DummyRemote:
        url = "git@github.com:owner/repo.git"
    class DummyRemotes(dict):
        def __contains__(self, k): return True
        @property
        def origin(self): return DummyRemote()
    class DummyRepo:
        remotes = DummyRemotes()
    monkeypatch.setattr(gs.git, "Repo", lambda **kwargs: DummyRepo())
    owner, repo = gs.get_repo_info()
    assert owner == "owner"
    assert repo == "repo"

def test_get_repo_info_https(monkeypatch):
    class DummyRemote:
        url = "https://github.com/owner/repo.git"
    class DummyRemotes(dict):
        def __contains__(self, k): return True
        @property
        def origin(self): return DummyRemote()
    class DummyRepo:
        remotes = DummyRemotes()
    monkeypatch.setattr(gs.git, "Repo", lambda **kwargs: DummyRepo())
    owner, repo = gs.get_repo_info()
    assert owner == "owner"
    assert repo == "repo"

def test_get_repo_info_fail(monkeypatch):
    class DummyRepo:
        remotes = {}
    monkeypatch.setattr(gs.git, "Repo", lambda **kwargs: DummyRepo())
    with pytest.raises(ValueError):
        gs.get_repo_info()

def test_setup_github_secrets_success(monkeypatch):
    monkeypatch.setattr(gs, "_validate_public_key", lambda k: k)
    monkeypatch.setattr(gs, "get_repo_info", lambda: ("owner", "repo"))
    monkeypatch.setattr(gs, "add_secret_to_github", lambda *a, **kw: None)
    ok, msg = gs.setup_github_secrets("goodkey", github_token="tok")
    assert ok
    assert "Successfully added" in msg

def test_setup_github_secrets_failures(monkeypatch):
    monkeypatch.setattr(gs, "_validate_public_key", lambda k: (_ for _ in ()).throw(ValueError("bad")))
    ok, msg = gs.setup_github_secrets("badkey", github_token="tok")
    assert not ok
    assert "Invalid PYSEALER_PUBLIC_KEY" in msg
    monkeypatch.setattr(gs, "_validate_public_key", lambda k: k)
    ok, msg = gs.setup_github_secrets("goodkey", github_token=None)
    assert not ok
    assert "No GitHub token" in msg
    monkeypatch.setattr(gs, "get_repo_info", lambda: (_ for _ in ()).throw(ValueError("fail")))
    ok, msg = gs.setup_github_secrets("goodkey", github_token="tok")
    assert not ok
    assert "Repository detection failed" in msg
    monkeypatch.setattr(gs, "get_repo_info", lambda: ("owner", "repo"))
    monkeypatch.setattr(gs, "add_secret_to_github", lambda *a, **kw: (_ for _ in ()).throw(Exception("fail")))
    ok, msg = gs.setup_github_secrets("goodkey", github_token="tok")
    assert not ok
    assert "Failed to upload secret" in msg
