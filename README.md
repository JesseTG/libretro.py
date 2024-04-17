# libretro.py

A Python binding for [libretro][libretro] intended for testing cores,
but suitable for any purpose.
Ease of use, flexibility, and complete API support are top priorities.

<div align="center">

[![Build Status](https://github.com/JesseTG/libretro.py/workflows/build/badge.svg)](https://github.com/JesseTG/libretro.py/actions)
[![PyPi](https://img.shields.io/pypi/v/PROJECT_NAME_URL)](https://pypi.org/project/PROJECT_NAME_URL)
[![License](https://img.shields.io/github/license/JesseTG/libretro.py)](LICENSE)

</div>

# Supported Environments

libretro.py has the following requirements:

- Python 3.10 or newer.
  May not work on alternative Python implementations like PyPy.
- Supported on Windows, macOS, and Linux.
  May work on other platforms, but no promises.

Nothing else is required for most functionality,
but some [extra features](#extras) have additional dependencies or constraints.

If contributing then [`just`][just] is optional but recommended,
as it will simplify most development tasks.
For details, run `just` (no arguments) in the project root.

# Installing

libretro.py supports **Python 3.10 or newer**.
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
- **`pillow`:** Support for the built-in software-only video driver
  powered by the [Pillow][pillow] image processing library.
  Not required for any particular feature,
  but it simplifies tests that inspect the core's video output.

For example, if you want to submit an improvement to the Pillow video driver,
you would install libretro.py like so:

```bash
pip install libretro.py[pillow,dev]
```

And if you just want to test your libretro core's OpenGL support:

```bash
pip install libretro.py[opengl]
```

[just]: https://just.systems
[libretro]: https://www.libretro.com
[pillow]: https://python-pillow.org
