"""
MIDI I/O sample cores from libretro-samples ``midi/``.

Names exposed by this subpackage:

* ``midi_test`` — polls ``RETRO_ENVIRONMENT_GET_MIDI_INTERFACE`` and echoes input events back through the output callback.

.. seealso::

    :mod:`libretro.samples`
        Overview of all sample-core categories and their lazy-loading semantics.
"""

from libretro.samples._loader import load_sample_core

_NAMES = ("midi_test",)


def __getattr__(name: str):
    """Lazily load a sample core by name from this category."""
    if name in _NAMES:
        return load_sample_core("midi", name)
    raise AttributeError(f"module 'libretro.samples.midi' has no attribute {name!r}")


def __dir__() -> list[str]:
    return [*_NAMES]
