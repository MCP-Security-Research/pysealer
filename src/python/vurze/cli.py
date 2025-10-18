"""
Command-line interface for vurze.

Provides commands:
- vurze init <optional arg of .env file path>: Initialize vurze with an .env file
- vurze decorate <python_file_path>: Add decorators to functions in a Python file
- vurze check <python_file_path>: Check the integrity of decorators in a Python file
- vurze remove (this is cleanup code)
"""

import argparse
import sys
from pathlib import Path

from .setup import setup_keypair
from .add_decorators import add_decorators_to_functions

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="vurze",
        description="Version control your Python functions with cryptographic decorators"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    init_parser = subparsers.add_parser(
        'init',
        help='Initialize vurze with an .env file'
    )
    init_parser.add_argument(
        'env_file',
        type=str,
        nargs='?',
        default='.env',
        help='Path to the .env file (default: .env in current directory)'
    )
    
    # Decorate command
    decorate_parser = subparsers.add_parser(
        'decorate', 
        help='Add decorators to all functions in a Python file'
    )
    decorate_parser.add_argument(
        'file_path', 
        type=str, 
        help='Path to the Python file to decorate'
    )
    
    # Check command
    check_parser = subparsers.add_parser(
        'check', 
        help='Check the integrity of decorators in a Python file'
    )
    check_parser.add_argument(
        'file_path', 
        type=str, 
        help='Path to the Python file to check'
    )

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 1
    
    # Handle init command
    if args.command == 'init':
        return handle_init(args)
    
    # Handle decorate and check commands
    file_path = Path(args.file_path)
    if not file_path.exists():
        print(f"Error: File '{file_path}' does not exist.", file=sys.stderr)
        return 1
    if not file_path.suffix == '.py':
        print(f"Error: File '{file_path}' is not a Python file.", file=sys.stderr)
        return 1
    try:
        if args.command == 'decorate':
            return handle_decorate(args)
        elif args.command == 'check':
            return handle_check(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


def handle_init(args):
    """Handle the init command."""
    try:
        env_path = Path(args.env_file)
        
        # Generate and store keypair (will raise error if keys already exist)
        setup_keypair(env_path)
        print(f"✓ Successfully initialized vurze!")
        print(f"✓ Keypair generated and stored in {env_path}")
        print(f"⚠️  Keep your .env file secure and add it to .gitignore!")
        
        return 0
    except Exception as e:
        print(f"Error during initialization: {e}", file=sys.stderr)
        return 1


def handle_decorate(args):
    """Handle the decorate command."""
    file_path = str(Path(args.file_path).resolve())
    
    try:
        # Add decorators to all functions and classes in the file
        modified_code = add_decorators_to_functions(file_path)
        
        # Write the modified code back to the file
        with open(file_path, 'w') as f:
            f.write(modified_code)
        
        print(f"✓ Successfully added decorators to {file_path}")
        return 0
        
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error while decorating file: {e}", file=sys.stderr)
        return 1


def handle_check(args):
    """Handle the check command."""
    file_path = str(Path(args.file_path).resolve())
    return 1


if __name__ == '__main__':
    sys.exit(main())