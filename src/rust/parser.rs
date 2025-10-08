/* Automatically add decorators to all functions and classes in a python file. */

use pyo3::prelude::*;
use crate::crypto;

// need to verify vurze has been imported before this is added

#[pyfunction]
pub fn add_decorators_to_functions(py: Python, file_path: &str, decorator: &str) -> PyResult<String> {
    // Import Python's ast module to access AST parsing functionality
    let ast = py.import("ast")?;
    
    // Read the entire file content into a string
    let content = std::fs::read_to_string(file_path)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;
    
    // Parse the Python source code into an Abstract Syntax Tree (AST)
    let tree = ast.call_method1("parse", (content,))?;

    // Create an iterator that will walk through every node in the AST tree
    let walk_iter = ast.call_method1("walk", (tree.clone(),))?;
    
    // Iterate through each node in the AST
    // try_iter() converts the Python iterator into a Rust iterator that can handle errors
    for node in walk_iter.try_iter()? {
        // Extract the current node from the iterator result
        let node = node?;
        // Get the type name of the current AST node
        // Each AST node has a type (e.g., "FunctionDef", "ClassDef", "If", etc.)
        let node_type = node.get_type().name()?;
        
        // Check if this node represents a function or class definition
        // "FunctionDef" = regular function (def function_name():)
        // "AsyncFunctionDef" = asynchronous function (async def function_name():)
        // "ClassDef" = class definition (class ClassName:)
        if node_type == "FunctionDef" || node_type == "AsyncFunctionDef" || node_type == "ClassDef" {

            // Extract the complete source code of this function/class for hashing
            // Step 1: Clone the node to avoid modifying the original
            let node_clone = node.call_method0("__deepcopy__")
                .or_else(|_| {
                    // If deepcopy fails, try to create a copy through unparsing and reparsing
                    let source = ast.call_method1("unparse", (&node,))?;
                    ast.call_method1("parse", (source,))
                })?;
            
            // Step 2: Get decorator_list and filter out vurze decorators
            if let Ok(decorator_list) = node_clone.getattr("decorator_list") {
                // Convert to Rust Vec to manipulate
                let decorators: Vec<PyObject> = decorator_list.extract()?;
                let mut filtered_decorators = Vec::new();
                
                for decorator in decorators {
                    // Get the decorator name
                    let decorator_bound = decorator.bind(py);
                    
                    // Check if decorator is a Name node with id attribute
                    if let Ok(decorator_id) = decorator_bound.getattr("id") {
                        let name: String = decorator_id.extract()?;
                        // Keep decorator if it doesn't start with "vurze"
                        if !name.starts_with("vurze") {
                            filtered_decorators.push(decorator.clone_ref(py));
                        }
                    } else {
                        // If not a simple Name, keep it (could be a decorator with args)
                        filtered_decorators.push(decorator.clone_ref(py));
                    }
                }
                
                // Replace decorator_list with filtered version
                let py_list = pyo3::types::PyList::new(py, &filtered_decorators)?;
                node_clone.setattr("decorator_list", py_list)?;
            }
            
            // Step 3: Convert the filtered node back to source code
            let function_source = ast.call_method1("unparse", (node_clone,))?;
            let source_str: String = function_source.extract()?;
            
            // Step 4: Generate hash of the function/class source code
            let hash = crypto::generate_hash(&source_str);
            
            // Step 5: Create decorator with the hash embedded
            let decorator_with_hash = format!("{}_{}", decorator, hash);

            // Get the decorator_list attribute from the original function node
            if let Ok(decorator_list) = node.getattr("decorator_list") {
                // Create a new AST Name node for the decorator
                let name_node = ast.call_method1("Name", (&decorator_with_hash, ast.getattr("Load")?,))?;
                // Append the decorator to the function's decorator list as the first decorator
                decorator_list.call_method1("insert", (0, name_node))?;
            }
        }
    }
    
    // Convert the modified AST back to Python source code
    let modified_code = ast.call_method1("unparse", (tree,))?;
    let code_str: String = modified_code.extract()?;

    // Return the modified Python code
    Ok(code_str)
}

/* i need a function that will extract all of the decorators from a python file that are named x 
and call the cryptographic function to verify that the hash matches. return true if it does
*/
// pub fn verify_decorators_for_functions()

