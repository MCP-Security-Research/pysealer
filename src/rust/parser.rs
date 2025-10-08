/* Automatically add decorators to all functions and classes in a python file. */

use pyo3::prelude::*;

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
            // Get the decorator_list attribute from the function node
            if let Ok(decorator_list) = node.getattr("decorator_list") {
                // Create a new AST Name node for the decorator
                let name_node = ast.call_method1("Name", (decorator, ast.getattr("Load")?,))?;
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
