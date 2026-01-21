//! Defines the _pysealer module which contains all of the Rust code that can be imported into Python.

use pyo3::prelude::*;

mod crypto;

/// Generate a new Ed25519 key pair
/// Returns (private_key_hex, public_key_hex)
#[pyfunction]
fn generate_keypair() -> (String, String) {
    crypto::generate_keypair()
}

/// Sign data using Ed25519 with a private key
/// Returns the signature as a hex string
#[pyfunction]
fn generate_signature(data: &str, private_key_hex: &str) -> PyResult<String> {
    crypto::generate_signature(data, private_key_hex)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e))
}

/// Verify an Ed25519 signature
/// Returns true if the signature is valid
#[pyfunction]
fn verify_signature(data: &str, signature_hex: &str, public_key_hex: &str) -> PyResult<bool> {
    crypto::verify_signature(data, signature_hex, public_key_hex)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e))
}

/// _pysealer pyo3 module definition
#[pymodule]
fn _pysealer(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(generate_keypair, m)?)?;
    m.add_function(wrap_pyfunction!(generate_signature, m)?)?;
    m.add_function(wrap_pyfunction!(verify_signature, m)?)?;
    Ok(())
}
