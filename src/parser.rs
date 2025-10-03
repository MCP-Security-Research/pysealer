// parsing ast tree file
use pyo3::prelude::*;

/// Extract function names from a Python file using Python's ast module.
#[pyfunction]
pub fn get_functions_from_file(py: Python, file_path: &str) -> PyResult<Vec<String>> {
    // Import Python's ast module to access AST parsing functionality
    // The ? operator propagates any import errors up to the caller
    let ast = py.import("ast")?;
    
    // Read the entire file content into a string
    // std::fs::read_to_string reads the file at the given path and returns the content as a String
    // map_err converts the std::io::Error into a PyIOError that Python can understand
    let content = std::fs::read_to_string(file_path)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;
    
    // Parse the Python source code into an Abstract Syntax Tree (AST)
    // ast.parse() converts the raw Python source code string into a structured tree
    // representation that we can programmatically analyze
    // call_method1 calls the Python method "parse" with one argument (the content)
    let tree = ast.call_method1("parse", (content,))?;
    
    // Initialize a vector to store the function names we discover
    let mut function_names = Vec::new();
    
    // Create an iterator that will walk through every node in the AST tree
    // ast.walk() is a Python generator that yields every node in the tree in depth-first order
    // This allows us to examine each node without having to implement our own tree traversal
    let walk_iter = ast.call_method1("walk", (tree,))?;
    
    // Iterate through each node in the AST
    // try_iter() converts the Python iterator into a Rust iterator that can handle errors
    for node in walk_iter.try_iter()? {
        // Extract the current node from the iterator result
        // The ? operator handles any errors that occur during iteration
        let node = node?;
        
        // Get the type name of the current AST node
        // Each AST node has a type (e.g., "FunctionDef", "ClassDef", "If", etc.)
        // get_type().name()? retrieves this type information as a string
        let node_type = node.get_type().name()?;
        
        // Check if this node represents a function definition
        // "FunctionDef" = regular function (def function_name():)
        // "AsyncFunctionDef" = asynchronous function (async def function_name():)
        if node_type == "FunctionDef" || node_type == "AsyncFunctionDef" {
            // Attempt to extract the function name from the node
            // getattr("name") accesses the 'name' attribute of the function node
            // We use if let Ok(...) because not all nodes may have a name attribute
            if let Ok(name) = node.getattr("name") {
                // Convert the Python string object to a Rust String
                // extract() performs the type conversion from Python object to Rust type
                let name_str: String = name.extract()?;
                
                // Add the function name to our collection
                function_names.push(name_str);
            }
        }
    }
    
    // Return the collected function names wrapped in Ok()
    // This indicates successful completion of the function
    Ok(function_names)
}

// add decorator function --> 