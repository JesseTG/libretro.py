"""Integration tests for the :class:`~libretro.core.Core` lifecycle."""

from __future__ import annotations

import pytest

from libretro import API_VERSION, Core


@pytest.fixture(
    params=[
        pytest.param(("custom", "led_test"), id="custom.led_test"),
        pytest.param(("tests", "test"), id="tests.test"),
    ],
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
