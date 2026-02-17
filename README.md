# pysealer

[![PyPI version](https://img.shields.io/pypi/v/pysealer?cacheSeconds=0)](https://pypi.org/project/pysealer/)
[![Python version](https://img.shields.io/pypi/pyversions/pysealer?cacheSeconds=0)](https://pypi.org/project/pysealer/)[![License](https://img.shields.io/github/license/MCP-Security-Research/pysealer)](LICENSE)

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

Pysealer is particularly useful for developers building Model Context Protocol (MCP) servers or agentic applications that rely heavily on Python functions to represent tool calls. Pysealer's intended and reccommended use is for Python codebases that heavily rely on Python functions.

### Step-by-Step Workflow

#### Create a GitHub Personal Access Token (PAT)

To use Pysealer effectively with GitHub Actions and remote repository secrets, you need to generate a [GitHub Personal Access Token (PAT)](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) with the appropriate permissions. Follow these steps:

1. **Navigate to GitHub Developer Settings**
   - Click on your profile picture in the top-right corner.
   - Select **Settings** from the dropdown menu.
   - Scroll down and click on **Developer settings** in the left-hand sidebar.
   - Under **Developer settings**, click on **Personal access tokens**.
   - Select **Fine-grained tokens**.

2. **Generate a New Token**
   - Click the **Generate new token** button.
   - Provide a **token name** and **note** to describe the purpose of the token (e.g., "Pysealer CI/CD Integration").
   - Set the resource owner and an **expiration date** for the token (e.g., 90 days, or choose "No expiration" if you prefer).
   - Select the repository you wish to set up Pysealer for.
   - Under **Select scopes**, check the following permissions:
     - **`Actions`**: Access to GitHub Actions workflows.
     - **`Secrets`**: Manage repository secrets.
     - Additional scopes may be required depending on your use case.
   - **Copy the token immediately** and save it securely (e.g., in a password manager or `.env` file). You won’t be able to see it again. You can use this token in the terminal to set up Pysealer.

#### Initialize Pysealer

To initialize Pysealer, use the following command:

```bash
pysealer init --github-token <PAT_TOKEN_HERE> --hook-mode <MANDATORY_OR_OPTIONAL> --hook-pattern <PATH_DECORATORS_ARE_ADDED_TO>
```

- `--github-token <PAT_TOKEN_HERE>`: Specifies the GitHub Personal Access Token (PAT) to authenticate and upload the public cryptography key to your remote GitHub repository.
- `--hook-mode <MANDATORY_OR_OPTIONAL>`: Determines whether the pre-commit hook is mandatory (enforced) or optional (can be bypassed).
- `--hook-pattern <PATH_DECORATORS_ARE_ADDED_TO>`: Defines the file path pattern (e.g., `examples/*.py`) where Pysealer will add decorators and enforce integrity checks.

#### Pysealer Pre-commit Hook

When you run the `pysealer init` command, a pre-commit hook is automatically set up in your Git repository. This hook ensures that your code is sealed with cryptographic decorators before it is committed and pushed to a remote repository. The pre-commit hook runs the `pysealer lock` command on the specified files or directories, adding the necessary decorators to maintain code integrity.

To bypass the pre-commit hook, you can use the `-n` flag with the `git commit` command:

```shell
git commit -n -m "Bypass pre-commit hook for emergency fix"
```

To remove the the pre-commit hook generated by pysealer, you can use this command:

```shell
rm -f .git/hooks/pre-commit
```

#### Lock Your Code

To lock your code and add cryptographic decorators for the first time, use the following command:

```bash
pysealer lock <PATH_DECORATORS_ARE_ADDED_TO>
```

#### Set Up CI/CD Integration

To automate integrity checks and monitor for unauthorized modifications, configure GitHub Actions or another CI/CD pipeline. Below is an example configuration for GitHub Actions:

```yaml
name: Pysealer Security Check

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'examples/**'
  pull_request:
    branches: [ main, develop ]
    paths:
      - 'examples/**'

jobs:
  pysealer-check:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.13'

    - name: Install pysealer
      run: |
        python -m pip install --upgrade pip
        pip install pysealer==0.8.9

    - name: Run pysealer check
      env:
          PYSEALER_PUBLIC_KEY: ${{ secrets.PYSEALER_PUBLIC_KEY }}
      run: |
        pysealer check examples
```

### Why Use Pysealer?

The primary use case for Pysealer is to provide defense-in-depth security. Even if a threat actor gains access to your Git repository permissions, they would still need access to the cryptographic keys stored in secure environment files. By adding additional protections to source code, Pysealer adds another trench that threat actors must bypass to perform an upstream attack. Pysealer can also be combined with other security tools to further enhance your application's security.

## Contributing

**🙌 Contributions are welcome!**

Before contributing, make sure to review the [CONTRIBUTING.md](CONTRIBUTING.md) document.

All ideas and contributions are appreciated—thanks for helping make Pysealer better!

## License

Pysealer is licensed under the MIT License. See [LICENSE](LICENSE) for details.
