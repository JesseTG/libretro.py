"""
Higher-level Python utilities built on top of :mod:`libretro.api` and :mod:`libretro.drivers`,
each of which can be run as a standalone module.

=======================
Additional Dependencies
=======================

You'll need to install the ``cli`` extra to run these scripts, like so:

.. code-block::

    pip install libretro.py[cli]


============================
Running the Built-In Scripts
============================

All included scripts can be run with ``python -m``, like so:

.. code-block::

    python -m libretro.py.system_info mycore_libretro.dll
"""

# Some notes for writing docs for the CLI scripts:
#
# - Use _common for CLI helper functions and types
# - Use list | None for multi-valued arguments, not tuple[T, ...]
#   ("..." makes Sphinx choke -- or maybe one of its extensions, not sure)
# - The module docstring should is shown in the doc site as a one-sentence synopsis
# - The main function docstring in each module is shown as the CLI's --help
#   (you can use semantic linebreaks, they won't affect the output)
# - Each standalone module must export a Click command named ("command")
#   so the sphinx_click extension can render a page on the doc site.
#   (Typer is a wrapper around Click, so that's okay.)
