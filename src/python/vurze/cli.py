"""
Command-line interface for vurze.

Commands:
- init: Initialize vurze with a new keypair and .env file.
- decorate: Add vurze decorators to all functions and classes in a Python file.
- check: Check the integrity and validity of vurze decorators in a Python file.
- remove: Remove all vurze decorators from a Python file.

Use `vurze --help` to see available options and command details.
"""

from pathlib import Path

import typer
from typing_extensions import Annotated

from .setup import setup_keypair
from .add_decorators import add_decorators, add_decorators_to_folder
from .check_decorators import check_decorators, check_decorators_in_folder
from .remove_decorators import remove_decorators, remove_decorators_from_folder

app = typer.Typer(
    name="vurze",
    help="Version control your Python functions and classes with cryptographic decorators",
    no_args_is_help=True,
)


@app.command()
def init(
    env_file: Annotated[
        str,
        typer.Argument(help="Path to the .env file")
    ] = ".env"
):
    """Initialize vurze with an .env file."""
    try:
        env_path = Path(env_file)
        
        # Generate and store keypair (will raise error if keys already exist)
        setup_keypair(env_path)
        typer.echo(typer.style("Successfully initialized vurze!", fg=typer.colors.BLUE, bold=True))
        typer.echo(f"🔑 Keypair generated and stored in {env_path}")
        typer.echo("⚠️  Keep your .env file secure and add it to .gitignore!")
        
    except Exception as e:
        typer.echo(typer.style(f"Error during initialization: {e}", fg=typer.colors.RED, bold=True), err=True)
        raise typer.Exit(code=1)


@app.command()
def decorate(
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
            
            typer.echo(typer.style(f"Successfully added decorators to {len(decorated_files)} file(s):", fg=typer.colors.BLUE, bold=True))
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
            
            typer.echo(typer.style(f"Successfully added decorators to 1 file(s):", fg=typer.colors.BLUE, bold=True))
            typer.echo(f"  {typer.style('✓', fg=typer.colors.GREEN)} {resolved_path}")
        
    except (RuntimeError, FileNotFoundError, NotADirectoryError, ValueError) as e:
        typer.echo(typer.style(f"Error: {e}", fg=typer.colors.RED, bold=True), err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(typer.style(f"Unexpected error while decorating: {e}", fg=typer.colors.RED, bold=True), err=True)
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
                typer.echo("⚠️  No vurze decorators found in any files.")
            elif total_valid == total_decorated:
                typer.echo(typer.style(f"All {total_decorated} decorator(s) across {total_files} file(s) are valid!", fg=typer.colors.BLUE, bold=True))
            else:
                typer.echo(typer.style(f"{total_decorated - total_valid}/{total_decorated} decorator(s) failed verification across {len(files_with_issues)} file(s)!", fg=typer.colors.BLUE, bold=True), err=True)
            
            # File-by-file details
            for file_path, results in all_results.items():
                if "error" in results:
                    continue
                
                decorated_count = sum(1 for r in results.values() if r["has_decorator"])
                valid_count = sum(1 for r in results.values() if r["valid"])
                
                if decorated_count > 0:
                    if valid_count == decorated_count:
                        typer.echo(f"{typer.style('✓', fg=typer.colors.GREEN)} {file_path}: {typer.style(f'All {decorated_count} decorator(s) valid', fg=typer.colors.GREEN)}")
                    else:
                        typer.echo(f"{typer.style('✗', fg=typer.colors.RED)} {file_path}: {typer.style(f'{decorated_count - valid_count}/{decorated_count} decorator(s) failed', fg=typer.colors.RED)}")
            
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
                typer.echo("⚠️  No vurze decorators found in this file.")
            elif valid_count == decorated_count:
                typer.echo(typer.style(f"All {decorated_count} decorator(s) across 1 file(s) are valid!", fg=typer.colors.BLUE, bold=True))
                typer.echo(f"{typer.style('✓', fg=typer.colors.GREEN)} {resolved_path}: {typer.style(f'All {decorated_count} decorator(s) valid', fg=typer.colors.GREEN)}")
            else:
                typer.echo(typer.style(f"{decorated_count - valid_count}/{decorated_count} decorator(s) failed verification across 1 file(s)!", fg=typer.colors.BLUE, bold=True), err=True)
                typer.echo(f"{typer.style('✗', fg=typer.colors.RED)} {resolved_path}: {typer.style(f'{decorated_count - valid_count}/{decorated_count} decorator(s) failed', fg=typer.colors.RED)}")
                raise typer.Exit(code=1)
    
    except (FileNotFoundError, NotADirectoryError, ValueError) as e:
        typer.echo(typer.style(f"Error: {e}", fg=typer.colors.RED, bold=True), err=True)
        raise typer.Exit(code=1)


@app.command()
def remove(
    file_path: Annotated[
        str,
        typer.Argument(help="Path to the Python file or folder to remove vurze decorators from")
    ]
):
    """Remove vurze decorators from all functions and classes in a Python file or all Python files in a folder."""
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
                typer.echo(typer.style(f"Successfully removed decorators from {len(modified_files)} file(s):", fg=typer.colors.BLUE, bold=True))
                for file in modified_files:
                    typer.echo(f"  {typer.style('✓', fg=typer.colors.GREEN)} {file}")
            else:
                typer.echo("⚠️  No vurze decorators found in any files.")
        
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
                typer.echo(typer.style(f"Successfully removed vurze decorators from {resolved_path}", fg=typer.colors.BLUE, bold=True))
            else:
                typer.echo(f"⚠️  No vurze decorators found in {resolved_path}")
    
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
