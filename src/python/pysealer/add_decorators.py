"""Automatically add cryptographic decorators to all functions and classes in a python file."""

import ast
import copy
from pathlib import Path
from pysealer import generate_signature
from .setup import get_private_key

def add_decorators(file_path: str) -> tuple[str, bool]:
    """
    Parse a Python file, add decorators to all functions and classes, and return the modified code.
    
    Args:
        file_path: Path to the Python file to process
        
    Returns:
        Tuple of (modified Python source code as a string, whether any decorators were added)
    """
    # Read the entire file content into a string
    with open(file_path, 'r') as f:
        content = f.read()

    # Split content into lines for manipulation
    lines = content.split('\n')

    # Parse the Python source code into an Abstract Syntax Tree (AST)
    tree = ast.parse(content)
    
    # First pass: Remove existing pysealer decorators
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
                        # Mark this line for removal (convert to 0-indexed)
                        lines_to_remove.add(decorator.lineno - 1)
    
    # Remove the marked lines (in reverse order to preserve indices)
    for line_idx in sorted(lines_to_remove, reverse=True):
        del lines[line_idx]
    
    # Re-parse the content after removing decorators to get updated line numbers
    modified_content = '\n'.join(lines)
    tree = ast.parse(modified_content)
    
    # Build parent map for all nodes
    parent_map = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parent_map[child] = parent

    decorators_to_add = []

    for node in ast.walk(tree):
        node_type = type(node).__name__

        # Only decorate:
        # - Top-level functions (not inside a class)
        # - Top-level classes
        if node_type in ("FunctionDef", "AsyncFunctionDef"):
            parent = parent_map.get(node)
            if isinstance(parent, ast.ClassDef):
                continue  # skip methods inside classes
        elif node_type == "ClassDef":
            pass  # always decorate classes
        else:
            continue

        # Extract the complete source code of this function/class for hashing
        node_clone = copy.deepcopy(node)

        # Filter out pysealer decorators
        if hasattr(node_clone, 'decorator_list'):
            filtered_decorators = []
            for decorator in node_clone.decorator_list:
                should_keep = True
                if isinstance(decorator, ast.Name):
                    if decorator.id.startswith("pysealer"):
                        should_keep = False
                elif isinstance(decorator, ast.Attribute):
                    if isinstance(decorator.value, ast.Name) and decorator.value.id == "pysealer":
                        should_keep = False
                elif isinstance(decorator, ast.Call):
                    func = decorator.func
                    if isinstance(func, ast.Attribute):
                        if isinstance(func.value, ast.Name) and func.value.id == "pysealer":
                            should_keep = False
                    elif isinstance(func, ast.Name) and func.id.startswith("pysealer"):
                        should_keep = False
                if should_keep:
                    filtered_decorators.append(decorator)
            node_clone.decorator_list = filtered_decorators

        module_wrapper = ast.Module(body=[node_clone], type_ignores=[])
        function_source = ast.unparse(module_wrapper)

        try:
            private_key = get_private_key()
        except (FileNotFoundError, ValueError) as e:
            raise RuntimeError(f"Cannot add decorators: {e}. Please run 'pysealer init' first.")

        try:
            signature = generate_signature(function_source, private_key)
        except Exception as e:
            raise RuntimeError(f"Failed to generate signature: {e}")

        decorator_line = node.lineno - 1
        if hasattr(node, 'decorator_list') and node.decorator_list:
            decorator_line = node.decorator_list[0].lineno - 1

        decorators_to_add.append((decorator_line, node.col_offset, signature))

    # If no decorators to add, return original content
    if not decorators_to_add:
        return content, False
    
    # Sort in reverse order to add from bottom to top (preserves line numbers)
    decorators_to_add.sort(reverse=True)

    # Add decorators to the lines first
    for line_idx, col_offset, signature in decorators_to_add:
        indent = ' ' * col_offset
        decorator_line = f"{indent}@pysealer._{signature}()"
        lines.insert(line_idx, decorator_line)
    
    # Now add 'import pysealer' at the top if not present
    has_import_pysealer = any(
        line.strip() == 'import pysealer' or line.strip().startswith('import pysealer') or line.strip().startswith('from pysealer')
        for line in lines
    )
    if not has_import_pysealer:
        # Find the import block
        import_indices = [i for i, line in enumerate(lines) if line.strip().startswith('import ') or line.strip().startswith('from ')]
        if import_indices:
            # Insert after the last import in the block
            last_import = import_indices[-1]
            lines.insert(last_import + 1, 'import pysealer')
        else:
            # No import block found, insert after shebang/docstring/comments
            insert_at = 0
            if lines and lines[0].startswith('#!'):
                insert_at = 1
            # Skip module-level docstrings and blank lines
            while insert_at < len(lines):
                line = lines[insert_at].strip()
                if line == '':
                    insert_at += 1
                elif line.startswith('"""') or line.startswith("'''"):
                    # Handle multi-line docstrings
                    quote = '"""' if line.startswith('"""') else "'''"
                    # Check if docstring ends on same line
                    if line.count(quote) >= 2:
                        insert_at += 1
                    else:
                        # Multi-line docstring
                        insert_at += 1
                        while insert_at < len(lines) and quote not in lines[insert_at]:
                            insert_at += 1
                        if insert_at < len(lines):
                            insert_at += 1
                elif line.startswith('#'):
                    # Skip comments
                    insert_at += 1
                else:
                    # Found first non-blank, non-comment, non-docstring line
                    break
            
            lines.insert(insert_at, 'import pysealer')
            # Add blank line after import if the next line isn't blank
            if insert_at + 1 < len(lines) and lines[insert_at + 1].strip() != '':
                lines.insert(insert_at + 1, '')

    # Join lines back together
    modified_code = '\n'.join(lines)

    return modified_code, True


def add_decorators_to_folder(folder_path: str) -> list[str]:
    """
    Add decorators to all Python files in a folder.
    
    Args:
        folder_path: Path to the folder containing Python files
        
    Returns:
        List of file paths that were successfully decorated
    """
    folder = Path(folder_path)
    
    if not folder.exists():
        raise FileNotFoundError(f"Folder '{folder_path}' does not exist.")
    
    if not folder.is_dir():
        raise NotADirectoryError(f"'{folder_path}' is not a directory.")
    
    # Find all Python files in the folder (non-recursive)
    python_files = list(folder.glob('*.py'))
    
    if not python_files:
        raise ValueError(f"No Python files found in '{folder_path}'.")
    
    decorated_files = []
    errors = []
    
    for py_file in python_files:
        try:
            modified_code, has_changes = add_decorators(str(py_file))
            if has_changes:
                with open(py_file, 'w') as f:
                    f.write(modified_code)
                decorated_files.append(str(py_file))
        except Exception as e:
            errors.append((str(py_file), str(e)))
    
    if errors:
        error_msg = "\n".join([f"  - {file}: {error}" for file, error in errors])
        raise RuntimeError(f"Failed to decorate some files:\n{error_msg}")
    
    return decorated_files
