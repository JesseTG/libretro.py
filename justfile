set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# To use a specific Python interpreter, set the `python` variable to the path of the interpreter,
# e.g. "just --set python /usr/bin/python3.11 variables"
python := "python"
VIRTUAL_ENV := "venv"
VIRTUAL_BIN := VIRTUAL_ENV / "Scripts"
TEST_DIR := "test"

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
bandit: venv
    {{VIRTUAL_BIN}}/bandit -r src

# Builds the project in preparation for release
build: venv
    {{VIRTUAL_BIN}}/python -m build

# Runs the Black Python formatter against the project
black: venv
    {{VIRTUAL_BIN}}/black src

# Checks if the project is formatted correctly against the Black rules
black-check: venv
    {{VIRTUAL_BIN}}/black src --check

# Cleans the project
clean:
    git clean -xdf

# Run flake8 checks against the project
flake8: venv
    {{VIRTUAL_BIN}}/flake8 src

# Lints the project
lint: black-check isort-check flake8 mypy bandit

# Runs all formatting tools against the project
lint-fix: black isort

# Install the project locally
install: venv
    {{VIRTUAL_BIN}}/pip install -v -e .

# Sorts imports throughout the project
isort: venv
    {{VIRTUAL_BIN}}/isort src

# Checks that imports throughout the project are sorted correctly
isort-check: venv
    {{VIRTUAL_BIN}}/isort src --check-only

# Run mypy type checking on the project
mypy: venv
    {{VIRTUAL_BIN}}/mypy src

# Create a virtual environment if necessary
[windows]
venv:
    if (-Not (Test-Path {{VIRTUAL_ENV}})) { {{python}} -m venv {{VIRTUAL_ENV}} }

[unix]
venv:
    [ -d {{VIRTUAL_ENV}} ] || {{python}} -m venv {{VIRTUAL_ENV}}
