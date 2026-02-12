"""
GitHub secrets integration for pysealer.

This module provides functionality to automatically upload the pysealer public key
to GitHub repository secrets when `pysealer init` is run.
"""

import logging
import os
import re
from typing import Optional, Tuple

import git
from github import Github, GithubException

# Suppress verbose GitHub API logging
logging.getLogger("github").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)


_BASE58_PATTERN = re.compile(r"^[1-9A-HJ-NP-Za-km-z]+$")


def _validate_public_key(public_key: str) -> str:
    """Validate and normalize a pysealer public key before uploading as a secret."""
    if public_key is None:
        raise ValueError("Public key is missing.")

    key = str(public_key).strip().strip("\"'")

    if not key:
        raise ValueError("Public key is empty.")

    if "\n" in key or "\r" in key:
        raise ValueError("Public key must be a single-line value without newlines.")

    if key.startswith("_"):
        raise ValueError("Public key looks like a decorator token (starts with '_'), not a raw key.")

    upper_key = key.upper()
    if "BEGIN PUBLIC KEY" in upper_key or "END PUBLIC KEY" in upper_key:
        raise ValueError("Public key appears to be PEM-formatted. Use the raw PYSEALER_PUBLIC_KEY value.")

    if key.startswith("{") or key.endswith("}"):
        raise ValueError("Public key appears to be JSON. Use only the raw key value.")

    if not _BASE58_PATTERN.fullmatch(key):
        raise ValueError("Public key is not valid Base58 format.")

    # Ed25519 32-byte Base58 keys are typically 43-44 chars.
    if len(key) < 43 or len(key) > 44:
        raise ValueError(
            f"Public key length {len(key)} is unexpected for pysealer (expected 43-44 characters)."
        )

    return key


def get_repo_info() -> Tuple[str, str]:
    """
    Extract GitHub owner and repository name from git remote URL.
    
    Supports both SSH and HTTPS formats:
    - SSH: git@github.com:owner/repo.git
    - HTTPS: https://github.com/owner/repo.git
    
    Returns:
        Tuple[str, str]: (owner, repo_name)
        
    Raises:
        ValueError: If not in a git repository or remote URL is not from GitHub
        RuntimeError: If unable to parse the remote URL
    """
    try:
        # Get the git repository from current directory
        repo = git.Repo(search_parent_directories=True)
        
        # Try to get the origin remote
        if 'origin' not in repo.remotes:
            raise ValueError("No 'origin' remote found in git repository")
        
        remote_url = repo.remotes.origin.url
        
        # Parse SSH format: git@github.com:owner/repo.git
        ssh_pattern = r'git@github\.com:([^/]+)/(.+?)(?:\.git)?$'
        ssh_match = re.match(ssh_pattern, remote_url)
        if ssh_match:
            owner, repo_name = ssh_match.groups()
            return owner, repo_name
        
        # Parse HTTPS format: https://github.com/owner/repo.git
        https_pattern = r'https://github\.com/([^/]+)/(.+?)(?:\.git)?$'
        https_match = re.match(https_pattern, remote_url)
        if https_match:
            owner, repo_name = https_match.groups()
            return owner, repo_name
        
        raise RuntimeError(f"Could not parse GitHub repository from remote URL: {remote_url}")
        
    except git.InvalidGitRepositoryError:
        raise ValueError("Not in a git repository. Please run this command from within a git repository.")
    except git.GitCommandError as e:
        raise RuntimeError(f"Git error: {e}")


def add_secret_to_github(token: str, owner: str, repo_name: str, secret_name: str, secret_value: str) -> None:
    """
    Add or update a secret in GitHub repository.
    
    Args:
        token: GitHub personal access token (needs 'repo' scope)
        owner: GitHub repository owner (user or organization)
        repo_name: Repository name
        secret_name: Name of the secret to create/update
        secret_value: Value of the secret (will be encrypted before upload)
        
    Raises:
        GithubException: If GitHub API request fails
        Exception: For other errors during the process
    """
    try:
        # Initialize GitHub client
        g = Github(token)
        
        # First, verify token has access by getting user info
        try:
            user = g.get_user()
            user.login  # Force API call to validate token
        except GithubException as auth_error:
            if auth_error.status == 401:
                raise Exception("Authentication failed. Your GitHub token is invalid or expired.")
            raise
        
        # Get the repository
        repo = g.get_repo(f"{owner}/{repo_name}")
        
        # Create or update the secret (actions secrets are at repository level)
        repo.create_secret(secret_name, secret_value, secret_type="actions")
        
    except GithubException as e:
        if e.status == 401:
            raise Exception("Authentication failed. Please check your GitHub token is valid.")
        elif e.status == 403:
            raise Exception(f"Permission denied (HTTP {e.status}). Your token needs 'repo' scope to manage secrets. "
                          f"For organization repositories like '{owner}/{repo_name}', you may also need admin:org scope or "
                          f"the token must be authorized for the organization.")
        elif e.status == 404:
            raise Exception(f"Repository '{owner}/{repo_name}' not found or you don't have access (HTTP {e.status}). "
                          f"Verify the repository exists and your token has access to it.")
        else:
            error_msg = e.data.get('message', str(e)) if hasattr(e, 'data') else str(e)
            raise Exception(f"GitHub API error (HTTP {e.status}): {error_msg}")


def setup_github_secrets(public_key: str, github_token: Optional[str] = None) -> Tuple[bool, str]:
    """
    Main function to orchestrate GitHub secrets setup.
    
    This function:
    1. Gets GitHub token from parameter or environment variable
    2. Extracts repository info from git remote
    3. Uploads the public key to GitHub secrets
    
    Args:
        public_key: The pysealer public key to upload
        github_token: Optional GitHub token. If None, uses GITHUB_TOKEN env var
        
    Returns:
        Tuple[bool, str]: (success, message)
        - success: True if secret was uploaded successfully
        - message: Success or error message
    """
    # Validate key before any API call
    try:
        validated_public_key = _validate_public_key(public_key)
    except ValueError as e:
        return False, f"Invalid PYSEALER_PUBLIC_KEY: {e}"

    # Get GitHub token
    token = github_token or os.getenv("GITHUB_TOKEN")
    if not token:
        return False, "No GitHub token provided. Use --github-token or set GITHUB_TOKEN environment variable."
    
    try:
        # Get repository information
        owner, repo_name = get_repo_info()
        
        # Upload the secret
        add_secret_to_github(token, owner, repo_name, "PYSEALER_PUBLIC_KEY", validated_public_key)
        
        return True, f"Successfully added PYSEALER_PUBLIC_KEY to {owner}/{repo_name}"
        
    except ValueError as e:
        return False, f"Repository detection failed: {e}"
    except RuntimeError as e:
        return False, f"Git error: {e}"
    except Exception as e:
        return False, f"Failed to upload secret: {e}"
