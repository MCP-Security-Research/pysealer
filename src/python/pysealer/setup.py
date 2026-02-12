"""Setup the storage of the pysealer keypair in a .env file."""

import os
from pathlib import Path
from typing import Optional
from dotenv import set_key, dotenv_values
from pysealer import generate_keypair


def _find_env_file() -> Path:
    """
    Search for .env file starting from current directory and walking up to parent directories.
    Also checks PYSEALER_ENV_PATH environment variable.
    
    Returns:
        Path: Path to the .env file
        
    Raises:
        FileNotFoundError: If no .env file is found
    """
    # First check if PYSEALER_ENV_PATH environment variable is set
    env_path_var = os.getenv("PYSEALER_ENV_PATH")
    if env_path_var:
        env_path = Path(env_path_var)
        if env_path.exists():
            return env_path

    # Start from current working directory and search upward
    current = Path.cwd()

    # Check current directory and all parent directories up to root
    for parent in [current] + list(current.parents):
        env_file = parent / '.env'
        if env_file.exists():
            return env_file

    # If not found, return the default location (current directory)
    # This will be used in error messages
    return Path.cwd() / '.env'

def setup_keypair(env_path: Optional[str | Path] = None):
    """
    Generate and store keypair securely.
    
    Args:
        env_path: Optional path to .env file. If None, creates in current directory.
    
    Returns:
        tuple[str, str]: (public_key_hex, private_key_hex)
    """
    # Determine .env location
    if env_path is None:
        env_path = Path.cwd() / '.env'
    else:
        env_path = Path(env_path)

    # Check if keys already exist
    if env_path.exists():
        # Read directly from file to avoid stale values from process environment
        env_values = dotenv_values(str(env_path))
        existing_private = env_values.get("PYSEALER_PRIVATE_KEY")
        existing_public = env_values.get("PYSEALER_PUBLIC_KEY")

        if existing_private or existing_public:
            raise ValueError(f"Keys already exist in {env_path} Cannot overwrite existing keys.")

    # Create .env if it doesn't exist
    env_path.touch(exist_ok=True)

    # Generate keypair using the Rust function
    private_key_hex, public_key_hex = generate_keypair()

    # Store keys in .env file
    set_key(str(env_path), "PYSEALER_PRIVATE_KEY", private_key_hex)
    set_key(str(env_path), "PYSEALER_PUBLIC_KEY", public_key_hex)

    return public_key_hex, private_key_hex


def get_public_key(env_path: Optional[str | Path] = None, prefer_environment: bool = True) -> str:
    """
    Retrieve the public key from environment variables or .env file.
    
    Automatically checks environment variables first (for CI/CD compatibility),
    then falls back to .env file if not found.
    
    Args:
        env_path: Optional path to .env file. If None, searches from current directory upward.
        prefer_environment: If True, return PYSEALER_PUBLIC_KEY from environment when present.
            If False, always read from the specified .env file.
    
    Returns:
        str: The public key hex string
        
    Raises:
        FileNotFoundError: If .env file not found and PYSEALER_PUBLIC_KEY not in environment
        ValueError: If PYSEALER_PUBLIC_KEY not found in .env file
    """
    # Check if PYSEALER_PUBLIC_KEY is available in environment first (CI/CD scenario)
    if prefer_environment:
        public_key_from_env = os.getenv("PYSEALER_PUBLIC_KEY")

        # If we have the key in environment, use it (works in CI without .env file)
        if public_key_from_env:
            return public_key_from_env.strip().strip("\"'")

    # Otherwise, look for .env file
    # Determine .env location
    if env_path is None:
        env_path = _find_env_file()
    else:
        env_path = Path(env_path)

    # Check if .env exists
    if not env_path.exists():
        raise FileNotFoundError(f"No .env file found at {env_path} and PYSEALER_PUBLIC_KEY not in environment. "
                               "Run 'pysealer init' first or set PYSEALER_PUBLIC_KEY environment variable.")

    # Read directly from .env to avoid mutating global process env
    env_values = dotenv_values(str(env_path))
    public_key = env_values.get("PYSEALER_PUBLIC_KEY")

    if not public_key:
        raise ValueError(f"PYSEALER_PUBLIC_KEY not found in {env_path}. Run 'pysealer init' first.")

    return str(public_key).strip().strip("\"'")


def get_private_key(env_path: Optional[str | Path] = None) -> str:
    """
    Retrieve the private key from the .env file.
    
    Args:
        env_path: Optional path to .env file. If None, searches from current directory upward.
    
    Returns:
        str: The private key hex string, or None if not found.
    """
    # Determine .env location
    if env_path is None:
        env_path = _find_env_file()
    else:
        env_path = Path(env_path)

    # Check if .env exists
    if not env_path.exists():
        raise FileNotFoundError(f"No .env file found at {env_path}. Run setup_keypair() first.")

    # Read directly from .env to avoid stale process environment values
    env_values = dotenv_values(str(env_path))
    private_key = env_values.get("PYSEALER_PRIVATE_KEY")

    if not private_key:
        raise ValueError(f"PYSEALER_PRIVATE_KEY not found in {env_path}. Run setup_keypair() first.")

    return str(private_key).strip().strip("\"'")
