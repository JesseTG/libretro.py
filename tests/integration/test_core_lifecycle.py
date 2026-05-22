"""Integration tests for the :class:`~libretro.core.Core` lifecycle."""

from __future__ import annotations

import pytest

from libretro import API_VERSION, Core

# Every (category, name) pair that the build system can produce. Tests
# automatically skip the entries that aren't bundled on the running
# platform (e.g. GL cores on Windows MSVC, every core on the
# py3-none-any fallback wheel).
ALL_SAMPLE_CORES = [
    ("audio", "audio_callback"),
    ("audio", "audio_no_callback"),
    ("audio", "audio_playback_wav"),
    ("input", "button_test"),
    ("midi", "midi_test"),
    ("tests", "test"),
    ("tests", "test_advanced"),
    ("tests", "cruzes"),
    ("video", "software_rendering"),
    ("video", "software_direct_to_vram"),
    ("video", "gl_fixedfunction"),
    ("video", "gl_shaders"),
    ("video", "gl_compute_shaders"),
    ("custom", "led_test"),
]


@pytest.fixture(
    params=[pytest.param(pair, id=f"{pair[0]}.{pair[1]}") for pair in ALL_SAMPLE_CORES],
)
def sample_core(request: pytest.FixtureRequest) -> Core:
    """Return a freshly-loaded :class:`~libretro.core.Core` for one bundled sample."""
    category, name = request.param
    module = pytest.importorskip(f"libretro.samples.{category}")
    try:
        return getattr(module, name)
    except ImportError as exc:
        pytest.skip(f"Sample core libretro.samples.{category}.{name} unavailable: {exc}")


def test_core_loads(sample_core: Core) -> None:
    """A bundled sample core can be instantiated and reports a non-empty library name."""
    info = sample_core.get_system_info()
    assert info.library_name, "library_name should be a non-empty bytes string"
    assert isinstance(info.library_name, bytes)


def test_core_api_version_matches_libretro_py(sample_core: Core) -> None:
    """Every sample core reports the libretro API version libretro.py is built against."""
    assert sample_core.api_version() == API_VERSION
