# Development TODOs

- use vurze to automatically add decorators as a vs code extension + vurze as a pre-commmit hook for checking whether decorators are valid?
- use git api to track diffs?

---

- kapfhammer mentioned fort knox for storing secrets? look into mise developer that made it
- dotenv github actions problem luman
- add .env to gitignore automatically???, check if a gitignore exists

- would a different approach other than ast be faster/more reliable/better?
- ensure tool works with recursive functions and classes. basic test cases using pytest, and also cargo test???
- create test cases that ensure that code runs the same after the decorators have been added
- what happens if someone deletes a decorator to a function
- also start to measure the performance of the tool?
- can my tool be attacked by adding soooooo many decorators? like should i create a limit?
- can my tool be used against itself to attack itself
- does my tool remove decorators that are automatically created? like does it clean up after itself properly?
- add tests for multi file

- what sort of attack should i demonstrate? how can I demonstrate this?
- how can my tool be used to prevent this attack? (add clear use cases and descriptions to the readme)
- remove code duplication (consider having one file processing tool, one parser, etc)
- update to use ruff to lint python code
- make the tool conform to ruff linting standards
- you can use maturin's sphinx generation for documentation?
- update to use ____ to lint rust code
- create a standalone install script other than using pip/uv
- add boxes to the readme file. for compatable python versions, for tool version, and more
- have a code review from professor

---

development commands:

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

release commands:

update the version in the init.py file, pyproject.toml, and Cargo.toml files
maturin build --release
git tag v0.1.0
git push origin main --tags

---

x
