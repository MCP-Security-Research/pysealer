"""Automatically add cryptographic decorators to all functions and classes in a python file."""

import ast
import copy
from vurze import generate_signature
from .setup import get_private_key

def add_decorators(file_path: str) -> str:
    """
    Parse a Python file, add decorators to all functions and classes, and return the modified code.
    
    Args:
        file_path: Path to the Python file to process
        
    Returns:
        Modified Python source code as a string
    """
    # Read the entire file content into a string
    with open(file_path, 'r') as f:
        content = f.read()

    # Split content into lines for manipulation
    lines = content.split('\n')

    # Dynamically add 'import vurze' grouped with other imports if not present
    has_import_vurze = any(
        line.strip() == 'import vurze' or line.strip().startswith('import vurze') or line.strip().startswith('from vurze')
        for line in lines
    )
    if not has_import_vurze:
        # Find the import block
        import_indices = [i for i, line in enumerate(lines) if line.strip().startswith('import ') or line.strip().startswith('from ')]
        if import_indices:
            # Insert after the last import in the block
            last_import = import_indices[-1]
            lines.insert(last_import + 1, 'import vurze')
        else:
            # No import block found, insert after shebang/docstring/comments as before
            insert_at = 0
            if lines and lines[0].startswith('#!'):
                insert_at = 1
            while insert_at < len(lines) and (lines[insert_at].strip() == '' or lines[insert_at].strip().startswith('"""') or lines[insert_at].strip().startswith("''")):
                if lines[insert_at].strip().startswith('"""') or lines[insert_at].strip().startswith("''"):
                    quote = lines[insert_at].strip()[:3]
                    insert_at += 1
                    while insert_at < len(lines) and not lines[insert_at].strip().endswith(quote):
                        insert_at += 1
                    if insert_at < len(lines):
                        insert_at += 1
                else:
                    insert_at += 1
            lines.insert(insert_at, 'import vurze')

    # Parse the Python source code into an Abstract Syntax Tree (AST)
    content = '\n'.join(lines)
    tree = ast.parse(content)
    
    # First pass: Remove existing vurze decorators
    lines_to_remove = set()
    for node in ast.walk(tree):
        if type(node).__name__ in ("FunctionDef", "AsyncFunctionDef", "ClassDef"):
            if hasattr(node, 'decorator_list'):
                for decorator in node.decorator_list:
                    is_vurze_decorator = False
                    
                    if isinstance(decorator, ast.Name):
                        if decorator.id.startswith("vurze"):
                            is_vurze_decorator = True
                    elif isinstance(decorator, ast.Attribute):
                        if isinstance(decorator.value, ast.Name) and decorator.value.id == "vurze":
                            is_vurze_decorator = True
                    elif isinstance(decorator, ast.Call):
                        func = decorator.func
                        if isinstance(func, ast.Attribute):
                            if isinstance(func.value, ast.Name) and func.value.id == "vurze":
                                is_vurze_decorator = True
                        elif isinstance(func, ast.Name) and func.id.startswith("vurze"):
                            is_vurze_decorator = True
                    
                    if is_vurze_decorator:
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

        # Filter out vurze decorators
        if hasattr(node_clone, 'decorator_list'):
            filtered_decorators = []
            for decorator in node_clone.decorator_list:
                should_keep = True
                if isinstance(decorator, ast.Name):
                    if decorator.id.startswith("vurze"):
                        should_keep = False
                elif isinstance(decorator, ast.Attribute):
                    if isinstance(decorator.value, ast.Name) and decorator.value.id == "vurze":
                        should_keep = False
                elif isinstance(decorator, ast.Call):
                    func = decorator.func
                    if isinstance(func, ast.Attribute):
                        if isinstance(func.value, ast.Name) and func.value.id == "vurze":
                            should_keep = False
                    elif isinstance(func, ast.Name) and func.id.startswith("vurze"):
                        should_keep = False
                if should_keep:
                    filtered_decorators.append(decorator)
            node_clone.decorator_list = filtered_decorators

        module_wrapper = ast.Module(body=[node_clone], type_ignores=[])
        function_source = ast.unparse(module_wrapper)

        try:
            private_key = get_private_key()
        except (FileNotFoundError, ValueError) as e:
            raise RuntimeError(f"Cannot add decorators: {e}. Please run 'vurze init' first.")

        try:
            signature = generate_signature(function_source, private_key)
        except Exception as e:
            raise RuntimeError(f"Failed to generate signature: {e}")

        decorator_line = node.lineno - 1
        if hasattr(node, 'decorator_list') and node.decorator_list:
            decorator_line = node.decorator_list[0].lineno - 1

        decorators_to_add.append((decorator_line, node.col_offset, signature))

    # Sort in reverse order to add from bottom to top (preserves line numbers)
    decorators_to_add.sort(reverse=True)

    # Add decorators to the lines
    for line_idx, col_offset, signature in decorators_to_add:
        indent = ' ' * col_offset
        decorator_line = f"{indent}@vurze._{signature}()"
        lines.insert(line_idx, decorator_line)

    # Join lines back together
    modified_code = '\n'.join(lines)

    return modified_code
