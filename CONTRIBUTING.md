# Contributing to Pysealer

Thank you for your interest in contributing to Pysealer! We welcome contributions of all kinds, including bug fixes, feature enhancements, documentation improvements, and more. Please follow the guidelines below to ensure a smooth contribution process.

## Getting Started

To get started developing Pysealer, follow these steps:

1. **Fork the Repository**: Start by forking the Pysealer repository to your GitHub account.
2. **Clone Your Fork**: Clone your forked repository to your local machine:
   ```bash
   git clone https://github.com/<your-username>/pysealer.git
   ```
3. **Set Up a Virtual Environment**: Use `uv` to create and activate a virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate
   ```
4. **Install Dependencies**: Install the required dependencies:
   ```bash
   uv tool install maturin
   ```

## Running Pysealer Locally

To run Pysealer locally, follow these steps:

1. Build the project:
   ```bash
   maturin develop --release
   ```
2. Run any pysealer command:
   ```bash
   pysealer --help
   ```

## Making Releases to Pysealer

To make a release for Pysealer, follow these steps:

1. Update the version in the following files:
   - `__init__.py`
   - `pyproject.toml`
   - `Cargo.toml`

2. Build the project for release:
   ```bash
   maturin build --release
   ```

3. Create a new Git tag for the release:
   ```bash
   git tag v0.1.0
   ```

4. Push the changes and tags to the remote repository:
   ```bash
   git push origin main --tags
   ```

## Development Workflow

When working on Pysealer, follow these steps:

- **Code Changes**: Make your changes in a new branch:
  ```bash
  git checkout -b feature/your-feature-name
  ```
- **Testing**: Ensure all tests pass before submitting your changes. Run Python tests with `pytest` and Rust tests with `cargo test`.
- **Linting**: Use `ruff` to lint Python code and ensure it conforms to the project's standards. For Rust code, use the appropriate linter (to be determined).
- **Commit Messages**: Write clear and concise commit messages. Follow the format:
  ```
  feat: Add new feature
  fix: Fix a bug
  docs: Update documentation
  ```
- **Push Changes**: Push your branch to your forked repository:
  ```bash
  git push origin feature/your-feature-name
  ```
- **Create a Pull Request**: Open a pull request to the `main` branch of the original repository. Follow the Pull request format specified below.

## Issue Format

When creating an issue, please follow this format to ensure clarity and consistency:

```text
[feat/bug/docs/question] short description of the issue

Description:
- What is the issue or feature request?
- Steps to reproduce (if applicable)
- Expected behavior vs. actual behavior (if applicable)
- Any additional context or screenshots

Environment:
- Python version: <e.g., 3.10>
- Operating system: <e.g., macOS 12>
- Pysealer version: <e.g., 0.8.9>

Linked Pull Requests (if any): #<PR-number>
```

## Pull Request Format

When creating a pull request, please follow this format to ensure clarity and consistency:

```text
[feat/fix/docs] short description of the change

Description:
- What does this PR do?
- Why is this change necessary?
- Are there any dependencies or prerequisites?
- Add any other supporting information here.

Review Process: Describe how this PR can be reviewed?

Linked Issues: Closes #<issue-number>
```

## Future Work Ideas

- Integrate the fnox secrets tool for secrets management. This will improve secret management, making it easier to share Pysealer private and public keys among multiple developers.
- Fix `ruff` linting errors in the current project to ensure Python code adheres to the project's standards.
- Add a Rust-based linter to enforce consistent coding standards for the Rust codebase.
- Increase test coverage by adding more tests for the Python implementation of the tool.
- Ensure compatibility with `ruff` by resolving any existing issues and maintaining compliance.
- Explore using Maturin's Sphinx integration to generate comprehensive documentation for the project.

Thank you for contributing to Pysealer! Your efforts help make this project better for everyone.
