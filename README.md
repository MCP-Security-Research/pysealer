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

COMMANDS FOR TESTING CLI
maturin develop --release
vurze --help
```

todo:

- luman art deco implementation for decorators, just adding decorators does not work, i need to verify that code runs the same after they have been added
- lumans art deco needs integrated with both add and remove?
- how does vurze currently handle imports of itself from the cli?? explore???

- create a finalized readme file
- hook up to pypi for first release and set up github actions for publishing / releasing

- make it be able to work with multiple files at once
- ensure tool works with recursive functions and classes. basic test cases using pytest, and also cargo test???
- would a different approach other than ast be faster/more reliable/better?
- start adding tests to make sure tool continues to work
- remove code duplication (consider having one file processing tool, one parser, etc)
- also start to measure the performance of the tool
- use git api to track diffs? (other option is using my own .vurze metadata file)
- update to use ruff to lint python code
- make the tool conform to ruff linting standards
- update to use ____ to lint rust code
- have a code review from professor
