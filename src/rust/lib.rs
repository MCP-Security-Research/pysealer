/* Defines the _vurze module which contains the parser and cyrptographic checks. */

use pyo3::prelude::*;

mod parser;
mod crypto;
use parser::add_decorators_to_functions;

/// _vurze pyo3 module definition
#[pymodule]
fn _vurze(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(add_decorators_to_functions, m)?)?;
    Ok(())
}
