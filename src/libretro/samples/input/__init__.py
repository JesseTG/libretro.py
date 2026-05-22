"""
Input-handling sample cores from libretro-samples ``input/``.

Names exposed by this subpackage:

* ``button_test`` — maps every RetroPad button and analog axis to an on-screen indicator.

.. seealso::

    :mod:`libretro.samples`
        Overview of all sample-core categories and their lazy-loading semantics.
"""

from libretro.samples._loader import load_sample_core

_NAMES = ("button_test",)


def __getattr__(name: str):
    """Lazily load a sample core by name from this category."""
    if name in _NAMES:
        return load_sample_core("input", name)
    raise AttributeError(f"module 'libretro.samples.input' has no attribute {name!r}")


def __dir__() -> list[str]:
    return [*_NAMES]
