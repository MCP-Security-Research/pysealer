"""Pyseal package entry point

This package serves as a bridge between the Python command line interface and the
underlying Rust implementation (compiled as _pyseal module). It exposes the
core functionality for adding version control decorators to Python functions.

This module also dynamically provides decorator placeholders (e.g. @pyseal._<sig>)
so that decorated functions remain importable.
"""

# Define the rust to python module version and functions
from ._pyseal import generate_keypair, generate_signature, verify_signature

__version__ = "0.1.3"
__all__ = ["generate_keypair", "generate_signature", "verify_signature"]

# Ensure dummy decorators are registered on import
from . import dummy_decorators

# Allow dynamic decorator resolution for @pyseal._<sig>()
def __getattr__(name):
	if name.startswith("_"):
		return dummy_decorators._dummy_decorator
	raise AttributeError(f"module 'pyseal' has no attribute '{name}'")
