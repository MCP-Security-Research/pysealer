# vurze

Version control your Python functions and classes with automated cryptographic decorator injection.

high level overview:

A python and rust based pypi package that automatically adds decorators to all functions and classses in a python file.
Also supports command line arguments for automatically adding the decoratos, and checking the version of functions
x
Have an decorator for every function and class in a python file ---> py03 rust python language bindings and use the python ast module
The decorator will use some sort of hashing/encryption to ensure both authorship and integrity of the function. i want to make sure that the function has not been tampered with
The private key could be stored in the users .env file
Basically it will act as a checksum to help detect potential security threats
x
For example: @toolname-9875348975
In the end, I would evaluate this based on how it prevents an attack from occuring
Attack → anything that involves changing the functions docstring or underlying code
Ex. Tool Poisoning Attack
ALSO: Could measure performance in the end!!!
ALSO: what should i use to lint and test my rust code?
ALSO: setup and integrate with pypi
how will i deal with env vars?

```text
vurze/
├── Cargo.toml                      # Rust package configuration
├── pyproject.toml                  # Python package metadata
├── README.md
... and so on
```

--------------------------------------------------------

development notes:

```text
COMMANDS I FOLLOWED TO SETUP MATURIN:
uv venv
source .venv/bin/activate
uv tool install maturin
maturin init
select pyo3

COMMANDS I FOLLOWED TO TEST MATURIN INITIALLY:
maturin develop
python -c "import vurze; print('Vurze imported successfully!')"
```

```text
COMMANDS FOR TESTING CLI
maturin develop --release
vurze --help
```

// generate a unique checksum for each function/class
// verify the checksume when called and return true or false
// Ed25519 asymmetric encryption
