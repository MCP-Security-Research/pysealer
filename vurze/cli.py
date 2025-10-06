#!/usr/bin/env python3
"""
Command-line interface for vurze.

Provides commands:
- vurze decorate <python_file_path>: Add decorators to functions in a Python file
- vurze check <python_file_path>: Check the integrity of decorators in a Python file
"""

import argparse
import sys
import os
from pathlib import Path

from . import add_decorators_to_functions


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="vurze",
        description="Version control your Python functions with cryptographic decorators"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
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
    decorate_parser.add_argument(
        '--decorator', 
        type=str, 
        default='@vurze_protected',
        help='Decorator name to add (default: @vurze_protected)'
    )
    decorate_parser.add_argument(
        '--output', 
        type=str, 
        help='Output file path (default: overwrites input file)'
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
    
    # Validate file path
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


def handle_decorate(args):
    """Handle the decorate command."""
    file_path = str(Path(args.file_path).resolve())
    decorator = args.decorator.lstrip('@')  # Remove @ if provided
    
    try:
        # Call the Rust function to add decorators
        modified_content = add_decorators_to_functions(file_path, f"@{decorator}")
        
        # Determine output path
        output_path = args.output if args.output else file_path
        
        # Write the modified content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        print(f"Successfully added decorators to '{file_path}'")
        if args.output and args.output != file_path:
            print(f"Output written to '{args.output}'")
        
        return 0
        
    except Exception as e:
        print(f"Failed to decorate file: {e}", file=sys.stderr)
        return 1


def handle_check(args):
    """Handle the check command."""
    file_path = str(Path(args.file_path).resolve())
    
    # TODO: Implement integrity checking logic
    # This will need additional Rust functions for:
    # 1. Parsing existing decorators
    # 2. Verifying checksums/signatures
    # 3. Detecting modifications
    
    print(f"Checking integrity of '{file_path}'...")
    print("Note: Check functionality is not yet implemented.")
    print("This will verify decorator integrity and detect function modifications.")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())