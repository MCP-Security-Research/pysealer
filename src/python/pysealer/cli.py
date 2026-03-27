"""
Command-line interface for pysealer.

Commands:
- init: Initialize pysealer with a new keypair and .env file.
- lock: Add pysealer decorators to all functions and classes in a Python file.
- check: Check the integrity and validity of pysealer decorators in a Python file.
- remove: Remove all pysealer decorators from a Python file.

Use `pysealer --help` to see available options and command details.
Use `pysealer --version` to see the current version of pysealer installed.
"""

from pathlib import Path

import typer
from typing_extensions import Annotated

from . import __version__, generate_signature, verify_signature
from .setup import setup_keypair
from .add_decorators import add_decorators, add_decorators_to_folder
from .check_decorators import check_decorators, check_decorators_in_folder
from .remove_decorators import remove_decorators, remove_decorators_from_folder
from .git_diff import is_git_available
from .git_pre_commit import install_hook, get_hook_status, is_git_repository

app = typer.Typer(
    name="pysealer",
    help="Version control your Python functions and classes with cryptographic decorators",
    no_args_is_help=True,
)


def _format_diff_output(func_name: str, diff_lines):
    """Format and display git diff with color coding."""
    if not diff_lines:
        return
    typer.echo(typer.style(f"    Function '{func_name}' was modified:", fg=typer.colors.RED, bold=True))

    for diff_type, content, line_num in diff_lines:
        # Format line with appropriate styling
        if diff_type == '-':
            # Deletions in red
            line_str = f"      {line_num:<4}{typer.style('-', fg=typer.colors.RED)}{typer.style(content, fg=typer.colors.RED)}"
        elif diff_type == '+':
            # Additions in green
            line_str = f"      {line_num:<4}{typer.style('+', fg=typer.colors.GREEN)}{typer.style(content, fg=typer.colors.GREEN)}"
        else:
            # Context lines in dim/default color
            line_str = f"      {line_num:<4} {content}"

        typer.echo(line_str)


def _format_missing_decorator_output(file_path: str, symbol_name: str, result: dict):
    """Format and display missing decorator information with exact source lines."""
    node_type = result.get("node_type")
    if node_type == "ClassDef":
        label = "Class"
    elif node_type == "AsyncFunctionDef":
        label = "Async function"
    else:
        label = "Function"

    typer.echo(
        typer.style(
            f"    {label} '{symbol_name}' does not contain a @pysealer decorator:",
            fg=typer.colors.RED,
            bold=True,
        )
    )

    line_start = result.get("line_start")
    line_end = result.get("line_end")

    try:
        with open(file_path, "r") as f:
            lines = f.readlines()

        if isinstance(line_start, int) and isinstance(line_end, int):
            for line_num in range(line_start, line_end + 1):
                if 1 <= line_num <= len(lines):
                    content = lines[line_num - 1].rstrip("\n")
                    typer.echo(f"      {line_num:<4} {content}")
            return
    except Exception:
        # Fall back to source from results if file line extraction fails.
        pass

    source = result.get("source") or ""
    if source:
        start = line_start if isinstance(line_start, int) else 1
        for i, line in enumerate(source.splitlines()):
            typer.echo(f"      {start + i:<4} {line}")


def version_callback(value: bool):
    """Helper function to display version information."""
    if value:
        typer.echo(f"pysealer {__version__}")
        raise typer.Exit()


@app.callback()
def version(
    version: Annotated[
        bool,
        typer.Option("--version", help="Report the current version of pysealer installed.", callback=version_callback, is_eager=True)
    ] = False
):
    """Report the current version of pysealer installed."""
    pass


@app.command()
def init(
    env_file: Annotated[
        str,
        typer.Argument(help="Path to the .env file")
    ] = ".env",
    github_token: Annotated[
        str,
        typer.Option("--github-token", help="GitHub personal access token for uploading public key to repository secrets.")
    ] = None,
    hook_mode: Annotated[
        str,
        typer.Option("--hook-mode", help="Hook mode: 'mandatory' (block commits on error) or 'optional' (warn only).")
    ] = "mandatory",
    hook_pattern: Annotated[
        str,
        typer.Option("--hook-pattern", help="File pattern for hook to process. Use quotes to prevent shell expansion: '**/*.py' or 'src/**/*.py'")
    ] = "**/*.py"
):
    """Initialize pysealer with an .env file and optionally upload public key to GitHub."""
    try:
        env_path = Path(env_file)

        # Generate and store keypair (will raise error if keys already exist)
        public_key, private_key = setup_keypair(env_path)

        # Self-test the generated keypair before any GitHub upload
        probe_message = "pysealer-keypair-self-test"
        probe_signature = generate_signature(probe_message, private_key)
        if not verify_signature(probe_message, probe_signature, public_key):
            raise RuntimeError("Generated keypair self-test failed. Aborting initialization.")

        typer.echo(typer.style("Successfully initialized pysealer!", fg=typer.colors.BLUE, bold=True))
        typer.echo(f"🔑 Keypair generated and stored in {env_path}")
        typer.echo("🔍 Keep your .env file secure and add it to .gitignore")

        # GitHub secrets integration (optional, only if token provided)
        if github_token:
            typer.echo(typer.style("Attempting to upload public key to GitHub repository secrets...", fg=typer.colors.BLUE, bold=True))
            try:
                from .github_secrets import setup_github_secrets

                success, message = setup_github_secrets(public_key, github_token)

                if success:
                    typer.echo(typer.style(f"✓ {message}", fg=typer.colors.GREEN))
                else:
                    typer.echo(typer.style(f"⚠️  Warning: {message}", fg=typer.colors.YELLOW))
                    typer.echo("   You can manually add the PYSEALER_PUBLIC_KEY to GitHub secrets later.")

            except ImportError as e:
                typer.echo(typer.style(f"⚠️  Warning: GitHub integration dependencies not installed: {e}", fg=typer.colors.YELLOW))
            except Exception as e:
                typer.echo(typer.style(f"⚠️  Warning: Failed to upload to GitHub: {e}", fg=typer.colors.YELLOW))
                typer.echo("   You can manually add the PYSEALER_PUBLIC_KEY to GitHub secrets later.")

        # Git hook installation (automatic if in git repository)
        if not is_git_repository():
            typer.echo(typer.style("⚠️  Warning: Not a git repository. Skipping hook installation.", fg=typer.colors.YELLOW))
            typer.echo("   Initialize git first with 'git init', then run 'pysealer hook install'")
        else:
            # Check if hook is already installed
            is_installed, _, _ = get_hook_status()

            if is_installed:
                typer.echo(typer.style("✓ Git pre-commit hook already installed", fg=typer.colors.GREEN))
            else:
                typer.echo(typer.style("Installing Pysealer git pre-commit hook...", fg=typer.colors.BLUE, bold=True))
                success, message = install_hook(mode=hook_mode, target_pattern=hook_pattern)

                if success:
                    typer.echo(typer.style(f"✓ {message}", fg=typer.colors.GREEN))
                    typer.echo(f"   Mode: {hook_mode}")
                    typer.echo(f"   Pattern: {hook_pattern}")
                    typer.echo("   The hook will automatically lock files before each commit.")
                    typer.echo("   To bypass: git commit --no-verify")
                else:
                    typer.echo(typer.style(f"⚠️  Warning: {message}", fg=typer.colors.YELLOW))
                    typer.echo("   You can manually install it by editing .git/hooks/pre-commit")

    except Exception as e:
        typer.echo(typer.style(f"Error during initialization: {e}", fg=typer.colors.RED, bold=True), err=True)
        raise typer.Exit(code=1)

@app.command()
def lock(
    file_path: Annotated[
        str,
        typer.Argument(help="Path to the Python file or folder to lock")
    ]
):
    """Add decorators to all functions and classes in a Python file or all Python files in a folder."""
    path = Path(file_path)

    # Validate path exists
    if not path.exists():
        typer.echo(typer.style(f"Error: Path '{path}' does not exist.", fg=typer.colors.RED, bold=True), err=True)
        raise typer.Exit(code=1)

    # Validate it's a Python file or directory
    if path.is_file() and path.suffix != '.py':
        typer.echo(typer.style(f"Error: File '{path}' is not a Python file.", fg=typer.colors.RED, bold=True), err=True)
        raise typer.Exit(code=1)

    try:
        # Handle folder path
        if path.is_dir():
            resolved_path = str(path.resolve())
            decorated_files = add_decorators_to_folder(resolved_path)

            file_word = "file" if len(decorated_files) == 1 else "files"
            typer.echo(typer.style(f"Successfully added decorators to {len(decorated_files)} {file_word}:", fg=typer.colors.BLUE, bold=True))
            for file in decorated_files:
                typer.echo(f"  {typer.style('✓', fg=typer.colors.GREEN)} {file}")

        # Handle file path
        else:

            # Add decorators to all functions and classes in the file
            resolved_path = str(path.resolve())
            modified_code, has_changes = add_decorators(resolved_path)

            if has_changes:
                # Write the modified code back to the file
                with open(resolved_path, 'w') as f:
                    f.write(modified_code)

                typer.echo(typer.style("Successfully added decorators to 1 file:", fg=typer.colors.BLUE, bold=True))
                typer.echo(f"  {typer.style('✓', fg=typer.colors.GREEN)} {resolved_path}")
            else:
                typer.echo(typer.style("No functions or classes found in file:", fg=typer.colors.YELLOW, bold=True))
                typer.echo(f"  {typer.style('⊘', fg=typer.colors.YELLOW)} {resolved_path}")

    except (RuntimeError, FileNotFoundError, NotADirectoryError, ValueError) as e:
        typer.echo(typer.style(f"Error: {e}", fg=typer.colors.RED, bold=True), err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(typer.style(f"Unexpected error while locking file: {e}", fg=typer.colors.RED, bold=True), err=True)
        raise typer.Exit(code=1)


@app.command()
def check(
    file_path: Annotated[
        str,
        typer.Argument(help="Path to the Python file or folder to check")
    ]
):
    """Check the integrity of decorators in a Python file or all Python files in a folder."""
    path = Path(file_path)

    # Validate path exists
    if not path.exists():
        typer.echo(typer.style(f"Error: Path '{path}' does not exist.", fg=typer.colors.RED, bold=True), err=True)
        raise typer.Exit(code=1)

    # Validate it's a Python file or directory
    if path.is_file() and path.suffix != '.py':
        typer.echo(typer.style(f"Error: File '{path}' is not a Python file.", fg=typer.colors.RED, bold=True), err=True)
        raise typer.Exit(code=1)

    try:
        # Check if git is available for diff output
        git_available = is_git_available()
        if not git_available:
            typer.echo(typer.style("Note: Git not available - diff output will not be shown for invalid signatures.", fg=typer.colors.YELLOW))
            typer.echo()

        # Handle folder path
        if path.is_dir():
            resolved_path = str(path.resolve())
            all_results = check_decorators_in_folder(resolved_path)

            total_checked = 0
            total_failed = 0
            files_with_symbols = []
            files_with_issues = []
            files_with_errors = []

            for file_path, results in all_results.items():
                # Track files with errors separately
                if "error" in results:
                    typer.echo(typer.style(f"✗ {file_path}: {results['error']}", fg=typer.colors.RED))
                    files_with_errors.append((file_path, results['error']))
                    files_with_issues.append(file_path)
                    continue

                checked_count = len(results)
                missing_count = sum(1 for r in results.values() if not r["has_decorator"])
                invalid_count = sum(1 for r in results.values() if r["has_decorator"] and not r["valid"])
                failed_count = missing_count + invalid_count

                if checked_count > 0:
                    files_with_symbols.append(file_path)
                    total_checked += checked_count
                    total_failed += failed_count

                    # Track files with any failures.
                    if failed_count > 0:
                        files_with_issues.append(file_path)

            # Summary header
            if files_with_errors and total_checked == 0:
                # All files had errors, couldn't check for decorators
                error_count = len(files_with_errors)
                file_word = "file" if error_count == 1 else "files"
                typer.echo(typer.style(f"\nFailed to check decorators in {error_count} {file_word} due to errors.", fg=typer.colors.RED, bold=True))
                typer.echo(typer.style("Fix the errors above to verify decorators.", fg=typer.colors.YELLOW))
                raise typer.Exit(code=1)
            elif total_checked == 0:
                typer.echo(typer.style("No pysealer decorators found in folder.", fg=typer.colors.RED, bold=True))
                raise typer.Exit(code=1)
            elif total_failed == 0:
                file_word = "file" if len(files_with_symbols) == 1 else "files"
                typer.echo(typer.style(f"All decorators are valid in {len(files_with_symbols)} {file_word}:", fg=typer.colors.BLUE, bold=True))
            else:
                failed_files = len(files_with_issues)
                check_word = "check" if total_failed == 1 else "checks"
                file_word = "file" if failed_files == 1 else "files"
                typer.echo(typer.style(f"{total_failed} {check_word} failed in {failed_files} {file_word}:", fg=typer.colors.BLUE, bold=True), err=True)

            # File-by-file details.
            if total_checked > 0:
                for file_path in files_with_symbols:
                    results = all_results[file_path]
                    if "error" in results:
                        continue

                    missing_count = sum(1 for r in results.values() if not r["has_decorator"])
                    invalid_count = sum(1 for r in results.values() if r["has_decorator"] and not r["valid"])
                    failed_count = missing_count + invalid_count

                    if failed_count == 0:
                        typer.echo(f"  {typer.style('✓', fg=typer.colors.GREEN)} {file_path}")
                    else:
                        typer.echo(f"  {typer.style('✗', fg=typer.colors.RED)} {file_path}")

                        # Show missing-decorator snippets.
                        for symbol_name, result in results.items():
                            if not result["has_decorator"]:
                                _format_missing_decorator_output(file_path, symbol_name, result)

                        # Show diff for each signature validation failure.
                        for func_name, result in results.items():
                            if result["has_decorator"] and not result["valid"]:
                                if result.get("diff"):
                                    _format_diff_output(func_name, result["diff"])

            # Exit with error if there were failures or errors
            if files_with_errors:
                raise typer.Exit(code=1)
            elif total_checked > 0 and total_failed > 0:
                raise typer.Exit(code=1)

        # Handle file path
        else:

            # Check all decorators in the file
            resolved_path = str(path.resolve())
            results = check_decorators(resolved_path)

            # Return success if no definitions are missing decorators and all signatures are valid.
            checked_count = len(results)
            missing_count = sum(1 for r in results.values() if not r["has_decorator"])
            decorated_count = sum(1 for r in results.values() if r["has_decorator"])
            valid_count = sum(1 for r in results.values() if r["has_decorator"] and r["valid"])
            failed_count = missing_count + (decorated_count - valid_count)

            if checked_count == 0:
                typer.echo(typer.style("No pysealer decorators found in 1 file:", fg=typer.colors.RED, bold=True))
                typer.echo(f"  {typer.style('⊘', fg=typer.colors.RED)} {resolved_path}")
                raise typer.Exit(code=1)
            elif failed_count == 0:
                typer.echo(typer.style(f"All decorators are valid in 1 file:", fg=typer.colors.BLUE, bold=True))
                typer.echo(f"  {typer.style('✓', fg=typer.colors.GREEN)} {resolved_path}")
            else:
                # Ratio output should agree with the denominator (e.g., 1/2 checks).
                check_word = "check" if checked_count == 1 else "checks"
                typer.echo(typer.style(f"{failed_count}/{checked_count} {check_word} failed in 1 file:", fg=typer.colors.BLUE, bold=True), err=True)
                typer.echo(f"  {typer.style('✗', fg=typer.colors.RED)} {resolved_path}")

                for symbol_name, result in results.items():
                    if not result["has_decorator"]:
                        _format_missing_decorator_output(resolved_path, symbol_name, result)

                # Show diff for each failed function
                for func_name, result in results.items():
                    if result["has_decorator"] and not result["valid"]:
                        if result.get("diff"):
                            _format_diff_output(func_name, result["diff"])

                raise typer.Exit(code=1)

    except (FileNotFoundError, NotADirectoryError, ValueError) as e:
        typer.echo(typer.style(f"Error: {e}", fg=typer.colors.RED, bold=True), err=True)
        raise typer.Exit(code=1)


@app.command()
def remove(
    file_path: Annotated[
        str,
        typer.Argument(help="Path to the Python file or folder to remove pysealer decorators from")
    ]
):
    """Remove pysealer decorators from all functions and classes in a Python file or all Python files in a folder."""
    path = Path(file_path)

    # Validate path exists
    if not path.exists():
        typer.echo(typer.style(f"Error: Path '{path}' does not exist.", fg=typer.colors.RED, bold=True), err=True)
        raise typer.Exit(code=1)

    # Validate it's a Python file or directory
    if path.is_file() and path.suffix != '.py':
        typer.echo(typer.style(f"Error: File '{path}' is not a Python file.", fg=typer.colors.RED, bold=True), err=True)
        raise typer.Exit(code=1)

    try:
        # Handle folder path
        if path.is_dir():
            resolved_path = str(path.resolve())
            modified_files = remove_decorators_from_folder(resolved_path)

            file_word = "file" if len(modified_files) == 1 else "files"
            typer.echo(typer.style(f"Successfully removed decorators from {len(modified_files)} {file_word}:", fg=typer.colors.BLUE, bold=True))
            for file in modified_files:
                typer.echo(f"  {typer.style('✓', fg=typer.colors.GREEN)} {file}")
        # Handle single file
        else:
            resolved_path = str(path.resolve())
            modified_content, _ = remove_decorators(resolved_path)
            typer.echo(typer.style(f"✓ Successfully removed decorators from: {resolved_path}", fg=typer.colors.GREEN))

    except Exception as e:
        typer.echo(typer.style(f"Error removing decorators: {e}", fg=typer.colors.RED, bold=True), err=True)
        raise typer.Exit(code=1)


def main():
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    main()
