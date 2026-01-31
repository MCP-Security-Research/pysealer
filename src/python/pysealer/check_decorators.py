"""Automatically verify cryptographic decorators for all functions and classes in a python file."""

import ast
import copy
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from pysealer import verify_signature
from .setup import get_public_key
from .git_diff import get_function_diff, is_git_available


def check_decorators(file_path: str) -> Dict[str, dict]:
    """
    Parse a Python file and verify all pysealer cryptographic decorators.
    
    This function checks that each function/class with a pysealer decorator has a valid
    signature that matches the current source code of that function/class.
    
    Args:
        file_path: Path to the Python file to verify
        
    Returns:
        Dictionary mapping function/class names to their verification results:
        {
            "function_name": {
                "valid": bool,           # Whether signature is valid
                "signature": str,        # The signature found in decorator
                "message": str,          # Success or error message
                "has_decorator": bool,   # Whether function has pysealer decorator
                "line_start": int,       # Starting line number
                "line_end": int,         # Ending line number
                "source": str,           # Function source code
                "diff": List[Tuple]      # Git diff if validation failed
            }
        }
    """
    # Read the file content
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Parse the Python source code into an AST
    tree = ast.parse(content)
    
    # Get the public key for verification
    try:
        public_key = get_public_key()
    except (FileNotFoundError, ValueError) as e:
        raise RuntimeError(f"Cannot verify decorators: {e}. Please run 'pysealer init' first.")
    
    # Dictionary to store results
    results = {}
    
    # Iterate through each node in the AST
    for node in ast.walk(tree):
        node_type = type(node).__name__
        
        # Check if this node is a function or class definition
        if node_type in ("FunctionDef", "AsyncFunctionDef", "ClassDef"):
            name = node.name
            
            # Look for pysealer decorator
            signature_from_decorator = None
            has_pysealer_decorator = False
            
            if hasattr(node, 'decorator_list'):
                for decorator in node.decorator_list:
                    # Check if decorator is a Call node (e.g., @pysealer._<signature>())
                    if isinstance(decorator, ast.Call):
                        func = decorator.func
                        # Check if it's pysealer._<signature>
                        if isinstance(func, ast.Attribute):
                            if isinstance(func.value, ast.Name) and func.value.id == "pysealer":
                                attr_name = func.attr
                                # Extract signature (remove leading underscore)
                                if attr_name.startswith('_'):
                                    signature_from_decorator = attr_name[1:]
                                    has_pysealer_decorator = True
                                    break
            
            # Initialize result for this function/class
            result = {
                "has_decorator": has_pysealer_decorator,
                "valid": False,
                "signature": signature_from_decorator,
                "message": "",
                "line_start": node.lineno,
                "line_end": node.end_lineno if hasattr(node, 'end_lineno') and node.end_lineno else node.lineno,
                "source": "",
                "diff": None
            }
            
            if not has_pysealer_decorator:
                result["message"] = "No pysealer decorator found"
                results[name] = result
                continue
            
            # Extract the source code without pysealer decorators for verification
            # Use original source to preserve formatting (quotes, spacing, etc.)
            content_lines = content.split('\n')
            start_line = node.lineno - 1
            end_line = node.end_lineno if hasattr(node, 'end_lineno') and node.end_lineno else node.lineno
            
            # Get the source lines for this node
            source_lines = content_lines[start_line:end_line]
            
            # Filter out pysealer decorator lines
            filtered_lines = []
            for line in source_lines:
                stripped = line.strip()
                # Skip lines that are pysealer decorators
                if stripped.startswith('@pysealer.') or stripped.startswith('@pysealer'):
                    continue
                filtered_lines.append(line)
            
            function_source = '\n'.join(filtered_lines)
            
            # Store the source code
            result["source"] = function_source
            
            # Verify the signature
            try:
                is_valid = verify_signature(function_source, signature_from_decorator, public_key)
                
                result["valid"] = is_valid
                if is_valid:
                    result["message"] = "✓ Signature valid - code has not been tampered with"
                else:
                    result["message"] = "✗ Signature invalid - code may have been modified"
                    
                    # Try to get git diff for failed validation (only if git is available)
                    if is_git_available():
                        try:
                            diff = get_function_diff(
                                file_path,
                                name,
                                function_source,
                                node.lineno
                            )
                            if diff:
                                result["diff"] = diff
                        except Exception:
                            # If git diff fails, just continue without it
                            pass
                    
            except Exception as e:
                result["message"] = f"✗ Error verifying signature: {e}"
            
            results[name] = result
    
    return results


def check_decorators_in_folder(folder_path: str) -> Dict[str, Dict[str, dict]]:
    """
    Check decorators in all Python files in a folder.
    
    Args:
        folder_path: Path to the folder containing Python files
        
    Returns:
        Dictionary mapping file paths to their verification results
    """
    folder = Path(folder_path)
    
    if not folder.exists():
        raise FileNotFoundError(f"Folder '{folder_path}' does not exist.")
    
    if not folder.is_dir():
        raise NotADirectoryError(f"'{folder_path}' is not a directory.")
    
    # Find all Python files in the folder (recursive)
    python_files = list(folder.rglob('*.py'))
    
    if not python_files:
        raise ValueError(f"No Python files found in '{folder_path}'.")
    
    all_results = {}
    
    for py_file in python_files:
        try:
            results = check_decorators(str(py_file))
            all_results[str(py_file)] = results
        except Exception as e:
            all_results[str(py_file)] = {"error": str(e)}
    
    return all_results
