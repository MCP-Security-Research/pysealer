from pathlib import Path

import pytest


def _remove_repo_pysealer_precommit_hook() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    hook_path = repo_root / ".git" / "hooks" / "pre-commit"

    if not hook_path.exists():
        return

    try:
        content = hook_path.read_text()
    except OSError:
        return

    if "Pysealer pre-commit hook" in content:
        try:
            hook_path.unlink()
        except OSError:
            pass


@pytest.fixture(autouse=True)
def cleanup_pysealer_precommit_hook():
    _remove_repo_pysealer_precommit_hook()
    yield
    _remove_repo_pysealer_precommit_hook()


def pytest_sessionfinish(session, exitstatus):
    _remove_repo_pysealer_precommit_hook()