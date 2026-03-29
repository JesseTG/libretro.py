set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# To use a specific Python interpreter, set the `python` variable to the path of the interpreter,
# e.g. "just --set python /usr/bin/python3.11 variables"

python := "python"

# The OS name is appended to the venv dir
# in case you're developing in an environment that exposes this directory
# to multiple OSes (e.g. WSL)

default_venv := "venv-" + os()

# List all available recipes.
list:
    @{{ just_executable() }} --list

# List all variables that can be used to configure the recipes. (_leading_underscores are private)
vars:
    @{{ just_executable() }} --evaluate

# Show the help for just itself
help:
    @{{ just_executable() }} --help

# Scans for security vulnerabilities
[group('Linting')]
bandit:
    bandit -c pyproject.toml -r src

# Builds a release for libretro.py
[group('Getting Started')]
build: install
    python -m build

# Runs the Black Python formatter against the project
[group('Linting')]
black:
    black src docs setup.py

# Checks if libretro.py is formatted correctly against the Black rules
[group('Linting')]
black-check:
    black src docs setup.py --check

# Cleans the project
clean:
    git clean -xdf

# Runs all other checks in this section
[group('Linting')]
lint: black-check isort-check pyright bandit

# Runs all formatting tools against the project
[group('Linting')]
lint-fix: black isort

# Install libretro.py locally, including all optional dependencies, and set up pre-commit hooks
[group('Getting Started')]
install:
    pip install --editable ".[all]"
    pre-commit install

# Sorts imports throughout the project
[group('Linting')]
isort:
    isort src

# Checks that imports throughout the project are sorted correctly
[group('Linting')]
isort-check:
    isort src --check-only

# Type-check libretro.py
[group('Linting')]
pyright:
    pyright --version
    pyright --project .

# Generate the documentation and serve it locally. View it in a web browser.
serve-docs:
    sphinx-autobuild --jobs auto --ignore "./docs/api/*" --builder dirhtml --keep-going --watch src docs build/doc

# Create a virtual environment
[group('Getting Started')]
[windows]
venv name=default_venv:
    if (-Not (Test-Path {{ name }})) { {{ python }} -m venv {{ name }} }

[group('Getting Started')]
[unix]
venv name=default_venv python=python:
    [ -d {{ name }} ] || python -m venv {{ name }}
