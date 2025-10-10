//! Defines the _vurze module which contains all of the Rust code that can be imported into Python.

use pyo3::prelude::*;

mod crypto;

/// Generate a complete signature package for data
/// Returns (hash, signature, public_key) 
#[pyfunction]
fn generate_signature_package(data: &str, private_key_hex: &str) -> PyResult<(String, String, String)> {
    crypto::generate_signature_package(data, private_key_hex)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e))
}

/// Verify a complete signature package
/// Returns true if both the hash matches and the signature is valid
#[pyfunction]
fn verify_signature_package(
    data: &str,
    hash: &str,
    signature: &str,
    public_key: &str,
) -> PyResult<bool> {
    crypto::verify_signature_package(data, hash, signature, public_key)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e))
}

/// _vurze pyo3 module definition
#[pymodule]
fn _vurze(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(generate_signature_package, m)?)?;
    m.add_function(wrap_pyfunction!(verify_signature_package, m)?)?;
    Ok(())
}
