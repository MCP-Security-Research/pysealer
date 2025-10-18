# Vurze

Version control your Python functions and classes with automated cryptographic decorator injection

- ⚡️ **Lightning Fast** - Built with Rust for maximum performance
- 🔐 **Cryptographic Security** - Ed25519 signatures ensure code integrity and authorship
- 🛠️ **CLI & Library** - Use as a command-line tool or import as a Python package
- 🔍 **Attack Detection** - Automatically detects tampering with function code or docstrings
- 📦 **PyO3 Powered** - Seamless Python-Rust integration via PyO3 bindings

vurze helps you maintain code integrity by automatically adding cryptographic signatures to your Python functions and classes. Each function receives a unique decorator containing a cryptographic signature that verifies both authorship and integrity, making it easy to detect tool poisoning attacks and unauthorized code modifications.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [How It Works](#how-it-works)
4. [CLI Commands](#cli-commands)
5. [Configuration](#configuration)
6. [Usage](#usage)
7. [CI/CD Pipeline Integration](#cicd-pipeline-integration)
8. [Contributing](#contributing)
9. [License](#license)

## Installation

x

## Quick Start

x

## How It Works

x

## CLI Commands

x

## Configuration

x

## Usage

mcp content here

## CI/CD Pipeline Integration

x

## Contributing

x

## License

vurze is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

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

challenges:
crypto system
storing private key in env var --> user sets the path to the var via the cli
spacing issues when changed

one decorator that looks like this: vurze.protect(x)
or
multiple decorators that look like this: @vurze.x(), @vurze.x()

you dont actually need hashing, it could be added for performance reasons though. consistent 32 byte input to ed25519 signing function

if i hash, i wouldnt be able to look at the diffs of the functions? how can i build a system that allows me to report exactly what changed in the function?

instead of tracking my own diffs, i could just use git history to retrieve source code? or i could use my own standalone metadata file?

problems:

- cryptography
- what decorators look like
- how can i ensure that i can detect and report diffs correctly

console print
and ruff for linting code
should i lint my rust code?
ill probobly have to fix my import paths for python at some point
fix recursive function calls. is there a more reliable way to change the code
