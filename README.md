# pysealer

[![PyPI version](https://img.shields.io/pypi/v/pysealer)](https://pypi.org/project/pysealer/)
[![Python version](https://img.shields.io/pypi/pyversions/pysealer)](https://pypi.org/project/pysealer/)
[![License](https://img.shields.io/github/license/MCP-Security-Research/pysealer)](LICENSE)

> 💡 **Cryptographically sign Python functions and classes for defense-in-depth security**

- 🦀 Built with the [maturin build system](https://www.maturin.rs/) for seamless Rust-Python packaging
- 🐍 Easily installable via pip for quick integration into your Python projects
- 🧩 Leverages Python decorators as cryptographic signatures to ensure code integrity
- 🔏 Powered by [Ed25519](https://docs.rs/ed25519-dalek/latest/ed25519_dalek/) cryptographic signatures

Pysealer helps maintain code integrity by automatically adding `@pysealer._<signature>()` decorators containing signed representations of an underlying Python functions code.

Pysealer takes the unique approach of having Python decorators store checksums that represent function code. By repurposing decorators for a novel use, it ensures that any unauthorized modifications to Python functions are immediately detectable.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Usage](#usage)
3. [How It Works](#how-it-works)
4. [Developer Use Case](#developer-use-case)
5. [Contributing](#contributing)
6. [License](#license)

## Getting Started

```shell
pip install pysealer
# or
uv pip install pysealer
```

## Usage

```shell
pysealer init [OPTIONS] [ENV_FILE]         # Initialize pysealer with an .env file and optionally upload public key to GitHub
pysealer lock <file.py|folder>            # Add decorators to all functions and classes in a Python file or all Python files in a folder
pysealer check <file.py|folder>           # Check the integrity of decorators in a Python file or all Python files in a folder
pysealer remove <file.py|folder>          # Remove pysealer decorators from all functions and classes in a Python file or all Python files in a folder
pysealer --help                           # Show all available commands and options
```

## How It Works

Pysealer ensures the integrity of your Python code by embedding cryptographic signatures into decorators. These signatures act as checksums, making it easy to detect unauthorized modifications. Here's how you can use Pysealer in your workflow:

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

#### 1. Lock the file

```shell
pysealer lock examples/fibonacci.py

Successfully added decorators to 1 file:
  ✓ /path/to/examples/fibonacci.py
```

```python
@pysealer._GnCLaWr9B6TD524JZ3v1CENXmo5Drwfgvc9arVagbghQ6hMH4Aqc8whs3Tf57pkTjsAVNDybviW9XG5Eu3JSP6T()
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
pysealer check examples/fibonacci.py

All decorators are valid in 1 file:
  ✓ /path/to/examples/fibonacci.py
```

#### 3. Modify the code (change return 0 to return 42)

```python
@pysealer._GnCLaWr9B6TD524JZ3v1CENXmo5Drwfgvc9arVagbghQ6hMH4Aqc8whs3Tf57pkTjsAVNDybviW9XG5Eu3JSP6T()
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
pysealer check examples/fibonacci.py

1/1 decorator failed in 1 file:
  ✗ /path/to/examples/fibonacci.py
    Function 'fibonacci' was modified:
      8    def fibonacci(n):
      9        if n <= 0:
      7   -        return 0
      10  +        return 42
      11       elif n == 1:
      12           return 1
```

## Developer Use Case

Pysealer is particularly useful for developers building Model Context Protocol (MCP) servers or agentic applications that rely heavily on Python functions to represent tool calls. For example, it can be integrated into Python codebases that heavily rely on Python functions.

### Step-by-Step Workflow

1. **Initialize Pysealer:** `pysealer init --github-token <PAT_TOKEN_HERE> --hook-mode <MANDATORY_OR_OPTIONAL> --hook-pattern <PATH_DECORATORS_ARE_ADDED_TO>`
   - `--github-token <PAT_TOKEN_HERE>`: Specifies the GitHub Personal Access Token (PAT) to authenticate and upload the public cryptography key to your remote GitHub repository.
   - `--hook-mode <MANDATORY_OR_OPTIONAL>`: Determines whether the pre-commit hook is mandatory (enforced) or optional (can be bypassed).
   - `--hook-pattern <PATH_DECORATORS_ARE_ADDED_TO>`: Defines the file path pattern (e.g., `examples/*.py`) where Pysealer will add decorators and enforce integrity checks.

2. **Lock Your Code:** `pysealer lock <PATH_DECORATORS_ARE_ADDED_TO>`

3. **Set Up CI/CD Integration:** Configure GitHub Actions or another CI/CD pipeline to automate integrity checks and ensure monitoring for unathorized modifications.

### Why Use Pysealer?

The primary use case for Pysealer is to provide defense-in-depth security. Even if a threat actor gains access to your Git repository permissions, they would still need access to the cryptographic keys stored in secure environment files. By adding additional protections to source code, Pysealer adds another trench that threat actors must bypass to perform an upstream attack. Pysealer can also be combined with other security tools to further enhance your application's security.

## Contributing

**🙌 Contributions are welcome!**

Before contributing, make sure to review the [CONTRIBUTING.md](CONTRIBUTING.md) document.

All ideas and contributions are appreciated—thanks for helping make Pysealer better!

## License

Pysealer is licensed under the MIT License. See [LICENSE](LICENSE) for details.
