"""
Audio-output sample cores from libretro-samples ``audio/``.

Names exposed by this subpackage:

* ``audio_callback`` — async audio via ``RETRO_ENVIRONMENT_SET_AUDIO_CALLBACK``.
* ``audio_no_callback`` — same tone generator emitted per frame through ``audio_batch_cb``.
* ``audio_playback_wav`` — decodes and plays a bundled WAV.

.. seealso::

    :mod:`libretro.samples`
        Overview of all sample-core categories and their lazy-loading semantics.
"""

from libretro.samples._loader import load_sample_core

_NAMES = ("audio_callback", "audio_no_callback", "audio_playback_wav")


def __getattr__(name: str):
    """Lazily load a sample core by name from this category."""
    if name in _NAMES:
        return load_sample_core("audio", name)
    raise AttributeError(f"module 'libretro.samples.audio' has no attribute {name!r}")


def __dir__() -> list[str]:
    return [*_NAMES]
