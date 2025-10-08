"""Vurze package entry point

This package serves as a bridge between the Python command line interface and the
underlying Rust implementation (compiled as _vurze module). It exposes the
core functionality for adding version control decorators to Python functions.
"""

from ._vurze import add_decorators_to_functions

__version__ = "0.1.0"
__all__ = ["add_decorators_to_functions"]
