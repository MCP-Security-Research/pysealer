"""Remove cryptographic pysealer decorators from all functions and classes in a Python file."""

import ast
from typing import List, Tuple, Dict
from pathlib import Path

def remove_decorators(file_path: str) -> Tuple[str, bool]:
    """
    Parse a Python file, remove all @pysealer.* decorators from functions and classes, and return the modified code.

    Args:
        file_path: Path to the Python file to process
    Returns:
        Modified Python source code as a string
    """
    with open(file_path, 'r') as f:
        content = f.read()

    tree = ast.parse(content)
    lines = content.split('\n')
    lines_to_remove = set()

    for node in ast.walk(tree):
        if type(node).__name__ in ("FunctionDef", "AsyncFunctionDef", "ClassDef"):
            if hasattr(node, 'decorator_list'):
                for decorator in node.decorator_list:
                    is_pysealer_decorator = False
                    if isinstance(decorator, ast.Name):
                        if decorator.id.startswith("pysealer"):
                            is_pysealer_decorator = True
                    elif isinstance(decorator, ast.Attribute):
                        if isinstance(decorator.value, ast.Name) and decorator.value.id == "pysealer":
                            is_pysealer_decorator = True
                    elif isinstance(decorator, ast.Call):
                        func = decorator.func
                        if isinstance(func, ast.Attribute):
                            if isinstance(func.value, ast.Name) and func.value.id == "pysealer":
                                is_pysealer_decorator = True
                        elif isinstance(func, ast.Name) and func.id.startswith("pysealer"):
                            is_pysealer_decorator = True
                    if is_pysealer_decorator:
                        lines_to_remove.add(decorator.lineno - 1)

    found = len(lines_to_remove) > 0
    for line_idx in sorted(lines_to_remove, reverse=True):
        del lines[line_idx]

    modified_code = '\n'.join(lines)
    return modified_code, found


def remove_decorators_from_folder(folder_path: str) -> List[str]:
    """
    Remove pysealer decorators from all Python files in a folder (recursively).

    Args:
        folder_path: Path to the folder to process
    Returns:
        List of file paths where decorators were removed
    """
    folder = Path(folder_path)
    
    if not folder.is_dir():
        raise NotADirectoryError(f"'{folder_path}' is not a directory")
    
    # Find all Python files recursively
    python_files = list(folder.rglob("*.py"))
    
    if not python_files:
        raise FileNotFoundError(f"No Python files found in '{folder_path}'")
    
    files_modified = []
    
    for py_file in python_files:
        try:
            file_path = str(py_file.resolve())
            modified_code, found = remove_decorators(file_path)
            
            if found:
                # Write the modified code back to the file
                with open(file_path, 'w') as f:
                    f.write(modified_code)
                files_modified.append(file_path)
        except Exception as e:
            # Skip files that can't be processed
            continue
    
    return files_modified
