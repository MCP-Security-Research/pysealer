"""Git-based diff functionality for comparing function/class changes."""

import ast
import subprocess
from pathlib import Path
from typing import Optional, Tuple, List
import difflib


def get_file_from_git(file_path: str, ref: str = "HEAD") -> Optional[str]:
    """
    Retrieve file content from a specific git reference.
    
    Args:
        file_path: Absolute path to the file
        ref: Git reference (default: HEAD)
        
    Returns:
        File content as string, or None if not in git or error occurs
    """
    try:
        # Get relative path from git root
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=Path(file_path).parent,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return None
            
        git_root = result.stdout.strip()
        relative_path = Path(file_path).relative_to(git_root)
        
        # Get file content from git
        result = subprocess.run(
            ["git", "show", f"{ref}:{relative_path}"],
            cwd=git_root,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return result.stdout
        return None
        
    except FileNotFoundError:
        # Git command not found
        return None
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, ValueError, OSError):
        return None


def extract_function_from_source(source_code: str, function_name: str) -> Optional[Tuple[str, int]]:
    """
    Extract a specific function or class from source code.
    
    Args:
        source_code: Python source code
        function_name: Name of function/class to extract
        
    Returns:
        Tuple of (function_source, start_line) or None if not found
    """
    try:
        tree = ast.parse(source_code)
        lines = source_code.splitlines(keepends=True)
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name == function_name:
                    # Get the source lines for this node
                    start_line = node.lineno
                    end_line = node.end_lineno if node.end_lineno else start_line
                    
                    function_lines = lines[start_line - 1:end_line]
                    function_source = ''.join(function_lines)
                    
                    return function_source, start_line
        
        return None
    except (SyntaxError, AttributeError):
        return None


def generate_function_diff(
    old_source: str,
    new_source: str,
    function_name: str,
    old_start_line: int,
    new_start_line: int,
    context_lines: int = 2
) -> List[Tuple[str, str, int]]:
    """
    Generate a unified diff for a specific function.
    
    Args:
        old_source: Old function source code
        new_source: New function source code
        function_name: Name of the function/class
        old_start_line: Starting line number in old file
        new_start_line: Starting line number in new file
        context_lines: Number of context lines to show
        
    Returns:
        List of tuples: (diff_type, line_content, line_number)
        where diff_type is ' ', '-', or '+'
    """
    old_lines = old_source.splitlines(keepends=False)
    new_lines = new_source.splitlines(keepends=False)
    
    # Generate unified diff
    diff = list(difflib.unified_diff(
        old_lines,
        new_lines,
        lineterm='',
        n=context_lines
    ))
    
    # Skip the header lines (first 3 lines of unified diff)
    if len(diff) > 3:
        diff = diff[3:]
    
    result = []
    current_old_line = old_start_line
    current_new_line = new_start_line
    
    for line in diff:
        if not line:
            continue
            
        prefix = line[0]
        content = line[1:] if len(line) > 1 else ''
        
        if prefix == '-':
            result.append(('-', content, current_old_line))
            current_old_line += 1
        elif prefix == '+':
            result.append(('+', content, current_new_line))
            current_new_line += 1
        elif prefix == ' ':
            result.append((' ', content, current_new_line))
            current_old_line += 1
            current_new_line += 1
        elif prefix == '@':
            # Parse line numbers from @@ -old_start,old_count +new_start,new_count @@
            try:
                parts = line.split()
                if len(parts) >= 3:
                    old_part = parts[1].lstrip('-')
                    new_part = parts[2].lstrip('+')
                    
                    if ',' in old_part:
                        current_old_line = int(old_part.split(',')[0])
                    else:
                        current_old_line = int(old_part)
                        
                    if ',' in new_part:
                        current_new_line = int(new_part.split(',')[0])
                    else:
                        current_new_line = int(new_part)
            except (ValueError, IndexError):
                pass
    
    return result


def is_git_available() -> bool:
    """
    Check if the current directory is in a git repository.
    
    Returns:
        True if .git directory exists in current or parent directories, False otherwise
    """
    current = Path.cwd()
    # Check current directory and all parent directories
    for parent in [current] + list(current.parents):
        if (parent / ".git").exists():
            return True
    return False


def get_function_diff(
    file_path: str,
    function_name: str,
    new_source: str,
    new_start_line: int
) -> Optional[List[Tuple[str, str, int]]]:
    """
    Get the diff for a specific function comparing current version to git HEAD.
    
    Args:
        file_path: Absolute path to the Python file
        function_name: Name of the function/class
        new_source: Current source code of the function
        new_start_line: Starting line number of function in current file
        
    Returns:
        List of diff tuples or None if git history unavailable
    """
    # Get the file from git
    old_file_content = get_file_from_git(file_path)
    
    if not old_file_content:
        return None
    
    # Extract the old version of the function
    old_function = extract_function_from_source(old_file_content, function_name)
    
    if not old_function:
        return None
    
    old_source, old_start_line = old_function
    
    # Generate the diff
    diff = generate_function_diff(
        old_source,
        new_source,
        function_name,
        old_start_line,
        new_start_line,
        context_lines=2
    )
    
    return diff if diff else None
