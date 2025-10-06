use pyo3::prelude::*;

mod parser;
use parser::add_decorators_to_functions;

/// A Python module implemented in Rust.
#[pymodule]
#[pyo3(name = "_vurze")]
fn vurze_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(add_decorators_to_functions, m)?)?;
    Ok(())
}



/*
example python code that does this: 

import os
import ast
import sys
import inspect

from graffito import graffiti

def emboss(elem: callable, name: str = "", checksum: str = ""):
    if os.path.exists(elem):
        src = open(elem, "r").read()
    else:
        src = inspect.getsource(elem)
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.ClassDef):
            if name == node.name:
                node.decorator_list.append(ast.Name(checksum))
    mod = ast.unparse(tree)
*/

/*
├── src/                            # Rust source code
│   ├── lib.rs                      # Main library entry, PyO3 bindings --> this is the main file
│   ├── cli.rs                      # Clap CLI implementation --> cli logic
│   ├── parser.rs                   # Python AST parsing logic --> parser logic for extracting all functions and classes.
│   ├── decorator.rs                # Decorator injection logic --> logic for injecting decorators!!!
│   ├── crypto.rs                   # Asymmetric encryption/verification --> logic for generating uniuque checksums and storing them

├── tests/
│   ├── test_parser.rs              # Rust unit tests
│   ├── test_crypto.rs
│   ├── test_cli.rs
│   └── test_integration.py         # Python integration tests
*/