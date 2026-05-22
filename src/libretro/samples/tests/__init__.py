"""
General-purpose sample cores from libretro-samples ``tests/``.

Names exposed by this subpackage:

* ``test`` — the canonical reference core (input descriptors, options, log interface, basic AV).
* ``test_advanced`` — subsystem + content-override coverage.
* ``cruzes`` — TTF text rendering demo (heavier; carries the ``slow`` test marker).

.. seealso::

    :mod:`libretro.samples`
        Overview of all sample-core categories and their lazy-loading semantics.
"""

from libretro.samples._loader import load_sample_core

_NAMES = ("test", "test_advanced", "cruzes")


def __getattr__(name: str):
    """Lazily load a sample core by name from this category."""
    if name in _NAMES:
        return load_sample_core("tests", name)
    raise AttributeError(f"module 'libretro.samples.tests' has no attribute {name!r}")


def __dir__() -> list[str]:
    return [*_NAMES]
