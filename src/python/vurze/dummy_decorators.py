
"""
This module defines dummy decorators for all decorators found in the target file.
It scans the caller file for all decorator usages and creates no-op decorators for them.
This allows code modified by vurze to run even if the decorators are not implemented.
"""

import os
import ast
import inspect


def _dummy_decorator(func=None, *args, **kwargs):
    # Handles both @deco and @deco(...)
    if callable(func) and not args and not kwargs:
        return func
    def wrapper(f):
        return f
    return wrapper

def _discover_decorators(file_path):
    """Yield all decorator names used in the given Python file."""
    if not os.path.exists(file_path):
        return
    with open(file_path, "r") as f:
        src = f.read()
    try:
        tree = ast.parse(src)
    except Exception:
        return
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for deco in node.decorator_list:
                # Handles @deco or @deco(...)
                if isinstance(deco, ast.Name):
                    yield deco.id
                elif isinstance(deco, ast.Attribute):
                    yield deco.attr
                elif isinstance(deco, ast.Call):
                    if isinstance(deco.func, ast.Name):
                        yield deco.func.id
                    elif isinstance(deco.func, ast.Attribute):
                        yield deco.func.attr

def _get_caller_file():
    stack = inspect.stack()
    for frame in stack:
        if frame.function == "<module>" and frame.filename != __file__:
            return frame.filename

# Main logic: define dummy decorators for all found in the caller file
_CALLER_FILE = _get_caller_file()
if _CALLER_FILE:
    _seen = set()
    for deco_name in _discover_decorators(_CALLER_FILE):
        if deco_name and deco_name not in globals() and deco_name not in _seen:
            globals()[deco_name] = _dummy_decorator
            _seen.add(deco_name)
