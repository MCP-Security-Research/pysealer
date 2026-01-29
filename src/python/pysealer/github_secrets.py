"""
GitHub secrets integration for pysealer.

This module provides functionality to automatically upload the pysealer public key
to GitHub repository secrets when `pysealer init` is run.
"""

import logging
import os
import re
from pathlib import Path
from typing import Optional, Tuple

import git
from github import Github, GithubException
from nacl import encoding, public

# Suppress verbose GitHub API logging
logging.getLogger("github").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)


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


def encrypt_secret(public_key: str, secret_value: str) -> str:
    """
    Encrypt a secret using GitHub's public key.
    
    GitHub requires secrets to be encrypted using the repository's public key
    before they can be uploaded via the API.
    
    Args:
        public_key: The repository's public key (base64 encoded)
        secret_value: The secret value to encrypt
        
    Returns:
        str: Base64 encoded encrypted secret
    """
    # Convert the public key from base64
    public_key_bytes = public_key.encode("utf-8")
    public_key_obj = public.PublicKey(public_key_bytes, encoding.Base64Encoder())
    
    # Encrypt the secret using sealed box
    sealed_box = public.SealedBox(public_key_obj)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    
    # Return base64 encoded encrypted secret
    return encoding.Base64Encoder().encode(encrypted).decode("utf-8")


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
        
        # Get the repository
        repo = g.get_repo(f"{owner}/{repo_name}")
        
        # Get the repository's public key for encrypting secrets
        public_key = repo.get_public_key()
        
        # Encrypt the secret
        encrypted_value = encrypt_secret(public_key.key, secret_value)
        
        # Create or update the secret (actions secrets are at repository level)
        repo.create_secret(secret_name, encrypted_value, secret_type="actions")
        
    except GithubException as e:
        if e.status == 401:
            raise Exception("Authentication failed. Please check your GitHub token.")
        elif e.status == 403:
            raise Exception("Permission denied. Your token needs 'repo' scope to manage secrets.")
        elif e.status == 404:
            raise Exception(f"Repository '{owner}/{repo_name}' not found or you don't have access.")
        else:
            raise Exception(f"GitHub API error: {e.data.get('message', str(e))}")


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
    # Get GitHub token
    token = github_token or os.getenv("GITHUB_TOKEN")
    if not token:
        return False, "No GitHub token provided. Use --github-token or set GITHUB_TOKEN environment variable."
    
    try:
        # Get repository information
        owner, repo_name = get_repo_info()
        
        # Upload the secret
        add_secret_to_github(token, owner, repo_name, "PYSEALER_PUBLIC_KEY", public_key)
        
        return True, f"Successfully added PYSEALER_PUBLIC_KEY to {owner}/{repo_name}"
        
    except ValueError as e:
        return False, f"Repository detection failed: {e}"
    except RuntimeError as e:
        return False, f"Git error: {e}"
    except Exception as e:
        return False, f"Failed to upload secret: {e}"
