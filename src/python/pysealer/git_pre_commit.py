"""
Git pre-commit hook management for pysealer.

This module provides functionality to install, uninstall, and manage git pre-commit hooks
that automatically run pysealer decorate on specified files before each commit.

The hook can be configured as:
- Mandatory: Commit fails if decorating fails
- Optional: Warnings are shown but commit proceeds
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple


def is_git_repository(path: Optional[Path] = None) -> bool:
    """Check if the current directory or specified path is a git repository."""
    check_path = path or Path.cwd()
    git_dir = check_path / ".git"
    
    if git_dir.exists():
        return True
    
    # Check if we're in a subdirectory of a git repo
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=str(check_path),
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def get_git_root(path: Optional[Path] = None) -> Optional[Path]:
    """Get the root directory of the git repository."""
    check_path = path or Path.cwd()
    
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(check_path),
            capture_output=True,
            text=True,
            check=True
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def create_hook_script(mode: str = "mandatory", target_pattern: str = "**/*.py") -> str:
    """
    Create the pre-commit hook script content.
    
    Args:
        mode: Either 'mandatory' (fail on error) or 'optional' (warn on error)
        target_pattern: Glob pattern for files to process (e.g., '**/*.py', 'src/**/*.py')
    
    Returns:
        The hook script as a string
    """
    hook_script = f'''#!/usr/bin/env python3
"""
Pysealer pre-commit hook - {mode.upper()} mode
Automatically adds cryptographic decorators to Python files before commit.

Target pattern: {target_pattern}
"""

import subprocess
import sys
from pathlib import Path


def get_staged_python_files(pattern="{target_pattern}"):
    """Get list of staged Python files matching the pattern."""
    try:
        # Get all staged files
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            check=True
        )
        
        staged_files = result.stdout.strip().split("\\n")
        
        # Filter for Python files matching pattern
        python_files = []
        for file in staged_files:
            if file and file.endswith(".py"):
                file_path = Path(file)
                # Simple pattern matching (supports **/*.py and src/**/*.py patterns)
                pattern_parts = pattern.split("/")
                if "**" in pattern:
                    # Match any .py file if pattern contains **
                    if pattern.endswith("**/*.py"):
                        python_files.append(file)
                    elif len(pattern_parts) > 1:
                        # Check if file starts with the directory before **
                        prefix = pattern_parts[0]
                        if prefix and file.startswith(prefix):
                            python_files.append(file)
                elif file.endswith(pattern.replace("*", "")):
                    python_files.append(file)
        
        return python_files
    except subprocess.CalledProcessError:
        return []


def main():
    """Main pre-commit hook logic."""
    staged_files = get_staged_python_files()
    
    if not staged_files:
        # No Python files staged, nothing to do
        sys.exit(0)
    
    print(f"🔒 Pysealer pre-commit hook ({mode} mode)")
    print(f"   Processing {{len(staged_files)}} Python file(s)...")
    
    # Run pysealer lock on each staged file
    failed_files = []
    for file in staged_files:
        try:
            result = subprocess.run(
                ["pysealer", "lock", file],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                failed_files.append((file, result.stderr or result.stdout))
        except FileNotFoundError:
            print("❌ Error: pysealer command not found")
            print("   Make sure pysealer is installed: pip install pysealer")
            
            if "{mode}" == "mandatory":
                sys.exit(1)
            else:
                print("   Proceeding with commit (optional mode)")
                sys.exit(0)
        except Exception as e:
            failed_files.append((file, str(e)))
    
    # Check if any files failed
    if failed_files:
        print("❌ Pysealer failed for the following files:")
        for file, error in failed_files:
            print(f"   - {{file}}: {{error}}")
        
        if "{mode}" == "mandatory":
            print("\\n⚠️  Commit blocked. Fix the issues above and try again.")
            print("   Or temporarily disable with: git commit --no-verify")
            sys.exit(1)
        else:
            print("\\n⚠️  Warning: Proceeding with commit (optional mode)")
    
    # Re-stage the modified files
    for file in staged_files:
        subprocess.run(["git", "add", file], check=False)
    
    print("✅ Successfully locked files")
    sys.exit(0)


if __name__ == "__main__":
    main()
'''
    return hook_script


def install_hook(
    mode: str = "mandatory",
    target_pattern: str = "**/*.py",
    repo_path: Optional[Path] = None
) -> Tuple[bool, str]:
    """
    Install the pysealer pre-commit hook.
    
    Args:
        mode: Either 'mandatory' (fail on error) or 'optional' (warn on error)
        target_pattern: Glob pattern for files to process
        repo_path: Path to git repository (defaults to current directory)
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Validate mode
    if mode not in ["mandatory", "optional"]:
        return False, f"Invalid mode '{mode}'. Must be 'mandatory' or 'optional'."
    
    # Find git repository
    git_root = get_git_root(repo_path)
    if not git_root:
        return False, "Not a git repository. Initialize git first with 'git init'."
    
    # Create hooks directory if it doesn't exist
    hooks_dir = git_root / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    
    # Path to pre-commit hook
    hook_path = hooks_dir / "pre-commit"
    
    # Check if hook already exists
    if hook_path.exists():
        # Read existing hook to check if it's ours
        existing_content = hook_path.read_text()
        if "Pysealer pre-commit hook" in existing_content:
            return False, f"Pysealer hook already installed at {hook_path}"
        else:
            return False, f"A different pre-commit hook already exists at {hook_path}. Remove it first or merge manually."
    
    # Create and write the hook script
    hook_script = create_hook_script(mode, target_pattern)
    hook_path.write_text(hook_script)
    
    # Make the hook executable
    hook_path.chmod(0o755)
    
    return True, f"Pre-commit hook installed in {mode} mode"


def uninstall_hook(repo_path: Optional[Path] = None) -> Tuple[bool, str]:
    """
    Uninstall the pysealer pre-commit hook.
    
    Args:
        repo_path: Path to git repository (defaults to current directory)
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    git_root = get_git_root(repo_path)
    if not git_root:
        return False, "Not a git repository."
    
    hook_path = git_root / ".git" / "hooks" / "pre-commit"
    
    if not hook_path.exists():
        return False, "No pre-commit hook found."
    
    # Check if it's our hook
    existing_content = hook_path.read_text()
    if "Pysealer pre-commit hook" not in existing_content:
        return False, "Pre-commit hook exists but is not a pysealer hook. Not removing."
    
    # Remove the hook
    hook_path.unlink()
    
    return True, "Pre-commit hook uninstalled successfully"


def get_hook_status(repo_path: Optional[Path] = None) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Check if pysealer pre-commit hook is installed and get its configuration.
    
    Args:
        repo_path: Path to git repository (defaults to current directory)
    
    Returns:
        Tuple of (is_installed: bool, mode: Optional[str], target_pattern: Optional[str])
    """
    git_root = get_git_root(repo_path)
    if not git_root:
        return False, None, None
    
    hook_path = git_root / ".git" / "hooks" / "pre-commit"
    
    if not hook_path.exists():
        return False, None, None
    
    content = hook_path.read_text()
    
    if "Pysealer pre-commit hook" not in content:
        return False, None, None
    
    # Extract mode and pattern from the hook
    mode = None
    pattern = None
    
    for line in content.split("\n"):
        if "mode" in line.lower() and ("MANDATORY" in line or "OPTIONAL" in line):
            mode = "mandatory" if "MANDATORY" in line else "optional"
        if "Target pattern:" in line:
            pattern = line.split("Target pattern:")[-1].strip()
    
    return True, mode, pattern
