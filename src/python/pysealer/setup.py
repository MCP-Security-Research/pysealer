"""Setup the storage of the pysealer keypair in a .env file."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv, set_key
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
    """
    # Determine .env location
    if env_path is None:
        env_path = Path.cwd() / '.env'
    else:
        env_path = Path(env_path)
    
    # Check if keys already exist
    if env_path.exists():
        load_dotenv(env_path)
        existing_private = os.getenv("PYSEALER_PRIVATE_KEY")
        existing_public = os.getenv("PYSEALER_PUBLIC_KEY")
        
        if existing_private or existing_public:
            raise ValueError(f"Keys already exist in {env_path} Cannot overwrite existing keys.")
    
    # Create .env if it doesn't exist
    env_path.touch(exist_ok=True)

    # Generate keypair using the Rust function
    private_key_hex, public_key_hex = generate_keypair()
    
    # Store keys in .env file
    set_key(str(env_path), "PYSEALER_PRIVATE_KEY", private_key_hex)
    set_key(str(env_path), "PYSEALER_PUBLIC_KEY", public_key_hex)
    
    return private_key_hex, public_key_hex


def get_public_key(env_path: Optional[str | Path] = None) -> str:
    """
    Retrieve the public key from the .env file.
    
    Args:
        env_path: Optional path to .env file. If None, searches from current directory upward.
    
    Returns:
        str: The public key hex string, or None if not found.
    """
    # Determine .env location
    if env_path is None:
        env_path = _find_env_file()
    else:
        env_path = Path(env_path)
    
    # Check if .env exists
    if not env_path.exists():
        raise FileNotFoundError(f"No .env file found at {env_path}. Run setup_keypair() first.")
    
    # Load environment variables from .env
    load_dotenv(env_path)
    
    # Get public key
    public_key = os.getenv("PYSEALER_PUBLIC_KEY")
    
    if public_key is None:
        raise ValueError(f"PYSEALER_PUBLIC_KEY not found in {env_path}. Run setup_keypair() first.")
    
    return public_key


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
    
    # Load environment variables from .env
    load_dotenv(env_path)
    
    # Get private key
    private_key = os.getenv("PYSEALER_PRIVATE_KEY")
    
    if private_key is None:
        raise ValueError(f"PYSEALER_PRIVATE_KEY not found in {env_path}. Run setup_keypair() first.")
    
    return private_key
