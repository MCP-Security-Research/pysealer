"""Defines dummy decorators for all decorators found in the target file."""

import os
import ast
import inspect


def _dummy_decorator(func=None, *args, **kwargs):
    """
    A no-op (dummy) decorator that can be used in place of any decorator.

    Handles both @deco and @deco(...) usages. If used as @deco, it returns the function unchanged.
    If used as @deco(...), it returns a wrapper that returns the function unchanged.

    Args:
        func (callable, optional): The function to decorate, or None if called with arguments.
        *args: Positional arguments (ignored).
        **kwargs: Keyword arguments (ignored).

    Returns:
        callable: The original function, unchanged.
    """
    if callable(func) and not args and not kwargs:
        return func
    def wrapper(f):
        return f
    return wrapper

def _discover_decorators(file_path):
    """
    Yield all decorator names used in the given Python file.

    This function parses the specified Python file and walks its AST to find all decorator names
    used on functions, async functions, and classes. It handles decorators used as @deco, @deco(...),
    and @obj.deco or @obj.deco(...).

    Args:
        file_path (str): Path to the Python file to scan.

    Yields:
        str: The name of each decorator found.
    """
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
                elif isinstance(deco.func, ast.Name):
                    yield deco.func.id
                elif isinstance(deco.func, ast.Attribute):
                    yield deco.func.attr

def _get_caller_file():
    """
    Find the filename of the module that imported this module at the top level.

    Returns:
        str or None: The filename of the caller module, or None if not found.
    """
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
