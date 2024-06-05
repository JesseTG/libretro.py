# libretro.py

A Python binding for [libretro][libretro] intended for testing cores,
but suitable for any purpose.
Ease of use, flexibility, and complete API support are top priorities.

<div align="center">

[![Workflow Status](https://github.com/JesseTG/libretro.py/actions/workflows/release.yml/badge.svg)](https://github.com/JesseTG/libretro.py/actions/workflows/release.yml)
[![PyPi](https://img.shields.io/pypi/v/libretro.py)](https://pypi.org/project/libretro.py)
[![License](https://img.shields.io/github/license/JesseTG/libretro.py)](LICENSE)

</div>

# Supported Environments

libretro.py has the following requirements:

- Python 3.11 or newer.
  May not work on alternative Python implementations like PyPy.
- Supported on Windows, macOS, and Linux.
  May work on other platforms, but no promises.

Nothing else is required for most functionality,
but some [extra features](#extras) have additional dependencies or constraints.

If contributing then [`just`][just] is optional but recommended,
as it will simplify most development tasks.
For details, run `just` (no arguments) in the project root.

# Installing

libretro.py supports **Python 3.11 or newer**.
Nothing else is required for most functionality,
but some extra features have additional dependencies.

You can install libretro.py with `pip` like so:

```bash
# Install the base libretro.py
pip install libretro.py
```

Using a virtual environment is recommended:

```bash
# Create a virtual environment
python -m venv ./venv

# Activate the virtual environment (in Bash)
source ./venv/bin/activate

# Activate the virtual environment (in PowerShell)
./venv/Scripts/activate.ps1 
```

Or if you have [`just`][just] installed, let it figure out the details for you:

```bash
just venv
```

## Extras

To install additional features,
add one or more of the following extras to the `install` command:

- **`dev`:** Assorted tools used to help develop libretro.py.
  Required if contributing to libretro.py.
- **`opengl`:** Support for the built-in OpenGL video driver.
  Required if testing a core's OpenGL support.
- **`opengl-window`:** Same as the `opengl` extra,
  but with support for opening an actual window.
  Can help simplify some debugging tasks,
  e.g. RenderDoc usage.

For example, if you want to submit an improvement to the OpenGL video driver,
you would install libretro.py like so:

```bash
pip install libretro.py[opengl,dev]
```

And if you just want to test your libretro core's OpenGL support:

```bash
pip install libretro.py[opengl]
```

Some of these extras have additional dependencies.

### OpenGL

If using OpenGL support on Linux,
you may need to install the `libopengl0` package.

[just]: https://just.systems
[libretro]: https://www.libretro.com
