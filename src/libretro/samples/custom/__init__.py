"""
Sample cores written specifically for libretro.py's test suite.

These cores are small, focused C libraries that exercise a single libretro
driver protocol or env-call cluster. They have no upstream counterpart
and are built from sources in ``cores/custom/`` in the libretro.py
repository.

.. seealso::

    :mod:`libretro.samples`
        Overview of all sample-core categories and their lazy-loading semantics.
"""

from libretro.samples._loader import load_sample_core

_NAMES = ("led_test",)


def __getattr__(name: str):
    """Lazily load a sample core by name from this category."""
    if name in _NAMES:
        return load_sample_core("custom", name)
    raise AttributeError(f"module 'libretro.samples.custom' has no attribute {name!r}")


def __dir__() -> list[str]:
    return [*_NAMES]
