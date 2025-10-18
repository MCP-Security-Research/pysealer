"""Automatically add cryptographic decorators to all functions and classes in a python file."""

import ast
import copy
from vurze import generate_signature
from .setup import get_private_key

def add_decorators_to_functions(file_path: str) -> str:
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
    
    # Parse the Python source code into an Abstract Syntax Tree (AST)
    tree = ast.parse(content)
    
    # Iterate through each node in the AST
    # ast.walk() returns an iterator that yields every node in the tree
    for node in ast.walk(tree):
        # Get the type name of the current AST node
        # Each AST node has a type (e.g., "FunctionDef", "ClassDef", "If", etc.)
        node_type = type(node).__name__
        
        # Check if this node represents a function or class definition
        # "FunctionDef" = regular function (def function_name():)
        # "AsyncFunctionDef" = asynchronous function (async def function_name():)
        # "ClassDef" = class definition (class ClassName:)
        if node_type in ("FunctionDef", "AsyncFunctionDef", "ClassDef"):
            
            # Extract the complete source code of this function/class for hashing
            # Step 1: Create a deep copy of the node to avoid modifying the original
            node_clone = copy.deepcopy(node)
            
            # Step 2: Get decorator_list and filter out vurze decorators
            if hasattr(node_clone, 'decorator_list'):
                filtered_decorators = []
                
                for decorator in node_clone.decorator_list:
                    should_keep = True
                    
                    # Check if decorator is a simple Name node starting with "vurze"
                    if isinstance(decorator, ast.Name):
                        if decorator.id.startswith("vurze"):
                            should_keep = False
                    
                    # Check if decorator is an Attribute node (e.g., vurze.something)
                    elif isinstance(decorator, ast.Attribute):
                        if isinstance(decorator.value, ast.Name) and decorator.value.id == "vurze":
                            should_keep = False
                    
                    # Check if decorator is a Call node
                    elif isinstance(decorator, ast.Call):
                        func = decorator.func
                        # Check if call is to vurze.something()
                        if isinstance(func, ast.Attribute):
                            if isinstance(func.value, ast.Name) and func.value.id == "vurze":
                                should_keep = False
                        # Check if call is to vurze_something()
                        elif isinstance(func, ast.Name) and func.id.startswith("vurze"):
                            should_keep = False
                    
                    if should_keep:
                        filtered_decorators.append(decorator)
                
                # Replace decorator_list with filtered version
                node_clone.decorator_list = filtered_decorators
            
            # Step 3: Convert the filtered node back to source code
            # Wrap in a Module for proper unparsing
            module_wrapper = ast.Module(body=[node_clone], type_ignores=[])
            function_source = ast.unparse(module_wrapper)
            
            # Step 4: Generate hash and signature of the function/class source code
            # Get the private key from .env file
            try:
                private_key = get_private_key()
            except (FileNotFoundError, ValueError) as e:
                raise RuntimeError(f"Cannot add decorators: {e}. Please run 'vurze init' first.")
            
            # Generate cryptographic signature of the source code
            try:
                signature = generate_signature(function_source, private_key)
            except Exception as e:
                raise RuntimeError(f"Failed to generate signature: {e}")
            
            # Step 5: Create decorator with the signature as the function name
            # Format: @vurze._<signature>()
            # Get the decorator_list attribute from the original function node
            if hasattr(node, 'decorator_list'):
                # Create AST nodes for: vurze._<signature>()
                # This builds: Attribute(value=Name('vurze'), attr='_<signature>')
                vurze_name = ast.Name(id='vurze', ctx=ast.Load())
                # Use underscore prefix followed by the signature as the attribute name
                signature_attr = ast.Attribute(value=vurze_name, attr=f'_{signature}', ctx=ast.Load())
                
                # Create the call node: vurze._<signature>()
                call_node = ast.Call(
                    func=signature_attr,
                    args=[],
                    keywords=[]
                )
                
                # Insert the decorator at the beginning of the decorator list
                node.decorator_list.insert(0, call_node)
    
    # Convert the modified AST back to Python source code
    modified_code = ast.unparse(tree)
    
    # Return the modified Python code
    return modified_code
