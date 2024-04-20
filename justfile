set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# To use a specific Python interpreter, set the `python` variable to the path of the interpreter,
# e.g. "just --set python /usr/bin/python3.11 variables"
python := "python"

# The OS name is appended to the venv dir
# in case you're developing in an environment that exposes this directory
# to multiple OSes (e.g. WSL)
venv := "venv-" + os()
_venv_bin := if os_family() == "windows" { venv / "Scripts" } else { venv / "bin" }

# List all available recipes.
list:
    @{{just_executable()}} --list

# List all variables that can be used to configure the recipes. (_leading_underscores are private)
vars:
    @{{just_executable()}} --evaluate

# Show the help for just itself
help:
    @{{just_executable()}} --help

# Scans the project for security vulnerabilities
bandit: _validate_venv
    {{_venv_bin}}/bandit -r src

# Builds the project in preparation for release
build: install
    {{_venv_bin}}/python -m build

# Runs the Black Python formatter against the project
black: _validate_venv
    {{_venv_bin}}/black src docs setup.py

# Checks if the project is formatted correctly against the Black rules
black-check: _validate_venv
    {{_venv_bin}}/black src docs setup.py --check

# Cleans the project
clean:
    git clean -xdf

# Run flake8 checks against the project
flake8: _validate_venv
    {{_venv_bin}}/flake8 src

# Lints the project
lint: black-check isort-check flake8 mypy bandit

# Runs all formatting tools against the project
lint-fix: black isort

# Install the project locally and install all dependencies
install: venv
    {{_venv_bin}}/pip install --editable ".[all]"

# Sorts imports throughout the project
isort: _validate_venv
    {{_venv_bin}}/isort src

# Checks that imports throughout the project are sorted correctly
isort-check: _validate_venv
    {{_venv_bin}}/isort src --check-only

# Run mypy type checking on the project
mypy: _validate_venv
    {{_venv_bin}}/mypy src

# Generate the documentation and serve it locally. View it in a web browser.
serve-docs: _validate_venv
    {{_venv_bin}}/sphinx-autobuild -j auto --ignore "./docs/libretro/*" --keep-going docs build/doc --watch src

[private]
[windows]
_validate_venv:
    @if (-Not (Test-Path {{venv}})) { throw "Virtual environment not found. Run `just install` to create it." }

[private]
[unix]
_validate_venv:
    @[ -d {{venv}} ] || { echo "Virtual environment not found. Run 'just install' to create it."; exit 1; }

# Create a virtual environment if necessary
[windows]
venv:
    if (-Not (Test-Path {{venv}})) { {{python}} -m venv {{venv}} }

[unix]
venv:
    [ -d {{venv}} ] || {{python}} -m venv {{venv}}
