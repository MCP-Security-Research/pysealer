"""
vurze - Version control your Python functions

A tool that automatically adds cryptographic decorators to Python functions
to help detect potential security threats and code modifications.
"""

from ._vurze import add_decorators_to_functions

__version__ = "0.1.0"
__all__ = ["add_decorators_to_functions"]