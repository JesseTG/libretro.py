# Contributing to libretro.py

This document tells you everything you need to know
to submit contributions to `libretro.py`.
It outlines steps for setting up your development environment
and guidelines for submitting pull requests.

# Getting Started

You can install everything you need to contribute to libretro.py with the following steps:

```bash
git clone https://github.com/JesseTG/libretro.py  # Clone the repository
cd libretro.py  # Enter the project directory
python -m venv ./venv  # Create a virtual environment where dependencies will be installed
pip install -v -e .  # Install the project in editable mode
```

Or, if you have `just` installed...

```bash
git clone https://github.com/JesseTG/libretro.py  # Clone the repository
cd libretro.py  # Enter the project directory
just install # Set up a virtual environment, install dependencies, and install the project in editable mode
```