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

_NAMES = (
    # Driver-specific cores
    "led_test",
    "rumble_test",
    "sensor_test",
    "microphone_test",
    "power_test",
    "perf_test",
    "vfs_test",
    "memory_map_test",
    "savestate_test",
    "keyboard_test",
    "proc_address_test",
    "shutdown_test",
    "options_v2_test",
    "options_v1_intl_test",
    # Env-query cores
    "path_query_test",
    "video_query_test",
    "pixel_format_test",
    "input_query_test",
    "timing_query_test",
    "audio_query_test",
    "language_test",
    "game_info_ext_test",
    "jit_capable_test",
    "hw_shared_context_test",
)


def __getattr__(name: str):
    """Lazily load a sample core by name from this category."""
    if name in _NAMES:
        return load_sample_core("custom", name)
    raise AttributeError(f"module 'libretro.samples.custom' has no attribute {name!r}")


def __dir__() -> list[str]:
    return [*_NAMES]
