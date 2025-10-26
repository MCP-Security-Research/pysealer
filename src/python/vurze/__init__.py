"""Vurze package entry point

This package serves as a bridge between the Python command line interface and the
underlying Rust implementation (compiled as _vurze module). It exposes the
core functionality for adding version control decorators to Python functions.
"""

from ._vurze import generate_keypair, generate_signature, verify_signature

# Define the rust to python module version and functions
__version__ = "0.1.0"
__all__ = ["generate_keypair", "generate_signature", "verify_signature"]


# Ensure dummy decorators are registered on import
from . import dummy_decorators

# Allow dynamic decorator resolution for @vurze._<sig>()
def __getattr__(name):
	# Only handle names that look like our decorator pattern
	if name.startswith("_"):
		return dummy_decorators._dummy_decorator
	raise AttributeError(f"module 'vurze' has no attribute '{name}'")
