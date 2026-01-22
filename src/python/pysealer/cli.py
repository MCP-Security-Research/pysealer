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

from . import __version__
from .setup import setup_keypair
from .add_decorators import add_decorators, add_decorators_to_folder
from .check_decorators import check_decorators, check_decorators_in_folder
from .remove_decorators import remove_decorators, remove_decorators_from_folder

app = typer.Typer(
    name="pysealer",
    help="Version control your Python functions and classes with cryptographic decorators",
    no_args_is_help=True,
)


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
        typer.Option("--github-token", help="GitHub personal access token for uploading public key to repository secrets")
    ] = None,
    skip_github: Annotated[
        bool,
        typer.Option("--skip-github", help="Skip GitHub secrets integration")
    ] = False
):
    """Initialize pysealer with an .env file and optionally upload public key to GitHub."""
    try:
        env_path = Path(env_file)
        
        # Generate and store keypair (will raise error if keys already exist)
        public_key, private_key = setup_keypair(env_path)
        typer.echo(typer.style("Successfully initialized pysealer!", fg=typer.colors.BLUE, bold=True))
        typer.echo(f"🔑 Keypair generated and stored in {env_path}")
        typer.echo("⚠️  Keep your .env file secure and add it to .gitignore!")
        
        # GitHub secrets integration (optional)
        if not skip_github:
            typer.echo()  # Blank line for readability
            typer.echo("Attempting to upload public key to GitHub repository secrets...")
            
            try:
                from .github_secrets import setup_github_secrets
                
                success, message = setup_github_secrets(public_key, github_token)
                
                if success:
                    typer.echo(typer.style(f"✓ {message}", fg=typer.colors.GREEN))
                else:
                    typer.echo(typer.style(f"⚠ Warning: {message}", fg=typer.colors.YELLOW))
                    typer.echo("  You can manually add the public key to GitHub secrets later.")
                    typer.echo(f"  Secret name: PYSEALER_PUBLIC_KEY")
                    typer.echo(f"  Public key: {public_key}")
                    
            except ImportError as e:
                typer.echo(typer.style(f"⚠ Warning: GitHub integration dependencies not installed: {e}", fg=typer.colors.YELLOW))
                typer.echo("  Install with: pip install PyGithub PyNaCl GitPython")
            except Exception as e:
                typer.echo(typer.style(f"⚠ Warning: Failed to upload to GitHub: {e}", fg=typer.colors.YELLOW))
                typer.echo("  You can manually add the public key to GitHub secrets later.")
        
    except Exception as e:
        typer.echo(typer.style(f"Error during initialization: {e}", fg=typer.colors.RED, bold=True), err=True)
        raise typer.Exit(code=1)

@app.command()
def lock(
    file_path: Annotated[
        str,
        typer.Argument(help="Path to the Python file or folder to decorate")
    ]
):
    """Add decorators to all functions and classes in a Python file or all Python files in a folder."""
    path = Path(file_path)
    
    # Validate path exists
    if not path.exists():
        typer.echo(typer.style(f"Error: Path '{path}' does not exist.", fg=typer.colors.RED, bold=True), err=True)
        raise typer.Exit(code=1)
    
    try:
        # Handle folder path
        if path.is_dir():
            resolved_path = str(path.resolve())
            decorated_files = add_decorators_to_folder(resolved_path)
            
            typer.echo(typer.style(f"Successfully added decorators to {len(decorated_files)} files:", fg=typer.colors.BLUE, bold=True))
            for file in decorated_files:
                typer.echo(f"  {typer.style('✓', fg=typer.colors.GREEN)} {file}")
        
        # Handle file path
        else:
            # Validate it's a Python file
            if not path.suffix == '.py':
                typer.echo(typer.style(f"Error: File '{path}' is not a Python file.", fg=typer.colors.RED, bold=True), err=True)
                raise typer.Exit(code=1)
            
            # Add decorators to all functions and classes in the file
            resolved_path = str(path.resolve())
            modified_code = add_decorators(resolved_path)
            
            # Write the modified code back to the file
            with open(resolved_path, 'w') as f:
                f.write(modified_code)
            
            typer.echo(typer.style(f"Successfully added decorators to 1 file:", fg=typer.colors.BLUE, bold=True))
            typer.echo(f"  {typer.style('✓', fg=typer.colors.GREEN)} {resolved_path}")
        
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
    
    try:
        # Handle folder path
        if path.is_dir():
            resolved_path = str(path.resolve())
            all_results = check_decorators_in_folder(resolved_path)
            
            total_decorated = 0
            total_valid = 0
            total_files = 0
            files_with_issues = []
            
            for file_path, results in all_results.items():
                # Skip files with errors
                if "error" in results:
                    typer.echo(typer.style(f"✗ {file_path}: {results['error']}", fg=typer.colors.RED))
                    files_with_issues.append(file_path)
                    continue
                
                total_files += 1
                decorated_count = sum(1 for r in results.values() if r["has_decorator"])
                valid_count = sum(1 for r in results.values() if r["valid"])
                
                total_decorated += decorated_count
                total_valid += valid_count
                
                # Track files with validation failures
                if decorated_count > 0 and valid_count < decorated_count:
                    files_with_issues.append(file_path)
            
            # Summary header
            if total_decorated == 0:
                typer.echo("⚠️  No pysealer decorators found in any files.")
            elif total_valid == total_decorated:
                typer.echo(typer.style(f"All decorators are valid in {total_files} files:", fg=typer.colors.BLUE, bold=True))
            else:
                typer.echo(typer.style(f"{total_decorated - total_valid}/{total_decorated} decorators failed verification across {total_files} files:", fg=typer.colors.BLUE, bold=True), err=True)
            
            # File-by-file details
            for file_path, results in all_results.items():
                if "error" in results:
                    continue
                
                decorated_count = sum(1 for r in results.values() if r["has_decorator"])
                valid_count = sum(1 for r in results.values() if r["valid"])
                
                if decorated_count > 0:
                    if valid_count == decorated_count:
                        typer.echo(f"  {typer.style('✓', fg=typer.colors.GREEN)} {file_path}: {typer.style(f'{decorated_count} decorators valid', fg=typer.colors.GREEN)}")
                    else:
                        typer.echo(f"  {typer.style('✗', fg=typer.colors.RED)} {file_path}: {typer.style(f'{decorated_count - valid_count}/{decorated_count} decorators failed', fg=typer.colors.RED)}")
            
            # Exit with error if there were failures
            if total_decorated > 0 and total_valid < total_decorated:
                raise typer.Exit(code=1)
        
        # Handle file path
        else:
            # Validate it's a Python file
            if not path.suffix == '.py':
                typer.echo(typer.style(f"Error: File '{path}' is not a Python file.", fg=typer.colors.RED, bold=True), err=True)
                raise typer.Exit(code=1)
            
            # Check all decorators in the file
            resolved_path = str(path.resolve())
            results = check_decorators(resolved_path)
            
            # Return success if all decorated functions are valid
            decorated_count = sum(1 for r in results.values() if r["has_decorator"])
            valid_count = sum(1 for r in results.values() if r["valid"])
            
            if decorated_count == 0:
                typer.echo("⚠️  No pysealer decorators found in this file.")
            elif valid_count == decorated_count:
                typer.echo(typer.style("All decorators are valid in 1 file:", fg=typer.colors.BLUE, bold=True))
                typer.echo(f"{typer.style('✓', fg=typer.colors.GREEN)} {resolved_path}: {typer.style(f'{decorated_count} decorators valid', fg=typer.colors.GREEN)}")
            else:
                typer.echo(typer.style(f"{decorated_count - valid_count}/{decorated_count} decorators failed verification across 1 file:", fg=typer.colors.BLUE, bold=True), err=True)
                typer.echo(f"  {typer.style('✗', fg=typer.colors.RED)} {resolved_path}: {typer.style(f'{decorated_count - valid_count}/{decorated_count} decorators failed', fg=typer.colors.RED)}")
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
    
    try:
        # Handle folder path
        if path.is_dir():
            resolved_path = str(path.resolve())
            modified_files = remove_decorators_from_folder(resolved_path)
            
            if modified_files:
                typer.echo(typer.style(f"Successfully removed decorators from {len(modified_files)} files:", fg=typer.colors.BLUE, bold=True))
                for file in modified_files:
                    typer.echo(f"  {typer.style('✓', fg=typer.colors.GREEN)} {file}")
            else:
                typer.echo("⚠️  No pysealer decorators found in any files.")
        
        # Handle file path
        else:
            # Validate it's a Python file
            if not path.suffix == '.py':
                typer.echo(typer.style(f"Error: File '{path}' is not a Python file.", fg=typer.colors.RED, bold=True), err=True)
                raise typer.Exit(code=1)
            
            resolved_path = str(path.resolve())
            modified_code, found = remove_decorators(resolved_path)
            
            with open(resolved_path, 'w') as f:
                f.write(modified_code)
            
            if found:
                typer.echo(typer.style(f"Successfully removed decorators from 1 file:", fg=typer.colors.BLUE, bold=True))
                typer.echo(f"  {typer.style('✓', fg=typer.colors.GREEN)} {resolved_path}")
            else:
                typer.echo(f"⚠️  No pysealer decorators found in {resolved_path}")
    
    except (FileNotFoundError, NotADirectoryError, ValueError) as e:
        typer.echo(typer.style(f"Error: {e}", fg=typer.colors.RED, bold=True), err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(typer.style(f"Unexpected error while removing decorators: {e}", fg=typer.colors.RED, bold=True), err=True)
        raise typer.Exit(code=1)


def main():
    """Main CLI entry point."""
    app()


if __name__ == '__main__':
    main()
