# vurze

Version control your Python functions and classes with automated cryptographic decorator injection

> 💡 **code version controls code**

- 🦀 Built with the [maturin build system](https://www.maturin.rs/) for easy Rust-Python packaging
- 🔗 [PyO3](https://pyo3.rs/v0.27.1/index.html) bindings for seamless Python-Rust integration
- 🔏 [Ed25519](https://docs.rs/ed25519-dalek/latest/ed25519_dalek/) signatures to ensure code integrity and authorship
- 🖥️ [Typer](https://typer.tiangolo.com/) for a clean and user-friendly command line interface

vurze helps you maintain code integrity by automatically adding cryptographic signatures to your Python functions and classes. Each function or class receives a unique decorator containing a cryptographic signature that verifies both authorship and integrity, making it easy to detect unauthorized code modifications.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Usage](#usage)
3. [How It Works](#how-it-works)
4. [Use Cases](#use-cases)
5. [Contributing](#contributing)
6. [License](#license)

## Getting Started

```shell
pip install vurze
# or
uv pip install vurze
```

## Usage

```shell
vurze init [ENV_FILE]         # Initialize the vurze tool by generating and saving keys to an ENV_FILE (default: .env)
vurze decorate <file.py>      # Add cryptographic decorators to all functions/classes in <file.py>
vurze check <file.py>         # Verify the integrity and validity of vurze decorators in <file.py>
vurze remove <file.py>        # Remove all vurze decorators from <file.py>
vurze --help                  # Show all available commands and options
```

## How It Works

vurze works by automatically injecting cryptographic decorators into your Python functions and classes. Here’s how the process works:

### Step-by-Step Example

Suppose you have a file `fibonacci.py`:

```python
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
```

#### 1. Decorate the file

```shell
$ vurze decorate fibonacci.py
Successfully added decorators to fibonacci.py
```

```python
@vurze._GnCLaWr9B6TD524JZ3v1CENXmo5Drwfgvc9arVagbghQ6hMH4Aqc8whs3Tf57pkTjsAVNDybviW9XG5Eu3JSP6T()
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
```

#### 2. Check integrity

```shell
$ vurze check fibonacci.py
All decorators are valid!
```

#### 3. Tamper with the code (change return 0 to return 42)

```python
@vurze._GnCLaWr9B6TD524JZ3v1CENXmo5Drwfgvc9arVagbghQ6hMH4Aqc8whs3Tf57pkTjsAVNDybviW9XG5Eu3JSP6T()
def fibonacci(n):
    if n <= 0:
        return 42
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
```

#### 4. Check again

```shell
$ vurze check fibonacci.py
✗ 1 decorator(s) failed verification!
```

## Use Cases

- **Version controlling MCP servers:**
  - Ensure that all code running on MCP servers is cryptographically signed and verifiable, preventing unauthorized changes and maintaining a trusted execution environment.
  - Detect and block tampered or malicious code before it is executed, reducing the risk of upstream supply chain attacks.

## Contributing

**🙌 Contributions are welcome!**

If you have suggestions, bug reports, or want to help improve vurze, feel free to open an [issue](https://github.com/MCP-Security-Research/vurze/issues) or submit a pull request.

All ideas and contributions are appreciated—thanks for helping make vurze better!

## License

vurze is licensed under the MIT License. See [LICENSE](LICENSE) for details.
