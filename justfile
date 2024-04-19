set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# To use a specific Python interpreter, set the `python` variable to the path of the interpreter,
# e.g. "just --set python /usr/bin/python3.11 variables"
python := "python"
venv := "venv"
_venv_bin := venv / "Scripts"
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
    {{_venv_bin}}/bandit -r src

# Builds the project in preparation for release
build: venv
    {{_venv_bin}}/python -m build

# Runs the Black Python formatter against the project
black: venv
    {{_venv_bin}}/black src

# Checks if the project is formatted correctly against the Black rules
black-check: venv
    {{_venv_bin}}/black src --check

# Cleans the project
clean:
    git clean -xdf

# Run flake8 checks against the project
flake8: venv
    {{_venv_bin}}/flake8 src

# Lints the project
lint: black-check isort-check flake8 mypy bandit

# Runs all formatting tools against the project
lint-fix: black isort

# Install the project locally
install: venv
    {{_venv_bin}}/pip install -v -e .

# Sorts imports throughout the project
isort: venv
    {{_venv_bin}}/isort src

# Checks that imports throughout the project are sorted correctly
isort-check: venv
    {{_venv_bin}}/isort src --check-only

# Run mypy type checking on the project
mypy: venv
    {{_venv_bin}}/mypy src

# Create a virtual environment if necessary
[windows]
venv:
    if (-Not (Test-Path {{venv}})) { {{python}} -m venv {{venv}} }

[unix]
venv:
    [ -d {{venv}} ] || {{python}} -m venv {{venv}}
